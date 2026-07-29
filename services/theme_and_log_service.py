import os
import logging
from pathlib import Path
from database.db_manager import db

DOCS_DIR = Path.home() / "Documents" / "ClassTool"
LOG_DIR = DOCS_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

logger = logging.getLogger("ClassTool")


class ThemeManager:
    LIGHT_STYLESHEET = """
        QMainWindow, QDialog, QWidget { background-color: #F4F5F7; color: #172B4D; font-family: 'Segoe UI', Arial, sans-serif; }
        QLabel { color: #172B4D; }
        QScrollBar:vertical { border: none; background: #EBECF0; width: 10px; border-radius: 5px; margin: 0px; }
        QScrollBar::handle:vertical { background: #C1C7D0; min-height: 20px; border-radius: 5px; }

        QTableWidget, QListWidget { 
            background-color: #FFFFFF; color: #172B4D; gridline-color: #DFE1E6; 
            border: 2px solid #DFE1E6; border-radius: 10px; padding: 5px; font-size: 14px;
            outline: none;
        }
        QTableWidget::item { 
            color: #172B4D; padding: 8px; border-bottom: 1px solid #EBECF0; 
            outline: none;
        }
        QTableWidget::item:focus, QListWidget::item:focus { 
            outline: none; border: none; 
        }
        QTableWidget::item:selected, QListWidget::item:selected { 
            background-color: #0052CC; color: #FFFFFF; font-weight: bold; outline: none; 
        }
        QHeaderView::section { background-color: #EBECF0; color: #172B4D; font-weight: bold; font-size: 14px; padding: 8px; border: none; }
        QComboBox, QLineEdit, QTextEdit { background-color: #FFFFFF; color: #172B4D; border: 2px solid #DFE1E6; border-radius: 6px; padding: 6px; }
        QGroupBox { font-weight: bold; color: #0052CC; border: 2px solid #DFE1E6; border-radius: 8px; background-color: #FFFFFF; }
    """

    DARK_STYLESHEET = """
        QMainWindow, QDialog, QWidget { background-color: #18191A; color: #E4E6EB; font-family: 'Segoe UI', Arial, sans-serif; }
        QLabel { color: #E4E6EB; }
        QScrollBar:vertical { border: none; background: #242526; width: 10px; border-radius: 5px; margin: 0px; }
        QScrollBar::handle:vertical { background: #3A3B3C; min-height: 20px; border-radius: 5px; }

        QTableWidget, QListWidget { 
            background-color: #242526; color: #E4E6EB; gridline-color: #3A3B3C; 
            border: 2px solid #3A3B3C; border-radius: 10px; padding: 5px; font-size: 14px;
            outline: none;
        }
        QTableWidget::item { 
            color: #E4E6EB; padding: 8px; border-bottom: 1px solid #3A3B3C; 
            outline: none;
        }
        QTableWidget::item:focus, QListWidget::item:focus { 
            outline: none; border: none; 
        }
        QTableWidget::item:selected, QListWidget::item:selected { 
            background-color: #2D88FF; color: #FFFFFF; font-weight: bold; outline: none; 
        }
        QHeaderView::section { background-color: #3A3B3C; color: #E4E6EB; font-weight: bold; font-size: 14px; padding: 8px; border: none; }
        QComboBox, QLineEdit, QTextEdit { background-color: #242526; color: #E4E6EB; border: 2px solid #3A3B3C; border-radius: 6px; padding: 6px; }
        QGroupBox { font-weight: bold; color: #4FC3F7; border: 2px solid #3A3B3C; border-radius: 8px; background-color: #242526; }
    """

    @classmethod
    def get_current_theme(cls):
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM app_settings WHERE key = 'theme'")
                row = cursor.fetchone()
                return row['value'] if row else "light"
        except Exception:
            return "light"

    @classmethod
    def set_theme(cls, theme_name):
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                               INSERT INTO app_settings (key, value)
                               VALUES ('theme', ?) ON CONFLICT(key) DO
                               UPDATE SET value = excluded.value
                               """, (theme_name,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving theme: {e}")

    @classmethod
    def apply_theme(cls, app_instance, theme_name):
        if app_instance is not None:
            if theme_name == "dark":
                app_instance.setStyleSheet(cls.DARK_STYLESHEET)
            else:
                app_instance.setStyleSheet(cls.LIGHT_STYLESHEET)