# Laboratorio 2C · Escribir, revisar y ejecutar un plan.md

**Sistemas Inteligentes · Sesión 2 · Especialización en Inteligencia Artificial · UNAL Manizales**

Un LLM redacta el plan.md de una intervención de MantenIA, la OT-523. La pareja lo revisa con la lista de chequeo J.6, lo corrige y lo aprueba. En la ejecución simulada se inyecta una falla: la pareja la registra, replanifica, vuelve a aprobar y termina.

El notebook es autocontenido: toda la explicación está dentro de él. Se trabaja en parejas, 40 minutos en clase (secciones 0 a 7) y cerca de una hora en casa (secciones 8 a 10).

## Cómo abrirlo (VS Code, entorno por defecto del curso)

1. Copie esta carpeta dentro de la carpeta del curso (la que tiene el entorno `.venv`) y abra la carpeta del curso en VS Code: **Archivo › Abrir carpeta**.
2. Abra `lab_2C_plan_md.ipynb` y elija el kernel del entorno del curso.
3. Ejecute las celdas en orden. En las secciones 5 y 8 se edita el archivo `planes/plan_OT-523.md` desde el Explorador de VS Code.

Todo el trabajo queda en la carpeta `planes/`: el plan, sus versiones, las aprobaciones y la ejecución. Si cierra VS Code o reinicia el kernel, ejecute de nuevo la sección 0 y siga donde iba; volver a ejecutar una celda no borra su trabajo.

## Acceso a un LLM

Igual que en el Laboratorio 2B:
- un archivo `.env` con `ANTHROPIC_API_KEY=sk-ant-...`, en una sola línea, sin espacios ni comillas;
- un modelo local con Ollama;
- las respuestas grabadas.

Con las respuestas grabadas, el borrador del plan es el de una corrida real de Claude Haiku 5.5. La replanificación grabada, en cambio, corresponde al plan de referencia del docente, en el escenario de la pareja: sirve como guía, y la pareja edita su propio plan a mano.

## Archivos

| Archivo o carpeta | Para qué sirve |
| :--- | :--- |
| `lab_2C_plan_md.ipynb` | El laboratorio |
| `documentos/` | Los seis documentos ficticios de la OT-523 |
| `plantilla_plan.md` | La plantilla del plan.md, con la lista de chequeo J.6 |
| `ejemplos/plan_OT-512_J8.md` | Un plan.md correcto, después de una replanificación |
| `plan_md.py` | Versiones del plan, casillas, registro de avance y aprobación ligada a la versión |
| `revisor_plan.py` | Revisión automática de los aspectos mecánicos de la lista J.6 |
| `simulador_ot523.py` | Simulador de la intervención: lee cada paso del plan, lo ejecuta con su reloj y guarda la ejecución |
| `redaccion_2c.py`, `cliente_llm.py` | Instrucciones al LLM y acceso al LLM |
| `pddl/` | Modelo PDDL de la OT-523 para la sección opcional 9.3 |
| `grabaciones/` | Las respuestas grabadas: el borrador y la replanificación en los tres escenarios |

## Respaldo: Google Colab

Suba el notebook a Colab y, a la carpeta `/content`, el mismo `lab_2C_plan_md.zip` que le entregó el docente; luego ejecute la primera celda. El plan se edita con doble clic en el panel **Archivos** de Colab.

## Entrega

El notebook ejecutado y la carpeta `planes/`, comprimidos en un .zip, uno por pareja, al inicio de la semana 2 del curso. No incluya el archivo `.env`. Los criterios de evaluación están en la sección 10 del notebook.
