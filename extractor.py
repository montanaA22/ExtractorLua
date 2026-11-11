import os, re

PATTERNS = {
    "triggerServerEvent": re.compile(r"triggerServerEvent\s*\(\s*[\"']?([^\"',\)]+)[\"']?"),
    "triggerClientEvent": re.compile(r"triggerClientEvent\s*\(\s*[\"']?([^\"',\)]+)[\"']?"),
    "addEvent":           re.compile(r"addEvent\s*\(\s*[\"']([^\"']+)[\"']"),
    "addEventHandler":    re.compile(r"addEventHandler\s*\(\s*[\"']([^\"']+)[\"']"),
    "elementData":        re.compile(r"(?:setElementData|getElementData)\s*\(\s*[^,]+,\s*[\"']([^\"']+)[\"']"),
    "export":             re.compile(r"exports\s*[\"']?([A-Za-z0-9_:]+)[\"']?"),
}

LUA_EXT = {".lua", ".luac", ".txt"}

def is_luac(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"\x1bLua"
    except OSError:
        return False

def get_block_context(text: str, match_start: int, match_end: int) -> str:
    """Extrae el bloque exacto de código (desde el for más cercano hasta el end de cierre)."""
    lookback = text[max(0, match_start - 1000):match_start]
    lines = lookback.split('\n')

    # Encontrar la línea que tiene el 'for' más cercano hacia arriba
    for_line_idx = -1
    for i in range(len(lines)-1, -1, -1):
        if "for " in lines[i]:
            for_line_idx = i
            break

    if for_line_idx != -1:
        start_idx = text[max(0, match_start - 1000):match_start].rfind(lines[for_line_idx])
        start_idx = max(0, match_start - 1000) + start_idx
    else:
        start_idx = text.rfind('\n', 0, match_start) + 1

    # Contar bloques 'for/do' y 'end' para cerrar correctamente
    block_text = text[start_idx:match_end]
    open_blocks = len(re.findall(r'\b(?:for|if|function|do)\b', block_text)) - len(re.findall(r'\bend\b', block_text))

    idx = match_end
    while open_blocks > 0 and idx < len(text):
        next_end = re.search(r'\bend\b', text[idx:])
        if not next_end: break
        idx += next_end.end()
        open_blocks -= 1

    end_idx = text.find('\n', idx)
    if end_idx == -1: end_idx = len(text)
    return text[start_idx:end_idx].strip()

def scan_file(path: str):
    findings = {k: [] for k in PATTERNS}
    blocks = {}

    if is_luac(path):
        return findings, blocks

    try:
        text = open(path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return findings, blocks

    for name, rx in PATTERNS.items():
        for m in rx.finditer(text):
            v = m.group(1).strip().strip("\"'")
            if v and v.lower() not in ("true", "false", "nil", "root", "localplayer"):
                findings[name].append(v)
                if v not in blocks:
                    blocks[v] = get_block_context(text, m.start(), m.end())

    return findings, blocks

def scan_folder(root: str):
    result = {k: set() for k in PATTERNS}
    blocks = {}
    files = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in LUA_EXT:
                files.append(os.path.join(dirpath, fn))

    for f in files:
        findings, b = scan_file(f)
        for k, vals in findings.items():
            for v in vals:
                result[k].add(v)
        blocks.update(b)

    return {k: sorted(v) for k, v in result.items()}, len(files), blocks
