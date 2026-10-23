"""Las tres estrategias del Laboratorio 2B (LLM-Modulo en práctica).

- Estrategia 1: el LLM planifica directamente.
- Estrategia 2: el LLM traduce la orden escrita a PDDL y Fast Downward resuelve.
- Estrategia 3: ciclo generar-verificar; el validador devuelve sus críticas al LLM.

Cada estrategia devuelve un Resultado con sus métricas. Los resultados se muestran en una
tabla y en un gráfico, y se exportan a CSV con el esquema común del contrapunto LLM del curso.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import presentacion as p
import utilidades_pddl as u

INSTANCIAS = {
    "ot512": {"titulo": "OT-512 · bomba 3", "dominio": "pddl/mantenia_dominio.pddl",
              "problema": "pddl/ot512.pddl", "orden": "ordenes/ot512.md"},
    "ot518": {"titulo": "OT-518 · bomba 3 y compresor 2", "dominio": "pddl/mantenia_dominio.pddl",
              "problema": "pddl/ot518.pddl", "orden": "ordenes/ot518.md"},
    "ot530": {"titulo": "OT-530 · tres equipos y tres técnicos", "dominio": "pddl/mantenia_dominio.pddl",
              "problema": "pddl/ot530.pddl", "orden": "ordenes/ot530.md"},
    "ot512_sin_solucion": {"titulo": "OT-512 sin técnico certificado", "dominio": "pddl/mantenia_dominio.pddl",
                           "problema": "pddl/ot512_sin_solucion.pddl", "orden": "ordenes/ot512_sin_solucion.md"},
    "ot512_misterio": {"titulo": "OT-512 «misterio» (nombres ofuscados)", "dominio": "pddl/misterio_dominio.pddl",
                       "problema": "pddl/misterio_ot512.pddl", "orden": None},
}

NOMBRES = {"e1": "E1 · el LLM planifica", "e2": "E2 · el LLM traduce y Fast Downward resuelve",
           "e3": "E3 · generar y verificar", "fd": "Fast Downward (referencia clásica)"}

SISTEMA = ("Eres un asistente de planificación de MantenIA, una empresa de mantenimiento industrial. "
           "Respondes exactamente en el formato que se te pide, sin explicaciones adicionales.")

GUIA_PDDL = ("Cómo leer el PDDL: cada acción tiene parámetros (las variables que empiezan con ?), precondiciones "
             "(los hechos que deben ser ciertos para aplicarla) y efectos (los hechos que agrega; los que aparecen "
             "dentro de (not ...) son los que elimina). Todo hecho que no aparece en el estado inicial es falso.")

COLUMNAS_CSV = ["sesion", "laboratorio", "pareja", "fecha", "tarea", "instancia", "metodo", "estrategia", "proveedor",
                "modelo", "correcto", "resultado", "iteraciones", "llamadas", "tokens_entrada", "tokens_salida",
                "tokens_razonamiento", "costo_usd", "tiempo_s", "notas"]


@dataclass
class Resultado:
    """Resultado de una estrategia sobre una instancia."""
    instancia: str
    estrategia: str             # "e1", "e2", "e3" o "fd"
    metodo: str                 # "llm", "hibrido" o "clasico"
    correcto: bool = False      # plan válido o, si no hay solución, reconocerlo
    resultado: str = ""         # descripción breve en español
    iteraciones: int = 0
    llamadas: int = 0
    tokens_entrada: int = 0
    tokens_salida: int = 0
    tokens_razonamiento: int = 0
    costo_usd: float | None = 0.0
    tiempo_s: float = 0.0
    proveedor: str = ""
    modelo: str = ""
    pasos: list = field(default_factory=list)
    conversacion: list = field(default_factory=list)
    notas: str = ""
    disponible: bool = True


# ----------------------------------------------------------------------------- datos de las instancias

_SOLUCION = {}


def cargar(clave: str):
    """Devuelve (texto del dominio, texto del problema, problema de Unified Planning, orden escrita o None)."""
    inst = INSTANCIAS[clave]
    dominio = Path(inst["dominio"]).read_text(encoding="utf-8")
    problema = Path(inst["problema"]).read_text(encoding="utf-8")
    orden = Path(inst["orden"]).read_text(encoding="utf-8") if inst["orden"] else None
    return dominio, problema, u.leer_problema(dominio, problema), orden


def tiene_solucion(clave: str) -> bool:
    """Si el problema de referencia tiene solución (lo decide Fast Downward; se calcula una vez)."""
    if clave not in _SOLUCION:
        _SOLUCION[clave] = u.resolver(cargar(clave)[2]).estado == "resuelto"
    return _SOLUCION[clave]


# ----------------------------------------------------------------------------- instrucciones y críticas

def instrucciones_planificar(dominio: str, problema: str) -> str:
    """Instrucción de las estrategias 1 y 3: dominio y problema en PDDL; se pide el plan."""
    return (f"{GUIA_PDDL}\n\n## Dominio\n{dominio.strip()}\n\n## Problema\n{problema.strip()}\n\n## Tarea\n"
            "Encuentra un plan que lleve del estado inicial a la meta. Cada acción solo se puede aplicar si en ese "
            "momento se cumplen todas sus precondiciones.\n"
            "Responde SOLO con el plan: una acción por línea, en formato PDDL, por ejemplo:\n"
            "(nombre-de-accion objeto1 objeto2)\n"
            "Si no existe ningún plan posible, responde exactamente: SIN PLAN")


def instrucciones_traducir(dominio: str, orden: str) -> str:
    """Instrucción de la estrategia 2: dominio en PDDL y orden escrita; se pide el problema en PDDL."""
    return (f"{GUIA_PDDL}\n\n## Dominio\n{dominio.strip()}\n\n## Orden de trabajo\n{orden.strip()}\n\n## Tarea\n"
            "Traduce la orden de trabajo a un problema PDDL para este dominio. Usa solo los tipos y predicados del "
            "dominio, y para los objetos usa exactamente los códigos que aparecen entre comillas invertidas en la orden. "
            "Declara todos los objetos en :objects con su tipo, escribe en :init todos los hechos que la orden afirma "
            "(lo que no escribas se considerará falso) y en :goal lo que debe lograrse; si hay varios hechos, "
            "agrúpalos con (and ...).\n"
            "Sigue esta estructura: (define (problem nombre) (:domain nombre-del-dominio) (:objects ...) (:init ...) (:goal ...))\n"
            "Responde SOLO con el problema en PDDL, empezando por (define (problem")


def critica(juicio) -> str:
    """Convierte el veredicto del validador (o un error de lectura) en una crítica para el LLM."""
    cierre = ("Corrige el plan y responde de nuevo SOLO con el plan completo, una acción por línea, "
              "o SIN PLAN si concluyes que no existe ninguno.")
    if isinstance(juicio, u.ResultadoLectura):
        if juicio.estado == "ilegible" and not juicio.pasos:
            return "No encontré acciones en tu respuesta con el formato (accion objeto1 objeto2). " + cierre
        if juicio.estado == "ilegible":
            return ("Algunas líneas de tu plan no tienen el formato de una acción:\n- "
                    + "\n- ".join(juicio.errores) + "\n" + cierre)
        return ("Tu plan usa acciones u objetos que no existen en el dominio o en el problema:\n- "
                + "\n- ".join(juicio.errores) + "\n" + cierre)
    if juicio.motivo == "precondicion":
        return (f"El validador rechazó tu plan. El paso {juicio.paso}, {juicio.accion}, no se puede aplicar porque en "
                f"ese momento no se cumple: {', '.join(juicio.faltantes)}. " + cierre)
    return ("El validador rechazó tu plan. Todas las acciones se pueden aplicar, pero al final no se cumple la meta: "
            f"falta {', '.join(juicio.faltantes)}. " + cierre)


def _extraer_problema(texto: str):
    """Extrae el bloque (define (problem ...)) de una respuesta, aunque venga con texto alrededor."""
    i = texto.find("(define")
    if i < 0:
        return None
    profundidad = 0
    for j in range(i, len(texto)):
        if texto[j] == "(":
            profundidad += 1
        elif texto[j] == ")":
            profundidad -= 1
            if profundidad == 0:
                return texto[i:j + 1]
    return texto[i:]


def _etiqueta(estrategia: str, clave: str, llamada: int, repeticion: int) -> str:
    """Nombre único de cada llamada (sirve para grabar y reproducir respuestas)."""
    return f"2b/{estrategia}/{clave}/{llamada}" + (f"/r{repeticion}" if repeticion > 1 else "")


def _acumular(res: Resultado, respuesta) -> None:
    res.llamadas += 1
    res.tokens_entrada += respuesta.tokens_entrada
    res.tokens_salida += respuesta.tokens_salida
    res.tokens_razonamiento += respuesta.tokens_razonamiento
    res.tiempo_s = round(res.tiempo_s + respuesta.segundos, 2)
    if respuesta.costo_usd is None or res.costo_usd is None:
        res.costo_usd = None
    else:
        res.costo_usd = round(res.costo_usd + respuesta.costo_usd, 6)
    res.proveedor = "grabado" if respuesta.grabada else respuesta.proveedor
    res.modelo = respuesta.modelo


def _juzgar_plan(res: Resultado, problema, texto: str, clave: str):
    """Lee y valida el plan del LLM; actualiza el resultado y devuelve el juicio (para la crítica)."""
    hay = tiene_solucion(clave)
    lectura = u.plan_desde_texto(problema, texto)
    res.pasos = lectura.pasos
    formato = ("Formato: " + " ".join(lectura.avisos) + " ") if lectura.avisos else ""
    if lectura.estado == "sin_plan":
        res.correcto = not hay
        res.resultado = "reconoce que no hay plan" if not hay else "dice que no hay plan, pero sí existe"
        res.notas = ""
        return None
    if lectura.estado != "ok":
        res.correcto = False
        res.resultado = "formato ilegible" if lectura.estado == "ilegible" else "acción u objeto inexistente"
        res.notas = (formato + "; ".join(lectura.errores))[:400]
        return lectura
    validacion = u.validar(problema, lectura.plan)
    res.correcto = validacion.valido
    if validacion.valido:
        res.resultado = "plan válido"
        res.notas = formato.strip()
    else:
        res.resultado = {"precondicion": "precondición incumplida", "meta": "meta no alcanzada"}[validacion.motivo]
        if not hay:
            res.resultado += "; inventa un plan para un problema sin solución"
        res.notas = (formato + validacion.explicacion)[:400]
    return validacion


# ----------------------------------------------------------------------------- estrategias

def estrategia_1(llm, clave: str, repeticion: int = 1) -> Resultado:
    """El LLM recibe el dominio y el problema en PDDL, y devuelve un plan."""
    dominio, texto_problema, problema, _ = cargar(clave)
    res = Resultado(clave, "e1", "llm", proveedor=llm.proveedor, modelo=llm.modelo)
    instruccion = instrucciones_planificar(dominio, texto_problema)
    respuesta = llm.completar([{"role": "user", "content": instruccion}], sistema=SISTEMA, etiqueta=_etiqueta("e1", clave, 1, repeticion))
    if not respuesta.disponible:
        res.disponible, res.resultado = False, "sin respuesta (no hay una respuesta grabada para esta instrucción)"
        return res
    _acumular(res, respuesta)
    res.iteraciones = 1
    res.conversacion = [{"rol": "system", "contenido": SISTEMA}, {"rol": "user", "contenido": instruccion},
                        {"rol": "assistant", "contenido": respuesta.texto}]
    _juzgar_plan(res, problema, respuesta.texto, clave)
    return res


def estrategia_2(llm, clave: str, max_reintentos: int = 2, repeticion: int = 1) -> Resultado:
    """El LLM traduce la orden escrita a un problema PDDL; Fast Downward lo resuelve; el plan se valida contra la referencia."""
    dominio, _, referencia, orden = cargar(clave)
    res = Resultado(clave, "e2", "hibrido", proveedor=llm.proveedor, modelo=llm.modelo)
    if orden is None:
        res.disponible, res.resultado = False, "no aplica a la versión misterio"
        return res
    instruccion = instrucciones_traducir(dominio, orden)
    mensajes = [{"role": "user", "content": instruccion}]
    res.conversacion = [{"rol": "system", "contenido": SISTEMA}, {"rol": "user", "contenido": instruccion}]
    traducido = None
    for intento in range(1, max_reintentos + 2):
        respuesta = llm.completar(mensajes, sistema=SISTEMA, etiqueta=_etiqueta("e2", clave, intento, repeticion),
                                  max_tokens_respuesta=2000)
        if not respuesta.disponible:
            res.disponible = res.llamadas > 0
            res.resultado = "sin respuesta (no hay una respuesta grabada para esta instrucción)"
            return res
        _acumular(res, respuesta)
        res.iteraciones = intento
        res.conversacion.append({"rol": "assistant", "contenido": respuesta.texto})
        texto_pddl = _extraer_problema(respuesta.texto) or respuesta.texto
        try:
            traducido = u.leer_problema(dominio, texto_pddl)
            break
        except u.ErrorPDDL as error:
            if intento > max_reintentos:
                res.resultado, res.notas = "PDDL ilegible", str(error)[:300]
                return res
            texto_critica = (f"El problema PDDL no se pudo leer. {error}\n"
                             "Corrige el error y responde de nuevo SOLO con el problema PDDL completo.")
            mensajes += [{"role": "assistant", "content": respuesta.texto}, {"role": "user", "content": texto_critica}]
            res.conversacion.append({"rol": "critica", "contenido": texto_critica})
    diferencias = u.comparar_problemas(referencia, traducido)
    detalle = [f"{k.replace('_', ' ')}: {', '.join(v)}" for k, v in diferencias.items() if v]
    planificacion = u.resolver(traducido)
    res.tiempo_s = round(res.tiempo_s + planificacion.segundos, 2)
    hay = tiene_solucion(clave)
    if planificacion.estado == "sin_solucion":
        res.correcto = not hay
        res.resultado = ("el planificador demuestra que no hay plan" if not hay
                         else "la traducción no tiene solución, pero la orden real sí")
    elif planificacion.estado == "resuelto":
        res.pasos = planificacion.pasos
        lectura = u.plan_desde_texto(referencia, "\n".join(planificacion.pasos))
        if lectura.estado != "ok":
            res.correcto, res.resultado = False, "la traducción usa nombres que la orden no tiene"
        else:
            validacion = u.validar(referencia, lectura.plan)
            res.correcto = validacion.valido
            res.resultado = ("plan válido" if validacion.valido
                             else "plan inválido en la orden real: error de significado en la traducción")
    else:
        res.correcto, res.resultado = False, "el planificador no terminó"
    res.notas = ("traducción idéntica a la referencia" if not detalle else "; ".join(detalle))[:300]
    return res


def estrategia_3(llm, clave: str, K: int = 5, repeticion: int = 1) -> Resultado:
    """Ciclo generar-verificar: hasta K planes; cada rechazo del validador vuelve al LLM como crítica."""
    dominio, texto_problema, problema, _ = cargar(clave)
    res = Resultado(clave, "e3", "hibrido", proveedor=llm.proveedor, modelo=llm.modelo)
    instruccion = instrucciones_planificar(dominio, texto_problema)
    mensajes = [{"role": "user", "content": instruccion}]
    res.conversacion = [{"rol": "system", "contenido": SISTEMA}, {"rol": "user", "contenido": instruccion}]
    for iteracion in range(1, K + 1):
        respuesta = llm.completar(mensajes, sistema=SISTEMA, etiqueta=_etiqueta("e3", clave, iteracion, repeticion))
        if not respuesta.disponible:
            res.disponible = res.llamadas > 0
            res.resultado = res.resultado or "sin respuesta (no hay una respuesta grabada para esta instrucción)"
            return res
        _acumular(res, respuesta)
        res.iteraciones = iteracion
        res.conversacion.append({"rol": "assistant", "contenido": respuesta.texto})
        juicio = _juzgar_plan(res, problema, respuesta.texto, clave)
        if res.correcto or juicio is None:  # plan válido, o el LLM afirma que no hay plan
            return res
        texto_critica = critica(juicio)
        mensajes += [{"role": "assistant", "content": respuesta.texto}, {"role": "user", "content": texto_critica}]
        res.conversacion.append({"rol": "critica", "contenido": texto_critica})
    res.resultado += f" (tras {K} iteraciones)"
    return res


def fast_downward(clave: str) -> Resultado:
    """Referencia clásica: Fast Downward sobre el problema de referencia, validado."""
    _, _, problema, _ = cargar(clave)
    planificacion = u.resolver(problema)
    res = Resultado(clave, "fd", "clasico", iteraciones=1, proveedor="local", modelo="Fast Downward (lama-first)",
                    tiempo_s=round(planificacion.segundos, 2), costo_usd=0.0, pasos=planificacion.pasos)
    if planificacion.estado == "resuelto":
        res.correcto = u.validar(problema, planificacion.plan).valido
        res.resultado = "plan válido" if res.correcto else "plan inválido"
    else:
        res.correcto = planificacion.estado == "sin_solucion"
        res.resultado = "demuestra que no hay plan" if res.correcto else "no terminó"
    return res


ESTRATEGIAS = {"e1": estrategia_1, "e2": estrategia_2, "e3": estrategia_3}


# ----------------------------------------------------------------------------- presentación y exportación

def _num(valor, decimales: int = 0) -> str:
    """Número en formato español: espacio para los miles y coma decimal."""
    return f"{valor:,.{decimales}f}".replace(",", " ").replace(".", ",")


def _costo(res: Resultado) -> str:
    if res.costo_usd is None:
        return "—"
    return "0" if res.costo_usd == 0 else _num(res.costo_usd, 5)


def mostrar_resultado(res: Resultado, abierta: bool = False) -> None:
    """Muestra el resultado de una estrategia: veredicto, métricas, plan y conversación."""
    titulo = f"{NOMBRES[res.estrategia]} · {INSTANCIAS[res.instancia]['titulo']}"
    if not res.disponible:
        p.nota(res.resultado, "aviso", titulo)
        return
    metricas = (f"Iteraciones: {res.iteraciones} · llamadas: {res.llamadas} · tokens: {_num(res.tokens_entrada)} de entrada y "
                f"{_num(res.tokens_salida)} de salida · costo: US${_costo(res)} · tiempo: {_num(res.tiempo_s, 1)} s · "
                f"{'planificador' if res.estrategia == 'fd' else 'LLM'}: {res.modelo}")
    texto = f"{'✓' if res.correcto else '✗'} {res.resultado}.\n{metricas}" + (f"\nDetalle: {res.notas}" if res.notas else "")
    p.nota(texto, "exito" if res.correcto else "error", titulo)
    if res.pasos:
        p.mostrar_plan(res.pasos, "Plan del LLM" if res.estrategia in ("e1", "e3") else "Plan de Fast Downward sobre la traducción del LLM")
    if res.conversacion:
        p.mostrar_conversacion(res.conversacion, "Conversación con el LLM", abierta=abierta)


def _breve(texto: str, n: int = 140) -> str:
    texto = re.sub(r"\s+", " ", texto or "").strip()
    return texto if len(texto) <= n else texto[:n - 1].rstrip() + "…"


def tabla(resultados) -> None:
    """Tabla resumen de los resultados, con el detalle de cada uno (abreviado)."""
    filas = [{"instancia": INSTANCIAS[r.instancia]["titulo"], "estrategia": NOMBRES[r.estrategia],
              "correcto": ("✓" if r.correcto else "✗") if r.disponible else "—", "resultado": r.resultado,
              "iteraciones": r.iteraciones, "tokens": _num(r.tokens_entrada + r.tokens_salida),
              "costo (US$)": _costo(r), "tiempo (s)": _num(r.tiempo_s, 1), "detalle": _breve(r.notas)}
             for r in resultados]
    p.mostrar_tabla(filas, titulo="Resultados")


def detalles(resultados) -> None:
    """Muestra completos los casos que más enseñan: fallos, varias iteraciones, notas de formato o diferencias."""
    casos = [r for r in resultados if r.disponible and r.estrategia != "fd" and
             (not r.correcto or r.iteraciones > 1 or r.notas.startswith("Formato")
              or (r.estrategia == "e2" and r.notas and r.notas != "traducción idéntica a la referencia"))]
    if not casos:
        p.nota("Todas las estrategias acertaron a la primera, sin notas de formato ni diferencias en la traducción.", "info")
    for r in casos:
        mostrar_resultado(r)


def grafico(resultados) -> None:
    """Gráfico comparativo por estrategia: resultados correctos, tiempo medio y tokens medios."""
    import matplotlib.pyplot as plt
    orden = [e for e in ("e1", "e2", "e3", "fd") if any(r.estrategia == e and r.disponible for r in resultados)]
    etiquetas = {"e1": "E1\nplanifica", "e2": "E2\ntraduce", "e3": "E3\ngenera y\nverifica", "fd": "Fast\nDownward"}
    colores = {"e1": "#7c3aed", "e2": "#2563eb", "e3": "#059669", "fd": "#6b7280"}
    fig, ejes = plt.subplots(1, 3, figsize=(12, 3.6))
    grupos = {e: [r for r in resultados if r.estrategia == e and r.disponible] for e in orden}
    nombres = [etiquetas[e] for e in orden]
    # 1. Proporción de resultados correctos, con su denominador: cada estrategia se aplica a un número distinto de instancias
    porcentajes = [100 * sum(r.correcto for r in grupos[e]) / len(grupos[e]) if grupos[e] else 0 for e in orden]
    barras = ejes[0].bar(nombres, porcentajes, color=[colores[e] for e in orden])
    ejes[0].bar_label(barras, labels=[f"{sum(r.correcto for r in grupos[e])}/{len(grupos[e])}" for e in orden], fontsize=9)
    ejes[0].set_title("Resultados correctos (% y aciertos/instancias)", fontsize=11)
    ejes[0].set_ylim(0, 115)
    # 2 y 3. Tiempo y tokens medios por instancia
    for eje, titulo, valor in [(ejes[1], "Tiempo medio por instancia (s)", lambda rs: sum(r.tiempo_s for r in rs) / len(rs)),
                               (ejes[2], "Tokens medios por instancia",
                                lambda rs: sum(r.tokens_entrada + r.tokens_salida for r in rs) / len(rs))]:
        valores = [valor(grupos[e]) if grupos[e] else 0 for e in orden]
        barras = eje.bar(nombres, valores, color=[colores[e] for e in orden])
        eje.bar_label(barras, labels=[_num(v, 1) if "Tiempo" in titulo else _num(v) for v in valores], fontsize=9)
        eje.set_title(titulo, fontsize=11)
    from matplotlib.ticker import FuncFormatter
    for eje in ejes:
        eje.spines[["top", "right"]].set_visible(False)
        eje.yaxis.set_major_formatter(FuncFormatter(lambda v, _: _num(v, 0 if float(v).is_integer() else 1)))
    fig.text(0.5, -0.04, "Las medias se calculan sobre las instancias en que se aplicó cada estrategia: la estrategia 2 "
                          "no incluye la versión misterio.", ha="center", fontsize=9, color="#555555")
    fig.tight_layout()
    plt.show()


def exportar_csv(resultados, pareja: str, ruta: str = "resultados_2B.csv") -> Path:
    """Exporta los resultados con el esquema común del contrapunto LLM (se reutiliza en las sesiones 3 a 7)."""
    ruta = Path(ruta)
    with ruta.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS_CSV)
        escritor.writeheader()
        for r in resultados:
            if not r.disponible:
                continue
            escritor.writerow({"sesion": 2, "laboratorio": "2B", "pareja": pareja, "fecha": date.today().isoformat(),
                               "tarea": "planificacion-mantenia", "instancia": r.instancia, "metodo": r.metodo,
                               "estrategia": NOMBRES[r.estrategia], "proveedor": r.proveedor, "modelo": r.modelo,
                               "correcto": int(r.correcto), "resultado": r.resultado, "iteraciones": r.iteraciones,
                               "llamadas": r.llamadas, "tokens_entrada": r.tokens_entrada, "tokens_salida": r.tokens_salida,
                               "tokens_razonamiento": r.tokens_razonamiento,
                               "costo_usd": "" if r.costo_usd is None else r.costo_usd, "tiempo_s": r.tiempo_s,
                               "notas": re.sub(r"\s+", " ", r.notas)})
    return ruta
