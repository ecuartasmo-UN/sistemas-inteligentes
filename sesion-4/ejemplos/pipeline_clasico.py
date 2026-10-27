"""Pipeline clásico sobre el patrón de calibración del caso 1 (Clase2.ppt, diapositiva 27).

Genera las imágenes de la diapositiva «Histograma, umbral y morfología» de la charla inicial:
gris → histograma → umbral de Otsu → apertura morfológica → componentes conectados → conteo y medición.

Uso, desde esta carpeta:  python pipeline_clasico.py
Requiere opencv-python, numpy y matplotlib. Escribe sus imágenes en ../assets/img/ con el prefijo ej_.
"""
from pathlib import Path

import cv2
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = Path(__file__).resolve().parent
ENTRADA = AQUI.parent / "assets" / "img" / "c2_d027_d.jpg"   # patrón de calibración del caso 1
SALIDA = AQUI.parent / "assets" / "img"
FONDO, TEXTO, ACENTO, AMBAR = "#0a0e17", "#e8ecf4", "#38bdf8", "#f5b942"


def guardar(nombre: str, img: np.ndarray) -> None:
    cv2.imwrite(str(SALIDA / nombre), img)


def histograma(gris: np.ndarray, umbral: float, nombre: str) -> None:
    """Histograma de niveles de gris con el umbral marcado, con los colores del tema del curso."""
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
    fig.patch.set_facecolor(FONDO)
    ax.set_facecolor(FONDO)
    ax.hist(gris.ravel(), bins=128, range=(0, 255), color=ACENTO)
    ax.axvline(umbral, color=AMBAR, linewidth=3)
    ax.text(umbral + 4, ax.get_ylim()[1] * 0.9, f"umbral = {umbral:.0f}", color=AMBAR, fontsize=15)
    ax.set_xlabel("nivel de gris (0 = negro, 255 = blanco)", color=TEXTO, fontsize=14)
    ax.set_ylabel("número de píxeles", color=TEXTO, fontsize=14)
    ax.tick_params(colors=TEXTO, labelsize=12)
    for borde in ax.spines.values():
        borde.set_color("#2a3550")
    fig.tight_layout()
    fig.savefig(SALIDA / nombre, facecolor=FONDO)
    plt.close(fig)


def contar(binaria: np.ndarray, color: np.ndarray, area_min: int = 800) -> tuple[int, list[int], np.ndarray]:
    """Cuenta las regiones con forma de cuadro y las dibuja numeradas sobre la imagen en color."""
    n, etiquetas, stats, centros = cv2.connectedComponentsWithStats(binaria)
    marcada = color.copy()
    areas = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        llenado = area / (w * h)
        if area < area_min or not 0.6 < w / h < 1.6 or llenado < 0.7:
            continue  # descarta ruido y regiones que no parecen cuadros (bordes de la mesa, la base)
        areas.append(int(area))
        cv2.rectangle(marcada, (x, y), (x + w, y + h), (248, 189, 56), 3)
        cv2.putText(marcada, str(len(areas)), (x + 4, y + h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (66, 185, 245), 2)
    return len(areas), areas, marcada


def pixeles(gris: np.ndarray, x: int, y: int, ancho: int = 12, alto: int = 8, lado: int = 64) -> np.ndarray:
    """Recorte ampliado de la imagen con el valor de cada píxel escrito encima: una imagen es una tabla de números."""
    recorte = gris[y:y + alto, x:x + ancho]
    grande = cv2.resize(recorte, (ancho * lado, alto * lado), interpolation=cv2.INTER_NEAREST)
    grande = cv2.cvtColor(grande, cv2.COLOR_GRAY2BGR)
    for i in range(alto):
        for j in range(ancho):
            v = int(recorte[i, j])
            tinta = (20, 20, 20) if v > 110 else (235, 235, 235)
            cv2.putText(grande, str(v), (j * lado + 8, i * lado + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.62, tinta, 2)
    return grande


def main() -> None:
    color = cv2.imread(str(ENTRADA))
    gris = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
    guardar("ej_gris.png", gris)
    guardar("ej_pixeles.png", pixeles(gris, 122, 228))   # borde de un cuadro negro sobre el papel blanco
    marco = cv2.cvtColor(gris, cv2.COLOR_GRAY2BGR)
    cv2.rectangle(marco, (122, 228), (134, 236), (66, 185, 245), 3)
    guardar("ej_pixeles_ubicacion.jpg", marco)

    suave = cv2.GaussianBlur(gris, (5, 5), 0)                       # filtrado: quita ruido fino
    umbral, binaria = cv2.threshold(suave, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    histograma(gris, umbral, "ej_histograma.png")
    guardar("ej_umbral.png", binaria)

    nucleo = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    limpia = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, nucleo)      # apertura: borra puntos y líneas finas
    guardar("ej_morfologia.png", limpia)

    n, areas, marcada = contar(limpia, color)
    guardar("ej_conteo.jpg", marcada)
    izquierda = [a for a in areas[: len(areas) // 2]]
    print(f"Umbral de Otsu: {umbral:.0f}")
    print(f"Cuadros contados: {n} (el patrón tiene 60)")
    print(f"Área de los cuadros en píxeles: mínimo {min(areas)}, máximo {max(areas)}, mediana {int(np.median(areas))}")
    print(f"(El área en píxeles cambia con la perspectiva: para medir en centímetros hace falta calibrar la cámara.)")


if __name__ == "__main__":
    main()
