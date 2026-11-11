import os, hashlib, tempfile, shutil
from functools import wraps
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from config import Config
from models import (init_db, create_key, validate_key, consume_key,
                    list_keys, revoke_key, delete_key, list_logs, stats,
                    create_user, get_user, create_user_session, get_user_by_session, link_key_to_user)
from extractor import scan_folder
from generator import build
from agent import explain_event

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
init_db()

# ==========================================
# AQUÍ DEFINIMOS EL LINK DEL ADMIN
# ==========================================
ADMIN_LINK = "ad7-admin-panel"

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def admin_required(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*a, **k)
    return w

def user_required(f):
    @wraps(f)
    def w(*a, **k):
        tok = request.cookies.get("ad7_session") or session.get("ad7_session")
        user = get_user_by_session(tok)
        if not user:
            return redirect(url_for("login_page"))
        return f(*a, **k)
    return w

# ==========================================
# RUTAS PÚBLICAS Y LANDING
# ==========================================
@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        pwd = request.form.get("password", "")
        user = get_user(username)

        if user and user["password_hash"] == hash_pwd(pwd):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            tok = create_user_session(user["id"])
            resp = redirect(url_for("dashboard_page"))
            resp.set_cookie("ad7_session", tok, httponly=True, samesite="Lax", max_age=7*86400)
            return resp
        return render_template("login.html", error="Usuario o contraseña incorrectos.")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        pwd = request.form.get("password", "")
        ip = request.remote_addr

        if len(username) < 3 or len(pwd) < 4:
            return render_template("register.html", error="Usuario y contraseña deben ser mayores.")

        if create_user(username, hash_pwd(pwd), ip):
            user = get_user(username)
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            tok = create_user_session(user["id"])
            resp = redirect(url_for("dashboard_page"))
            resp.set_cookie("ad7_session", tok, httponly=True, samesite="Lax", max_age=7*86400)
            return resp
        return render_template("register.html", error="El nombre de usuario ya existe.")
    return render_template("register.html")

@app.route("/logout_user")
def logout_user():
    resp = redirect(url_for("landing"))
    resp.delete_cookie("ad7_session")
    session.clear()
    return resp

# ==========================================
# DASHBOARD Y ACTIVACIÓN DE KEY
# ==========================================
@app.route("/dashboard")
@user_required
def dashboard_page():
    tok = request.cookies.get("ad7_session")
    user = get_user_by_session(tok)
    return render_template("dashboard.html", user=user)

@app.route("/api/activate_key", methods=["POST"])
@user_required
def api_activate_key():
    data = request.get_json(silent=True) or {}
    key = (data.get("key") or "").strip()

    row, err = validate_key(key)
    if err:
        return jsonify(ok=False, error=err), 400

    consume_key(row["id"], f"user:{session.get('username')}")

    days = (row["expires_at"] - row["created_at"]) // 86400
    link_key_to_user(session["user_id"], key, days)

    return jsonify(ok=True)

# ==========================================
# EXTRACTOR (INDEX)
# ==========================================
@app.route("/index")
@user_required
def index_page():
    user = get_user(session.get("username"))
    if not user or not user.get("active_key"):
        return redirect(url_for("dashboard_page"))
    return render_template("index.html")

# ==========================================
# ADMIN (RUTAS DINÁMICAS)
# ==========================================
@app.route(f"/{ADMIN_LINK}", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if hash_pwd(pwd) == hash_pwd(Config.ADMIN_PASSWORD):
            session["admin"] = True
            return redirect(url_for("admin_panel"))
        return render_template("admin.html", error="Credenciales inválidas"), 401
    if session.get("admin"):
        return redirect(url_for("admin_panel"))
    return render_template("admin.html", error=None)

@app.route(f"/{ADMIN_LINK}/panel")
@admin_required
def admin_panel():
    return render_template("admin.html",
                           keys=list_keys(), logs=list_logs(),
                           st=stats(), admin_id=Config.ADMIN_ID, error=None,
                           logout_url=f"/{ADMIN_LINK}/logout",
                           create_key_url=f"/{ADMIN_LINK}/keys/create",
                           revoke_url_base=f"/{ADMIN_LINK}/keys",
                           index_url="/dashboard")

@app.route(f"/{ADMIN_LINK}/keys/create", methods=["POST"])
@admin_required
def admin_create_key():
    days = max(1, min(int(request.form.get("days", 7)), 365))
    uses = max(1, min(int(request.form.get("uses", 1)), 999))
    create_key("admin-web", days=days, uses=uses)
    return redirect(url_for("admin_panel"))

@app.route(f"/{ADMIN_LINK}/keys/<int:kid>/revoke", methods=["POST"])
@admin_required
def admin_revoke(kid):
    revoke_key(kid, "admin-web")
    return redirect(url_for("admin_panel"))

@app.route(f"/{ADMIN_LINK}/keys/<int:kid>/delete", methods=["POST"])
@admin_required
def admin_delete(kid):
    delete_key(kid, "admin-web")
    return redirect(url_for("admin_panel"))

@app.route(f"/{ADMIN_LINK}/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

# ==========================================
# APIS DEL EXTRACTOR (SUBIDA Y GENERACIÓN)
# ==========================================
@app.route("/api/upload", methods=["POST"])
@user_required
def api_upload():
    files = request.files.getlist("files")
    folder_name = (request.form.get("folder") or "carpeta").replace("/", "_").replace("\\", "_")
    if not files:
        return jsonify(ok=False, error="No se recibieron archivos"), 400

    folder = tempfile.mkdtemp(prefix="ad7_", dir=Config.UPLOAD_DIR)
    extract_dir = os.path.join(folder, folder_name)
    os.makedirs(extract_dir, exist_ok=True)

    saved = 0
    for f in files:
        if not f.filename: continue
        if not f.filename.lower().endswith((".lua", ".luac", ".txt")): continue
        base = os.path.basename(f.filename.replace("\\", "/")).replace("/", "_")
        stem, ext = os.path.splitext(base)
        dst = os.path.join(extract_dir, base)
        i = 1
        while os.path.exists(dst):
            dst = os.path.join(extract_dir, f"{stem}_{i}{ext}")
            i += 1
        f.save(dst)
        saved += 1

    if saved == 0:
        shutil.rmtree(folder, ignore_errors=True)
        return jsonify(ok=False, error="No se guardó ningún .lua/.luac"), 400

    results, count, code_blocks = scan_folder(extract_dir)
    session["last_scan"] = {"dir": extract_dir, "files": count}
    return jsonify(ok=True, folder=folder_name, files=count, events=results, blocks=code_blocks)

@app.route("/api/analyze", methods=["POST"])
@user_required
def api_analyze():
    data = request.get_json(silent=True) or {}
    ev = (data.get("event") or "").strip()
    block = data.get("block") or ""
    if not ev: return jsonify(ok=False, error="Sin evento"), 400
    return jsonify(ok=True, agent=explain_event(ev, block))

@app.route("/api/generate", methods=["POST"])
@user_required
def api_generate():
    data = request.get_json(silent=True) or {}
    event = data.get("event")
    loop_type = data.get("loop_type", "loose_ipairs")
    extra = data.get("extra_args", "player")
    rand_id = data.get("random_id", False)
    event_type = data.get("event_type", "triggerServerEvent")

    if not event:
        return jsonify(ok=False, error="Falta el evento"), 400

    lua = build(event, loop_type, rand_id, extra, event_type)
    return jsonify(ok=True, lua=lua)

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=False)
