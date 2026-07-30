import os
import string
import hashlib
from PyQt6.QtCore import QThread, pyqtSignal
from services.theme_and_log_service import logger

KEY_FILE_NAME = ".class_tool.key"

def generate_signature(pin_hash):
    """PIN hash'inden benzersiz bir USB imzası üretir."""
    return hashlib.sha256(f"AMMAR_SECURE_{pin_hash}".encode('utf-8')).hexdigest()

class USBWatcherWorker(QThread):
    usb_found = pyqtSignal()
    usb_removed = pyqtSignal()

    def __init__(self, target_signature, parent=None):
        super().__init__(parent)
        self.target_signature = target_signature
        self.running = True
        self.is_connected = False

    def run(self):
        while self.running:
            found = self.check_usb_key()
            if found and not self.is_connected:
                self.is_connected = True
                self.usb_found.emit()
            elif not found and self.is_connected:
                self.is_connected = False
                self.usb_removed.emit()
            self.msleep(1000)

    def check_usb_key(self):
        available_drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

        for drive in available_drives:
            key_path = os.path.join(drive, KEY_FILE_NAME)
            if os.path.exists(key_path):
                try:
                    with open(key_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content == self.target_signature:
                            return True
                except Exception:
                    continue
        return False

    def stop(self):
        self.running = False


def create_usb_key_file(drive_letter, pin_hash):
    """Seçilen USB'ye öğretmenin PIN'i ile imzalanmış gizli dosyayı yazar."""
    target_path = os.path.join(f"{drive_letter}:\\", KEY_FILE_NAME)
    try:
        signature = generate_signature(pin_hash)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(signature)
        return True
    except Exception as e:
        logger.error(f"USB Anahtarı oluşturma hatası: {e}")
        return False