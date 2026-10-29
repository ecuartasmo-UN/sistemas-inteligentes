"""Gráficas y tablas del Laboratorio 5B: las órdenes, la matriz de confusión, los errores, los aciertos según la
cantidad de ejemplos y la tabla de las órdenes trampa.

Las tablas son HTML con sus propios colores, para que se lean igual con el tema claro y con el oscuro de VS Code.
"""
from __future__ import annotations

import html
import io
import re

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import HTML, Image, display

import presentacion as p

SIN_RESPUESTA = "sin respuesta válida"
COLORES = {"bolsa de palabras": "#64748b", "red recurrente (LSTM)": "#7c3aed", "transformer preentrenado": "#0284c7"}
_FUENTE = 'font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:14px;line-height:1.45;'
matplotlib.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})


def _e(texto) -> str:
    return html.escape(str(texto))


def _mostrar(fig) -> None:
    """Muestra la figura como PNG sobre fondo blanco."""
    fig.patch.set_facecolor("white")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    display(Image(data=buf.getvalue(), format="png"))


# ------------------------------------------------------------------ los textos

def muestra(c, por_clase: int = 2) -> None:
    """Algunos textos de entrenamiento de cada clase y cuántos hay en cada conjunto."""
    filas = [{c.palabra_clase: k, "texto": t} for k in c.clases for t in c.entrenamiento[k][:por_clase]]
    p.mostrar_tabla(filas, titulo=f"{por_clase} ejemplos de cada {c.palabra_clase} · {c.nombre}")
    cuentas = [{c.palabra_clase: k, "entrenamiento": len(c.entrenamiento[k]),
                "prueba": sum(1 for _, x in c.prueba if x == k),
                **({"trampa y control": sum(1 for _, x in c.trampa if x == k)} if c.trampa else {})} for k in c.clases]
    p.mostrar_tabla(cuentas, titulo="Cuántos hay en cada conjunto")


# ------------------------------------------------------------------ matriz de confusión y errores

def matriz(c, titulo: str) -> None:
    """La matriz de confusión como tabla coloreada: filas, la clase real; columnas, la asignada."""
    columnas = list(c.clases) + ([SIN_RESPUESTA] if any(a is None for a in c.asignadas) else [])
    th = (f"style='{_FUENTE}padding:6px 10px;background:#eef1f4;color:#1f2328;border:1px solid #d0d7de;"
          "text-align:center'")
    filas = []
    for real in c.clases:
        indices = [i for i, r in enumerate(c.reales) if r == real]
        celdas = []
        for col in columnas:
            asignada = None if col == SIN_RESPUESTA else col
            n = sum(1 for i in indices if c.asignadas[i] == asignada)
            fraccion = n / len(indices) if indices else 0
            if n == 0:
                fondo, color = "#ffffff", "#8c959f"
            elif col == real:
                fondo, color = f"rgba(34,139,34,{0.15 + 0.6 * fraccion:.2f})", "#0b3d0b"
            else:
                fondo, color = f"rgba(219,38,38,{0.12 + 0.55 * fraccion:.2f})", "#5c0b0b"
            celdas.append(f"<td style='{_FUENTE}padding:6px 12px;text-align:center;border:1px solid #d0d7de;"
                          f"background:{fondo};color:{color};font-weight:{700 if n else 400}'>{n}</td>")
        aciertos = sum(1 for i in indices if c.asignadas[i] == real)
        filas.append(f"<tr><th {th}>{_e(real)}</th>{''.join(celdas)}<td style='{_FUENTE}padding:6px 12px;"
                     f"text-align:center;border:1px solid #d0d7de;background:#f6f8fa;color:#1f2328'>"
                     f"{aciertos} de {len(indices)}</td></tr>")
    cabeza = (f"<tr><th {th}>real ↓ · asignado →</th>" + "".join(f"<th {th}>{_e(k)}</th>" for k in columnas)
              + f"<th {th}>aciertos</th></tr>")
    total = sum(1 for r, a in zip(c.reales, c.asignadas) if r == a)
    pie = (f"<div style='{_FUENTE}margin-top:6px;color:#1f2328;background:#f6f8fa;border:1px solid #d0d7de;"
           f"border-radius:6px;padding:6px 10px;display:inline-block'>Aciertos: <b>{total} de {len(c.reales)}"
           f" ({round(100 * total / max(1, len(c.reales)))} %)</b>. Al azar, con {len(c.clases)} clases iguales, se "
           f"esperaría cerca de {round(100 / len(c.clases))} %.</div>")
    display(HTML(f"<div style='{_FUENTE}font-weight:700;margin:8px 0 4px;color:inherit'>{_e(titulo)}</div>"
                 f"<div style='overflow-x:auto'><table style='border-collapse:collapse;background:#ffffff'>{cabeza}"
                 f"{''.join(filas)}</table></div>{pie}"))


def errores(c, respuestas: dict | None = None, maximo: int = 12, conocidas: set | None = None, normalizar=None) -> None:
    """Los textos mal clasificados, con su clase real y la asignada.

    conocidas: las palabras de los ejemplos; si se da, una columna dice cuáles del texto vio la arquitectura."""
    malos = [(t, r, a) for t, r, a in zip(c.textos, c.reales, c.asignadas) if r != a]
    if not malos:
        p.nota("No hubo errores en los textos de prueba.", "exito")
        return
    filas = []
    for t, r, a in malos[:maximo]:
        fila = {"texto": t, "real": r, "asignado": a or SIN_RESPUESTA}
        if conocidas is not None:
            vistas = (w for w in re.findall(r"\w+", t.lower()) if normalizar(w) in conocidas)   # con sus tildes
            fila["palabras que vio en los ejemplos"] = ", ".join(dict.fromkeys(vistas)) or "ninguna"
        if respuestas is not None:
            fila["respuesta del LLM"] = respuestas.get(t, "")
        filas.append(fila)
    resto = f" (se muestran {maximo})" if len(malos) > maximo else ""
    p.mostrar_tabla(filas, titulo=f"Los {len(malos)} errores{resto}")


# ------------------------------------------------------------------ cuántos ejemplos

def curva_cantidades(resultados, conjunto, llm_resultado=None) -> None:
    """El porcentaje de aciertos en la prueba de cada arquitectura, según los ejemplos por clase."""
    fig, ax = plt.subplots(figsize=(9, 4.4))
    for nombre, color in COLORES.items():
        puntos = sorted((r.ejemplos, 100 * r.aciertos() / r.total()) for r in resultados if r.metodo == nombre)
        if puntos:
            ax.plot(*zip(*puntos), "o-", color=color, lw=2.5, ms=7, label=nombre)
            for r in resultados:            # el conteo junto a cada punto; si otro punto queda muy cerca y arriba, va debajo
                if r.metodo == nombre:
                    y = 100 * r.aciertos() / r.total()
                    debajo = any(o.ejemplos == r.ejemplos and o.metodo != nombre and 0 < 100 * o.aciertos() / o.total() - y < 6
                                 for o in resultados)
                    ax.annotate(f"{r.aciertos()}/{r.total()}", (r.ejemplos, y), xytext=(0, -16 if debajo else 8),
                                textcoords="offset points", ha="center", fontsize=10, color=color)
    azar = 100 / len(conjunto.clases)
    ax.axhline(azar, color="#9ca3af", ls=":", lw=1.5)
    ax.text(ax.get_xlim()[1], azar, "al azar  ", ha="right", va="bottom", color="#6b7280")
    if llm_resultado is not None:
        valor = 100 * llm_resultado.aciertos() / llm_resultado.total()
        ax.axhline(valor, color="#d97706", ls="--", lw=2)
        ax.text(ax.get_xlim()[0], valor, "  LLM, sin ejemplos", va="bottom", color="#d97706", fontweight="bold")
    cantidades = sorted({r.ejemplos for r in resultados})
    ax.set_xticks(cantidades)
    ax.set_ylim(0, 118)
    ax.set_yticks(range(0, 101, 20))
    ax.set_xlabel(f"ejemplos etiquetados por {conjunto.palabra_clase}")
    ax.set_ylabel("aciertos en la prueba (%)")
    ax.grid(axis="y", color="#e5e7eb")
    ax.legend(frameon=False, loc="upper left", ncol=3, fontsize=11)
    ax.set_title(f"¿Cuántos ejemplos necesita cada arquitectura? · {len(conjunto.prueba)} "
                 f"{'textos' if conjunto.propio else 'órdenes'} de prueba", loc="left", fontsize=13)
    _mostrar(fig)


# ------------------------------------------------------------------ trampas y órdenes propias

def tabla_pruebas(filas, respuestas: dict, nombres, titulo: str, columna: str = "orden") -> None:
    """Cada orden trampa o propia, con lo que respondió cada arquitectura: verde si acierta, rojo si no."""
    if not filas:
        p.nota("No hay órdenes trampa ni órdenes suyas para poner a prueba.", "info")
        return
    th = f"style='{_FUENTE}padding:6px 10px;background:#eef1f4;color:#1f2328;border:1px solid #d0d7de;text-align:left'"
    td = f"{_FUENTE}padding:5px 10px;border:1px solid #d0d7de;vertical-align:top;"
    cuerpo = []
    aciertos = {k: 0 for k in respuestas}
    for i, (texto, esperado, tipo) in enumerate(filas):
        celdas = (f"<td style='{td}color:#1f2328;background:#ffffff'>{_e(texto)}</td>"
                  f"<td style='{td}color:#57606a;background:#ffffff'>{_e(tipo)}</td>"
                  f"<td style='{td}color:#1f2328;background:#f6f8fa;font-weight:700'>{_e(esperado)}</td>")
        for k, asignadas in respuestas.items():
            bien = asignadas[i] == esperado
            aciertos[k] += bien
            fondo, color, marca = ("#dcfce7", "#14532d", "✓") if bien else ("#fee2e2", "#7f1d1d", "✗")
            celdas += f"<td style='{td}background:{fondo};color:{color}'>{marca} {_e(asignadas[i])}</td>"
        cuerpo.append(f"<tr>{celdas}</tr>")
    pie = "".join(f"<td style='{td}background:#f6f8fa;color:#1f2328;font-weight:700'>{aciertos[k]} de {len(filas)}</td>"
                  for k in respuestas)
    cuerpo.append(f"<tr><td style='{td}background:#f6f8fa;color:#1f2328;font-weight:700' colspan='3'>aciertos</td>{pie}</tr>")
    cabeza = (f"<tr><th {th}>{_e(columna)}</th><th {th}>tipo</th><th {th}>esperado</th>"
              + "".join(f"<th {th}>{_e(n)}</th>" for n in nombres) + "</tr>")
    display(HTML(f"<div style='{_FUENTE}font-weight:700;margin:8px 0 4px'>{_e(titulo)}</div>"
                 f"<div style='overflow-x:auto'><table style='border-collapse:collapse;background:#ffffff'>{cabeza}"
                 f"{''.join(cuerpo)}</table></div>"))
