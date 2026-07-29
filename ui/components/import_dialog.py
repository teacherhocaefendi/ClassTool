from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QLabel, QFileDialog, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from services.ocr_service import OCRService
from services.eokul_parser_service import EOkulParserService


class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self):
        try:
            text = OCRService.extract_text_from_image(self.image_path)
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class ImportDialog(QDialog):
    def __init__(self, class_id, parent=None):
        super().__init__(parent)
        self.class_id = class_id
        self.setWindowTitle("🤖 AI Smart Scanner & Text Import")
        self.setFixedSize(580, 480)  # Derli toplu pencere boyutu
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        instructions = QLabel(
            "<b>🤖 AI Scanner & Clipboard Parser</b><br>"
            "1. Sınıf listesi görselini yükleyin (AI otomatik okur) veya metni doğrudan yapıştırın.<br>"
            "2. Format: <i>[Numara] [Ad] [Soyad] [Kız/Erkek]</i>"
        )
        instructions.setStyleSheet("font-size: 13px;")
        layout.addWidget(instructions)

        toolbar = QHBoxLayout()
        self.btn_upload = QPushButton("📷 Upload Class List Image (AI Vision)")
        self.btn_upload.setStyleSheet("""
            QPushButton { background-color: #0052CC; color: white; padding: 10px; font-weight: bold; border-radius: 6px; }
            QPushButton:hover { background-color: #003e99; }
        """)
        self.btn_upload.clicked.connect(self.upload_image)

        toolbar.addWidget(self.btn_upload)
        layout.addLayout(toolbar)

        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Paste list here or upload an image...")
        layout.addWidget(self.text_editor)

        action_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("padding: 8px 15px; font-weight: bold; border-radius: 4px;")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("💾 Save to Database")
        btn_save.setStyleSheet("background-color: #36B37E; color: white; padding: 8px 15px; font-weight: bold; border-radius: 4px;")
        btn_save.clicked.connect(self.process_text)

        action_layout.addWidget(btn_cancel)
        action_layout.addWidget(btn_save)
        layout.addLayout(action_layout)

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Class List Image", "", "Image Files (*.png *.jpg *.jpeg)",
            options=QFileDialog.Option.DontUseNativeDialog
        )
        if not file_path:
            return

        self.btn_upload.setEnabled(False)
        self.text_editor.setPlainText("🤖 Gemini AI Vision is scanning image...")

        self.worker = AIWorker(file_path)
        self.worker.finished.connect(self.on_ai_success)
        self.worker.error.connect(self.on_ai_error)
        self.worker.start()

    def on_ai_success(self, text):
        self.btn_upload.setEnabled(True)
        self.text_editor.setPlainText(text)

    def on_ai_error(self, error_message):
        self.btn_upload.setEnabled(True)
        QMessageBox.critical(self, "AI Processing Error", error_message)
        self.text_editor.clear()

    def process_text(self):
        raw_text = self.text_editor.toPlainText()
        try:
            count = EOkulParserService.parse_raw_text(self.class_id, raw_text)
            QMessageBox.information(self, "Success", f"Successfully imported {count} students.")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Parsing Error", str(e))