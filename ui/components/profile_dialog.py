from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QPushButton, QLabel, QTextEdit, QSlider, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QFrame)
from PyQt6.QtCore import Qt
from database.db_manager import db
from services.report_service import ReportService
from services.badge_service import BadgeService, BADGES
from services.theme_and_log_service import ThemeManager
from ui.components.confetti_widget import ConfettiWidget


class ProfileDialog(QDialog):
    def __init__(self, student_id, student_name, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.student_name = student_name
        self.setWindowTitle(f"Öğrenci Profili: {student_name}")
        self.resize(650, 540)
        self.notes_hidden = True
        self.setup_ui(student_name)
        self.load_profile_data()
        self.load_student_logs()
        self.load_badges()

    def setup_ui(self, student_name):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        is_dark = (ThemeManager.get_current_theme() == "dark")
        title_color = "#60A5FA" if is_dark else "#1D4ED8"

        title = QLabel(f"👤 {student_name}")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {title_color};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(6)
        self.soc_slider = self.create_slider()
        self.foc_slider = self.create_slider()
        self.part_slider = self.create_slider()

        form_layout.addRow("Sosyallik (1-5):", self.soc_slider)
        form_layout.addRow("Odaklanma (1-5):", self.foc_slider)
        form_layout.addRow("Katılım (1-5):", self.part_slider)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Örn: Derse İlgili, Görsel Öğrenen")
        form_layout.addRow("Etiketler:", self.tags_input)
        layout.addLayout(form_layout)

        # ROZETLER BÖLÜMÜ
        lbl_badges = QLabel("<b>🏅 Öğrenci Rozetleri (Açmak/Kapatmak için Tıklayın):</b>")
        layout.addWidget(lbl_badges)

        self.badge_frame = QFrame()
        frame_bg = "#242526" if is_dark else "#EBECF0"
        self.badge_frame.setStyleSheet(f"QFrame {{ background-color: {frame_bg}; border-radius: 6px; padding: 4px; }}")
        self.badge_layout = QHBoxLayout(self.badge_frame)
        self.badge_layout.setSpacing(4)
        layout.addWidget(self.badge_frame)

        # GİZLİ ÖĞRETMEN NOTLARI
        notes_header = QHBoxLayout()
        notes_header.addWidget(QLabel("<b>Öğretmen Özel Notları:</b>"))
        notes_header.addStretch()
        self.btn_privacy = QPushButton("👁️ Notları Göster")
        self.btn_privacy.setStyleSheet(
            "background-color: #F59E0B; color: white; padding: 3px 8px; font-weight: bold; border-radius: 4px; font-size: 12px;")
        self.btn_privacy.clicked.connect(self.toggle_privacy)
        notes_header.addWidget(self.btn_privacy)
        layout.addLayout(notes_header)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setVisible(False)

        self.hidden_placeholder = QLabel("🔒 Özel notlar sınıf güvenliği için gizlenmiştir.")
        placeholder_bg = "#3A3B3C" if is_dark else "#EBECF0"
        placeholder_fg = "#9CA3AF" if is_dark else "#5E6C84"
        self.hidden_placeholder.setStyleSheet(
            f"background-color: {placeholder_bg}; padding: 6px; border-radius: 4px; color: {placeholder_fg}; font-style: italic;")
        self.hidden_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.notes_input)
        layout.addWidget(self.hidden_placeholder)

        # LOG GEÇMİŞİ
        layout.addWidget(QLabel("<b>Ders İçi İşlem Geçmişi:</b>"))
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(3)
        self.logs_table.setHorizontalHeaderLabels(["Tür", "Kategori", "Açıklama / Tarih"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.logs_table.verticalHeader().setVisible(False)
        self.logs_table.setMaximumHeight(90)
        layout.addWidget(self.logs_table)

        # BUTONLAR
        btn_layout = QHBoxLayout()
        btn_pdf = QPushButton("📄 PDF Rapor İndir")
        btn_pdf.setStyleSheet(
            "background-color: #2563EB; color: white; padding: 7px 12px; font-weight: bold; border-radius: 4px;")
        btn_pdf.clicked.connect(self.export_pdf)

        btn_cancel = QPushButton("İptal")
        btn_save = QPushButton("Profili Kaydet")

        btn_cancel.setStyleSheet("padding: 7px 12px; font-weight: bold; border-radius: 4px;")
        btn_save.setStyleSheet(
            "background-color: #10B981; color: white; padding: 7px 12px; font-weight: bold; border-radius: 4px;")

        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.save_data)

        btn_layout.addWidget(btn_pdf)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

        # Konfeti Katmanı
        self.confetti = ConfettiWidget(self)

    def create_slider(self):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(5)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        return slider

    def load_badges(self):
        for i in reversed(range(self.badge_layout.count())):
            w = self.badge_layout.itemAt(i).widget()
            if w: w.setParent(None)

        current_badges = [b['key'] for b in BadgeService.get_student_badges(self.student_id)]
        is_dark = (ThemeManager.get_current_theme() == "dark")

        for b_key, b_info in BADGES.items():
            btn = QPushButton(f"{b_info['icon']} {b_info['title']}")
            btn.setToolTip(b_info['desc'])

            is_active = (b_key in current_badges)
            if is_active:
                btn.setStyleSheet(
                    "QPushButton { background-color: #2563EB; color: white; font-weight: bold; padding: 5px 8px; border-radius: 10px; border: none; font-size: 11px; }")
            else:
                bg = "#3A3B3C" if is_dark else "#DFE1E6"
                fg = "#9CA3AF" if is_dark else "#5E6C84"
                btn.setStyleSheet(
                    f"QPushButton {{ background-color: {bg}; color: {fg}; font-weight: bold; padding: 5px 8px; border-radius: 10px; border: none; font-size: 11px; }}")

            btn.clicked.connect(lambda checked, k=b_key: self.toggle_badge(k))
            self.badge_layout.addWidget(btn)

    def toggle_badge(self, badge_key):
        is_added = BadgeService.toggle_student_badge(self.student_id, badge_key)
        if is_added:
            self.confetti.start_confetti(2000)
        self.load_badges()

    def toggle_privacy(self):
        self.notes_hidden = not self.notes_hidden
        self.notes_input.setVisible(not self.notes_hidden)
        self.hidden_placeholder.setVisible(self.notes_hidden)
        self.btn_privacy.setText("👁️ Notları Göster" if self.notes_hidden else "🙈 Notları Gizle")

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
            QMessageBox.critical(self, "Hata", f"Profil kaydedilemedi:\n{e}")