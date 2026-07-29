import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer

from database.db_manager import db
from services.theme_and_log_service import logger, ThemeManager, LOG_FILE
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
import sys
import traceback

def exception_hook(exctype, value, tb):
    print("=== CRASH DETECTED ===")
    traceback.print_exception(exctype, value, tb)
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook

def main():
    app = QApplication(sys.argv)
    logger.info("Starting Class Tool Application [Alpha 1.0]...")

    # Uygulama kapanırken DB dosyasını otomatik kilitlesin
    def on_app_exit():
        try:
            logger.info("Encrypting and locking database before exit...")
            db.lock_database()
        except Exception as e:
            logger.error(f"Error locking database on exit: {e}")

    app.aboutToQuit.connect(on_app_exit)

    icon_path = os.path.join("assets", "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    try:
        db.initialize_database()
        current_theme = ThemeManager.get_current_theme()
        ThemeManager.apply_theme(app, current_theme)
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        QMessageBox.critical(None, "Fatal Error", f"Veritabanı başlatılamadı!\nLog Dosyası:\n{LOG_FILE}")
        sys.exit(1)

    login_win = LoginWindow()

    def on_login_success():
        global main_win  # <-- ÇÖZÜM: Değişkeni global yaparak bellekten silinmesini engelliyoruz
        try:
            logger.info("Login successful. Initializing MainWindow.")
            main_win = MainWindow()
            main_win.show()
            login_win.hide()
            QTimer.singleShot(400, main_win.check_todays_homework_notifications)
        except Exception as ex:
            logger.error(f"MainWindow crash: {ex}")
            QMessageBox.critical(None, "Crash Error", f"Uygulama çalışırken bir hata oluştu.\nLog Kaydı:\n{LOG_FILE}\n\nHata: {str(ex)}")

    login_win.login_successful.connect(on_login_success)
    login_win.show()

    try:
        sys.exit(app.exec())
    except Exception as err:
        logger.critical(f"Unhandled exception: {err}")
        QMessageBox.critical(None, "Critical Error", f"Kritik hata yakalandı!\nLog Konumu:\n{LOG_FILE}")


if __name__ == "__main__":
    main()