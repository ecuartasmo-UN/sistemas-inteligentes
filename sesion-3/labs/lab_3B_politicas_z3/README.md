# Laboratorio 3B · Verificar una política de negocio con Z3

**Sistemas Inteligentes · Sesión 3 · Especialización en Inteligencia Artificial · UNAL Manizales**

La política de compras de repuestos de MantenIA se escribe como una tabla de reglas y el solver Z3 la verifica: busca contradicciones, lagunas y casos límite, y muestra cada problema como un contraejemplo. Después, un LLM traduce la política del lenguaje natural a la tabla y Z3 verifica esa traducción; se compara con un LLM que razona solo sobre la misma política.

El notebook es autocontenido: toda la explicación está dentro de él. Se trabaja en parejas, 60 minutos en clase y hasta 30 en casa. **No se escribe código:** se editan tablas.

## Cómo abrirlo (VS Code, entorno por defecto del curso)

1. Copie esta carpeta dentro de la carpeta del curso (la que tiene el entorno `.venv`) y abra la carpeta del curso en VS Code: **Archivo › Abrir carpeta**.
2. Abra `lab_3B_politicas_z3.ipynb` y elija el kernel del entorno del curso.
3. Ejecute las celdas en orden. La primera instala lo que falte de `requirements.txt`, incluido `z3-solver`.

## Acceso a un LLM (solo en la sección 5)

El notebook usa la primera vía disponible:

1. **API.** Cree un archivo `.env` en esta carpeta, o en una carpeta superior, con una sola línea, sin espacios ni comillas: `ANTHROPIC_API_KEY=sk-ant-...`. También sirven `OPENAI_API_KEY` o `GEMINI_API_KEY`. El LLM por defecto es Claude Haiku 5.5, con su modo de razonamiento desactivado. El laboratorio hace 2 llamadas (hasta 4 si la traducción necesita correcciones) y cuesta cerca de una décima de centavo de dólar.
2. **Modelo local.** Con Ollama instalado y abierto, y el modelo descargado (`ollama pull qwen3:4b-instruct`), no necesita clave ni tiene costo. Es un modelo pequeño: sirve para comparar, no para auditar.
3. **Respuestas grabadas.** Si no hay ninguna de las anteriores, el notebook reproduce respuestas reales de Claude Haiku 5.5, grabadas el 26 de octubre de 2026. Corre completo, pero no puede probar instrucciones nuevas.

**Nunca** escriba la clave dentro del notebook y **no entregue** el archivo `.env`.

## Archivos

| Archivo o carpeta | Para qué sirve |
| :--- | :--- |
| `lab_3B_politicas_z3.ipynb` | El laboratorio |
| `politicas/` | El texto de la política de compras: la original (`compras_mantenia.md`) y la ampliada (`compras_ampliada.md`), que lee el LLM |
| `politicas.py` | Lee las tablas de campos y reglas, las traduce a Z3, hace las verificaciones, dibuja el mapa de casos, le pide al LLM la traducción o la auditoría y exporta el CSV |
| `cliente_llm.py` | Acceso al LLM por cualquiera de las tres vías, con registro de tokens, tiempo y costo, y un presupuesto |
| `grabaciones/` | Las respuestas grabadas de Claude Haiku 5.5 |
| `presentacion.py`, `entorno.py`, `requirements.txt` | Apoyo y preparación del entorno |

## Su propia política (trabajo independiente TI-2)

La sección 6.2 sirve para cualquier política, no solo la de MantenIA. Los campos pueden ser de tres tipos: **número** (con su mínimo y su máximo, por ejemplo `1 a 30`), **categoría** (con sus valores separados por comas; para sí o no, use `sí, no`) y una sola **decisión** (los valores posibles de lo que decide la política). Las reglas usan `<`, `<=`, `>`, `>=`, `=` y `≠`, unidas con « y ». Anonimice los datos: no use nombres ni cifras confidenciales.

## Respaldo: Google Colab

Suba el notebook a Colab y, a la carpeta `/content`, el mismo `lab_3B_politicas_z3.zip` que le entregó el docente; luego ejecute la primera celda. La clave se guarda en los **Secrets** de Colab con el nombre `ANTHROPIC_API_KEY`. En Colab no funciona la vía local con Ollama.

## Entrega

El notebook ejecutado, con sus salidas y las celdas ✏️ completas, y el archivo `resultados_3B.csv`. Uno por pareja, al inicio de la semana 3 del curso. Los criterios de evaluación están en la sección 7 del notebook.
