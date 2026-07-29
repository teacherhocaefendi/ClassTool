from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QPushButton, QMessageBox)


class AddStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ Add New Student")
        self.setFixedSize(400, 280)  # Kibar sabit boyut
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
        self.gender_input.addItems(["Female", "Male"])

        form_layout.addRow("Student No:", self.number_input)
        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("Gender:", self.gender_input)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_cancel = QPushButton("Cancel")

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
        gender = self.gender_input.currentText()

        if not number or not first_name or not last_name:
            QMessageBox.warning(self, "Validation Error", "All fields must be filled.")
            return

        self.student_data = {
            "student_number": number,
            "first_name": first_name.capitalize(),
            "last_name": last_name.capitalize(),
            "gender": gender
        }
        self.accept()