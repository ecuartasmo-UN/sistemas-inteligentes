"""Un expansor jerárquico (HTN) mínimo para el Laboratorio 2A.

Una tarea compuesta se descompone con un método (una función de Python) en subtareas,
hasta llegar a tareas primitivas, que son las acciones del dominio PDDL. El expansor
aplica los efectos de cada acción para saber dónde está cada cosa, pero no comprueba
sus precondiciones: como una receta escrita a mano, puede producir un plan inválido.
Por eso el plan que resulta siempre se valida.
"""
from __future__ import annotations

import html

from IPython.display import HTML, display

import utilidades_pddl as u


class ErrorHTN(Exception):
    """La descomposición no se pudo completar."""


def hechos(estado, predicado: str) -> list:
    """Argumentos de los hechos de un predicado: hechos(estado, "en") → [["ana", "base"], ["luis", "base"]]."""
    resultado = []
    for h in sorted(estado):
        partes = h.strip("()").split()
        if partes and partes[0] == predicado:
            resultado.append(partes[1:])
    return resultado


def expandir(problema, tareas, metodos: dict):
    """Descompone las tareas con los métodos y devuelve (pasos del plan, árbol de descomposición)."""
    acciones = {a.name: a for a in problema.actions}
    estado = u.estado_inicial(problema)
    pasos = []

    def nodo(tarea):
        nonlocal estado
        nombre, *argumentos = tarea
        etiqueta = f"({nombre}{' ' + ' '.join(argumentos) if argumentos else ''})"
        if nombre in acciones:
            estado = u.aplicar(acciones[nombre], u.objetos(problema, argumentos), estado)
            pasos.append(etiqueta)
            return {"tarea": etiqueta, "primitiva": True, "hijos": []}
        if nombre not in metodos:
            raise ErrorHTN(f"No hay un método para la tarea «{nombre}».")
        subtareas = metodos[nombre](estado, *argumentos)
        return {"tarea": etiqueta, "primitiva": False, "hijos": [nodo(s) for s in subtareas]}

    arbol = [nodo(t) for t in tareas]
    return pasos, arbol


def mostrar_arbol(arbol) -> None:
    """Muestra el árbol de descomposición: tareas compuestas en negrita y acciones en verde."""
    def lista(nodos):
        items = []
        for n in nodos:
            if n["primitiva"]:
                items.append(f"<li><code style='color:#14532d;background:#dcfce7;border-radius:4px;padding:0 4px'>"
                             f"{html.escape(n['tarea'])}</code></li>")
            else:
                items.append(f"<li><b>{html.escape(n['tarea'])}</b>{lista(n['hijos']) if n['hijos'] else ' <i>(nada que hacer)</i>'}</li>")
        return "<ul style='margin:2px 0 2px 4px'>" + "".join(items) + "</ul>"
    display(HTML(f"<div style='font-family:system-ui,sans-serif;font-size:14px;color:#1f2328;background:#ffffff;"
                 f"border:1px solid #d0d7de;border-radius:8px;padding:8px 12px'>{lista(arbol)}</div>"))
