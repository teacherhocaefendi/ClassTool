from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QPushButton, QLabel, QTextEdit, QSlider, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from database.db_manager import db
from services.report_service import ReportService


class ProfileDialog(QDialog):
    def __init__(self, student_id, student_name, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.student_name = student_name
        self.setWindowTitle(f"Private Profile: {student_name}")
        self.resize(650, 600)
        self.notes_hidden = True
        self.setup_ui(student_name)
        self.load_profile_data()
        self.load_student_logs()

    def setup_ui(self, student_name):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(f"👤 {student_name}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #172B4D;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.soc_slider = self.create_slider()
        self.foc_slider = self.create_slider()
        self.part_slider = self.create_slider()

        form_layout.addRow("Sociability (1-5):", self.soc_slider)
        form_layout.addRow("Focus Level (1-5):", self.foc_slider)
        form_layout.addRow("Participation (1-5):", self.part_slider)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("e.g., Talkative, Visual Learner")
        self.tags_input.setStyleSheet("padding: 6px; border: 1px solid #DFE1E6; border-radius: 4px;")
        form_layout.addRow("Tags:", self.tags_input)
        layout.addLayout(form_layout)

        # Gizli Öğretmen Notları
        notes_header = QHBoxLayout()
        notes_header.addWidget(QLabel("<b>Teacher Private Notes:</b>"))
        notes_header.addStretch()
        self.btn_privacy = QPushButton("👁️ Show Notes")
        self.btn_privacy.setStyleSheet(
            "background-color: #FF991F; color: white; padding: 4px 10px; font-weight: bold; border-radius: 4px;")
        self.btn_privacy.clicked.connect(self.toggle_privacy)
        notes_header.addWidget(self.btn_privacy)
        layout.addLayout(notes_header)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setVisible(False)

        self.hidden_placeholder = QLabel("🔒 Notes are hidden for classroom security.")
        self.hidden_placeholder.setStyleSheet(
            "background-color: #EBECF0; padding: 10px; border-radius: 4px; color: #5E6C84; font-style: italic;")
        self.hidden_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.notes_input)
        layout.addWidget(self.hidden_placeholder)

        # GEÇMİŞ PUANLAMA LOGLARI TABLOSU
        layout.addWidget(QLabel("<b>Activity & Log History:</b>"))
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(3)
        self.logs_table.setHorizontalHeaderLabels(["Type", "Category", "Comment / Date"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.logs_table.verticalHeader().setVisible(False)
        self.logs_table.setMaximumHeight(130)
        layout.addWidget(self.logs_table)

        # BUTONLAR
        btn_layout = QHBoxLayout()

        # YENİ: PDF Rapor İndir Butonu
        btn_pdf = QPushButton("📄 PDF Rapor İndir")
        btn_pdf.setStyleSheet(
            "background-color: #0747A6; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_pdf.clicked.connect(self.export_pdf)

        btn_cancel = QPushButton("Cancel")
        btn_save = QPushButton("Save Profile")

        btn_cancel.setStyleSheet(
            "background-color: #DFE1E6; color: #172B4D; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_save.setStyleSheet(
            "background-color: #0052CC; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")

        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.save_data)

        btn_layout.addWidget(btn_pdf)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def create_slider(self):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(5)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        return slider

    def toggle_privacy(self):
        self.notes_hidden = not self.notes_hidden
        self.notes_input.setVisible(not self.notes_hidden)
        self.hidden_placeholder.setVisible(self.notes_hidden)
        self.btn_privacy.setText("👁️ Show Notes" if self.notes_hidden else "🙈 Hide Notes")

    def load_profile_data(self):
        profile = db.get_student_profile(self.student_id)
        self.soc_slider.setValue(profile['sociability_score'])
        self.foc_slider.setValue(profile['focus_score'])
        self.part_slider.setValue(profile['participation_score'])
        self.tags_input.setText(profile['personality_tags'])
        self.notes_input.setText(profile['teacher_notes'])

    def load_student_logs(self):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT log_type, category_tag, comment, created_at
                           FROM logs
                           WHERE student_id = ?
                           ORDER BY id DESC
                           """, (self.student_id,))
            logs = cursor.fetchall()

        self.logs_table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            self.logs_table.setItem(row, 0, QTableWidgetItem(str(log['log_type'])))
            self.logs_table.setItem(row, 1, QTableWidgetItem(str(log['category_tag'])))
            self.logs_table.setItem(row, 2, QTableWidgetItem(f"{log['comment']} ({log['created_at']})"))

    def export_pdf(self):
        safe_name = self.student_name.replace(" ", "_")
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Öğrenci Gelişim Raporu Kaydet", f"{safe_name}_Gelisim_Raporu.pdf", "PDF Files (*.pdf)",
            options=QFileDialog.Option.DontUseNativeDialog
        )
        if file_path:
            try:
                ReportService.export_student_pdf_report(self.student_id, file_path)
                QMessageBox.information(self, "Başarılı", f"Öğrenci gelişim raporu PDF olarak kaydedildi:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF oluşturulamadı:\n{str(e)}")

    def save_data(self):
        try:
            db.update_student_profile(
                self.student_id,
                self.soc_slider.value(),
                self.foc_slider.value(),
                self.part_slider.value(),
                self.tags_input.text().strip(),
                self.notes_input.toPlainText().strip()
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save profile:\n{e}")