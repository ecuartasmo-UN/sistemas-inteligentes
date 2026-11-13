"""El contrapunto del Laboratorio 7B: un LLM estima el dominio de los mismos técnicos que el modelo bayesiano.

- Los datos: 10 técnicos simulados de la alineación de una bomba, con 8 respuestas cada uno (datos/). El archivo trae
  también su estado oculto al terminar, que solo se usa para evaluar. El LLM nunca lo ve.
- El LLM recibe la descripción de la habilidad y las respuestas, sin los parámetros. Responde en un formato fijo:
  una línea por técnico, con su dominio estimado, su decisión y una razón corta. Una línea de técnico que no cumple
  el formato se cuenta como no válida y se muestra tal cual, sin adivinar. El texto que no es de ningún técnico se
  cuenta aparte, como texto fuera del formato.
- Se comparan tres criterios: la exactitud frente al estado simulado, la consistencia entre dos corridas iguales y
  la explicación.
- Cada método escribe sus filas en el CSV común del contrapunto, contrapunto_7B.csv, con el esquema de las sesiones
  2 a 6. El archivo se guarda solo y conserva lo anotado en otras sesiones del kernel. Volver a ejecutar un método
  reemplaza sus filas.
"""
from __future__ import annotations

import csv
import io
import re
from datetime import date
from pathlib import Path

import apoyo as a
import graficas as g
import presentacion as p
import tutor
from apoyo import ErrorDeLaboratorio, amable

DATOS = Path("datos/tecnicos_contrapunto.csv")
ARCHIVO_CSV = "contrapunto_7B.csv"
COLUMNAS_CSV = ["sesion", "laboratorio", "pareja", "fecha", "tarea", "instancia", "metodo", "estrategia", "proveedor",
                "modelo", "correcto", "resultado", "iteraciones", "llamadas", "tokens_entrada", "tokens_salida",
                "tokens_razonamiento", "costo_usd", "tiempo_s", "notas"]
TAREA = "Alineación de una bomba: ¿domina el técnico al terminar 8 ejercicios?"
_REGISTRO: dict = {}
_LLM: dict = {}
_PAREJA = [""]

PROMPT = """Eres el modelo del estudiante de un tutor inteligente. El tutor acompaña la inducción de técnicos nuevos de \
mantenimiento industrial.

La habilidad es «Alineación de una bomba»: dejar en línea los ejes del motor y de la bomba. Cada técnico resolvió \
8 ejercicios de esta habilidad, en orden. ✓ es una respuesta correcta y ✗ una incorrecta. Un técnico puede acertar \
sin dominar la habilidad, y puede fallar aunque la domine. Los técnicos pueden aprender mientras practican.
{parametros}
Para cada técnico, estima la probabilidad de que ya domine la habilidad al terminar sus 8 ejercicios. Después decide \
si pasa a la siguiente habilidad. El tutor solo lo deja pasar si está al menos 95 % seguro de que domina.

Los técnicos:
{tecnicos}

Responde con una línea por técnico, en este formato exacto:
T01; 0.80; no domina; una razón de menos de 15 palabras
Usa punto decimal. Escribe «domina» si el técnico pasa, y «no domina» si debe seguir practicando. \
No escribas nada más."""
PARAMETROS = """
El modelo del curso tiene cuatro parámetros para esta habilidad. El dominio inicial es 0.10: la probabilidad de que un \
técnico ya domine al llegar. El aprendizaje es 0.12: la probabilidad de aprender en cada ejercicio. La adivinanza es \
0.15: la probabilidad de acertar sin dominar. El descuido es 0.10: la probabilidad de fallar aunque domine.
"""
_LINEA = re.compile(r"^\W*(T\d{1,2})\W*[;|,\t:]\s*([0-9]+(?:[.,][0-9]+)?)\s*(%?)\s*[;|,\t]\s*(no domina|domina)\s*"
                    r"(?:[;|,\t:.-]\s*(.*))?$", re.I)


# ----------------------------------------------------------------------------- los datos

def cargar_tecnicos() -> list:
    """Los 10 técnicos del contrapunto, con su estado oculto aparte."""
    try:
        with DATOS.open(encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
    except OSError:
        raise ErrorDeLaboratorio(f"No encuentro {DATOS}. Abre el notebook desde la carpeta del laboratorio.") from None
    h = tutor.HABILIDADES["alineacion"]
    tecnicos = []
    for fila in filas:
        resp = tutor.leer_respuestas(fila["respuestas"], f"las respuestas de {fila['tecnico']}")
        valores = tutor.curva(resp, h)
        tecnicos.append({"tecnico": fila["tecnico"], "respuestas": resp, "texto": fila["respuestas"],
                         "bkt": valores[-1], "real": fila["domina_al_terminar"].strip().lower() in ("sí", "si"),
                         "curva": valores})
    return tecnicos


@amable
def mostrar_tecnicos() -> list | None:
    """Las respuestas de los 10 técnicos: lo mismo que va a leer el LLM. El estado oculto no se muestra todavía."""
    tecnicos = cargar_tecnicos()
    p.mostrar_tabla([{"Técnico": t["tecnico"], "Respuestas, en orden": t["texto"]} for t in tecnicos],
                    titulo="Los 10 técnicos del contrapunto: 8 ejercicios de alineación cada uno",
                    pie="Datos simulados. Si cada uno domina o no al terminar se revela después, al evaluar.")
    return tecnicos


def prompt(con_parametros: bool = False) -> str:
    tecnicos = cargar_tecnicos()
    return PROMPT.format(parametros=PARAMETROS if con_parametros else "",
                         tecnicos="\n".join(f"{t['tecnico']}: {t['texto']}" for t in tecnicos))


# ----------------------------------------------------------------------------- leer la respuesta del LLM

def leer_respuesta(texto: str, tecnicos: list) -> tuple:
    """Lee una línea por técnico: su dominio estimado, su decisión y su razón.

    Devuelve (estimaciones, líneas de técnico no válidas, otras líneas fuera del formato)."""
    validos = {t["tecnico"] for t in tecnicos}
    estimaciones, invalidas, extra = {}, [], []
    for linea in texto.splitlines():
        original = linea.strip()
        if not original or original.startswith("```"):
            continue
        limpia = original.replace("**", "")
        if not (re.match(r"^\W*T", limpia) and re.search(r"[;|]", limpia[:12])):
            extra.append(original)      # no es la línea de un técnico: comentarios, títulos o cuentas
            continue
        m = _LINEA.match(limpia)
        if not m:
            invalidas.append(original)
            continue
        tecnico = "T" + m.group(1)[1:].zfill(2)
        valor = float(m.group(2).replace(",", "."))
        if m.group(3) == "%" or 1 < valor <= 100:
            valor /= 100
        if tecnico not in validos or not 0 <= valor <= 1 or tecnico in estimaciones:
            invalidas.append(original)
            continue
        estimaciones[tecnico] = {"dominio": valor, "domina": m.group(4).lower() == "domina",
                                 "razon": (m.group(5) or "").strip()}
    return estimaciones, invalidas, extra


# ----------------------------------------------------------------------------- comparar

def _resumen(nombre: str, decisiones: dict, tecnicos: list) -> dict:
    """Aciertos, técnicos que pasan sin dominar y técnicos que practican de más."""
    validas = [t for t in tecnicos if t["tecnico"] in decisiones]
    aciertos = sum(decisiones[t["tecnico"]] == t["real"] for t in validas)
    sin_dominar = sum(decisiones[t["tecnico"]] and not t["real"] for t in validas)
    de_mas = sum(not decisiones[t["tecnico"]] and t["real"] for t in validas)
    return {"Método": nombre, "Decisiones válidas": f"{len(validas)} de {len(tecnicos)}",
            "Aciertos": f"{aciertos} de {len(validas)}" if validas else "-",
            "Avanzan sin dominar": sin_dominar, "Practican de más": de_mas}


def _registrar(metodo: str, estrategia: str, proveedor: str, modelo: str, tecnicos: list, decisiones: dict,
               estimados: dict, segundos: float, llamadas: int = 0, entrada: int = 0, salida: int = 0,
               costo: float = 0.0) -> None:
    """Anota una fila por técnico en el CSV común. La llamada y sus tokens van en la fila del primer técnico."""
    for clave in [k for k in _REGISTRO if k[0] == metodo and k[1] == estrategia]:
        del _REGISTRO[clave]
    for i, t in enumerate(tecnicos):
        primero = i == 0
        dicho = decisiones.get(t["tecnico"])
        _REGISTRO[(metodo, estrategia, t["tecnico"])] = {
            "sesion": 7, "laboratorio": "7B", "fecha": date.today().isoformat(), "tarea": TAREA,
            "instancia": f"técnico {t['tecnico']}", "metodo": metodo, "estrategia": estrategia, "proveedor": proveedor,
            "modelo": modelo, "correcto": int(dicho is not None and dicho == t["real"]),
            "resultado": "no válida" if dicho is None else ("domina" if dicho else "no domina"), "iteraciones": 1,
            "llamadas": llamadas if primero else 0, "tokens_entrada": entrada if primero else 0,
            "tokens_salida": salida if primero else 0, "tokens_razonamiento": 0,
            "costo_usd": round(costo, 7) if primero else 0, "tiempo_s": f"{segundos / len(tecnicos):.5f}",
            "notas": f"real: {'domina' if t['real'] else 'no domina'}; estimado: "
                     + (a.num(estimados[t['tecnico']], 3) if t["tecnico"] in estimados else "sin dato")}


def _pedir(llm, etiqueta: str, con_parametros: bool, tecnicos: list):
    instruccion = prompt(con_parametros)
    try:
        # Con los parámetros, algunos modelos hacen la cuenta por escrito antes de responder: necesitan más espacio
        respuesta = llm.completar(instruccion, etiqueta=etiqueta, max_tokens_respuesta=3000 if con_parametros else 700)
    except Exception as e:      # sin red, sin saldo o el servidor caído: se explica y el notebook sigue
        p.nota(f"El LLM no respondió: {e}", "error", "Sin respuesta del LLM")
        return None, None
    if not respuesta.disponible:
        return None, None
    estimaciones, invalidas, extra = leer_respuesta(respuesta.texto, tecnicos)
    return respuesta, (instruccion, estimaciones, invalidas, extra)


def _avisar_extra(extra: list) -> None:
    """Cuenta el texto que el LLM escribió fuera del formato, aparte de los técnicos, y muestra las primeras líneas."""
    if extra:
        muestra = "\n".join(extra[:3]) + ("\n…" if len(extra) > 3 else "")
        p.nota(f"El LLM escribió {len(extra)} {'línea' if len(extra) == 1 else 'líneas'} fuera del formato pedido, "
               f"aparte de los técnicos. No se usan. Las primeras:\n{muestra}", "aviso", "Texto fuera del formato")


@amable
def comparar_con_llm(llm) -> dict | None:
    """Dos corridas iguales del LLM frente al modelo bayesiano, con el estado simulado como referencia."""
    if llm is None:
        raise ErrorDeLaboratorio("No hay un cliente del LLM. Ejecuta la celda de «Antes de empezar» que lo crea.")
    tecnicos = cargar_tecnicos()
    corridas = []
    for k in (1, 2):
        respuesta, datos = _pedir(llm, f"contrapunto-{k}", False, tecnicos)
        if respuesta is None:
            return None
        instruccion, estimaciones, invalidas, extra = datos
        corridas.append((respuesta, estimaciones, invalidas))
        if k == 1:
            p.mostrar_conversacion([{"rol": "user", "contenido": instruccion}],
                                   titulo="El prompt, igual para las dos corridas y para todas las parejas",
                                   etiquetas={"user": "Prompt"})
        p.mostrar_conversacion([{"rol": "assistant", "contenido": respuesta.texto}], titulo=f"La respuesta de la corrida {k}")
        _avisar_extra(extra)
        _registrar("LLM", f"sin parámetros, corrida {k}", respuesta.proveedor, respuesta.modelo, tecnicos,
                   {t: e["domina"] for t, e in estimaciones.items()}, {t: e["dominio"] for t, e in estimaciones.items()},
                   respuesta.segundos, 1, respuesta.tokens_entrada, respuesta.tokens_salida, respuesta.costo_usd or 0.0)
    _registrar("BKT", f"umbral {tutor.UMBRAL}", "local", "Bayesian Knowledge Tracing", tecnicos,
               {t["tecnico"]: t["bkt"] >= tutor.UMBRAL for t in tecnicos}, {t["tecnico"]: t["bkt"] for t in tecnicos}, 0.0)
    (_, e1, inv1), (_, e2, inv2) = corridas
    _LLM["sin parametros"] = e1
    filas = []
    for t in tecnicos:
        x1, x2 = e1.get(t["tecnico"]), e2.get(t["tecnico"])
        filas.append({"Técnico": t["tecnico"], "Respuestas": t["texto"],
                      "BKT": f"{a.prob(t['bkt'])} · {'domina' if t['bkt'] >= tutor.UMBRAL else 'no domina'}",
                      "LLM, corrida 1": f"{a.prob(x1['dominio'])} · {'domina' if x1['domina'] else 'no domina'}" if x1 else "no válida",
                      "LLM, corrida 2": f"{a.prob(x2['dominio'])} · {'domina' if x2['domina'] else 'no domina'}" if x2 else "no válida",
                      "¿Domina de verdad?": "sí" if t["real"] else "no"})
    g.contrapunto([{"tecnico": t["tecnico"], "bkt": t["bkt"], "real": t["real"],
                    "llm1": e1[t["tecnico"]]["dominio"] if t["tecnico"] in e1 else None,
                    "llm2": e2[t["tecnico"]]["dominio"] if t["tecnico"] in e2 else None} for t in tecnicos])
    p.desplegable("Ver la tabla por técnico: el dominio estimado y la decisión de cada método",
                  p.tabla_html(filas, pie="«Domina»: pasa a la siguiente habilidad. La última columna es el estado "
                                          "simulado, que el LLM no vio."))
    resumen = [_resumen("BKT (umbral 0.95)", {t["tecnico"]: t["bkt"] >= tutor.UMBRAL for t in tecnicos}, tecnicos),
               _resumen("LLM, corrida 1", {k: v["domina"] for k, v in e1.items()}, tecnicos),
               _resumen("LLM, corrida 2", {k: v["domina"] for k, v in e2.items()}, tecnicos)]
    p.mostrar_tabla(resumen, titulo="Criterio 1 · La exactitud frente al estado simulado",
                    pie="Avanzar sin dominar es el error caro: el técnico llega a la planta sin saber alinear una bomba.")
    comunes = [t for t in tecnicos if t["tecnico"] in e1 and t["tecnico"] in e2]
    cambian = sum(e1[t["tecnico"]]["domina"] != e2[t["tecnico"]]["domina"] for t in comunes)
    diferencia = (sum(abs(e1[t["tecnico"]]["dominio"] - e2[t["tecnico"]]["dominio"]) for t in comunes) / len(comunes)
                  if comunes else 0.0)
    gemelos = [(x, y) for i, x in enumerate(tecnicos) for y in tecnicos[i + 1:] if x["texto"] == y["texto"]]

    def par(e, x, y):
        return (f"{a.prob(e[x['tecnico']]['dominio'])} y {a.prob(e[y['tecnico']]['dominio'])}"
                if x["tecnico"] in e and y["tecnico"] in e else "no válida")
    p.mostrar_tabla([{"Qué se mide": "Decisiones que cambian entre las dos corridas", "LLM": f"{cambian} de {len(comunes)}",
                      "BKT": "0: con las mismas respuestas, siempre da lo mismo"},
                     {"Qué se mide": "Cuánto cambia, en promedio, el dominio estimado de un técnico de una corrida a la otra",
                      "LLM": a.num(diferencia, 3), "BKT": "0"},
                     {"Qué se mide": "Líneas que no cumplen el formato", "LLM": f"{len(inv1)} y {len(inv2)}",
                      "BKT": "no aplica"}],
                    titulo="Criterio 2 · La consistencia entre dos corridas iguales")
    if gemelos:
        p.mostrar_tabla([{"Técnicos con las mismas respuestas": f"{x['tecnico']} y {y['tecnico']}", "Respuestas": x["texto"],
                          "LLM, corrida 1": par(e1, x, y), "LLM, corrida 2": par(e2, x, y),
                          "BKT": f"{a.prob(x['bkt'])} y {a.prob(y['bkt'])}"} for x, y in gemelos],
                        pie="Con las mismas respuestas, un modelo consistente da el mismo dominio estimado.")
    p.mostrar_tabla([{"Técnico": t["tecnico"], "Respuestas": t["texto"],
                      "Razón del LLM, corrida 1": e1[t["tecnico"]]["razon"] if t["tecnico"] in e1 else "no válida",
                      "Razón del LLM, corrida 2": e2[t["tecnico"]]["razon"] if t["tecnico"] in e2 else "no válida"}
                     for t in tecnicos],
                    titulo="Criterio 3 · La explicación del LLM",
                    pie="Para revisar una razón, compárala con las respuestas del técnico: ¿describe lo que pasó? "
                        "BKT explica con su curva, paso a paso.")
    for k, inv in ((1, inv1), (2, inv2)):
        if inv:
            p.nota("\n".join(inv), "aviso", f"Líneas de la corrida {k} que no cumplen el formato (no se adivinan)")
    p.nota(llm.texto_resumen(), "neutro", "Consumo del LLM en este notebook, sumando todas sus llamadas")
    _guardar()
    a.anotar("5", "contrapunto", "LLM sin parámetros, corrida 1", "aciertos", resumen[1]["Aciertos"])
    a.anotar("5", "contrapunto", "LLM sin parámetros, corrida 2", "aciertos", resumen[2]["Aciertos"])
    a.anotar("5", "contrapunto", "BKT", "aciertos", resumen[0]["Aciertos"])
    return {"corrida_1": e1, "corrida_2": e2, "resumen": resumen}


@amable
def llm_con_parametros(llm) -> dict | None:
    """El mismo pedido, ahora con los cuatro parámetros del curso: ¿se acerca el LLM al modelo bayesiano?"""
    if llm is None:
        raise ErrorDeLaboratorio("No hay un cliente del LLM. Ejecuta la celda de «Antes de empezar» que lo crea.")
    tecnicos = cargar_tecnicos()
    respuesta, datos = _pedir(llm, "contrapunto-parametros", True, tecnicos)
    if respuesta is None:
        return None
    instruccion, estimaciones, invalidas, extra = datos
    p.mostrar_conversacion([{"rol": "user", "contenido": instruccion}, {"rol": "assistant", "contenido": respuesta.texto}],
                           titulo="El prompt con los cuatro parámetros, y la respuesta", etiquetas={"user": "Prompt"})
    _avisar_extra(extra)
    _registrar("LLM", "con los cuatro parámetros", respuesta.proveedor, respuesta.modelo, tecnicos,
               {t: e["domina"] for t, e in estimaciones.items()}, {t: e["dominio"] for t, e in estimaciones.items()},
               respuesta.segundos, 1, respuesta.tokens_entrada, respuesta.tokens_salida, respuesta.costo_usd or 0.0)
    antes = _LLM.get("sin parametros", {})
    filas = [{"Técnico": t["tecnico"], "BKT": a.prob(t["bkt"]),
              "LLM sin parámetros": a.prob(antes[t["tecnico"]]["dominio"]) if t["tecnico"] in antes else "-",
              "LLM con parámetros": a.prob(estimaciones[t["tecnico"]]["dominio"]) if t["tecnico"] in estimaciones else "no válida",
              "¿Domina de verdad?": "sí" if t["real"] else "no"} for t in tecnicos]
    p.mostrar_tabla(filas, titulo="¿Se acerca el LLM a BKT si le das los parámetros?",
                    pie=None if antes else "«-»: en esta sesión del kernel no has ejecutado la sección 5.")
    resumen = [_resumen("BKT (umbral 0.95)", {t["tecnico"]: t["bkt"] >= tutor.UMBRAL for t in tecnicos}, tecnicos),
               _resumen("LLM con parámetros", {k: v["domina"] for k, v in estimaciones.items()}, tecnicos)]
    p.mostrar_tabla(resumen, titulo="La exactitud frente al estado simulado")
    if invalidas:
        p.nota("\n".join(invalidas), "aviso", "Líneas que no cumplen el formato (no se adivinan)")
    p.nota(llm.texto_resumen(), "neutro", "Consumo del LLM en este notebook, sumando todas sus llamadas")
    _guardar()
    a.anotar("6.2", "contrapunto", "LLM con los cuatro parámetros", "aciertos", resumen[1]["Aciertos"])
    return {"estimaciones": estimaciones, "resumen": resumen}


def _leer_csv(destino: Path) -> list:
    """Las filas que ya tiene el CSV. Las lee aunque Excel lo haya guardado con punto y coma o en la codificación de Windows."""
    try:
        datos = destino.read_bytes()
    except OSError:
        return []
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            texto = datos.decode(codificacion)
            break
        except UnicodeDecodeError:
            continue
    else:
        return []
    if not texto.strip():
        return []
    primera = texto.splitlines()[0]
    lector = csv.DictReader(io.StringIO(texto), delimiter=";" if primera.count(";") > primera.count(",") else ",")
    filas = list(lector)
    if not set(COLUMNAS_CSV) <= set(lector.fieldnames or []):
        return []
    return [{k: fila.get(k, "") for k in COLUMNAS_CSV} for fila in filas]


def _guardar(ruta: str = ARCHIVO_CSV) -> list | None:
    """Guarda el CSV del contrapunto: lo anotado antes, más los métodos de esta sesión del kernel, que reemplazan sus filas."""
    destino = Path(ruta)
    presentes = {(m, e) for m, e, _ in _REGISTRO}
    filas = {(f["metodo"], f["estrategia"], f["instancia"]): f for f in _leer_csv(destino)
             if (f["metodo"], f["estrategia"]) not in presentes}
    for fila in _REGISTRO.values():
        filas[(fila["metodo"], fila["estrategia"], fila["instancia"])] = fila
    try:
        with destino.open("w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=COLUMNAS_CSV)
            escritor.writeheader()
            for fila in filas.values():
                escritor.writerow({**fila, "pareja": _PAREJA[0] or fila.get("pareja", "")})
    except PermissionError:
        p.nota(f"No pude escribir {destino}. Ciérralo si está abierto en Excel y ejecuta de nuevo.", "error")
        return None
    return list(filas.values())


def guardar_csv(pareja: str, ruta: str = ARCHIVO_CSV) -> None:
    """Pone los nombres de la pareja en el CSV común del contrapunto y muestra lo que tiene, por método."""
    if not isinstance(pareja, str) or not pareja.strip() or pareja.strip() == "Nombre 1 y Nombre 2":
        p.nota("Escribe los nombres de la pareja en PAREJA, para que el CSV sea suyo.", "aviso")
    else:
        _PAREJA[0] = pareja.strip()
    filas = _guardar(ruta)
    if filas is None:
        return
    if not filas:
        p.nota("No hay resultados del contrapunto para guardar. Ejecuta antes la sección 5.", "aviso")
        return
    destino = Path(ruta)
    grupos = {}
    for fila in filas:
        grupo = grupos.setdefault((fila["metodo"], fila["estrategia"]), {"filas": 0, "aciertos": 0, "costo": 0.0})
        grupo["filas"] += 1
        grupo["aciertos"] += int(fila["correcto"])
        grupo["costo"] += float(fila["costo_usd"] or 0)
    p.mostrar_tabla([{"Método": m, "Estrategia": e, "Técnicos": x["filas"], "Aciertos": x["aciertos"],
                      "Costo (US$)": a.num(x["costo"], 5)} for (m, e), x in grupos.items()],
                    titulo=f"{len(filas)} filas guardadas en {destino}")
