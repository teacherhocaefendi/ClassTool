from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout, QMessageBox)

class EditStudentDialog(QDialog):
    def __init__(self, student_data, parent=None):
        super().__init__(parent)
        self.student_data = student_data
        self.setWindowTitle("Edit Student Information")
        self.setMinimumSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.number_input = QLineEdit(str(self.student_data['number']))
        self.first_name_input = QLineEdit(self.student_data['first_name'])
        self.last_name_input = QLineEdit(self.student_data['last_name'])

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Female", "Male"])
        current_gender = "Female" if self.student_data['gender'].lower() in ['female', 'kız'] else "Male"
        self.gender_input.setCurrentText(current_gender)

        form_layout.addRow("Student No:", self.number_input)
        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("Gender:", self.gender_input)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save Changes")
        btn_save.setStyleSheet("background-color: #36B37E; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_save.clicked.connect(self.save_changes)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("background-color: #DFE1E6; color: #172B4D; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def save_changes(self):
        num = self.number_input.text().strip()
        fn = self.first_name_input.text().strip()
        ln = self.last_name_input.text().strip()

        if not num or not fn:
            QMessageBox.warning(self, "Warning", "Number and First Name cannot be empty.")
            return

        self.updated_data = {
            'number': num,
            'first_name': fn,
            'last_name': ln,
            'gender': self.gender_input.currentText()
        }
        self.accept()