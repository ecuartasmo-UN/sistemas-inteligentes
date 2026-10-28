# Imágenes y modelos del Laboratorio 4B: origen y licencia

## Cápsulas y fotos: conjunto VisA

- **Autoría:** Zou, Y., Jeong, J., Pemula, L., Zhang, D. y Dabeer, O. (2022). *SPot-the-Difference self-supervised pre-training for anomaly detection and segmentation*. ECCV 2022. <https://arxiv.org/abs/2207.14315>
- **Fuente:** conjunto VisA (Visual Anomaly), subconjunto *capsules*, descargado del sitio oficial el 28 de octubre de 2026. <https://github.com/amazon-science/spot-diff>
- **Licencia:** [Creative Commons Atribución 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.es).

| Archivo | Origen y cambios |
| :--- | :--- |
| `imagenes/capsulas/<clase>/*.jpg` | 32 recortes de fotos de VisA, 8 por clase. El origen de cada uno (foto y región) está en `imagenes/capsulas/origen.csv`. **Cambios:** cada recorte es un cuadrado de 448 píxeles centrado en una cápsula; fuera de la cápsula se pintó el color típico de la tela, para que se vea una sola. |
| `imagenes/fotos/capsulas_principal.jpg` | `capsules/Data/Images/Normal/000.JPG`, reducida de 1500 × 1000 a 1000 × 667 píxeles |
| `imagenes/fotos/capsulas_juntas.jpg` | `capsules/Data/Images/Normal/005.JPG`, reducida igual |
| `imagenes/fotos/capsulas_limite.jpg` | `capsules/Data/Images/Normal/020.JPG`, reducida igual |

**Las clases.** La clase de cada recorte sale de las máscaras oficiales de VisA, que marcan los píxeles de cada defecto: `burbuja` (*bubble*), `deforme` (*misshape*) y `mancha` (*discolor*). Las normales vienen de fotos sin defectos. Por clase se tomaron los ocho defectos más grandes, cada uno de una foto distinta.

**Las referencias de conteo.** `imagenes/fotos/referencias.json` guarda, para cada foto, la cantidad de cápsulas y el centro de cada una: las mismas del Laboratorio 4A, revisadas región por región y, en la foto límite, marcadas a mano.

## Figura de CLIP

La figura de la sección 2 viene del repositorio de CLIP: OpenAI (2021), <https://github.com/openai/CLIP>, licencia MIT.

## Modelos

Los modelos no vienen en esta carpeta: se descargan de Hugging Face con `preparar.ipynb`, cada uno en una versión fija.

| Modelo | Autor | Licencia | Repositorio |
| :--- | :--- | :--- | :--- |
| CLIP ViT-B/32 | OpenAI | MIT | <https://huggingface.co/openai/clip-vit-base-patch32> |
| OWLv2 base | Google | Apache-2.0 | <https://huggingface.co/google/owlv2-base-patch16-ensemble> |
| RT-DETRv2 R18 | Baidu y Universidad de Pekín | Apache-2.0 | <https://huggingface.co/PekingU/rtdetr_v2_r18vd> |

La ficha del modelo de CLIP declara fuera de alcance cualquier uso desplegado, comercial o no, sin pruebas exhaustivas en el dominio. Aquí se usa para aprender y comparar.

## Respuestas grabadas

`grabaciones/respuestas.json` guarda respuestas reales de Claude Haiku 5.5 (Anthropic) a las 32 cápsulas, obtenidas por la API el 28 de octubre de 2026. No se escribieron a mano.

MantenIA, la estación de inspección y su cliente farmacéutico son ficticios.
