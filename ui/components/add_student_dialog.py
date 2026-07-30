from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QPushButton, QMessageBox)
from services.language_service import LanguageService
from utils.helpers import turkish_capitalize


class AddStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(LanguageService.get("add_student"))
        self.setFixedSize(400, 280)
        self.student_data = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        form_layout = QFormLayout()

        self.number_input = QLineEdit()
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()

        self.gender_input = QComboBox()
        self.gender_input.addItems([LanguageService.get("female"), LanguageService.get("male")])

        form_layout.addRow(LanguageService.get("no") + ":", self.number_input)
        form_layout.addRow(LanguageService.get("first_name") + ":", self.first_name_input)
        form_layout.addRow(LanguageService.get("last_name") + ":", self.last_name_input)
        form_layout.addRow(LanguageService.get("gender") + ":", self.gender_input)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.btn_save = QPushButton(LanguageService.get("save"))
        self.btn_cancel = QPushButton(LanguageService.get("cancel"))

        self.btn_save.setStyleSheet("background-color: #36B37E; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        self.btn_cancel.setStyleSheet("padding: 8px; border-radius: 4px; font-weight: bold;")

        self.btn_save.clicked.connect(self.validate_and_save)
        self.btn_cancel.clicked.connect(self.reject)

        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_save)

        layout.addLayout(button_layout)

    def validate_and_save(self):
        number = self.number_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        gender = "Female" if self.gender_input.currentIndex() == 0 else "Male"

        if not number or not first_name or not last_name:
            QMessageBox.warning(self, LanguageService.get("warning"), "Lütfen tüm alanları doldurun.")
            return

        self.student_data = {
            "student_number": number,
            "first_name": turkish_capitalize(first_name),
            "last_name": turkish_capitalize(last_name),
            "gender": gender
        }
        self.accept()