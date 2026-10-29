"""Una red convolucional pequeña que lee dígitos (charla inicial, «Una CNN que lee dígitos»).

Entrena en CPU, durante 2 épocas, una CNN de dos capas convolucionales sobre MNIST
(60 000 imágenes de entrenamiento y 10 000 de prueba, de 28 × 28 píxeles) y guarda:
- los filtros de 5 × 5 que aprendió la primera capa, junto a los dos filtros de Sobel de la Sesión 4;
- un dígito de prueba y sus mapas de rasgos en la primera y la segunda capa;
- la exactitud en la prueba, la matriz de confusión y los pares de dígitos que más confunde.

Uso, desde esta carpeta:  python cnn_mnist.py
Requiere torch y torchvision. La primera vez descarga MNIST (unos 12 MB) en datos/.
Escribe las imágenes en ../assets/img/ con el prefijo cnn_ y los números en salidas/cnn_mnist.json.
"""
import time

import numpy as np
import torch
from torch import nn
from torchvision import datasets, transforms

from comun import DATOS, divergente, gris, guardar_json, guardar_png, mosaico

torch.manual_seed(7)
torch.set_num_threads(4)


class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.capa1 = nn.Conv2d(1, 8, kernel_size=5)    # 28×28 → 8 mapas de 24×24
        self.capa2 = nn.Conv2d(8, 16, kernel_size=5)   # 12×12 → 16 mapas de 8×8
        self.salida = nn.Linear(16 * 4 * 4, 10)        # una puntuación por dígito
        self.reducir = nn.MaxPool2d(2)

    def forward(self, x, mapas=False):
        m1 = torch.relu(self.capa1(x))
        m2 = torch.relu(self.capa2(self.reducir(m1)))
        y = self.salida(self.reducir(m2).flatten(1))
        return (y, m1, m2) if mapas else y


def main() -> None:
    a_tensor = transforms.ToTensor()
    entrenamiento = datasets.MNIST(DATOS, train=True, download=True, transform=a_tensor)
    prueba = datasets.MNIST(DATOS, train=False, download=True, transform=a_tensor)
    cargador = torch.utils.data.DataLoader(entrenamiento, batch_size=64, shuffle=True)

    red = CNN()
    optimizador = torch.optim.Adam(red.parameters(), lr=1e-3)
    inicio = time.time()
    for epoca in range(2):
        for x, y in cargador:
            optimizador.zero_grad()
            nn.functional.cross_entropy(red(x), y).backward()
            optimizador.step()
        print(f"Época {epoca + 1} terminada ({time.time() - inicio:.0f} s)")
    segundos = time.time() - inicio

    red.eval()
    with torch.no_grad():
        x_prueba = torch.stack([prueba[i][0] for i in range(len(prueba))])
        y_prueba = torch.tensor([prueba[i][1] for i in range(len(prueba))])
        predichas = red(x_prueba).argmax(1)
    confusion = np.zeros((10, 10), int)
    for real, pred in zip(y_prueba.tolist(), predichas.tolist()):
        confusion[real, pred] += 1
    exactitud = float((predichas == y_prueba).float().mean())
    pares = sorted(((confusion[r, p], r, p) for r in range(10) for p in range(10) if r != p), reverse=True)[:5]
    print(f"Exactitud en las 10 000 imágenes de prueba: {exactitud:.2%} ({segundos:.0f} s de entrenamiento)")
    print("Lo que más confunde:", ", ".join(f"{r} leído como {p} ({n} veces)" for n, r, p in pares))

    print("Imágenes:")
    # Muestras: el primer ejemplo de cada dígito en la prueba, dos filas
    muestras = [x_prueba[(y_prueba == d).nonzero()[k, 0], 0].numpy() for k in (0, 1) for d in range(10)]
    guardar_png("cnn_muestras_mnist.png", mosaico([gris(m) for m in muestras], 10, 4))
    filtros = red.capa1.weight.detach()[:, 0].numpy()
    guardar_png("cnn_filtros_capa1.png", mosaico([divergente(f) for f in filtros], 4, 24))
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], float)
    guardar_png("cnn_filtros_sobel.png", mosaico([divergente(sobel_x), divergente(sobel_x.T)], 2, 40))
    # Un dígito de prueba bien leído y sus mapas de rasgos
    i = int(((y_prueba == 3) & (predichas == 3)).nonzero()[0, 0])
    with torch.no_grad():
        _, m1, m2 = red(x_prueba[i:i + 1], mapas=True)
    guardar_png("cnn_entrada.png", mosaico([gris(x_prueba[i, 0].numpy())], 1, 10))
    guardar_png("cnn_mapas_capa1.png", mosaico([gris(m) for m in m1[0].numpy()], 4, 5))
    guardar_png("cnn_mapas_capa2.png", mosaico([gris(m) for m in m2[0].numpy()], 8, 7))

    guardar_json("cnn_mnist.json", {
        "epocas": 2, "segundos_entrenamiento": round(segundos), "exactitud_prueba": round(exactitud, 4),
        "imagenes_entrenamiento": len(entrenamiento), "imagenes_prueba": len(prueba),
        "parametros": sum(p.numel() for p in red.parameters()),
        "digito_de_los_mapas": 3, "indice_prueba": i,
        "matriz_confusion": confusion.tolist(),
        "mas_confundidos": [{"real": r, "leido_como": p, "veces": int(n)} for n, r, p in pares],
    })


if __name__ == "__main__":
    main()
