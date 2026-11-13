"""La red de la alarma (Pearl, 1988; Russell y Norvig, AIMA, cap. 13), la del Laboratorio 7A.

Cinco nodos: Robo y Sismo pueden hacer sonar la Alarma; si suena, Juan y María pueden llamar.
Las tablas de probabilidad son las de AIMA. El script calcula con pyAgrum:
- consultas predictivas, de la causa al efecto;
- consultas diagnósticas, del efecto a la causa;
- el explaining away: saber que hubo un sismo vuelve menos probable el robo;
- la independencia condicional: si ya sabes que sonó la alarma, la llamada de Juan no cambia nada.

Uso, desde esta carpeta:  python alarma_7a.py
Requiere pyagrum (3.3 o posterior). Escribe salidas/alarma_7a.json.
"""
import pyagrum as gum

from comun import guardar_json, red

# Las tablas de AIMA: la probabilidad de «sí» de cada nodo, según sus padres
P_ROBO = 0.001
P_SISMO = 0.002
P_ALARMA = {("si", "si"): 0.95, ("si", "no"): 0.94, ("no", "si"): 0.29, ("no", "no"): 0.001}   # (robo, sismo)
P_JUAN = {"si": 0.90, "no": 0.05}      # según la alarma
P_MARIA = {"si": 0.70, "no": 0.01}     # según la alarma


def construir() -> gum.BayesNet:
    """Arma la red con sus cinco tablas."""
    bn = gum.fastBN("Robo{no|si}->Alarma{no|si}<-Sismo{no|si};Alarma->Juan{no|si};Alarma->Maria{no|si}")
    bn.cpt("Robo").fillWith([1 - P_ROBO, P_ROBO])
    bn.cpt("Sismo").fillWith([1 - P_SISMO, P_SISMO])
    for (robo, sismo), p in P_ALARMA.items():
        bn.cpt("Alarma")[{"Robo": robo, "Sismo": sismo}] = [1 - p, p]
    for alarma in ("si", "no"):
        bn.cpt("Juan")[{"Alarma": alarma}] = [1 - P_JUAN[alarma], P_JUAN[alarma]]
        bn.cpt("Maria")[{"Alarma": alarma}] = [1 - P_MARIA[alarma], P_MARIA[alarma]]
    return bn


def main() -> None:
    bn = construir()
    ie = gum.LazyPropagation(bn)

    def prob(nodo: str, evidencia: dict) -> float:
        """La probabilidad de que el nodo valga «si», dada la evidencia."""
        ie.setEvidence(evidencia)
        ie.makeInference()
        return float(ie.posterior(nodo)[{nodo: "si"}])

    si = "si"
    consultas = {
        # La creencia en el robo cambia con cada evidencia nueva
        "robo_previa": prob("Robo", {}),
        "robo_juan": prob("Robo", {"Juan": si}),
        "robo_juan_maria": prob("Robo", {"Juan": si, "Maria": si}),
        "sismo_juan_maria": prob("Sismo", {"Juan": si, "Maria": si}),
        # Predicción: de la causa al efecto
        "alarma_robo": prob("Alarma", {"Robo": si}),
        "juan_robo": prob("Juan", {"Robo": si}),
        "maria_robo": prob("Maria", {"Robo": si}),
        # Explaining away: el sismo explica la alarma y el robo pierde fuerza
        "robo_alarma": prob("Robo", {"Alarma": si}),
        "robo_alarma_sismo": prob("Robo", {"Alarma": si, "Sismo": si}),
        # Independencia condicional: con la alarma conocida, la llamada no agrega nada
        "robo_alarma_juan": prob("Robo", {"Alarma": si, "Juan": si}),
    }
    for k, v in consultas.items():
        print(f"{k:22} {v:.4f}")
    # Cuántos números necesita la red frente a la tabla conjunta de 5 variables binarias
    numeros_red = 1 + 1 + 4 + 2 + 2
    numeros_conjunta = 2 ** 5 - 1
    print(f"La red usa {numeros_red} números; la tabla conjunta, {numeros_conjunta}.")
    guardar_json("alarma_7a.json", {
        "tablas": {"robo": P_ROBO, "sismo": P_SISMO, "alarma": {f"{r},{s}": p for (r, s), p in P_ALARMA.items()},
                   "juan": P_JUAN, "maria": P_MARIA},
        "consultas": {k: red(v) for k, v in consultas.items()},
        "numeros_red": numeros_red, "numeros_conjunta": numeros_conjunta})


if __name__ == "__main__":
    main()
