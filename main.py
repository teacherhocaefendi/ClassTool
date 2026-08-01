import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer, Qt

from database.db_manager import db
from services.theme_and_log_service import logger, ThemeManager, LOG_FILE
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def get_asset_path(filename):
    """Hem PyInstaller EXE çalışırken hem de normal Python çalışırken ikon yolunu kesin olarak bulur."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller ile paketlendiğinde
        base_path = sys._MEIPASS
    else:
        # Normal Python ile çalışırken
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "assets", filename)


def exception_hook(exctype, value, tb):
    print("=== BEKLENMEYEN HATA YAKALANDI ===")
    traceback.print_exception(exctype, value, tb)
    sys.__excepthook__(exctype, value, tb)


sys.excepthook = exception_hook


def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)

    if hasattr(Qt.HighDpiScaleFactorRoundingPolicy, 'PassThrough'):
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # UYGULAMA İKONUNU GLOBAL OLARAK BAĞLIYORUZ (TÜM PENCERELERDE GÖRÜNÜR)
    icon_path = get_asset_path("app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    logger.info("Class Tool Uygulaması Başlatılıyor [Sürüm 1.2.1]...")

    def on_app_exit():
        try:
            logger.info("Uygulama kapatılıyor, veritabanı kilitleniyor...")
            db.lock_database()
        except Exception as e:
            logger.error(f"Kapanışta veritabanı kilitlenirken hata: {e}")

    app.aboutToQuit.connect(on_app_exit)

    try:
        db.initialize_database()
        current_theme = ThemeManager.get_current_theme()
        ThemeManager.apply_theme(app, current_theme)
    except Exception as e:
        logger.error(f"Başlatma hatası: {e}")
        QMessageBox.critical(None, "Kritik Hata", f"Veritabanı başlatılamadı!\n\nLog Dosyası:\n{LOG_FILE}")
        sys.exit(1)

    login_win = LoginWindow()

    def on_login_success():
        global main_win
        try:
            logger.info("Giriş başarılı. Ana pencere yükleniyor.")
            main_win = MainWindow()
            main_win.show()
            login_win.hide()
            QTimer.singleShot(400, main_win.check_todays_homework_notifications)
        except Exception as ex:
            logger.error(f"Ana pencere çökme hatası: {ex}")
            QMessageBox.critical(None, "Sistem Hatası",
                                 f"Uygulama çalışırken beklenmeyen bir hata oluştu.\n\nLog Kaydı:\n{LOG_FILE}\n\nHata Detayı: {str(ex)}")

    login_win.login_successful.connect(on_login_success)
    login_win.show()

    try:
        sys.exit(app.exec())
    except Exception as err:
        logger.critical(f"Yakalanamayan kritik hata: {err}")
        QMessageBox.critical(None, "Kritik Hata", f"Kritik bir sistem hatası yakalandı!\n\nLog Konumu:\n{LOG_FILE}")


if __name__ == "__main__":
    main()