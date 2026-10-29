# Laboratorio 5B · Leer órdenes de trabajo con un transformer

**Sistemas Inteligentes · Sesión 5 · Especialización en Inteligencia Artificial · UNAL Manizales**

MantenIA recibe órdenes de trabajo escritas en español y debe enviar cada una al equipo que la atiende: eléctrico, mecánico, fugas o instrumentación. En este laboratorio usted:
- compara tres arquitecturas con los mismos ejemplos: una **bolsa de palabras**, una **red recurrente** (LSTM) entrenada desde cero y un **transformer preentrenado**, con la red del Laboratorio 5A encima;
- cambia cuántos ejemplos etiquetados hay por equipo;
- pone a prueba las tres con órdenes escritas con otras palabras y con negaciones;
- termina con un **LLM** que clasifica solo con una instrucción, y mide su costo por cada 1000 órdenes.

El notebook es autocontenido: toda la explicación está dentro de él. Se trabaja en parejas, 60 minutos en clase y hasta 30 en casa. **No se escribe código:** se cambian números, órdenes y nombres de archivo en las celdas marcadas con ✏️.

## Antes de la clase: `preparar.ipynb`

El transformer corre en su computador. Hay que descargarlo una vez, **en casa**:
1. Copie esta carpeta dentro de la carpeta del curso, la que tiene el entorno `.venv`, y ábrala en VS Code.
2. Abra `preparar.ipynb`, elija el kernel del entorno del curso y ejecute sus dos celdas.

Instala lo que falte, `torch` y `transformers` (unos 150 MB), con las mismas versiones del Laboratorio 4B: si ya lo preparó, no descarga ninguna librería. Luego descarga el transformer **Granite Embedding 107M multilingüe**, de IBM (214 MB). Debe terminar con «✓ Preparación completa».

- **Mac con procesador Intel:** no hay `torch` para Python 3.13. Use el respaldo en Google Colab.
- **Linux:** instale antes la versión de `torch` para CPU desde una terminal con el entorno activado:
  `python -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu`

## El LLM: tres vías

El notebook elige solo la primera vía disponible y siempre dice cuál usa.
- **API:** cree un archivo `.env` en la carpeta del curso, fuera de esta carpeta, con la línea `ANTHROPIC_API_KEY=su-clave` (o `OPENAI_API_KEY`, o `GEMINI_API_KEY`). La clave nunca se imprime ni se guarda en el notebook. La corrida de la clase cuesta menos de un centavo de dólar con Claude Haiku 5.5.
- **Local:** Ollama con un modelo de texto, por ejemplo `ollama pull qwen3:4b-instruct` (2,5 GB). Nada sale de su computador.
- **Grabado:** sin clave ni Ollama, el notebook usa respuestas reales de Claude Haiku 5.5, grabadas el 29-oct-2026.

## Archivos

| Archivo o carpeta | Para qué sirve |
| :--- | :--- |
| `lab_5B_ordenes_de_trabajo.ipynb` | El laboratorio |
| `preparar.ipynb` | Instala las librerías y descarga el transformer, antes de la clase |
| `datos/ordenes.csv` | Las 258 órdenes de MantenIA, con su equipo y su conjunto (entrenamiento, prueba o trampa) |
| `mis_textos/` | Donde van sus textos para el trabajo independiente TI-2, con `LEEME.md` y un ejemplo |
| `grabaciones/` | Las respuestas grabadas del LLM |
| `ordenes.py` | Las tres arquitecturas, el LLM, la comparación y el CSV |
| `graficas.py` | Matrices de confusión, errores y aciertos según la cantidad de ejemplos |
| `cliente_llm.py` | El cliente común del LLM |
| `presentacion.py`, `entorno.py`, `requirements.txt` | Apoyo y preparación del entorno |
| `LICENCIA_DATOS.md` | Origen de las órdenes, del transformer y de las respuestas grabadas |

## Sus propios textos (trabajo independiente TI-2)

La sección 9.1 acepta otros textos y otras clases: un CSV con las columnas `texto` y `clase` en la carpeta `mis_textos/`. Las instrucciones están en `mis_textos/LEEME.md`. **Sin datos personales ni información confidencial.**

## Respaldo: Google Colab

Suba el notebook a Colab y, a la carpeta `/content`, el mismo `lab_5B_ordenes_de_trabajo.zip` que le entregó el docente; luego ejecute la primera celda. Colab ya trae `torch` y `transformers`, y el transformer se descarga la primera vez que se usa. Para la vía API, guarde la clave en los **Secrets** de Colab con el nombre `ANTHROPIC_API_KEY`.

## Entrega

El notebook ejecutado, con sus salidas y las celdas ✏️ completas, y el archivo `resultados_5B.csv`, que se crea en la sección 8. Uno por pareja, al inicio de la semana 4 del curso. Los criterios de evaluación están en la sección 10 del notebook.
