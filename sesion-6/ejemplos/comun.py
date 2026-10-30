"""Utilidades comunes de los ejemplos de la Sesión 6: rutas, descargas y guardado de resultados."""
import json
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATOS = AQUI / "datos"            # descargas (Titanic, German Credit, Mushroom); no se suben al repositorio
SALIDAS = AQUI / "salidas"        # los números de cada gráfica, en JSON


def descargar(url: str, nombre: str) -> Path:
    """Descarga un archivo a datos/ la primera vez; después usa la copia local."""
    destino = DATOS / nombre
    if not destino.exists():
        DATOS.mkdir(exist_ok=True)
        with urllib.request.urlopen(url) as r:
            destino.write_bytes(r.read())
    return destino


def guardar_json(nombre: str, datos) -> None:
    SALIDAS.mkdir(exist_ok=True)
    (SALIDAS / nombre).write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
