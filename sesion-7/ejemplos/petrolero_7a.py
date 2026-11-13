"""El problema del petrolero (Raiffa, 1968): un diagrama de influencia y el valor de la información (Laboratorio 7A).

Un petrolero decide si perfora un pozo sin saber si está seco, húmedo o empapado.
Antes puede pagar una prueba sísmica, que da una pista imperfecta sobre el pozo.
El script calcula con pyAgrum y también a mano, para comprobar:
- la utilidad esperada de perforar sin la prueba;
- la decisión según cada resultado de la prueba;
- el valor de la información de la prueba, comparado con su precio.

Uso, desde esta carpeta:  python petrolero_7a.py
Requiere pyagrum (3.3 o posterior). Escribe salidas/petrolero_7a.json.
"""
import pyagrum as gum

from comun import guardar_json, red

POZO = ["seco", "humedo", "empapado"]
P_POZO = {"seco": 0.5, "humedo": 0.3, "empapado": 0.2}
GANANCIA = {"seco": -70, "humedo": 50, "empapado": 200}     # perforar; no perforar vale 0
COSTO_PRUEBA = 10
RESULTADO = ["sin_estructura", "abierta", "cerrada"]        # lo que dice la prueba sísmica
P_RESULTADO = {                                             # P(resultado | pozo)
    "seco": {"sin_estructura": 0.6, "abierta": 0.3, "cerrada": 0.1},
    "humedo": {"sin_estructura": 0.3, "abierta": 0.4, "cerrada": 0.3},
    "empapado": {"sin_estructura": 0.1, "abierta": 0.4, "cerrada": 0.5},
}


def a_mano() -> dict:
    """La misma cuenta con sumas y productos, como en una hoja de cálculo."""
    ue_sin = sum(P_POZO[p] * GANANCIA[p] for p in POZO)                 # perforar sin saber nada
    decision_sin = "perforar" if ue_sin > 0 else "no perforar"
    por_resultado = {}
    ue_con = 0.0
    for r in RESULTADO:
        p_r = sum(P_POZO[p] * P_RESULTADO[p][r] for p in POZO)
        posterior = {p: P_POZO[p] * P_RESULTADO[p][r] / p_r for p in POZO}
        ue_perforar = sum(posterior[p] * GANANCIA[p] for p in POZO)
        mejor = max(ue_perforar, 0.0)
        ue_con += p_r * mejor
        por_resultado[r] = {"p": red(p_r), "posterior": {p: red(v) for p, v in posterior.items()},
                            "ue_perforar": red(ue_perforar, 2),
                            "decision": "perforar" if ue_perforar > 0 else "no perforar"}
    valor_info = ue_con - max(ue_sin, 0.0)
    return {"ue_sin_prueba": red(ue_sin, 2), "decision_sin_prueba": decision_sin,
            "ue_con_prueba_gratis": red(ue_con, 2), "valor_informacion": red(valor_info, 2),
            "ue_con_prueba_pagada": red(ue_con - COSTO_PRUEBA, 2), "por_resultado": por_resultado,
            "conviene_probar": valor_info > COSTO_PRUEBA}


def diagrama(costo: float) -> gum.InfluenceDiagram:
    """El diagrama de influencia: dos decisiones, dos nodos de azar y dos de utilidad."""
    d = gum.fastID("*Prueba{no|si}->Resultado{sin_estructura|abierta|cerrada|ninguno};"
                   "Petroleo{seco|humedo|empapado}->Resultado;"
                   "Prueba->*Perforar{no|si};Resultado->Perforar;"
                   "Perforar->$Ganancia<-Petroleo;Prueba->$CostoPrueba")
    d.cpt("Petroleo").fillWith([P_POZO[p] for p in POZO])
    for p in POZO:
        # Sin prueba, el resultado siempre es «ninguno»
        d.cpt("Resultado")[{"Petroleo": p, "Prueba": "no"}] = [0, 0, 0, 1]
        d.cpt("Resultado")[{"Petroleo": p, "Prueba": "si"}] = [P_RESULTADO[p][r] for r in RESULTADO] + [0]
        d.utility("Ganancia")[{"Petroleo": p, "Perforar": "si"}] = GANANCIA[p]
        d.utility("Ganancia")[{"Petroleo": p, "Perforar": "no"}] = 0
    d.utility("CostoPrueba")[{"Prueba": "si"}] = -costo
    d.utility("CostoPrueba")[{"Prueba": "no"}] = 0
    return d


def con_pyagrum() -> dict:
    """Resuelve el diagrama con pyAgrum, con la prueba pagada y gratis."""
    salida = {}
    for nombre, costo in (("pagada", COSTO_PRUEBA), ("gratis", 0)):
        ie = gum.ShaferShenoyLIMIDInference(diagrama(costo))
        ie.makeInference()
        meu = ie.MEU()
        prueba = ie.optimalDecision("Prueba")
        salida[nombre] = {"meu": red(meu["mean"], 2),
                          "probar": "si" if prueba[{"Prueba": "si"}] > 0.5 else "no"}
    # Sin la opción de probar: se fuerza la decisión «no» como evidencia
    ie = gum.ShaferShenoyLIMIDInference(diagrama(COSTO_PRUEBA))
    ie.setEvidence({"Prueba": "no"})
    ie.makeInference()
    salida["sin_prueba"] = {"meu": red(ie.MEU()["mean"], 2)}
    salida["valor_informacion"] = red(salida["gratis"]["meu"] - salida["sin_prueba"]["meu"], 2)
    return salida


def main() -> None:
    mano = a_mano()
    pg = con_pyagrum()
    print(f"Sin la prueba: perforar vale {mano['ue_sin_prueba']} en promedio → {mano['decision_sin_prueba']}.")
    for r, v in mano["por_resultado"].items():
        print(f"  Si la prueba dice {r:15} (p = {v['p']:.2f}): perforar vale {v['ue_perforar']:7.2f} → {v['decision']}")
    print(f"Con la prueba gratis: {mano['ue_con_prueba_gratis']}. Valor de la información: {mano['valor_informacion']}"
          f" frente a un precio de {COSTO_PRUEBA} → {'probar' if mano['conviene_probar'] else 'no probar'}.")
    print(f"pyAgrum: {pg}")
    assert abs(pg["valor_informacion"] - mano["valor_informacion"]) < 0.01, "pyAgrum y la cuenta a mano no coinciden"
    guardar_json("petrolero_7a.json", {
        "p_pozo": P_POZO, "ganancia": GANANCIA, "costo_prueba": COSTO_PRUEBA, "p_resultado": P_RESULTADO,
        "a_mano": mano, "pyagrum": pg})


if __name__ == "__main__":
    main()
