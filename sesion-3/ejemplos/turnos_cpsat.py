"""Turnos del equipo de mantenimiento de MantenIA con CP-SAT (ejemplo de la charla inicial).

Ejecutar:  python turnos_cpsat.py      (requiere: pip install "ortools==9.15.*")

Escenarios:
  1. Las cuatro reglas duras y las dos preferencias: CP-SAT encuentra la mejor asignación.
  2. Se agrega una regla de seguridad nueva que choca con la de descanso: no hay solución,
     y CP-SAT señala qué reglas entran en conflicto.
  3. Dos formas de relajar el conflicto, cada una con su costo para el negocio.
"""
from ortools.sat.python import cp_model

TECNICOS = ["Ana", "Marta", "Luis", "Jorge"]
CERTIFICADOS = {"Ana", "Marta"}          # certificación vigente; la de Luis venció y Jorge está en formación
DIAS = ["Lun", "Mar", "Mié"]
TURNOS = ["Día", "Noche"]


def resolver(escenario: str, apagadas=()):
    m = cp_model.CpModel()
    x = {(t, d, s): m.NewBoolVar(f"{t}_{d}_{s}") for t in TECNICOS for d in DIAS for s in TURNOS}
    reglas = {}  # nombre de la regla -> literal que la activa (para diagnosticar conflictos)

    def regla(nombre):
        reglas[nombre] = m.NewBoolVar(nombre)
        return reglas[nombre]

    # D1 · Cobertura: cada turno de cada día tiene al menos un técnico
    r = regla("D1 cobertura")
    for d in DIAS:
        for s in TURNOS:
            m.Add(sum(x[t, d, s] for t in TECNICOS) >= 1).OnlyEnforceIf(r)
    # D2 · Un solo turno por día para cada técnico
    r = regla("D2 un turno por día")
    for t in TECNICOS:
        for d in DIAS:
            m.Add(sum(x[t, d, s] for s in TURNOS) <= 1).OnlyEnforceIf(r)
    # D3 · Descanso: quien trabaja de noche no trabaja el turno de día siguiente
    r = regla("D3 descanso tras la noche")
    for t in TECNICOS:
        for i in range(len(DIAS) - 1):
            m.AddImplication(x[t, DIAS[i], "Noche"], x[t, DIAS[i + 1], "Día"].Not()).OnlyEnforceIf(r)
    # D4 · Competencia: cada noche hay al menos un técnico certificado
    certificados_por_noche = 2 if escenario in ("conflicto", "permitir_noches_seguidas") else 1
    r = regla(f"D4 {certificados_por_noche} certificado(s) por noche")
    for d in DIAS:
        m.Add(sum(x[t, d, "Noche"] for t in CERTIFICADOS) >= certificados_por_noche).OnlyEnforceIf(r)
    # D5 · Regla de descanso adicional de los escenarios 2 y 3a: nadie trabaja dos noches seguidas
    if escenario in ("conflicto", "un_certificado"):
        r = regla("D5 no dos noches seguidas")
        for t in TECNICOS:
            for i in range(len(DIAS) - 1):
                m.Add(x[t, DIAS[i], "Noche"] + x[t, DIAS[i + 1], "Noche"] <= 1).OnlyEnforceIf(r)

    # Las reglas duras quedan activas: se declaran como supuestos para que CP-SAT
    # pueda decir cuáles chocan si no hay solución
    m.AddAssumptions([lit for nombre, lit in reglas.items() if nombre not in apagadas])

    # Preferencias (restricciones blandas) en el objetivo
    # B1 · Marta pidió no trabajar el miércoles (cita médica)
    b1 = sum(x["Marta", "Mié", s] for s in TURNOS)
    # B2 · Equidad: la diferencia entre quien más y quien menos turnos tiene
    carga = {t: sum(x[t, d, s] for d in DIAS for s in TURNOS) for t in TECNICOS}
    mx, mn = m.NewIntVar(0, 6, "max"), m.NewIntVar(0, 6, "min")
    m.AddMaxEquality(mx, list(carga.values()))
    m.AddMinEquality(mn, list(carga.values()))
    # B3 · No asignar más turnos de los necesarios
    total = sum(x.values())
    m.Minimize(10 * b1 + 3 * total + 2 * (mx - mn))

    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.random_seed = 0
    estado = solver.Solve(m)
    return solver, estado, x, reglas, carga


def mostrar(titulo, escenario):
    solver, estado, x, reglas, carga = resolver(escenario)
    print(f"\n=== {titulo} ===")
    print("Estado:", solver.StatusName(estado))
    if estado in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f"{'':8}" + "".join(f"{d}-{s:<7}" for d in DIAS for s in TURNOS))
        for t in TECNICOS:
            fila = "".join(f"{'  ■':<11}" if solver.Value(x[t, d, s]) else f"{'  ·':<11}" for d in DIAS for s in TURNOS)
            print(f"{t:<8}{fila}  turnos: {solver.Value(carga[t])}")
        print("Objetivo:", int(solver.ObjectiveValue()))
    elif estado == cp_model.INFEASIBLE:
        # CP-SAT devuelve un conjunto de reglas que basta para el conflicto, no siempre el mínimo.
        # Se reduce probando a quitar una regla a la vez: si sin ella sigue sin solución, sobra.
        indices = solver.SufficientAssumptionsForInfeasibility()
        conflicto = [n for n, lit in reglas.items() if lit.Index() in indices]
        for nombre in list(conflicto):
            resto = [n for n in conflicto if n != nombre]
            apagadas = [n for n in reglas if n not in resto]
            s2, e2, *_ = resolver(escenario, apagadas)
            if e2 == cp_model.INFEASIBLE:
                conflicto = resto
        print("No hay solución. Reglas que entran en conflicto:", " + ".join(conflicto))


if __name__ == "__main__":
    mostrar("1. Reglas D1 a D4 y preferencias", "base")
    mostrar("2. Nueva regla de seguridad (2 certificados por noche) y nadie dos noches seguidas", "conflicto")
    mostrar("3a. Relajar D4: se vuelve a 1 certificado por noche", "un_certificado")
    mostrar("3b. Relajar D5: se permiten noches seguidas", "permitir_noches_seguidas")
