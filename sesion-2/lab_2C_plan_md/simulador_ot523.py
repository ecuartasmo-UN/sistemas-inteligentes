"""Simulador de la intervención OT-523 y ejecución paso a paso del plan.md (Laboratorio 2C).

El simulador reproduce, con un reloj que empieza a las 13:00, las operaciones de la
intervención: asignar a la técnica, retirar los rodamientos, bloquear, desacoplar, cambiar,
alinear, pedir aprobaciones, arrancar, probar y cerrar la orden. Es determinista: el mismo
escenario produce siempre los mismos hechos. Cada escenario de falla introduce un problema
real en un punto de la ejecución.

La clase Ejecucion une el plan.md aprobado con el simulador. Lee cada paso del plan,
reconoce su operación por el verbo con que empieza (un paso, una operación), la ejecuta,
marca la casilla solo si la verificación pasa y escribe en el registro de avance. La
ejecución se guarda en planes/ejecucion.json: si se reinicia el kernel, se retoma.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

from presentacion import mostrar_tabla, nota

ESCENARIOS = {
    "sin_falla": "Todo sale según el procedimiento.",
    "rodamiento_equivocado": "La caja rotulada 6206-2RS trae rodamientos de otra referencia.",
    "vibracion_alta": "Después del cambio, la prueba de vibración falla.",
    "tecnico_ausente": "La técnica asignada es llamada a una emergencia en medio de la intervención.",
}
INICIO = 13 * 60          # la ventana empieza a las 13:00
FIN_VENTANA = 17 * 60     # y termina a las 17:00
LIMITE_RESPALDO = 19 * 60  # el compresor de respaldo no puede operar después de las 19:00
LIMITE_VIBRACION = 4.5    # mm/s
SUPERVISOR = "Carlos Ortiz"
PRODUCCION = "Rosa Méndez"

# Operación, cómo empieza el paso del plan que la usa, ejemplo y minutos que tarda
OPERACIONES = [
    ("asignar_tecnico", "Asignar", "Asignar la OT-523 a Marta Rojas", 5),
    ("consultar_inventario", "Consultar ... inventario", "Consultar el inventario de rodamientos 6206-2RS", 2),
    ("retirar_repuesto", "Retirar ... rodamientos", "Retirar 2 rodamientos 6206-2RS de la bodega de la Planta Sur", 15),
    ("pedir_repuesto", "Pedir ... rodamientos", "Pedir 2 rodamientos 6206-2RS a la Planta Norte", 90),
    ("bloquear", "Bloquear", "Bloquear el compresor 2 con candado y etiqueta", 10),
    ("desacoplar", "Desacoplar", "Desacoplar el motor del compresor", 20),
    ("cambiar_rodamientos", "Cambiar ... rodamientos", "Cambiar los dos rodamientos del motor", 60),
    ("alinear", "Alinear / Acoplar", "Acoplar el motor y alinear el acople", 30),
    ("solicitar_aprobacion", "APROBACIÓN: persona ...", "APROBACIÓN: Carlos Ortiz autoriza retirar el bloqueo y arrancar", 5),
    ("retirar_bloqueo_y_arrancar", "Retirar el bloqueo / Arrancar", "Retirar el bloqueo y arrancar el motor", 10),
    ("prueba_vibracion", "Medir la vibración", "Medir la vibración durante 30 minutos de operación", 30),
    ("detener_y_bloquear", "Detener", "Detener el motor y volver a bloquearlo", 10),
    ("esperar", "Esperar", "Esperar hasta las 16:00 (o: esperar 30 minutos)", 0),
    ("cerrar_orden", "Cerrar / Registrar", "Cerrar la OT-523 con las mediciones", 10),
]

# Cómo se reconoce la operación de un paso: por el verbo con que empieza su acción (sin tildes, en minúsculas)
_REGLAS = [
    ("solicitar_aprobacion", r"^(aprobacion|autorizacion|autorizar|aprobar|solicitar (la )?(aprobacion|autorizacion))"),
    ("retirar_bloqueo_y_arrancar", r"^(retirar (el |los |su )?(bloqueo|candado)|quitar (el )?(bloqueo|candado)|desbloquear|"
                                   r"arrancar|poner en marcha|puesta en marcha)"),
    ("retirar_repuesto", r"^(retirar|sacar|tomar)\b.*\b(rodamiento|repuesto)"),
    ("pedir_repuesto", r"^(pedir|solicitar|trasladar|traer)\b.*\b(rodamiento|repuesto)"),
    ("consultar_inventario", r"^(consultar|revisar|verificar)\b.*\b(inventario|existencias)"),
    ("asignar_tecnico", r"^asignar"),
    ("detener_y_bloquear", r"^(detener|parar|apagar)"),
    ("bloquear", r"^(bloquear|aplicar (el )?bloqueo|poner (el |su )?candado)"),
    ("desacoplar", r"^(desacoplar|retirar (el )?protector)"),
    ("cambiar_rodamientos", r"^(cambiar|reemplazar|instalar|montar|sustituir|desmontar|extraer)\b.*\brodamiento"),
    ("alinear", r"^(alinear|realinear|acoplar|montar (las )?tapas)"),
    ("prueba_vibracion", r"^(medir|prueba|probar|verificar|comprobar)\b.*\bvibracion"),
    ("esperar", r"^esperar"),
    ("cerrar_orden", r"^(cerrar|registrar)\b"),
]
_PERSONAS = {"marta": "Marta Rojas", "rojas": "Marta Rojas", "luis": "Luis Torres", "torres": "Luis Torres",
             "ana": "Ana Gómez", "gomez": "Ana Gómez", "carlos": SUPERVISOR, "ortiz": SUPERVISOR,
             "rosa": PRODUCCION, "mendez": PRODUCCION}
_NUMEROS = {"un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4}


@dataclass
class Observacion:
    """Lo que se observa al hacer una operación."""
    ok: bool
    texto: str
    evidencia: str = ""
    inicio: str = ""
    fin: str = ""


def hora(minuto: int) -> str:
    return f"{minuto // 60:02d}:{minuto % 60:02d}"


def _minuto(texto_hora: str) -> int:
    h, m = texto_hora.split(":")
    return int(h) * 60 + int(m)


def _sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


# ----------------------------------------------------------------------------- interpretar un paso del plan

def _accion(texto: str) -> str:
    """La acción de un paso: el texto antes de «→», «(requiere» o «Resultado»."""
    t = re.split(r"→|\(requiere|\(req\.|resultado\s*:", texto, maxsplit=1, flags=re.I)[0]
    return t.replace("~~", "").replace("**", "").strip()


def _personas(texto: str) -> list:
    """Personas que nombra el texto, en el orden en que aparecen."""
    t = _sin_tildes(texto.lower())
    halladas = []
    for clave, nombre in _PERSONAS.items():
        m = re.search(rf"\b{clave}\b", t)
        if m:
            halladas.append((m.start(), nombre))
    return list(dict.fromkeys(n for _, n in sorted(halladas)))


def interpretar(texto: str) -> dict:
    """Reconoce la operación del simulador que cumple un paso, y sus argumentos.

    Devuelve {"operacion", "argumentos", "problema"}: si el paso no se puede interpretar, «problema»
    explica qué falta en su texto. Interpretar no ejecuta nada.
    """
    accion = _accion(texto)
    a = _sin_tildes(accion.lower())
    completo = _sin_tildes(texto.lower())
    operacion = next((op for op, patron in _REGLAS if re.search(patron, a)), None)
    resultado = {"operacion": operacion, "argumentos": [], "problema": ""}
    if operacion is None:
        resultado["problema"] = ("Ninguna operación del simulador empieza así: únalo al paso que lo cumple o reescríbalo "
                                 "con el verbo de una operación.")
        return resultado
    personas = _personas(accion)
    if operacion == "asignar_tecnico":
        if not personas:
            resultado["problema"] = "No encuentro en el paso a quién se asigna la intervención: escriba su nombre."
        else:
            resultado["argumentos"] = [personas[0]]
    elif operacion in ("retirar_repuesto", "pedir_repuesto"):
        ref = re.search(r"\b(62\d\d-2rs)\b", completo)
        if not ref:
            resultado["problema"] = "El paso no dice qué referencia de rodamiento: escríbala (por ejemplo, 6206-2RS)."
            return resultado
        cantidad = re.search(r"\b(\d+|un|uno|una|dos|tres|cuatro)\s+(unidades|rodamientos|rodamiento)\b", completo)
        n = (int(cantidad.group(1)) if cantidad.group(1).isdigit() else _NUMEROS[cantidad.group(1)]) if cantidad else 2
        resultado["argumentos"] = [ref.group(1).upper(), n]
        if operacion == "pedir_repuesto":
            origen = re.search(r"planta (norte|sur)", completo)
            resultado["argumentos"].append(f"Planta {origen.group(1).capitalize()}" if origen else "Planta Norte")
    elif operacion == "solicitar_aprobacion":
        aprobadores = [n for n in personas if n in (SUPERVISOR, PRODUCCION)] or personas
        if not aprobadores:
            resultado["problema"] = "El paso de aprobación no dice quién aprueba: escriba el nombre de esa persona."
        elif len(aprobadores) > 1:
            resultado["problema"] = (f"El paso nombra a {' y a '.join(aprobadores)}: un paso, una aprobación. Separe cada "
                                     "aprobación en su propio paso.")
        else:
            quien = aprobadores[0]
            extension = bool(re.search(r"extensi|extender|ampliar|ventana|plazo|hasta las", a))
            arranque = bool(re.search(r"arran|bloqueo|candado|marcha", a))
            if extension and arranque:   # el paso menciona las dos cosas: decide quién aprueba
                extension, arranque = quien == PRODUCCION, quien == SUPERVISOR
            if extension:
                resultado["argumentos"] = [quien, "extensión de la ventana"]
            elif arranque:
                resultado["argumentos"] = [quien, "retirar el bloqueo y arrancar"]
            else:
                resultado["problema"] = ("No reconozco qué se aprueba en este paso. Escriba si se autoriza retirar el bloqueo "
                                         "y arrancar, o extender la ventana.")
    elif operacion == "esperar":
        hasta = re.search(r"(\d{1,2}):(\d{2})", a)   # «hasta las 16:00», «a que regrese a las 16:00»
        minutos = re.search(r"(\d+)\s*min", a)
        if hasta:
            resultado["operacion"], resultado["argumentos"] = "esperar_hasta", [f"{int(hasta.group(1)):02d}:{hasta.group(2)}"]
        elif minutos:
            resultado["argumentos"] = [int(minutos.group(1))]
        else:
            resultado["problema"] = "El paso no dice cuánto esperar: escriba los minutos o la hora («hasta las 16:00»)."
    return resultado


# ----------------------------------------------------------------------------- la intervención

class IntervencionOT523:
    """Estado de la intervención OT-523 en un escenario dado."""

    def __init__(self, escenario: str = "sin_falla", documentos: str = "documentos"):
        if escenario not in ESCENARIOS:
            raise ValueError(f"Escenario desconocido: {escenario}. Use uno de: {', '.join(ESCENARIOS)}.")
        self.escenario = escenario
        self.minuto = INICIO
        self.fin_ventana = FIN_VENTANA
        with open(Path(documentos) / "3_certificaciones.csv", encoding="utf-8") as f:
            self.certificaciones = {fila["tecnico"]: fila for fila in csv.DictReader(f)}
        self.inventario = {"6206-2RS": 2, "6205-2RS": 4}
        self.tecnico = None
        self.ausente_hasta = None
        self._ausencia_ocurrio = False
        self.en_mano = None          # (referencia real, cantidad)
        self.bloqueado = False
        self.candado = None
        self.desacoplado = False
        self.instalados = None
        self.alineaciones = 0
        self.aprobaciones = set()
        self.en_marcha = False
        self.vibracion = None
        self.orden_cerrada = False

    # -- utilidades internas
    def _resultado(self, ok, texto, minutos=0, evidencia=""):
        inicio = self.minuto
        self.minuto += minutos
        return Observacion(ok, texto, evidencia, hora(inicio), hora(self.minuto))

    def _rechazo(self, texto):
        """La operación no se hace (no consume tiempo)."""
        return self._resultado(False, texto, 0)

    def _fuera_de_ventana(self, minutos):
        fin = self.minuto + minutos
        if fin > LIMITE_RESPALDO:
            return self._rechazo(f"Esta operación terminaría a las {hora(fin)}, y el compresor de respaldo no puede operar "
                                 "después de las 19:00. La intervención se debe reprogramar.")
        if fin > self.fin_ventana and "extension" not in self.aprobaciones:
            return self._rechazo(f"Esta operación terminaría a las {hora(fin)}, después del fin de la ventana (17:00). "
                                 f"La supervisora de producción, {PRODUCCION}, debe aprobar la extensión antes de continuar.")
        return None

    def _tecnico_disponible(self):
        if self.tecnico is None:
            return self._rechazo("Todavía no hay una persona asignada a la intervención.")
        if self.ausente_hasta and self.minuto < self.ausente_hasta:
            return self._rechazo(f"{self.tecnico} no ha regresado de la emergencia (vuelve a las {hora(self.ausente_hasta)}).")
        return None

    def en_servicio(self) -> bool:
        return (self.en_marcha and self.vibracion is not None and self.vibracion < LIMITE_VIBRACION
                and self.orden_cerrada and not self.bloqueado)

    # -- operaciones
    def asignar_tecnico(self, nombre: str):
        c = self.certificaciones.get(nombre)
        if c is None:
            return self._rechazo(f"No hay registro de certificación para {nombre}.")
        if c["estado"] != "vigente" or "compresor2" not in c["equipos"]:
            return self._rechazo(f"{nombre} no puede intervenir el compresor 2: certificación {c['estado']} "
                                 f"(hasta {c['vigente_hasta']}) para {c['equipos']}.")
        self.tecnico = nombre
        return self._resultado(True, f"{nombre} asignada a la OT-523.", 5,
                               f"{nombre} asignada; certificación vigente hasta {c['vigente_hasta']}")

    def consultar_inventario(self, referencia: str = "6206-2RS", *_):
        n = self.inventario.get(referencia, 0)
        return self._resultado(True, f"Existencias de {referencia} en la bodega de la Planta Sur: {n}.", 2,
                               f"{n} unidades de {referencia} en inventario")

    def retirar_repuesto(self, referencia: str = "6206-2RS", cantidad: int = 2):
        if (falla := self._fuera_de_ventana(15)) is not None:
            return falla
        if self.inventario.get(referencia, 0) < cantidad:
            return self._rechazo(f"No hay {cantidad} unidades de {referencia} en la bodega de la Planta Sur.")
        self.inventario[referencia] -= cantidad
        real = "6205-2RS" if (self.escenario == "rodamiento_equivocado" and referencia == "6206-2RS") else referencia
        self.en_mano = (real, cantidad)
        if real != referencia:
            return self._resultado(False, f"Se retiraron {cantidad} rodamientos de la caja rotulada {referencia}, pero la "
                                          f"referencia grabada en ellos es {real}: no sirven para este motor.", 15)
        return self._resultado(True, f"Se retiraron {cantidad} rodamientos {referencia}; la referencia grabada coincide.", 15,
                               f"salida de inventario de {cantidad} × {referencia}; referencia grabada verificada")

    def pedir_repuesto(self, referencia: str = "6206-2RS", cantidad: int = 2, origen: str = "Planta Norte"):
        if (falla := self._fuera_de_ventana(90)) is not None:
            return falla
        self.en_mano = (referencia, cantidad)
        return self._resultado(True, f"Llegaron {cantidad} rodamientos {referencia} de la {origen}; referencia grabada "
                                     "verificada.", 90, f"remisión de la {origen}; referencia {referencia} verificada")

    def bloquear(self):
        if (falla := self._tecnico_disponible()) is not None:
            return falla
        if (falla := self._fuera_de_ventana(10)) is not None:
            return falla
        self.bloqueado, self.candado, self.en_marcha = True, self.tecnico, False
        return self._resultado(True, f"Candado y etiqueta de {self.tecnico} puestos en el seccionador; energía cero verificada.",
                               10, f"candado de {self.tecnico} puesto; energía cero verificada")

    def desacoplar(self):
        if (falla := self._tecnico_disponible()) is not None:
            return falla
        if not self.bloqueado:
            return self._rechazo("No se puede desacoplar un equipo que no está bloqueado (norma MNT-07).")
        if (falla := self._fuera_de_ventana(20)) is not None:
            return falla
        self.desacoplado = True
        return self._resultado(True, "Protector retirado y motor desacoplado del compresor.", 20, "acople retirado")

    def cambiar_rodamientos(self):
        if self.escenario == "tecnico_ausente" and not self._ausencia_ocurrio and self.tecnico:
            self._ausencia_ocurrio = True
            self.ausente_hasta = 16 * 60
            return self._rechazo(f"Al empezar el cambio, {self.tecnico} fue llamada a una emergencia en la caldera 1 y "
                                 "regresa a las 16:00. Su candado sigue puesto y solo ella puede retirarlo; Luis Torres "
                                 "no puede reemplazarla porque su certificación venció el 30 de septiembre.")
        if (falla := self._tecnico_disponible()) is not None:
            return falla
        if not (self.bloqueado and self.desacoplado):
            return self._rechazo("El motor debe estar bloqueado y desacoplado antes de cambiar los rodamientos.")
        if self.en_mano is None:
            return self._rechazo("No hay rodamientos nuevos en mano.")
        if self.en_mano[0] != "6206-2RS":
            return self._rechazo(f"Los rodamientos {self.en_mano[0]} no ajustan al eje del motor, que usa 6206-2RS.")
        if (falla := self._fuera_de_ventana(60)) is not None:
            return falla
        self.instalados = "6206-2RS"
        return self._resultado(True, "Rodamientos 6206-2RS instalados según el procedimiento del fabricante.", 60,
                               "lista del fabricante, pasos 3 a 5, completa")

    def alinear(self):
        if (falla := self._tecnico_disponible()) is not None:
            return falla
        if not (self.bloqueado and self.instalados):
            return self._rechazo("Para alinear, el motor debe estar bloqueado y con los rodamientos instalados.")
        if (falla := self._fuera_de_ventana(30)) is not None:
            return falla
        self.alineaciones += 1
        return self._resultado(True, "Motor acoplado y acople alineado con el alineador láser: desalineación de 0,03 mm "
                                     "(tolerancia 0,05 mm).", 30, "lectura del alineador láser: 0,03 mm")

    def solicitar_aprobacion(self, quien: str, motivo: str):
        m = _sin_tildes(motivo.lower())
        if any(k in m for k in ("extensi", "ventana", "plazo")):
            if quien != PRODUCCION:
                return self._rechazo(f"La extensión de la ventana la aprueba la supervisora de producción, {PRODUCCION}.")
            self.aprobaciones.add("extension")
            return self._resultado(True, f"{quien} aprobó extender la ventana de mantenimiento hasta las 19:00 como máximo.", 5,
                                   f"aprobación de {quien} registrada en la OT-523")
        if any(k in m for k in ("arran", "bloqueo")):
            if quien != SUPERVISOR:
                return self._rechazo(f"Según la norma MNT-07, autoriza retirar el bloqueo y arrancar el supervisor de "
                                     f"mantenimiento, {SUPERVISOR}.")
            self.aprobaciones.add("arranque")
            return self._resultado(True, f"{quien} autorizó retirar el bloqueo y arrancar.", 5,
                                   f"firma de {quien} en la OT-523")
        return self._rechazo("No reconozco el motivo. Use, por ejemplo, «retirar el bloqueo y arrancar» o «extender la ventana».")

    def retirar_bloqueo_y_arrancar(self):
        if not self.bloqueado:
            return self._rechazo("El equipo no está bloqueado.")
        if "arranque" not in self.aprobaciones:
            return self._rechazo(f"Falta la autorización del supervisor de mantenimiento, {SUPERVISOR} (norma MNT-07).")
        if (falla := self._tecnico_disponible()) is not None:
            return falla
        if self.candado != self.tecnico:
            return self._rechazo(f"Solo {self.candado}, quien puso el candado, puede retirarlo.")
        if (falla := self._fuera_de_ventana(10)) is not None:
            return falla
        self.bloqueado, self.candado, self.en_marcha = False, None, True
        self.aprobaciones.discard("arranque")
        return self._resultado(True, f"{self.tecnico} retiró su candado y arrancó el motor sin alarmas.", 10,
                               "candado retirado por quien lo puso; arranque sin alarmas")

    def prueba_vibracion(self):
        if not self.en_marcha:
            return self._rechazo("El motor debe estar en marcha para medir la vibración.")
        if (falla := self._fuera_de_ventana(30)) is not None:
            return falla
        if self.escenario == "vibracion_alta" and self.alineaciones < 2:
            self.vibracion = 6.3
            return self._resultado(False, "Vibración de 6,3 mm/s después de 30 minutos (límite: 4,5 mm/s). "
                                          "El patrón indica una desalineación del acople.", 30)
        self.vibracion = 2.8
        return self._resultado(True, "Vibración de 2,8 mm/s después de 30 minutos (límite: 4,5 mm/s).", 30,
                               "vibración de 2,8 mm/s tras 30 min")

    def detener_y_bloquear(self):
        if not self.en_marcha:
            return self._rechazo("El motor no está en marcha.")
        if (falla := self._tecnico_disponible()) is not None:
            return falla
        if (falla := self._fuera_de_ventana(10)) is not None:
            return falla
        self.en_marcha, self.bloqueado, self.candado = False, True, self.tecnico
        return self._resultado(True, f"Motor detenido; candado de {self.tecnico} puesto y energía cero verificada.", 10,
                               f"candado de {self.tecnico} puesto; energía cero verificada")

    def esperar(self, minutos: int):
        if (falla := self._fuera_de_ventana(int(minutos))) is not None:
            return falla
        return self._resultado(True, f"Espera de {minutos} minutos.", int(minutos), f"espera de {minutos} min")

    def esperar_hasta(self, texto_hora: str):
        minutos = max(0, _minuto(texto_hora) - self.minuto)
        if (falla := self._fuera_de_ventana(minutos)) is not None:
            return falla
        return self._resultado(True, f"Espera hasta las {texto_hora}.", minutos, f"espera hasta las {texto_hora}")

    def revision_del_plan(self):
        """Revisar y aprobar de nuevo el plan durante la intervención (no es un paso del plan)."""
        return self._resultado(True, "Revisión y nueva aprobación del plan.", 5, "plan revisado y aprobado")

    def cerrar_orden(self):
        if not (self.en_marcha and self.vibracion is not None and self.vibracion < LIMITE_VIBRACION):
            return self._rechazo("No se puede cerrar la orden sin una prueba de vibración aprobada con el motor en marcha.")
        if (falla := self._fuera_de_ventana(10)) is not None:
            return falla
        self.orden_cerrada = True
        return self._resultado(True, "OT-523 cerrada en el sistema de mantenimiento, con las mediciones registradas.", 10,
                               "OT-523 cerrada con mediciones")


def mostrar_operaciones() -> None:
    """Tabla de las operaciones que ofrece el simulador y de cómo debe empezar cada paso del plan que las usa."""
    mostrar_tabla([{"operación": n, "el paso empieza con": inicio, "ejemplo de paso": ejemplo, "minutos": m}
                   for n, inicio, ejemplo, m in OPERACIONES],
                  titulo="Operaciones del simulador de la OT-523 (un paso del plan = una operación)")


def mostrar_correspondencia(plan) -> None:
    """Muestra, para cada paso del plan, la operación del simulador que lo cumpliría. No ejecuta nada."""
    filas, problemas, anterior = [], 0, None
    for p in plan.pasos():
        i = interpretar(p["texto"])
        observacion = i["problema"] or ("ya cumplido" if p["marcado"] else "")
        repetible = i["operacion"] in ("solicitar_aprobacion", "esperar", "esperar_hasta")   # cada aprobación va en su paso
        if not i["problema"] and anterior and anterior[1] == i["operacion"] and not p["marcado"] and not repetible:
            observacion = f"Es la misma operación del paso {anterior[0]}: un paso, una operación. Únalos."
        problemas += bool(i["problema"]) or observacion.startswith("Es la misma")
        anterior = (p["id"], i["operacion"])
        filas.append({"paso": p["id"], "acción": _accion(p["texto"])[:70], "operación": i["operacion"] or "—",
                      "argumentos": ", ".join(str(a) for a in i["argumentos"]) or "—", "observación": observacion})
    mostrar_tabla(filas, titulo="Cómo leerá el simulador cada paso del plan")
    if problemas:
        nota(f"{problemas} paso(s) no se pueden ejecutar tal como están escritos: corríjalos en el archivo del plan antes de "
             "aprobarlo. Cada paso empieza con el verbo de una operación de la tabla; lo que no es una operación (verificar "
             "la referencia, calentar los rodamientos, avisar a alguien) va en el resultado o en la verificación del paso "
             "que lo cumple.", "aviso")
    else:
        nota("El simulador puede ejecutar cada paso del plan.", "exito")


# ----------------------------------------------------------------------------- ejecución del plan

class Ejecucion:
    """Ejecuta, paso a paso, un plan.md aprobado sobre el simulador, y guarda lo ejecutado en disco.

    Ejecucion(plan, escenario) empieza una ejecución o retoma la que está guardada en la carpeta del plan.
    Con desde_cero=True borra la ejecución guardada y desmarca las casillas del plan.
    """

    def __init__(self, plan, escenario: str | None = None, desde_cero: bool = False, mostrar: bool = True):
        self.plan = plan
        self.archivo = plan.ruta.parent / "ejecucion.json"
        guardada = None
        if self.archivo.exists() and not desde_cero:
            guardada = json.loads(self.archivo.read_text(encoding="utf-8"))
        if guardada and not guardada["eventos"]:
            guardada = None   # una ejecución sin operaciones no fija el escenario
        if guardada and escenario and guardada["escenario"] != escenario:
            nota(f"Esta carpeta ya tiene una ejecución con el escenario «{guardada['escenario']}», y se retoma esa. Para "
                 f"empezar otra, use simulador.Ejecucion(plan, \"{escenario}\", desde_cero=True).", "aviso")
        escenario = guardada["escenario"] if guardada else escenario
        if escenario is None:
            raise ValueError("Elija un escenario: " + ", ".join(ESCENARIOS) + ".")
        self.sim = IntervencionOT523(escenario)
        self.eventos, self.falla = [], None
        if guardada:
            for evento in guardada["eventos"]:   # el simulador es determinista: repetir los eventos reconstruye el estado
                getattr(self.sim, evento["operacion"])(*evento["argumentos"])
                self.eventos.append(evento)
            self.falla = guardada.get("falla")
            if mostrar:
                nota(f"Se retomó la ejecución guardada: escenario «{escenario}», {len(self.eventos)} operaciones, "
                     f"hora simulada {hora(self.sim.minuto)}.", "info")
        elif desde_cero:
            self.archivo.unlink(missing_ok=True)
            lineas = [l.replace("- [x]", "- [ ]", 1) if re.match(r"^- \[[xX]\] ", l.strip()) else l
                      for l in plan.texto.splitlines()]
            plan.guardar("\n".join(lineas))
            plan.registrar(hora(INICIO), f"Ejecución reiniciada desde cero (escenario «{escenario}»).")

    # -- estado
    @property
    def escenario(self) -> str:
        return self.sim.escenario

    def hora(self) -> str:
        return hora(self.sim.minuto)

    def evidencias(self) -> set:
        return {e["paso"] for e in self.eventos if e.get("paso") and e["ok"]}

    def _guardar(self) -> None:
        self.archivo.write_text(json.dumps({"escenario": self.escenario, "eventos": self.eventos, "falla": self.falla},
                                           ensure_ascii=False, indent=1), encoding="utf-8")

    def _evento(self, paso, operacion, argumentos, obs) -> None:
        self.eventos.append({"paso": paso, "operacion": operacion, "argumentos": argumentos, **asdict(obs)})
        self._guardar()

    def _lista(self) -> bool:
        if not self.plan.aprobado():
            nota("El plan no está aprobado en su versión actual. Apruébelo (o vuelva a aprobarlo si lo cambió) antes de "
                 "ejecutar.", "error", "No se ejecuta")
            return False
        if self.falla and self.falla["huella"] == self.plan.huella():
            nota(f"Hay una falla sin resolver en el paso {self.falla['paso']}. Los pasos siguientes no se ejecutan sobre un "
                 "plan que ya no describe la realidad: replanifique y vuelva a aprobar.", "aviso", "En espera")
            return False
        return True

    # -- ejecutar
    def ejecutar(self) -> None:
        """Ejecuta en orden los pasos pendientes del plan, hasta terminar, hasta una falla o hasta un paso que no se entiende."""
        if not self._lista():
            return
        pendientes = [p for p in self.plan.pasos() if not p["marcado"]]
        if not pendientes:
            nota("No quedan pasos pendientes en el plan.", "info")
        for p in pendientes:
            if not self._ejecutar_paso(p):
                break

    def paso(self, identificador) -> None:
        """Ejecuta un solo paso del plan (el que tiene ese número)."""
        if not self._lista():
            return
        p = self.plan.paso(identificador)
        if p is None:
            nota(f"El plan no tiene un paso {identificador} pendiente de ejecutar. Revise la numeración en el archivo.", "error")
        elif p["marcado"]:
            nota(f"El paso {identificador} ya está cumplido.", "aviso")
        else:
            self._ejecutar_paso(p)

    def _ejecutar_paso(self, p) -> bool:
        interpretacion = interpretar(p["texto"])
        if interpretacion["problema"]:
            nota(f"«{_accion(p['texto'])[:90]}»\n{interpretacion['problema']}\nNo se ejecutó nada: corrija el paso en el "
                 "archivo del plan (tendrá que aprobarlo de nuevo) y vuelva a ejecutar.", "aviso",
                 f"Paso {p['id']} · no se puede interpretar")
            return False
        operacion, argumentos = interpretacion["operacion"], interpretacion["argumentos"]
        obs = getattr(self.sim, operacion)(*argumentos)
        self._evento(p["id"], operacion, argumentos, obs)
        titulo = f"Paso {p['id']} · {operacion} · {obs.inicio}–{obs.fin}"
        if obs.ok:
            self.plan.marcar(p["id"])
            self.plan.registrar(obs.fin, f"Paso {p['id']} cumplido ({obs.evidencia}).")
            nota(f"✓ {obs.texto}\nVerificación: {obs.evidencia}. Casilla marcada y registro actualizado.", "exito", titulo)
            return True
        self.plan.registrar(obs.fin, f"Paso {p['id']} falló: {obs.texto}")
        self.falla = {"paso": p["id"], "texto": obs.texto, "hora": obs.fin, "huella": self.plan.huella()}
        self._guardar()
        nota(f"✗ {obs.texto}\nLa casilla no se marca. La falla quedó en el registro de avance: toca replanificar.",
             "error", titulo)
        return False

    def aprobar_plan(self, por: str, cargo: str) -> str:
        """Aprueba el plan en la hora simulada actual. Durante la intervención, revisar y aprobar toma 5 minutos."""
        if self.eventos:
            obs = self.sim.revision_del_plan()
            self._evento(None, "revision_del_plan", [], obs)
            return self.plan.aprobar(por=por, cargo=cargo, hora=obs.fin)
        return self.plan.aprobar(por=por, cargo=cargo, hora="12:45")

    # -- cierre
    def verificar_cierre(self) -> None:
        """Comprueba los criterios de aceptación, la evidencia de cada casilla y que el registro conserve la ejecución."""
        pasos = self.plan.pasos()
        evidencias = self.evidencias()
        sin_evidencia = [p["id"] for p in pasos if p["marcado"] and p["id"] not in evidencias]
        pendientes = [p["id"] for p in pasos if not p["marcado"]]
        # Cada operación y cada aprobación debe seguir en el registro tal como se escribió: ni borrada ni cambiada
        registro = "\n".join(self.plan.entradas_registro())
        esperadas = [(f"paso {e['paso']}", f"{e['fin']} · Paso {e['paso']} " +
                      (f"cumplido ({e['evidencia']})." if e["ok"] else f"falló: {e['texto']}"))
                     for e in self.eventos if e.get("paso")]
        esperadas += [(f"aprobación de las {a['fecha'][-5:]}", f"{a['fecha'][-5:]} · Plan aprobado por {a['por']} ({a['cargo']}) "
                       f"· versión {a['version']}.") for a in self.plan._aprobaciones()]
        borradas = [nombre for nombre, linea in esperadas if linea not in registro]
        s = self.sim
        filas = [
            {"comprobación": "Compresor 2 en marcha, sin bloqueo", "resultado": "✓" if s.en_marcha and not s.bloqueado else "✗"},
            {"comprobación": "Vibración menor de 4,5 mm/s",
             "resultado": f"✓ {str(s.vibracion).replace('.', ',')} mm/s" if s.vibracion is not None and s.vibracion < LIMITE_VIBRACION else "✗"},
            {"comprobación": "OT-523 cerrada", "resultado": "✓" if s.orden_cerrada else "✗"},
            {"comprobación": "Dentro de la ventana, o con la extensión aprobada",
             "resultado": "✓" if s.minuto <= FIN_VENTANA or "extension" in s.aprobaciones else "✗"},
            {"comprobación": "Casillas marcadas con evidencia del simulador",
             "resultado": "✓" if not sin_evidencia else f"✗ sin evidencia: {', '.join(sin_evidencia)}"},
            {"comprobación": "El registro conserva cada operación y cada aprobación, sin cambios",
             "resultado": "✓" if not borradas else f"✗ faltan o cambiaron: {', '.join(borradas)}"},
            {"comprobación": "Pasos pendientes", "resultado": "ninguno" if not pendientes else ", ".join(pendientes)},
        ]
        mostrar_tabla(filas, titulo=f"Cierre de la OT-523 · hora simulada {hora(s.minuto)}")
        if s.en_servicio() and not sin_evidencia and not pendientes and not borradas:
            nota("Se cumplen los criterios de aceptación: la intervención terminó, cada casilla tiene evidencia y el registro "
                 "está completo.", "exito")
        elif sin_evidencia:
            nota("Hay casillas marcadas sin evidencia del simulador: alguien las marcó a mano. Una casilla marcada no es una "
                 "prueba.", "error")
        elif borradas:
            nota("Faltan en el registro de avance entradas de la ejecución o de las aprobaciones, o alguien las cambió. El "
                 "registro es la memoria del plan: no se borra ni se corrige. Recupérelas con plan.restaurar_registro(...) "
                 "desde una versión anterior.", "error")
        else:
            nota("La intervención todavía no cumple los criterios de aceptación.", "aviso")


def hay_ejecucion(plan) -> bool:
    """True si la intervención ya empezó: hay operaciones guardadas en la carpeta del plan."""
    archivo = plan.ruta.parent / "ejecucion.json"
    return archivo.exists() and bool(json.loads(archivo.read_text(encoding="utf-8")).get("eventos"))


def retomar(plan):
    """Retoma la ejecución guardada en la carpeta del plan. Devuelve None si la intervención todavía no empieza."""
    return Ejecucion(plan) if hay_ejecucion(plan) else None
