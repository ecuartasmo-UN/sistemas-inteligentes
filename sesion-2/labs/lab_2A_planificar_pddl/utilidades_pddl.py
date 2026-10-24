"""Utilidades de planificación para los laboratorios de la Sesión 2 de Sistemas Inteligentes.

Envuelven Unified Planning y Fast Downward con mensajes en español:
- leer un dominio y un problema PDDL, y explicar los errores de escritura;
- resolver un problema con Fast Downward;
- validar un plan y explicar qué precondición falla;
- convertir el texto de un plan (por ejemplo, el que escribe un LLM) en un plan;
- trazar un plan estado por estado;
- construir variantes de un problema, compararlas y ofuscar sus nombres.

Los hechos se escriben siempre en sintaxis PDDL, por ejemplo «(bloqueado bomba3)».
"""
from __future__ import annotations

import re
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from unified_planning.engines import PlanGenerationResultStatus, ValidationResultStatus
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import OneshotPlanner, PlanValidator, get_environment

# Silencia los créditos que Unified Planning imprime cada vez que usa un motor
get_environment().credits_stream = None


class ErrorPDDL(Exception):
    """Error al leer un texto PDDL. El mensaje explica en español qué revisar."""


@dataclass
class ResultadoPlanificacion:
    """Lo que devuelve el planificador."""
    estado: str                 # "resuelto", "sin_solucion" o "sin_resultado"
    pasos: list                 # acciones en formato PDDL, p. ej. "(desplazarse ana base bodega)"
    segundos: float             # tiempo de cálculo, incluido el arranque del planificador
    plan: object = None         # plan de Unified Planning, o None
    mensaje: str = ""           # explicación en español


@dataclass
class ResultadoValidacion:
    """Veredicto del validador, con una explicación en español."""
    valido: bool
    motivo: str = ""            # "", "precondicion", "meta" o "sin_plan"
    paso: int | None = None     # número del paso que falla (desde 1)
    accion: str = ""            # acción que falla, en formato PDDL
    faltantes: list = field(default_factory=list)  # hechos que debían ser ciertos y no lo son
    explicacion: str = ""       # explicación en español
    mensaje_validador: str = ""  # mensaje original del validador de Unified Planning (en inglés)


@dataclass
class ResultadoLectura:
    """Resultado de convertir el texto de un plan en un plan de Unified Planning."""
    estado: str                 # "ok", "sin_plan", "ilegible" o "inexistente"
    pasos: list = field(default_factory=list)    # acciones encontradas, en formato PDDL
    errores: list = field(default_factory=list)  # problemas encontrados, en español
    plan: object = None
    avisos: list = field(default_factory=list)   # advertencias de formato que no impiden leer el plan


# Nombre en español de cada estado que devuelve el planificador
NOMBRE_ESTADO = {"resuelto": "resuelto", "sin_solucion": "sin solución", "sin_resultado": "sin resultado"}

# Frases en español para explicar los hechos del dominio de MantenIA.
# Cada objeto se nombra con su tipo («el técnico luis»), para que la frase concuerde en género.
FRASES_MANTENIA = {
    "en": "{0} debe estar en {1}",
    "ubicado": "{0} debe estar ubicado en {1}",
    "almacenado": "{0} debe estar almacenado en {1}",
    "lleva": "{0} debe llevar {1}",
    "compatible": "{0} debe ser compatible con {1}",
    "certificado": "{0} debe estar certificado para {1}",
    "encendido": "{0} debe estar encendido",
    "bloqueado": "{0} debe estar bloqueado",
    "averiado": "{0} debe estar averiado",
    "reparado": "{0} debe estar reparado",
    "en-servicio": "{0} debe estar en servicio",
    "probado": "{0} debe haber pasado la prueba de presión",
}
SUSTANTIVOS_MANTENIA = {"tecnico": "el técnico", "equipo": "el equipo", "repuesto": "el repuesto", "lugar": ""}


# ----------------------------------------------------------------------------- lectura

def _leer_texto(fuente) -> str:
    """Acepta una ruta a un archivo .pddl o directamente el texto PDDL."""
    if isinstance(fuente, Path):
        return fuente.read_text(encoding="utf-8")
    if isinstance(fuente, str) and "(" not in fuente and Path(fuente).exists():
        return Path(fuente).read_text(encoding="utf-8")
    return str(fuente)


def sugerir_ascii(palabra: str) -> str:
    """Quita tildes y cambia la ñ por n: «técnico» → «tecnico»."""
    descompuesta = unicodedata.normalize("NFKD", palabra)
    return "".join(c for c in descompuesta if not unicodedata.combining(c))


def revisar_nombres(texto: str) -> list:
    """Devuelve las palabras con tildes, ñ u otros caracteres no ASCII, sin contar los comentarios."""
    sin_comentarios = re.sub(r";[^\n]*", "", texto)
    return sorted({p for p in re.findall(r"[^\s()]+", sin_comentarios) if not p.isascii()})


def _tipos(texto_dominio: str) -> list:
    """Los tipos que declara un dominio en (:types ...), sin contar «object»."""
    m = re.search(r"\(:types([^)]*)\)", re.sub(r";[^\n]*", "", texto_dominio), flags=re.I)
    return [x for x in (m.group(1).split() if m else []) if x not in ("-", "object")]


def _revisar_objetos(texto_problema: str, tipos: list) -> str | None:
    """Revisa la sección :objects de un problema: grupos de nombres que terminan en «- tipo». Devuelve el error o None."""
    m = re.search(r"\(:objects([^)]*)\)", re.sub(r";[^\n]*", "", texto_problema), flags=re.I)
    if not m or not tipos:
        return None
    tokens, pendientes, i = m.group(1).split(), [], 0
    while i < len(tokens):
        if tokens[i] == "-":
            tipo = tokens[i + 1] if i + 1 < len(tokens) else ""
            if tipo not in tipos:
                return (f"En :objects, después de «-» va un tipo ({', '.join(tipos)}), y aquí aparece «{tipo or 'nada'}». "
                        "Si un nombre lleva guion, escríbalo sin espacios (planta-sur). El tipo se escribe una sola vez, "
                        "al final de cada grupo de nombres: «bomba3 compresor2 - equipo».")
            if not pendientes:
                return (f"En :objects, el tipo «{tipo}» no tiene nombres antes. Escriba primero los nombres y al final su "
                        "tipo: «bomba3 compresor2 - equipo».")
            pendientes, i = [], i + 2
            continue
        pendientes.append(tokens[i])
        i += 1
    if pendientes:
        return (f"En :objects, {', '.join(pendientes)} no {'tiene' if len(pendientes) == 1 else 'tienen'} tipo. Termine "
                "cada grupo de nombres con «- tipo»; por ejemplo, «bomba3 compresor2 - equipo».")
    return None


def _traducir_error(error: Exception, texto: str, cual: str, tipos: list = ()) -> str:
    """Convierte un error del lector de PDDL en una explicación en español."""
    msg = str(error)
    m = re.search(r"line:?\s*(\d+)", msg)
    linea = int(m.group(1)) if m else None
    lineas = texto.splitlines()
    fragmento = lineas[linea - 1].strip() if linea and 0 < linea <= len(lineas) else ""
    donde = f" Revise la línea {linea} del {cual}: «{fragmento}»." if linea else ""
    if "found end of text" in msg:
        base = "Falta cerrar al menos un paréntesis: el texto termina antes de cerrar todo lo que se abrió."
        donde = f" Cuente los paréntesis del {cual}."
    elif "already defined" in msg:
        nombre = re.search(r"Name ([\w-]+) already defined", msg)
        base = (f"El nombre «{nombre.group(1) if nombre else '?'}» está declarado dos veces. Cada objeto se declara una "
                "sola vez en :objects; si copió líneas de otro problema, borre la repetida.")
        msg = msg.split("!")[0] + "!"
    elif "Expected ')', found '-'" in msg:
        base = ("Hay un guion «-» donde no corresponde. En PDDL, el tipo se declara una sola vez después de los nombres: "
                "«?e - equipo» en un parámetro, o «bomba3 compresor2 - equipo» en :objects.")
    elif "Expected ')'" in msg:
        base = "Hay un paréntesis de más, o faltó agrupar varios hechos con (and ...)."
    elif re.search(r"Expected '(:[a-z-]+)'", msg):
        clave = re.search(r"Expected '(:[a-z-]+)'", msg).group(1)
        base = (f"Se esperaba la sección {clave}. Revise que esa palabra clave esté bien escrita "
                "y que la sección anterior esté bien cerrada.")
    elif "Not able to handle" in msg:
        base = "Un hecho usa un predicado que no existe en el dominio."
    elif "Found invalid expression" in msg:
        nombre = re.search(r"Found invalid expression: ([^.\s]+)", msg)
        if cual == "dominio" and nombre and nombre.group(1) in tipos:
            base = (f"En las precondiciones y los efectos no se escribe el tipo: escriba, por ejemplo, «(probado ?e)», sin "
                    f"«- {nombre.group(1)}». El tipo de cada variable se declara solo en :parameters y en :predicates.")
        elif cual == "dominio":
            base = (f"El nombre «{nombre.group(1) if nombre else '?'}» no está declarado en el dominio. Si es un "
                    "parámetro, escríbalo con «?» y declárelo en :parameters de la acción; si es un predicado, "
                    "declárelo en :predicates. Revise también cómo está escrito.")
        else:
            base = (f"El nombre «{nombre.group(1) if nombre else '?'}» no está declarado: "
                    "agréguelo en :objects o revise cómo está escrito.")
    elif "is not well-formed" in msg:
        base = "Un hecho no respeta los tipos: algún argumento no es del tipo que pide el predicado."
    elif "has arity" in msg:
        m2 = re.search(r"fluent: ([\w-]+) has arity (\d+) but (\d+)", msg)
        base = (f"El predicado «{m2.group(1)}» necesita {m2.group(2)} argumentos y recibió {m2.group(3)}."
                if m2 else "Un predicado recibió un número equivocado de argumentos.")
    else:
        base = f"El {cual} no se pudo leer."
    primera = msg.strip().splitlines()[0][:220] if msg.strip() else type(error).__name__
    return f"{base}{donde}\n(Mensaje original del lector: {primera})"


def leer_problema(dominio, problema):
    """Lee un dominio y un problema PDDL (rutas o texto) y devuelve el problema de Unified Planning.

    Si algo está mal escrito, lanza ErrorPDDL con una explicación en español.
    """
    texto_d, texto_p = _leer_texto(dominio), _leer_texto(problema)
    for cual, texto in (("dominio", texto_d), ("problema", texto_p)):
        raras = revisar_nombres(texto)
        if raras:
            sugerencias = ", ".join(f"«{p}» → «{sugerir_ascii(p)}»" for p in raras)
            raise ErrorPDDL(f"El {cual} tiene nombres con tildes, ñ u otros caracteres especiales: {sugerencias}. "
                            "En PDDL use solo letras sin tilde, números y guiones.")
    tipos = _tipos(texto_d)
    try:
        PDDLReader().parse_problem_string(texto_d)
    except Exception as e:
        raise ErrorPDDL(_traducir_error(e, texto_d, "dominio", tipos)) from None
    error_objetos = _revisar_objetos(texto_p, tipos)
    if error_objetos:
        raise ErrorPDDL(error_objetos)
    try:
        return PDDLReader().parse_problem_string(texto_d, texto_p)
    except Exception as e:
        raise ErrorPDDL(_traducir_error(e, texto_p, "problema", tipos)) from None


# ----------------------------------------------------------------------------- hechos y estados

def _hecho(expr) -> str:
    """Escribe un hecho de Unified Planning en sintaxis PDDL: bloqueado(bomba3) → (bloqueado bomba3)."""
    if expr.is_not():
        return f"(not {_hecho(expr.arg(0))})"
    if expr.is_fluent_exp():
        argumentos = " ".join(str(a) for a in expr.args)
        return f"({expr.fluent().name}{' ' + argumentos if argumentos else ''})"
    return str(expr)


def _atomos(expr):
    """Separa una conjunción (and ...) en sus hechos."""
    if expr.is_and():
        for a in expr.args:
            yield from _atomos(a)
    else:
        yield expr


def estado_inicial(problema) -> set:
    """Conjunto de hechos ciertos al empezar (mundo cerrado: lo que no aparece es falso)."""
    return {_hecho(f) for f, v in problema.initial_values.items()
            if v.is_bool_constant() and v.bool_constant_value()}


def metas(problema) -> list:
    """Hechos que deben ser ciertos al final."""
    return [_hecho(a) for g in problema.goals for a in _atomos(g)]


def _cumple(atomo, estado: set) -> bool:
    if atomo.is_not():
        return _hecho(atomo.arg(0)) not in estado
    if atomo.is_bool_constant():
        return atomo.bool_constant_value()
    return _hecho(atomo) in estado


def _sustitucion(accion, argumentos):
    em = get_environment().expression_manager
    return {em.ParameterExp(p): a for p, a in zip(accion.parameters, argumentos)}


def precondiciones_insatisfechas(accion, argumentos, estado: set) -> list:
    """Hechos de la precondición que no se cumplen en el estado (incluidos los hechos fijos del problema)."""
    s = _sustitucion(accion, argumentos)
    return [_hecho(a) for pre in accion.preconditions for a in _atomos(pre.substitute(s)) if not _cumple(a, estado)]


def aplicar(accion, argumentos, estado: set) -> set:
    """Estado que resulta de aplicar la acción: primero se eliminan hechos, luego se agregan."""
    s = _sustitucion(accion, argumentos)
    agrega, elimina = set(), set()
    for efecto in accion.effects:
        hecho = _hecho(efecto.fluent.substitute(s))
        (agrega if efecto.value.bool_constant_value() else elimina).add(hecho)
    return (set(estado) - elimina) | agrega


def precondiciones_de(accion) -> list:
    """Precondiciones de una acción del dominio, en PDDL y con los nombres de sus parámetros: (bloqueado e)."""
    return [_hecho(a) for pre in accion.preconditions for a in _atomos(pre)]


def objetos(problema, nombres) -> list:
    """Convierte nombres de objetos («ana», «bodega») en expresiones de Unified Planning."""
    em = get_environment().expression_manager
    return [em.ObjectExp(problema.object(n)) for n in nombres]


def accion_a_texto(accion_instanciada) -> str:
    """Escribe una acción del plan en formato PDDL: (desplazarse ana base bodega)."""
    argumentos = " ".join(str(p) for p in accion_instanciada.actual_parameters)
    return f"({accion_instanciada.action.name}{' ' + argumentos if argumentos else ''})"


def explicar_hecho(hecho: str, problema=None, frases=None, sustantivos=None) -> str:
    """Explica un hecho en español si hay una frase para su predicado; si no, lo deja en PDDL."""
    frases = FRASES_MANTENIA if frases is None else frases
    sustantivos = SUSTANTIVOS_MANTENIA if sustantivos is None else sustantivos
    partes = hecho.strip("()").split()
    if not partes or partes[0] == "not" or partes[0] not in frases:
        return f"debe cumplirse {hecho}"

    def nombrar(obj):
        if problema is not None and problema.has_object(obj):
            sustantivo = sustantivos.get(problema.object(obj).type.name, "")
            return f"{sustantivo} {obj}".strip()
        return obj

    try:
        return frases[partes[0]].format(*[nombrar(o) for o in partes[1:]])
    except (IndexError, KeyError):
        return f"debe cumplirse {hecho}"


# ----------------------------------------------------------------------------- planificar y validar

def resolver(problema, motor: str = "fast-downward", limite_segundos: int = 60) -> ResultadoPlanificacion:
    """Resuelve el problema con Fast Downward (configuración por defecto de Unified Planning)."""
    inicio = time.perf_counter()
    with OneshotPlanner(name=motor) as planificador:
        r = planificador.solve(problema, timeout=limite_segundos)
    segundos = time.perf_counter() - inicio
    resueltos = (PlanGenerationResultStatus.SOLVED_SATISFICING, PlanGenerationResultStatus.SOLVED_OPTIMALLY)
    sin_solucion = (PlanGenerationResultStatus.UNSOLVABLE_PROVEN, PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY)
    if r.status in resueltos:
        pasos = [accion_a_texto(a) for a in r.plan.actions]
        return ResultadoPlanificacion("resuelto", pasos, segundos, r.plan,
                                      f"El planificador encontró un plan de {len(pasos)} pasos en {segundos:.2f} s.")
    if r.status in sin_solucion:
        return ResultadoPlanificacion("sin_solucion", [], segundos, None,
                                      f"El planificador demostró en {segundos:.2f} s que no existe ningún plan "
                                      "que lleve del estado inicial a la meta.")
    return ResultadoPlanificacion("sin_resultado", [], segundos, None,
                                  f"El planificador no terminó ({r.status.name}) en {segundos:.2f} s.")


def _detalle(hechos, problema) -> str:
    """Lista los hechos y, si hay una frase en español para su predicado, la agrega."""
    partes = []
    for h in hechos:
        frase = explicar_hecho(h, problema)
        partes.append(h if frase.startswith("debe cumplirse") else f"{h}, es decir, {frase}")
    return "; ".join(partes)


def explicar_fallo(problema, plan) -> ResultadoValidacion:
    """Recorre el plan y explica el primer paso que no se puede aplicar, o la meta que no se cumple."""
    estado = estado_inicial(problema)
    for i, a in enumerate(plan.actions, 1):
        faltan = precondiciones_insatisfechas(a.action, a.actual_parameters, estado)
        if faltan:
            texto = accion_a_texto(a)
            detalle = _detalle(faltan, problema)
            return ResultadoValidacion(False, "precondicion", i, texto, faltan,
                                       f"El paso {i}, {texto}, no se puede aplicar porque no se cumple: {detalle}.")
        estado = aplicar(a.action, a.actual_parameters, estado)
    faltan = [h for h in metas(problema) if h not in estado]
    detalle = _detalle(faltan, problema)
    return ResultadoValidacion(False, "meta", len(plan.actions), "", faltan,
                               f"Todas las acciones se pueden aplicar, pero al final no se cumple la meta: falta {detalle}.")


def validar(problema, plan) -> ResultadoValidacion:
    """Valida el plan con el validador de Unified Planning y explica el resultado en español."""
    if plan is None:
        return ResultadoValidacion(False, "sin_plan", explicacion="No hay plan que validar.")
    with PlanValidator(problem_kind=problema.kind) as validador:
        r = validador.validate(problema, plan)
    original = " ".join(m.message for m in (r.log_messages or []))
    if r.status == ValidationResultStatus.VALID:
        return ResultadoValidacion(True, explicacion=("El plan es válido: cada acción cumple sus precondiciones "
                                                      "en el momento de aplicarse y, al final, se cumple la meta."),
                                   mensaje_validador=original or "VALID")
    resultado = explicar_fallo(problema, plan)
    resultado.mensaje_validador = original or "INVALID"
    return resultado


# ----------------------------------------------------------------------------- leer planes escritos como texto

_PATRON_PDDL = re.compile(r"\(\s*([a-z][a-z0-9_-]*)((?:\s+[a-z0-9_-]+)*)\s*\)")
_PATRON_FUNCION = re.compile(r"\b([a-z][a-z0-9_-]*)\(\s*([a-z0-9_-]+(?:\s*,\s*[a-z0-9_-]+)*)?\s*\)")
# Viñeta o numeración al inicio de una línea: «- », «2. », «2) », «paso 2: »
_MARCA_LISTA = re.compile(r"^(?:[-*•]\s*|\d+\s*[.):]\s*|paso\s+\d+\s*[.):-]?\s*)")


def _clasificar_lineas(t: str, nombres_acciones: set) -> list:
    """Clasifica cada línea: ("accion", nombre, argumentos), ("intento", línea, sugerencia), ("varias", línea),
    ("rotulo", línea), ("vacia",) o ("prosa", línea).

    Un «intento» es una línea que parece una acción mal escrita, por ejemplo con comas o sin paréntesis. Un «rótulo»
    es un título corto, como «Ana:» o «**Plan**», que agrupa acciones sin cortar el plan.
    """
    lineas = []
    for original in t.splitlines():
        linea = original.strip()
        if not linea or linea.startswith("```"):
            lineas.append(("vacia",))
            continue
        if re.fullmatch(r"\*\*[^*()]{1,40}\*\*:?|[^\s()]+(?:\s+[^\s()]+){0,3}:", linea):
            lineas.append(("rotulo", linea))
            continue
        linea = _MARCA_LISTA.sub("", linea.replace("`", "").replace("**", "")).strip().rstrip(".,").strip()
        m = _PATRON_PDDL.fullmatch(linea)
        if m:
            lineas.append(("accion", m.group(1), m.group(2).split()))
            continue
        m = _PATRON_FUNCION.fullmatch(linea)
        if m:
            lineas.append(("accion", m.group(1), [x.strip() for x in (m.group(2) or "").split(",") if x.strip()]))
            continue
        palabras = re.sub(r"[(),]", " ", linea).split()
        parece = palabras and (linea.startswith("(") or palabras[0] in nombres_acciones)
        if parece and linea.count("(") >= 2 and all(re.fullmatch(r"[a-z0-9_-]+", p) for p in palabras):
            lineas.append(("varias", original.strip()))
        elif parece and len(palabras) <= 10 and all(re.fullmatch(r"[a-z0-9_-]+", p) for p in palabras):
            lineas.append(("intento", original.strip(), f"({' '.join(palabras)})"))
        else:
            lineas.append(("prosa", original.strip()))
    return lineas


def plan_desde_texto(problema, texto: str, estricto: bool = False) -> ResultadoLectura:
    """Convierte un plan escrito como texto (por una persona o por un LLM) en un plan de Unified Planning.

    Acepta líneas como «(desplazarse ana base bodega)», «1. (desplazarse ana base bodega)» o
    «desplazarse(ana, base, bodega)», y comentarios con «;». Una línea que parece una acción mal escrita
    (con comas, sin paréntesis, o con dos acciones) se reporta como error, en lugar de ignorarse. Si el
    texto dice «SIN PLAN» y no trae un plan después, lo reporta así.

    Con estricto=False (respuestas de un LLM), si la respuesta trae explicaciones además del plan, se lee
    el último bloque de líneas que son solo acciones y se advierte en `avisos`; los rótulos cortos («Ana:»)
    no cortan el bloque. Con estricto=True (planes escritos por una persona), toda línea que no sea una
    acción ni un comentario es un error.
    """
    t = re.sub(r"<think>.*?</think>", " ", str(texto), flags=re.S | re.I).lower()
    t = re.sub(r"(;|#|//)[^\n]*", " ", t)  # comentarios
    acciones = {a.name: a for a in problema.actions}
    lineas = _clasificar_lineas(t, set(acciones))
    DE_PLAN = ("accion", "intento", "varias")

    # Bloques: líneas del plan seguidas; las líneas en blanco y los rótulos no cortan un bloque, la prosa sí
    bloques, actual, fin_ultimo = [], [], -1
    for i, linea in enumerate(lineas):
        if linea[0] in DE_PLAN:
            actual.append(linea)
            fin_ultimo = i
        elif linea[0] == "prosa" and actual:
            bloques.append(actual)
            actual = []
    if actual:
        bloques.append(actual)
    hay_texto = any(l[0] in ("prosa", "rotulo") for l in lineas)
    texto_final = " ".join(l[1] for l in lineas[fin_ultimo + 1:] if l[0] in ("prosa", "rotulo"))

    avisos, errores = [], []
    if not bloques or re.search(r"\bsin\s+plan\b", texto_final):
        if re.search(r"\bsin\s+plan\b", t):
            return ResultadoLectura("sin_plan")
        if estricto:
            return ResultadoLectura("ilegible", errores=["No se encontró ninguna acción con el formato (accion arg1 arg2 ...), "
                                                        "una por línea."])
        # Último recurso: acciones escritas dentro de un párrafo
        elegidas = [("accion", m.group(1), m.group(2).split()) for m in _PATRON_PDDL.finditer(t)] or \
                   [("accion", m.group(1), [x.strip() for x in (m.group(2) or "").split(",") if x.strip()])
                    for m in _PATRON_FUNCION.finditer(t)]
        if not elegidas:
            return ResultadoLectura("ilegible", errores=["No se encontró ninguna acción con el formato (accion arg1 arg2 ...)."])
        avisos.append("Las acciones venían dentro del texto, no una por línea: se leyeron todas las que aparecen, en orden.")
    elif estricto:
        elegidas = [l for l in lineas if l[0] in DE_PLAN]
        errores = [f"La línea «{l[1]}» no es una acción. Si es una nota, escríbala como comentario, después de «;»."
                   for l in lineas if l[0] == "prosa"]
    else:
        elegidas = bloques[-1]
        if len(bloques) > 1 or hay_texto:
            ignoradas = sum(len(b) for b in bloques[:-1])
            avisos.append(f"La respuesta trae texto además del plan: se leyó solo el último bloque de acciones "
                          f"({len(elegidas)} líneas)" + (f"; se ignoraron {ignoradas} líneas de acciones anteriores, "
                                                        "separadas del plan por texto." if ignoradas else "."))

    pasos, mal_escritas = [], bool(errores)
    for i, linea in enumerate(elegidas, 1):
        if linea[0] == "intento":
            mal_escritas = True
            errores.append(f"Paso {i}: «{linea[1]}» no tiene el formato de una acción. Escríbala entre paréntesis, con los "
                           f"argumentos separados por espacios y sin comas: {linea[2]}.")
            continue
        if linea[0] == "varias":
            mal_escritas = True
            errores.append(f"Paso {i}: «{linea[1]}» tiene más de una acción. Escriba una acción por línea.")
            continue
        _, nombre, argumentos = linea
        pasos.append(f"({nombre}{' ' + ' '.join(argumentos) if argumentos else ''})")
        if nombre not in acciones:
            errores.append(f"Paso {i}: la acción «{nombre}» no existe en el dominio.")
            continue
        accion = acciones[nombre]
        if len(argumentos) != len(accion.parameters):
            errores.append(f"Paso {i}: «{nombre}» necesita {len(accion.parameters)} argumentos y recibió {len(argumentos)}.")
            continue
        for parametro, obj in zip(accion.parameters, argumentos):
            if not problema.has_object(obj):
                errores.append(f"Paso {i}: el objeto «{obj}» no existe en el problema.")
            elif not problema.object(obj).type.is_compatible(parametro.type):
                errores.append(f"Paso {i}: «{obj}» es de tipo {problema.object(obj).type.name}, "
                               f"pero «{nombre}» espera un {parametro.type.name} en esa posición.")
    if errores:
        return ResultadoLectura("ilegible" if mal_escritas else "inexistente", pasos, errores, avisos=avisos)
    plan = PDDLReader().parse_plan_string(problema, "\n".join(pasos))
    return ResultadoLectura("ok", pasos, [], plan, avisos=avisos)


# ----------------------------------------------------------------------------- traza

def trazar(problema, plan) -> dict:
    """Ejecuta el plan sobre el modelo y devuelve, para cada paso, los hechos agregados y eliminados.

    Si un paso no se puede aplicar, la traza se detiene en él y lo explica.
    """
    estado = estado_inicial(problema)
    inicial = sorted(estado)
    pasos = []
    for i, a in enumerate(plan.actions, 1):
        texto = accion_a_texto(a)
        faltan = precondiciones_insatisfechas(a.action, a.actual_parameters, estado)
        if faltan:
            pasos.append({"paso": i, "accion": texto, "aplicable": False, "faltantes": faltan,
                          "agrega": [], "elimina": [], "estado": sorted(estado)})
            break
        nuevo = aplicar(a.action, a.actual_parameters, estado)
        pasos.append({"paso": i, "accion": texto, "aplicable": True, "faltantes": [],
                      "agrega": sorted(nuevo - estado), "elimina": sorted(estado - nuevo), "estado": sorted(nuevo)})
        estado = nuevo
    return {"inicial": inicial, "pasos": pasos, "metas": metas(problema),
            "meta_cumplida": all(h in estado for h in metas(problema))}


# ----------------------------------------------------------------------------- variantes y comparaciones

def _bloque(texto: str, clave: str):
    """Ubica la sección «(:clave ...)» de un texto PDDL y devuelve (inicio, fin)."""
    m = re.search(r"\(\s*" + re.escape(clave) + r"\b", texto)
    if not m:
        raise ErrorPDDL(f"No se encontró la sección {clave}.")
    profundidad = 0
    for j in range(m.start(), len(texto)):
        if texto[j] == "(":
            profundidad += 1
        elif texto[j] == ")":
            profundidad -= 1
            if profundidad == 0:
                return m.start(), j + 1
    raise ErrorPDDL(f"La sección {clave} no está bien cerrada.")


def _patron_hecho(hecho: str):
    partes = hecho.strip().strip("()").split()
    return re.compile(r"\(\s*" + r"\s+".join(re.escape(p) for p in partes) + r"\s*\)")


def variante(texto_problema: str, agregar=(), quitar=(), meta=None, objetos=None, nombre=None) -> str:
    """Construye una variante de un problema PDDL.

    agregar / quitar: hechos del estado inicial, p. ej. "(certificado luis bomba3)".
    meta: lista de hechos que reemplaza la meta.
    objetos: diccionario tipo → lista de objetos nuevos, p. ej. {"lugar": ["planta-sur"]}.
    nombre: nombre nuevo del problema.
    """
    t = _leer_texto(texto_problema)
    if objetos:
        i, f = _bloque(t, ":objects")
        seccion = t[i:f]
        for tipo, nuevos in objetos.items():
            seccion, n = re.subn(r"(\s-\s*" + re.escape(tipo) + r")\b", " " + " ".join(nuevos) + r"\1", seccion, count=1)
            if n == 0:
                seccion = seccion[:-1] + f" {' '.join(nuevos)} - {tipo})"
        t = t[:i] + seccion + t[f:]
    i, f = _bloque(t, ":init")
    seccion = t[i:f]
    for h in quitar:
        seccion, n = _patron_hecho(h).subn("", seccion, count=1)
        if n == 0:
            raise ErrorPDDL(f"El hecho {h} no está en el estado inicial.")
    if agregar:
        seccion = seccion[:-1].rstrip() + "\n         " + " ".join(agregar) + ")"
    t = t[:i] + seccion + t[f:]
    if meta is not None:
        i, f = _bloque(t, ":goal")
        cuerpo = meta[0] if len(meta) == 1 else "(and " + " ".join(meta) + ")"
        t = t[:i] + f"(:goal {cuerpo})" + t[f:]
    if nombre:
        t = re.sub(r"\(\s*problem\s+[^\s)]+", f"(problem {nombre}", t, count=1)
    return t


def comparar_problemas(referencia, otro) -> dict:
    """Compara dos problemas: objetos, estado inicial y meta que faltan o sobran en «otro»."""
    obj_ref = {o.name for o in referencia.all_objects}
    obj_otro = {o.name for o in otro.all_objects}
    ini_ref, ini_otro = estado_inicial(referencia), estado_inicial(otro)
    met_ref, met_otro = set(metas(referencia)), set(metas(otro))
    return {"objetos_faltan": sorted(obj_ref - obj_otro), "objetos_sobran": sorted(obj_otro - obj_ref),
            "init_faltan": sorted(ini_ref - ini_otro), "init_sobran": sorted(ini_otro - ini_ref),
            "meta_faltan": sorted(met_ref - met_otro), "meta_sobran": sorted(met_otro - met_ref)}


def ofuscar(texto: str, mapa: dict) -> str:
    """Reemplaza nombres PDDL completos según el mapa, sin tocar partes de otras palabras."""
    claves = sorted(mapa, key=len, reverse=True)
    patron = re.compile(r"(?<![\w-])(" + "|".join(re.escape(k) for k in claves) + r")(?![\w-])")
    return patron.sub(lambda m: mapa[m.group(1)], texto)


def tiempo_planificador(problema, repeticiones: int = 3) -> float:
    """Tiempo medio (s) que tarda Fast Downward en resolver el problema."""
    tiempos = [resolver(problema).segundos for _ in range(repeticiones)]
    return sum(tiempos) / len(tiempos)
