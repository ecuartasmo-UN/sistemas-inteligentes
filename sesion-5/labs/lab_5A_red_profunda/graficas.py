"""Gráficas y tablas del Laboratorio 5A: los datos, el código de la red, las curvas de aprendizaje y la matriz de confusión.

Las curvas usan los colores de las diapositivas 10 y 11 de la charla inicial, oscurecidos para el fondo blanco:
cian para el entrenamiento, ámbar para la validación y verde para la parada temprana y el dropout.
Las tablas son HTML con sus propios colores, para que se lean igual con el tema claro y con el oscuro de VS Code.
"""
from __future__ import annotations

import html
import io

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import HTML, Image, display

import presentacion as p

CIAN, AMBAR, VERDE, GRIS = "#0284c7", "#d97706", "#16a34a", "#6b7280"
OTROS = ["#7c3aed", "#0284c7", "#d97706", "#16a34a", "#db2777", "#0f766e"]
_FUENTE = 'font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:14px;line-height:1.45;'
_MONO = "font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;"
matplotlib.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})


def _e(texto) -> str:
    return html.escape(str(texto))


def _n(valor, decimales: int = 0) -> str:
    return f"{valor:,.{decimales}f}".replace(",", " ").replace(".", ",")


def _mostrar(fig) -> None:
    """Muestra la figura como PNG sobre fondo blanco."""
    fig.patch.set_facecolor("white")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    display(Image(data=buf.getvalue(), format="png"))


def _ejes(ax, xlabel="época de entrenamiento", ylabel="pérdida (error)") -> None:
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color="#e5e7eb")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: _n(v, 2)))


def _rotulo(ax, x, y, texto, color, abajo: bool = False, alto: int = 6) -> None:
    ax.annotate(texto, (x, y), xytext=(-4, -16 if abajo else alto), textcoords="offset points", ha="right", color=color,
                fontweight="bold")


def _tasa(tasa) -> str:
    """La tasa como se escribe en el código: 0.00001, no 1e-05."""
    import numpy as np
    return np.format_float_positional(tasa, trim="-")


# ------------------------------------------------------------------ los datos y la red

def primeras_filas(filas, lecturas) -> None:
    """Las primeras filas del conjunto y las dos primeras fallas, con los nombres de las columnas en español."""
    nombres = ["temperatura del aire [K]", "temperatura del proceso [K]", "velocidad de giro [rpm]", "torque [Nm]",
               "desgaste de la herramienta [min]"]
    elegidas = list(range(5)) + [i for i, f in enumerate(filas) if f["Machine failure"] == "1"][:2]
    tabla = []
    for i in elegidas:
        f = filas[i]
        fila = {"registro": i + 1, "tipo": f["Type"]}
        fila.update({n: f[c].replace(".", ",") for n, c in zip(nombres, lecturas)})
        fila["¿falló?"] = "sí" if f["Machine failure"] == "1" else "no"
        tabla.append(fila)
    p.mostrar_tabla(tabla, titulo="Cinco registros del AI4I 2020 y las dos primeras fallas")


def codigo_red(capas, dropout, parametros) -> None:
    """La red en PyTorch, como lista de capas, con su tamaño."""
    lineas, entradas = ["red = nn.Sequential("], 8
    for i, n in enumerate(capas, 1):
        lineas.append(f"    nn.Linear({entradas}, {n}), nn.ReLU(), nn.Dropout({dropout:g}),   # capa oculta {i}")
        entradas = n
    lineas += [f"    nn.Linear({entradas}, 1),{' ' * 37}# salida: ¿falla?", ")",
               "perdida = nn.BCEWithLogitsLoss()   # la entropía cruzada; incluye la sigmoide, que da la probabilidad"]
    forma = " → ".join(["8 entradas"] + [str(n) for n in capas] + ["1 salida"])
    display(HTML(f"<div style='{_FUENTE}font-weight:700;margin:8px 0 4px'>La red en PyTorch · {_e(forma)} · "
                 f"{_n(parametros)} parámetros</div><pre style='{_MONO}background:#f6f8fa;color:#1f2328;border:1px solid "
                 f"#d0d7de;border-radius:8px;padding:10px 12px;white-space:pre;overflow-x:auto;margin:0 0 8px'>"
                 f"{_e(chr(10).join(lineas))}</pre>"))


# ------------------------------------------------------------------ curvas de aprendizaje

def curvas(r, titulo: str) -> None:
    """Pérdida de entrenamiento y de validación por época, con la época de menor pérdida de validación."""
    fig, ax = plt.subplots(figsize=(9, 4))
    epocas = range(1, len(r.perdida_validacion) + 1)
    ax.plot(epocas, r.perdida_entrenamiento, color=CIAN, lw=2.5)
    ax.plot(epocas, r.perdida_validacion, color=AMBAR, lw=2.5)
    tope = max(max(r.perdida_validacion[:3] + r.perdida_entrenamiento[:3]), max(r.perdida_validacion)) * 1.1
    ax.set_ylim(0, min(tope, 1.0))
    # Si las dos curvas terminan juntas, el rótulo de la más baja va debajo de ella, salvo que quede pegado al eje
    validacion_abajo = r.perdida_validacion[-1] < r.perdida_entrenamiento[-1]
    juntas = abs(r.perdida_validacion[-1] - r.perdida_entrenamiento[-1]) < 0.06 * ax.get_ylim()[1]
    cerca_del_eje = min(r.perdida_validacion[-1], r.perdida_entrenamiento[-1]) < 0.08 * ax.get_ylim()[1]
    # Pegadas al eje no hay espacio debajo: el rótulo de la curva más alta sube un poco más
    subir = 22 if juntas and cerca_del_eje else 6
    _rotulo(ax, len(epocas), r.perdida_entrenamiento[-1], "entrenamiento", CIAN,
            abajo=juntas and not validacion_abajo and not cerca_del_eje, alto=subir if validacion_abajo else 6)
    _rotulo(ax, len(epocas), r.perdida_validacion[-1], "validación", AMBAR,
            abajo=juntas and validacion_abajo and not cerca_del_eje, alto=6 if validacion_abajo else subir)
    if r.mejor_epoca and r.mejor_epoca < len(epocas):
        ax.axvline(r.mejor_epoca, color=VERDE, ls="--", lw=1.8)
        ax.text(r.mejor_epoca, ax.get_ylim()[1] * 0.95, f"  mínimo de validación: época {r.mejor_epoca}",
                color=VERDE, fontweight="bold", va="top")
    ax.set_title(titulo, loc="left", fontsize=13)
    _ejes(ax)
    _mostrar(fig)


def curvas_tasas(resultados, perdida_constante: float) -> None:
    """La pérdida de validación después de cada paso, para cada tasa de aprendizaje."""
    fig, ax = plt.subplots(figsize=(9, 4.4))
    tope = 1.0
    for i, r in enumerate(resultados):
        color = OTROS[i % len(OTROS)]
        x = [(k + 1) / r.pasos_por_epoca for k in range(len(r.pasos_validacion))]
        y = [min(v, tope) for v in r.pasos_validacion]
        ax.plot(x, y, color=color, lw=2, label=f"tasa {_tasa(r.tasa)}")
        maximo = max(r.pasos_validacion)
        if maximo > tope:
            k = r.pasos_validacion.index(maximo)
            ax.annotate(f"subió hasta {_n(maximo, 0 if maximo >= 10 else 1)}", (x[k], tope), xytext=(12, -14),
                        textcoords="offset points", color=color, fontweight="bold")
    ax.axhline(perdida_constante, color=GRIS, ls=":", lw=1.5)
    ax.text(ax.get_xlim()[1], perdida_constante, "responder siempre «no falla»  ", color=GRIS, ha="right", va="bottom")
    ax.set_ylim(0, tope * 1.02)
    ax.legend(loc="upper right", frameon=False)
    ax.set_title("La pérdida de validación después de cada paso (los valores mayores que 1 se cortan arriba)", loc="left",
                 fontsize=12)
    _ejes(ax)
    _mostrar(fig)


def curvas_frenos(base, con_dropout, paradas) -> None:
    """Como la diapositiva 11: validación sin frenos (punteada) y con dropout, y dónde para cada paciencia."""
    fig, ax = plt.subplots(figsize=(9, 4.4))
    e = range(1, len(base.perdida_validacion) + 1)
    ax.plot(e, base.perdida_entrenamiento, color=CIAN, lw=1.2, alpha=0.6)
    ax.plot(e, base.perdida_validacion, color=AMBAR, lw=2.5, ls="--")
    _rotulo(ax, len(e), base.perdida_validacion[-1], f"validación sin frenos · {_n(base.perdida_validacion[-1], 2)}", AMBAR)
    _rotulo(ax, len(e), base.perdida_entrenamiento[-1], "entrenamiento sin frenos", CIAN)
    tope = max(base.perdida_validacion) * 1.15
    if con_dropout is not None:
        d = range(1, len(con_dropout.perdida_validacion) + 1)
        ax.plot(d, con_dropout.perdida_validacion, color=VERDE, lw=2.5)
        _rotulo(ax, len(d), con_dropout.perdida_validacion[-1],
                f"validación con dropout {con_dropout.dropout:g} · {_n(con_dropout.perdida_validacion[-1], 2)}",
                VERDE)
        tope = max(tope, max(con_dropout.perdida_validacion) * 1.15)
    for r in paradas:
        # Una línea vertical donde se detiene, con su paciencia, y un punto en la época de la red que se guarda
        parada = len(r.perdida_validacion)
        ax.axvline(parada, color="#475569", ls=":", lw=1.6)
        ax.text(parada - 2, tope * 0.97, f"paciencia {r.paciencia}: para en la época {parada}", rotation=90, va="top",
                ha="right", color="#334155", fontsize=10)
        ax.plot([r.epoca_guardada], [r.perdida_guardada], "o", color="#475569", ms=7)
        ax.annotate(f"se queda con la {r.epoca_guardada}", (r.epoca_guardada, r.perdida_guardada), xytext=(0, -18),
                    textcoords="offset points", ha="center", color="#334155", fontsize=10)
    ax.set_ylim(0, tope)
    ax.set_title("Los frenos contra la memoria", loc="left", fontsize=13)
    _ejes(ax)
    _mostrar(fig)


def curvas_redes(resultados) -> None:
    """La pérdida de validación de cada red de la sección 6."""
    fig, ax = plt.subplots(figsize=(9, 4))
    for i, r in enumerate(resultados):
        e = range(1, len(r.perdida_validacion) + 1)
        ax.plot(e, r.perdida_validacion, color=OTROS[i % len(OTROS)], lw=2, label=str(list(r.capas)))
    ax.set_ylim(0, min(0.3, max(max(r.perdida_validacion[2:] or r.perdida_validacion) for r in resultados) * 1.1))
    ax.legend(title="red", frameon=False, loc="upper right")
    ax.set_title("Pérdida de validación de cada red", loc="left", fontsize=13)
    _ejes(ax)
    _mostrar(fig)


# ------------------------------------------------------------------ matriz de confusión

def matriz_fallas(vp, fn, fp, vn, titulo: str) -> None:
    """La matriz de confusión de dos clases, con el nombre de cada casilla."""
    th = f"style='{_FUENTE}padding:8px 12px;background:#eef1f4;color:#1f2328;border:1px solid #d0d7de;text-align:center'"

    def celda(n, texto, fondo, color):
        return (f"<td style='{_FUENTE}padding:8px 16px;text-align:center;border:1px solid #d0d7de;background:{fondo};"
                f"color:{color}'><b style='font-size:18px'>{_n(n)}</b><br>{_e(texto)}</td>")
    filas = (f"<tr><th {th}>real ↓ · la red dice →</th><th {th}>falla</th><th {th}>no falla</th></tr>"
             f"<tr><th {th}>falló</th>{celda(vp, 'fallas detectadas', '#dcfce7', '#14532d')}"
             f"{celda(fn, 'fallas que no vio', '#fee2e2' if fn else '#ffffff', '#7f1d1d')}</tr>"
             f"<tr><th {th}>no falló</th>{celda(fp, 'falsas alarmas', '#ffedd5' if fp else '#ffffff', '#7c2d12')}"
             f"{celda(vn, 'bien descartadas', '#f0fdf4', '#14532d')}</tr>")
    display(HTML(f"<div style='{_FUENTE}font-weight:700;margin:8px 0 4px'>{_e(titulo)}</div>"
                 f"<div style='overflow-x:auto'><table style='border-collapse:collapse;background:#ffffff'>{filas}</table></div>"))
