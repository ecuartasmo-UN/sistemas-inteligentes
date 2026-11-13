"""El modelo del estudiante del Laboratorio 7B (Sesión 7, Sistemas Inteligentes): Bayesian Knowledge Tracing.

- El curso: la inducción de los técnicos nuevos de MantenIA, una empresa ficticia, con tres habilidades.
- Los técnicos salen de una simulación con parámetros conocidos: no hay personas reales.
- Cada respuesta actualiza el dominio estimado con las ecuaciones de Corbett y Anderson (1994): primero la regla de
  Bayes, después la oportunidad de aprender. Se supone que nadie olvida.
- La simulación usa la semilla 7 y el mismo orden de sorteos de Sesion 7/ejemplos/bkt_7b.py. Por eso la regla
  «hasta dominar (0.95)» y la de 5 ejercicios fijos dan las cifras de las diapositivas.
- Cada experimento se anota en la bitácora resultados_7B.csv.
"""
from __future__ import annotations

import copy
import unicodedata

import numpy as np

import apoyo as a
import graficas as g
import presentacion as p
from apoyo import ErrorDeLaboratorio, amable

SEMILLA = 7
TECNICOS = 200          # técnicos simulados por habilidad y por regla
MAX_EJERCICIOS = 30     # tope de ejercicios por habilidad
UMBRAL = 0.95           # el umbral de Corbett y Anderson (1994)
FIJO = 5

# Los cuatro parámetros de cada habilidad: dominio inicial, aprendizaje, adivinanza y descuido
HABILIDADES = {
    "bloqueo": {"nombre": "Bloqueo y etiquetado", "L0": 0.30, "T": 0.20, "G": 0.20, "S": 0.08},
    "alineacion": {"nombre": "Alineación de una bomba", "L0": 0.10, "T": 0.12, "G": 0.15, "S": 0.10},
    "vibracion": {"nombre": "Lectura de vibración", "L0": 0.15, "T": 0.15, "G": 0.25, "S": 0.10},
}
CLAVES = {"dominio_inicial": "L0", "aprendizaje": "T", "adivinanza": "G", "descuido": "S"}
TOPE_ADIVINANZA, TOPE_DESCUIDO = 0.3, 0.1      # Baker, Corbett y Aleven (2008)
ACIERTO = set("✓✔✅1")
FALLO = set("✗✘❌×xX0")


def _normal(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(t)) if unicodedata.category(c) != "Mn").lower().strip()


# ----------------------------------------------------------------------------- las ecuaciones

def actualizar(prob: float, acierto: bool, h: dict) -> tuple:
    """Una respuesta: la regla de Bayes y, después, la oportunidad de aprender. Devuelve (después de Bayes, siguiente)."""
    if acierto:
        post = prob * (1 - h["S"]) / (prob * (1 - h["S"]) + (1 - prob) * h["G"])
    else:
        post = prob * h["S"] / (prob * h["S"] + (1 - prob) * (1 - h["G"]))
    return post, post + (1 - post) * h["T"]


def curva(respuestas: list, h: dict) -> list:
    """El dominio estimado antes de cada respuesta y al final: n + 1 valores."""
    valores = [h["L0"]]
    for r in respuestas:
        valores.append(actualizar(valores[-1], r, h)[1])
    return valores


def hasta_umbral(valores: list, umbral: float):
    """Cuántos ejercicios hicieron falta para llegar al umbral, o None si no llegó."""
    return next((i for i, v in enumerate(valores) if v >= umbral), None)


# ----------------------------------------------------------------------------- revisar lo que escribe la pareja

def leer_respuestas(texto, nombre: str) -> list:
    """Lee una secuencia de respuestas: ✓ o 1 si acierta, ✗ o 0 si falla. Ignora los espacios y las comas."""
    if isinstance(texto, (list, tuple)):
        texto = " ".join(str(x) for x in texto)
    if not isinstance(texto, str):
        raise ErrorDeLaboratorio(f"Revisa {nombre}: debe ser un texto entre comillas, como \"✗ ✗ ✓ ✓\" o \"0 0 1 1\".")
    respuestas = []
    for c in texto:
        if c in ACIERTO:
            respuestas.append(True)
        elif c in FALLO:
            respuestas.append(False)
        elif c in " ,;-/|\t":
            continue
        elif c.isalpha():
            raise ErrorDeLaboratorio(f"En {nombre} hay letras, como «{c}». No escribas «sí» o «no», ni V o F. Escribe cada "
                                     "respuesta como ✓ o 1 si acierta, y como ✗ o 0 si falla.")
        else:
            raise ErrorDeLaboratorio(f"En {nombre} hay un «{c}». Escribe cada respuesta como ✓ o 1 si acierta, y como ✗ o 0 "
                                     "si falla. Puedes separarlas con espacios.")
    if not respuestas:
        raise ErrorDeLaboratorio(f"En {nombre} no hay respuestas. Escribe al menos una: ✓ o 1, ✗ o 0.")
    if len(respuestas) > MAX_EJERCICIOS:
        raise ErrorDeLaboratorio(f"En {nombre} hay {len(respuestas)} respuestas. Usa {MAX_EJERCICIOS} o menos.")
    return respuestas


def leer_parametros(nombre: str, valores) -> dict:
    """Revisa los cuatro parámetros. Avisa si la adivinanza o el descuido pasan los topes de Baker et al. (2008)."""
    inicio = nombre[0].upper() + nombre[1:]      # el nombre al comienzo de una oración
    if not isinstance(valores, dict):
        raise ErrorDeLaboratorio(f"{inicio} debe ser un diccionario entre llaves con los cuatro parámetros: "
                                 '{"dominio_inicial": 0.10, "aprendizaje": 0.12, "adivinanza": 0.15, "descuido": 0.10}.')
    h = {}
    for clave, valor in valores.items():
        k = CLAVES.get(_normal(clave).replace(" ", "_"))
        if k is None:
            raise ErrorDeLaboratorio(f"{inicio} tiene un parámetro llamado {clave!r}. Los cuatro son dominio_inicial, "
                                     "aprendizaje, adivinanza y descuido.")
        h[k] = a.probabilidad(f"El parámetro «{clave}» de {nombre}", valor)
    faltan = [c for c, k in CLAVES.items() if k not in h]
    if faltan:
        raise ErrorDeLaboratorio(f"A {nombre} le falta: {', '.join(faltan)}. Escribe los cuatro parámetros.")
    if h["G"] + h["S"] >= 1:
        raise ErrorDeLaboratorio(f"En {nombre}, la adivinanza y el descuido suman {a.num(h['G'] + h['S'], 4)}. Con eso, "
                                 "acertar no hace más probable el dominio: el modelo deja de tener sentido.")
    if h["G"] > TOPE_ADIVINANZA:
        p.nota(f"En {nombre}, la adivinanza pasa de {TOPE_ADIVINANZA}, el tope que usan Baker, Corbett y Aleven (2008). "
               "Con una adivinanza tan alta, un acierto dice muy poco sobre el dominio.", "aviso", "Revisa los parámetros")
    if h["S"] > TOPE_DESCUIDO:
        p.nota(f"En {nombre}, el descuido pasa de {TOPE_DESCUIDO}, el tope que usan Baker, Corbett y Aleven (2008). "
               "Con un descuido tan alto, un error dice muy poco sobre el dominio.", "aviso", "Revisa los parámetros")
    return h


def _parametros_en_texto(h: dict) -> str:
    return " · ".join(f"{c.replace('_', ' ')} {a.num(h[k], 2)}" for c, k in CLAVES.items())


def _simbolos(respuestas: list) -> str:
    return " ".join("✓" if r else "✗" for r in respuestas)


# ----------------------------------------------------------------------------- 1 y 2. el curso y un técnico

@amable
def mostrar_curso() -> None:
    """Las tres habilidades del curso de inducción, con sus cuatro parámetros."""
    filas = [{"Habilidad": h["nombre"], "Dominio inicial": a.num(h["L0"], 2), "Aprendizaje": a.num(h["T"], 2),
              "Adivinanza": a.num(h["G"], 2), "Descuido": a.num(h["S"], 2)} for h in HABILIDADES.values()]
    p.mostrar_tabla(filas, titulo="El curso de inducción de los técnicos nuevos de MantenIA",
                    pie="Datos de una simulación con estos parámetros: no hay personas reales.")


def simular_tecnico(h: dict, rng: np.random.Generator, regla: str, valor: float) -> tuple:
    """Simula a un técnico hasta que la regla diga «basta». Devuelve sus respuestas, la curva y si domina al terminar.

    regla: «dominio» (hasta que el dominio estimado llegue al umbral), «fijo» (un número fijo de ejercicios) o
    «seguidos» (hasta acertar varias veces seguidas). El orden de los sorteos es el de ejemplos/bkt_7b.py."""
    domina = rng.random() < h["L0"]           # el estado oculto: ¿ya domina la habilidad?
    prob = h["L0"]                             # lo que estima el tutor
    respuestas, valores, seguidos = [], [prob], 0
    while len(respuestas) < MAX_EJERCICIOS:
        if (regla == "dominio" and prob >= valor) or (regla == "fijo" and len(respuestas) >= valor) \
                or (regla == "seguidos" and seguidos >= valor):
            break
        acierto = bool(rng.random() < ((1 - h["S"]) if domina else h["G"]))
        respuestas.append(acierto)
        prob = actualizar(prob, acierto, h)[1]
        valores.append(prob)
        seguidos = seguidos + 1 if acierto else 0
        if not domina and rng.random() < h["T"]:   # practicar puede enseñar
            domina = True
    return respuestas, valores, domina


@amable
def tecnico_de_ejemplo() -> dict | None:
    """El técnico de la diapositiva: el número 2 de la semilla 7, en la alineación. Su curva, respuesta a respuesta."""
    h = HABILIDADES["alineacion"]
    rng = np.random.default_rng(SEMILLA)
    for indice in range(1000):
        resp, valores, _ = simular_tecnico(h, rng, "dominio", UMBRAL)
        error_tardio = any(resp[i] and not resp[i + 1] for i in range(len(resp) - 1))
        if 6 <= len(resp) <= 10 and error_tardio and valores[-1] >= UMBRAL:
            break
    filas, prob = [], h["L0"]
    for i, r in enumerate(resp, 1):
        post, siguiente = actualizar(prob, r, h)
        filas.append({"Ejercicio": i, "Respuesta": "✓" if r else "✗", "Dominio antes": a.prob(prob),
                      "Después de la regla de Bayes": a.prob(post), "Después de practicar": a.prob(siguiente)})
        prob = siguiente
    g.curvas_de_dominio([("técnico de ejemplo", resp, valores)], [UMBRAL],
                        f"{h['nombre']}: el técnico de ejemplo, respuesta a respuesta")
    p.mostrar_tabla(filas, titulo="El dominio estimado, respuesta a respuesta",
                    pie=f"Parámetros: {_parametros_en_texto(h)}. Llega al umbral de {UMBRAL} en el ejercicio {len(resp)}.")
    a.anotar("2", "técnico de ejemplo", f"{h['nombre']}: {_simbolos(resp)}", "dominio final", round(valores[-1], 4))
    return {"respuestas": resp, "curva": valores}


# ----------------------------------------------------------------------------- 3. otras respuestas y otros parámetros

@amable
def comparar_parametros(respuestas, parametros_b) -> list | None:
    """Las mismas respuestas con los parámetros de la alineación (A) y con los tuyos (B)."""
    resp = leer_respuestas(respuestas, "RESPUESTAS")
    ha = HABILIDADES["alineacion"]
    hb = leer_parametros("PARAMETROS_B", parametros_b)
    ca, cb = curva(resp, ha), curva(resp, hb)
    g.curvas_de_dominio([("A: alineación", resp, ca), ("B: tus parámetros", resp, cb)], [UMBRAL],
                        "Las mismas respuestas, con dos juegos de parámetros")
    filas = [{"Ejercicio": i, "Respuesta": "✓" if r else "✗", "Dominio A": a.prob(ca[i]), "Dominio B": a.prob(cb[i])}
             for i, r in enumerate(resp, 1)]
    llega_a, llega_b = hasta_umbral(ca, UMBRAL), hasta_umbral(cb, UMBRAL)
    p.mostrar_tabla(filas, titulo="El dominio estimado después de cada respuesta",
                    pie=f"A: {_parametros_en_texto(ha)}. B: {_parametros_en_texto(hb)}. Llega al umbral de {UMBRAL}: "
                        f"A {('en el ejercicio ' + str(llega_a)) if llega_a else 'no llega'}; "
                        f"B {('en el ejercicio ' + str(llega_b)) if llega_b else 'no llega'}.")
    a.anotar("3", "otros parámetros", f"{_simbolos(resp)} con {_parametros_en_texto(hb)}", "dominio final de B",
             round(cb[-1], 4))
    if all(abs(ha[k] - hb[k]) < 1e-12 for k in CLAVES.values()):
        p.nota("A y B tienen los mismos parámetros, así que sus curvas coinciden. Cambia un parámetro de B, como la "
               "adivinanza.", "info")
    return filas


# ----------------------------------------------------------------------------- 4. la regla de selección

_ESTADOS: dict = {}


def _estados_de_referencia() -> dict:
    """El estado del generador al comenzar cada bloque de ejemplos/bkt_7b.py: así, 0.95 y 5 fijos dan sus cifras."""
    if not _ESTADOS:
        rng = np.random.default_rng(SEMILLA)
        for clave, h in HABILIDADES.items():
            _ESTADOS[(clave, "dominio")] = copy.deepcopy(rng.bit_generator.state)
            for _ in range(TECNICOS):
                simular_tecnico(h, rng, "dominio", UMBRAL)
            _ESTADOS[(clave, "fijo")] = copy.deepcopy(rng.bit_generator.state)
            for _ in range(TECNICOS):
                simular_tecnico(h, rng, "fijo", FIJO)
    return _ESTADOS


def simular_regla(clave: str, regla: str, valor: float) -> dict:
    """200 técnicos simulados con una regla. Cada regla parte del mismo punto de la semilla 7."""
    gen = np.random.Generator(np.random.PCG64())
    gen.bit_generator.state = copy.deepcopy(_estados_de_referencia()[(clave, "fijo" if regla == "fijo" else "dominio")])
    ejercicios, dominan = [], 0
    for _ in range(TECNICOS):
        resp, _, domina = simular_tecnico(HABILIDADES[clave], gen, regla, valor)
        ejercicios.append(len(resp))
        dominan += domina
    return {"ejercicios": float(np.mean(ejercicios)), "minimo": min(ejercicios), "maximo": max(ejercicios),
            "dominan": dominan / TECNICOS}


def _nombre_regla(regla: str, valor) -> str:
    return {"dominio": f"hasta dominar ({a.num(valor, 3)})", "fijo": f"siempre {int(valor)} ejercicios",
            "seguidos": f"{int(valor)} aciertos seguidos"}[regla]


def _leer_umbrales(nombre: str, umbrales) -> list:
    umbrales = a.lista_de_probabilidades(nombre, umbrales, "[0.85, 0.95, 0.99]")
    for u in umbrales:
        if u >= 1 or u <= 0:
            raise ErrorDeLaboratorio(f"{nombre} tiene un {a.num(u)}. Un umbral va entre 0 y 1, sin incluirlos: "
                                     "el tutor nunca está seguro del todo.")
    if len(set(umbrales)) < len(umbrales):
        raise ErrorDeLaboratorio(f"{nombre} repite un umbral. Escribe cada valor una sola vez.")
    return umbrales


def _leer_fijos(fijos) -> list:
    fijos = a.lista_de_numeros("FIJOS", fijos, "[5, 10]", minimo=1)
    for n in fijos:
        if n != int(n) or n > MAX_EJERCICIOS:
            raise ErrorDeLaboratorio(f"FIJOS tiene un {a.num(n)}. Cada valor es un número entero de ejercicios, de 1 a "
                                     f"{MAX_EJERCICIOS}.")
    return [int(n) for n in fijos]


@amable
def comparar_reglas(umbrales, fijos) -> list | None:
    """Compara reglas de selección con 200 técnicos simulados por habilidad: cuántos dominan y cuántos ejercicios hacen."""
    reglas = [("dominio", u) for u in _leer_umbrales("UMBRALES", umbrales)] + [("fijo", n) for n in _leer_fijos(fijos)]
    reglas.append(("seguidos", 3))
    filas, puntos, referencia = [], [], set()
    for clave, h in HABILIDADES.items():
        for regla, valor in reglas:
            r = simular_regla(clave, regla, valor)
            if regla == "seguidos":
                referencia.add(len(filas))
            filas.append({"Habilidad": h["nombre"], "Regla": _nombre_regla(regla, valor),
                          "Dominan al terminar": a.pct(r["dominan"]), "Avanzan sin dominar": a.pct(1 - r["dominan"]),
                          "Ejercicios en promedio": a.num(r["ejercicios"], 2),
                          "Mínimo y máximo": f"{r['minimo']} a {r['maximo']}"})
            puntos.append((h["nombre"], _nombre_regla(regla, valor), r["ejercicios"], r["dominan"]))
            if regla != "seguidos":
                a.anotar("4", "regla de selección", f"{h['nombre']}: {_nombre_regla(regla, valor)}",
                         "dominan al terminar", round(r["dominan"], 4))
    g.reglas_de_seleccion(puntos)
    compacta = []
    for regla, valor in reglas:
        fila = {"Regla": _nombre_regla(regla, valor)}
        for h in HABILIDADES.values():
            x = next(f for f in filas if f["Habilidad"] == h["nombre"] and f["Regla"] == _nombre_regla(regla, valor))
            fila[h["nombre"]] = f"{x['Avanzan sin dominar']} · {x['Ejercicios en promedio']} ej."
        compacta.append(fila)
    p.mostrar_tabla(compacta, titulo=f"Avanzan sin dominar, y ejercicios en promedio ({TECNICOS} técnicos en cada casilla)",
                    referencia={len(compacta) - 1},
                    pie="En gris, la referencia: avanzar tras tres aciertos seguidos, sin modelo del estudiante.")
    p.desplegable("Ver la tabla completa, con el mínimo y el máximo de ejercicios",
                  p.tabla_html(filas, referencia=referencia))
    if len(reglas) <= 3:
        p.nota("Agrega otros valores a las listas, como el umbral 0.85 y 10 ejercicios fijos. Así ves qué ganas y qué "
               "pierdes con cada regla.", "info")
    return filas


# ----------------------------------------------------------------------------- 6.1. el costo de la certeza

def _clave_habilidad(nombre) -> str:
    texto = _normal(nombre)
    for clave, h in HABILIDADES.items():
        if texto in (clave, _normal(h["nombre"])) or texto in _normal(h["nombre"]).split():
            return clave
    raise ErrorDeLaboratorio(f"No encuentro la habilidad {nombre!r}. Escribe \"bloqueo\", \"alineación\" o \"vibración\".")


@amable
def costo_de_la_certeza(habilidad, umbrales) -> list | None:
    """Cuántos ejercicios más cuesta cada punto de certeza: el umbral contra los ejercicios y el dominio real."""
    clave = _clave_habilidad(habilidad)
    umbrales = sorted(_leer_umbrales("UMBRALES_CERTEZA", umbrales))
    filas, datos = [], []
    for u in umbrales:
        r = simular_regla(clave, "dominio", u)
        datos.append((u, r["ejercicios"], r["dominan"]))
        filas.append({"Umbral": a.num(u, 3), "Ejercicios en promedio": a.num(r["ejercicios"], 2),
                      "Dominan al terminar": a.pct(r["dominan"]), "Avanzan sin dominar": a.pct(1 - r["dominan"])})
        a.anotar("6.1", "costo de la certeza", f"{HABILIDADES[clave]['nombre']}: umbral {a.num(u, 3)}",
                 "ejercicios en promedio", round(r["ejercicios"], 4))
    g.costo_de_la_certeza(datos, HABILIDADES[clave]["nombre"])
    p.mostrar_tabla(filas, titulo=f"{HABILIDADES[clave]['nombre']}: la certeza que pides y lo que cuesta")
    return filas


# ----------------------------------------------------------------------------- 6.3. tus propios datos (TI-2)

@amable
def mis_datos(habilidades, secuencias, umbrales) -> list | None:
    """Tus habilidades, sus parámetros y las respuestas de tus estudiantes ficticios: curvas y ejercicios hasta cada umbral."""
    if not isinstance(habilidades, dict) or not habilidades:
        raise ErrorDeLaboratorio("MIS_HABILIDADES debe ser un diccionario entre llaves, con una habilidad por línea.")
    if len(habilidades) > 5:
        raise ErrorDeLaboratorio(f"MIS_HABILIDADES tiene {len(habilidades)} habilidades. Usa 5 o menos: el TI-2 pide de 3 a 5.")
    params = {}
    for nombre, valores in habilidades.items():
        nombre = a.texto("El nombre de una habilidad de MIS_HABILIDADES", nombre)
        params[nombre] = leer_parametros(f"la habilidad «{nombre}»", valores)
    normales = {_normal(n): n for n in params}
    if not isinstance(secuencias, list) or not secuencias:
        raise ErrorDeLaboratorio("MIS_SECUENCIAS debe ser una lista entre corchetes. Cada elemento va entre paréntesis: "
                                 '("habilidad", "estudiante", "✓ ✗ ✓ ✓").')
    umbrales = sorted(_leer_umbrales("UMBRALES_TI", umbrales))
    por_habilidad, filas = {}, []
    for i, s in enumerate(secuencias, 1):
        if not isinstance(s, tuple) or len(s) != 3:
            raise ErrorDeLaboratorio(f"El elemento {i} de MIS_SECUENCIAS no tiene tres partes entre paréntesis. Escríbelo "
                                     'así: ("habilidad", "estudiante", "✓ ✗ ✓ ✓").')
        habilidad, estudiante, texto = s
        nombre = normales.get(_normal(habilidad)) if isinstance(habilidad, str) else None
        if nombre is None:
            raise ErrorDeLaboratorio(f"El elemento {i} de MIS_SECUENCIAS usa la habilidad {habilidad!r}, que no está en "
                                     f"MIS_HABILIDADES. Las habilidades son: {', '.join(params)}.")
        estudiante = a.texto(f"El estudiante del elemento {i} de MIS_SECUENCIAS", estudiante)
        resp = leer_respuestas(texto, f"las respuestas del elemento {i} de MIS_SECUENCIAS")
        valores = curva(resp, params[nombre])
        por_habilidad.setdefault(nombre, []).append((estudiante, resp, valores))
        fila = {"Habilidad": nombre, "Estudiante": estudiante, "Respuestas": _simbolos(resp),
                "Dominio al final": a.prob(valores[-1])}
        for u in umbrales:
            n = hasta_umbral(valores, u)
            fila[f"Ejercicios hasta {a.num(u, 3)}"] = str(n) if n is not None else "no llega"
        filas.append(fila)
    for nombre, curvas in por_habilidad.items():
        g.curvas_de_dominio(curvas, umbrales, f"{nombre} · {_parametros_en_texto(params[nombre])}")
    p.mostrar_tabla(filas, titulo="Tus estudiantes ficticios: el dominio estimado y los ejercicios hasta cada umbral",
                    pie="Cuenta los ejercicios hasta la primera vez que el dominio llega al umbral. Ahí el tutor ya lo "
                        "deja avanzar, aunque después baje. «No llega»: el tutor le pediría más ejercicios.")
    return filas
