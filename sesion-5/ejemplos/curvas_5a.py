"""Memorizar o generalizar: curvas de aprendizaje sobre los datos del Laboratorio 5A (charla inicial).

Usa el AI4I 2020 Predictive Maintenance Dataset (UCI, CC BY 4.0): 10 000 registros de una
máquina, con la temperatura del aire y del proceso, la velocidad de giro, el torque, el desgaste
de la herramienta y el tipo de producto, y si la máquina falló.

Para que el sobreajuste se vea, entrena con solo 400 registros una red grande
(3 capas ocultas de 128 neuronas) durante 300 épocas, y la valida con otros 3000:
- sin regularización: la pérdida de entrenamiento sigue bajando y la de validación sube;
- con dropout del 30 %: las dos curvas quedan más cerca;
- la parada temprana se queda con la época de menor pérdida de validación.

Uso, desde esta carpeta:  python curvas_5a.py
Requiere torch y pandas. La primera vez descarga el conjunto (unos 500 KB) en datos/.
Escribe los números en salidas/curvas_5a.json; las diapositivas dibujan las curvas en SVG.
"""
import io
import urllib.request
import zipfile

import numpy as np
import pandas as pd
import torch
from torch import nn

from comun import DATOS, guardar_json

URL = "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"
COLUMNAS = ["Air temperature [K]", "Process temperature [K]", "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"]
EPOCAS, N_ENTRENAMIENTO, N_VALIDACION = 300, 400, 3000


def cargar() -> pd.DataFrame:
    archivo = DATOS / "ai4i2020.csv"
    if not archivo.exists():
        DATOS.mkdir(exist_ok=True)
        with urllib.request.urlopen(URL) as r, zipfile.ZipFile(io.BytesIO(r.read())) as z:
            archivo.write_bytes(z.read("ai4i2020.csv"))
    return pd.read_csv(archivo)


def entrenar(x_e, y_e, x_v, y_v, dropout: float) -> tuple[list, list]:
    torch.manual_seed(7)
    capas, ancho = [], x_e.shape[1]
    for _ in range(3):
        capas += [nn.Linear(ancho, 128), nn.ReLU(), nn.Dropout(dropout)]
        ancho = 128
    red = nn.Sequential(*capas, nn.Linear(ancho, 1))
    optimizador = torch.optim.Adam(red.parameters(), lr=1e-3)
    perdida = nn.BCEWithLogitsLoss()
    curva_e, curva_v = [], []
    for _ in range(EPOCAS):
        red.train()
        optimizador.zero_grad()
        p = perdida(red(x_e), y_e)
        p.backward()
        optimizador.step()
        red.eval()
        with torch.no_grad():
            curva_e.append(round(float(perdida(red(x_e), y_e)), 4))
            curva_v.append(round(float(perdida(red(x_v), y_v)), 4))
    return curva_e, curva_v


def main() -> None:
    datos = cargar()
    x = pd.concat([datos[COLUMNAS], pd.get_dummies(datos["Type"], dtype=float)], axis=1).to_numpy(float)
    y = datos["Machine failure"].to_numpy(float)
    orden = np.random.default_rng(7).permutation(len(datos))
    e, v = orden[:N_ENTRENAMIENTO], orden[N_ENTRENAMIENTO:N_ENTRENAMIENTO + N_VALIDACION]
    media, desv = x[e].mean(0), x[e].std(0) + 1e-9
    a_t = lambda idx: (torch.tensor((x[idx] - media) / desv, dtype=torch.float32), torch.tensor(y[idx, None], dtype=torch.float32))
    x_e, y_e = a_t(e)
    x_v, y_v = a_t(v)

    resultado = {"registros": len(datos), "fallas": int(y.sum()), "entrenamiento": N_ENTRENAMIENTO,
                 "validacion": N_VALIDACION, "epocas": EPOCAS, "fallas_entrenamiento": int(y[e].sum())}
    for nombre, dropout in [("sin_regularizacion", 0.0), ("con_dropout", 0.3)]:
        curva_e, curva_v = entrenar(x_e, y_e, x_v, y_v, dropout)
        mejor = int(np.argmin(curva_v))
        resultado[nombre] = {"entrenamiento": curva_e, "validacion": curva_v, "parada_temprana": mejor + 1,
                             "validacion_minima": curva_v[mejor], "validacion_final": curva_v[-1]}
        print(f"{nombre}: pérdida final {curva_e[-1]:.3f} en entrenamiento y {curva_v[-1]:.3f} en validación; "
              f"mínima en validación {curva_v[mejor]:.3f} en la época {mejor + 1}")
    print(f"{len(datos)} registros, {int(y.sum())} fallas ({y.mean():.1%}); "
          f"{int(y[e].sum())} fallas en los {N_ENTRENAMIENTO} de entrenamiento")
    guardar_json("curvas_5a.json", resultado)


if __name__ == "__main__":
    main()
