"""El LLM como experto sin datos (Laboratorio 6A): escribe reglas de supervivencia y el notebook las aplica.

El LLM no ve a ningún pasajero. Recibe la descripción de las variables y escribe de 3 a 5 reglas en un formato fijo,
una lista de decisión como la base de reglas de un sistema experto: gana la primera regla que se cumpla. Este módulo lee
cada línea, la aplica a los 1309 pasajeros y cuenta cuántos acierta. Una línea que no cumple el formato no se adivina:
se muestra como «no válida» y se ignora.
"""
from __future__ import annotations

import re
import time

import numpy as np

import presentacion as p
from arboles import NO_SOBREVIVE, SOBREVIVE, ErrorDeLaboratorio, _ESTADO, _amable, _normal, _pct, _registrar

PUERTOS_ANONIMOS = {"a": "Southampton", "b": "Cherbourg", "c": "Queenstown"}
VARIABLES = """* sexo: mujer u hombre
* edad: en años (puede faltar)
* clase: 1, 2 o 3 (la clase del pasaje)
* tarifa: lo que pagó por el pasaje, en {moneda}
* hermanos_o_conyuge: cuántos hermanos o cónyuge viajaban con el pasajero
* padres_o_hijos: cuántos padres o hijos viajaban con el pasajero
* puerto: dónde embarcó ({puertos})"""
FORMATO = """Escriba de 3 a 5 reglas, una por línea, con este formato exacto:
SI <condición> ENTONCES sobrevive
SI <condición> Y <condición> ENTONCES no sobrevive
Cada condición es: variable operador valor. Los operadores son = , != , < , <= , > , >=.
Las reglas se aplican en orden: gana la primera que se cumpla. Termine con una línea:
EN OTRO CASO sobrevive   (o EN OTRO CASO no sobrevive)
No escriba nada más: ni títulos, ni explicaciones, ni numeración."""
INSTRUCCIONES = {
    "titanic": ("Usted es un historiador marítimo. Sin ver ningún dato, escriba las reglas que, según su conocimiento, "
                "predicen qué pasajeros del Titanic (1912) sobrevivieron al naufragio.\n\nVariables disponibles:\n"
                + VARIABLES.format(moneda="libras de 1912", puertos="Southampton, Cherbourg o Queenstown") + "\n\n" + FORMATO),
    "anonimo": ("Usted es un historiador marítimo. Sin ver ningún dato, escriba las reglas que, según su conocimiento, "
                "predicen qué pasajeros de un barco de pasajeros que naufragó hace más de un siglo sobrevivieron.\n\n"
                "Variables disponibles:\n" + VARIABLES.format(moneda="libras de la época", puertos="A, B o C")
                + "\n\n" + FORMATO),
}
NOMBRES = {"titanic": "con el nombre del Titanic", "anonimo": "sin nombrar el barco"}
_OPERADORES = {"=": lambda a, b: a == b, "!=": lambda a, b: a != b, "<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
               ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}
_VARIABLES = {"sexo": "sexo", "edad": "edad", "clase": "clase", "tarifa": "tarifa", "hermanos_o_conyuge": "hermanos_o_conyuge",
              "hermanos o conyuge": "hermanos_o_conyuge", "padres_o_hijos": "padres_o_hijos", "padres o hijos": "padres_o_hijos",
              "puerto": "puerto"}


def _valor(variable: str, texto: str, version: str):
    """Convierte el valor escrito por el LLM al tipo de la variable, o None si no se entiende."""
    t = _normal(texto).strip(" .'\"").replace("años", "").replace("anos", "").replace("£", "").replace("libras", "").strip()
    if variable == "sexo":
        return {"mujer": "mujer", "femenino": "mujer", "female": "mujer", "mujeres": "mujer",
                "hombre": "hombre", "masculino": "hombre", "male": "hombre", "hombres": "hombre"}.get(t)
    if variable == "puerto":
        if version == "anonimo" and t in PUERTOS_ANONIMOS:
            return PUERTOS_ANONIMOS[t]
        return {"southampton": "Southampton", "cherbourg": "Cherbourg", "queenstown": "Queenstown"}.get(t)
    if variable == "clase":
        t = {"primera": "1", "segunda": "2", "tercera": "3"}.get(t, t).replace(".a", "").replace("ª", "")
    try:
        return float(t.replace(",", "."))
    except ValueError:
        return None


def leer_reglas(texto: str, version: str = "titanic"):
    """Lee la respuesta del LLM: las reglas válidas, las líneas que no se pudieron leer y la conclusión por defecto."""
    reglas, invalidas, defecto = [], [], None
    for linea in texto.splitlines():
        original = linea.strip()
        if not original or original.startswith("```"):     # las líneas vacías y las cercas de código no son reglas
            continue
        l = original.replace("**", "").replace("`", "")      # primero el formato de Markdown, después la viñeta
        l = re.sub(r"^\s*(\d+[.)]|[-*•])\s*", "", l)
        l = (l.replace("≤", "<=").replace("≥", ">=").replace("≠", "!=").replace("==", "=").replace("<>", "!=")
             .replace("=<", "<=").replace("=>", ">=").strip())
        m = re.match(r"(?i)^en otro caso\s*[:,]?\s*(no sobrevive|sobrevive)\s*\.?$", l)
        if m:
            defecto = SOBREVIVE if m.group(1).lower() == "sobrevive" else NO_SOBREVIVE
            continue
        m = re.match(r"(?i)^si\s+(.+?)\s+entonces\s+(no sobrevive|sobrevive)\s*\.?$", l)
        if not m:
            invalidas.append(original)
            continue
        condiciones, valida = [], True
        for c in re.split(r"(?i)\s+y\s+", m.group(1)):
            mc = re.match(r"^\s*([a-záéíóúñ_ ]+?)\s*(!=|<=|>=|=|<|>)\s*(.+?)\s*$", c, re.I)
            if not mc or _normal(mc.group(1)) not in _VARIABLES:
                valida = False
                break
            variable, operador = _VARIABLES[_normal(mc.group(1))], mc.group(2)
            valor = _valor(variable, mc.group(3), version)
            if valor is None or (variable in ("sexo", "puerto") and operador not in ("=", "!=")):
                valida = False
                break
            condiciones.append((variable, operador, valor))
        if valida and condiciones:
            reglas.append({"texto": original, "condiciones": condiciones,
                           "entonces": SOBREVIVE if m.group(2).lower() == "sobrevive" else NO_SOBREVIVE})
        else:
            invalidas.append(original)
    return reglas, invalidas, defecto


def _cumple(pasajero: dict, condiciones: list) -> bool:
    for variable, operador, valor in condiciones:
        dato = pasajero[variable]
        if dato is None or dato == "":
            return False        # un dato desconocido no cumple la condición
        if not _OPERADORES[operador](dato, valor):
            return False
    return True


def aplicar(reglas: list, defecto, filas: list):
    """Aplica la lista de decisión a cada pasajero: la primera regla que se cumple decide; si ninguna, la de otro caso."""
    prediccion, usada = [], []
    for pasajero in filas:
        for k, r in enumerate(reglas):
            if _cumple(pasajero, r["condiciones"]):
                prediccion.append(r["entonces"])
                usada.append(k)
                break
        else:
            prediccion.append(defecto or NO_SOBREVIVE)
            usada.append(-1)
    return np.array(prediccion), np.array(usada)


def _aciertos(dicho, real) -> str:
    """«27 de 86 (31 %)»: los aciertos de una regla entre los pasajeros sobre los que decide."""
    n, bien = len(real), int((dicho == real).sum())
    return f"{bien} de {n}" + (f" ({_pct(bien / n, 0)})" if n else "")


@_amable
def pedir_reglas(llm, datos, version: str = "titanic") -> dict | None:
    """Pide al LLM sus reglas, las aplica a los pasajeros y las compara con la regla del experto y con el árbol."""
    if datos is None or datos.propio:
        raise ErrorDeLaboratorio("Las reglas del LLM se aplican a los pasajeros del Titanic: ejecute antes la sección 1.")
    if llm is None:
        raise ErrorDeLaboratorio("No hay un cliente del LLM: ejecute la celda de la sección 0 que lo crea.")
    if version not in INSTRUCCIONES:
        raise ErrorDeLaboratorio(f"VERSION debe ser \"titanic\" o \"anonimo\"; escribió {version!r}.")
    instruccion = INSTRUCCIONES[version]
    inicio = time.perf_counter()
    try:
        respuesta = llm.completar(instruccion, etiqueta=f"reglas-{version}", max_tokens_respuesta=600)
    except Exception as e:      # sin red, sin saldo o el servidor caído: se explica y el notebook sigue
        p.nota(f"El LLM no respondió: {e}", "error", "Sin respuesta del LLM")
        return None
    if not respuesta.disponible:
        return None
    p.mostrar_conversacion([{"rol": "user", "contenido": instruccion}, {"rol": "assistant", "contenido": respuesta.texto}],
                           titulo=f"La instrucción y la respuesta del LLM ({NOMBRES[version]})",
                           etiquetas={"user": "La instrucción, igual para todas las parejas"})
    reglas, invalidas, defecto = leer_reglas(respuesta.texto, version)
    if not reglas:
        p.nota("Ninguna línea de la respuesta cumple el formato pedido, así que no hay reglas que aplicar. Eso también es un "
               "resultado: anótelo en su análisis.", "aviso", "Sin reglas válidas")
        return {"reglas": [], "invalidas": invalidas, "acierto": None}
    prediccion, usada = aplicar(reglas, defecto, datos.filas)
    tabla = []
    for k, r in enumerate(reglas):
        m = usada == k
        tabla.append({"#": k + 1, "regla del LLM": r["texto"], "decide sobre": f"{int(m.sum())} pasajeros",
                      "acierta": _aciertos(prediccion[m], datos.y[m])})
    m = usada == -1
    tabla.append({"#": "—", "regla del LLM": f"EN OTRO CASO {defecto or NO_SOBREVIVE}"
                  + ("" if defecto else " (el LLM no la escribió; se usa «no sobrevive»)"),
                  "decide sobre": f"{int(m.sum())} pasajeros", "acierta": _aciertos(prediccion[m], datos.y[m])})
    for linea in invalidas:
        tabla.append({"#": "✗", "regla del LLM": linea, "decide sobre": "no válida: no cumple el formato", "acierta": "—"})
    p.mostrar_tabla(tabla, titulo="Las reglas del LLM, aplicadas en orden a los 1309 pasajeros")
    acierto = float((prediccion == datos.y).mean())
    comparacion = [{"método": "Responder siempre «no sobrevive»", "acierto": _pct((datos.y == NO_SOBREVIVE).mean())}]
    if "experto" in _ESTADO:
        comparacion.append({"método": "La regla del experto (sección 1)", "acierto": _pct(_ESTADO["experto"])})
    comparacion.append({"método": f"Las reglas del LLM ({NOMBRES[version]})", "acierto": _pct(acierto)})
    if "arbol_cv" in _ESTADO:
        comparacion.append({"método": f"El árbol de profundidad {_ESTADO['profundidad']} (validación cruzada)",
                            "acierto": _pct(_ESTADO["arbol_cv"])})
    p.mostrar_tabla(comparacion, titulo="¿Quién acierta más?")
    p.nota(llm.texto_resumen(), "neutro", "Consumo del LLM")
    _registrar(datos, "LLM", f"reglas sin datos, {NOMBRES[version]}", respuesta.proveedor, respuesta.modelo, prediccion,
               time.perf_counter() - inicio, llamadas=1, tokens_entrada=respuesta.tokens_entrada,
               tokens_salida=respuesta.tokens_salida, costo_usd=respuesta.costo_usd or 0.0)
    return {"reglas": reglas, "invalidas": invalidas, "acierto": acierto, "texto": respuesta.texto}
