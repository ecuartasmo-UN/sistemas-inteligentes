"""Manejo del plan.md del Laboratorio 2C: versiones, pasos, casillas, registro de avance y aprobación.

La aprobación queda ligada a una versión del plan: se calcula una huella de todo el plan,
salvo las entradas del registro de avance y el estado de las casillas. Si después de aprobar
alguien cambia un paso, un riesgo o el objetivo, o agrega cualquier otra cosa, la huella
cambia y el plan deja de estar aprobado.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

FECHA = "2026-10-22"   # fecha simulada de la intervención OT-523
# Un paso: «- [ ] 7. Texto», «- [x] 9b. Texto»; tachado: «- [ ] ~~9. Texto~~», «- [ ] 9. ~~Texto~~» o «- ~~[ ] 9. Texto~~»
_PASO = re.compile(r"^- (~~)?\[( |x|X)\] (~~)?\s*(\d+[a-z]?)\.\s*(.*)$")
# Una entrada del registro de avance: «- 2026-10-22 13:05 · texto», o el marcador de registro vacío
_ENTRADA = re.compile(r"^- (\d{4}-\d{2}-\d{2} \d{1,2}:\d{2} · |\(vac[ií]o)")


class PlanMD:
    """Un plan.md guardado en un archivo de texto."""

    def __init__(self, ruta: str = "planes/plan_OT-523.md"):
        self.ruta = Path(ruta)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        self.ruta_aprobaciones = self.ruta.parent / "aprobaciones.json"

    # -- texto
    @property
    def texto(self) -> str:
        return self.ruta.read_text(encoding="utf-8") if self.ruta.exists() else ""

    def existe(self) -> bool:
        return self.ruta.exists() and bool(self.texto.strip())

    def guardar(self, texto: str) -> None:
        self.ruta.write_text(texto.strip() + "\n", encoding="utf-8")

    def guardar_version(self, nombre: str) -> Path:
        """Guarda una copia con nombre, por ejemplo planes/plan_OT-523_v1_llm.md."""
        destino = self.version(nombre)
        shutil.copy2(self.ruta, destino)
        return destino

    def version(self, nombre: str) -> Path:
        """Ruta de una versión guardada, exista o no."""
        return self.ruta.with_name(f"{self.ruta.stem}_{nombre}.md")

    # -- secciones y pasos
    def secciones(self) -> dict:
        """Diccionario título → contenido de cada sección «## ...»."""
        resultado, actual, lineas = {}, None, []
        for linea in self.texto.splitlines():
            if linea.startswith("## "):
                if actual is not None:
                    resultado[actual] = "\n".join(lineas).strip()
                actual, lineas = linea[3:].strip(), []
            elif actual is not None:
                lineas.append(linea)
        if actual is not None:
            resultado[actual] = "\n".join(lineas).strip()
        return resultado

    def pasos(self, incluir_tachados: bool = False) -> list:
        """Pasos de la sección «Pasos»: dicts con id, marcado, tachado y texto (con sus líneas de continuación)."""
        pasos, actual, en_pasos = [], None, False
        for linea in self.texto.splitlines():
            if linea.startswith("## "):
                en_pasos, actual = "paso" in linea.lower(), None
                continue
            if not en_pasos:
                continue
            m = _PASO.match(linea.strip())
            if m:
                texto = m.group(5).strip()
                actual = {"id": m.group(4), "marcado": m.group(2).lower() == "x", "texto": texto,
                          "tachado": bool(m.group(1) or m.group(3)) or texto.startswith("~~")}
                pasos.append(actual)
            elif actual is not None and linea.startswith((" ", "\t")) and linea.strip() and not linea.strip().startswith("- "):
                actual["texto"] += " " + linea.strip()
        return pasos if incluir_tachados else [p for p in pasos if not p["tachado"]]

    def paso(self, identificador) -> dict | None:
        return next((p for p in self.pasos() if p["id"] == str(identificador)), None)

    # -- casillas y registro
    def marcar(self, identificador) -> None:
        lineas = self.texto.splitlines()
        en_pasos = False
        for i, linea in enumerate(lineas):
            if linea.startswith("## "):
                en_pasos = "paso" in linea.lower()
            m = _PASO.match(linea.strip())
            if en_pasos and m and m.group(4) == str(identificador) and not (m.group(1) or m.group(3)):
                lineas[i] = linea.replace("- [ ]", "- [x]", 1)
        self.guardar("\n".join(lineas))

    def registrar(self, hora: str, texto: str) -> None:
        """Agrega una línea al registro de avance: «- 2026-10-22 13:05 · texto»."""
        linea = f"- {FECHA} {hora} · {texto}"
        actual = self.texto.rstrip()
        if "## Registro de avance" not in actual:
            actual += "\n\n## Registro de avance"
        lineas = [l for l in actual.splitlines() if not re.match(r"^- \(vac[ií]o", l.strip())]
        self.guardar("\n".join(lineas) + "\n" + linea)

    def entradas_registro(self) -> list:
        """Las entradas del registro de avance, en orden."""
        registro = self.secciones().get("Registro de avance", "")
        return [l.strip() for l in registro.splitlines() if re.match(r"^- \d{4}-\d{2}-\d{2} \d{1,2}:\d{2} · ", l.strip())]

    def _fusionar_registro(self, texto_anterior: str) -> int:
        """Agrega al registro actual las entradas de texto_anterior que falten. Devuelve cuántas agregó."""
        anterior = re.split(r"^## Registro de avance\s*$", texto_anterior, flags=re.M)
        entradas_anteriores = [l.strip() for l in (anterior[1] if len(anterior) > 1 else "").splitlines()
                               if re.match(r"^- \d{4}-\d{2}-\d{2} \d{1,2}:\d{2} · ", l.strip())]
        actuales = self.entradas_registro()
        faltan = [l for l in entradas_anteriores if l not in actuales]
        if not faltan:
            return 0
        clave = lambda l: re.search(r"\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}", l).group(0)
        todas = sorted(dict.fromkeys(actuales + faltan), key=clave)
        cuerpo = re.split(r"^## Registro de avance\s*$", self.texto, flags=re.M)[0].rstrip()
        self.guardar(cuerpo + "\n\n## Registro de avance\n" + "\n".join(todas))
        return len(faltan)

    def restaurar_registro(self, version_anterior) -> int:
        """Recupera las entradas del registro de una versión anterior que falten en la actual.

        Sirve cuando una replanificación (de una persona o de un LLM) borra entradas del registro:
        el registro es la memoria del plan y no se debe perder. Devuelve cuántas entradas recuperó.
        """
        return self._fusionar_registro(Path(version_anterior).read_text(encoding="utf-8"))

    def adoptar(self, version) -> int:
        """Reemplaza el plan por una versión guardada (por ejemplo, una propuesta del LLM), sin perder el registro.

        Devuelve cuántas entradas del registro actual recuperó en la versión adoptada.
        """
        anterior = self.texto
        self.guardar(Path(version).read_text(encoding="utf-8"))
        return self._fusionar_registro(anterior)

    # -- aprobación ligada a la versión
    def huella(self) -> str:
        """Huella de todo el plan, salvo las entradas del registro de avance y el estado de las casillas.

        Solo se excluyen las entradas que están en la sección «Registro de avance»: una línea con ese formato
        escrita en otra sección cambia la huella, como cualquier otro cambio.
        """
        lineas, en_registro = [], False
        for l in self.texto.splitlines():
            if l.startswith("## "):
                en_registro = l.strip().lower() == "## registro de avance"
            if not (en_registro and _ENTRADA.match(l.strip())):
                lineas.append(l)
        texto = re.sub(r"- \[[xX]\]", "- [ ]", "\n".join(lineas))
        texto = re.sub(r"\s+", " ", texto).strip()
        return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:8]

    def _aprobaciones(self) -> list:
        if self.ruta_aprobaciones.exists():
            return json.loads(self.ruta_aprobaciones.read_text(encoding="utf-8"))
        return []

    def aprobar(self, por: str, cargo: str, hora: str) -> str:
        """Registra la aprobación de la versión actual del plan y devuelve su huella."""
        huella = self.huella()
        aprobaciones = self._aprobaciones()
        aprobaciones.append({"version": huella, "por": por, "cargo": cargo, "fecha": f"{FECHA} {hora}",
                             "registrado": datetime.now().isoformat(timespec="seconds")})
        self.ruta_aprobaciones.write_text(json.dumps(aprobaciones, ensure_ascii=False, indent=1), encoding="utf-8")
        self.registrar(hora, f"Plan aprobado por {por} ({cargo}) · versión {huella}.")
        return huella

    def aprobado(self) -> bool:
        """True si la versión actual del plan es la última aprobada."""
        aprobaciones = self._aprobaciones()
        return bool(aprobaciones) and aprobaciones[-1]["version"] == self.huella()

    def reiniciar(self) -> None:
        """Borra el plan, sus versiones, sus aprobaciones y su ejecución (para empezar de nuevo)."""
        shutil.rmtree(self.ruta.parent, ignore_errors=True)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
