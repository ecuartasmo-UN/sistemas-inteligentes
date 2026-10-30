# Laboratorio 6A · Del dato al conocimiento

**Sistemas Inteligentes · Sesión 6 · Especialización en Inteligencia Artificial · UNAL Manizales**

Un algoritmo induce reglas a partir de casos resueltos, como las que un experto escribía a mano en un sistema experto. En este laboratorio usted:
- induce un **árbol de decisión** con los 1309 pasajeros del Titanic y lee sus reglas, con los casos que respaldan cada una;
- lo compara con la regla del experto, «mujeres y niños primero», con dos **ensambles** y con las reglas que escribe un **LLM** sin ver los datos;
- mide el sobreajuste con **validación cruzada** al cambiar la profundidad del árbol;
- elige el **umbral de decisión** de un crédito, con el German Credit, según el costo de cada error.

El notebook es autocontenido: toda la explicación está dentro de él. Se trabaja en parejas, 60 minutos en clase y hasta 30 en casa. **No se escribe código:** se cambian números y textos en las celdas marcadas con ✏️.

## Antes de la clase

1. Copie esta carpeta dentro de la carpeta del curso, la que tiene el entorno `.venv`, y ábrala en VS Code.
2. Abra `lab_6A_del_dato_al_conocimiento.ipynb`, elija el kernel del entorno del curso y ejecute **la primera celda**. Instala lo que falte, `scikit-learn` (unos 40 MB con sus dependencias). Debe terminar con «✓ Todos los paquetes del laboratorio están instalados» o «✓ Paquetes instalados».

Funciona en Windows, en macOS (también con procesador Intel) y en Linux, con Python 3.12 o 3.13.

## El LLM: tres vías

Solo la sección 5 y la 7.1 usan un LLM. El notebook elige solo la primera vía disponible y siempre dice cuál usa.
- **API:** cree un archivo `.env` en la carpeta del curso, fuera de esta carpeta, con la línea `ANTHROPIC_API_KEY=su-clave` (o `OPENAI_API_KEY`, o `GEMINI_API_KEY`). La clave nunca se imprime ni se guarda en el notebook. Las dos llamadas del laboratorio cuestan menos de una décima de centavo de dólar con Claude Haiku 5.5.
- **Local:** Ollama con un modelo de texto, por ejemplo `ollama pull qwen3:4b-instruct` (2,5 GB). Nada sale de su computador.
- **Grabado:** sin clave ni Ollama, el notebook usa respuestas reales de Claude Haiku 5.5, grabadas el 29-oct-2026.

## Archivos

| Archivo o carpeta | Para qué sirve |
| :--- | :--- |
| `lab_6A_del_dato_al_conocimiento.ipynb` | El laboratorio |
| `datos/titanic3.csv` | Los 1309 pasajeros del Titanic, sin nombres |
| `datos/credito_aleman.csv` | Las 1000 solicitudes del German Credit, en español |
| `mis_casos/` | Donde van sus casos para el trabajo independiente TI-1, con `LEEME.md` y un ejemplo |
| `grabaciones/` | Las respuestas grabadas del LLM |
| `arboles.py` | Los datos, la regla del experto, los árboles y sus reglas, los ensambles y el CSV |
| `reglas_llm.py` | Las reglas del LLM: la instrucción, su lectura y su aplicación |
| `costos.py` | El German Credit: probabilidades, umbrales y costos |
| `graficas.py` | El árbol dibujado, las curvas y las matrices |
| `cliente_llm.py` | El cliente común del LLM |
| `presentacion.py`, `entorno.py`, `requirements.txt` | Apoyo y preparación del entorno |
| `LICENCIA_DATOS.md` | Origen y licencia de los datos y de las respuestas grabadas |

## Sus propios casos (trabajo independiente TI-1)

La sección 7.4 acepta otros casos, otras columnas y otras conclusiones: un CSV con una columna `conclusion` en la carpeta `mis_casos/`. Las instrucciones están en `mis_casos/LEEME.md`. **Sin datos personales ni información confidencial.**

## Respaldo: Google Colab

Suba el notebook a Colab y, a la carpeta `/content`, el mismo `lab_6A_del_dato_al_conocimiento.zip` que le entregó el docente; luego ejecute la primera celda. Colab ya trae `scikit-learn`. Para la vía API, guarde la clave en los **Secrets** de Colab con el nombre `ANTHROPIC_API_KEY`.

## Entrega

El notebook ejecutado, con sus salidas y las celdas ✏️ completas, y el archivo `resultados_6A.csv`, que se crea en la sección 8. Uno por pareja, al inicio de la semana 4 del curso. Los criterios de evaluación están en la sección 8 del notebook.
