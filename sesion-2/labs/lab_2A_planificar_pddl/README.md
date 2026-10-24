# Laboratorio 2A · Planificar una operación en PDDL

**Sistemas Inteligentes · Sesión 2 · Especialización en Inteligencia Artificial · UNAL Manizales**

Formalizar en PDDL una orden de mantenimiento de MantenIA, resolverla con Unified Planning y Fast Downward, validar el plan y analizar cómo cambia al modificar metas y recursos.

El notebook es autocontenido: toda la explicación está dentro de él. Se trabaja en parejas, 35 minutos en clase y cerca de una hora en casa. No necesita ninguna clave ni conexión a un modelo de lenguaje.

## Cómo abrirlo (VS Code, entorno por defecto del curso)

1. Copie esta carpeta dentro de la carpeta del curso (la que tiene el entorno `.venv`) y abra la carpeta del curso en VS Code: **Archivo › Abrir carpeta**.
2. Abra `lab_2A_planificar_pddl.ipynb` y elija el kernel del entorno del curso (**Seleccionar kernel**, arriba a la derecha).
3. Ejecute las celdas en orden. La primera comprueba Python e instala lo que falte de `requirements.txt`.

Si todavía no tiene el entorno del curso, siga la guía `entorno/INSTALACION.md` del curso antes de empezar.

## Archivos

| Archivo | Para qué sirve |
| :--- | :--- |
| `lab_2A_planificar_pddl.ipynb` | El laboratorio |
| `pddl/mantenia_dominio.pddl`, `pddl/ot512.pddl` | El dominio de MantenIA y el problema de la orden OT-512 |
| `utilidades_pddl.py` | Leer, resolver, validar y trazar planes, con mensajes en español |
| `presentacion.py` | Mostrar planes, trazas y veredictos |
| `comprobaciones_2a.py` | Retroalimentación de los ejercicios (orienta; no califica) |
| `htn_2a.py` | Expansor jerárquico de la sección 8, que es opcional |
| `entorno.py`, `requirements.txt` | Preparación del entorno |

## Respaldo: Google Colab

Solo si no puede instalar el entorno: suba el notebook a [Colab](https://colab.research.google.com/) con **Archivo › Subir notebook**, suba a la carpeta `/content` el mismo `lab_2A_planificar_pddl.zip` que le entregó el docente y ejecute la primera celda. Ella descomprime la carpeta y continúa normalmente.

Para pruebas rápidas de PDDL sin instalar nada, también sirve el editor en línea [editor.planning.domains](https://editor.planning.domains/), que resuelve y valida en el navegador. No reemplaza el notebook: los ejercicios y sus comprobaciones están en él.

## Entrega

El notebook ejecutado, con sus salidas y los ejercicios ✏️ resueltos, uno por pareja, al inicio de la semana 2 del curso. Los criterios de evaluación están en la sección 9 del notebook.
