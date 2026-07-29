from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QMessageBox, QLabel)
from database.db_manager import db
from services.language_service import LanguageService


class ClassManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(LanguageService.get("new_class"))
        self.setFixedSize(400, 260)  # Devasa tam ekran yerine kibar sabit boyut
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel(LanguageService.get("new_class"))
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0052CC;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.class_name_input = QLineEdit()
        self.class_name_input.setPlaceholderText("e.g., 5-A, 8-B")

        self.academic_year_input = QLineEdit()
        self.academic_year_input.setText("2026-2027")

        for inp in [self.class_name_input, self.academic_year_input]:
            inp.setStyleSheet("padding: 8px; border: 1px solid #DFE1E6; border-radius: 4px;")

        form_layout.addRow(LanguageService.get("class_name"), self.class_name_input)
        form_layout.addRow(LanguageService.get("academic_year"), self.academic_year_input)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton(LanguageService.get("cancel"))
        btn_cancel.setStyleSheet("padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton(LanguageService.get("save_class"))
        btn_save.setStyleSheet("""
            QPushButton { background-color: #36B37E; color: white; padding: 8px; 
                          font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #2b8f65; }
        """)
        btn_save.clicked.connect(self.save_class)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def save_class(self):
        name = self.class_name_input.text().strip()
        year = self.academic_year_input.text().strip()

        if not name or not year:
            QMessageBox.warning(self, "Validation Error", "All fields must be filled.")
            return

        try:
            db.add_class(name, year)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create class:\n{e}")