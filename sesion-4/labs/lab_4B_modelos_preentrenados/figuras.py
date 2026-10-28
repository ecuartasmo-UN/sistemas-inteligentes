"""Figuras del Laboratorio 4B: galerías, matrices de confusión, similitudes de CLIP y cajas de los detectores.

Las fotos se muestran como JPEG, para que el notebook entregado pese poco. Las tablas y las galerías con texto
son HTML con sus propios colores, para que se lean igual con el tema claro y con el oscuro de VS Code.
"""
from __future__ import annotations

import base64
import html
import io

import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML, Image, display
from matplotlib.patches import Rectangle

# Los mismos colores del 4A: azul, lo correcto; rojo, junta dos o más; naranja, sin cápsula; magenta, perdida
AZUL, ROJO, NARANJA, MAGENTA = "#1a66f2", "#db2626", "#f98c0d", "#d946ef"
_FUENTE = 'font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:14px;line-height:1.45;'
SIN_RESPUESTA = "sin respuesta válida"


def _e(texto) -> str:
    return html.escape(str(texto))


def _mostrar(fig) -> None:
    """Muestra la figura como JPEG sobre fondo blanco."""
    fig.patch.set_facecolor("white")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="jpeg", dpi=90, bbox_inches="tight", pad_inches=0.15, pil_kwargs={"quality": 82})
    plt.close(fig)
    display(Image(data=buf.getvalue(), format="jpeg"))


def _miniatura(imagen, lado: int = 150) -> str:
    """Una imagen de PIL como JPEG pequeño en base64, para las galerías en HTML."""
    copia = imagen.copy()
    copia.thumbnail((lado, lado))
    buf = io.BytesIO()
    copia.convert("RGB").save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode("ascii")


# ------------------------------------------------------------------ las imágenes del caso

def galeria(conjunto, maximo_por_clase: int = 8, titulo: str = "") -> None:
    """Una fila por clase, con sus imágenes."""
    clases = conjunto.clases
    columnas = max(1, min(maximo_por_clase, max(len(conjunto.de_clase(k)) for k in clases)))
    fig, ejes = plt.subplots(len(clases), columnas, figsize=(1.7 * columnas + 0.6, 1.8 * len(clases) + 0.4), squeeze=False)
    for i, k in enumerate(clases):
        imagenes = conjunto.de_clase(k)[:columnas]
        for j in range(columnas):
            ax = ejes[i][j]
            ax.set_xticks([])
            ax.set_yticks([])
            for borde in ax.spines.values():
                borde.set_visible(False)
            if j < len(imagenes):
                ax.imshow(imagenes[j].miniatura)
            if j == 0:
                ax.set_ylabel(f"{k}\n({len(conjunto.de_clase(k))})", fontsize=13, rotation=0, ha="right", va="center",
                              labelpad=14)
    if titulo:
        fig.suptitle(titulo, fontsize=13, x=0.01, ha="left")
    _mostrar(fig)


# ------------------------------------------------------------------ matriz de confusión

def matriz(clasificacion, titulo: str | None = None) -> None:
    """La matriz de confusión como tabla coloreada: filas, la clase real; columnas, la clase asignada."""
    c = clasificacion
    columnas = list(c.clases) + ([SIN_RESPUESTA] if any(a is None for a in c.asignadas) else [])
    th = (f"style='{_FUENTE}padding:6px 10px;background:#eef1f4;color:#1f2328;border:1px solid #d0d7de;"
          "text-align:center'")
    filas = []
    for real in c.clases:
        celdas = []
        indices = [i for i, r in enumerate(c.reales) if r == real]
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
        exactitud = f"{aciertos} de {len(indices)}" if indices else "—"
        filas.append(f"<tr><th {th}>{_e(real)}</th>{''.join(celdas)}"
                     f"<td style='{_FUENTE}padding:6px 12px;text-align:center;border:1px solid #d0d7de;background:#f6f8fa;"
                     f"color:#1f2328'>{exactitud}</td></tr>")
    cabeza = (f"<tr><th {th}>real ↓ · asignada →</th>" + "".join(f"<th {th}>{_e(k)}</th>" for k in columnas)
              + f"<th {th}>aciertos</th></tr>")
    total = (f"<div style='{_FUENTE}margin-top:6px;color:#1f2328;background:#f6f8fa;border:1px solid #d0d7de;"
             f"border-radius:6px;padding:6px 10px;display:inline-block'>Exactitud total: <b>{c.aciertos} de {len(c.reales)}"
             f" ({round(100 * c.exactitud)} %)</b>. Al azar, con {len(c.clases)} clases iguales, se esperaría cerca de "
             f"{round(100 / len(c.clases))} %.</div>")
    titulo = titulo or f"Matriz de confusión · {c.metodo} · {c.nombre}"
    display(HTML(f"<div style='{_FUENTE}font-weight:700;margin:8px 0 4px;color:inherit'>{_e(titulo)}</div>"
                 f"<div style='overflow-x:auto'><table style='border-collapse:collapse;background:#ffffff'>{cabeza}"
                 f"{''.join(filas)}</table></div>{total}"))


# ------------------------------------------------------------------ errores

def galeria_errores(clasificacion, maximo: int = 12) -> None:
    """Las imágenes mal clasificadas, con la clase real, la asignada y, si la hay, la explicación del LLM."""
    c = clasificacion
    errores = [i for i, (r, a) in enumerate(zip(c.reales, c.asignadas)) if r != a]
    if not errores:
        display(HTML(f"<div style='{_FUENTE}color:#14532d;background:#e8f6ec;border:1px solid #8fd19e;border-radius:8px;"
                     "padding:8px 12px'>No hay errores que mostrar.</div>"))
        return
    tarjetas = []
    for i in errores[:maximo]:
        img = c.imagenes[i]
        asignada = c.asignadas[i] or SIN_RESPUESTA
        explicacion = c.explicaciones[i] if c.explicaciones else ""
        texto = (f"<div style='font-size:12.5px;color:#57606a;margin-top:3px'>«{_e(explicacion)}»</div>"
                 if explicacion else "")
        tarjetas.append(
            f"<div style='width:180px;margin:4px;padding:6px;border:1px solid #d0d7de;border-radius:8px;background:#ffffff;"
            f"color:#1f2328;vertical-align:top;display:inline-block'>"
            f"<img src='data:image/jpeg;base64,{_miniatura(img.imagen)}' alt='{_e(img.nombre)}' "
            f"style='width:166px;height:auto;border-radius:4px'>"
            f"<div style='font-size:12.5px;margin-top:4px'><b>{_e(img.nombre)}</b><br>real: <b>{_e(img.clase)}</b> · "
            f"asignada: <b style='color:#b42318'>{_e(asignada)}</b></div>{texto}</div>")
    resto = (f"<div style='{_FUENTE}color:#57606a'>… y {len(errores) - maximo} errores más.</div>"
             if len(errores) > maximo else "")
    display(HTML(f"<div style='{_FUENTE}font-weight:700;margin:8px 0 4px'>Galería de errores · {_e(c.metodo)} · "
                 f"{_e(c.nombre)} · {len(errores)} de {len(c.reales)} imágenes</div>"
                 f"<div style='{_FUENTE}'>{''.join(tarjetas)}</div>{resto}"))


# ------------------------------------------------------------------ CLIP por dentro

def similitudes(clasificacion, indice: int) -> None:
    """Una imagen y su similitud con la descripción de cada clase: gana la barra más larga."""
    c = clasificacion
    img = c.imagenes[indice]
    valores = c.similitudes[indice]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.4), gridspec_kw={"width_ratios": [1, 2.3]})
    a1.imshow(img.miniatura)
    a1.set_xticks([])
    a1.set_yticks([])
    a1.set_title(f"{img.nombre} (real: {img.clase})", fontsize=11, loc="left")
    ganadora = int(np.argmax(valores))
    colores = [AZUL if j == ganadora else "#9aa4b2" for j in range(len(valores))]
    etiquetas = [f"{k}: «{_corta(c.frases[k])}»" for k in c.clases]
    a2.barh(range(len(valores)), valores, color=colores)
    a2.set_yticks(range(len(valores)))
    a2.set_yticklabels(etiquetas, fontsize=10)
    a2.invert_yaxis()
    minimo, maximo = float(min(valores)), float(max(valores))
    margen = max(0.01, (maximo - minimo) * 0.6)
    a2.set_xlim(minimo - margen, maximo + margen / 2)
    for j, v in enumerate(valores):
        a2.text(v, j, f" {v:.3f}", va="center", fontsize=10)
    a2.set_xlabel("similitud entre la imagen y la frase")
    a2.set_title(f"Gana «{c.clases[ganadora]}»", fontsize=11, loc="left")
    _mostrar(fig)


def _corta(frases, largo: int = 55) -> str:
    texto = frases if isinstance(frases, str) else " | ".join(frases)
    return texto if len(texto) <= largo else texto[: largo - 1] + "…"


# ------------------------------------------------------------------ detectores

def cajas(deteccion, titulo: str = "", mostrar_etiquetas: bool = True) -> None:
    """La foto con las cajas del detector. Con referencia, cada caja toma el color de la comparación del 4A."""
    d = deteccion
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(d.imagen)
    estado = d.estado_cajas()
    for i, (x0, y0, x1, y1) in enumerate(d.cajas):
        color = {"correcta": AZUL, "junta": ROJO, "sobrante": NARANJA}.get(estado[i], "#facc15")
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=color, linewidth=2.2))
        if mostrar_etiquetas:
            texto = f"{d.etiquetas[i]} {d.puntajes[i]:.2f}" if d.etiquetas[i] else f"{d.puntajes[i]:.2f}"
            arriba = y0 > 18   # si la caja empieza en el borde de la foto, la etiqueta va por dentro
            ax.text(x0 + 2, y0 - 3 if arriba else y0 + 3, texto, fontsize=8.5, color="white",
                    va="bottom" if arriba else "top",
                    bbox={"facecolor": color, "alpha": 0.85, "pad": 1.2, "edgecolor": "none"})
    if d.comparacion is not None:
        for x, y in d.comparacion["perdidas"]:
            ax.plot(x, y, "x", color=MAGENTA, markersize=18, markeredgewidth=5)
    ax.set_xticks([])
    ax.set_yticks([])
    leyenda = (" · Azul: una cápsula · Rojo: dos o más · Naranja: caja de más · X magenta: perdida"
               if d.comparacion is not None else "")
    ax.set_title((titulo or d.descripcion) + leyenda, fontsize=11, loc="left")
    _mostrar(fig)


def regiones_4a(resultado, comparacion, titulo: str = "") -> None:
    """Las regiones del pipeline del 4A sobre la foto, con los colores de la comparación."""
    estado = {}
    if comparacion is not None:
        estado.update({i: AZUL for i in comparacion.correctas})
        estado.update({i: ROJO for i in comparacion.fusionadas})
        estado.update({i: NARANJA for i in comparacion.sobrantes})
    rgb = resultado.imagen[:, :, ::-1].astype(float) / 255
    salida = rgb * 0.55
    for g in resultado.regiones:
        color = np.array([int(estado.get(g.id, "#7c3aed")[k:k + 2], 16) / 255 for k in (1, 3, 5)])
        zona = resultado.etiquetas == g.id
        salida[zona] = 0.45 * salida[zona] + 0.55 * color
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(np.clip(salida, 0, 1))
    if comparacion is not None:
        for x, y in comparacion.perdidas:
            ax.plot(x, y, "x", color=MAGENTA, markersize=18, markeredgewidth=5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(titulo + " · Azul: una cápsula · Rojo: junta dos o más · Naranja: sin cápsula", fontsize=11, loc="left")
    _mostrar(fig)
