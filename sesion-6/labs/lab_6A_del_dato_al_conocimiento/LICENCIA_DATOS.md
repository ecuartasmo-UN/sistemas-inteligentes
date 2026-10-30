# Datos del Laboratorio 6A: origen y licencia

## `datos/titanic3.csv`: los pasajeros del Titanic

- **Fuente:** el conjunto titanic3 del Departamento de Bioestadística de la Universidad Vanderbilt (Frank E. Harrell Jr.), <https://hbiostat.org/data/>. Lo armó Thomas Cason, de la Universidad de Virginia, a partir de *Encyclopedia Titanica*, con los datos vigentes al 2 de agosto de 1999. Descargado de <https://hbiostat.org/data/repo/titanic3.csv> el 29 de octubre de 2026.
- **Condiciones de uso:** la página no declara una licencia formal. Dice: «Permission is granted to anyone wishing to use the data sets provided here», y pide la nota que sigue. *Data obtained from http://hbiostat.org/data courtesy of the Vanderbilt University Department of Biostatistics.*
- **Cambios:** se quitaron las columnas `name`, `ticket`, `cabin` y `home.dest`, que identifican a la persona o no se usan. Quedan 1309 pasajeros y 10 columnas; no incluye a la tripulación.

| Columna | Qué es | Uso en el laboratorio |
| :--- | :--- | :--- |
| `pclass` | Clase del pasaje: 1, 2 o 3 | Dato |
| `survived` | 1 si sobrevivió | La respuesta: 500 sobrevivientes |
| `sex` | `female` o `male` | Dato |
| `age` | Edad en años; vacía en 263 pasajeros | Dato |
| `sibsp`, `parch` | Hermanos o cónyuge, y padres o hijos, a bordo | Datos |
| `fare` | Tarifa, en libras de 1912 | Dato |
| `embarked` | Puerto: S (Southampton), C (Cherbourg) o Q (Queenstown) | Dato |
| `boat`, `body` | El bote salvavidas y el número del cuerpo recuperado | Solo en la sección 7.2: revelan la respuesta |

## `datos/credito_aleman.csv`: Statlog German Credit

- **Fuente:** Hofmann, H. (1994). *Statlog (German Credit Data)*. UCI Machine Learning Repository, conjunto 144. <https://doi.org/10.24432/C5NC77>. Descargado del archivo oficial de UCI el 29 de octubre de 2026.
- **Licencia:** [Creative Commons Atribución 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.es).
- **Cambios:** los códigos de `german.data` (`A11`, `A34`…) se tradujeron al español con la documentación del conjunto (`german.doc`), y se excluyeron dos variables: la 9, «estado civil y sexo», cuya codificación no permite recuperar el sexo, y la 20, «trabajador extranjero», que está codificada al revés (Fabris et ál., 2022). Quedan 1000 solicitudes, 18 datos y la columna `pagador`: 700 buenos y 300 malos.
- **Qué es:** solicitudes de crédito de un banco alemán, de 1973 a 1975, a las que se otorgó el crédito. Son anónimas.
- **La matriz de costos** viene en `german.doc`: clasificar como bueno a un mal pagador cuesta 5; clasificar como malo a uno bueno cuesta 1.

## `mis_casos/ejemplo.csv`

Cuarenta casos inventados para el curso: el diagnóstico de una bomba de MantenIA, la empresa ficticia del curso, con las variables de las reglas R1 a R4 de la Sesión 1. No vienen de ninguna organización real.

## `grabaciones/respuestas.json`

Dos respuestas reales de Claude Haiku 5.5 (Anthropic), obtenidas por API el 29 de octubre de 2026 con las instrucciones de las secciones 5 y 7.1.
