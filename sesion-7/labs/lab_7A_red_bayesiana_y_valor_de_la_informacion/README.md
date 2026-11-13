# Laboratorio 7A · Red bayesiana y decisión con valor de la información

**Sistemas Inteligentes · Sesión 7 · Especialización en Inteligencia Artificial · UNAL Manizales**

Un sistema inteligente casi nunca está seguro. En este laboratorio razonas con probabilidades y decides con ellas:
- ves por qué la mayoría de los avisos de una alarma muy precisa son falsos: la **tasa base**;
- agregas evidencia a la **red de la alarma** de Judea Pearl para predecir y diagnosticar;
- compruebas el **explaining away** y la **independencia condicional**;
- calculas la **utilidad esperada** del **petrolero** de Howard Raiffa, con un **diagrama de influencia**;
- calculas el **valor de la información** de una prueba sísmica y lo comparas con su precio;
- en casa, cambias las tablas y los pagos, pruebas una prueba menos confiable y cargas tu propia decisión, para el TI-1.

Toda la explicación está dentro del notebook. Se trabaja en parejas, 60 minutos en clase y hasta 30 en casa. **No escribes código:** cambias valores en las celdas marcadas con ✏️.

## Antes de la clase

Copia esta carpeta dentro de la carpeta del curso, la que tiene el entorno `.venv`. Ábrela en VS Code y elige el kernel del entorno del curso. Ejecuta en casa la primera celda del notebook: instala `pyagrum` si falta. Son unos 5 MB si ya hiciste el Laboratorio 6A, y unos 35 MB si no. Funciona con Python 3.12 o 3.13. No usa ningún LLM y no necesita Graphviz.

## Archivos

| Archivo | Para qué sirve |
| :--- | :--- |
| `lab_7A_red_bayesiana_y_valor_de_la_informacion.ipynb` | El laboratorio |
| `redes.py` | La tasa base y la red de la alarma, con pyAgrum y con la cuenta a mano |
| `decisiones.py` | La utilidad esperada, el valor de la información y tu propia decisión |
| `graficas.py` | El árbol de frecuencias, la red, las barras, el diagrama de influencia y la curva |
| `apoyo.py` | Revisa lo que escribes y lleva la bitácora `resultados_7A.csv` |
| `presentacion.py`, `entorno.py`, `requirements.txt` | Apoyo y preparación del entorno |
| `LICENCIA.md` | Origen de la red de la alarma, del petrolero y de pyAgrum |

## Respaldo: Google Colab

Sube el notebook a Colab y, a la carpeta `/content`, el archivo `lab_7A_red_bayesiana_y_valor_de_la_informacion.zip` que te entregó el docente. Luego ejecuta la primera celda: instala `pyagrum` en Colab.

## Entrega

El notebook ejecutado, con los resultados de cada celda y las celdas ✏️ completas. También el archivo `resultados_7A.csv`: la bitácora que el notebook escribe solo, y que conserva lo anotado aunque reinicies el kernel. Entregan uno por pareja, en la fase de cierre del curso. Los criterios de evaluación están en la sección 8 del notebook.
