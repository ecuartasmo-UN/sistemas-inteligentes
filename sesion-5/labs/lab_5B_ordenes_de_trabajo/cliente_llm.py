"""Cliente de LLM común a los laboratorios de Sistemas Inteligentes (sesiones 2 a 5).

Una sola función de llamada, `completar`, para varios proveedores. Desde la sesión 4 acepta imágenes:
`mensaje_con_imagen` arma un mensaje neutro que el cliente traduce al formato de cada proveedor.
Desde la sesión 5 no envía la temperatura: Claude Sonnet 5.5 y Haiku 5.5 la rechazan con un error 400, Gemini 3.6
Flash la ignora y GPT-6 la retira con el razonamiento activo (documentación consultada el 29-oct-2026). La
reproducibilidad la dan las respuestas grabadas.
- API: Anthropic, OpenAI y Google Gemini. La clave se lee de una variable de entorno,
  de un archivo .env (en la carpeta del laboratorio o en una carpeta superior) o, en
  Colab, de sus Secrets. La clave nunca se imprime.
- local: un modelo abierto servido con Ollama en el computador del estudiante.
- grabado: respuestas reales de una corrida anterior, para trabajar sin red ni clave.

Registra los tokens, el tiempo y el costo de cada llamada, y se detiene si se supera
el presupuesto configurado.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

# Precios en USD por millón de tokens (entrada, salida), tomados de las páginas oficiales.
FECHA_PRECIOS = "2026-10-29"
FUENTES_PRECIOS = {
    "anthropic": "https://platform.claude.com/docs/en/about-claude/pricing",
    "openai": "https://developers.openai.com/api/docs/pricing",
    "gemini": "https://ai.google.dev/gemini-api/docs/pricing",
}
PRECIOS = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
    "gpt-6-luna": (0.10, 0.50),
    "gpt-5-nano": (0.05, 0.40),
    "gpt-5-mini": (0.25, 2.00),
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "gemini-2.5-flash-lite": (0.10, 0.40),
}
MODELOS_POR_DEFECTO = {
    "anthropic": "claude-haiku-5-5",
    "openai": "gpt-6-luna",
    "gemini": "gemini-3.5-flash-lite",
    "ollama": "qwen3:4b-instruct",
}
VARIABLES_CLAVE = {
    "anthropic": ["ANTHROPIC_API_KEY"],
    "openai": ["OPENAI_API_KEY"],
    "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
}
URL_OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
if not URL_OLLAMA.startswith("http"):
    URL_OLLAMA = "http://" + URL_OLLAMA
URL_GEMINI = "https://generativelanguage.googleapis.com/v1beta/openai/"

# Razonamiento en la API de Anthropic, de la configuración preferida a la de respaldo (verificado el 21-oct-2026).
# Los modelos 5.5 usan "adaptive" con output_config.effort; Haiku 5.5 acepta "disabled", Opus 5.5 no.
# Los modelos anteriores usan "enabled" con budget_tokens. "margen" deja espacio para los tokens de razonamiento.
_RAZONAMIENTO_ANTHROPIC = {
    False: [{"thinking": {"type": "disabled"}},
            {"thinking": {"type": "adaptive"}, "output_config": {"effort": "low"}, "margen": 4000},
            {"margen": 4000}],
    True: [{"thinking": {"type": "adaptive"}, "output_config": {"effort": "high"}, "margen": 8000},
           {"thinking": {"type": "enabled", "budget_tokens": 4000}, "margen": 4000},
           {"margen": 8000}],
}
PROVEEDORES = ("anthropic", "openai", "gemini", "ollama", "grabado")
# Modelos locales que ven imágenes, en orden de preferencia. Todos pesan más de 1 GB: se descargan con «ollama pull».
MODELOS_VISION_OLLAMA = ("qwen2.5vl:3b", "gemma3:4b", "llava:7b", "moondream")


def mensaje_con_imagen(texto: str, imagen: bytes, tipo: str = "image/jpeg", id: str | None = None) -> dict:
    """Mensaje de usuario con una imagen y un texto, en un formato neutro que el cliente adapta a cada proveedor.

    id: identificador estable de la imagen (por ejemplo, su archivo, su tamaño y un hash del original). Si se da,
        las grabaciones reconocen la imagen por él y no por sus bytes, que pueden cambiar un poco al reducirla con
        otra versión de Pillow."""
    bloque = {"type": "image", "media_type": tipo, "data": base64.standard_b64encode(imagen).decode("ascii")}
    if id:
        bloque["id"] = id
    return {"role": "user", "content": [bloque, {"type": "text", "text": texto}]}


def _tiene_imagenes(mensajes) -> bool:
    return any(isinstance(m.get("content"), list) and any(b.get("type") == "image" for b in m["content"]) for m in mensajes)


def _adaptar(mensajes: list, proveedor: str) -> list:
    """Traduce los mensajes con imágenes del formato neutro al de cada proveedor; el texto pasa igual."""
    salida = []
    for m in mensajes:
        contenido = m.get("content")
        if not isinstance(contenido, list):
            salida.append(m)
            continue
        textos = [b["text"] for b in contenido if b.get("type") == "text"]
        imagenes = [b for b in contenido if b.get("type") == "image"]
        if proveedor == "anthropic":
            bloques = [{"type": "image", "source": {"type": "base64", "media_type": b["media_type"], "data": b["data"]}}
                       for b in imagenes] + [{"type": "text", "text": x} for x in textos]
            salida.append({"role": m["role"], "content": bloques})
        elif proveedor in ("openai", "gemini"):
            bloques = [{"type": "text", "text": x} for x in textos] + [
                {"type": "image_url", "image_url": {"url": f"data:{b['media_type']};base64,{b['data']}"}} for b in imagenes]
            salida.append({"role": m["role"], "content": bloques})
        else:   # ollama: el texto en content y las imágenes aparte, en base64
            salida.append({"role": m["role"], "content": "\n".join(textos), "images": [b["data"] for b in imagenes]})
    return salida


class PresupuestoAgotado(RuntimeError):
    """Se superó el límite de llamadas o de tokens configurado para el notebook."""


class ErrorLLM(RuntimeError):
    """El proveedor del LLM no respondió; el mensaje explica qué revisar."""


@dataclass
class Respuesta:
    """Respuesta del LLM, con sus métricas."""
    texto: str
    proveedor: str
    modelo: str
    tokens_entrada: int = 0
    tokens_salida: int = 0
    tokens_razonamiento: int = 0
    segundos: float = 0.0
    costo_usd: float | None = 0.0
    grabada: bool = False
    disponible: bool = True
    fecha: str = ""
    coincide: bool = True   # con respuestas grabadas: False si se reprodujo la grabación de otra instrucción


# ----------------------------------------------------------------------------- claves y detección

def cargar_claves() -> None:
    """Carga las claves de un archivo .env (si existe) y, en Colab, de sus Secrets."""
    try:
        from dotenv import find_dotenv, load_dotenv
        ruta = find_dotenv(usecwd=True)
        if ruta:
            load_dotenv(ruta, override=False)
    except ImportError:
        pass
    try:
        from google.colab import userdata  # solo existe en Colab
        for variables in VARIABLES_CLAVE.values():
            for v in variables:
                if not os.environ.get(v):
                    try:
                        valor = userdata.get(v)
                        if valor:
                            os.environ[v] = valor
                    except Exception:
                        pass
    except ImportError:
        pass


def _clave(proveedor: str):
    """Devuelve la clave del proveedor, limpia de errores de copiado comunes (espacios, comillas, «=» de más)."""
    for v in VARIABLES_CLAVE.get(proveedor, []):
        valor = os.environ.get(v)
        if valor:
            return valor.strip().lstrip("=").strip().strip("\"'").strip()
    return None


def _ollama_modelos(tiempo: float = 1.5):
    """Lista los modelos de Ollama instalados, o None si el servidor no responde."""
    try:
        with urllib.request.urlopen(f"{URL_OLLAMA}/api/tags", timeout=tiempo) as r:
            return [m["name"] for m in json.load(r).get("models", [])]
    except Exception:
        return None


def estado_proveedores(carpeta_grabaciones: str = "grabaciones", vision: bool = False) -> list:
    """Resume qué vías están disponibles en este computador (sin mostrar ninguna clave).

    vision=True: la vía local solo cuenta si Ollama tiene un modelo que ve imágenes."""
    cargar_claves()
    filas = []
    for p in ("anthropic", "openai", "gemini"):
        filas.append({"vía": f"API · {p}", "disponible": "sí" if _clave(p) else "no",
                      "detalle": f"clave en {VARIABLES_CLAVE[p][0]}" if _clave(p) else f"falta {VARIABLES_CLAVE[p][0]}"})
    modelos = _ollama_modelos()
    if modelos is None:
        filas.append({"vía": "local · ollama", "disponible": "no", "detalle": "el servidor de Ollama no responde"})
    else:
        buscados = MODELOS_VISION_OLLAMA if vision else (MODELOS_POR_DEFECTO["ollama"],)
        tiene = any(m in modelos for m in buscados)
        filas.append({"vía": "local · ollama", "disponible": "sí" if tiene else "no",
                      "detalle": f"modelos: {', '.join(modelos) or 'ninguno'}"
                      + ("" if tiene else f" (falta {buscados[0]}" + (", un modelo que ve imágenes" if vision else "") + ")")})
    n = len(_leer_grabaciones(Path(carpeta_grabaciones)))
    filas.append({"vía": "grabado", "disponible": "sí" if n else "no", "detalle": f"{n} respuestas grabadas"})
    return filas


def detectar_proveedor(carpeta_grabaciones: str = "grabaciones", vision: bool = False) -> str:
    """Elige la primera vía disponible: API (Anthropic, OpenAI, Gemini), luego Ollama, luego grabado.

    vision=True: Ollama solo se elige si tiene un modelo que ve imágenes."""
    cargar_claves()
    for p in ("anthropic", "openai", "gemini"):
        if _clave(p):
            return p
    modelos = _ollama_modelos()
    buscados = MODELOS_VISION_OLLAMA if vision else (MODELOS_POR_DEFECTO["ollama"],)
    if modelos and any(m in modelos for m in buscados):
        return "ollama"
    return "grabado"


def _numero(valor, decimales: int = 0) -> str:
    """Número en formato español: espacio para los miles y coma decimal (8 929; 0,0015)."""
    return f"{valor:,.{decimales}f}".replace(",", " ").replace(".", ",")


# ----------------------------------------------------------------------------- grabaciones

def _archivo_grabaciones(carpeta: Path) -> Path:
    return carpeta / "respuestas.json"


def _leer_grabaciones(carpeta: Path) -> dict:
    ruta = _archivo_grabaciones(carpeta)
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    return {}


def _sin_bytes(mensajes) -> list:
    """Cambia los bytes de cada imagen que tiene identificador por ese identificador."""
    salida = []
    for m in mensajes:
        contenido = m.get("content")
        if isinstance(contenido, list):
            contenido = [{"type": "image", "id": b["id"]} if b.get("type") == "image" and b.get("id") else b
                         for b in contenido]
            m = {**m, "content": contenido}
        salida.append(m)
    return salida


def _huella(sistema, mensajes) -> str:
    texto = json.dumps({"s": sistema or "", "m": _sin_bytes(mensajes)}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


# ----------------------------------------------------------------------------- cliente

class ClienteLLM:
    """Cliente de LLM con registro de costo y presupuesto.

    proveedor: "anthropic", "openai", "gemini", "ollama" o "grabado" (None = detección automática).
    modelo: None usa el modelo por defecto del proveedor.
    max_llamadas, max_tokens: presupuesto del notebook (entrada + salida).
    grabar: guarda cada respuesta real en grabaciones/respuestas.json (lo usa el docente);
            None toma el valor de la variable de entorno LLM_GRABAR.
    razonamiento: False (por defecto) pide la respuesta directa; True activa el modo de razonamiento
            de los modelos que lo tienen (Claude, modelos locales como Qwen3). Cómo funciona ese modo
            se estudia en la Unidad 3; aquí solo se comparan sus resultados y su costo.
    """

    def __init__(self, proveedor=None, modelo=None, max_llamadas: int = 80,
                 max_tokens: int = 500_000, carpeta_grabaciones: str = "grabaciones", grabar: bool | None = None,
                 razonamiento: bool = False, mostrar: bool = True, vision: bool = False):
        cargar_claves()
        self.carpeta = Path(carpeta_grabaciones)
        elegido = (proveedor or os.environ.get("LLM_PROVEEDOR") or detectar_proveedor(str(self.carpeta), vision)).lower()
        self.por_variable = not proveedor and bool(os.environ.get("LLM_PROVEEDOR"))   # la vía la fijó el entorno
        if elegido not in PROVEEDORES:
            raise ValueError(f"Proveedor desconocido: {elegido}. Use uno de: {', '.join(PROVEEDORES)}.")
        self.proveedor = elegido
        self.modelo = modelo or os.environ.get("LLM_MODELO") or MODELOS_POR_DEFECTO.get(elegido, "")
        if vision and elegido == "ollama" and not modelo:
            # El modelo de texto por defecto no ve imágenes: se usa el primer modelo de visión instalado
            instalados = _ollama_modelos() or []
            self.modelo = next((m for m in MODELOS_VISION_OLLAMA if m in instalados), MODELOS_VISION_OLLAMA[0])
        self.razonamiento = razonamiento
        self._opcion_anthropic = 0  # índice de la configuración de razonamiento que acepta el modelo
        self.max_llamadas, self.max_tokens = max_llamadas, max_tokens
        self.grabar = os.environ.get("LLM_GRABAR") == "1" if grabar is None else grabar
        self.registro: list = []
        self._grabaciones = _leer_grabaciones(self.carpeta) if elegido == "grabado" else {}
        if elegido == "grabado" and self._grabaciones:
            primera = next(iter(self._grabaciones.values()))
            self._modelo_grabado = primera["modelo"]
            self.modelo = f"{primera['modelo']} (grabado el {primera['fecha'][:10]})"
        if elegido in VARIABLES_CLAVE and not _clave(elegido):
            raise ErrorLLM(f"No se encontró la clave de {elegido}. Cree un archivo .env en la carpeta del laboratorio "
                           f"con la línea {VARIABLES_CLAVE[elegido][0]}=su-clave, o elija otra vía.")
        if mostrar:
            self.describir()

    # -- información
    def describir(self) -> None:
        if self.por_variable:
            print("La vía la fijó la variable de entorno LLM_PROVEEDOR, no la detección automática.")
        if self.proveedor == "grabado":
            n = len(self._grabaciones)
            if n:
                precio = PRECIOS.get(getattr(self, "_modelo_grabado", ""))
                print(f"Vía: respuestas grabadas ({n}) de {self.modelo}.\n"
                      "Son respuestas reales de una corrida anterior; no se hace ninguna llamada nueva."
                      + (f"\nLos tokens, el tiempo y el costo que se muestran son los de esa corrida (US${_numero(precio[0], 2)} / "
                         f"US${_numero(precio[1], 2)} por millón de tokens de entrada / salida)." if precio else ""))
                if self.razonamiento:
                    print("Nota: las respuestas se grabaron sin modo de razonamiento; con esta vía no se puede activar.")
            else:
                print("Vía: grabado, pero no hay respuestas grabadas en esta carpeta.\n"
                      "Configure una clave de API o un modelo local para usar un LLM.")
            return
        precio = PRECIOS.get(self.modelo)
        texto_precio = (f"US${_numero(precio[0], 2)} / US${_numero(precio[1], 2)} por millón de tokens de entrada / salida "
                        f"(precios del {FECHA_PRECIOS})") if precio else ("sin costo monetario (modelo local)"
                                                                          if self.proveedor == "ollama" else "precio no registrado")
        print(f"Vía: {self.proveedor} · modelo: {self.modelo} · razonamiento: {'activado' if self.razonamiento else 'desactivado'}\n"
              f"Costo: {texto_precio}\n"
              f"Presupuesto de este notebook: {self.max_llamadas} llamadas y {_numero(self.max_tokens)} tokens.")

    def resumen(self) -> dict:
        """Totales de las llamadas hechas hasta ahora."""
        costos = [r["costo_usd"] for r in self.registro if r["costo_usd"] is not None]
        return {"llamadas": len(self.registro),
                "tokens_entrada": sum(r["tokens_entrada"] for r in self.registro),
                "tokens_salida": sum(r["tokens_salida"] for r in self.registro),
                "costo_usd": round(sum(costos), 6) if costos else None,
                "segundos": round(sum(r["segundos"] for r in self.registro), 1)}

    def texto_resumen(self) -> str:
        """Resumen del consumo en una frase."""
        r = self.resumen()
        costo = "costo no registrado" if r["costo_usd"] is None else f"US${_numero(r['costo_usd'], 4)}"
        return (f"{r['llamadas']} llamadas · {_numero(r['tokens_entrada'])} tokens de entrada y "
                f"{_numero(r['tokens_salida'])} de salida · {costo} · {_numero(r['segundos'], 1)} s de espera")

    # -- llamada principal
    def completar(self, mensajes, sistema: str | None = None, etiqueta: str | None = None,
                  max_tokens_respuesta: int = 1500, exacta: bool = True) -> Respuesta:
        """Envía la conversación al LLM y devuelve su respuesta.

        mensajes: lista de {"role": "user" | "assistant", "content": texto}, o mensajes con imagen
                  creados con mensaje_con_imagen.
        etiqueta: nombre único de la llamada (sirve para grabar y reproducir respuestas).
        exacta: con respuestas grabadas, True solo reproduce la respuesta si la instrucción es idéntica a la
                grabada; False la reproduce aunque la instrucción haya cambiado, con un aviso.
        """
        if isinstance(mensajes, str):
            mensajes = [{"role": "user", "content": mensajes}]
        usados = sum(r["tokens_entrada"] + r["tokens_salida"] for r in self.registro)
        if len(self.registro) >= self.max_llamadas or usados >= self.max_tokens:
            raise PresupuestoAgotado(
                f"Se alcanzó el presupuesto del notebook ({len(self.registro)} llamadas, {usados} tokens). "
                "Si de verdad necesita más, cree el cliente con un límite mayor, por ejemplo "
                "ClienteLLM(max_llamadas=150).")
        if self.proveedor == "grabado":
            respuesta = self._desde_grabacion(sistema, mensajes, etiqueta, exacta)
        else:
            respuesta = self._con_reintentos(sistema, mensajes, max_tokens_respuesta)
            if self.grabar and etiqueta:
                self._grabar(etiqueta, sistema, mensajes, respuesta)
        if respuesta.disponible:
            self.registro.append({**asdict(respuesta), "etiqueta": etiqueta})
        return respuesta

    # -- reintentos ante límites de tasa o servidores saturados
    def _con_reintentos(self, sistema, mensajes, max_tokens_respuesta) -> Respuesta:
        espera = 2.0
        for intento in range(5):
            try:
                return self._llamar(sistema, mensajes, max_tokens_respuesta)
            except ErrorLLM:
                raise
            except Exception as e:  # errores de red, límites de tasa o servidor saturado
                estado = getattr(e, "status_code", None)
                nombre = type(e).__name__
                transitorio = estado in (408, 409, 429, 500, 502, 503, 504, 529) or any(
                    k in nombre for k in ("RateLimit", "Overloaded", "Connection", "Timeout", "InternalServer"))
                if not transitorio or intento == 4:
                    raise ErrorLLM(f"El proveedor {self.proveedor} respondió con un error ({nombre}: {str(e)[:300]}).") from None
                print(f"  (el servidor está ocupado; se reintenta en {espera:.0f} s)")
                time.sleep(espera)
                espera *= 2
        raise ErrorLLM("No se obtuvo respuesta del LLM.")

    def _llamar(self, sistema, mensajes, max_tokens_respuesta) -> Respuesta:
        inicio = time.perf_counter()
        mensajes = _adaptar(mensajes, self.proveedor)
        if self.proveedor == "anthropic":
            import anthropic
            cliente = anthropic.Anthropic(api_key=_clave("anthropic"))
            argumentos = {"model": self.modelo, "messages": mensajes}
            if sistema:
                argumentos["system"] = sistema
            # Configuraciones del razonamiento, de la preferida a la de respaldo. Se usa la primera que el modelo
            # acepte y se recuerda para las llamadas siguientes.
            opciones = _RAZONAMIENTO_ANTHROPIC[self.razonamiento]
            for i in range(self._opcion_anthropic, len(opciones)):
                extra = dict(opciones[i])
                margen = extra.pop("margen", 0)  # espacio para los tokens de razonamiento, si el modelo razona
                try:
                    r = cliente.messages.create(**argumentos, **extra, max_tokens=max_tokens_respuesta + margen)
                except Exception as e:
                    error = str(e).lower()
                    if i == len(opciones) - 1 or not any(k in error for k in ("thinking", "effort", "output_config")):
                        raise
                    continue
                if i != self._opcion_anthropic and not self.razonamiento:
                    print(f"  Nota: {self.modelo} no permite desactivar su modo de razonamiento; se usa el esfuerzo "
                          "mínimo. Los tokens de razonamiento que use se cuentan como tokens de salida.")
                self._opcion_anthropic = i
                break
            texto = "".join(getattr(b, "text", "") or "" for b in r.content if getattr(b, "type", "") == "text")
            entrada, salida = r.usage.input_tokens, r.usage.output_tokens
            detalles = getattr(r.usage, "output_tokens_details", None)
            razonamiento = getattr(detalles, "thinking_tokens", 0) or 0
            if not texto and getattr(r, "stop_reason", "") == "max_tokens":
                raise ErrorLLM("El modelo agotó el límite de tokens de salida antes de responder. "
                               "Use un límite mayor (max_tokens_respuesta).")
        elif self.proveedor in ("openai", "gemini"):
            from openai import OpenAI
            cliente = OpenAI(api_key=_clave(self.proveedor), base_url=URL_GEMINI if self.proveedor == "gemini" else None)
            completos = ([{"role": "system", "content": sistema}] if sistema else []) + mensajes
            argumentos = {"model": self.modelo, "messages": completos}
            argumentos["max_tokens" if self.proveedor == "gemini" else "max_completion_tokens"] = max_tokens_respuesta
            r = cliente.chat.completions.create(**argumentos)
            texto = r.choices[0].message.content or ""
            entrada, salida = r.usage.prompt_tokens, r.usage.completion_tokens
            detalles = getattr(r.usage, "completion_tokens_details", None)
            razonamiento = getattr(detalles, "reasoning_tokens", 0) or 0
        elif self.proveedor == "ollama":
            completos = ([{"role": "system", "content": sistema}] if sistema else []) + mensajes
            cuerpo = {"model": self.modelo, "messages": completos, "stream": False, "think": self.razonamiento,
                      "options": {"num_predict": max_tokens_respuesta}}
            peticion = urllib.request.Request(f"{URL_OLLAMA}/api/chat", data=json.dumps(cuerpo).encode("utf-8"),
                                              headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(peticion, timeout=900) as resp:
                    r = json.load(resp)
            except urllib.error.HTTPError as e:
                detalle = e.read().decode("utf-8", "ignore")[:200]
                if e.code == 404:
                    raise ErrorLLM(f"Ollama no tiene el modelo {self.modelo}. En una terminal ejecute: "
                                   f"ollama pull {self.modelo}") from None
                raise ErrorLLM(f"Ollama respondió con un error {e.code}: {detalle}") from None
            except urllib.error.URLError:
                raise ErrorLLM("No se pudo conectar con Ollama. Abra la aplicación de Ollama "
                               "(o ejecute «ollama serve» en una terminal) y vuelva a intentar.") from None
            texto = r.get("message", {}).get("content", "")
            entrada, salida, razonamiento = r.get("prompt_eval_count", 0), r.get("eval_count", 0), 0
        else:
            raise ErrorLLM(f"Proveedor no soportado: {self.proveedor}")
        segundos = time.perf_counter() - inicio
        precio = PRECIOS.get(self.modelo)
        if self.proveedor == "ollama":
            costo = 0.0
        elif precio:
            costo = (entrada * precio[0] + salida * precio[1]) / 1_000_000
        else:
            costo = None
        return Respuesta(texto, self.proveedor, self.modelo, entrada, salida, razonamiento, round(segundos, 2),
                         costo, False, True, datetime.now().isoformat(timespec="seconds"))

    # -- grabar y reproducir
    def _grabar(self, etiqueta, sistema, mensajes, respuesta: Respuesta) -> None:
        self.carpeta.mkdir(parents=True, exist_ok=True)
        datos = _leer_grabaciones(self.carpeta)
        datos[etiqueta] = {**asdict(respuesta), "huella": _huella(sistema, mensajes)}
        _archivo_grabaciones(self.carpeta).write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")

    def _desde_grabacion(self, sistema, mensajes, etiqueta, exacta: bool = True) -> Respuesta:
        g = self._grabaciones.get(etiqueta or "")
        if not g:
            print(f"  No hay una respuesta grabada para «{etiqueta}». Para probar esta llamada, configure "
                  "una clave de API o un modelo local.")
            return Respuesta("", "grabado", self.modelo, disponible=False)
        coincide = g.get("huella") == _huella(sistema, mensajes)
        if not coincide:
            if exacta:
                print(f"  La instrucción de «{etiqueta}» no es la que se grabó, así que no tiene respuesta: con respuestas "
                      "grabadas solo se reproducen las instrucciones originales. Para probar una instrucción nueva, "
                      "configure una clave de API o un modelo local.")
                return Respuesta("", "grabado", self.modelo, disponible=False)
            print("  Aviso: la instrucción cambió desde la grabación; se muestra la respuesta grabada para la instrucción original.")
        return Respuesta(g["texto"], "grabado", g["modelo"], g["tokens_entrada"], g["tokens_salida"],
                         g.get("tokens_razonamiento", 0), g["segundos"], g["costo_usd"], True, True, g["fecha"], coincide)


def configurar(**opciones) -> ClienteLLM:
    """Crea el cliente de LLM con detección automática de la vía disponible."""
    return ClienteLLM(**opciones)
