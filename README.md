# Sistemas Inteligentes · laboratorios

**Especialización en Inteligencia Artificial · Universidad Nacional de Colombia, sede Manizales**

Laboratorios del curso *Sistemas Inteligentes*. Cada laboratorio es un notebook de Jupyter autocontenido: toda la explicación está dentro del notebook. Se trabajan en parejas, en VS Code, en su propio computador.

## Contenido

| Carpeta | Qué contiene |
| :--- | :--- |
| [`entorno/`](entorno/) | Guía de instalación del entorno del curso (`INSTALACION.md`), las librerías (`requirements.txt`) y un notebook que comprueba que todo funciona (`verificar_entorno.ipynb`). Se usa en la fase previa, antes de la sesión 1 |
| [`sesion-2/lab_2A_planificar_pddl/`](sesion-2/lab_2A_planificar_pddl/) | Laboratorio 2A · Planificar una operación en PDDL. No usa LLM |
| [`sesion-2/lab_2B_llm_modulo/`](sesion-2/lab_2B_llm_modulo/) | Laboratorio 2B · LLM-Modulo en práctica |
| [`sesion-2/lab_2C_plan_md/`](sesion-2/lab_2C_plan_md/) | Laboratorio 2C · Escribir, revisar y ejecutar un plan.md |

Cada laboratorio tiene su propio `README.md` con el tiempo, el modo de trabajo y lo que se entrega.

## Cómo empezar

1. **Descargue el repositorio.** Con Git: `git clone https://github.com/ecuartasmo-UN/sistemas-inteligentes.git`. Sin Git: botón **Code › Download ZIP** y descomprímalo. La carpeta que obtiene es la **carpeta del curso**.
2. **Instale el entorno** siguiendo [`entorno/INSTALACION.md`](entorno/INSTALACION.md): Python 3.13, VS Code con las extensiones de Python y Jupyter, y un entorno virtual `.venv` en la carpeta del curso.
3. **Compruebe la instalación** abriendo `entorno/verificar_entorno.ipynb` en VS Code, con el kernel `.venv`, y ejecutándolo completo.
4. **Abra el laboratorio** de la sesión y ejecute sus celdas en orden.

## Acceso a un modelo de lenguaje (2B y 2C)

Los laboratorios que usan un LLM eligen solos la primera vía disponible:

1. **Una clave de API**, en un archivo `.env` en la carpeta del curso, con una sola línea, sin espacios ni comillas: `ANTHROPIC_API_KEY=su-clave`.
2. **Un modelo local** con Ollama (`ollama pull qwen3:4b-instruct`), sin clave ni costo.
3. **Respuestas grabadas** de una corrida real: el notebook corre completo sin clave y sin internet, aunque no puede probar instrucciones nuevas.

Para forzar una vía, cambie `PROVEEDOR` en la celda ✏️ de la sección 0.1 del notebook; por ejemplo, `PROVEEDOR = "grabado"`.

**Nunca suba su archivo `.env` ni escriba la clave en un notebook.** El `.gitignore` de este repositorio excluye `.env` y `.venv`.

## Respaldo: Google Colab

Si no puede instalar el entorno, cada laboratorio también corre en Google Colab: descargue el `.zip` del laboratorio desde la sección **Releases** de este repositorio, súbalo a `/content` y siga las instrucciones del desplegable «Respaldo: trabajar en Google Colab» del notebook.

## Créditos

Las imágenes de los notebooks son de dominio público, tienen licencia Creative Commons o son diagramas propios; cada una lleva su crédito junto a la imagen. MantenIA, la empresa de los ejemplos, es ficticia.
