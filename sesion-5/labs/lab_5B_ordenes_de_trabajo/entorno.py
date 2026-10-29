"""Preparación del entorno de los laboratorios de Sistemas Inteligentes.

El entorno por defecto es VS Code con el entorno virtual del curso (Python 3.13).
Esta función comprueba la versión de Python, instala lo que falte de requirements.txt
y resume el entorno. Solo usa la biblioteca estándar, para poder correr antes de
instalar cualquier otra cosa.
"""
from __future__ import annotations

import importlib.metadata
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

VERSION_RECOMENDADA = (3, 13)
VERSION_MINIMA = (3, 12)


def en_colab() -> bool:
    """True si el notebook corre en Google Colab (el respaldo del curso)."""
    return "google.colab" in sys.modules or "COLAB_RELEASE_TAG" in os.environ


def _requisitos(ruta: Path) -> list:
    """Lee requirements.txt y devuelve pares (paquete, versión fijada o None)."""
    pares = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.split("#")[0].strip()
        if not linea:
            continue
        m = re.match(r"([A-Za-z0-9_.\-\[\]]+)\s*(==\s*([\w.]+))?", linea)
        if m:
            pares.append((m.group(1).split("[")[0], m.group(3)))
    return pares


def _version_instalada(paquete: str):
    try:
        return importlib.metadata.version(paquete)
    except importlib.metadata.PackageNotFoundError:
        return None


def preparar(requisitos: str = "requirements.txt", instalar: bool = True, en_colab_aceptar: tuple = ()) -> None:
    """Comprueba Python, instala los paquetes que falten y muestra un resumen del entorno.

    en_colab_aceptar: paquetes que, en Colab, se aceptan con la versión que ya trae (por ejemplo torch, cuya
    reinstalación descargaría más de 1 GB)."""
    print("Preparando el entorno del laboratorio...\n")
    version = sys.version_info[:2]
    if version < VERSION_MINIMA:
        print(f"✗ Este kernel usa Python {version[0]}.{version[1]}. El curso necesita Python "
              f"{VERSION_MINIMA[0]}.{VERSION_MINIMA[1]} o superior (se recomienda {VERSION_RECOMENDADA[0]}.{VERSION_RECOMENDADA[1]}).\n"
              "  En VS Code, haga clic en el selector de kernel (arriba a la derecha) y elija el entorno del curso.")
    else:
        print(f"✓ Python {version[0]}.{version[1]}")

    en_entorno_virtual = sys.prefix != sys.base_prefix
    if en_colab():
        print("✓ Google Colab (respaldo del curso)"
              + (": la vía local con Ollama no está disponible aquí." if Path("cliente_llm.py").exists() else "."))
    elif en_entorno_virtual:
        # Solo las dos últimas carpetas: bastan para reconocer el .venv del curso y no exponen el nombre de usuario
        print(f"✓ Entorno virtual: …/{'/'.join(Path(sys.prefix).parts[-2:])}")
    else:
        print("! El kernel no está en un entorno virtual. Funciona, pero se recomienda usar el entorno del curso.")

    ruta = Path(requisitos)
    faltan = []
    if ruta.exists():
        for paquete, fijada in _requisitos(ruta):
            instalada = _version_instalada(paquete)
            aceptada = en_colab() and instalada is not None and paquete in en_colab_aceptar
            # «2.14.1+cpu» cuenta como 2.14.1: es la misma versión de torch, compilada solo para la CPU
            if instalada is None or (fijada and instalada.split("+")[0] != fijada and not aceptada):
                faltan.append(f"{paquete}=={fijada}" if fijada else paquete)
    else:
        print(f"! No se encontró {requisitos} en la carpeta de trabajo. Abra el notebook desde la carpeta del laboratorio, "
              "en el Explorador de VS Code, y reinicie el kernel.")

    if faltan and instalar:
        print(f"\nInstalando {len(faltan)} paquete(s): {', '.join(faltan)}")
        print("(la primera vez puede tardar uno o dos minutos)")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *faltan])
            print("✓ Paquetes instalados.")
            faltan = []
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"✗ No se pudieron instalar los paquetes ({e}).\n"
                  "  Abra una terminal en VS Code (Terminal › Nueva terminal) y ejecute:\n"
                  f"  python -m pip install -r {requisitos}")
    elif not faltan and ruta.exists():
        print("✓ Todos los paquetes del laboratorio están instalados.")

    print(f"\nSistema operativo: {platform.system()} {platform.release()} · Carpeta de trabajo: {Path.cwd().name}")
