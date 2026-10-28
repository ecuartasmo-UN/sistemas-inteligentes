# Laboratorio 4A · Procesamiento y análisis clásico de imágenes

**Sistemas Inteligentes · Sesión 4 · Especialización en Inteligencia Artificial · UNAL Manizales**

Una estación de inspección cuenta cápsulas blandas en fotos de cada lote, y cuenta mal. Usted ajusta su pipeline clásico, etapa por etapa, con cada imagen intermedia a la vista:
- el canal, elegido con el histograma;
- el umbral;
- el filtrado y la morfología;
- la separación de cápsulas que se tocan;
- la medición.

Valida cada configuración contra un conteo hecho a mano, cápsula por cápsula, y la pone a prueba con una lámpara mal ubicada.

El notebook es autocontenido: toda la explicación está dentro de él. Se trabaja en parejas, 60 minutos en clase y hasta 30 en casa. **No se escribe código:** se cambian valores en las celdas marcadas con ✏️. No usa ningún LLM ni necesita claves.

## Antes de la clase

La primera celda del notebook instala OpenCV, scikit-image y SciPy, unos 95 MB. **Ejecútela en casa antes de la sesión** para no depender de la red del salón: abra el notebook, elija el kernel del entorno del curso y ejecute solo la primera celda. Debe terminar con «✓ Todos los paquetes del laboratorio están instalados» o «✓ Paquetes instalados».

## Cómo abrirlo (VS Code, entorno por defecto del curso)

1. Copie esta carpeta dentro de la carpeta del curso (la que tiene el entorno `.venv`) y abra la carpeta del curso en VS Code: **Archivo › Abrir carpeta**.
2. Abra `lab_4A_pipeline_clasico.ipynb` y elija el kernel del entorno del curso.
3. Ejecute las celdas en orden.

## Archivos

| Archivo o carpeta | Para qué sirve |
| :--- | :--- |
| `lab_4A_pipeline_clasico.ipynb` | El laboratorio |
| `imagenes/` | Las fotos de cápsulas, el patrón de calibración y `referencias.json`, con el centro de cada cápsula |
| `mis_fotos/` | Donde van sus fotos para el trabajo independiente TI-1 |
| `inspeccion.py` | El pipeline: etapas, comparación con la referencia, lámpara simulada, medición y bitácora |
| `vista.py` | Las figuras: etapas, píxeles, histogramas, cuadrícula, regiones y medidas |
| `presentacion.py`, `entorno.py`, `requirements.txt` | Apoyo y preparación del entorno |
| `LICENCIA_IMAGENES.md` | Origen y licencia de cada imagen |

## Sus propias fotos (trabajo independiente TI-1)

La sección 10 acepta cualquier foto: cópiela en `mis_fotos/` y escriba su ruta en la celda ✏️. Funciona mejor con los objetos sobre un fondo liso que contraste con ellos. **Sin personas, documentos con datos personales ni información confidencial.**

## Respaldo: Google Colab

Suba el notebook a Colab y, a la carpeta `/content`, el mismo `lab_4A_pipeline_clasico.zip` que le entregó el docente; luego ejecute la primera celda. Colab ya trae OpenCV y scikit-image.

## Entrega

El notebook ejecutado, con sus salidas y las celdas ✏️ completas, y el archivo `resultados_4A.csv`. Ese archivo es la bitácora: se escribe solo, con cada corrida, y reiniciar el kernel no lo borra. Uno por pareja, al inicio de la semana 3 del curso. Los criterios de evaluación están en la sección 12 del notebook.
