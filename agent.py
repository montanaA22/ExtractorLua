def explain_event(event_name: str, block_code: str = "") -> dict:
    if block_code:
        return {
            "what": f"Evento '{event_name}' identificado.",
            "kind": "RPC Original",
            "risk": "Analizar manualmente",
            "notes": "Se preservó el bloque de código original exacto para ejecución.",
            "pattern_id": "custom_block",
            "loop_template": block_code,
        }
    return {
        "what": f"Evento '{event_name}' sin bloque extraíble.",
        "kind": "RPC Directo",
        "risk": "Desconocido",
        "notes": "Se generará una llamada simple.",
        "pattern_id": "direct",
        "loop_template": "",
    }
