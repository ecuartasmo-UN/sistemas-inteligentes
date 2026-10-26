"""Política de compras de repuestos de MantenIA verificada con Z3 (ejemplo de la charla intermedia).

Ejecutar:  python politica_z3.py      (requiere: pip install z3-solver)

La política, tal como está escrita:
  R1. Las compras a proveedores homologados de menos de $2.000.000 las aprueba el supervisor.
  R2. Las compras a proveedores homologados de más de $2.000.000 y hasta $10.000.000 las aprueba
      el jefe de planta.
  R3. Las compras de más de $10.000.000 las aprueba el gerente.
  R4. Las compras a proveedores no homologados las aprueba el gerente.
  R5. El gerente no aprueba compras de menos de $1.000.000.

Z3 responde tres preguntas:
  1. ¿Hay alguna compra que la política no deja aprobar a nadie? (contradicción)
  2. ¿Hay alguna compra a un proveedor homologado que ninguna regla cubre? (laguna)
  3. Después de corregir R1 y R5, ¿queda alguna de las dos? Si Z3 responde «unsat», no existe
     ningún caso así: no es que no lo haya encontrado, es que demostró que no lo hay.
"""
from z3 import And, Bool, Implies, Int, IntVal, Not, Optimize, Or, Solver, sat

SUPERVISOR, JEFE, GERENTE = 0, 1, 2
NOMBRE = {SUPERVISOR: "supervisor", JEFE: "jefe de planta", GERENTE: "gerente"}

monto = Int("monto")                # en pesos
homologado = Bool("homologado")     # ¿el proveedor está homologado?
CASO_VALIDO = And(monto >= 1, monto <= 100_000_000)


def reglas(aprobador, corregida=False):
    """Las reglas de la política para una compra (monto, homologado) aprobada por `aprobador`."""
    limite_r1 = monto <= 2_000_000 if corregida else monto < 2_000_000
    r5 = Implies(And(monto < 1_000_000, homologado), aprobador != GERENTE) if corregida \
        else Implies(monto < 1_000_000, aprobador != GERENTE)
    return And(
        Implies(And(limite_r1, homologado), aprobador == SUPERVISOR),                         # R1
        Implies(And(monto > 2_000_000, monto <= 10_000_000, homologado), aprobador == JEFE),  # R2
        Implies(monto > 10_000_000, aprobador == GERENTE),                                    # R3
        Implies(Not(homologado), aprobador == GERENTE),                                       # R4
        r5,                                                                                   # R5
    )


def nadie_puede_aprobar(corregida=False):
    """Una compra para la que ningún aprobador cumple todas las reglas a la vez."""
    return And(*[Not(reglas(IntVal(a), corregida)) for a in NOMBRE])


def ninguna_regla_cubre(corregida=False):
    """Una compra a proveedor homologado en la que ninguna regla dice quién aprueba."""
    limite_r1 = monto <= 2_000_000 if corregida else monto < 2_000_000
    cubierta = Or(limite_r1, And(monto > 2_000_000, monto <= 10_000_000), monto > 10_000_000)
    return And(homologado, Not(cubierta))


def preguntar(titulo, condicion, maximizar=False):
    # Optimize devuelve el caso de mayor monto: un contraejemplo más realista que $1
    s = Optimize() if maximizar else Solver()
    s.add(CASO_VALIDO, condicion)
    if maximizar:
        s.maximize(monto)
    resultado = s.check()
    print(f"\n{titulo}\n  Z3: {resultado}")
    if resultado == sat:
        m = s.model()
        print(f"  Contraejemplo: compra de ${m[monto].as_long():,} a un proveedor "
              f"{'homologado' if m.eval(homologado) else 'no homologado'}".replace(",", "."))
    else:
        print("  No existe ningún caso así.")


if __name__ == "__main__":
    print("=== Política original ===")
    preguntar("1. ¿Hay una compra que nadie puede aprobar? (contradicción)", nadie_puede_aprobar(), maximizar=True)
    preguntar("2. ¿Hay una compra homologada que ninguna regla cubre? (laguna)", ninguna_regla_cubre())
    print("\n=== Política corregida: R1 dice «hasta $2.000.000» y R5 se aplica solo a proveedores homologados ===")
    preguntar("1. ¿Hay una compra que nadie puede aprobar?", nadie_puede_aprobar(corregida=True))
    preguntar("2. ¿Hay una compra homologada que ninguna regla cubre?", ninguna_regla_cubre(corregida=True))
