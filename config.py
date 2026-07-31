import os
from pathlib import Path

# PATHS (Kullanıcı Belgelerim Klasörüne Sabitlendi)
DOCS_DIR = Path.home() / "Documents" / "ClassTool"
DB_DIR = DOCS_DIR / "database"
DB_PATH = DB_DIR / "student_tracking.db"

DB_DIR.mkdir(parents=True, exist_ok=True)

# UI CONSTANTS
APP_NAME = "Smart Board Student Tracker"
APP_VERSION = "1.2.0"

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

COLORS = {
    "primary": "#0052CC",
    "secondary": "#FF991F",
    "background": "#F4F5F7",
    "surface": "#FFFFFF",
    "text_dark": "#172B4D",
    "text_light": "#FFFFFF",
    "success": "#36B37E",
    "danger": "#FF5630"
}

DB_ENCRYPTION_KEY = os.environ.get("APP_DB_KEY", "dev_default_secure_key_123")

WEIGHTS = {
    "homework": 0.40,
    "participation": 0.40,
    "behavior": 0.20
}