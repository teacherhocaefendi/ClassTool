from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QLabel, QMessageBox)
from database.db_manager import db


class ClassNotesDialog(QDialog):
    def __init__(self, class_id, class_name, parent=None):
        super().__init__(parent)
        self.class_id = class_id
        self.setWindowTitle(f"📌 Class Sticky Notes - {class_name}")
        self.resize(500, 400)
        self.setup_ui(class_name)
        self.load_note()

    def setup_ui(self, class_name):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(f"📝 Quick Notes & Announcements ({class_name})")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #172B4D;")
        layout.addWidget(title)

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Write lesson objectives, homework reminders, or announcements for this class...")
        self.note_input.setStyleSheet("""
            QTextEdit {
                background-color: #FFF9C4; color: #172B4D; font-size: 15px; 
                padding: 12px; border: 1px solid #FBC02D; border-radius: 6px;
            }
        """)
        layout.addWidget(self.note_input)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("background-color: #DFE1E6; color: #172B4D; padding: 8px 15px; font-weight: bold; border-radius: 4px;")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("💾 Save Notes")
        btn_save.setStyleSheet("background-color: #36B37E; color: white; padding: 8px 15px; font-weight: bold; border-radius: 4px;")
        btn_save.clicked.connect(self.save_note)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def load_note(self):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS class_notes (class_id INTEGER PRIMARY KEY, note TEXT)")
            cursor.execute("SELECT note FROM class_notes WHERE class_id = ?", (self.class_id,))
            row = cursor.fetchone()
            if row and row['note']:
                self.note_input.setText(row['note'])

    def save_note(self):
        note_text = self.note_input.toPlainText().strip()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO class_notes (class_id, note) VALUES (?, ?)
                ON CONFLICT(class_id) DO UPDATE SET note = excluded.note
            """, (self.class_id, note_text))
            conn.commit()

        QMessageBox.information(self, "Success", "Class notes saved successfully!")
        self.accept()