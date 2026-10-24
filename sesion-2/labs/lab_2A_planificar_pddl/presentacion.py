"""Funciones de presentación para los notebooks de la Sesión 2 de Sistemas Inteligentes.

Muestran planes, trazas, veredictos, documentos y comparaciones como HTML.
Cada caja define su propio fondo y su color de texto, para que se lea igual
con el tema claro y con el tema oscuro de VS Code.
"""
from __future__ import annotations

import csv
import difflib
import html
import inspect
import re
from pathlib import Path

from IPython.display import HTML, Markdown, display

_FUENTE = 'font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:14px;line-height:1.5;text-align:left;'
_MONO = "font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;"
_COLORES = {
    "info": ("#eaf2fb", "#173f73", "#9cc2ec"),
    "exito": ("#e8f6ec", "#14532d", "#8fd19e"),
    "error": ("#fdecea", "#7f1d1d", "#f1a7a0"),
    "aviso": ("#fff6e0", "#6b3f00", "#f0c96b"),
    "neutro": ("#f6f7f9", "#1f2328", "#d0d7de"),
}


def _e(texto) -> str:
    return html.escape(str(texto))


def caja(contenido_html: str, tipo: str = "info", titulo: str | None = None) -> None:
    """Muestra una caja de color con contenido HTML (tipos: info, exito, error, aviso, neutro)."""
    fondo, color, borde = _COLORES.get(tipo, _COLORES["info"])
    cabeza = f"<div style='font-weight:700;margin-bottom:4px'>{_e(titulo)}</div>" if titulo else ""
    display(HTML(f"<div style='{_FUENTE}background:{fondo};color:{color};border:1px solid {borde};"
                 f"border-radius:8px;padding:10px 14px;margin:8px 0'>{cabeza}{contenido_html}</div>"))


def nota(texto: str, tipo: str = "info", titulo: str | None = None) -> None:
    """Muestra un mensaje breve en una caja de color."""
    caja(_e(texto).replace("\n", "<br>"), tipo, titulo)


# ----------------------------------------------------------------------------- PDDL y planes

_PALABRAS_PDDL = r"(define|domain|problem|:domain|:requirements|:types|:predicates|:action|:parameters|:precondition|:effect|:objects|:init|:goal|and|not|:strips|:typing)"


def _resaltar_pddl(texto: str) -> str:
    """Colorea comentarios, palabras clave y variables de un texto PDDL ya escapado."""
    lineas = []
    for linea in texto.split("\n"):
        codigo, _, comentario = linea.partition(";")
        codigo = re.sub(r"(?<![\w-])" + _PALABRAS_PDDL + r"(?![\w-])",
                        r"<span style='color:#8250df;font-weight:600'>\1</span>", codigo)
        codigo = re.sub(r"(\?[\w-]+)", r"<span style='color:#b35900'>\1</span>", codigo)
        if comentario:
            codigo += f"<span style='color:#6e7781;font-style:italic'>;{comentario}</span>"
        lineas.append(codigo)
    return "\n".join(lineas)


def mostrar_pddl(texto: str, titulo: str | None = None) -> None:
    """Muestra un texto PDDL con colores."""
    cabeza = (f"<div style='{_FUENTE}font-weight:700;color:#1f2328;background:#eef1f4;padding:6px 12px;"
              f"border-radius:8px 8px 0 0;border:1px solid #d0d7de;border-bottom:none'>{_e(titulo)}</div>") if titulo else ""
    radio = "0 0 8px 8px" if titulo else "8px"
    display(HTML(f"{cabeza}<pre style='{_MONO}background:#f6f8fa;color:#1f2328;border:1px solid #d0d7de;"
                 f"border-radius:{radio};padding:10px 12px;margin:0 0 8px 0;white-space:pre;overflow-x:auto'>"
                 f"{_resaltar_pddl(_e(texto.strip()))}</pre>"))


def mostrar_plan(pasos, titulo: str = "Plan") -> None:
    """Muestra un plan como lista numerada de acciones."""
    if not pasos:
        nota("El plan está vacío.", "aviso", titulo)
        return
    filas = "".join(f"<li style='margin:2px 0'><code style='{_MONO}background:transparent;color:#1f2328'>{_e(p)}</code></li>"
                    for p in pasos)
    caja(f"<ol style='margin:4px 0 0 18px;padding:0'>{filas}</ol>", "neutro", f"{titulo} · {len(pasos)} pasos")


def _fichas(hechos, fondo, color, tachado=False) -> str:
    deco = "text-decoration:line-through;" if tachado else ""
    return " ".join(f"<span style='{_MONO}{deco}background:{fondo};color:{color};border-radius:6px;padding:1px 6px;"
                    f"margin:1px;display:inline-block'>{_e(h)}</span>" for h in hechos) or "—"


def mostrar_estado(hechos, titulo: str = "Estado") -> None:
    """Muestra un conjunto de hechos como fichas."""
    caja(_fichas(sorted(hechos), "#eef1f4", "#1f2328"), "neutro", f"{titulo} · {len(hechos)} hechos")


def mostrar_traza(traza: dict, mostrar_estados: bool = False) -> None:
    """Muestra la traza de un plan: en cada paso, los hechos que se agregan y los que se eliminan."""
    th = f"style='{_FUENTE}text-align:left;padding:6px 8px;background:#eef1f4;color:#1f2328;border-bottom:2px solid #d0d7de'"
    td = f"style='{_FUENTE}vertical-align:top;padding:6px 8px;color:#1f2328;border-bottom:1px solid #e1e4e8'"
    cab = f"<tr><th {th}>Paso</th><th {th}>Acción</th><th {th}>Se agrega</th><th {th}>Se elimina</th>"
    cab += f"<th {th}>Estado resultante</th></tr>" if mostrar_estados else "</tr>"
    filas = [f"<tr><td {td}>S0</td><td {td}><i>estado inicial</i></td><td {td} colspan='{3 if mostrar_estados else 2}'>"
             f"{_fichas(traza['inicial'], '#eef1f4', '#1f2328')}</td></tr>"]
    for p in traza["pasos"]:
        if not p["aplicable"]:
            td_error = f"style='{_FUENTE}vertical-align:top;padding:6px 8px;color:#7f1d1d;border-bottom:1px solid #e1e4e8'"
            filas.append(f"<tr><td {td}>{p['paso']}</td><td {td}><code style='{_MONO}color:#7f1d1d;background:transparent;white-space:nowrap'>"
                         f"{_e(p['accion'])}</code></td><td {td_error} colspan='{3 if mostrar_estados else 2}'>"
                         f"✗ No se puede aplicar: falta {_fichas(p['faltantes'], '#fdecea', '#7f1d1d')}</td></tr>")
            continue
        fila = (f"<tr><td {td}>{p['paso']}</td><td {td}><code style='{_MONO}background:transparent;color:#1f2328;white-space:nowrap'>{_e(p['accion'])}</code></td>"
                f"<td {td}>{_fichas(p['agrega'], '#dcfce7', '#14532d')}</td><td {td}>{_fichas(p['elimina'], '#fee2e2', '#7f1d1d', True)}</td>")
        if mostrar_estados:
            fila += f"<td {td}>{_fichas(p['estado'], '#eef1f4', '#1f2328')}</td>"
        filas.append(fila + "</tr>")
    fondo, color, borde = _COLORES["exito" if traza["meta_cumplida"] else "aviso"]
    pie = ("✓ Al final se cumple la meta: " if traza["meta_cumplida"] else "La meta no se cumple al final: ") + " ".join(traza["metas"])
    display(HTML(f"<div style='overflow-x:auto;margin:8px 0'><table style='border-collapse:collapse;background:#ffffff;"
                 f"border:1px solid #d0d7de;border-radius:8px'>{cab}{''.join(filas)}</table>"
                 f"<div style='{_FUENTE}background:{fondo};color:{color};border:1px solid {borde};border-radius:6px;"
                 f"padding:6px 10px;margin-top:6px'>{_e(pie)}</div></div>"))


def mostrar_veredicto(validacion, titulo: str = "Veredicto del validador") -> None:
    """Muestra si un plan es válido y, si no lo es, qué falla."""
    original = (f"<div style='{_MONO}margin-top:6px;opacity:0.85'>Mensaje original del validador: "
                f"{_e(validacion.mensaje_validador)}</div>") if validacion.mensaje_validador else ""
    if validacion.valido:
        caja(f"✓ {_e(validacion.explicacion)}{original}", "exito", titulo)
    else:
        caja(f"✗ {_e(validacion.explicacion)}{original}", "error", titulo)


def mostrar_planificacion(resultado, titulo: str = "Resultado del planificador") -> None:
    """Muestra lo que devolvió el planificador."""
    tipo = {"resuelto": "exito", "sin_solucion": "aviso"}.get(resultado.estado, "error")
    caja(_e(resultado.mensaje), tipo, titulo)
    if resultado.pasos:
        mostrar_plan(resultado.pasos, "Plan encontrado")


# ----------------------------------------------------------------------------- tablas, documentos y texto

def mostrar_tabla(filas, columnas=None, titulo: str | None = None) -> None:
    """Muestra una tabla a partir de una lista de diccionarios (o de listas, con columnas)."""
    if not filas:
        nota("No hay filas para mostrar.", "aviso", titulo)
        return
    if isinstance(filas[0], dict):
        columnas = columnas or list(filas[0].keys())
        filas = [[f.get(c, "") for c in columnas] for f in filas]
    th = f"style='{_FUENTE}text-align:left;padding:6px 10px;background:#eef1f4;color:#1f2328;border-bottom:2px solid #d0d7de'"
    td = f"style='{_FUENTE}vertical-align:top;padding:5px 10px;color:#1f2328;border-bottom:1px solid #e1e4e8'"
    cuerpo = "".join("<tr>" + "".join(f"<td {td}>{_e(v)}</td>" for v in fila) + "</tr>" for fila in filas)
    cabeza = f"<div style='{_FUENTE}font-weight:700;margin:6px 0 4px'>{_e(titulo)}</div>" if titulo else ""
    display(HTML(f"{cabeza}<div style='overflow-x:auto'><table style='border-collapse:collapse;background:#ffffff;"
                 f"border:1px solid #d0d7de'><tr>{''.join(f'<th {th}>{_e(c)}</th>' for c in columnas)}</tr>{cuerpo}</table></div>"))


def mostrar_markdown(texto: str) -> None:
    """Muestra texto Markdown renderizado."""
    display(Markdown(texto))


def mostrar_archivo(ruta, titulo: str | None = None) -> None:
    """Muestra un archivo: Markdown renderizado, CSV como tabla y el resto como texto."""
    ruta = Path(ruta)
    titulo = titulo or ruta.name
    if ruta.suffix.lower() == ".csv":
        with ruta.open(encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
        mostrar_tabla(filas, titulo=f"📄 {titulo}")
        return
    texto = ruta.read_text(encoding="utf-8")
    if ruta.suffix.lower() == ".md":
        display(HTML(f"<div style='{_FUENTE}font-weight:700;margin:10px 0 2px'>📄 {_e(titulo)}</div>"))
        display(Markdown(texto))
        return
    display(HTML(f"<div style='{_FUENTE}font-weight:700;margin:10px 0 2px'>📄 {_e(titulo)}</div>"
                 f"<pre style='{_MONO}background:#f6f8fa;color:#1f2328;border:1px solid #d0d7de;border-radius:8px;"
                 f"padding:10px 12px;white-space:pre-wrap'>{_e(texto)}</pre>"))


def mostrar_diferencias(antes: str, despues: str, nombre_antes: str = "antes", nombre_despues: str = "después") -> None:
    """Muestra las diferencias entre dos textos: en verde lo agregado, en rojo lo eliminado."""
    lineas = list(difflib.unified_diff(antes.splitlines(), despues.splitlines(), nombre_antes, nombre_despues, lineterm="", n=2))
    if not lineas:
        nota("Los dos textos son iguales.", "info")
        return
    salida = []
    for l in lineas:
        if l.startswith("+++") or l.startswith("---"):
            estilo = "color:#57606a;font-weight:600"
        elif l.startswith("@@"):
            estilo = "color:#0969da"
        elif l.startswith("+"):
            estilo = "background:#dcfce7;color:#14532d"
        elif l.startswith("-"):
            estilo = "background:#fee2e2;color:#7f1d1d"
        else:
            estilo = "color:#1f2328"
        salida.append(f"<span style='{estilo};display:block'>{_e(l) or '&nbsp;'}</span>")
    display(HTML(f"<pre style='{_MONO}background:#f6f8fa;border:1px solid #d0d7de;border-radius:8px;padding:8px 10px;"
                 f"white-space:pre-wrap'>{''.join(salida)}</pre>"))


def mostrar_conversacion(mensajes, titulo: str = "Conversación con el LLM", abierta: bool = False) -> None:
    """Muestra los mensajes intercambiados con el LLM en un bloque desplegable."""
    colores = {"system": ("#f3e8ff", "#4c1d95", "Instrucción de sistema"), "user": ("#eaf2fb", "#173f73", "Instrucción"),
               "assistant": ("#e8f6ec", "#14532d", "Respuesta del LLM"), "critica": ("#fdecea", "#7f1d1d", "Crítica del validador")}
    bloques = []
    for m in mensajes:
        fondo, color, etiqueta = colores.get(m.get("rol", m.get("role")), ("#f6f7f9", "#1f2328", m.get("rol", "")))
        bloques.append(f"<div style='background:{fondo};color:{color};border-radius:6px;padding:6px 10px;margin:6px 0'>"
                       f"<div style='{_FUENTE}font-weight:700'>{_e(etiqueta)}</div>"
                       f"<pre style='{_MONO}white-space:pre-wrap;margin:4px 0 0;color:{color};background:transparent'>"
                       f"{_e(m.get('contenido', m.get('content', '')))}</pre></div>")
    display(HTML(f"<details {'open' if abierta else ''} style='{_FUENTE}margin:8px 0;color:#1f2328;background:#ffffff;"
                 f"border:1px solid #d0d7de;border-radius:8px;padding:6px 10px'><summary style='cursor:pointer;font-weight:700'>"
                 f"{_e(titulo)} ({len(mensajes)} mensajes)</summary>{''.join(bloques)}</details>"))


def mostrar_fuente(objeto) -> None:
    """Muestra el código fuente de una función o clase de los módulos de apoyo."""
    display(HTML(f"<pre style='{_MONO}background:#f6f8fa;color:#1f2328;border:1px solid #d0d7de;border-radius:8px;"
                 f"padding:10px 12px;white-space:pre;overflow-x:auto'>{_e(inspect.getsource(objeto))}</pre>"))
