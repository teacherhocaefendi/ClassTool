import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton,
                             QLabel, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from database.db_manager import db
from utils.crypto import verify_pin, hash_pin
from services.usb_security_service import USBWatcherWorker, generate_signature
from services.language_service import LanguageService
from ui.components.setup_dialog import SetupDialog


def get_asset_path(filename):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, "assets", filename)


class LoginWindow(QWidget):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Class Tool - Giriş Ekranı")
        self.resize(420, 260)

        # Giriş penceresine ikonu mutlak yol ile bağlıyoruz
        icon_path = get_asset_path("app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.usb_worker = None
        self.check_initial_setup()
        self.setup_ui()
        self.start_usb_watcher()

    def check_initial_setup(self):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_settings WHERE key = 'pin_hash'")
            row = cursor.fetchone()
            if not row:
                setup = SetupDialog(self)
                setup.exec()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        self.title_label = QLabel(LanguageService.get("login_title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setPlaceholderText("PIN Şifresi")
        self.pin_input.setMaxLength(6)
        self.pin_input.setStyleSheet("""
            QLineEdit { padding: 12px; font-size: 18px; border: 2px solid #0052CC; border-radius: 6px; }
        """)
        self.pin_input.returnPressed.connect(self.verify_login)
        layout.addWidget(self.pin_input)

        login_btn = QPushButton(LanguageService.get("unlock_sys"))
        login_btn.setStyleSheet("""
            QPushButton { background-color: #0052CC; color: white; padding: 12px; font-size: 16px; font-weight: bold; border-radius: 6px; }
            QPushButton:hover { background-color: #003e99; }
        """)
        login_btn.clicked.connect(self.verify_login)
        layout.addWidget(login_btn)

    def get_stored_pin_hash(self):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_settings WHERE key = 'pin_hash'")
            row = cursor.fetchone()
            return row['value'] if row else hash_pin("1234")

    def start_usb_watcher(self):
        stored_hash = self.get_stored_pin_hash()
        target_sig = generate_signature(stored_hash)

        self.usb_worker = USBWatcherWorker(target_sig)
        self.usb_worker.usb_found.connect(self.on_usb_unlocked)
        self.usb_worker.start()

    def stop_usb_watcher(self):
        if self.usb_worker and self.usb_worker.isRunning():
            self.usb_worker.stop()
            self.usb_worker.wait(500)

    def on_usb_unlocked(self):
        self.stop_usb_watcher()
        self.login_successful.emit()

    def verify_login(self):
        pin = self.pin_input.text().strip()
        stored_hash = self.get_stored_pin_hash()

        if verify_pin(stored_hash=stored_hash, provided_pin=pin):
            self.pin_input.clear()
            self.stop_usb_watcher()
            self.login_successful.emit()
        else:
            QMessageBox.warning(self, "Erişim Engellendi", "Hatalı PIN Şifresi. Lütfen tekrar deneyin.")
            self.pin_input.clear()

    def closeEvent(self, event):
        self.stop_usb_watcher()
        super().closeEvent(event)