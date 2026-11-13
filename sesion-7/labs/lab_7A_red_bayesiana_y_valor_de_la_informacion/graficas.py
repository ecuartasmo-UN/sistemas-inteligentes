"""Gráficas del Laboratorio 7A: el árbol de frecuencias, la red de la alarma, las barras de creencia,
el diagrama de influencia y la curva del valor de la información.

Usan los colores de las diapositivas, oscurecidos para el fondo blanco: azul para el azar, ámbar para las decisiones,
verde para las utilidades y rojo para las fallas. Se dibujan con matplotlib, sin Graphviz.
"""
from __future__ import annotations

import io
import textwrap

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import Image, display
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon

AZUL, AMBAR, VERDE, ROJO, GRIS, TINTA = "#0284c7", "#d97706", "#16a34a", "#dc2626", "#6b7280", "#1f2328"
FONDO_AZUL, FONDO_AMBAR, FONDO_VERDE, FONDO_ROJO, FONDO_GRIS = "#d9ecfa", "#fde9c4", "#dcfce7", "#fee2e2", "#eef1f4"
matplotlib.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})


def _n(valor: float, decimales: int = 1) -> str:
    """Un número con punto decimal y espacio para los miles, sin ceros que sobren."""
    texto = f"{valor:,.{decimales}f}".replace(",", " ")
    return texto.rstrip("0").rstrip(".") if "." in texto else texto


def _mostrar(fig) -> None:
    fig.patch.set_facecolor("white")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    display(Image(data=buf.getvalue(), format="png"))


def _caja(ax, x, y, texto, borde, fondo, ancho=2.4, alto=0.8, tam=12, negrita=False) -> None:
    ax.add_patch(FancyBboxPatch((x - ancho / 2, y - alto / 2), ancho, alto, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fondo, ec=borde, lw=1.6))
    ax.text(x, y, texto, ha="center", va="center", fontsize=tam, color=TINTA, fontweight="bold" if negrita else "normal")


def _flecha(ax, de, a, color=GRIS, rad=0.0) -> None:
    ax.add_patch(FancyArrowPatch(de, a, arrowstyle="-|>", mutation_scale=18, color=color, lw=1.6,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


def _borde_elipse(dx: float, dy: float, semi_x: float, semi_y: float) -> tuple:
    """El punto del borde de una elipse en la dirección (dx, dy), medido desde su centro."""
    largo = (dx ** 2 + dy ** 2) ** 0.5
    ux, uy = dx / largo, dy / largo
    t = 1 / ((ux / semi_x) ** 2 + (uy / semi_y) ** 2) ** 0.5
    return ux * t, uy * t


# ----------------------------------------------------------------------------- 1. la tasa base

def arbol_de_frecuencias(bombas: int, tasa: float, sensibilidad: float, especificidad: float) -> None:
    """De 1000 bombas, cuántas fallan y cuántas hacen sonar la alarma: la regla de Bayes con frecuencias."""
    fallan = bombas * tasa
    sanas = bombas - fallan
    detectadas, calladas = fallan * sensibilidad, fallan * (1 - sensibilidad)
    falsas, silencio = sanas * (1 - especificidad), sanas * especificidad
    avisos = detectadas + falsas
    fig, ax = plt.subplots(figsize=(10, 4.6))
    _caja(ax, 5, 4.2, f"{_n(bombas)} bombas", GRIS, FONDO_GRIS, ancho=2.6, negrita=True)
    def contar(n, singular, plural):
        return f"{_n(n)} {singular if abs(n - 1) < 1e-9 else plural}"
    _caja(ax, 2.5, 2.8, contar(fallan, "falla", "fallan"), ROJO, FONDO_ROJO, ancho=2.6)
    _caja(ax, 7.5, 2.8, contar(sanas, "sana", "sanas"), AZUL, FONDO_AZUL, ancho=2.6)
    hojas = [(1.2, contar(detectadas, "avisa", "avisan"), True), (3.8, contar(calladas, "calla", "callan"), False),
             (6.2, contar(falsas, "avisa", "avisan"), True), (8.8, contar(silencio, "calla", "callan"), False)]
    for x, texto, aviso in hojas:
        _caja(ax, x, 1.4, texto, AMBAR if aviso else GRIS, FONDO_AMBAR if aviso else "white", ancho=2.3)
    for (x0, y0), (x1, y1) in (((5, 3.8), (2.5, 3.2)), ((5, 3.8), (7.5, 3.2)), ((2.5, 2.4), (1.2, 1.8)),
                               ((2.5, 2.4), (3.8, 1.8)), ((7.5, 2.4), (6.2, 1.8)), ((7.5, 2.4), (8.8, 1.8))):
        ax.plot([x0, x1], [y0, y1], color=GRIS, lw=1.4)
    ax.text(2.0, 3.65, f"tasa de falla: {_n(tasa * 100)} %", ha="center", fontsize=10.5, color=GRIS)
    ax.text(1.2, 0.75, f"sensibilidad {_n(sensibilidad * 100)} %", ha="center", fontsize=10.5, color=GRIS)
    ax.text(6.2, 0.75, f"falsas alarmas: {_n((1 - especificidad) * 100)} % de las sanas", ha="center", fontsize=10.5,
            color=GRIS)
    posterior = detectadas / avisos if avisos else 0
    ax.text(5, -0.05, f"De {_n(avisos)} avisos, {_n(detectadas)} son fallas: {_n(posterior * 100)} %", ha="center",
            fontsize=14, color="#b45309", fontweight="bold")
    ax.set_xlim(-0.2, 10.2)
    ax.set_ylim(-0.4, 4.7)
    ax.axis("off")
    _mostrar(fig)


# ----------------------------------------------------------------------------- 2. la red de la alarma

def red_de_la_alarma(tablas: dict) -> None:
    """La red con cinco nodos y, junto a cada uno, su tabla pequeña."""
    fig, ax = plt.subplots(figsize=(11, 5.6))
    pos = {"Robo": (2.6, 4.4), "Sismo": (7.4, 4.4), "Alarma": (5, 2.8), "Juan": (2.6, 1.0), "María": (7.4, 1.0)}
    for de, a in (("Robo", "Alarma"), ("Sismo", "Alarma"), ("Alarma", "Juan"), ("Alarma", "María")):
        (x0, y0), (x1, y1) = pos[de], pos[a]
        bx, by = _borde_elipse(x1 - x0, y1 - y0, 1.0, 0.425)
        _flecha(ax, (x0 + bx, y0 + by), (x1 - bx * 1.04, y1 - by * 1.04), color=AZUL)
    for nombre, (x, y) in pos.items():
        ax.add_patch(Ellipse((x, y), 2.0, 0.85, fc=FONDO_AZUL, ec=AZUL, lw=2))
        ax.text(x, y, nombre, ha="center", va="center", fontsize=14, fontweight="bold", color=TINTA)
    a = tablas["Alarma"]
    textos = {
        "Robo": (0.2, 4.4, f"P(robo) = {_n(tablas['Robo'], 4)}", "right"),
        "Sismo": (9.8, 4.4, f"P(sismo) = {_n(tablas['Sismo'], 4)}", "left"),
        "Alarma": (6.35, 2.8, "robo  sismo   P(alarma)\n"
                              f" sí     sí      {_n(a[('si', 'si')], 3)}\n sí     no      {_n(a[('si', 'no')], 3)}\n"
                              f" no     sí      {_n(a[('no', 'si')], 3)}\n no     no      {_n(a[('no', 'no')], 3)}", "left"),
        "Juan": (1.35, 1.0, f"alarma  P(llama)\n  sí     {_n(tablas['Juan']['si'], 3)}\n  no     {_n(tablas['Juan']['no'], 3)}",
                 "right"),
        "María": (8.65, 1.0, f"alarma  P(llama)\n  sí     {_n(tablas['María']['si'], 3)}\n  no     {_n(tablas['María']['no'], 3)}",
                  "left"),
    }
    for _, (x, y, texto, lado) in textos.items():
        ax.text(x, y, texto, ha=lado, va="center", multialignment="left", fontsize=11, family="monospace", color=TINTA,
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#d0d7de"))
    ax.text(5, 5.25, "Cada flecha va de la causa al efecto. Cada nodo guarda su tabla: la probabilidad de «sí» según sus padres.",
            ha="center", fontsize=11, color=GRIS)
    ax.set_xlim(-1.6, 11.6)
    ax.set_ylim(0.2, 5.5)
    ax.set_aspect("equal")
    ax.axis("off")
    _mostrar(fig)


def barras_de_creencia(filas: list, titulo: str) -> None:
    """Una barra por escenario: la probabilidad del robo según lo que sabes."""
    if not filas:
        return
    fig, ax = plt.subplots(figsize=(9.5, 0.62 * len(filas) + 1.1))
    etiquetas = ["\n".join(textwrap.wrap(t, 34)) for t, _ in filas]
    valores = [v * 100 for _, v in filas]
    y = list(range(len(filas)))[::-1]
    ax.barh(y, valores, color=AZUL, height=0.6)
    tope = max(max(valores) * 1.25, 5)
    for yi, v in zip(y, valores):
        ax.text(v + tope * 0.01, yi, (f"{v:.2g} %" if 0 < v < 0.05 else f"{v:.1f} %"), va="center", fontsize=11.5,
                color=TINTA, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(etiquetas, fontsize=11)
    ax.set_xlim(0, tope)
    ax.set_xlabel("probabilidad del robo (%)")
    ax.set_title(titulo, fontsize=12.5, loc="left")
    _mostrar(fig)


# ----------------------------------------------------------------------------- 5 y 6. el diagrama de influencia

def _rombo(ax, x, y, texto, ancho=2.9, alto=1.15) -> None:
    ax.add_patch(Polygon([(x - ancho / 2, y), (x, y + alto / 2), (x + ancho / 2, y), (x, y - alto / 2)], closed=True,
                         fc=FONDO_VERDE, ec=VERDE, lw=2))
    ax.text(x, y, "\n".join(textwrap.wrap(texto, 14)), ha="center", va="center", fontsize=11, color=TINTA, fontweight="bold")


def _ovalo(ax, x, y, texto) -> None:
    ax.add_patch(Ellipse((x, y), 2.5, 0.95, fc=FONDO_AZUL, ec=AZUL, lw=2))
    ax.text(x, y, "\n".join(textwrap.wrap(texto, 16)), ha="center", va="center", fontsize=11, color=TINTA, fontweight="bold")


def _rectangulo(ax, x, y, texto) -> None:
    ax.add_patch(FancyBboxPatch((x - 1.2, y - 0.42), 2.4, 0.84, boxstyle="round,pad=0.02,rounding_size=0.05",
                                fc=FONDO_AMBAR, ec=AMBAR, lw=2))
    ax.text(x, y, "\n".join(textwrap.wrap(texto, 16)), ha="center", va="center", fontsize=11, color=TINTA, fontweight="bold")


def diagrama_de_influencia(nombres: dict, con_informacion: bool) -> None:
    """El diagrama de influencia: rectángulos para las decisiones, óvalos para el azar y rombos para las utilidades."""
    if con_informacion:
        fig, ax = plt.subplots(figsize=(10.5, 5.2))
        pos = {"informacion": (1.4, 3.5), "precio": (1.4, 5.0), "estado": (7.8, 3.5), "resultado": (4.6, 2.25),
               "decision": (1.4, 1.0), "utilidad": (7.8, 1.0)}
        arcos = [("informacion", "resultado"), ("estado", "resultado"), ("informacion", "decision"),
                 ("resultado", "decision"), ("decision", "utilidad"), ("estado", "utilidad"), ("informacion", "precio")]
    else:
        fig, ax = plt.subplots(figsize=(10.5, 3.4))
        pos = {"estado": (7.8, 2.6), "decision": (1.4, 1.0), "utilidad": (7.8, 1.0)}
        arcos = [("decision", "utilidad"), ("estado", "utilidad")]
    def borde(nodo, ux, uy):
        """El borde de cada forma en la dirección (ux, uy): rectángulo, óvalo o rombo."""
        if nodo in ("informacion", "decision"):
            escala = 1 / max(abs(ux) / 1.25, abs(uy) / 0.45)
        elif nodo in ("utilidad", "precio"):
            escala = 1 / (abs(ux) / 1.45 + abs(uy) / 0.575)
        else:
            return _borde_elipse(ux, uy, 1.25, 0.475)
        return ux * escala, uy * escala
    for de, a in arcos:
        (x0, y0), (x1, y1) = pos[de], pos[a]
        largo = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        ux, uy = (x1 - x0) / largo, (y1 - y0) / largo
        ox, oy = borde(de, ux, uy)
        ix, iy = borde(a, ux, uy)
        _flecha(ax, (x0 + ox, y0 + oy), (x1 - ix * 1.06, y1 - iy * 1.06))
    for clave, (x, y) in pos.items():
        texto = nombres[clave]
        if clave in ("informacion", "decision"):
            _rectangulo(ax, x, y, texto)
        elif clave in ("utilidad", "precio"):
            _rombo(ax, x, y, texto)
        else:
            _ovalo(ax, x, y, texto)
    # La leyenda de las formas
    leyenda = "rectángulo: decisión\nóvalo: azar\nrombo: utilidad"
    if con_informacion:
        leyenda += "\n\nflecha hacia una decisión:\nlo que sabes al decidir"
    ax.text(9.6, (5.3 if con_informacion else 3.0), leyenda, ha="left",
            va="top", fontsize=11, color=GRIS, bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#d0d7de"))
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0.3, 5.6 if con_informacion else 3.3)
    ax.set_aspect("equal")
    ax.axis("off")
    _mostrar(fig)


# ----------------------------------------------------------------------------- 7.2. la confiabilidad de la prueba

def curva_de_confiabilidad(malla, curva, niveles, valores, precio: float, vip: float) -> None:
    """El valor de la información según qué tanto informa la prueba. Muestra su precio y el tope: la información perfecta."""
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    ax.plot(malla, curva, color=AZUL, lw=2.4, label="valor de la prueba")
    ax.scatter(niveles, valores, color=AZUL, zorder=3, s=40)
    ax.axhline(precio, color=AMBAR, lw=2, ls="--", label=f"precio de la prueba: {_n(precio, 2)}")
    ax.axhline(vip, color=GRIS, lw=1.6, ls=":", label=f"información perfecta: {_n(vip, 2)}")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, max(vip, precio) * 1.12 + 0.01)
    ax.set_xlabel("confiabilidad de la prueba (0 = no informa nada; 1 = la prueba original)")
    ax.set_ylabel("valor de la información")
    ax.legend(loc="center left", bbox_to_anchor=(0.01, 0.6), fontsize=10.5, frameon=False)
    _mostrar(fig)
