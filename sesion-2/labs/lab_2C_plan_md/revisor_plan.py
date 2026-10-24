"""Revisor estructural del plan.md (Laboratorio 2C).

Comprueba los aspectos mecánicos de la lista de chequeo J.6: que existan las secciones,
que cada paso tenga resultado y verificación, que haya una sección de fuera de alcance,
un paso de aprobación antes de lo irreversible, una tabla de riesgos y un registro con hora.
No juzga si el contenido es correcto: eso lo hace la pareja. Cada punto dice qué queda
para el juicio humano.
"""
from __future__ import annotations

import re

from presentacion import mostrar_tabla

DOCUMENTOS = ["ot-523", "inventario", "certificaci", "procedimiento", "norma", "ventana", "mnt-07"]
IRREVERSIBLES = r"^(retirar (el |los |su )?(bloqueo|candado)|desbloquear|arrancar|poner en marcha|cerrar|liberar)"

PUNTOS = [
    (1, "El objetivo se puede comprobar con una verificación concreta.",
     "¿Lo podría comprobar alguien que no escribió el plan? ¿Tiene plazo y criterio medible?"),
    (2, "El contexto nombra las fuentes, sistemas y datos involucrados, y declara los supuestos.",
     "¿Los datos citados son los de los documentos? ¿Falta algún supuesto riesgoso?"),
    (3, "Hay una sección explícita de lo que queda fuera del alcance.",
     "¿Las exclusiones son las que importan?"),
    (4, "Las restricciones no negociables están escritas.",
     "¿Están todas las de la norma, las certificaciones, el procedimiento y la ventana?"),
    (5, "Cada paso tiene una acción, un resultado esperado y una verificación.",
     "¿Cada verificación se puede ejecutar de verdad, o solo dice «revisar»?"),
    (6, "Las dependencias entre pasos son explícitas.",
     "¿Las dependencias son las correctas? ¿El orden respeta la norma (bloquear antes de intervenir)?"),
    (7, "Los pasos irreversibles o costosos piden aprobación humana.",
     "¿Aprueba la persona correcta, según la norma? ¿Falta otra aprobación?"),
    (8, "Los criterios de aceptación incluyen una verificación de extremo a extremo.",
     "¿Demuestran que se cumplió el objetivo completo?"),
    (9, "Los riesgos principales tienen una señal de alerta y una respuesta.",
     "¿Son los riesgos principales? ¿Las respuestas respetan las restricciones?"),
    (10, "El registro de avance está al día y cada replanificación dice qué cambió y por qué.",
     "¿Las entradas explican las decisiones, no solo los hechos?"),
]


def _accion(texto: str) -> str:
    """La acción de un paso: el texto antes de «→», «(requiere» o «Resultado»."""
    return re.split(r"→|\(requiere|\(req\.|resultado\s*:", texto, maxsplit=1, flags=re.I)[0]


def _seccion(secciones: dict, *claves) -> str:
    for titulo, contenido in secciones.items():
        if any(c in titulo.lower() for c in claves):
            return contenido
    return ""


def revisar(plan) -> list:
    """Devuelve, para cada punto de J.6, la revisión automática (✓, ✗ o —) y su detalle."""
    secciones = plan.secciones()
    pasos = plan.pasos()
    resultados = {}

    objetivo = _seccion(secciones, "objetivo")
    # Un plazo (17:00) o un umbral con su unidad (4,5 mm/s); el «2» de «compresor 2» no cuenta
    medible = bool(re.search(r"\d{1,2}:\d{2}|\d+(?:[,.]\d+)?\s*(?:mm/s|mm\b|min\b|minutos|horas?\b|h\b|%|°c)", objetivo.lower()))
    resultados[1] = ("✓" if objetivo and medible else "✗",
                     "tiene un plazo o un criterio con cifras" if objetivo and medible
                     else "falta un objetivo con plazo o criterio medible (con cifras)")

    contexto = _seccion(secciones, "contexto").lower()
    citados = [d for d in DOCUMENTOS if d in contexto]
    supuestos = "supuesto" in contexto
    resultados[2] = ("✓" if len(citados) >= 2 and supuestos else "✗",
                     f"cita {len(citados)} fuentes" + ("; declara supuestos" if supuestos else "; no declara supuestos"))

    alcance = _seccion(secciones, "alcance").lower()
    fuera = re.search(r"fuera del? alcance\s*:?\s*(.+)", alcance)
    resultados[3] = ("✓" if fuera and len(fuera.group(1).strip()) > 3 else "✗",
                     "declara exclusiones" if fuera else "no hay «Fuera de alcance»")

    restricciones = _seccion(secciones, "restricciones")
    resultados[4] = ("✓" if len(restricciones.strip()) > 10 else "✗",
                     f"{len([l for l in restricciones.splitlines() if l.strip().startswith('-')])} restricciones escritas")

    sin_verif = [p["id"] for p in pasos if not re.search(r"verif", p["texto"], re.I)]
    sin_resultado = [p["id"] for p in pasos if not re.search(r"→|resultado", p["texto"], re.I)]
    ok5 = pasos and not sin_verif and not sin_resultado
    detalle5 = f"{len(pasos)} pasos" + (f"; sin verificación: {', '.join(sin_verif)}" if sin_verif else "") + \
               (f"; sin resultado: {', '.join(sin_resultado)}" if sin_resultado else "")
    resultados[5] = ("✓" if ok5 else "✗", detalle5)

    con_dependencia = [p["id"] for p in pasos[1:] if re.search(r"requiere|req\.", p["texto"], re.I)]
    ok6 = len(pasos) > 1 and len(con_dependencia) >= (len(pasos) - 1) / 2
    resultados[6] = ("✓" if ok6 else "✗", f"{len(con_dependencia)} de {max(len(pasos) - 1, 0)} pasos declaran de qué dependen")

    # Solo el verbo con que empieza la acción: «Esperar ... sin retirar el bloqueo» no retira el bloqueo
    acciones = [_accion(p["texto"]).strip().lower().replace("~~", "") for p in pasos]
    indices_aprobacion = [i for i, a in enumerate(acciones) if a.startswith(("aprobaci", "autoriz"))]
    indices_irreversibles = [i for i, a in enumerate(acciones) if re.match(IRREVERSIBLES, a)]
    ok7 = bool(indices_aprobacion) and (not indices_irreversibles or min(indices_aprobacion) < min(indices_irreversibles))
    resultados[7] = ("✓" if ok7 else "✗", "hay un paso de aprobación antes de lo irreversible" if ok7
                     else "no hay un paso de APROBACIÓN antes de retirar el bloqueo, arrancar o cerrar")

    aceptacion = _seccion(secciones, "aceptaci")
    resultados[8] = ("✓" if len(aceptacion.strip()) > 10 else "✗",
                     "hay criterios de aceptación" if aceptacion.strip() else "faltan criterios de aceptación")

    riesgos = _seccion(secciones, "riesgo")
    filas = [l for l in riesgos.splitlines() if l.strip().startswith("|") and not re.match(r"^\|\s*:?-", l.strip())]
    filas_completas = [f for f in filas[1:] if len([c for c in f.strip().strip("|").split("|") if c.strip()]) >= 3]
    resultados[9] = ("✓" if len(filas_completas) >= 2 else "✗", f"{len(filas_completas)} riesgos con señal y respuesta")

    registro = _seccion(secciones, "registro")
    entradas = [l for l in registro.splitlines() if re.search(r"\d{1,2}:\d{2}", l)]
    fallas = [i for i, l in enumerate(entradas) if re.search(r"· Paso \w+ falló:", l)]   # las que registra la ejecución
    # Después de la última falla debe haber una entrada que explique el cambio: no un paso cumplido ni una aprobación
    explicadas = [l for l in entradas[fallas[-1] + 1:] if not re.search(r"· (Paso \w+ (cumplido|falló)|Plan aprobado)", l)
                  and not re.search(r"·\s*(Replanificación:\s*)?\.\.\.\s*$", l) and len(l) > 80] if fallas else []
    if not entradas:
        resultados[10] = ("—", "todavía no hay entradas (el plan no se ha ejecutado)")
    elif fallas and not explicadas:
        resultados[10] = ("✗", f"{len(entradas)} entradas; después de la última falla no hay una entrada que explique "
                               "la replanificación")
    else:
        resultados[10] = ("✓", f"{len(entradas)} entradas con hora" + ("; la replanificación está explicada" if fallas else ""))

    return [{"punto": n, "criterio": criterio, "automático": resultados[n][0], "detalle": resultados[n][1],
             "queda para la pareja": juicio} for n, criterio, juicio in PUNTOS]


def mostrar_revision(revision, titulo: str = "Revisión estructural del plan.md (lista J.6)") -> None:
    mostrar_tabla(revision, columnas=["punto", "automático", "criterio", "detalle", "queda para la pareja"], titulo=titulo)


def comparar(revision_pareja: dict, revision_automatica: list) -> None:
    """Pone lado a lado la revisión de la pareja y la automática, y señala dónde no coinciden."""
    from presentacion import nota
    pendientes = [n for n, (veredicto, evidencia) in revision_pareja.items()
                  if veredicto.strip() in ("", "...") or evidencia.strip() in ("", "...")]
    if pendientes:
        nota(f"Faltan por revisar los puntos {', '.join(str(n) for n in pendientes)}: reemplace cada «...».", "aviso")
        return
    filas, distintas = [], []
    for r in revision_automatica:
        veredicto, evidencia = revision_pareja.get(r["punto"], ("", ""))
        v = veredicto.strip().lower()
        cumple = v.startswith("cumple")
        if r["automático"] in ("✓", "✗") and not v.startswith("no aplica") and (r["automático"] == "✓") != cumple:
            distintas.append(r["punto"])
        filas.append({"punto": r["punto"], "automático": r["automático"], "pareja": veredicto, "evidencia de la pareja": evidencia})
    mostrar_tabla(filas, titulo="Revisión de la pareja frente a la revisión automática")
    if distintas:
        nota(f"En los puntos {', '.join(str(n) for n in distintas)} la pareja y el revisor automático no coinciden. "
             "No significa que la pareja se equivoque: el revisor solo mira la forma. Anote en su análisis quién "
             "tiene la razón y por qué.", "info")
    else:
        nota("La pareja y el revisor automático coinciden en los puntos que el revisor puede comprobar. "
             "Recuerde que el revisor no juzga si el contenido es correcto.", "info")


def comparar_hallazgos(hallazgos: list, revision_automatica: list) -> None:
    """Muestra los hallazgos de la pareja junto a lo que vio el revisor automático en el mismo punto de J.6."""
    from presentacion import nota
    completos = [h for h in hallazgos if len(h) == 3 and all(str(x).strip() not in ("", "...") for x in h)]
    if len(completos) < 3:
        nota(f"Hay {len(completos)} hallazgo(s) completo(s). Escriban al menos tres: el punto de J.6, qué está mal y dónde, "
             "y qué documento lo muestra. Reemplace cada «...».", "aviso")
        return
    automatico = {r["punto"]: r for r in revision_automatica}
    filas, invisibles = [], 0
    for punto, problema, fuente in completos:
        r = automatico.get(int(punto)) if str(punto).isdigit() else None
        if r is None:
            nota(f"«{punto}» no es un punto de J.6: use un número del 1 al 10.", "aviso")
            return
        vio = r["automático"] == "✗"
        invisibles += not vio
        filas.append({"punto": punto, "criterio": r["criterio"], "hallazgo de la pareja": problema, "fuente": fuente,
                      "revisor automático": "también lo marcó ✗" if vio else f"marcó {r['automático']}: no lo vio"})
    mostrar_tabla(filas, titulo="Hallazgos de la pareja frente a la revisión automática")
    nota(f"{invisibles} de sus {len(completos)} hallazgos están en puntos que el revisor automático dio por buenos: son "
         "errores de contenido, que solo una persona que lee el plan contra los documentos puede ver.", "info")
