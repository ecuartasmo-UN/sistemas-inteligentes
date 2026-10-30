"""Gráficas y tablas del Laboratorio 6A: el árbol dibujado, la validación cruzada, la curva de profundidad, las matrices
de confusión con costo y la curva de costo según el umbral.

Usan los colores de las diapositivas de la charla inicial, oscurecidos para el fondo blanco: azul para el entrenamiento,
ámbar para la validación, verde para «sobrevive» y para lo mejor, y rojo para «no sobrevive» y para lo que cuesta.
Las tablas son HTML con sus propios colores, para que se lean igual con el tema claro y con el oscuro de VS Code.
"""
from __future__ import annotations

import html
import io
import math
import textwrap

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import HTML, Image, display

AZUL, AMBAR, VERDE, ROJO, GRIS = "#0284c7", "#d97706", "#16a34a", "#dc2626", "#6b7280"
VERDE_OSCURO = "#166534"
MARCAS = ["o", "s", "D", "^", "v", "P"]
OTROS = ["#7c3aed", "#0284c7", "#d97706", "#0f766e", "#db2777", "#4d7c0f"]
_FUENTE = 'font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:14px;line-height:1.45;'
matplotlib.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})


def _e(texto) -> str:
    return html.escape(str(texto))


def _n(valor, decimales: int = 0) -> str:
    return f"{valor:,.{decimales}f}".replace(",", " ").replace(".", ",")


def _mostrar(fig) -> None:
    """Muestra la figura como PNG sobre fondo blanco."""
    fig.patch.set_facecolor("white")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    display(Image(data=buf.getvalue(), format="png"))


def _color_clase(clase: str, clases: list) -> str:
    if clase == "sobrevive":
        return VERDE
    if clase == "no sobrevive":
        return ROJO
    return OTROS[clases.index(clase) % len(OTROS)] if clase in clases else GRIS


# ------------------------------------------------------------------ el árbol

def dibujar_arbol(nodos: list, clases: list, titulo: str) -> None:
    """Dibuja un árbol: las preguntas en cajas azules, los rótulos de cada rama y las hojas con su conclusión y sus casos."""
    por_id = {n["id"]: n for n in nodos}
    orden_hojas, nivel = [], {}

    def recorrer(i, profundidad):
        nivel[i] = profundidad
        n = por_id[i]
        if n["hoja"]:
            orden_hojas.append(i)
        else:
            recorrer(n["izquierda"], profundidad + 1)
            recorrer(n["derecha"], profundidad + 1)

    recorrer(0, 0)
    x = {}

    def posicion(i):
        n = por_id[i]
        if n["hoja"]:
            x[i] = float(orden_hojas.index(i))
        else:
            x[i] = (posicion(n["izquierda"]) + posicion(n["derecha"])) / 2
        return x[i]

    posicion(0)
    hojas, niveles = len(orden_hojas), max(nivel.values()) + 1
    fig, ax = plt.subplots(figsize=(max(7.5, 1.75 * hojas), 1.55 * niveles + 0.4))
    y = {i: -1.25 * nivel[i] for i in por_id}
    for n in nodos:
        if not n["hoja"]:
            for hijo, rotulo in ((n["izquierda"], n["rotulo_izquierda"]), (n["derecha"], n["rotulo_derecha"])):
                ax.plot([x[n["id"]], x[hijo]], [y[n["id"]], y[hijo]], color="#94a3b8", lw=1.4, zorder=1)
                # el rótulo va más cerca del hijo que del padre, para que no choque con el de la rama vecina
                ax.text(0.42 * x[n["id"]] + 0.58 * x[hijo], 0.42 * y[n["id"]] + 0.58 * y[hijo],
                        "\n".join(textwrap.wrap(rotulo, 12, break_long_words=False)), ha="center", va="center", fontsize=9.5, color="#475569",
                        zorder=3, bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none"})
    for n in nodos:
        if n["hoja"]:
            color = _color_clase(n["clase"], clases)
            texto = "\n".join(textwrap.wrap(n["clase"], 16)) + f"\n{n['aciertos']} de {n['casos']}"
            ax.text(x[n["id"]], y[n["id"]], texto, ha="center", va="center", fontsize=10, color=color, fontweight="bold",
                    zorder=4, bbox={"boxstyle": "round,pad=0.35", "fc": "white", "ec": color, "lw": 1.8})
        else:
            ax.text(x[n["id"]], y[n["id"]], "\n".join(textwrap.wrap(n["pregunta"], 22)), ha="center", va="center",
                    fontsize=10, color="#0c4a6e", zorder=4,
                    bbox={"boxstyle": "round,pad=0.35", "fc": "#eaf2fb", "ec": AZUL, "lw": 1.4})
    ax.set_xlim(-0.7, hojas - 0.3)
    ax.set_ylim(-1.25 * (niveles - 1) - 0.65, 0.55)
    ax.axis("off")
    ax.set_title(titulo, fontsize=12, loc="left", color="#1f2328")
    _mostrar(fig)


def partes_validacion(aciertos, titulo: str) -> None:
    """El acierto de cada parte de la validación cruzada, en fichas, y su promedio."""
    fichas = "".join(
        f"<div style='background:#eaf2fb;color:#0c4a6e;border:1px solid #9cc2ec;border-radius:8px;padding:6px 12px;"
        f"text-align:center;min-width:86px'><div style='font-size:12px'>parte {i}</div>"
        f"<div style='font-weight:700'>{_n(100 * a, 1)} %</div></div>" for i, a in enumerate(aciertos, 1))
    promedio = (f"<div style='background:#fff6e0;color:#6b3f00;border:2px solid #d97706;border-radius:8px;padding:6px 12px;"
                f"text-align:center;min-width:96px'><div style='font-size:12px'>promedio</div>"
                f"<div style='font-weight:700'>{_n(100 * sum(aciertos) / len(aciertos), 1)} %</div></div>")
    display(HTML(f"<div style='{_FUENTE}color:#1f2328;margin:6px 0 2px;font-weight:700'>{_e(titulo)}</div>"
                 f"<div style='{_FUENTE}display:flex;flex-wrap:wrap;gap:8px;margin:4px 0 10px'>{fichas}{promedio}</div>"))


def curva_profundidad(filas: list, mejor: dict, nombre: str) -> None:
    """El acierto en entrenamiento y en validación cruzada según la profundidad del árbol, como en la diapositiva 11."""
    etiquetas = ["∞" if f["profundidad"] == "sin límite" else str(f["profundidad"]) for f in filas]
    xs = list(range(len(filas)))
    entrenamiento = [100 * f["entrenamiento"] for f in filas]
    validacion = [100 * f["validacion"] for f in filas]
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    ax.plot(xs, entrenamiento, color=AZUL, lw=2.5, marker="o", label="acierto en entrenamiento")
    ax.plot(xs, validacion, color=AMBAR, lw=2.5, marker="o", label="acierto en validación cruzada")
    k = filas.index(mejor)
    ax.axvline(k, color=VERDE, ls="--", lw=1.6)
    ax.annotate(f"la mejor en validación: profundidad {etiquetas[k]} · {_n(100 * mejor['validacion'], 1)} %", (k, 100),
                xytext=(6, -14), textcoords="offset points", color=VERDE, fontweight="bold", fontsize=11)
    ax.set_xticks(xs, etiquetas)
    ax.set_xlabel("profundidad máxima del árbol (∞ = sin límite)")
    ax.set_ylabel("aciertos (%)")
    bajo = min(entrenamiento + validacion)
    ax.set_ylim(max(0, math.floor(bajo / 5) * 5 - 5), 102)
    ax.grid(axis="y", color="#e5e7eb")
    ax.legend(loc="lower right", frameon=False)
    ax.set_title(f"¿Qué tan profundo? · {nombre}", fontsize=12, loc="left")
    _mostrar(fig)


# ------------------------------------------------------------------ el costo del error

def matrices_costo(resultados: list, costo_mal_aprobado: float, costo_buen_rechazado: float) -> None:
    """Una matriz de confusión por umbral, con el costo de cada casilla y el total."""
    def celda(cantidad, costo, color_fondo, color_texto):
        detalle = f"× {_n(costo, 2 if not float(costo).is_integer() else 0)} = {_n(cantidad * costo, 0)}" if costo else "sin costo"
        return (f"<td style='padding:6px 10px;border:1px solid #d0d7de;background:{color_fondo};color:{color_texto};"
                f"text-align:center'><div style='font-weight:700;font-size:15px'>{cantidad}</div>"
                f"<div style='font-size:12px'>{detalle}</div></td>")

    th = "style='padding:5px 10px;background:#eef1f4;color:#1f2328;border:1px solid #d0d7de;font-weight:600'"
    bloques = []
    for r in resultados:
        tabla = (f"<table style='border-collapse:collapse;background:#ffffff'>"
                 f"<tr><th {th}>real ↓ · decisión →</th><th {th}>aprobar</th><th {th}>rechazar</th></tr>"
                 f"<tr><th {th}>buen pagador</th>{celda(r['buenos_aprobados'], 0, '#f6f7f9', '#1f2328')}"
                 f"{celda(r['buenos_rechazados'], costo_buen_rechazado, '#fff6e0', '#6b3f00')}</tr>"
                 f"<tr><th {th}>mal pagador</th>{celda(r['malos_aprobados'], costo_mal_aprobado, '#fdecea', '#7f1d1d')}"
                 f"{celda(r['malos_rechazados'], 0, '#f6f7f9', '#1f2328')}</tr></table>")
        bloques.append(f"<div><div style='font-weight:700;margin-bottom:4px'>{_e(r['nombre'])}</div>{tabla}"
                       f"<div style='margin-top:4px'>costo total: <b>{_n(r['costo'], 0)}</b> · aciertos: "
                       f"{_n(100 * r['exactitud'], 1)} %</div></div>")
    display(HTML(f"<div style='{_FUENTE}color:#1f2328;display:flex;flex-wrap:wrap;gap:22px;margin:8px 0'>{''.join(bloques)}</div>"))


def curva_costo(curva: list, probados: list, teorico: float, texto_teorico: str, minimo: dict, referencias: dict) -> None:
    """El costo total según el umbral, con los umbrales probados, el umbral teórico y el de menor costo en estos datos.

    Los rótulos van en una leyenda debajo de la gráfica, para no tapar la curva."""
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    ax.plot([c["umbral"] for c in curva], [c["costo"] for c in curva], color=AMBAR, lw=2.5, label="costo total según el umbral")
    for nombre, valor, estilo in (("rechazar a todos", referencias["rechazar"], ":"), ("aprobar a todos", referencias["aprobar"], "--")):
        ax.axhline(valor, color=GRIS, ls=estilo, lw=1.2)
        ax.annotate(f"{nombre}: {_n(valor)}", (0.99, valor), xycoords=("axes fraction", "data"), xytext=(0, 4),
                    textcoords="offset points", ha="right", color=GRIS, fontsize=10)
    bajo = min(c["costo"] for c in curva)
    alto = max(referencias.values())
    ax.set_ylim(max(0, bajo - 0.25 * (alto - bajo)), alto + 0.08 * (alto - bajo))
    ax.axvline(teorico, color=VERDE, ls="--", lw=1.6, label=f"umbral teórico: {texto_teorico}")
    for k, r in enumerate(probados):      # cada umbral probado con su propia marca roja
        ax.plot([r["umbral"]], [r["costo"]], MARCAS[k % len(MARCAS)], color=ROJO, ms=8, zorder=6, ls="none",
                label=f"{r['nombre']}: costo {_n(r['costo'])}")
    ax.plot([minimo["umbral"]], [minimo["costo"]], "o", mfc="none", mec=VERDE_OSCURO, mew=2.4, ms=16, zorder=7, ls="none",
            label=f"menor costo en estos datos: umbral {_n(minimo['umbral'], 2)} · costo {_n(minimo['costo'])}")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False, fontsize=10, numpoints=1)
    ax.set_xlim(0, 1)
    ax.set_xlabel("umbral: probabilidad de ser mal pagador desde la cual se rechaza")
    ax.set_ylabel("costo total")
    ax.grid(axis="y", color="#e5e7eb")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: _n(v, 1)))
    ax.set_title("El costo total según el umbral · German Credit", fontsize=12, loc="left")
    _mostrar(fig)
