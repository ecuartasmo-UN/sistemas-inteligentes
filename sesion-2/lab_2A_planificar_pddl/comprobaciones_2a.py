"""Comprobaciones automáticas de los ejercicios del Laboratorio 2A.

Orientan a la pareja: dicen qué revisar, sin calificar y sin mostrar la solución.
"""
from __future__ import annotations

import base64
import re
from collections import Counter

import utilidades_pddl as u
from presentacion import mostrar_plan, mostrar_veredicto, nota

# Orden OT-518 de referencia, codificada para no mostrar la solución al abrir este archivo.
_OT518 = (
    "KGRlZmluZSAocHJvYmxlbSBvdC01MTgpCiAgKDpkb21haW4gbWFudGVuaWEpCiAgKDpvYmplY3RzIGFuYSBsdWlzIC0gdGVjbmljbwogICAg"
    "ICAgICAgICBib21iYTMgY29tcHJlc29yMiAtIGVxdWlwbwogICAgICAgICAgICBzZWxsbyByb2RhbWllbnRvIC0gcmVwdWVzdG8KICAgICAg"
    "ICAgICAgYmFzZSBib2RlZ2EgcGxhbnRhLW5vcnRlIHBsYW50YS1zdXIgLSBsdWdhcikKICAoOmluaXQgKGVuIGFuYSBiYXNlKSAoZW4gbHVp"
    "cyBiYXNlKQogICAgICAgICAodWJpY2FkbyBib21iYTMgcGxhbnRhLW5vcnRlKSAodWJpY2FkbyBjb21wcmVzb3IyIHBsYW50YS1zdXIpCiAg"
    "ICAgICAgIChlbmNlbmRpZG8gYm9tYmEzKSAoZW5jZW5kaWRvIGNvbXByZXNvcjIpCiAgICAgICAgIChhdmVyaWFkbyBib21iYTMpIChhdmVy"
    "aWFkbyBjb21wcmVzb3IyKQogICAgICAgICAoYWxtYWNlbmFkbyBzZWxsbyBib2RlZ2EpIChhbG1hY2VuYWRvIHJvZGFtaWVudG8gYm9kZWdh"
    "KQogICAgICAgICAoY29tcGF0aWJsZSBzZWxsbyBib21iYTMpIChjb21wYXRpYmxlIHJvZGFtaWVudG8gY29tcHJlc29yMikKICAgICAgICAg"
    "KGNlcnRpZmljYWRvIGFuYSBib21iYTMpIChjZXJ0aWZpY2FkbyBsdWlzIGNvbXByZXNvcjIpKQogICg6Z29hbCAoYW5kIChlbi1zZXJ2aWNp"
    "byBib21iYTMpIChlbi1zZXJ2aWNpbyBjb21wcmVzb3IyKSkpKQo="
)

# Dominio de referencia con la regla de la prueba de presión, codificado para no mostrar la solución al abrir este archivo.
_DOMINIO_PRUEBA = (
    "KGRlZmluZSAoZG9tYWluIG1hbnRlbmlhKQogICg6cmVxdWlyZW1lbnRzIDpzdHJpcHMgOnR5cGluZykKICAoOnR5cGVzIHRlY25pY28gZXF1"
    "aXBvIHJlcHVlc3RvIGx1Z2FyKQogICg6cHJlZGljYXRlcwogICAgKGVuID90IC0gdGVjbmljbyA/bCAtIGx1Z2FyKSAodWJpY2FkbyA/ZSAt"
    "IGVxdWlwbyA/bCAtIGx1Z2FyKQogICAgKGFsbWFjZW5hZG8gP3IgLSByZXB1ZXN0byA/bCAtIGx1Z2FyKSAobGxldmEgP3QgLSB0ZWNuaWNv"
    "ID9yIC0gcmVwdWVzdG8pCiAgICAoY29tcGF0aWJsZSA/ciAtIHJlcHVlc3RvID9lIC0gZXF1aXBvKSAoY2VydGlmaWNhZG8gP3QgLSB0ZWNu"
    "aWNvID9lIC0gZXF1aXBvKQogICAgKGVuY2VuZGlkbyA/ZSAtIGVxdWlwbykgKGJsb3F1ZWFkbyA/ZSAtIGVxdWlwbykgKGF2ZXJpYWRvID9l"
    "IC0gZXF1aXBvKQogICAgKHJlcGFyYWRvID9lIC0gZXF1aXBvKSAoZW4tc2VydmljaW8gP2UgLSBlcXVpcG8pCiAgICAocHJvYmFkbyA/ZSAt"
    "IGVxdWlwbykpCgogICg6YWN0aW9uIGRlc3BsYXphcnNlCiAgICA6cGFyYW1ldGVycyAoP3QgLSB0ZWNuaWNvID9kZXNkZSAtIGx1Z2FyID9o"
    "YWNpYSAtIGx1Z2FyKQogICAgOnByZWNvbmRpdGlvbiAoZW4gP3QgP2Rlc2RlKQogICAgOmVmZmVjdCAoYW5kIChlbiA/dCA/aGFjaWEpIChu"
    "b3QgKGVuID90ID9kZXNkZSkpKSkKCiAgKDphY3Rpb24gcmV0aXJhci1yZXB1ZXN0bwogICAgOnBhcmFtZXRlcnMgKD90IC0gdGVjbmljbyA/"
    "ciAtIHJlcHVlc3RvID9sIC0gbHVnYXIpCiAgICA6cHJlY29uZGl0aW9uIChhbmQgKGVuID90ID9sKSAoYWxtYWNlbmFkbyA/ciA/bCkpCiAg"
    "ICA6ZWZmZWN0IChhbmQgKGxsZXZhID90ID9yKSAobm90IChhbG1hY2VuYWRvID9yID9sKSkpKQoKICAoOmFjdGlvbiBibG9xdWVhcgogICAg"
    "OnBhcmFtZXRlcnMgKD90IC0gdGVjbmljbyA/ZSAtIGVxdWlwbyA/bCAtIGx1Z2FyKQogICAgOnByZWNvbmRpdGlvbiAoYW5kIChlbiA/dCA/"
    "bCkgKHViaWNhZG8gP2UgP2wpIChlbmNlbmRpZG8gP2UpIChjZXJ0aWZpY2FkbyA/dCA/ZSkpCiAgICA6ZWZmZWN0IChhbmQgKGJsb3F1ZWFk"
    "byA/ZSkgKG5vdCAoZW5jZW5kaWRvID9lKSkpKQoKICAoOmFjdGlvbiByZXBhcmFyCiAgICA6cGFyYW1ldGVycyAoP3QgLSB0ZWNuaWNvID9l"
    "IC0gZXF1aXBvID9yIC0gcmVwdWVzdG8gP2wgLSBsdWdhcikKICAgIDpwcmVjb25kaXRpb24gKGFuZCAoZW4gP3QgP2wpICh1YmljYWRvID9l"
    "ID9sKSAoYmxvcXVlYWRvID9lKSAoYXZlcmlhZG8gP2UpCiAgICAgICAgICAgICAgICAgICAgICAgKGxsZXZhID90ID9yKSAoY29tcGF0aWJs"
    "ZSA/ciA/ZSkgKGNlcnRpZmljYWRvID90ID9lKSkKICAgIDplZmZlY3QgKGFuZCAocmVwYXJhZG8gP2UpIChub3QgKGF2ZXJpYWRvID9lKSkg"
    "KG5vdCAobGxldmEgP3QgP3IpKSkpCgogICg6YWN0aW9uIHByb2JhcgogICAgOnBhcmFtZXRlcnMgKD90IC0gdGVjbmljbyA/ZSAtIGVxdWlw"
    "byA/bCAtIGx1Z2FyKQogICAgOnByZWNvbmRpdGlvbiAoYW5kIChlbiA/dCA/bCkgKHViaWNhZG8gP2UgP2wpIChyZXBhcmFkbyA/ZSkgKGJs"
    "b3F1ZWFkbyA/ZSkpCiAgICA6ZWZmZWN0IChwcm9iYWRvID9lKSkKCiAgKDphY3Rpb24gbGliZXJhcgogICAgOnBhcmFtZXRlcnMgKD90IC0g"
    "dGVjbmljbyA/ZSAtIGVxdWlwbyA/bCAtIGx1Z2FyKQogICAgOnByZWNvbmRpdGlvbiAoYW5kIChlbiA/dCA/bCkgKHViaWNhZG8gP2UgP2wp"
    "IChibG9xdWVhZG8gP2UpIChyZXBhcmFkbyA/ZSkgKHByb2JhZG8gP2UpKQogICAgOmVmZmVjdCAoYW5kIChlbi1zZXJ2aWNpbyA/ZSkgKGVu"
    "Y2VuZGlkbyA/ZSkgKG5vdCAoYmxvcXVlYWRvID9lKSkpKQopCg=="
)

# Qué parte de la orden escrita revisar, según el predicado del hecho que falta o sobra
_PISTAS = {
    "en": "dónde empieza cada técnico",
    "ubicado": "dónde está cada equipo",
    "encendido": "si la orden dice que los equipos siguen energizados",
    "averiado": "qué equipos están averiados",
    "almacenado": "dónde están los repuestos",
    "compatible": "qué repuesto sirve a cada equipo",
    "certificado": "quién está certificado para cada equipo",
    "en-servicio": "qué debe ser cierto al final",
}


def _pendiente(texto: str) -> None:
    return "..." in re.sub(r";[^\n]*", "", texto)


def _predicado(hecho: str) -> str:
    return hecho.strip("()").split()[0]


def _pistas(diferencias: dict) -> str:
    lineas = []
    for clave, verbo in (("init_faltan", "Faltan"), ("init_sobran", "Sobran")):
        for pred, n in sorted(Counter(_predicado(h) for h in diferencias[clave]).items()):
            lineas.append(f"• En el estado inicial {verbo.lower()} {n} hecho(s) con «{pred}»: revise {_PISTAS.get(pred, 'la orden')}.")
    if diferencias["meta_faltan"] or diferencias["meta_sobran"]:
        lineas.append("• La meta no coincide con la orden: revise qué debe ser cierto al final.")
    if diferencias["objetos_faltan"]:
        lineas.append(f"• Faltan objetos que la orden menciona: {', '.join(diferencias['objetos_faltan'])}.")
    if diferencias["objetos_sobran"]:
        lineas.append(f"• Hay objetos que la orden no menciona: {', '.join(diferencias['objetos_sobran'])}.")
    return "\n".join(lineas)


def comprobar_plan_corregido(problema, texto_plan: str) -> None:
    """Ejercicio 1: el plan corregido debe ser válido para la OT-512."""
    if _pendiente(texto_plan):
        nota("Todavía hay partes marcadas con «...»: complételas y vuelva a ejecutar la celda.", "aviso")
        return
    lectura = u.plan_desde_texto(problema, texto_plan, estricto=True)
    if lectura.estado != "ok":
        nota("No se pudo leer el plan:\n" + "\n".join(lectura.errores or ["no tiene acciones"]), "error")
        return
    if lectura.avisos:
        nota("\n".join(lectura.avisos), "aviso", "Formato")
    validacion = u.validar(problema, lectura.plan)
    mostrar_veredicto(validacion)
    if validacion.valido:
        nota("¡Bien! El plan corregido cumple todas las precondiciones y logra la meta.", "exito", "Comprobación")
    else:
        nota("Lea el mensaje del validador: dice qué paso falla y qué hecho le falta. "
             "Piense qué acción produce ese hecho y dónde debe ir.", "aviso", "Pista")


def comprobar_ot518(dominio, texto_problema: str) -> None:
    """Ejercicio 2: el modelo de la OT-518 debe producir planes válidos para la orden real."""
    if _pendiente(texto_problema):
        nota("Todavía hay partes marcadas con «...»: complételas y vuelva a ejecutar la celda.", "aviso")
        return
    try:
        problema = u.leer_problema(dominio, texto_problema)
    except u.ErrorPDDL as e:
        nota(str(e), "error", "El problema no se pudo leer")
        return
    resultado = u.resolver(problema)
    referencia = u.leer_problema(dominio, base64.b64decode(_OT518).decode("utf-8"))
    diferencias = u.comparar_problemas(referencia, problema)
    if resultado.estado != "resuelto":
        nota("Su modelo se lee bien, pero no tiene solución: ningún plan lleva del estado inicial a la meta.\n"
             + (_pistas(diferencias) or "Revise certificaciones, compatibilidades y dónde están los repuestos."), "aviso", "Pista")
        return
    lectura = u.plan_desde_texto(referencia, "\n".join(resultado.pasos))
    if lectura.estado != "ok":
        nombres = ", ".join(f"«{n}»" for n in diferencias["objetos_sobran"]) or "algunos objetos"
        nota(f"Su modelo usa nombres que no son los códigos de la orden: {nombres}. Use exactamente los nombres que "
             "pide la orden (bomba3, compresor2, sello, rodamiento, base, bodega, planta-norte y planta-sur).",
             "error", "Revise los nombres")
        return
    validacion = u.validar(referencia, lectura.plan)
    exacto = not any(diferencias.values())
    if validacion.valido and exacto:
        nota("¡Muy bien! Su modelo describe la orden OT-518 y el plan que produce es válido en la orden real.",
             "exito", "Comprobación")
        mostrar_plan(resultado.pasos, "Plan de su modelo")
        return
    if validacion.valido:
        nota("El plan que produce su modelo también funciona en la orden real, pero su modelo no describe la orden "
             "con exactitud:\n" + _pistas(diferencias), "aviso", "Casi")
    else:
        nota("El plan que produce su modelo NO funciona en la orden real.\n" + validacion.explicacion + "\n"
             + _pistas(diferencias), "error", "Revise su modelo")
    return


def comprobar_regla_presion(texto_dominio: str, texto_problema: str) -> None:
    """Ejercicio 3: el dominio debe exigir la prueba de presión antes de liberar el equipo."""
    if _pendiente(texto_dominio):
        nota("Todavía hay partes marcadas con «...»: complételas y vuelva a ejecutar la celda.", "aviso")
        return
    try:
        problema = u.leer_problema(texto_dominio, texto_problema)
    except u.ErrorPDDL as e:
        nota(str(e), "error", "El dominio no se pudo leer")
        return
    acciones = {a.name: a for a in problema.actions}
    if not any(f.name == "probado" for f in problema.fluents):
        nota("Falta declarar el predicado (probado ?e - equipo) en :predicates.", "aviso", "Pista")
        return
    if "probar" not in acciones:
        nota("No encuentro la acción «probar». Agréguela con sus parámetros, su precondición y su efecto.", "aviso", "Pista")
        return
    if not any(p.startswith("(probado ") for p in u.precondiciones_de(acciones["liberar"])):
        nota("La acción «liberar» todavía no exige (probado ?e): sin esa precondición, el planificador "
             "puede liberar el equipo sin probarlo.", "aviso", "Pista")
        return
    resultado = u.resolver(problema)
    if resultado.estado != "resuelto":
        nota("Con su dominio la orden ya no tiene solución: revise que «probar» se pueda aplicar después de "
             "reparar (sus precondiciones) y que produzca (probado ?e) (su efecto).", "aviso", "Pista")
        return
    nombres = [p.strip("()").split()[0] for p in resultado.pasos]
    if "probar" not in nombres:
        nota("El plan no prueba el equipo antes de liberarlo. Revise la precondición de «liberar».", "aviso", "Pista")
        return
    # El plan de su dominio se valida contra la regla de referencia: probar después de reparar, en el lugar del equipo
    referencia = u.leer_problema(base64.b64decode(_DOMINIO_PRUEBA).decode("utf-8"), texto_problema)
    lectura = u.plan_desde_texto(referencia, "\n".join(resultado.pasos))
    if lectura.estado != "ok":
        nota("La acción «probar» debe tener los mismos parámetros que «bloquear»: (?t - tecnico ?e - equipo ?l - lugar).\n"
             + "\n".join(lectura.errores), "aviso", "Pista")
        return
    validacion = u.validar(referencia, lectura.plan)
    if not validacion.valido:
        nota("Su dominio produce un plan con la prueba, pero la prueba no ocurre cuando debe:\n" + validacion.explicacion
             + "\nRevise la precondición de «probar»: el equipo debe estar reparado y todavía bloqueado, y el técnico, "
             "en el lugar del equipo.", "aviso", "Pista")
        mostrar_plan(resultado.pasos, "Plan de su dominio")
        return
    exige = {pre.strip("()").split()[0] for pre in u.precondiciones_de(acciones["probar"])}
    riesgos = {"en": "con el técnico en otro lugar", "ubicado": "en un lugar donde el equipo no está",
               "reparado": "un equipo todavía sin reparar", "bloqueado": "un equipo ya liberado"}
    faltan = [n for n in riesgos if n not in exige]
    if faltan:
        nota("En esta orden el plan prueba la bomba cuando debe, pero su acción «probar» no exige "
             f"{', '.join(f'({n} ...)' for n in faltan)}. Con otra orden, el planificador podría probar "
             f"{' o '.join(riesgos[n] for n in faltan)}.", "aviso", "Casi")
        mostrar_plan(resultado.pasos, "Plan de su dominio")
        return
    nota("¡Bien! El planificador ahora prueba el equipo después de repararlo y antes de liberarlo, sin que nadie se lo "
         "diga paso a paso.", "exito", "Comprobación")
    mostrar_plan(resultado.pasos, "Plan con la regla nueva")
    return


def comprobar_regla_bloqueo(texto_dominio: str, texto_problema: str) -> None:
    """Ejercicio opcional: solo quien bloqueó el equipo puede liberarlo."""
    if _pendiente(texto_dominio):
        nota("Todavía hay partes marcadas con «...»: complételas y vuelva a ejecutar la celda.", "aviso")
        return
    try:
        problema = u.leer_problema(texto_dominio, texto_problema)
    except u.ErrorPDDL as e:
        nota(str(e), "error", "El dominio no se pudo leer")
        return
    resultado = u.resolver(problema)
    if resultado.estado != "resuelto":
        nota("Con su dominio la orden ya no tiene solución: revise que «bloquear» registre quién bloqueó "
             "y que «liberar» lo exija y lo borre.", "aviso", "Pista")
        return
    quien_bloquea = [p.split()[1] for p in resultado.pasos if p.startswith("(bloquear ")]
    quien_libera = [p.split()[1] for p in resultado.pasos if p.startswith("(liberar ")]
    acciones = {a.name: a for a in problema.actions}
    agrega = {e.fluent.fluent().name for e in acciones["bloquear"].effects if e.value.is_true()} - {"bloqueado"}
    borra = {e.fluent.fluent().name for e in acciones["liberar"].effects if e.value.is_false()}
    if agrega - borra:
        nota(f"«liberar» debe borrar también el hecho que registra quién bloqueó ({', '.join(sorted(agrega - borra))}): "
             "si no, queda en el estado aunque el candado ya no esté, y el equipo parecería bloqueado por alguien.",
             "aviso", "Casi")
        return
    if quien_bloquea and quien_bloquea == quien_libera:
        nota(f"¡Bien! Ahora libera el equipo la misma persona que lo bloqueó ({quien_libera[0]}).", "exito", "Comprobación")
        mostrar_plan(resultado.pasos, "Plan con la norma de bloqueo")
        return
    nota(f"Bloquea {', '.join(quien_bloquea) or 'nadie'} y libera {', '.join(quien_libera) or 'nadie'}: "
         "la regla todavía no se cumple. ¿Qué hecho registra quién puso el candado?", "aviso", "Pista")
    return
