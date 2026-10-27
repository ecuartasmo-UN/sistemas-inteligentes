"""La iluminación decide: el mismo pipeline con luz desigual (charla de cierre).

Oscurece el patrón de calibración del caso 1 con un gradiente de luz, como una lámpara a un lado,
y compara el umbral global de Otsu con un umbral adaptativo, que decide píxel por píxel según su vecindario.

Uso, desde esta carpeta:  python iluminacion.py
Requiere opencv-python y numpy. Reutiliza las funciones de pipeline_clasico.py y escribe en ../assets/img/.
"""
import cv2
import numpy as np

from pipeline_clasico import ENTRADA, contar, guardar


def main() -> None:
    color = cv2.imread(str(ENTRADA))
    alto, ancho = color.shape[:2]
    # Luz desigual: del 100 % a la derecha al 22 % a la izquierda
    gradiente = np.tile(np.linspace(0.22, 1.0, ancho), (alto, 1))[..., None]
    oscura = np.clip(color * gradiente, 0, 255).astype(np.uint8)
    guardar("ej_luz_desigual.jpg", oscura)

    gris = cv2.GaussianBlur(cv2.cvtColor(oscura, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    nucleo = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))

    umbral, global_ = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    global_ = cv2.morphologyEx(global_, cv2.MORPH_OPEN, nucleo)
    n_global, _, marcada_global = contar(global_, oscura)
    guardar("ej_umbral_global.png", global_)
    guardar("ej_conteo_global.jpg", marcada_global)

    adaptativa = cv2.adaptiveThreshold(gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 151, 15)
    adaptativa = cv2.morphologyEx(adaptativa, cv2.MORPH_OPEN, nucleo)
    n_adapt, _, marcada_adapt = contar(adaptativa, oscura)
    guardar("ej_umbral_adaptativo.png", adaptativa)
    guardar("ej_conteo_adaptativo.jpg", marcada_adapt)

    print(f"Con luz desigual, umbral global de Otsu ({umbral:.0f}): {n_global} cuadros contados de 60")
    print(f"Con luz desigual, umbral adaptativo: {n_adapt} cuadros contados de 60")


if __name__ == "__main__":
    main()
