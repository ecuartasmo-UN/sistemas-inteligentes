"""Utilidades comunes de los ejemplos de la Sesión 5: rutas, colores del tema y guardado de resultados."""
import json
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
DATOS = AQUI / "datos"            # descargas (MNIST, AI4I); no se suben al repositorio
SALIDAS = AQUI / "salidas"        # los números de cada gráfica, en JSON
IMG = AQUI.parent / "assets" / "img"

# Colores de tema-si.css
FONDO = np.array([10, 14, 23])        # --bg
TEXTO = np.array([232, 236, 244])     # --text
CIAN = np.array([56, 189, 248])       # --accent: valores positivos
VIOLETA = np.array([167, 139, 250])   # --violet: valores negativos


def guardar_json(nombre: str, datos) -> None:
    SALIDAS.mkdir(exist_ok=True)
    (SALIDAS / nombre).write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")


def gris(m: np.ndarray) -> np.ndarray:
    """De 0 (fondo) a 1 (texto claro): para dígitos y mapas de activación."""
    m = np.asarray(m, float)
    m = (m - m.min()) / (np.ptp(m) or 1)
    return (FONDO + m[..., None] * (TEXTO - FONDO)).astype(np.uint8)


def divergente(m: np.ndarray) -> np.ndarray:
    """Negativos en violeta, cero en el fondo y positivos en cian: para filtros y pesos."""
    m = np.asarray(m, float)
    m = m / (np.abs(m).max() or 1)
    pos = np.clip(m, 0, 1)[..., None]
    neg = np.clip(-m, 0, 1)[..., None]
    return (FONDO + pos * (CIAN - FONDO) + neg * (VIOLETA - FONDO)).astype(np.uint8)


def mosaico(celdas: list[np.ndarray], columnas: int, escala: int, margen: int = 6) -> np.ndarray:
    """Une imágenes RGB del mismo tamaño en una cuadrícula, ampliadas sin suavizar."""
    celdas = [np.kron(c, np.ones((escala, escala, 1), dtype=np.uint8)) for c in celdas]
    alto, ancho = celdas[0].shape[:2]
    filas = -(-len(celdas) // columnas)
    lienzo = np.zeros((filas * (alto + margen) - margen, columnas * (ancho + margen) - margen, 3), np.uint8)
    lienzo[:] = FONDO
    for i, c in enumerate(celdas):
        f, k = divmod(i, columnas)
        lienzo[f * (alto + margen):f * (alto + margen) + alto, k * (ancho + margen):k * (ancho + margen) + ancho] = c
    return lienzo


def guardar_png(nombre: str, rgb: np.ndarray) -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb).save(IMG / nombre, optimize=True)
    print(f"  {nombre}: {rgb.shape[1]}×{rgb.shape[0]} px")
