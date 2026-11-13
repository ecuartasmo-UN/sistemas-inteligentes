"""Utilidades comunes de los ejemplos de la Sesión 7: la carpeta de salidas y el guardado en JSON."""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDAS = AQUI / "salidas"        # los números de cada gráfica, en JSON


def guardar_json(nombre: str, datos) -> None:
    """Guarda los resultados de un ejemplo en salidas/, con tildes legibles."""
    SALIDAS.mkdir(exist_ok=True)
    (SALIDAS / nombre).write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")


def red(x: float, dec: int = 4) -> float:
    """Redondea un número para el JSON."""
    return round(float(x), dec)
