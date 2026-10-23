# Laboratorio 2B · LLM-Modulo en práctica

**Sistemas Inteligentes · Sesión 2 · Especialización en Inteligencia Artificial · UNAL Manizales**

Sobre las órdenes de MantenIA del Laboratorio 2A se comparan tres estrategias: el LLM planifica directamente; el LLM traduce a PDDL y resuelve el planificador; y un ciclo generar-verificar en el que el validador devuelve los errores al LLM. Se miden validez, iteraciones y costo.

El notebook es autocontenido: toda la explicación está dentro de él. Se trabaja en parejas, 35 minutos en clase y cerca de una hora en casa.

## Cómo abrirlo (VS Code, entorno por defecto del curso)

1. Copie esta carpeta dentro de la carpeta del curso (la que tiene el entorno `.venv`) y abra la carpeta del curso en VS Code: **Archivo › Abrir carpeta**.
2. Abra `lab_2B_llm_modulo.ipynb` y elija el kernel del entorno del curso.
3. Ejecute las celdas en orden. La primera instala lo que falte de `requirements.txt`.

## Acceso a un LLM

El notebook usa la primera vía disponible:

1. **API.** Cree un archivo `.env` en esta carpeta, o en una carpeta superior, con una sola línea, sin espacios ni comillas: `ANTHROPIC_API_KEY=sk-ant-...`. También sirven `OPENAI_API_KEY` o `GEMINI_API_KEY`. El LLM por defecto es Claude Haiku 5.5, con su modo de razonamiento desactivado. El laboratorio completo hace al menos 14 llamadas (más si el LLM necesita críticas) y cuesta menos de un centavo de dólar.
2. **Modelo local.** Con Ollama instalado y abierto, y el modelo descargado (`ollama pull qwen3:4b-instruct`), no necesita clave ni tiene costo. En un portátil sin GPU es más lento.
3. **Respuestas grabadas.** Si no hay ninguna de las anteriores, el notebook reproduce respuestas reales grabadas de Claude Haiku 5.5. Corre completo, pero no puede probar instrucciones nuevas.

**Nunca** escriba la clave dentro del notebook y **no entregue** el archivo `.env`.

## Archivos

| Archivo o carpeta | Para qué sirve |
| :--- | :--- |
| `lab_2B_llm_modulo.ipynb` | El laboratorio |
| `pddl/` | Dominio, cinco instancias (OT-512, OT-518, OT-530, OT-512 sin solución, OT-512 «misterio»), la clave de la versión misterio y el dominio mal traducido |
| `ordenes/` | Las órdenes escritas que traduce la estrategia 2 |
| `estrategias_2b.py` | Las tres estrategias, el juicio con el validador y la exportación al CSV |
| `cliente_llm.py` | Acceso al LLM por cualquiera de las tres vías, con registro de tokens, tiempo y costo, y un presupuesto |
| `grabaciones/` | Las respuestas grabadas: las de Claude Haiku 5.5 y, en `qwen3-4b-instruct/`, las del experimento opcional de la sección 9.1 |
| `utilidades_pddl.py`, `presentacion.py`, `entorno.py`, `requirements.txt` | Apoyo y preparación del entorno |

## Respaldo: Google Colab

Suba el notebook a Colab y, a la carpeta `/content`, el mismo `lab_2B_llm_modulo.zip` que le entregó el docente; luego ejecute la primera celda. La clave se guarda en los **Secrets** de Colab con el nombre `ANTHROPIC_API_KEY`. En Colab no funciona la vía local con Ollama.

## Entrega

El notebook ejecutado, con sus salidas y las celdas ✏️ completas, y el archivo `resultados_2B.csv`. Uno por pareja, al inicio de la semana 2 del curso. Los criterios de evaluación están en la sección 9 del notebook.
