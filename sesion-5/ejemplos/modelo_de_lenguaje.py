"""Un modelo de lenguaje pequeño por dentro, con números reales (charlas intermedia y de cierre).

Usa Qwen/Qwen2.5-0.5B, el modelo base sin ajuste por instrucciones (Apache 2.0, 988 MB, 24 capas
de 14 cabezas), y solo el tokenizador de GPT-2 (MIT). Calcula:
1. Tokenización: la misma frase de MantenIA, en español y en inglés, con los dos tokenizadores.
2. «banco» según el contexto: su vector en cuatro frases, antes de la primera capa y en la capa 12.
   Qwen solo mira hacia atrás, así que el contexto que decide el sentido va antes de «banco».
3. Atención real: a qué palabras atiende «banco» en la capa 12, promediando las 14 cabezas.
   Se deja fuera el primer token, que en estos modelos recibe buena parte de la atención sin aportar
   significado (el «sumidero de atención» de Xiao et al., 2024).
4. El siguiente token: las probabilidades después de una orden de MantenIA, con temperatura 0,5, 1 y 1,5,
   y continuaciones generadas con temperatura 0,2, 0,8 y 1,3.
5. La codificación posicional sinusoidal de Vaswani et al. (2017), para 40 posiciones y 64 dimensiones.

Uso, desde esta carpeta:  python modelo_de_lenguaje.py
Requiere torch y transformers. La primera vez descarga el modelo (988 MB) y el tokenizador de GPT-2.
Escribe los números en salidas/modelo_de_lenguaje.json y la codificación posicional en
../assets/img/tr_codificacion_posicional.png.
"""
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from comun import divergente, guardar_json, guardar_png

QWEN, REV_QWEN = "Qwen/Qwen2.5-0.5B", "060db6499f32faf8b98477b0a26969ef7d8b9987"
GPT2 = "openai-community/gpt2"
FRASES_TOKENS = {"es": "La bomba 3 presenta vibración alta y temperatura elevada en el rodamiento.",
                 "en": "Pump 3 shows high vibration and elevated temperature in the bearing."}
FRASES_BANCO = ["Para pagar la factura del proveedor fuimos al banco",
                "El gerente pidió el crédito para la planta en el banco",
                "Cansado después del turno, el técnico se sentó en el banco",
                "Para descansar un rato en el parque, se sentaron en el banco"]
CAPA = 12
INICIO = "Orden de trabajo OT-512. La bomba 3 presenta vibración alta. La causa más probable es un"


def coseno(a, b) -> float:
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def main() -> None:
    tok = AutoTokenizer.from_pretrained(QWEN, revision=REV_QWEN)
    tok_gpt2 = AutoTokenizer.from_pretrained(GPT2)
    red = AutoModelForCausalLM.from_pretrained(QWEN, revision=REV_QWEN, dtype=torch.float32,
                                               attn_implementation="eager").eval()
    resultado = {"modelo": QWEN, "revision": REV_QWEN, "capas": red.config.num_hidden_layers,
                 "cabezas": red.config.num_attention_heads}

    # 1. Tokenización
    resultado["tokens"] = {}
    for nombre, t in [("gpt2", tok_gpt2), ("qwen2.5", tok)]:
        for idioma, frase in FRASES_TOKENS.items():
            piezas = [t.decode([i]) for i in t(frase)["input_ids"]]
            resultado["tokens"][f"{nombre}_{idioma}"] = piezas
            print(f"{nombre:8} {idioma}: {len(piezas):2} tokens | {'|'.join(piezas)}")

    # 2 y 3. «banco» según el contexto y su atención
    estados, atenciones, piezas_banco = [], [], []
    for frase in FRASES_BANCO:
        ids = tok(frase, return_tensors="pt")
        with torch.no_grad():
            salida = red(**ids, output_hidden_states=True, output_attentions=True)
        estados.append([h[0, -1].numpy() for h in salida.hidden_states])
        atenciones.append(salida.attentions[CAPA - 1][0, :, -1].mean(0).numpy())
        piezas_banco.append([tok.decode([i]) for i in ids["input_ids"][0]])
    matriz = lambda capa: [[round(coseno(a[capa], b[capa]), 2) for b in estados] for a in estados]
    resultado["banco"] = {"frases": FRASES_BANCO, "capa": CAPA,
                          "similitud_antes": matriz(0), "similitud_capa": matriz(CAPA)}
    print(f"«banco», similitud en la capa {CAPA}:", matriz(CAPA))
    resultado["atencion"] = []
    for frase, piezas, a in zip(FRASES_BANCO, piezas_banco, atenciones):
        resto = a[1:] / a[1:].sum()
        resultado["atencion"].append({"frase": frase, "tokens": piezas[1:],
                                      "peso_primer_token": round(float(a[0]), 3),
                                      "pesos_sin_primer_token": [round(float(x), 3) for x in resto]})
        top = np.argsort(resto)[::-1][:4]
        print(f"atención desde «banco» | {frase[:45]}… →", ", ".join(f"{piezas[1:][i].strip()}={resto[i]:.2f}" for i in top))

    # 4. El siguiente token, con temperatura
    ids = tok(INICIO, return_tensors="pt")
    with torch.no_grad():
        logits = red(**ids).logits[0, -1]
    resultado["siguiente_token"] = {"inicio": INICIO, "temperaturas": {}}
    for temperatura in (0.5, 1.0, 1.5):
        p = torch.softmax(logits / temperatura, dim=-1)
        top = torch.topk(p, 8)
        resultado["siguiente_token"]["temperaturas"][str(temperatura)] = [
            {"token": tok.decode([int(i)]), "probabilidad": round(float(q), 4)} for q, i in zip(top.values, top.indices)]
        print(f"T={temperatura}:", ", ".join(f"«{tok.decode([int(i)])}» {float(q):.1%}" for q, i in zip(top.values, top.indices)))
    resultado["continuaciones"] = {}
    for temperatura in (0.2, 0.8, 1.3):
        textos = []
        for semilla in (1, 2):
            torch.manual_seed(semilla)
            with torch.no_grad():
                g = red.generate(**ids, do_sample=True, temperature=temperatura, top_k=0, top_p=1.0,
                                 max_new_tokens=14, pad_token_id=tok.eos_token_id)
            textos.append(tok.decode(g[0, ids["input_ids"].shape[1]:], skip_special_tokens=True))
        resultado["continuaciones"][str(temperatura)] = textos
        print(f"T={temperatura}:", " ║ ".join(textos))

    # 5. Codificación posicional sinusoidal
    pos = np.arange(40)[:, None]
    i = np.arange(0, 64, 2)[None, :]
    angulo = pos / np.power(10000, i / 64)
    pe = np.zeros((40, 64))
    pe[:, 0::2], pe[:, 1::2] = np.sin(angulo), np.cos(angulo)
    guardar_png("tr_codificacion_posicional.png", np.kron(divergente(pe), np.ones((12, 12, 1), dtype=np.uint8)))
    guardar_json("modelo_de_lenguaje.json", resultado)


if __name__ == "__main__":
    main()
