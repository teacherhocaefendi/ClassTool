from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout,
                             QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from database.db_manager import db

class ScoringDialog(QDialog):
    def __init__(self, student_id, student_name, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.setWindowTitle(f"Score: {student_name}")
        self.setMinimumSize(800, 600)  # Pencereni çok fazla küçültmeyi engeller
        self.showMaximized()
        self.setup_ui(student_name)

    def setup_ui(self, student_name):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel(f"Evaluating: {student_name}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #172B4D;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(15)

        # Positive Behaviors (+)
        positives = [
            ("High Participation", "participation"),
            ("Good Behavior / Leadership", "behavior")
        ]

        for i, (label_text, tag) in enumerate(positives):
            btn = QPushButton(f"➕ {label_text}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #36B37E; color: white; padding: 15px;
                    font-size: 16px; font-weight: bold; border-radius: 8px;
                }
                QPushButton:hover { background-color: #2b8f65; }
            """)
            btn.clicked.connect(lambda checked, t=tag, n=label_text: self.log_event("+", t, n))
            grid.addWidget(btn, i, 0)

        # Negative Behaviors (-)
        negatives = [
            ("Distracted / Passive", "participation"),
            ("Disruptive Behavior", "behavior")
        ]

        for i, (label_text, tag) in enumerate(negatives):
            btn = QPushButton(f"➖ {label_text}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF5630; color: white; padding: 15px;
                    font-size: 16px; font-weight: bold; border-radius: 8px;
                }
                QPushButton:hover { background-color: #cc4526; }
            """)
            btn.clicked.connect(lambda checked, t=tag, n=label_text: self.log_event("-", t, n))
            grid.addWidget(btn, i, 1)

        layout.addLayout(grid)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #DFE1E6; color: #172B4D; padding: 10px;
                font-size: 16px; font-weight: bold; border-radius: 8px;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def log_event(self, log_type, tag, label_text):
        try:
            db.add_log_entry(self.student_id, log_type, tag, label_text)
            self.accept() # Close dialog on success
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save log:\n{e}")