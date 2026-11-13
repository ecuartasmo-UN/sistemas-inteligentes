"""La alarma de vibración de MantenIA: la regla de Bayes con frecuencias naturales (charla inicial).

Ejemplo ilustrativo. MantenIA es una empresa ficticia, y las cifras las inventamos.
- De 1000 bombas, el 2 % va a fallar este mes: 20 bombas.
- La alarma acierta el 95 %. Detecta 19 de las 20 que fallan, y calla en el 95 % de las sanas.
- Aun así, la mayoría de sus avisos son falsos, porque las fallas son raras.
- Con esa probabilidad, decide si reemplazar la bomba ahora o esperar.

Uso, desde esta carpeta:  python tasa_base_7a.py
Solo usa la biblioteca estándar. Escribe salidas/tasa_base_7a.json.
"""
from comun import guardar_json, red

BOMBAS = 1000
TASA_FALLA = 0.02        # la tasa base: la proporción de bombas que fallan
SENSIBILIDAD = 0.95      # de las bombas que fallan, la alarma avisa en esta proporción
ESPECIFICIDAD = 0.95     # de las bombas sanas, la alarma calla en esta proporción
# La decisión: reemplazar la bomba ahora o esperar. Costos ilustrativos, en millones de pesos
COSTO_REEMPLAZO = 8     # reemplazo planeado
COSTO_FALLA = 40        # falla sin aviso: paro de la línea y reparación de urgencia


def main() -> None:
    fallan = round(BOMBAS * TASA_FALLA)
    sanas = BOMBAS - fallan
    detectadas = round(fallan * SENSIBILIDAD)
    falsas = round(sanas * (1 - ESPECIFICIDAD))
    avisos = detectadas + falsas
    # La regla de Bayes con frecuencias: de todos los avisos, ¿cuántos son fallas de verdad?
    posterior = detectadas / avisos
    # La misma cuenta con probabilidades, para la vertical de consulta
    p_aviso = SENSIBILIDAD * TASA_FALLA + (1 - ESPECIFICIDAD) * (1 - TASA_FALLA)
    posterior_formula = SENSIBILIDAD * TASA_FALLA / p_aviso
    print(f"De {BOMBAS} bombas fallan {fallan}; la alarma detecta {detectadas} y da {falsas} falsas alarmas.")
    print(f"De {avisos} avisos, {detectadas} son fallas: {posterior:.1%} (con la fórmula: {posterior_formula:.4f}).")
    # La utilidad esperada de cada decisión, antes y después de la alarma (los costos son utilidades negativas)
    decision = {}
    for momento, p_falla in (("sin_alarma", TASA_FALLA), ("con_alarma", posterior)):
        esperar = -COSTO_FALLA * p_falla
        reemplazar = -COSTO_REEMPLAZO
        decision[momento] = {"p_falla": red(p_falla), "esperar": red(esperar, 2), "reemplazar": reemplazar,
                             "mejor": "esperar" if esperar > reemplazar else "reemplazar"}
        print(f"{momento}: esperar vale {esperar:.2f}; reemplazar vale {reemplazar} → {decision[momento]['mejor']}")
    guardar_json("tasa_base_7a.json", {
        "bombas": BOMBAS, "tasa_falla": TASA_FALLA, "sensibilidad": SENSIBILIDAD, "especificidad": ESPECIFICIDAD,
        "fallan": fallan, "sanas": sanas, "detectadas": detectadas, "no_detectadas": fallan - detectadas,
        "falsas": falsas, "avisos": avisos, "posterior": red(posterior), "p_aviso": red(p_aviso),
        "posterior_formula": red(posterior_formula),
        "costo_reemplazo": COSTO_REEMPLAZO, "costo_falla": COSTO_FALLA, "decision": decision})


if __name__ == "__main__":
    main()
