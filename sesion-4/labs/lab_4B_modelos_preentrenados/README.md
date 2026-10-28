# Laboratorio 4B · Reconocimiento con modelos preentrenados

**Sistemas Inteligentes · Sesión 4 · Especialización en Inteligencia Artificial · UNAL Manizales**

Las mismas cápsulas del Laboratorio 4A, ahora con modelos que ya saben ver:
- **CLIP**, que clasifica sin entrenamiento previo: usted escribe cada clase como una frase;
- un **LLM multimodal**, que recibe cada imagen con una instrucción;
- dos **detectores**: uno entrenado con objetos comunes y uno que busca lo que usted describe con texto.

Los compara con la matriz de confusión, el costo por imagen y el análisis de errores, y decide cuándo basta el pipeline del 4A.

El notebook es autocontenido: toda la explicación está dentro de él. Se trabaja en parejas, 60 minutos en clase y hasta 30 en casa. **No se escribe código:** se cambian frases y números en las celdas marcadas con ✏️.

## Antes de la clase: `preparar.ipynb`

CLIP y los detectores corren en su computador. Hay que descargarlos una vez, **en casa y con buena conexión**:
1. Copie esta carpeta dentro de la carpeta del curso, la que tiene el entorno `.venv`, y ábrala en VS Code.
2. Abra `preparar.ipynb`, elija el kernel del entorno del curso y ejecute sus dos celdas.

Descarga unos 1,5 GB: `torch` y `transformers` (unos 150 MB en Windows o en un Mac con procesador Apple) y los tres modelos (1,3 GB). Debe terminar con «✓ Preparación completa».

- **Mac con procesador Intel:** no hay `torch` para Python 3.13. Use el respaldo en Google Colab.
- **Linux:** `pip` instala por defecto la versión de `torch` con los componentes para tarjetas NVIDIA, de varios GB. Antes de `preparar.ipynb`, instale la versión para CPU desde una terminal con el entorno activado:
  `python -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu`

## El LLM: tres vías

El notebook elige solo la primera vía disponible y siempre dice cuál usa.
- **API:** cree un archivo `.env` en la carpeta del curso, fuera de esta carpeta, con la línea `ANTHROPIC_API_KEY=su-clave` (o `OPENAI_API_KEY`, o `GEMINI_API_KEY`). La clave nunca se imprime ni se guarda en el notebook. Las dos corridas de la clase cuestan menos de un centavo de dólar con Claude Haiku 5.5.
- **Local:** Ollama con un modelo que ve imágenes, por ejemplo `ollama pull qwen2.5vl:3b` (unos 3 GB).
- **Grabado:** sin clave ni Ollama, el notebook usa respuestas reales de Claude Haiku 5.5, grabadas el 28-oct-2026, para imágenes de 112, 224 y 448 píxeles.

## Archivos

| Archivo o carpeta | Para qué sirve |
| :--- | :--- |
| `lab_4B_modelos_preentrenados.ipynb` | El laboratorio |
| `preparar.ipynb` | Instala las librerías y descarga los modelos, antes de la clase |
| `imagenes/capsulas/` | 32 cápsulas, una carpeta por clase, y `origen.csv` con la foto de VisA de cada una |
| `imagenes/fotos/` | Las tres fotos del 4A para contar, con `referencias.json` (el centro de cada cápsula) |
| `mis_imagenes/` | Donde van sus imágenes para el trabajo independiente TI-2, una carpeta por clase |
| `grabaciones/` | Las respuestas grabadas del LLM |
| `reconocimiento.py` | CLIP, el LLM, los detectores, la comparación y el CSV |
| `figuras.py` | Galerías, matrices de confusión y cajas |
| `cliente_llm.py` | El cliente común del LLM, con imágenes |
| `inspeccion.py` | El pipeline del 4A, para comparar conteos |
| `presentacion.py`, `entorno.py`, `requirements.txt` | Apoyo y preparación del entorno |
| `LICENCIA_IMAGENES.md` | Origen y licencia de las imágenes y de los modelos |

## Sus propias imágenes (trabajo independiente TI-2)

La sección 7 acepta otras imágenes y otras clases: cree una carpeta por clase dentro de `mis_imagenes/`, copie allí las imágenes y escriba una frase por clase en la celda ✏️. Las instrucciones están en `mis_imagenes/LEEME.md`. **Sin personas, documentos con datos personales ni información confidencial.**

## Respaldo: Google Colab

Suba el notebook a Colab y, a la carpeta `/content`, el mismo `lab_4B_modelos_preentrenados.zip` que le entregó el docente; luego ejecute la primera celda. Colab ya trae `torch` y `transformers`, y los modelos se descargan la primera vez que se usan. Para la vía API, guarde la clave en los **Secrets** de Colab con el nombre `ANTHROPIC_API_KEY`.

## Entrega

El notebook ejecutado, con sus salidas y las celdas ✏️ completas, y el archivo `resultados_4B.csv`, que se crea en la sección 5. Uno por pareja, al inicio de la semana 3 del curso. Los criterios de evaluación están en la sección 8 del notebook.
