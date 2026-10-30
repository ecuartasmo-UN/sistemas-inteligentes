"""Gráficas del Laboratorio 6B: el mundo de 4×3, sus valores y políticas, las curvas del agente y la pista del bote.

Usan los colores de las diapositivas de la charla intermedia, oscurecidos para el fondo blanco: verde para la salida +1,
rojo para la −1, azul para las flechas de la política y ámbar para lo que se resalta.
"""
from __future__ import annotations

import io
import textwrap

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import Image, display
from matplotlib.patches import FancyArrowPatch, Rectangle

AZUL, AMBAR, VERDE, ROJO, GRIS = "#0284c7", "#d97706", "#16a34a", "#dc2626", "#6b7280"
OTROS = ["#d97706", "#7c3aed", "#db2777", "#0f766e", "#64748b"]   # sin verde: el verde es la referencia
matplotlib.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})
_MURO = (2, 2)
_SALIDAS = {(4, 3): 1.0, (4, 2): -1.0}


def _n(valor, decimales: int = 0) -> str:
    return f"{valor:,.{decimales}f}".replace(",", " ").replace(".", ",")


def _mostrar(fig) -> None:
    fig.patch.set_facecolor("white")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    display(Image(data=buf.getvalue(), format="png"))


def _cuadricula(ax, valores=None, politica=None, resaltar=(), titulo="", texto_valor=11, texto_flecha=22,
                inicio=False) -> None:
    """Una cuadrícula de 4×3: el muro, las salidas, los valores y una flecha por casilla."""
    for f in (1, 2, 3):
        for c in (1, 2, 3, 4):
            x, y = c - 1, f - 1
            if (c, f) == _MURO:
                ax.add_patch(Rectangle((x, y), 1, 1, fc="#cbd5e1", ec="#94a3b8"))
                ax.text(x + 0.5, y + 0.5, "muro", ha="center", va="center", fontsize=9, color="#475569")
                continue
            if (c, f) in _SALIDAS:
                bueno = _SALIDAS[(c, f)] > 0
                ax.add_patch(Rectangle((x, y), 1, 1, fc="#dcfce7" if bueno else "#fee2e2", ec="#94a3b8"))
                ax.text(x + 0.5, y + 0.5, "+1" if bueno else "−1", ha="center", va="center", fontsize=texto_flecha - 4,
                        fontweight="bold", color=VERDE if bueno else ROJO)
                continue
            fondo = "#fde9c4" if (c, f) in resaltar else "white"
            ax.add_patch(Rectangle((x, y), 1, 1, fc=fondo, ec="#94a3b8"))
            if politica is not None:
                ax.text(x + 0.5, y + (0.58 if valores is not None else 0.5), politica[(c, f)], ha="center", va="center",
                        fontsize=texto_flecha, color=AZUL)
            if valores is not None:
                ax.text(x + 0.5, y + 0.2, _n(valores[(c, f)], 3), ha="center", va="center", fontsize=texto_valor, color="#1f2328")
            if inicio and (c, f) == (1, 1):
                ax.text(x + 0.5, y + 0.12, "inicio", ha="center", va="center", fontsize=9, color=GRIS)
    ax.set_xlim(-0.05, 4.05)
    ax.set_ylim(-0.05, 3.05)
    ax.set_aspect("equal")
    ax.axis("off")
    if titulo:
        ax.set_title("\n".join(textwrap.wrap(titulo, 30)), fontsize=11, loc="left")


def mundo() -> None:
    """El mundo de 4×3 con el robot en el inicio, y el movimiento incierto."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.5, 3.6), gridspec_kw={"width_ratios": [1.35, 1]})
    _cuadricula(a, titulo="El mundo de 4×3")
    a.add_patch(plt.Circle((0.5, 0.5), 0.2, color=AZUL))
    a.text(0.5, 0.12, "inicio", ha="center", va="center", fontsize=9, color=GRIS)
    b.add_patch(plt.Circle((0, 0), 0.18, color=AZUL))
    for (dx, dy), texto, ancho in (((0, 1), "0,8", 3), ((-1, 0), "0,1", 1.6), ((1, 0), "0,1", 1.6)):
        b.add_patch(FancyArrowPatch((0.22 * dx, 0.22 * dy), (0.95 * dx, 0.95 * dy), arrowstyle="-|>", mutation_scale=20,
                                    color=AMBAR, lw=ancho))
        b.text(1.15 * dx + (0.18 if dy else 0), 1.12 * dy + (0.12 if dx else 0), texto, ha="center", va="center",
               fontsize=13, color="#b45309", fontweight="bold")
    b.text(0, -0.5, "quiere subir: sube con 0,8 y se\ndesvía a cada lado con 0,1", ha="center", va="center", fontsize=11,
           color="#334155")
    b.set_xlim(-1.5, 1.5)
    b.set_ylim(-0.8, 1.4)
    b.set_aspect("equal")
    b.axis("off")
    b.set_title("El movimiento incierto", fontsize=11, loc="left")
    _mostrar(fig)


def iteraciones(historia: dict) -> None:
    """Los valores de cada casilla en algunas iteraciones: se propagan desde la salida +1."""
    claves = sorted(historia)
    fig, ejes = plt.subplots(1, len(claves), figsize=(2.55 * len(claves), 2.5))
    for ax, k in zip(ejes, claves):
        _cuadricula(ax, historia[k], None, titulo=f"iteración {k}", texto_valor=8.5, texto_flecha=14)
    _mostrar(fig)


def politicas(cuadros: list) -> None:
    """Varias cuadrículas lado a lado: (título, valores o None, política, casillas para resaltar)."""
    fig, ejes = plt.subplots(1, len(cuadros), figsize=(3.7 * len(cuadros), 3.0), squeeze=False)
    for ax, (titulo, valores, politica, resaltar) in zip(ejes[0], cuadros):
        _cuadricula(ax, valores, politica, resaltar, titulo, texto_flecha=20 if valores is None else 18)
    _mostrar(fig)


def curvas(series: dict, referencia: float) -> None:
    """El retorno medio de cada 100 episodios, con la línea de lo que promete la iteración de valores."""
    fig, ax = plt.subplots(figsize=(9.5, 4.0))
    for k, (nombre, puntos) in enumerate(series.items()):
        ax.plot([e for e, _ in puntos], [v for _, v in puntos], lw=2.4, color=OTROS[k % len(OTROS)], label=nombre)
    ax.axhline(referencia, color=VERDE, ls="--", lw=1.6)
    ax.annotate(f"lo que promete la iteración de valores desde el inicio: {_n(referencia, 3)}", (0.01, referencia),
                xycoords=("axes fraction", "data"), xytext=(0, 6), textcoords="offset points", color=VERDE, fontsize=10,
                fontweight="bold")
    ax.set_xlabel("episodios de práctica")
    ax.set_ylabel("retorno medio de 100 episodios")
    ax.grid(axis="y", color="#e5e7eb")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: _n(v, 2)))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False, fontsize=10)   # debajo: no tapa
    _mostrar(fig)


def pista(casillas: list, elegir, titulo: str) -> None:
    """La pista del bote: las flechas del juego, la acción del agente en cada casilla y cuántas veces pasó por ella."""
    pista_txt = ["#####", "#A> #", "#^#v#", "# < #", "#####"]
    simbolos = {">": "→", "v": "↓", "<": "←", "^": "↑"}
    visitas = {}
    for c in casillas[1:]:
        visitas[c] = visitas.get(c, 0) + 1
    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    for f in range(5):
        for c in range(5):
            x, y = c, 4 - f
            ch = pista_txt[f][c]
            if ch == "#":
                ax.add_patch(Rectangle((x, y), 1, 1, fc="#94a3b8", ec="#64748b"))
                continue
            vez = visitas.get((f, c), 0)
            fondo = "#dcfce7" if vez else "white"
            ax.add_patch(Rectangle((x, y), 1, 1, fc=fondo, ec="#64748b"))
            if ch in simbolos:
                ax.text(x + 0.18, y + 0.78, simbolos[ch], ha="center", va="center", fontsize=15, color=AMBAR, fontweight="bold")
            if ch == "A":
                ax.text(x + 0.18, y + 0.8, "inicio", ha="left", va="center", fontsize=8, color=GRIS)
            ax.text(x + 0.55, y + 0.5, elegir((f, c)), ha="center", va="center", fontsize=24, color=AZUL)
            if vez:
                ax.text(x + 0.82, y + 0.14, f"{vez}×", ha="center", va="center", fontsize=9, color=VERDE, fontweight="bold")
    ax.text(0.05, -0.35, "ámbar: flechas de la pista (pagan +3 al entrar en su sentido) · azul: la acción del agente",
            fontsize=9, color="#334155", transform=ax.transData)
    ax.set_xlim(-0.05, 5.05)
    ax.set_ylim(-0.55, 5.05)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titulo, fontsize=10.5, loc="left", wrap=True)
    _mostrar(fig)
