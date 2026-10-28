"""Figuras del Laboratorio 4A: etapas del pipeline, píxeles, histogramas, cuadrícula, regiones y medidas.

Cada figura tiene fondo blanco y títulos en español, para que se lea igual con el tema claro y
con el tema oscuro de VS Code.
"""
from __future__ import annotations

import io

import cv2
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import Image, display
from matplotlib.patches import Rectangle

import presentacion as p

# Azul para lo correcto: el verde se confundiría con el de las cápsulas
AZUL, ROJO, NARANJA, MORADO = (0.10, 0.40, 0.95), (0.86, 0.15, 0.15), (0.98, 0.55, 0.05), (0.55, 0.30, 0.85)
MAGENTA = "#d946ef"


def _rgb(imagen: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB) if imagen.ndim == 3 else imagen


def _ejes(ax, titulo: str) -> None:
    ax.set_title(titulo, fontsize=12, loc="left")
    ax.set_xticks([])
    ax.set_yticks([])


def _mostrar(fig) -> None:
    """Muestra la figura como JPEG: las fotos en PNG harían que el notebook entregado pesara decenas de megas."""
    fig.patch.set_facecolor("white")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="jpeg", dpi=90, bbox_inches="tight", pad_inches=0.15, pil_kwargs={"quality": 82})
    plt.close(fig)
    display(Image(data=buf.getvalue(), format="jpeg"))


def _colores_etiquetas(etiquetas: np.ndarray) -> np.ndarray:
    """Un color distinto por región, sobre fondo negro, sin rojos ni naranjas (que en la comparación indican errores)."""
    n = int(etiquetas.max())
    orden = (np.arange(max(n, 1)) * 0.618) % 1          # colores vecinos bien distintos
    paleta = plt.get_cmap("viridis")(0.15 + 0.85 * orden)[:, :3]
    salida = np.zeros(etiquetas.shape + (3,))
    for i in range(1, n + 1):
        salida[etiquetas == i] = paleta[i - 1]
    return salida


# ------------------------------------------------------------------ la imagen como números

def mostrar_imagen(imagen: np.ndarray, titulo: str = "") -> None:
    """Muestra una imagen en color, grande."""
    fig, ax = plt.subplots(figsize=(10, 6.7))
    ax.imshow(_rgb(imagen))
    _ejes(ax, titulo)
    _mostrar(fig)


def mostrar_pixeles(imagen: np.ndarray, fondo=(40, 600), capsula=(172, 440), borde=(133, 311), ancho=12, alto=8) -> None:
    """La imagen como tabla de números: dos zonas marcadas, sus valores R, G y B, y una ampliación con cada píxel."""
    rgb = _rgb(imagen)
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    saturacion = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)[:, :, 1]
    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 5.2), gridspec_kw={"width_ratios": [1.15, 1]})
    a.imshow(rgb)
    for (x, y), nombre, color in ((fondo, "A · fondo", AZUL), (capsula, "B · cápsula", ROJO)):
        a.add_patch(Rectangle((x, y), 24, 24, fill=False, edgecolor=color, linewidth=2.5))
        a.text(x, y - 8, nombre, color=color, fontsize=12, fontweight="bold",
               bbox={"facecolor": "white", "alpha": 0.8, "pad": 1, "edgecolor": "none"})
    x, y = borde   # C es diminuto: se marca con un recuadro holgado y una flecha
    a.add_patch(Rectangle((x - 10, y - 10), ancho + 20, alto + 20, fill=False, edgecolor=NARANJA, linewidth=3))
    a.annotate("C · borde", xy=(x - 10, y + alto / 2), xytext=(x - 120, y - 40), color=NARANJA, fontsize=12,
               fontweight="bold", arrowprops={"arrowstyle": "->", "color": NARANJA, "lw": 2},
               bbox={"facecolor": "white", "alpha": 0.8, "pad": 1, "edgecolor": "none"})
    _ejes(a, "Tres zonas de la foto")
    x, y = borde
    recorte = gris[y:y + alto, x:x + ancho]
    b.imshow(recorte, cmap="gray", vmin=0, vmax=255)
    for i in range(alto):
        for j in range(ancho):
            v = int(recorte[i, j])
            b.text(j, i, str(v), ha="center", va="center", fontsize=10, color="black" if v > 110 else "white")
    _ejes(b, f"Zona C ampliada: {ancho} × {alto} píxeles en gris (0 = negro, 255 = blanco)")
    _mostrar(fig)

    def promedio(canal, punto):
        x, y = punto
        return int(round(float(canal[y:y + 24, x:x + 24].mean())))
    filas = []
    for nombre, punto in (("A · fondo gris", fondo), ("B · cápsula verde", capsula)):
        filas.append({"zona": nombre, "rojo (R)": promedio(rgb[:, :, 0], punto), "verde (G)": promedio(rgb[:, :, 1], punto),
                      "azul (B)": promedio(rgb[:, :, 2], punto), "gris": promedio(gris, punto),
                      "saturación": promedio(saturacion, punto)})
    p.mostrar_tabla(filas, titulo="Promedio de cada canal en las zonas A y B (0 a 255)")


def mostrar_histogramas(imagen: np.ndarray, canales=("gris", "saturacion"), suavizado: int = 5) -> None:
    """Cada canal como imagen y su histograma, con el umbral que elegiría Otsu."""
    import inspeccion
    fig, ejes = plt.subplots(len(canales), 2, figsize=(14, 3.6 * len(canales)), gridspec_kw={"width_ratios": [1, 1.5]})
    ejes = np.atleast_2d(ejes)
    for fila, canal in zip(ejes, canales):
        c = inspeccion.extraer_canal(imagen, inspeccion._normal(canal))
        if suavizado > 1:
            c = cv2.GaussianBlur(c, (suavizado, suavizado), 0)
        umbral, _ = cv2.threshold(c, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        fila[0].imshow(c, cmap="gray", vmin=0, vmax=255)
        _ejes(fila[0], f"Canal: {canal}")
        cuentas, bordes, _ = fila[1].hist(c.ravel(), bins=128, range=(0, 255), color="#3b82f6")
        # Si un pico aplasta al resto (la tela en la saturación), se recorta el eje y se anota su altura
        pico = int(np.argmax(cuentas))
        resto = np.delete(cuentas, range(max(0, pico - 6), min(len(cuentas), pico + 7)))
        if resto.size and cuentas[pico] > 4 * resto.max():
            tope = 1.6 * resto.max()
            fila[1].set_ylim(0, tope)
            fila[1].annotate(f"↑ el pico sigue: {int(cuentas[pico]):,} píxeles".replace(",", "."),
                             xy=(bordes[pico] + 1, tope * 0.97), xytext=(bordes[pico] + 12, tope * 0.75),
                             fontsize=11, color="#1e3a8a", arrowprops={"arrowstyle": "->", "color": "#1e3a8a"})
        fila[1].axvline(umbral, color="#d97706", linewidth=2.5)
        fila[1].text(umbral + 3, fila[1].get_ylim()[1] * 0.88, f"Otsu: {umbral:.0f}", color="#b45309", fontsize=12)
        fila[1].set_title(f"Histograma del canal {canal}", fontsize=12, loc="left")
        fila[1].set_xlabel("valor del píxel (0 a 255)")
        fila[1].set_ylabel("número de píxeles")
        fila[1].set_xlim(0, 255)
    _mostrar(fig)


def mostrar_cuadricula(imagen: np.ndarray, filas: int = 3, columnas: int = 4) -> None:
    """La foto con una cuadrícula rotulada, para contar a mano casilla por casilla."""
    rgb = _rgb(imagen)
    alto, ancho = rgb.shape[:2]
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(rgb)
    for i in range(1, filas):
        ax.axhline(i * alto / filas, color="white", linewidth=1.5)
    for j in range(1, columnas):
        ax.axvline(j * ancho / columnas, color="white", linewidth=1.5)
    for i in range(filas):
        for j in range(columnas):
            ax.text(j * ancho / columnas + 8, i * alto / filas + 28, f"{'ABCDEFG'[i]}{j + 1}", color="white", fontsize=14,
                    fontweight="bold", bbox={"facecolor": "black", "alpha": 0.55, "pad": 2, "edgecolor": "none"})
    _ejes(ax, "Cuente las cápsulas casilla por casilla. Una cápsula que cruza una línea cuenta en la casilla donde está su centro.")
    _mostrar(fig)


# ------------------------------------------------------------------ el pipeline

def mostrar_etapas(r) -> None:
    """Las seis etapas del pipeline lado a lado: de la foto a las regiones."""
    fig, ejes = plt.subplots(2, 3, figsize=(15, 6.8))
    for ax, (titulo, img) in zip(ejes.ravel(), r.etapas):
        if titulo.startswith("6"):
            ax.imshow(_colores_etiquetas(img))
        elif img.ndim == 2:
            ax.imshow(img, cmap="gray", vmin=0, vmax=255)
        else:
            ax.imshow(img)
        _ejes(ax, titulo)
    _mostrar(fig)


def mostrar_comparacion(r, comp=None) -> None:
    """Las regiones sobre la foto, coloreadas según la comparación con la referencia."""
    base = _rgb(r.imagen).astype(float) / 255 * 0.55
    salida = base.copy()
    estado = {}
    if comp is not None:
        estado.update({i: AZUL for i in comp.correctas})
        estado.update({i: ROJO for i in comp.fusionadas})
        estado.update({i: NARANJA for i in comp.sobrantes})
    for g in r.regiones:
        color = np.array(estado.get(g.id, MORADO))
        zona = r.etiquetas == g.id
        salida[zona] = 0.45 * salida[zona] + 0.55 * color
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(np.clip(salida, 0, 1))
    contorno = cv2.morphologyEx((r.etiquetas > 0).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    ax.contour(contorno, levels=[0.5], colors="white", linewidths=0.6)
    numerar = r.conteo <= 60   # con cientos de regiones, los números taparían la foto
    if numerar:
        for g in r.regiones:
            ax.text(g.x, g.y, str(g.id), ha="center", va="center", fontsize=10, fontweight="bold", color="white",
                    bbox={"facecolor": "black", "alpha": 0.6, "pad": 1.5, "edgecolor": "none"})
    if comp is not None:
        sobrantes = set(comp.sobrantes)
        for g in r.regiones:   # las regiones de más suelen ser fragmentos pequeños: un círculo las hace visibles
            if g.id in sobrantes:
                ax.plot(g.x, g.y, "o", markersize=26, markerfacecolor="none", markeredgecolor="#f97316", markeredgewidth=3)
        for x, y in comp.perdidas:
            ax.plot(x, y, "x", color=MAGENTA, markersize=18, markeredgewidth=5)
        titulo = (f"{r.nombre} · Azul: una cápsula · Rojo: junta dos o más · "
                  "Naranja (con círculo): sin cápsula · X magenta: perdida")
    else:
        titulo = f"{r.nombre}: {r.conteo} regiones (sin comparar todavía con la referencia)"
    if not numerar:
        titulo += " · demasiadas regiones para numerarlas"
    _ejes(ax, titulo)
    _mostrar(fig)


def mostrar_distancia(r) -> None:
    """Cómo se separan objetos que se tocan: la máscara, la distancia al fondo con sus centros y las regiones."""
    if r is None or r.distancia is None:
        p.nota("Esta corrida no separó objetos: ponga \"separar\": True en PARAMETROS y ejecute de nuevo.", "aviso")
        return
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(16, 4.4))
    a.imshow(r.mascara, cmap="gray")
    _ejes(a, "Máscara: cápsulas unidas en una mancha")
    b.imshow(r.distancia, cmap="magma")
    filas, cols = np.nonzero(r.marcas)
    finales = r.etiquetas[filas, cols] > 0   # solo los centros de regiones que quedaron (no los de fragmentos descartados)
    b.plot(cols[finales], filas[finales], "o", color="#22d3ee", markersize=6)
    _ejes(b, f"Distancia al fondo y un centro por región ({int(finales.sum())})")
    c.imshow(_colores_etiquetas(r.etiquetas))
    _ejes(c, f"Regiones crecidas desde cada centro: {r.conteo}")
    _mostrar(fig)


def mostrar_bordes(imagen: np.ndarray, canal: str = "saturacion") -> None:
    """Bordes con el filtro de Sobel: dónde cambia rápido el valor de los píxeles."""
    import inspeccion
    c = inspeccion.extraer_canal(imagen, inspeccion._normal(canal))
    gx = cv2.Sobel(c, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(c, cv2.CV_32F, 0, 1, ksize=3)
    magnitud = np.hypot(gx, gy)
    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 4.8))
    a.imshow(c, cmap="gray", vmin=0, vmax=255)
    _ejes(a, f"Canal: {canal}")
    b.imshow(magnitud, cmap="gray", vmax=np.percentile(magnitud, 99))
    _ejes(b, "Bordes (Sobel): claro donde el valor cambia rápido")
    _mostrar(fig)


# ------------------------------------------------------------------ medir

def mostrar_forma(r, fuera: list, tolerancia) -> None:
    """Las cápsulas dentro de la tolerancia de alargamiento en azul y las que se salen en rojo."""
    base = _rgb(r.imagen).astype(float) / 255 * 0.55
    for g in r.regiones:
        zona = r.etiquetas == g.id
        color = np.array(ROJO if g.id in fuera else AZUL)
        base[zona] = 0.45 * base[zona] + 0.55 * color
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(np.clip(base, 0, 1))
    for g in r.regiones:
        ax.text(g.x, g.y, str(g.id), ha="center", va="center", fontsize=10, fontweight="bold", color="white",
                bbox={"facecolor": "black", "alpha": 0.6, "pad": 1.5, "edgecolor": "none"})
    _ejes(ax, f"Tolerancia ±{tolerancia:g} % sobre el alargamiento típico · azul: pasa · rojo: se rechaza ({len(fuera)})")
    _mostrar(fig)


def mostrar_patron(imagen: np.ndarray, cuadros: list, factor: float, base: list | None = None) -> None:
    """Cada cuadro del patrón coloreado según su lado en píxeles: la perspectiva a la vista."""
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.imshow(_rgb(imagen))
    lados = np.array([c["lado_px"] for c in cuadros])
    normal = plt.Normalize(lados.min(), lados.max())
    mapa = plt.get_cmap("viridis")
    for c, lado in zip(cuadros, lados):
        ax.add_patch(Rectangle((c["x"], c["y"]), c["w"], c["h"], fill=True, alpha=0.75, color=mapa(normal(lado))))
        ax.text(c["cx"], c["cy"], f"{lado * factor:.0f}", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    for c in base or []:   # las franjas de la base del montaje: no son cuadros del patrón
        ax.add_patch(Rectangle((c["x"], c["y"]), c["w"], c["h"], fill=False, edgecolor="#dc2626", linewidth=2.5))
    if base:
        b0 = min(base, key=lambda c: c["x"])
        ax.text(b0["x"], b0["y"] - 12, "base del montaje (no cuenta)", color="#dc2626", fontsize=11, fontweight="bold",
                bbox={"facecolor": "white", "alpha": 0.8, "pad": 1, "edgecolor": "none"})
    barra = fig.colorbar(plt.cm.ScalarMappable(norm=normal, cmap=mapa), ax=ax, fraction=0.03, pad=0.01)
    barra.set_label("color: lado del cuadro en píxeles")
    _ejes(ax, "Todos los cuadros son iguales. El número es su lado «medido» en mm con un solo factor; el color, en píxeles")
    _mostrar(fig)
