# Laboratorio 5A · Del perceptrón a la red profunda

**Sistemas Inteligentes · Sesión 5 · Especialización en Inteligencia Artificial · UNAL Manizales**

MantenIA quiere anticipar las fallas de una máquina de fresado con las lecturas de sus sensores. En este laboratorio usted entrena en PyTorch un **perceptrón multicapa** que lo predice, con el conjunto AI4I 2020, y:
- cambia las capas, las neuronas, la tasa de aprendizaje, las épocas y el dropout;
- lee las curvas de aprendizaje de entrenamiento y de validación;
- provoca el sobreajuste y lo frena con dropout y parada temprana;
- compara redes de distinta profundidad y anchura.

El notebook es autocontenido: toda la explicación está dentro de él. Se trabaja en parejas, 60 minutos en clase y hasta 30 en casa. **No se escribe código:** se cambian números en las celdas marcadas con ✏️.

## Antes de la clase

1. Copie esta carpeta dentro de la carpeta del curso, la que tiene el entorno `.venv`, y ábrala en VS Code.
2. Abra `lab_5A_red_profunda.ipynb`, elija el kernel del entorno del curso y ejecute **solo la primera celda**. Instala `torch` si falta (unos 130 MB en Windows o en un Mac con procesador Apple). Si ya preparó el Laboratorio 4B, no descarga nada.

- **Mac con procesador Intel:** no hay `torch` para Python 3.13. Use el respaldo en Google Colab.
- **Linux:** `pip` instala por defecto la versión de `torch` para tarjetas NVIDIA, de varios GB. Instale antes la versión para CPU desde una terminal con el entorno activado:
  `python -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu`

No usa LLM, claves de API ni modelos descargados: la red se entrena en su computador, en segundos.

## Archivos

| Archivo o carpeta | Para qué sirve |
| :--- | :--- |
| `lab_5A_red_profunda.ipynb` | El laboratorio |
| `datos/ai4i2020.csv` | Los 10 000 registros de la máquina |
| `red_fallas.py` | Los datos, la red, el entrenamiento, las comparaciones y la bitácora |
| `graficas.py` | Las curvas de aprendizaje y la matriz de confusión |
| `presentacion.py`, `entorno.py`, `requirements.txt` | Apoyo y preparación del entorno |
| `LICENCIA_DATOS.md` | Origen y licencia de los datos |

## Respaldo: Google Colab

Suba el notebook a Colab y, a la carpeta `/content`, el mismo `lab_5A_red_profunda.zip` que le entregó el docente; luego ejecute la primera celda. Colab ya trae `torch`.

## Entrega

El notebook ejecutado, con sus salidas y las celdas ✏️ completas, y el archivo `resultados_5A.csv`, que se crea solo al entrenar. Uno por pareja, al inicio de la semana 4 del curso. Los criterios de evaluación están en la sección 8 del notebook.
