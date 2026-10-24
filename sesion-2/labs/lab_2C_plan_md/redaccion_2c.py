"""Redacción y replanificación del plan.md con un LLM (Laboratorio 2C)."""
from __future__ import annotations

import re
from pathlib import Path

SISTEMA = ("Eres un asistente de planificación de mantenimiento de MantenIA, una empresa de mantenimiento industrial. "
           "Redactas planes claros en Markdown y en español. No inventas datos: usas solo lo que dicen los documentos "
           "y declaras como supuesto lo que falte.")


def plantilla(ruta: str = "plantilla_plan.md") -> str:
    """La plantilla del plan.md, sin la lista de chequeo del final."""
    texto = Path(ruta).read_text(encoding="utf-8")
    return texto.split("\n---\n")[0].strip()


def documentos(carpeta: str = "documentos") -> str:
    """Los documentos de la OT-523, uno detrás de otro, con su nombre."""
    partes = []
    for f in sorted(Path(carpeta).iterdir()):
        if f.suffix in (".md", ".csv"):
            partes.append(f"### {f.name}\n{f.read_text(encoding='utf-8').strip()}")
    return "\n\n".join(partes)


def limpiar(texto: str) -> str:
    """Quita los delimitadores de código y todo lo que esté antes del título del plan."""
    texto = re.sub(r"^```[a-zA-Z]*\s*$", "", texto, flags=re.M).strip()
    i = texto.find("# Plan")
    return texto[i:].strip() if i >= 0 else texto


def acciones_disponibles() -> str:
    """Las operaciones que el equipo puede ejecutar en la intervención, con el verbo con que empieza cada paso."""
    from simulador_ot523 import OPERACIONES
    return "\n".join(f"- {inicio}: por ejemplo, «{ejemplo}»" for _, inicio, ejemplo, _ in OPERACIONES)


def instruccion_redaccion() -> str:
    return ("Redacta el plan.md de la intervención descrita en los documentos, con la estructura exacta de la plantilla.\n\n"
            "Reglas:\n"
            "- Usa solo información de los documentos; si falta un dato, decláralo como supuesto en el Contexto.\n"
            "- Escribe cada paso en una línea, con este formato: - [ ] N. <acción> (requiere ...) → Resultado: <...> · "
            "Verificación: <...>\n"
            "- Cada paso es una sola de las acciones disponibles y empieza con su verbo. Usa como máximo 12 pasos.\n"
            "- Numera los pasos 1, 2, 3...\n"
            "- Sé breve: frases cortas, sin repetir en una sección lo que ya dice otra.\n"
            "- En el Registro de avance escribe una sola línea: - (vacío: el plan aún no se ha ejecutado)\n"
            "- No incluyas la lista de chequeo ni los comentarios HTML de la plantilla, y no agregues secciones que no "
            "estén en ella.\n"
            "- Responde solo con el plan.md, empezando por «# Plan:».\n\n"
            f"## Acciones disponibles en la intervención\n{acciones_disponibles()}\n\n"
            f"## Plantilla\n{plantilla()}\n\n## Documentos\n{documentos()}")


def redactar(llm):
    """Pide al LLM el plan.md de la OT-523. Devuelve (texto del plan o None, respuesta)."""
    instruccion = instruccion_redaccion()
    respuesta = llm.completar([{"role": "user", "content": instruccion}], sistema=SISTEMA,
                              etiqueta="2c/redaccion", max_tokens_respuesta=6000)
    if not respuesta.disponible:
        return None, respuesta
    return limpiar(respuesta.texto), respuesta


def instruccion_replanificacion(texto_plan: str, observacion: str) -> str:
    return ("El plan.md siguiente estaba aprobado y en ejecución. Durante la ejecución ocurrió una falla, que quedó "
            "registrada al final del Registro de avance.\n\n"
            "Actualiza el plan desde el estado real:\n"
            "- Conserva marcados [x] los pasos cumplidos y no cambies su texto.\n"
            "- Tacha solo el paso que falló, sin marcarlo como cumplido, con este formato: - [ ] ~~N. <texto del paso>~~ "
            "(falló: <motivo>). Agrega los pasos nuevos que hagan falta, cada uno con su resultado y su verificación, "
            "numerados como subpasos del paso que falló (si falló el 4: 4b, 4c...). Cada paso nuevo es una sola de las "
            "acciones disponibles y empieza con su verbo. Ajusta las dependencias de los pasos pendientes.\n"
            "- Si cambian el plazo, el alcance o los riesgos, actualiza el Objetivo, los Riesgos y los Criterios de "
            "aceptación, y agrega un paso de APROBACIÓN con la persona que debe aprobar según los documentos.\n"
            "- Agrega al Registro de avance una línea que diga qué cambió en el plan y por qué. No borres el registro.\n"
            "- No agregues secciones que no estén en el plan actual.\n"
            "- Responde solo con el plan.md completo, empezando por «# Plan:».\n\n"
            f"## Acciones disponibles en la intervención (referencia: no la copies en el plan)\n{acciones_disponibles()}\n\n"
            f"## Documentos\n{documentos()}\n\n## Falla observada\n{observacion}\n\n## Plan actual\n{texto_plan}")


def replanificar(llm, plan, falla: dict, escenario: str):
    """Pide al LLM el plan actualizado después de una falla. Devuelve (texto o None, respuesta).

    falla: la falla registrada por la ejecución (ej.falla), con el paso y lo que se observó.
    """
    instruccion = instruccion_replanificacion(plan.texto, f"Paso {falla['paso']}: {falla['texto']}")
    respuesta = llm.completar([{"role": "user", "content": instruccion}], sistema=SISTEMA,
                              etiqueta=f"2c/replanificacion/{escenario}", max_tokens_respuesta=7000,
                              exacta=False)  # parte del plan de cada pareja: con grabaciones, se muestra la del docente
    if not respuesta.disponible:
        return None, respuesta
    return limpiar(respuesta.texto), respuesta
