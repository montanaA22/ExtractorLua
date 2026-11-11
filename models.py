import sqlite3, time, secrets
from contextlib import contextmanager
from config import Config

@contextmanager
def db():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            last_ip TEXT,
            active_key TEXT,
            plan TEXT
        );
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            expires_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            created_by TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            max_uses INTEGER NOT NULL DEFAULT 1,
            uses INTEGER NOT NULL DEFAULT 0,
            revoked INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            detail TEXT
        );
        """)

# === USUARIOS ===
def create_user(username, pwd_hash, ip):
    now = int(time.time())
    with db() as c:
        try:
            c.execute("INSERT INTO users (username, password_hash, created_at, last_ip) VALUES (?,?,?,?)",
                      (username, pwd_hash, now, ip))
            return True
        except sqlite3.IntegrityError:
            return False

def get_user(username):
    with db() as c:
        row = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None

def create_user_session(user_id):
    tok = secrets.token_urlsafe(32)
    now = int(time.time())
    with db() as c:
        c.execute("INSERT INTO user_sessions (token, user_id, expires_at) VALUES (?,?,?)",
                  (tok, user_id, now + 7*86400)) # 7 días
    return tok

def get_user_by_session(token):
    if not token: return None
    now = int(time.time())
    with db() as c:
        row = c.execute("""SELECT u.* FROM users u
                           JOIN user_sessions s ON u.id = s.user_id
                           WHERE s.token = ? AND s.expires_at > ?""", (token, now)).fetchone()
        return dict(row) if row else None

def link_key_to_user(user_id, key, days):
    now = int(time.time())
    with db() as c:
        c.execute("UPDATE users SET active_key = ?, plan = ?, last_ip = ? WHERE id = ?",
                  (key, f"{days} Días", now, user_id))

# === KEYS & ADMIN ===
def gen_key(prefix="AD7"):
    raw = secrets.token_hex(8).upper()
    return f"{prefix}-{raw[:4]}-{raw[4:8]}-{raw[8:12]}-{raw[12:16]}"

def create_key(created_by: str, days: int = 7, uses: int = 1) -> str:
    k = gen_key()
    now = int(time.time())
    with db() as c:
        c.execute("INSERT INTO keys(key, created_by, created_at, expires_at, max_uses) VALUES(?,?,?,?,?)",
                  (k, created_by, now, now + days * 86400, uses))
        log(c, created_by, "key.create", k)
    return k

def validate_key(key: str):
    now = int(time.time())
    with db() as c:
        row = c.execute("SELECT * FROM keys WHERE key = ?", (key,)).fetchone()
        if not row: return None, "Key no existe."
        if row["revoked"]: return None, "Key revocada."
        if row["expires_at"] < now: return None, "Key expirada."
        if row["uses"] >= row["max_uses"]: return None, "Key sin usos."
        return dict(row), None

def consume_key(key_id: int, actor: str):
    with db() as c:
        c.execute("UPDATE keys SET uses = uses + 1 WHERE id = ?", (key_id,))
        log(c, actor, "key.use", str(key_id))

def log(c, actor, action, detail=""):
    c.execute("INSERT INTO logs(ts, actor, action, detail) VALUES(?,?,?,?)",
              (int(time.time()), actor, action, detail))

def list_keys():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM keys ORDER BY id DESC").fetchall()]

def revoke_key(key_id: int, actor: str):
    with db() as c:
        c.execute("UPDATE keys SET revoked = 1 WHERE id = ?", (key_id,))
        log(c, actor, "key.revoke", str(key_id))

def delete_key(key_id: int, actor: str):
    with db() as c:
        c.execute("DELETE FROM keys WHERE id = ?", (key_id,))
        log(c, actor, "key.delete", str(key_id))

def list_logs(limit: int = 300):
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]

def stats():
    with db() as c:
        total = c.execute("SELECT COUNT(*) AS n FROM keys").fetchone()["n"]
        used = c.execute("SELECT COUNT(*) AS n FROM keys WHERE uses > 0").fetchone()["n"]
        active = c.execute("SELECT COUNT(*) AS n FROM keys WHERE revoked = 0 AND uses < max_uses AND expires_at > ?",
                           (int(time.time()),)).fetchone()["n"]
    return {"total": total, "used": used, "active": active}
