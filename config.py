import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-change-me")
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "zeyun-admin-2024")
    SECRET_ADMIN_URL = os.getenv("SECRET_ADMIN_URL", "admin-secreto") # <-- NUEVO
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    DB_PATH = os.getenv("DB_PATH", "zeyun.db")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    MAX_CONTENT_LENGTH = 300 * 1024 * 1024
