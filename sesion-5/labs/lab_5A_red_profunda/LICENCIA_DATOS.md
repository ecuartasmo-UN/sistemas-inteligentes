# Datos del Laboratorio 5A: origen y licencia

## `datos/ai4i2020.csv`: AI4I 2020 Predictive Maintenance Dataset

- **Autoría:** Matzka, S. (2020). *Explainable artificial intelligence for predictive maintenance applications*. Third International Conference on Artificial Intelligence for Industries (AI4I 2020), IEEE, 69–74. <https://doi.org/10.1109/AI4I49448.2020.00023>
- **Fuente:** UCI Machine Learning Repository, conjunto 601. <https://doi.org/10.24432/C5HS5C>. Descargado del archivo oficial de UCI el 29 de octubre de 2026, sin cuenta ni formulario.
- **Licencia:** [Creative Commons Atribución 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.es).
- **Cambios:** ninguno. El archivo se distribuye tal como viene en el .zip de UCI (522 KB, 10 000 filas).
- **Qué es:** UCI lo describe como «a synthetic dataset that reflects real predictive maintenance data encountered in industry». Es **sintético**: no viene de una máquina real.

## Columnas

| Columna | Qué es | Uso en el laboratorio |
| :--- | :--- | :--- |
| `UDI` | Número de fila | No se usa |
| `Product ID` | Código de la pieza, con su tipo | No se usa |
| `Type` | Calidad del producto: L, M o H | Entrada, como tres columnas de 0 y 1 |
| `Air temperature [K]`, `Process temperature [K]` | Temperaturas en kelvin | Entradas |
| `Rotational speed [rpm]` | Velocidad de giro | Entrada |
| `Torque [Nm]` | Torque | Entrada |
| `Tool wear [min]` | Desgaste de la herramienta, en minutos de uso | Entrada |
| `Machine failure` | 1 si la máquina falló | La respuesta: 339 fallas en 10 000 registros |
| `TWF`, `HDF`, `PWF`, `OSF`, `RNF` | Modo de falla: desgaste, disipación de calor, potencia, sobreesfuerzo y aleatoria | No se usan: contienen la respuesta |

MantenIA y su máquina de fresado son ficticias.
