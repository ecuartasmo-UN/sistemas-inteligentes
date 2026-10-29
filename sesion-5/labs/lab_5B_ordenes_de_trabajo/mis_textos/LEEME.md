# Sus textos (trabajo independiente TI-2)

La sección 9.1 del notebook compara las tres arquitecturas, y opcionalmente el LLM, con textos de su trabajo, sin tocar el código.

## El formato

Un archivo CSV en esta carpeta, por ejemplo `mis_textos/mis_textos.csv`, con dos columnas y sus nombres en la primera fila:

| texto | clase |
| :--- | :--- |
| Solicito un certificado laboral para un trámite bancario | talento humano |
| La impresora de la oficina de mantenimiento no imprime | sistemas |

- **De 2 a 6 clases**, que usted define. El TI-2 pide 3 o 4.
- **De 30 a 60 textos de una o dos líneas, al menos 8 por clase.** Con 15 o más por clase, la comparación con 10 ejemplos usa 10; con menos, usa los que haya.
- **La prueba.** El notebook reserva el último tercio de los textos de cada clase, en el orden del archivo. Si prefiere elegirlos usted, agregue una tercera columna, `conjunto`, y escriba `prueba` en esos textos y `entrenamiento` en los demás.
- `ejemplo.csv` tiene 36 solicitudes internas ficticias de MantenIA, en tres clases. Úselo como modelo, o para probar la sección antes de escribir los suyos.

## Cómo crearlo

1. En Excel o en Google Sheets, escriba `texto` en A1 y `clase` en B1, y un texto por fila debajo.
2. Guárdelo en esta carpeta como **CSV UTF-8 (delimitado por comas)**. El notebook también lee el CSV que Excel en español guarda con punto y coma.
3. En la sección 9.1 del notebook, escriba su nombre en `RUTA_MIS_TEXTOS` (por ejemplo `"mis_textos/mis_textos.csv"`) y ejecute la celda.

## Sin datos personales

Los textos **no deben tener datos personales** (nombres, documentos, teléfonos, correos, direcciones) **ni información confidencial** de su organización. Si se basa en textos reales, reescríbalos con datos inventados. Con la vía API, cada texto que envíe al LLM sale de su computador hacia los servidores del proveedor; con la vía local, no. Sus archivos de esta carpeta no se incluyen en la entrega del laboratorio: van en el TI-2.
