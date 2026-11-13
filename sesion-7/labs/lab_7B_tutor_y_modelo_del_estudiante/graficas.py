"""Gráficas del Laboratorio 7B: las curvas de dominio, las reglas de selección y el costo de la certeza.

Usan los colores de las diapositivas, oscurecidos para el fondo blanco. Las respuestas se marcan con ✓ en verde y ✗ en rojo.
"""
from __future__ import annotations

import io
import textwrap

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import Image, display

AZUL, AMBAR, VERDE, ROJO, GRIS, TINTA = "#0284c7", "#d97706", "#16a34a", "#dc2626", "#6b7280", "#1f2328"
SERIES = [AZUL, AMBAR, "#7c3aed", "#0f766e", "#db2777", "#64748b"]
matplotlib.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})


def _n(valor: float, decimales: int = 2) -> str:
    texto = f"{valor:,.{decimales}f}".replace(",", " ")
    return texto.rstrip("0").rstrip(".") if "." in texto else texto


def _mostrar(fig) -> None:
    fig.patch.set_facecolor("white")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    display(Image(data=buf.getvalue(), format="png"))


def curvas_de_dominio(curvas: list, umbrales: list, titulo: str) -> None:
    """Una o varias curvas de dominio. Cada punto es el dominio estimado después de una respuesta, marcada con ✓ o ✗."""
    largo = max(len(resp) for _, resp, _ in curvas)
    fig, ax = plt.subplots(figsize=(9.5, 4.3))
    for k, (nombre, resp, valores) in enumerate(curvas):
        color = SERIES[k % len(SERIES)]
        ax.plot(range(len(valores)), valores, color=color, lw=2.4, marker="o", ms=5, label=nombre, zorder=3)
        if len(curvas) <= 2:
            # Las respuestas, arriba de cada paso: verde si acierta, rojo si falla
            fila = 1.06 + 0.07 * k
            for i, r in enumerate(resp, 1):
                ax.text(i, fila, "✓" if r else "✗", ha="center", va="center", fontsize=13, fontweight="bold",
                        color=VERDE if r else ROJO, clip_on=False)
            if len(curvas) == 2:
                ax.text(0.15, fila, nombre.split(":")[0], ha="left", va="center", fontsize=10, color=color, clip_on=False)
    previo = None
    for u in sorted(umbrales):
        ax.axhline(u, color=GRIS, lw=1.3, ls="--")
        # Si dos umbrales están cerca, la etiqueta del más alto sube un poco para no pisar la otra
        y = u if previo is None or u - previo >= 0.05 else previo + 0.05
        ax.text(largo + 0.15, y, f"umbral {_n(u, 3)}", va="center", fontsize=10, color=GRIS)
        previo = y
    ax.set_xlim(-0.2, largo + 0.2)
    ax.set_ylim(0, 1.0)
    ax.set_xticks(range(largo + 1))
    ax.set_xlabel("ejercicios respondidos")
    ax.set_ylabel("dominio estimado")
    ax.set_title("\n".join(textwrap.wrap(titulo, 80)), fontsize=12, loc="left",
                 pad=(28 + 16 * len(curvas)) if len(curvas) <= 2 else 8)
    if len(curvas) > 1:
        ax.legend(loc="lower right", fontsize=10, frameon=False)
    _mostrar(fig)


def reglas_de_seleccion(puntos: list) -> None:
    """Una barra por regla: qué parte de los técnicos domina al terminar, y cuántos ejercicios pide en promedio."""
    habilidades = list(dict.fromkeys(h for h, *_ in puntos))
    reglas = list(dict.fromkeys(r for _, r, *_ in puntos))
    fig, ejes = plt.subplots(1, len(habilidades), figsize=(4.1 * len(habilidades), 0.5 * len(reglas) + 1.6), sharey=True)
    y = list(range(len(reglas)))[::-1]
    for ax, habilidad in zip(ejes, habilidades):
        datos = {r: (e, d) for h, r, e, d in puntos if h == habilidad}
        for yi, regla in zip(y, reglas):
            ejercicios, dominan = datos[regla]
            gris = "seguidos" in regla
            ax.barh(yi, dominan * 100, color=GRIS if gris else (AZUL if "dominar" in regla else AMBAR), height=0.62)
            ax.text(2, yi, f"{dominan * 100:.1f} % · {_n(ejercicios, 2)} ej.", va="center", fontsize=9.5, color="white",
                    fontweight="bold")
        ax.set_title("\n".join(textwrap.wrap(habilidad, 26)), fontsize=11.5, loc="left")
        ax.set_xlim(0, 100)
        ax.set_xlabel("dominan al terminar (%)")
    ejes[0].set_yticks(y)
    ejes[0].set_yticklabels(reglas, fontsize=10)
    fig.suptitle("Dominan al terminar. Azul: hasta dominar. Ámbar: un número fijo de ejercicios. Gris: la referencia. "
                 "«ej.»: ejercicios en promedio.", x=0.01, y=1.06, ha="left", fontsize=9.5, color=GRIS)
    _mostrar(fig)


def costo_de_la_certeza(datos: list, habilidad: str) -> None:
    """El umbral contra los ejercicios que pide y contra los técnicos que dominan al terminar."""
    umbrales = [u for u, _, _ in datos]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.5, 3.8))
    a.plot(umbrales, [e for _, e, _ in datos], color=AZUL, lw=2.4, marker="o")
    a.set_xlabel("umbral de dominio")
    a.set_ylabel("ejercicios en promedio")
    a.set_title("Lo que cuesta", fontsize=12, loc="left")
    b.plot(umbrales, [d * 100 for _, _, d in datos], color=VERDE, lw=2.4, marker="o")
    b.set_xlabel("umbral de dominio")
    b.set_ylabel("dominan al terminar (%)")
    b.set_title("Lo que se gana", fontsize=12, loc="left")
    b.set_ylim(max(0, min(d * 100 for _, _, d in datos) - 10), 101)
    for ax in (a, b):
        ax.grid(alpha=0.25)
    fig.suptitle(habilidad, x=0.06, y=1.05, ha="left", fontsize=12.5)
    _mostrar(fig)


def contrapunto(filas: list) -> None:
    """El dominio estimado de cada técnico: BKT frente a las dos corridas del LLM."""
    fig, ax = plt.subplots(figsize=(9.5, 0.45 * len(filas) + 1.4))
    y = list(range(len(filas)))[::-1]
    for yi, f in zip(y, filas):
        ax.plot([0, 1], [yi, yi], color="#eef1f4", lw=6, zorder=1, solid_capstyle="round")
        if f["bkt"] is not None:
            ax.scatter(f["bkt"], yi, s=80, color=AZUL, zorder=3, label="BKT" if yi == y[0] else None)
        for k, (clave, marca) in enumerate((("llm1", "D"), ("llm2", "s"))):
            if f[clave] is not None:
                ax.scatter(f[clave], yi, s=55, marker=marca, color=AMBAR, edgecolor=TINTA if k else AMBAR, zorder=4,
                           label=(f"LLM, corrida {k + 1}") if yi == y[0] else None)
        ax.text(1.04, yi, "domina" if f["real"] else "no domina", va="center", fontsize=10.5,
                color=VERDE if f["real"] else ROJO, fontweight="bold")
    ax.axvline(0.95, color=GRIS, lw=1.3, ls="--")
    ax.set_yticks(y)
    ax.set_yticklabels([f["tecnico"] for f in filas])
    ax.set_xlim(0, 1)
    ax.set_xlabel("dominio estimado (la línea punteada es el umbral de 0.95)")
    ax.set_title("Lo que estima cada uno, y lo que pasaba de verdad (a la derecha)", fontsize=12, loc="left")
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.18), ncol=3, fontsize=10, frameon=False)
    _mostrar(fig)
