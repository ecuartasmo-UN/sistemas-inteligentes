# Sus casos (trabajo independiente TI-1)

La sección 7.4 del notebook induce un árbol con sus casos y lo compara con las reglas de su sistema experto de la Sesión 1, sin tocar el código.

## El formato

Un archivo CSV en esta carpeta, por ejemplo `mis_casos/mis_casos.csv`. La primera fila lleva los nombres de las columnas: de 3 a 6 columnas de datos y una columna `conclusion` con la decisión que daría un experto.

| vibracion | ruido | temp_rodamiento | desalineacion_visible | conclusion |
| :--- | :--- | :--- | :--- | :--- |
| alta | metálico | 88 | no | cambiar rodamiento |
| baja | normal | 55 | no | sin falla |

- **Valores:** números (con punto o coma decimal) o categorías cortas, como `alta`, `media` y `baja`. Una columna con todos sus valores numéricos se trata como número; si no, como categoría, con hasta 12 valores distintos.
- **De 40 a 60 casos,** uno por fila, sin celdas vacías. Cada conclusión necesita al menos 2 casos, y mejor 5 o más: con menos de 5, la validación cruzada usa menos partes y el notebook lo avisa.
- **Las excepciones importan.** Si escribe la conclusión aplicando sus reglas al pie de la letra, el árbol solo las copiará. Incluya casos frontera y los casos en que un experto no seguiría la regla.
- `ejemplo.csv` tiene 40 casos inventados del diagnóstico de MantenIA. Úselo como modelo, o para probar la sección antes de escribir los suyos.

## Cómo crearlo

1. En Excel o en Google Sheets, escriba los nombres de las columnas en la fila 1, con `conclusion` en la última, y un caso por fila debajo.
2. Guárdelo en esta carpeta como **CSV UTF-8 (delimitado por comas)**. El notebook también lee el CSV que Excel en español guarda con punto y coma.
3. En la sección 7.4 del notebook, escriba en `RUTA_MIS_CASOS` la ruta de su archivo, con la carpeta y entre comillas (por ejemplo `"mis_casos/mis_casos.csv"`), y ejecute las tres celdas. Un archivo de Excel (.xlsx) no sirve: guárdelo antes como CSV.

## Sin datos personales

Los casos **no deben tener datos personales** (nombres, documentos, teléfonos, correos, direcciones) **ni información confidencial** de su organización. Si parte de casos reales, cámbieles los datos que identifiquen a una persona, un cliente o un proveedor. Sus archivos de esta carpeta no se incluyen en la entrega del laboratorio, y sus resultados no se anotan en `resultados_6A.csv`: van en el TI-1. Los primeros casos sí quedan a la vista en el notebook que entrega.
