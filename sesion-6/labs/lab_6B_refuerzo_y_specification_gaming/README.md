# Laboratorio 6B · Aprendizaje por refuerzo y *specification gaming*

**Sistemas Inteligentes · Sesión 6 · Especialización en Inteligencia Artificial · UNAL Manizales**

Un agente que nadie corrige: solo recibe recompensas por lo que hace. En este laboratorio usted:
- resuelve el **mundo de 4×3** de Russell y Norvig con la **iteración de valores** y lee su política, una flecha por casilla;
- cambia la recompensa por paso y ve cambiar la conducta;
- entrena un agente que aprende sin conocer el modelo (**Q-learning**) y compara su política con la exacta;
- compara planes de **exploración**;
- entrena al bote de la **carrera de botes** de los *AI Safety Gridworlds* y compara la recompensa que gana con su desempeño real;
- en casa, arregla la recompensa del bote y prueba el movimiento incierto y el descuento.

El notebook es autocontenido: toda la explicación está dentro de él. Se trabaja en parejas, 60 minutos en clase y hasta 30 en casa. **No se escribe código:** se cambian valores en las celdas marcadas con ✏️.

## Antes de la clase

Nada que descargar: el laboratorio usa `numpy` y `matplotlib`, que ya están en el entorno del curso. Copie esta carpeta dentro de la carpeta del curso, la que tiene el entorno `.venv`, ábrala en VS Code y elija el kernel del entorno del curso. Funciona en Windows, en macOS (también con procesador Intel) y en Linux, con Python 3.12 o 3.13. No usa ningún LLM.

## Archivos

| Archivo | Para qué sirve |
| :--- | :--- |
| `lab_6B_refuerzo_y_specification_gaming.ipynb` | El laboratorio |
| `refuerzo.py` | El mundo de 4×3, la iteración de valores, el agente de Q-learning, la carrera de botes y la bitácora |
| `graficas.py` | Las cuadrículas, las curvas y la pista |
| `presentacion.py`, `entorno.py`, `requirements.txt` | Apoyo y preparación del entorno |
| `LICENCIA.md` | Origen del mundo de 4×3 y de la carrera de botes |

## Respaldo: Google Colab

Suba el notebook a Colab y, a la carpeta `/content`, el mismo `lab_6B_refuerzo_y_specification_gaming.zip` que le entregó el docente; luego ejecute la primera celda.

## Entrega

El notebook ejecutado, con los resultados de cada celda y las celdas ✏️ completas, y el archivo `resultados_6B.csv`, la bitácora que el notebook escribe solo y que conserva lo anotado aunque se reinicie el kernel. Uno por pareja, al inicio de la semana 4 del curso. Los criterios de evaluación están en la sección 8 del notebook.
