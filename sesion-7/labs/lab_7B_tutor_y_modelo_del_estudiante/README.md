# Laboratorio 7B · Sistema tutorial inteligente: el modelo del estudiante

**Sistemas Inteligentes · Sesión 7 · Especialización en Inteligencia Artificial · UNAL Manizales**

Un tutor inteligente estima qué sabe cada persona, aunque no lo pueda ver. En este laboratorio:
- sigues con **Bayesian Knowledge Tracing** el dominio de un técnico simulado, respuesta a respuesta;
- cambias las respuestas y los cuatro parámetros, y ves cómo cambia la curva de dominio;
- comparas dos reglas para elegir el siguiente ejercicio: practicar hasta dominar, o un número fijo de ejercicios;
- le pides a un **LLM** que estime el mismo dominio, y lo comparas en exactitud, consistencia y explicación;
- en casa, mides cuánto cuesta cada punto de certeza y le das los parámetros al LLM;
- para el TI-2, escribes tus propios datos en una celda.

Toda la explicación está dentro del notebook. Se trabaja en parejas, 60 minutos en clase y hasta 30 en casa. **No escribes código:** cambias valores en las celdas marcadas con ✏️.

## Antes de la clase

Nada que instalar: usa `numpy`, `matplotlib` y el cliente de LLM del entorno del curso. Copia esta carpeta dentro de la carpeta del curso, la que tiene el entorno `.venv`. Ábrela en VS Code y elige el kernel del entorno del curso. Funciona con Python 3.12 o 3.13.

**El LLM** llega por la primera vía disponible. Puede ser una clave de API en el `.env` de la carpeta del curso, Ollama o las respuestas de `grabaciones/`. Con las grabadas no hace falta red ni clave.

## Archivos

| Archivo | Para qué sirve |
| :--- | :--- |
| `lab_7B_tutor_y_modelo_del_estudiante.ipynb` | El laboratorio |
| `tutor.py` | Bayesian Knowledge Tracing, los técnicos simulados, las reglas de selección y tus datos |
| `contrapunto.py` | El prompt al LLM, la lectura de sus respuestas y la comparación con el modelo bayesiano |
| `cliente_llm.py` | La conexión con el LLM, con su costo y su presupuesto |
| `graficas.py` | Las curvas de dominio y las barras |
| `apoyo.py` | Revisa lo que escribes y lleva la bitácora `resultados_7B.csv` |
| `presentacion.py`, `entorno.py`, `requirements.txt` | Apoyo y preparación del entorno |
| `datos/` | Los 10 técnicos simulados del contrapunto, con su `LEEME.md` |
| `grabaciones/` | Respuestas reales de Claude Haiku 5.5, para trabajar sin clave |
| `LICENCIA.md` | Origen del modelo y de los datos |

## Respaldo: Google Colab

Sube el notebook a Colab y, a la carpeta `/content`, el archivo `lab_7B_tutor_y_modelo_del_estudiante.zip` que te entregó el docente. Luego ejecuta la primera celda.

## Entrega

El notebook ejecutado, con los resultados de cada celda y las celdas ✏️ completas. También `resultados_7B.csv`, la bitácora, y `contrapunto_7B.csv`, el contrapunto en el formato común del curso. Entregan uno por pareja, en la fase de cierre del curso. Los criterios de evaluación están en la sección 7 del notebook.
