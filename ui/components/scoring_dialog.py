from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout,
                             QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from database.db_manager import db


class ScoringDialog(QDialog):
    def __init__(self, student_id, student_name, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.setWindowTitle(f"⭐ Puan Ver: {student_name}")
        self.setFixedSize(520, 380)  # Devasa tam ekran yerine kibar sabit boyut
        self.setup_ui(student_name)

    def setup_ui(self, student_name):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel(f"👤 {student_name}")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)

        # Pozitif Davranışlar (+)
        positives = [
            ("Derse Katılım", "participation"),
            ("Liderlik / Davranış", "behavior")
        ]

        for i, (label_text, tag) in enumerate(positives):
            btn = QPushButton(f"➕ {label_text}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #10B981; color: white; padding: 12px;
                    font-size: 14px; font-weight: bold; border-radius: 6px; border: none;
                }
                QPushButton:hover { background-color: #059669; }
            """)
            btn.clicked.connect(lambda checked, t=tag, n=label_text: self.log_event("+", t, n))
            grid.addWidget(btn, i, 0)

        # Negatif Davranışlar (-)
        negatives = [
            ("Dikkatsiz / Pasif", "participation"),
            ("Olumsuz Davranış", "behavior")
        ]

        for i, (label_text, tag) in enumerate(negatives):
            btn = QPushButton(f"➖ {label_text}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444; color: white; padding: 12px;
                    font-size: 14px; font-weight: bold; border-radius: 6px; border: none;
                }
                QPushButton:hover { background-color: #DC2626; }
            """)
            btn.clicked.connect(lambda checked, t=tag, n=label_text: self.log_event("-", t, n))
            grid.addWidget(btn, i, 1)

        layout.addLayout(grid)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #374151; color: #F3F4F6; padding: 8px;
                font-size: 13px; font-weight: bold; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #4B5563; }
        """)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def log_event(self, log_type, tag, label_text):
        try:
            db.add_log_entry(self.student_id, log_type, tag, label_text)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt eklenirken hata oluştu:\n{e}")