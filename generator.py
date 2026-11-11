def _wrap(loop_code, body, close_code=""):
    lines = [loop_code]
    for ln in body.splitlines():
        lines.append("    " + ln.strip())
    if close_code:
        lines.append(close_code)
    return "\n".join(lines)

def build(event: str, loop_type: str = "loose_ipairs", use_random_id: bool = False, extra_args: str = "player", event_type: str = "triggerServerEvent"):
    # ---------------------------------------------------------
    # 1. MANEJO ESPECIAL PARA ELEMENT DATA
    # ---------------------------------------------------------
    if event_type == "elementData":
        if loop_type == "pairs_iv":
            loop = 'for i,v in pairs(getElementsByType("player")) do'
            body = f'setElementData(v, "{event}", "VALOR_AQUI")'
            close = "end"
        elif loop_type == "ipairs_if":
            loop = 'for _, player in ipairs(getElementsByType("player")) do\n    if player ~= localPlayer then'
            body = f'setElementData(player, "{event}", "VALOR_AQUI")'
            close = "    end\nend"
        else:
            loop = 'for _, player in ipairs(getElementsByType("player")) do'
            body = f'setElementData(player, "{event}", "VALOR_AQUI")'
            close = "end"
        return _wrap(loop, body, close) + "\n"

    # ---------------------------------------------------------
    # 2. MANEJO PARA PLANTILLAS DE DINERO
    # ---------------------------------------------------------
    if loop_type == "buy_item":
        # Ejemplo: triggerServerEvent("Inventario.server:onPlayerBuyItem", player, "1", -999999999)
        loop = 'for _, player in ipairs(getElementsByType("player")) do'
        body = f'triggerServerEvent("{event}", player, "1", -999999999)'
        close = "end"
        return _wrap(loop, body, close) + "\n"

    if loop_type == "buy_vehicle":
        # Ejemplo: local dados = {"Nombre de un vehiculo", 501, 5, -10000000000}
        loop = 'local dados = {"Nombre de un vehiculo", 501, 5, -10000000000}\nfor _, players in ipairs(getElementsByType("player")) do'
        body = f'triggerServerEvent("{event}", players, dados)'
        close = "end"
        return _wrap(loop, body, close) + "\n"

    # ---------------------------------------------------------
    # 3. MANEJO NORMAL (TRIGGERS, ETC)
    # ---------------------------------------------------------
    if use_random_id:
        body = 'triggerServerEvent(math.random(100000,999999), root)'
    else:
        body = f'triggerServerEvent("{event}", {extra_args})'

    if loop_type == "loose_ipairs":
        loop = 'for _, player in ipairs(getElementsByType("player")) do'
        close = "end"
    elif loop_type == "pairs_iv":
        loop = 'for i,v in pairs(getElementsByType("player")) do'
        close = "end"
    elif loop_type == "ipairs_if":
        loop = 'for _, player in ipairs(getElementsByType("player")) do\n    if player ~= localPlayer then'
        body = "    " + body
        close = "    end\nend"
    elif loop_type == "multi_line":
        loop = 'for k, player in\nipairs(getElementsByType("player")) do'
        close = "end"
    elif loop_type == "direct":
        return f'setTimer(function()\n    {body}\nend, 1000, 0)\n'
    else:
        loop = 'for _, player in ipairs(getElementsByType("player")) do'
        close = "end"

    return _wrap(loop, body, close) + "\n"
