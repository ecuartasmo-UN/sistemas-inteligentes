# Imágenes del Laboratorio 4A: origen y licencia

## Fotos de cápsulas: conjunto VisA

| Archivo | Imagen original de VisA |
| :--- | :--- |
| `imagenes/capsulas_principal.jpg` | `capsules/Data/Images/Normal/000.JPG` |
| `imagenes/capsulas_juntas.jpg` | `capsules/Data/Images/Normal/005.JPG` |
| `imagenes/capsulas_limite.jpg` | `capsules/Data/Images/Normal/020.JPG` |
| `imagenes/capsulas_deforme.jpg` | `capsules/Data/Images/Anomaly/070.JPG` |

- **Autoría:** Zou, Y., Jeong, J., Pemula, L., Zhang, D. y Dabeer, O. (2022). *SPot-the-Difference self-supervised pre-training for anomaly detection and segmentation*. ECCV 2022. <https://arxiv.org/abs/2207.14315>
- **Fuente:** conjunto VisA (Visual Anomaly), descargado del sitio oficial el 28 de octubre de 2026. <https://github.com/amazon-science/spot-diff>
- **Licencia:** [Creative Commons Atribución 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.es).
- **Cambios:**
  - las fotos se redujeron de 1500 × 1000 a 1000 × 667 píxeles;
  - la lámpara de la sección 8 se simula al ejecutar el notebook y no modifica los archivos.

## Patrón de calibración

`imagenes/patron_calibracion.jpg` viene de la diapositiva 27 de *Procesamiento Digital de Imágenes* (2007), de Ernesto Cuartas Morales, y se usa en el curso con autorización del autor. Sus cuadros negros miden 5 × 5 cm.

## Referencias de conteo

`imagenes/referencias.json` guarda, para cada foto de cápsulas, la cantidad y el centro de cada cápsula. En las fotos principal, juntas y deforme se tomaron de una configuración de referencia del pipeline y se revisaron región por región; en la foto límite se marcaron a mano. La cápsula deforme es la que marca la máscara oficial de VisA.

MantenIA, la estación de inspección y su cliente farmacéutico son ficticios.
