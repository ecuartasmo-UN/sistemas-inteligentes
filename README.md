# Sistemas Inteligentes · laboratorios

**Especialización en Inteligencia Artificial · Universidad Nacional de Colombia, sede Manizales**

Material del curso *Sistemas Inteligentes*: el contenido del curso, las diapositivas de cada sesión y los laboratorios.

## Ver las diapositivas

Las diapositivas se abren en el navegador desde **https://ecuartasmo-un.github.io/sistemas-inteligentes/**:

- [Sesión 1](https://ecuartasmo-un.github.io/sistemas-inteligentes/sesion-1/): IA, sistemas expertos, agentes y sistemas multiagente
- [Sesión 2](https://ecuartasmo-un.github.io/sistemas-inteligentes/sesion-2/): planificación automática, LLMs y planificación, plan.md
- [Sesión 3](https://ecuartasmo-un.github.io/sistemas-inteligentes/sesion-3/): razonamiento automático: solvers, restricciones, lógica y razonamiento en LLMs
- [Sesión 4](https://ecuartasmo-un.github.io/sistemas-inteligentes/sesion-4/): visión por computador: procesamiento digital de imágenes, CLIP, YOLO y LLMs multimodales
- [Sesión 5](https://ecuartasmo-un.github.io/sistemas-inteligentes/sesion-5/): redes neuronales y aprendizaje profundo: de la neurona a la red profunda, la arquitectura transformer y los LLMs
- [Sesión 6](https://ecuartasmo-un.github.io/sistemas-inteligentes/sesion-6/): aprendizaje de máquina: árboles de decisión, ensambles, el costo del error y aprendizaje por refuerzo

También funcionan sin internet: descargue el repositorio y abra `sesion-N/index.html` con doble clic. Use las flechas del teclado para avanzar.

## Contenido

| Carpeta o archivo | Qué contiene |
| :--- | :--- |
| [`Sistemas_Inteligentes_contenido_actualizado_2026_v4.md`](Sistemas_Inteligentes_contenido_actualizado_2026_v4.md) | Contenido del curso: unidades, sesiones, laboratorios, evaluación y referencias |
| [`entorno/`](entorno/) | Guía de instalación del entorno del curso (`INSTALACION.md`), las librerías (`requirements.txt`) y un notebook que comprueba que todo funciona (`verificar_entorno.ipynb`). Se usa en la fase previa, antes de la sesión 1 |
| [`sesion-1/`](sesion-1/) | Diapositivas de la sesión 1 y su trabajo independiente |
| [`sesion-2/`](sesion-2/) | Diapositivas de la sesión 2 (con el club de lectura), la lectura del club, trabajo independiente, plantilla del plan.md y ejemplo en PDDL. La lectura es Kambhampati et al. (2024), *Position: LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks*, ICML 2024, versión de [arXiv:2402.01817](https://arxiv.org/abs/2402.01817) con licencia CC BY 4.0 |
| [`sesion-2/labs/lab_2A_planificar_pddl/`](sesion-2/labs/lab_2A_planificar_pddl/) | Laboratorio 2A · Planificar una operación en PDDL. No usa LLM |
| [`sesion-2/labs/lab_2B_llm_modulo/`](sesion-2/labs/lab_2B_llm_modulo/) | Laboratorio 2B · LLM-Modulo en práctica |
| [`sesion-2/labs/lab_2C_plan_md/`](sesion-2/labs/lab_2C_plan_md/) | Laboratorio 2C · Escribir, revisar y ejecutar un plan.md |
| [`sesion-3/`](sesion-3/) | Diapositivas de la sesión 3 (con el club de lectura), trabajo independiente, ejemplos de CP-SAT y Z3, y [`prompting.docx`](sesion-3/prompting.docx): del prompt al plan.md con Claude Code, y la anatomía de un buen prompt para Claude 5.5 |
| [`sesion-3/labs/lab_3A_vibe_coding.md`](sesion-3/labs/lab_3A_vibe_coding.md) | Laboratorio 3A · Vibe coding: la logística de una empresa de aseo. Un archivo con el problema y el prompt para su asistente de IA |
| [`sesion-3/labs/lab_3B_politicas_z3/`](sesion-3/labs/lab_3B_politicas_z3/) | Laboratorio 3B · Verificar una política de negocio con Z3 |
| [`sesion-4/`](sesion-4/) | Diapositivas de la sesión 4 (con el club de lectura), trabajo independiente y ejemplos con OpenCV. La charla inicial rediseña la clase «Procesamiento Digital de Imágenes» (2007); con la flecha ↓ se ve el contenido completo del original |
| [`sesion-4/labs/lab_4A_pipeline_clasico/`](sesion-4/labs/lab_4A_pipeline_clasico/) | Laboratorio 4A · Procesamiento y análisis clásico de imágenes. No usa LLM |
| [`sesion-4/labs/lab_4B_modelos_preentrenados/`](sesion-4/labs/lab_4B_modelos_preentrenados/) | Laboratorio 4B · Reconocimiento con modelos preentrenados: CLIP, un LLM multimodal y dos detectores. **Antes de la clase**, ejecute en casa su `preparar.ipynb`, que descarga unos 1,5 GB |
| [`sesion-5/`](sesion-5/) | Diapositivas de la sesión 5 (con el club de lectura), trabajo independiente y los scripts que producen las gráficas con datos reales |
| [`sesion-5/labs/lab_5A_red_profunda/`](sesion-5/labs/lab_5A_red_profunda/) | Laboratorio 5A · Del perceptrón a la red profunda: una red en PyTorch que predice la falla de una máquina. No usa LLM. **Antes de la clase**, ejecute en casa su primera celda |
| [`sesion-5/labs/lab_5B_ordenes_de_trabajo/`](sesion-5/labs/lab_5B_ordenes_de_trabajo/) | Laboratorio 5B · Leer órdenes de trabajo con un transformer: bolsa de palabras, red recurrente, transformer preentrenado y un LLM. **Antes de la clase**, ejecute en casa su `preparar.ipynb`, que descarga unos 220 MB |
| [`sesion-6/`](sesion-6/) | Diapositivas de la sesión 6 (con el club de lectura), trabajo independiente y los scripts que producen las gráficas con datos reales |
| [`sesion-6/labs/lab_6A_del_dato_al_conocimiento/`](sesion-6/labs/lab_6A_del_dato_al_conocimiento/) | Laboratorio 6A · Del dato al conocimiento: árboles de decisión con el Titanic, ensambles, las reglas de un LLM y el costo del error con el German Credit. **Antes de la clase**, ejecute en casa su primera celda, que instala `scikit-learn` (unos 40 MB) |
| [`sesion-6/labs/lab_6B_refuerzo_y_specification_gaming/`](sesion-6/labs/lab_6B_refuerzo_y_specification_gaming/) | Laboratorio 6B · Aprendizaje por refuerzo y *specification gaming*: la iteración de valores y Q-learning en el mundo de 4×3, y la carrera de botes. No usa LLM |

Cada laboratorio es un notebook de Jupyter autocontenido: toda la explicación está dentro del notebook. Se trabajan en parejas, en VS Code, en su propio computador. Cada uno tiene su propio `README.md` con el tiempo, el modo de trabajo y lo que se entrega. La excepción es el 3A: un solo archivo Markdown con el problema y el prompt, que se usa con su asistente de IA (Claude o Gemini), en VS Code o en el navegador.

## Cómo empezar

1. **Descargue el repositorio.** Con Git: `git clone https://github.com/ecuartasmo-UN/sistemas-inteligentes.git`. Sin Git: botón **Code › Download ZIP** y descomprímalo. La carpeta que obtiene es la **carpeta del curso**.
2. **Instale el entorno** siguiendo [`entorno/INSTALACION.md`](entorno/INSTALACION.md): Python 3.13, VS Code con las extensiones de Python y Jupyter, y un entorno virtual `.venv` en la carpeta del curso.
3. **Compruebe la instalación** abriendo `entorno/verificar_entorno.ipynb` en VS Code, con el kernel `.venv`, y ejecutándolo completo.
4. **Abra el laboratorio** de la sesión, en `sesion-N/labs/`, y ejecute sus celdas en orden.

## Acceso a un modelo de lenguaje (2B, 2C, 3B, 4B, 5B y 6A)

Los laboratorios que usan un LLM eligen solos la primera vía disponible:

1. **Una clave de API**, en un archivo `.env` en la carpeta del curso, con una sola línea, sin espacios ni comillas: `ANTHROPIC_API_KEY=su-clave`.
2. **Un modelo local** con Ollama (`ollama pull qwen3:4b-instruct`, unos 2,5 GB), sin clave ni costo; sirve para el 2B, el 2C, el 3B, el 5B y el 6A. El 4B necesita un modelo que vea imágenes, por ejemplo `ollama pull qwen2.5vl:3b` (unos 3 GB).
3. **Respuestas grabadas** de una corrida real: el notebook corre completo sin clave y sin internet, aunque no puede probar instrucciones nuevas.

Para forzar una vía, cambie `PROVEEDOR` en la celda ✏️ de configuración del LLM, en la sección 0 del notebook; por ejemplo, `PROVEEDOR = "grabado"`.

**Nunca suba su archivo `.env` ni escriba la clave en un notebook.** El `.gitignore` de este repositorio excluye `.env` y `.venv`.

## Respaldo: Google Colab

Si no puede instalar el entorno, cada laboratorio también corre en Google Colab: descargue el `.zip` del laboratorio desde la sección **Releases** de este repositorio, súbalo a `/content` y siga las instrucciones del desplegable «Respaldo: trabajar en Google Colab» del notebook.

## Créditos

Las imágenes de las diapositivas y de los notebooks son de dominio público, tienen licencia Creative Commons, son diagramas propios o vienen del material original del docente; cada una lleva su crédito junto a la imagen, y las pocas figuras tomadas de otras obras citan su fuente al pie. Algunas imágenes con derechos reservados de la sesión 2 no se incluyen aquí: en su lugar aparece un recuadro con su descripción, y el crédito enlaza a la fuente original. MantenIA, la empresa de los ejemplos, es ficticia.
