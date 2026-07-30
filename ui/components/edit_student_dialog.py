from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout,
                             QMessageBox)
from services.language_service import LanguageService
from utils.helpers import turkish_capitalize


class EditStudentDialog(QDialog):
    def __init__(self, student_data, parent=None):
        super().__init__(parent)
        self.student_data = student_data
        self.setWindowTitle(LanguageService.get("edit_info"))
        self.setMinimumSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.number_input = QLineEdit(str(self.student_data['number']))
        self.first_name_input = QLineEdit(self.student_data['first_name'])
        self.last_name_input = QLineEdit(self.student_data['last_name'])

        self.gender_input = QComboBox()
        self.gender_input.addItems([LanguageService.get("female"), LanguageService.get("male")])

        current_gender_idx = 0 if self.student_data['gender'].lower() in ['female', 'kız'] else 1
        self.gender_input.setCurrentIndex(current_gender_idx)

        form_layout.addRow(LanguageService.get("no") + ":", self.number_input)
        form_layout.addRow(LanguageService.get("first_name") + ":", self.first_name_input)
        form_layout.addRow(LanguageService.get("last_name") + ":", self.last_name_input)
        form_layout.addRow(LanguageService.get("gender") + ":", self.gender_input)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton(LanguageService.get("save"))
        btn_save.setStyleSheet(
            "background-color: #36B37E; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_save.clicked.connect(self.save_changes)

        btn_cancel = QPushButton(LanguageService.get("cancel"))
        btn_cancel.setStyleSheet(
            "background-color: #DFE1E6; color: #172B4D; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def save_changes(self):
        num = self.number_input.text().strip()
        fn = self.first_name_input.text().strip()
        ln = self.last_name_input.text().strip()

        if not num or not fn:
            QMessageBox.warning(self, LanguageService.get("warning"), "Öğrenci numarası ve adı boş bırakılamaz.")
            return

        self.updated_data = {
            'number': num,
            'first_name': turkish_capitalize(fn),
            'last_name': turkish_capitalize(ln),
            'gender': "Female" if self.gender_input.currentIndex() == 0 else "Male"
        }
        self.accept()