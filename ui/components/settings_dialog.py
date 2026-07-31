import string
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QMessageBox, QLabel, QFrame, QFileDialog, QHBoxLayout)
from database.db_manager import db
from utils.crypto import hash_pin, verify_pin
from services.usb_security_service import create_usb_key_file
from services.backup_service import BackupService
from services.language_service import LanguageService


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(LanguageService.get("settings_title"))
        self.setFixedSize(420, 480)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 1. PIN DEĞİŞTİRME BÖLÜMÜ
        title_pin = QLabel(LanguageService.get("pin_title"))
        title_pin.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(title_pin)

        form_layout = QFormLayout()
        self.current_pin_input = QLineEdit()
        self.current_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_pin_input.setPlaceholderText(LanguageService.get("current_pin"))

        self.new_pin_input = QLineEdit()
        self.new_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pin_input.setPlaceholderText(LanguageService.get("new_pin"))

        self.confirm_pin_input = QLineEdit()
        self.confirm_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pin_input.setPlaceholderText(LanguageService.get("confirm_pin"))

        for inp in [self.current_pin_input, self.new_pin_input, self.confirm_pin_input]:
            inp.setStyleSheet("padding: 6px; border-radius: 4px;")

        form_layout.addRow(LanguageService.get("current_pin") + ":", self.current_pin_input)
        form_layout.addRow(LanguageService.get("new_pin") + ":", self.new_pin_input)
        form_layout.addRow(LanguageService.get("confirm_pin") + ":", self.confirm_pin_input)
        layout.addLayout(form_layout)

        btn_save = QPushButton(LanguageService.get("update_pin"))
        btn_save.setStyleSheet("background-color: #0052CC; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_save.clicked.connect(self.update_pin)
        layout.addWidget(btn_save)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)

        # 2. GÜVENLİ USB ANAHTAR
        title_usb = QLabel(LanguageService.get("usb_title"))
        title_usb.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(title_usb)

        btn_make_usb = QPushButton(LanguageService.get("usb_key_btn"))
        btn_make_usb.setStyleSheet("background-color: #36B37E; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_make_usb.clicked.connect(self.make_usb_key)
        layout.addWidget(btn_make_usb)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line2)

        # 3. TAŞINABİLİR VERİ YEDEKLEME
        title_data = QLabel(LanguageService.get("backup_title"))
        title_data.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_data)

        data_btn_layout = QHBoxLayout()
        btn_export = QPushButton(LanguageService.get("export_backup"))
        btn_export.setStyleSheet("background-color: #0747A6; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_export.clicked.connect(self.export_backup)

        btn_import = QPushButton(LanguageService.get("import_backup"))
        btn_import.setStyleSheet("background-color: #FF5630; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_import.clicked.connect(self.import_backup)

        data_btn_layout.addWidget(btn_export)
        data_btn_layout.addWidget(btn_import)
        layout.addLayout(data_btn_layout)

    def get_stored_pin_hash(self):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_settings WHERE key = 'pin_hash'")
            row = cursor.fetchone()
            return row['value'] if row else hash_pin("1234")

    def update_pin(self):
        curr = self.current_pin_input.text().strip()
        new_p = self.new_pin_input.text().strip()
        conf_p = self.confirm_pin_input.text().strip()
        stored_hash = self.get_stored_pin_hash()

        if not verify_pin(stored_hash, curr):
            QMessageBox.warning(self, LanguageService.get("error"), LanguageService.get("curr_pin_wrong"))
            return

        if len(new_p) < 4:
            QMessageBox.warning(self, LanguageService.get("error"), LanguageService.get("pin_short"))
            return

        if new_p != conf_p:
            QMessageBox.warning(self, LanguageService.get("error"), LanguageService.get("pins_mismatch"))
            return

        new_hash = hash_pin(new_p)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO app_settings (key, value) VALUES ('pin_hash', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (new_hash,))
            conn.commit()

        QMessageBox.information(self, LanguageService.get("success"), LanguageService.get("pin_updated"))
        self.accept()

    def make_usb_key(self):
        drives = [f"{d}" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\") and d not in ['C', 'D']]
        if not drives:
            QMessageBox.warning(self, LanguageService.get("usb_not_found_title"), LanguageService.get("usb_not_found_msg"))
            return

        target_drive = drives[0]
        stored_hash = self.get_stored_pin_hash()

        confirm_title = "Güvenlik USB'si Oluştur" if LanguageService.current_lang == "tr" else "Create Security USB"
        confirm_msg = f"({target_drive}:) Sürücüsü Güvenlik Anahtarınız Yapılsın mı?\nHiçbir dosyanız silinmeyecektir." if LanguageService.current_lang == "tr" else f"Turn Drive ({target_drive}:) into your Security Dongle?\nNo files will be deleted."

        reply = QMessageBox.question(
            self, confirm_title, confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if create_usb_key_file(target_drive, stored_hash):
                succ_msg = f"USB Anahtar {target_drive}: sürücüsüne başarıyla kaydedildi!" if LanguageService.current_lang == "tr" else f"USB Key successfully registered on drive {target_drive}:!"
                QMessageBox.information(self, LanguageService.get("success"), succ_msg)
            else:
                err_msg = "USB sürücüsüne anahtar yazılamadı." if LanguageService.current_lang == "tr" else "Failed to write key to USB drive."
                QMessageBox.critical(self, LanguageService.get("error"), err_msg)

    def export_backup(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Backup", "class_tool_backup.json", "JSON Files (*.json)", options=QFileDialog.Option.DontUseNativeDialog)
        if file_path:
            try:
                BackupService.export_full_backup_json(file_path)
                QMessageBox.information(self, "Success", f"Tüm veriler başarıyla yedeklendi:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Yedekleme başarısız:\n{e}")

    def import_backup(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Backup", "", "JSON Files (*.json)", options=QFileDialog.Option.DontUseNativeDialog)
        if file_path:
            reply = QMessageBox.question(
                self, "Confirm Import",
                "Mevcut tüm veriler silinecek ve yedekten yüklenecektir. Emin misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    BackupService.import_full_backup_json(file_path)
                    QMessageBox.information(self, "Success", "Yedek başarıyla yüklendi! Uygulama yenileniyor.")
                    self.accept()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Yedek yükleme başarısız:\n{e}")