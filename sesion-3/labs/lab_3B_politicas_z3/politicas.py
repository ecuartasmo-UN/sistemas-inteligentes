"""Módulo de apoyo del Laboratorio 3B · Verificar una política de negocio con Z3.

Una política se escribe como dos tablas de texto, sin sintaxis de Z3:

CAMPOS
| campo     | tipo      | valores                              |
| monto     | número    | 1 a 100.000.000                      |
| proveedor | categoría | homologado, no homologado            |
| aprobador | decisión  | supervisor, jefe de planta, gerente  |

REGLAS
| id | si                                        | entonces               |
| R1 | proveedor = homologado y monto < 2000000  | aprobador = supervisor |

- Una condición une comparaciones con «y»: <, <=, >, >=, =, ≠ (también != , ≤ y ≥). «siempre» es una regla sin condición.
- Los números son enteros, dentro del rango de su campo.
- El efecto habla del campo de decisión: «= valor», «= valor1 o valor2» (cualquiera de los dos) o «≠ valor».
- Hay exactamente un campo de tipo decisión. Los números pueden llevar puntos de miles y el signo $.

El módulo traduce las tablas a fórmulas de Z3 y responde tres preguntas: ¿hay casos que nadie puede decidir
sin romper una regla (contradicciones)?, ¿hay casos que ninguna regla decide (lagunas)? y ¿qué pasa en los bordes?
También compara dos versiones de una política, pide a un LLM que la traduzca o que razone sobre ella, y exporta
los resultados al CSV común del contrapunto LLM del curso.
"""
from __future__ import annotations

import csv
import html
import itertools
import json
import re
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from IPython import get_ipython
from IPython.display import HTML, display
from z3 import And, Bool, BoolVal, If, Implies, Int, IntVal, Not, Optimize, Or, Solver, sat, unsat

import presentacion as p

# ----------------------------------------------------------------------------- lectura de las tablas

_OPERADORES = {"<=": "<=", "≤": "<=", ">=": ">=", "≥": ">=", "!=": "≠", "≠": "≠", "<": "<", ">": ">", "=": "="}
_PATRON_TERMINO = re.compile(r"^\s*(.+?)\s*(<=|>=|!=|≠|≤|≥|<|>|=)\s*(.+?)\s*$")


class ErrorPolitica(ValueError):
    """Error al leer una política, con un mensaje en español que dice qué revisar."""


def _mostrar_error(shell, etype, evalue, tb, tb_offset=None):
    """En el notebook, un error de las tablas se muestra como una nota, sin el detalle técnico de Python."""
    p.nota(str(evalue), "error", "Revise la tabla")
    return []


if get_ipython() is not None:
    get_ipython().set_custom_exc((ErrorPolitica,), _mostrar_error)


def _normal(texto: str) -> str:
    """Minúsculas y sin tildes, para comparar nombres de campos y valores."""
    t = unicodedata.normalize("NFD", str(texto).strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _filas(texto: str) -> list[list[str]]:
    """Lee una tabla Markdown: devuelve sus filas de datos, sin el encabezado ni la línea de guiones."""
    filas = []
    for linea in str(texto).strip().splitlines():
        linea = linea.strip()
        if not linea or not linea.startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in celdas if c):
            continue
        filas.append(celdas)
    return filas[1:] if filas else []


def _numero(texto: str, ctx: str) -> int:
    limpio = re.sub(r"[\s$]", "", str(texto))
    if re.fullmatch(r"-?\d+([.,]\d+)+", limpio) and not re.fullmatch(r"-?\d{1,3}([.,]\d{3})+", limpio):
        raise ErrorPolitica(f"{ctx}: «{texto}» parece un número con decimales. Los números deben ser enteros: "
                            "use otra unidad (por ejemplo, minutos en vez de horas) o redondee.")
    limpio = limpio.replace(".", "").replace(",", "")
    if not re.fullmatch(r"-?\d+", limpio):
        raise ErrorPolitica(f"{ctx}: «{texto}» no es un número. Escriba solo cifras, por ejemplo 2000000 o 2.000.000.")
    return int(limpio)


@dataclass
class Campo:
    nombre: str
    tipo: str               # "numero", "categoria" o "decision"
    valores: list = field(default_factory=list)   # categorías, o [mínimo, máximo] para los números


def leer_campos(texto: str) -> dict[str, Campo]:
    campos = {}
    for i, fila in enumerate(_filas(texto), 1):
        if len(fila) < 3:
            raise ErrorPolitica(f"Campos, fila {i}: debe tener tres columnas (campo | tipo | valores).")
        nombre, tipo, valores = fila[0], _normal(fila[1]), fila[2]
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúñÑ_][\wÁÉÍÓÚáéíóúñÑ]*", nombre):
            raise ErrorPolitica(f"Campos, fila {i}: «{nombre}» no sirve como nombre de campo. Use una palabra sin espacios, "
                                "por ejemplo monto o equipo_detenido.")
        if tipo.startswith("numero"):
            m = re.fullmatch(r"\s*(.+?)\s+a\s+(.+?)\s*", valores)
            if not m:
                raise ErrorPolitica(f"Campos, fila {i}: los valores de un número se escriben «mínimo a máximo», "
                                    "por ejemplo «1 a 100.000.000».")
            minimo, maximo = _numero(m.group(1), f"Campo {nombre}"), _numero(m.group(2), f"Campo {nombre}")
            if minimo > maximo:
                raise ErrorPolitica(f"Campo {nombre}: el mínimo ({minimo}) es mayor que el máximo ({maximo}).")
            campos[nombre] = Campo(nombre, "numero", [minimo, maximo])
        elif tipo.startswith("categoria") or tipo.startswith("decision"):
            lista = [v.strip() for v in valores.split(",") if v.strip()]
            if len(lista) < 2:
                raise ErrorPolitica(f"Campo {nombre}: escriba al menos dos valores separados por comas.")
            campos[nombre] = Campo(nombre, "decision" if tipo.startswith("decision") else "categoria", lista)
        else:
            raise ErrorPolitica(f"Campos, fila {i}: el tipo «{fila[1]}» no existe. Use número, categoría o decisión.")
    decisiones = [c for c in campos.values() if c.tipo == "decision"]
    if len(decisiones) != 1:
        raise ErrorPolitica(f"La tabla de campos debe tener exactamente un campo de tipo decisión; tiene {len(decisiones)}.")
    if len(campos) < 2:
        raise ErrorPolitica("La tabla de campos debe tener al menos un campo además de la decisión.")
    return campos


@dataclass
class Termino:
    campo: str
    op: str
    valor: object           # int para números; índice de la categoría para las categorías
    texto: str


@dataclass
class Regla:
    id: str
    si: str
    entonces: str
    terminos: list          # lista de Termino (vacía si «siempre»)
    efecto_op: str          # "=" (alguno de los valores) o "≠"
    efecto_valores: list    # índices de los valores de la decisión

    @property
    def asigna(self) -> bool:
        """True si la regla dice quién decide (efecto «=»); False si solo prohíbe (efecto «≠»)."""
        return self.efecto_op == "="


def _buscar_campo(campos: dict, nombre: str, ctx: str) -> Campo:
    for c in campos.values():
        if _normal(c.nombre) == _normal(nombre):
            return c
    raise ErrorPolitica(f"{ctx}: el campo «{nombre}» no existe. Campos de esta política: {', '.join(campos)}.")


def _indice_valor(campo: Campo, valor: str, ctx: str) -> int:
    for k, v in enumerate(campo.valores):
        if _normal(v) == _normal(valor):
            return k
    raise ErrorPolitica(f"{ctx}: «{valor}» no es un valor de {campo.nombre}. Valores posibles: {', '.join(campo.valores)}.")


def _leer_termino(campos: dict, texto: str, ctx: str) -> Termino:
    if re.search(r"=\s*[<>]", texto):
        raise ErrorPolitica(f"{ctx}: en «{texto.strip()}» escriba primero el signo de comparación: <= o >=, no =< ni =>.")
    m = _PATRON_TERMINO.match(texto)
    if not m:
        raise ErrorPolitica(f"{ctx}: no entiendo «{texto}». Escriba campo, comparación y valor, por ejemplo «monto < 2000000».")
    campo = _buscar_campo(campos, m.group(1), ctx)
    op = _OPERADORES[m.group(2)]
    if campo.tipo == "decision":
        raise ErrorPolitica(f"{ctx}: la decisión ({campo.nombre}) va en la columna «entonces», no en la condición.")
    if campo.tipo == "numero":
        valor = _numero(m.group(3), ctx)
        minimo, maximo = campo.valores
        if not minimo - 1 <= valor <= maximo + 1:
            raise ErrorPolitica(f"{ctx}: {_formato_valor(campo, valor)} está fuera del rango de {campo.nombre} "
                                f"({_formato_valor(campo, minimo)} a {_formato_valor(campo, maximo)}), así que la comparación "
                                "no distingue ningún caso. Revise el número o el rango del campo.")
        return Termino(campo.nombre, op, valor, texto.strip())
    if op not in ("=", "≠"):
        raise ErrorPolitica(f"{ctx}: {campo.nombre} es una categoría: solo admite = o ≠, no «{m.group(2)}».")
    return Termino(campo.nombre, op, _indice_valor(campo, m.group(3), ctx), texto.strip())


def leer_reglas(texto: str, campos: dict) -> list[Regla]:
    decision = next(c for c in campos.values() if c.tipo == "decision")
    reglas, vistos = [], set()
    for i, fila in enumerate(_filas(texto), 1):
        if len(fila) < 3:
            raise ErrorPolitica(f"Reglas, fila {i}: debe tener tres columnas (id | si | entonces).")
        rid, si, entonces = fila[0] or f"fila {i}", fila[1], fila[2]
        if rid in vistos:
            raise ErrorPolitica(f"Reglas: el id {rid} está repetido. Cada regla necesita un id distinto.")
        vistos.add(rid)
        ctx = f"Regla {rid}"
        if _normal(si) in ("siempre", ""):
            terminos = []
        else:
            terminos = []
            for t in re.split(r"\s+[yY]\s+", si.strip()):
                try:
                    terminos.append(_leer_termino(campos, t, ctx))
                except ErrorPolitica:
                    if re.search(r"\s[oO]\s", t):
                        raise ErrorPolitica(f"{ctx}: en la condición, las comparaciones solo se unen con «y». "
                                            "Para «o», escriba dos reglas con el mismo efecto.") from None
                    raise
        m = _PATRON_TERMINO.match(entonces)
        if not m or _OPERADORES[m.group(2)] not in ("=", "≠"):
            raise ErrorPolitica(f"{ctx}: el efecto debe ser «{decision.nombre} = valor» o «{decision.nombre} ≠ valor».")
        if _normal(m.group(1)) != _normal(decision.nombre):
            raise ErrorPolitica(f"{ctx}: el efecto debe hablar del campo de decisión ({decision.nombre}), no de «{m.group(1)}».")
        op = _OPERADORES[m.group(2)]
        valores = [v.strip() for v in re.split(r"\s+o\s+", m.group(3)) if v.strip()]
        if op == "≠" and len(valores) > 1:
            raise ErrorPolitica(f"{ctx}: con ≠ escriba un solo valor; para prohibir varios, use una regla por valor.")
        reglas.append(Regla(rid, si.strip(), entonces.strip(), terminos, op, [_indice_valor(decision, v, ctx) for v in valores]))
    if not reglas:
        raise ErrorPolitica("La tabla de reglas está vacía.")
    return reglas


# ----------------------------------------------------------------------------- resultados

@dataclass
class Hallazgo:
    tipo: str               # "contradicción" o "laguna"
    caso: dict              # valores de los campos que no son la decisión
    reglas: list            # reglas que chocan (contradicción) o que aplican al caso (laguna)
    explicacion: str


def _formato_valor(campo: Campo, valor) -> str:
    if campo.tipo == "numero":
        return f"{valor:,}".replace(",", ".")
    return str(valor)


def describir_caso(politica: "Politica", caso: dict) -> str:
    return ", ".join(f"{n} = {_formato_valor(politica.campos[n], v)}" for n, v in caso.items())


def _decide(ev: dict) -> str:
    """Resumen de lo que decide la política en un caso evaluado."""
    if ev["veredicto"].startswith("laguna"):
        return "nadie: laguna"
    if ev["veredicto"].startswith("contradicción"):
        return "nadie: contradicción"
    return " o ".join(ev["_permitidos"])


def tabla_hallazgos(politica: "Politica", hallazgos: list) -> list[dict]:
    """Los hallazgos de Z3 como filas de una tabla compacta."""
    return [{"problema": f"contradicción entre {' y '.join(h.reglas)}" if h.tipo == "contradicción" else "laguna",
             "caso de ejemplo": describir_caso(politica, h.caso)} for h in hallazgos]


# ----------------------------------------------------------------------------- la política

class Politica:
    """Una política escrita como tablas de campos y reglas, con sus verificaciones en Z3."""

    def __init__(self, campos: str, reglas: str, nombre: str = "Política"):
        self.nombre = nombre
        self.texto_campos, self.texto_reglas = campos, reglas
        self.campos = leer_campos(campos)
        self.reglas = leer_reglas(reglas, self.campos)
        self.decision = next(c for c in self.campos.values() if c.tipo == "decision")
        self.entradas = [c for c in self.campos.values() if c.tipo != "decision"]

    # -- fórmulas
    def _variables(self) -> dict:
        return {c.nombre: Int(c.nombre) for c in self.campos.values()}

    def _dominio(self, v: dict, incluir_decision: bool = False):
        r = []
        for c in self.campos.values():
            if c.tipo == "decision" and not incluir_decision:
                continue
            if c.tipo == "numero":
                r += [v[c.nombre] >= c.valores[0], v[c.nombre] <= c.valores[1]]
            else:
                r += [v[c.nombre] >= 0, v[c.nombre] < len(c.valores)]
        return And(*r)

    @staticmethod
    def _formula_termino(t: Termino, v: dict):
        a, b = v[t.campo], IntVal(t.valor)
        return {"<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b, "=": a == b, "≠": a != b}[t.op]

    def condicion(self, regla: Regla, v: dict):
        return And(*[self._formula_termino(t, v) for t in regla.terminos]) if regla.terminos else BoolVal(True)

    def efecto(self, regla: Regla, decision_valor):
        if regla.efecto_op == "=":
            return Or(*[decision_valor == IntVal(k) for k in regla.efecto_valores])
        return decision_valor != IntVal(regla.efecto_valores[0])

    def _permitido(self, v: dict, k: int):
        """La decisión k cumple todas las reglas que aplican al caso v."""
        return And(*[Implies(self.condicion(r, v), self.efecto(r, IntVal(k))) for r in self.reglas])

    def _caso(self, modelo, v: dict) -> dict:
        caso = {}
        for c in self.entradas:
            valor = modelo.eval(v[c.nombre], model_completion=True).as_long()
            caso[c.nombre] = valor if c.tipo == "numero" else c.valores[valor]
        return caso

    def _fijar(self, v: dict, caso: dict):
        r = []
        for c in self.entradas:
            valor = caso[c.nombre]
            r.append(v[c.nombre] == (IntVal(int(valor)) if c.tipo == "numero" else IntVal(_indice_valor(c, valor, "Caso"))))
        return And(*r)

    def _numerico(self):
        return next((c for c in self.entradas if c.tipo == "numero"), None)

    # -- un caso
    def evaluar(self, caso: dict) -> dict:
        """Qué reglas aplican a un caso concreto, qué valores de la decisión quedan permitidos y el veredicto."""
        faltan = [c.nombre for c in self.entradas if c.nombre not in caso]
        if faltan:
            raise ErrorPolitica(f"Al caso le faltan los campos: {', '.join(faltan)}.")
        v = self._variables()
        fijo = self._fijar(v, caso)
        aplican = []
        for r in self.reglas:
            s = Solver(); s.add(fijo, Not(self.condicion(r, v)))
            if s.check() == unsat:
                aplican.append(r)
        permitidos = []
        for k, nombre in enumerate(self.decision.valores):
            s = Solver(); s.add(fijo, self._permitido(v, k))
            if s.check() == sat:
                permitidos.append(nombre)
        if not any(r.asigna for r in aplican):
            veredicto = "laguna: ninguna regla dice quién decide"
        elif not permitidos:
            veredicto = f"contradicción: ningún valor de {self.decision.nombre} cumple todas las reglas"
        else:
            veredicto = f"{self.decision.nombre}: {' o '.join(permitidos)}"
        return {"caso": describir_caso(self, caso), "reglas que aplican": ", ".join(r.id for r in aplican) or "ninguna",
                "veredicto": veredicto, "_permitidos": permitidos, "_aplican": [r.id for r in aplican]}

    @staticmethod
    def _chocan(reglas, n_valores: int) -> bool:
        """Ningún valor de la decisión cumple a la vez los efectos de estas reglas."""
        for k in range(n_valores):
            if all((k in r.efecto_valores) if r.efecto_op == "=" else (k != r.efecto_valores[0]) for r in reglas):
                return False
        return True

    def _caso_ejemplo(self, v: dict, restricciones: list, evitar: list | None = None) -> dict | None:
        """Un caso que cumple las restricciones. Se prefiere, en orden: que apliquen las menos reglas de «evitar»,
        el mayor valor numérico y los primeros valores de cada categoría."""
        s = Optimize()
        s.add(self._dominio(v), *restricciones)
        if evitar:
            s.minimize(sum(If(c, 1, 0) for c in evitar))
        num = self._numerico()
        if num:
            s.maximize(v[num.nombre])
        for c in self.entradas:
            if c.tipo != "numero":
                s.minimize(v[c.nombre])
        return self._caso(s.model(), v) if s.check() == sat else None

    def _orden(self, hallazgo: "Hallazgo"):
        num = self._numerico()
        return (-(hallazgo.caso[num.nombre] if num else 0),
                [c.valores.index(hallazgo.caso[c.nombre]) for c in self.entradas if c.tipo != "numero"])

    # -- las tres preguntas
    def contradicciones(self, maximo: int = 8) -> list[Hallazgo]:
        """Busca los conjuntos mínimos de reglas que pueden aplicar a la vez y no dejan ningún valor de la decisión.

        Devuelve uno por conjunto, con un caso de ejemplo, ordenados del monto más alto al más bajo. La búsqueda es completa:
        basta revisar conjuntos de hasta tantas reglas como valores tiene la decisión."""
        v = self._variables()
        n = len(self.decision.valores)
        conds = [self.condicion(r, v) for r in self.reglas]
        hallazgos, minimos, vivos, revisados = [], [], [()], 0
        for _ in range(min(len(self.reglas), n)):
            siguientes = []
            for base in vivos:
                for j in range((base[-1] + 1) if base else 0, len(self.reglas)):
                    grupo = base + (j,)
                    if any(set(m) <= set(grupo) for m in minimos):
                        continue
                    revisados += 1
                    if revisados > 5000:
                        p.nota("La política tiene demasiadas reglas que se cruzan: se muestran las contradicciones halladas "
                               "hasta ahora.", "aviso")
                        return sorted(hallazgos, key=self._orden)[:maximo]
                    sol = Solver()
                    sol.add(self._dominio(v), *[conds[i] for i in grupo])
                    if sol.check() != sat:
                        continue                      # estas reglas nunca aplican a la vez
                    reglas = [self.reglas[i] for i in grupo]
                    if self._chocan(reglas, n):
                        minimos.append(grupo)
                        otras = [conds[i] for i in range(len(self.reglas)) if i not in grupo]
                        caso = self._caso_ejemplo(v, [conds[i] for i in grupo], evitar=otras)
                        ids = [r.id for r in reglas]
                        efectos = "; ".join(f"{r.id} dice «{r.entonces}»" for r in reglas)
                        tambien = [x for x in self.evaluar(caso)["_aplican"] if x not in ids]
                        nota = (f" En este caso también aplica{'n' if len(tambien) > 1 else ''} {', '.join(tambien)}, "
                                "pero el choque no depende de esa regla." if tambien else "")
                        hallazgos.append(Hallazgo("contradicción", caso, ids,
                                                  f"Las reglas {', '.join(ids)} aplican a la vez y se contradicen: {efectos}.{nota}"))
                    else:
                        siguientes.append(grupo)
            vivos = siguientes
        return sorted(hallazgos, key=self._orden)[:maximo]

    def lagunas(self, maximo: int = 8) -> list[Hallazgo]:
        """Busca casos que ninguna regla decide (ninguna regla con efecto «=» aplica), uno por cada zona distinta."""
        v = self._variables()
        terminos = [self._formula_termino(t, v) for r in self.reglas for t in r.terminos]
        sin_regla = [Not(self.condicion(r, v)) for r in self.reglas if r.asigna]
        hallazgos, bloqueos = [], []
        for _ in range(maximo):
            s = Solver()
            s.add(self._dominio(v), *sin_regla, *bloqueos)
            if s.check() != sat:
                break
            m = s.model()
            # la zona: la combinación de verdad de las comparaciones de la política en ese caso
            firma = [t if m.eval(t, model_completion=True) else Not(t) for t in terminos]
            caso = self._caso_ejemplo(v, sin_regla + firma)
            aplican = self.evaluar(caso)["_aplican"]
            hallazgos.append(Hallazgo("laguna", caso, aplican,
                                      "Ninguna regla dice quién decide este caso"
                                      + (f" (solo aplican prohibiciones: {', '.join(aplican)})." if aplican else ".")))
            bloqueos.append(Not(And(*firma)) if firma else BoolVal(False))
        return sorted(hallazgos, key=self._orden)

    def bordes(self) -> list[dict]:
        """Evalúa los casos justo antes, en y justo después de cada umbral de cada campo numérico de las reglas.

        Los demás campos toman sus valores extremos (los números) o cada uno de sus valores (las categorías)."""
        filas, vistos = [], set()
        for num in [c for c in self.entradas if c.tipo == "numero"]:
            umbrales = sorted({t.valor for r in self.reglas for t in r.terminos if t.campo == num.nombre})
            valores = sorted({x for u in umbrales for x in (u - 1, u, u + 1) if num.valores[0] <= x <= num.valores[1]})
            otras = [c for c in self.entradas if c is not num]
            combinaciones = list(itertools.product(*[c.valores for c in otras])) or [()]
            for combo in combinaciones[:8]:
                fijos = dict(zip([c.nombre for c in otras], combo))
                for x in valores:
                    caso = {c.nombre: (x if c is num else fijos[c.nombre]) for c in self.entradas}
                    clave = tuple(caso.values())
                    if clave in vistos:
                        continue
                    vistos.add(clave)
                    ev = self.evaluar(caso)
                    filas.append({"caso": ev["caso"], "reglas que aplican": ev["reglas que aplican"], "veredicto": ev["veredicto"]})
        return filas

    # -- comparar dos versiones
    def comparar(self, otra: "Politica") -> list[dict]:
        """Compara regla por regla con otra versión de la política (por ejemplo, la traducción de un LLM).

        Para cada regla que cambia, muestra un caso donde las dos versiones difieren y qué decide cada política en él."""
        if [c.nombre for c in self.campos.values()] != [c.nombre for c in otra.campos.values()]:
            raise ErrorPolitica("Las dos políticas deben tener los mismos campos para compararlas regla por regla.")
        a_nombre, b_nombre = self.nombre, (otra.nombre if otra.nombre != self.nombre else otra.nombre + " (otra)")
        v = self._variables()
        d = Int(self.decision.nombre)
        mias, suyas = {r.id: r for r in self.reglas}, {r.id: r for r in otra.reglas}
        filas = []
        for rid in list(mias) + [x for x in suyas if x not in mias]:
            a, b = mias.get(rid), suyas.get(rid)
            texto_a = f"{a.si} → {a.entonces}" if a else "(no está)"
            texto_b = f"{b.si} → {b.entonces}" if b else "(no está)"
            if not a or not b:
                filas.append({"regla": rid, a_nombre: texto_a, b_nombre: texto_b, "resultado": "está solo en una de las dos"})
                continue
            ca, cb = self.condicion(a, v), otra.condicion(b, v)
            s = Solver()
            s.add(self._dominio(v), d >= 0, d < len(self.decision.valores),
                  Or(ca != cb, And(ca, cb, self.efecto(a, d) != otra.efecto(b, d))))
            if s.check() == sat:
                caso = self._caso(s.model(), v)
                resultado = (f"difiere en {describir_caso(self, caso)}: {a_nombre} decide «{_decide(self.evaluar(caso))}»; "
                             f"{b_nombre} decide «{_decide(otra.evaluar(caso))}»")
            else:
                resultado = "igual"
            filas.append({"regla": rid, a_nombre: texto_a, b_nombre: texto_b, "resultado": resultado})
        return filas

    # -- presentación
    def mostrar(self) -> None:
        p.mostrar_tabla([{"campo": c.nombre, "tipo": c.tipo.replace("numero", "número").replace("categoria", "categoría")
                          .replace("decision", "decisión"),
                          "valores": (f"{_formato_valor(c, c.valores[0])} a {_formato_valor(c, c.valores[1])}"
                                      if c.tipo == "numero" else ", ".join(c.valores))} for c in self.campos.values()],
                        titulo=f"{self.nombre}: campos")
        p.mostrar_tabla([{"id": r.id, "si": r.si, "entonces": r.entonces,
                          "tipo": "decide" if r.asigna else "prohíbe"} for r in self.reglas], titulo=f"{self.nombre}: reglas")

    def mapa(self) -> None:
        """Dibuja la política como un mapa de casos: el eje horizontal es el campo numérico, cada fila una combinación."""
        num = self._numerico()
        if not num:
            p.nota("El mapa necesita un campo numérico.", "aviso")
            return
        otras = [c for c in self.entradas if c is not num]
        combos = list(itertools.product(*[c.valores for c in otras])) or [()]
        if len(combos) > 6:
            p.nota("Hay demasiadas combinaciones para dibujar el mapa: use la tabla de bordes.", "aviso")
            return
        umbrales = sorted({t.valor for r in self.reglas for t in r.terminos if t.campo == num.nombre}
                          | {num.valores[0], num.valores[1]})
        # tramos: cada umbral es un punto y entre dos umbrales hay un intervalo
        tramos = []
        for i, u in enumerate(umbrales):
            tramos.append(("punto", u))
            if i + 1 < len(umbrales) and umbrales[i + 1] - u > 1:
                tramos.append(("intervalo", (u + 1, umbrales[i + 1] - 1)))
        paleta = ["#38bdf8", "#f5b942", "#a78bfa", "#4ade80", "#fb923c", "#f472b6"]
        color = {v: paleta[k % len(paleta)] for k, v in enumerate(self.decision.valores)}
        ancho_p, alto, x0 = 14, 34, 190
        n_i = sum(t == "intervalo" for t, _ in tramos)
        # los intervalos se angostan para que el mapa quepa en unos 900 px; si no cabe, el SVG se escala
        ancho_i = max(90, min(120, (900 - x0 - 20 - (len(tramos) - n_i) * ancho_p) // max(n_i, 1)))
        ancho = x0 + sum(ancho_i if t == "intervalo" else ancho_p for t, _ in tramos) + 20
        filas_svg, y = [], 30
        for combo in combos:
            etiqueta = " · ".join(str(x) for x in combo) or num.nombre
            filas_svg.append(f"<text x='{x0 - 10}' y='{y + 22}' text-anchor='end' font-size='13' fill='#1f2328'>{html.escape(etiqueta)}</text>")
            x = x0
            for tipo, val in tramos:
                w = ancho_i if tipo == "intervalo" else ancho_p
                muestra = (val[0] + val[1]) // 2 if tipo == "intervalo" else val
                caso = {num.nombre: muestra, **{c.nombre: v for c, v in zip(otras, combo)}}
                ev = self.evaluar(caso)
                if ev["veredicto"].startswith("laguna"):
                    relleno, texto = "#ffffff", "laguna"
                    borde = "stroke='#dc2626' stroke-width='3'"
                elif ev["veredicto"].startswith("contradicción"):
                    relleno, texto, borde = "url(#rayas)", "choque", "stroke='#dc2626' stroke-width='2'"
                else:
                    relleno = color[ev["_permitidos"][0]] if len(ev["_permitidos"]) == 1 else "#cbd5e1"
                    texto, borde = (ev["_permitidos"][0] if len(ev["_permitidos"]) == 1 else "varios"), "stroke='#ffffff'"
                filas_svg.append(f"<rect x='{x}' y='{y}' width='{w}' height='{alto}' fill='{relleno}' {borde}>"
                                 f"<title>{html.escape(ev['caso'])}: {html.escape(ev['veredicto'])}</title></rect>")
                if tipo == "intervalo":
                    filas_svg.append(f"<text x='{x + w / 2}' y='{y + 22}' text-anchor='middle' font-size='12' fill='#0a0e17'>"
                                     f"{html.escape(texto)}</text>")
                x += w
            y += alto + 8
        x, ejes = x0, []
        for tipo, val in tramos:
            w = ancho_i if tipo == "intervalo" else ancho_p
            if tipo == "punto":
                ejes.append(f"<text x='{x + w / 2}' y='{y + 14}' text-anchor='middle' font-size='11' fill='#57606a'>"
                            f"{html.escape(_formato_valor(num, val))}</text>")
            x += w
        leyenda = " · ".join(f"<span style='color:{color[v]};font-weight:700'>■</span> {html.escape(v)}" for v in self.decision.valores)
        svg = (f"<svg width='{ancho}' height='{y + 30}' viewBox='0 0 {ancho} {y + 30}' "
               "style='max-width:100%;height:auto;background:#ffffff;font-family:system-ui,sans-serif'>"
               "<defs><pattern id='rayas' width='8' height='8' patternTransform='rotate(45)' patternUnits='userSpaceOnUse'>"
               "<rect width='8' height='8' fill='#fde2e2'/><line x1='0' y1='0' x2='0' y2='8' stroke='#dc2626' stroke-width='3'/></pattern></defs>"
               f"<text x='{x0}' y='18' font-size='13' fill='#1f2328' font-weight='700'>{html.escape(self.nombre)}: quién decide según {html.escape(num.nombre)}</text>"
               + "".join(filas_svg) + "".join(ejes) + "</svg>")
        display(HTML(f"<div style='overflow-x:auto;background:#ffffff;border:1px solid #d0d7de;border-radius:8px;padding:8px'>{svg}"
                     f"<div style='font:13px system-ui;color:#1f2328;margin-top:4px'>{leyenda} · "
                     "<span style='color:#cbd5e1;font-weight:700'>■</span> varios (sirve cualquiera de los permitidos) · "
                     "<span style='color:#dc2626;font-weight:700'>▨</span> choque (contradicción) · "
                     "<span style='color:#dc2626;font-weight:700'>□</span> laguna. "
                     "Las columnas angostas son los valores exactos de cada umbral; pase el cursor sobre un tramo para ver el caso.</div></div>"))


def mostrar_hallazgos(politica: Politica, hallazgos: list[Hallazgo], tipo: str) -> None:
    """Muestra las contradicciones o lagunas como contraejemplos en recuadros."""
    if not hallazgos:
        p.caja(f"<b>Z3: unsat.</b> No existe ningún caso con {('contradicciones' if tipo == 'contradicción' else 'lagunas')} "
               "en esta política. No es que no lo haya encontrado: demostró que no lo hay.", "exito",
               f"Sin {('contradicciones' if tipo == 'contradicción' else 'lagunas')}")
        return
    for i, h in enumerate(hallazgos, 1):
        p.caja(f"<b>Caso:</b> {html.escape(describir_caso(politica, h.caso))}<br>{html.escape(h.explicacion)}", "error",
               f"Z3: sat · {tipo} {i} de {len(hallazgos)}")


# ----------------------------------------------------------------------------- el LLM

_NOTACION = """Notación de la tabla:
- «si»: comparaciones unidas con « y », cada una con la forma «campo comparación valor», usando <, <=, >, >=, = o ≠;
  o la palabra «siempre» si la regla no tiene condición. Los números van en cifras, sin puntos ni signo $.
- «entonces»: «{d} = VALOR», «{d} = VALOR1 o VALOR2» (cualquiera de los dos sirve) o «{d} ≠ VALOR» (prohíbe ese valor)."""


def instruccion_traducir(politica_campos: str) -> str:
    campos = leer_campos(politica_campos)
    d = next(c for c in campos.values() if c.tipo == "decision").nombre
    lineas = []
    for c in campos.values():
        if c.tipo == "numero":
            lineas.append(f"- {c.nombre}: número entero, de {c.valores[0]} a {c.valores[1]}.")
        else:
            lineas.append(f"- {c.nombre}{' (la decisión)' if c.tipo == 'decision' else ''}: {' | '.join(c.valores)}.")
    return ("Traduces políticas escritas a una tabla de reglas que luego verifica un solver lógico.\n"
            "Campos disponibles (use exactamente estos nombres y valores):\n" + "\n".join(lineas) + "\n"
            + _NOTACION.format(d=d) + "\n"
            "Una fila por cada regla del texto, con el mismo id. "
            'Responda solo un arreglo JSON de objetos {"id": ..., "si": ..., "entonces": ...}, sin otro texto.')


def _extraer_json(texto: str):
    bloques = re.findall(r"```(?:json)?\s*(.*?)```", texto, re.S) or [texto]
    for b in reversed(bloques):
        for patron in (r"\[.*\]", r"\{.*\}"):
            m = re.search(patron, b, re.S)
            if m:
                try:
                    return json.loads(m.group(0))
                except json.JSONDecodeError:
                    continue
    return None


@dataclass
class ResultadoLLM:
    estrategia: str
    politica: Politica | None = None
    casos: dict = field(default_factory=dict)
    conversacion: list = field(default_factory=list)
    respuestas: list = field(default_factory=list)
    error: str = ""

    def metricas(self) -> dict:
        r = self.respuestas
        costos = [x.costo_usd for x in r if x.costo_usd is not None]
        return {"llamadas": len(r), "tokens_entrada": sum(x.tokens_entrada for x in r),
                "tokens_salida": sum(x.tokens_salida for x in r), "tokens_razonamiento": sum(x.tokens_razonamiento for x in r),
                "costo_usd": round(sum(costos), 6) if costos else "", "tiempo_s": round(sum(x.segundos for x in r), 2),
                "proveedor": r[-1].proveedor if r else "", "modelo": r[-1].modelo if r else ""}


def traducir(llm, texto_politica: str, campos: str, etiqueta: str = "3b/traduccion", intentos: int = 3,
             nombre: str = "Traducción del LLM") -> ResultadoLLM:
    """El LLM traduce el texto de la política a la tabla de reglas. Si la tabla no se puede leer, el error vuelve al LLM."""
    sistema = instruccion_traducir(campos)
    mensajes = [{"role": "user", "content": texto_politica}]
    res = ResultadoLLM("traducir")
    res.conversacion = [{"rol": "system", "contenido": sistema}, {"rol": "user", "contenido": texto_politica}]
    for i in range(intentos):
        r = llm.completar(mensajes, sistema=sistema, etiqueta=f"{etiqueta}/{i}", max_tokens_respuesta=1500)
        res.respuestas.append(r)
        if not r.disponible:
            res.error = r.texto
            return res
        res.conversacion.append({"rol": "assistant", "contenido": r.texto})
        datos = _extraer_json(r.texto)
        try:
            if not isinstance(datos, list) or not datos:
                raise ErrorPolitica("La respuesta no tiene un arreglo JSON de reglas.")
            filas = "| id | si | entonces |\n" + "\n".join(
                f"| {d.get('id', '')} | {d.get('si', '')} | {d.get('entonces', '')} |" for d in datos)
            res.politica = Politica(campos, filas, nombre)
            return res
        except ErrorPolitica as e:
            critica = (f"La tabla no se pudo leer: {e} Corrija ese punto y responda de nuevo solo el arreglo JSON completo.")
            res.conversacion.append({"rol": "critica", "contenido": critica})
            mensajes += [{"role": "assistant", "content": r.texto}, {"role": "user", "content": critica}]
            res.error = str(e)
    return res


def instruccion_razonar(politica_campos: str) -> str:
    campos = leer_campos(politica_campos)
    d = next(c for c in campos.values() if c.tipo == "decision")
    entradas = [c for c in campos.values() if c.tipo != "decision"]
    ejemplo = ", ".join(f'"{c.nombre}": {c.valores[0] if c.tipo == "numero" else json.dumps(c.valores[0], ensure_ascii=False)}'
                        for c in entradas)
    return (f"Eres un auditor de políticas. Revisa la política y responde dos preguntas:\n"
            f"1. ¿Hay algún caso en que ningún valor de {d.nombre} cumple todas las reglas a la vez (una contradicción)?\n"
            f"2. ¿Hay algún caso para el que ninguna regla dice qué {d.nombre} corresponde (una laguna)?\n"
            "Los campos son: " + "; ".join(f"{c.nombre} ({'número' if c.tipo == 'numero' else ' | '.join(c.valores)})" for c in entradas)
            + ". Piensa paso a paso y sé breve. Al final, escribe un bloque JSON con esta forma, con un caso concreto por cada problema "
            'que encuentres (listas vacías si no hay):\n{"contradicciones": [{' + ejemplo + '}], "lagunas": [{' + ejemplo + "}]}")


def razonar(llm, texto_politica: str, campos: str, etiqueta: str = "3b/razonar") -> ResultadoLLM:
    """El LLM razona solo sobre la política y propone casos concretos de contradicción y de laguna."""
    sistema = instruccion_razonar(campos)
    res = ResultadoLLM("razonar")
    res.conversacion = [{"rol": "system", "contenido": sistema}, {"rol": "user", "contenido": texto_politica}]
    r = llm.completar([{"role": "user", "content": texto_politica}], sistema=sistema, etiqueta=etiqueta,
                      max_tokens_respuesta=3000)
    res.respuestas.append(r)
    res.conversacion.append({"rol": "assistant", "contenido": r.texto})
    if not r.disponible:
        res.error = r.texto
        return res
    datos = _extraer_json(r.texto)
    if not isinstance(datos, dict):
        res.error = "El LLM no terminó con el bloque JSON de casos (pudo agotar su límite de salida)."
        return res
    res.casos = {"contradicción": datos.get("contradicciones") or [], "laguna": datos.get("lagunas") or []}
    return res


def revisar_casos_del_llm(politica: Politica, res: ResultadoLLM) -> list[dict]:
    """Comprueba con Z3 cada caso que propuso el LLM: ¿es de verdad una contradicción o una laguna?"""
    filas = []
    for tipo, casos in res.casos.items():
        for caso in casos:
            try:
                ev = politica.evaluar({c.nombre: caso.get(c.nombre) for c in politica.entradas})
                real = ev["veredicto"].startswith(tipo)
                filas.append({"el LLM dice": tipo, "caso": ev["caso"], "Z3 dice": ev["veredicto"],
                              "¿es real?": "sí" if real else "no"})
            except (ErrorPolitica, TypeError, ValueError) as e:
                filas.append({"el LLM dice": tipo, "caso": json.dumps(caso, ensure_ascii=False), "Z3 dice": f"no se pudo leer: {e}",
                              "¿es real?": "no"})
    return filas


def cobertura(politica: Politica, res: ResultadoLLM, contradicciones: list[Hallazgo], lagunas: list[Hallazgo]) -> list[dict]:
    """Para cada problema que encontró Z3, ¿lo encontró también el LLM con alguno de sus casos?"""
    filas = []
    revisados = []
    for tipo, casos in res.casos.items():
        for caso in casos:
            try:
                ev = politica.evaluar({c.nombre: caso.get(c.nombre) for c in politica.entradas})
                revisados.append((tipo, caso, ev))
            except (ErrorPolitica, TypeError, ValueError):
                pass
    for h in contradicciones:
        encontrado = any(t == "contradicción" and ev["veredicto"].startswith("contradicción")
                         and set(h.reglas) <= set(ev["_aplican"]) for t, _, ev in revisados)
        filas.append({"problema que encontró Z3": f"contradicción entre {', '.join(h.reglas)}",
                      "caso de Z3": describir_caso(politica, h.caso), "¿lo encontró el LLM?": "sí" if encontrado else "no"})
    for h in lagunas:
        encontrado = any(t == "laguna" and ev["veredicto"].startswith("laguna") for t, _, ev in revisados)
        filas.append({"problema que encontró Z3": "laguna", "caso de Z3": describir_caso(politica, h.caso),
                      "¿lo encontró el LLM?": "sí" if encontrado else "no"})
    return filas


# ----------------------------------------------------------------------------- CSV común del contrapunto LLM

COLUMNAS_CSV = ["sesion", "laboratorio", "pareja", "fecha", "tarea", "instancia", "metodo", "estrategia", "proveedor",
                "modelo", "correcto", "resultado", "iteraciones", "llamadas", "tokens_entrada", "tokens_salida",
                "tokens_razonamiento", "costo_usd", "tiempo_s", "notas"]


def fila_csv(instancia: str, metodo: str, estrategia: str, correcto: bool, resultado: str, metricas: dict | None = None,
             iteraciones: int = 1, notas: str = "") -> dict:
    m = metricas or {}
    return {"sesion": 3, "laboratorio": "3B", "fecha": date.today().isoformat(), "tarea": "verificar una política",
            "instancia": instancia, "metodo": metodo, "estrategia": estrategia, "proveedor": m.get("proveedor", ""),
            "modelo": m.get("modelo", ""), "correcto": int(bool(correcto)), "resultado": resultado,
            "iteraciones": iteraciones, "llamadas": m.get("llamadas", 0), "tokens_entrada": m.get("tokens_entrada", 0),
            "tokens_salida": m.get("tokens_salida", 0), "tokens_razonamiento": m.get("tokens_razonamiento", 0),
            "costo_usd": m.get("costo_usd", 0), "tiempo_s": m.get("tiempo_s", ""), "notas": notas}


def exportar_csv(filas: list[dict], pareja: str, ruta: str = "resultados_3B.csv") -> Path:
    destino = Path(ruta)
    with destino.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS_CSV)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({**fila, "pareja": pareja})
    return destino


def medir(funcion, *args, **kwargs):
    """Ejecuta una verificación de Z3 y devuelve su resultado y los segundos que tardó."""
    t0 = time.perf_counter()
    resultado = funcion(*args, **kwargs)
    return resultado, round(time.perf_counter() - t0, 3)
