from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QMessageBox, QLabel)
from database.db_manager import db
from utils.crypto import hash_pin


class SetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🚀 First Time Setup - Master Password")
        self.setFixedSize(400, 260)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Welcome! Set Your Access PIN")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0052CC;")
        layout.addWidget(title)

        form = QFormLayout()
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setPlaceholderText("Enter 4-6 digit PIN")

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirm PIN")

        for inp in [self.pin_input, self.confirm_input]:
            inp.setStyleSheet("padding: 8px; border: 1px solid #DFE1E6; border-radius: 4px;")

        form.addRow("New PIN:", self.pin_input)
        form.addRow("Confirm PIN:", self.confirm_input)
        layout.addLayout(form)

        btn_save = QPushButton("💾 Save & Start")
        btn_save.setStyleSheet("background-color: #36B37E; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        btn_save.clicked.connect(self.save_setup)
        layout.addWidget(btn_save)

    def save_setup(self):
        p1 = self.pin_input.text().strip()
        p2 = self.confirm_input.text().strip()

        if len(p1) < 4:
            QMessageBox.warning(self, "Error", "PIN must be at least 4 digits.")
            return

        if p1 != p2:
            QMessageBox.warning(self, "Error", "PINs do not match.")
            return

        hashed = hash_pin(p1)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO app_settings (key, value) VALUES ('pin_hash', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (hashed,))
            conn.commit()

        QMessageBox.information(self, "Success", "Master PIN configured successfully!")
        self.accept()