from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QSpinBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from database.db_manager import db
from services.language_service import LanguageService
from services.theme_and_log_service import ThemeManager


class OralGradeDialog(QDialog):
    def __init__(self, class_id, class_name, parent=None):
        super().__init__(parent)
        self.class_id = class_id
        self.class_name = class_name

        title_text = f"📊 {class_name} - " + (
            "Sözlü / Performans Notu Hesaplayıcı" if LanguageService.current_lang == "tr" else "Oral Grade Calculator")
        self.setWindowTitle(title_text)
        self.resize(820, 580)

        # Garbage Collector önlemi için self.main_layout kullanıyoruz
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        self.init_ui()
        QTimer.singleShot(100, self.load_config)

    def init_ui(self):
        # Tema moduna göre üst panel rengini dinamik ayarlıyoruz (Dark/Light uyumlu)
        is_dark = (ThemeManager.get_current_theme() == "dark")
        frame_bg = "#1E293B" if is_dark else "#F1F5F9"
        text_color = "#F8FAFC" if is_dark else "#1E293B"
        spin_bg = "#0F172A" if is_dark else "#FFFFFF"
        spin_fg = "white" if is_dark else "#1E293B"
        spin_border = "#334155" if is_dark else "#CBD5E1"

        # ÜST PANEL (AYARLAR)
        config_frame = QFrame()
        config_frame.setStyleSheet(f"QFrame {{ background-color: {frame_bg}; border-radius: 8px; padding: 10px; }}")
        config_layout = QHBoxLayout(config_frame)
        config_layout.setSpacing(8)

        lbl_oral = QLabel("Sözlü:" if LanguageService.current_lang == "tr" else "Grade:")
        lbl_oral.setStyleSheet(f"font-weight: bold; color: {text_color};")

        self.cmb_oral = QComboBox()
        self.cmb_oral.addItems(["1. Sözlü / Performans", "2. Sözlü / Performans", "3. Sözlü / Performans"])
        self.cmb_oral.setMinimumWidth(150)

        spin_style = f"""
            QSpinBox {{ 
                padding: 4px; 
                padding-right: 15px;
                font-weight: bold; 
                border-radius: 4px; 
                background: {spin_bg}; 
                color: {spin_fg}; 
                border: 1px solid {spin_border};
                min-width: 60px; 
            }}
            QSpinBox::up-button {{ width: 14px; }}
            QSpinBox::down-button {{ width: 14px; }}
        """

        self.spin_hw = QSpinBox()
        self.spin_hw.setRange(0, 100)
        self.spin_hw.setStyleSheet(spin_style)

        self.spin_part = QSpinBox()
        self.spin_part.setRange(0, 100)
        self.spin_part.setStyleSheet(spin_style)

        self.spin_beh = QSpinBox()
        self.spin_beh.setRange(0, 100)
        self.spin_beh.setStyleSheet(spin_style)

        btn_calc = QPushButton("⚡ Hesapla" if LanguageService.current_lang == "tr" else "⚡ Calculate")
        btn_calc.setStyleSheet(
            "QPushButton { background-color: #2563EB; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px; }")
        btn_calc.clicked.connect(self.calculate_and_save)

        hw_lbl = QLabel("Ödev %:" if LanguageService.current_lang == "tr" else "HW %:")
        hw_lbl.setStyleSheet(f"font-weight: bold; color: {text_color};")

        part_lbl = QLabel("Katılım %:" if LanguageService.current_lang == "tr" else "Part %:")
        part_lbl.setStyleSheet(f"font-weight: bold; color: {text_color};")

        beh_lbl = QLabel("Davranış %:" if LanguageService.current_lang == "tr" else "Beh %:")
        beh_lbl.setStyleSheet(f"font-weight: bold; color: {text_color};")

        config_layout.addWidget(lbl_oral)
        config_layout.addWidget(self.cmb_oral)
        config_layout.addWidget(hw_lbl)
        config_layout.addWidget(self.spin_hw)
        config_layout.addWidget(part_lbl)
        config_layout.addWidget(self.spin_part)
        config_layout.addWidget(beh_lbl)
        config_layout.addWidget(self.spin_beh)
        config_layout.addWidget(btn_calc)

        self.main_layout.addWidget(config_frame)

        # TABLO KISMI
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "No",
            LanguageService.get("first_name"),
            LanguageService.get("last_name"),
            "Ödev / Katılım Detay",
            "Sözlü Notu"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.main_layout.addWidget(self.table)

        self.cmb_oral.currentIndexChanged.connect(self.load_config)

    def fetch_student_stats(self, student_id):
        stats = {'total_hw': 0, 'done_hw': 0, 'positives': 0, 'negatives': 0}
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT status FROM homework_checks WHERE student_id = ?", (student_id,))
                hw_checks = cursor.fetchall()
                stats['total_hw'] = len(hw_checks)
                stats['done_hw'] = sum(1 for c in hw_checks if c['status'] == 'Done')

                cursor.execute("SELECT log_type FROM logs WHERE student_id = ?", (student_id,))
                logs = cursor.fetchall()
                stats['positives'] = sum(1 for l in logs if l['log_type'] in ['+', 'Quick Score', 'Doğru'])
                stats['negatives'] = sum(1 for l in logs if l['log_type'] in ['-', 'Yanlış'])
        except Exception:
            pass
        return stats

    def load_config(self):
        try:
            oral_idx = self.cmb_oral.currentIndex() + 1
            hw, part, beh = db.get_oral_grade_weights(self.class_id, oral_idx)

            self.spin_hw.setValue(int(hw))
            self.spin_part.setValue(int(part))
            self.spin_beh.setValue(int(beh))

            self.calculate_and_save()
        except Exception:
            pass

    def calculate_and_save(self):
        hw_w = self.spin_hw.value()
        part_w = self.spin_part.value()
        beh_w = self.spin_beh.value()

        if hw_w + part_w + beh_w != 100:
            QMessageBox.warning(self, "Uyarı", f"Ağırlıklar toplamı 100 olmalıdır! (Şu an: {hw_w + part_w + beh_w})")
            return

        try:
            oral_idx = self.cmb_oral.currentIndex() + 1
            db.save_oral_grade_weights(self.class_id, oral_idx, hw_w, part_w, beh_w)

            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, student_number, first_name, last_name FROM students WHERE class_id = ?",
                               (self.class_id,))
                students = cursor.fetchall()

            self.table.setRowCount(len(students))

            is_dark = (ThemeManager.get_current_theme() == "dark")
            grade_color = QColor(
                "#34D399" if is_dark else "#059669")  # Karanlık modda açık yeşil, aydınlık modda koyu yeşil

            for row_idx, student in enumerate(students):
                s_id = student['id']
                s_num = student['student_number']
                fn = student['first_name']
                ln = student['last_name']

                stats = self.fetch_student_stats(s_id)

                total_hw = stats['total_hw']
                done_hw = stats['done_hw']
                hw_score = (done_hw / total_hw * 100.0) if total_hw > 0 else 100.0

                positives = stats['positives']
                negatives = stats['negatives']
                part_score = max(0.0, min(100.0, 70.0 + (positives * 5.0) - (negatives * 10.0)))

                beh_score = 100.0

                final_grade = round(
                    (hw_score * hw_w / 100.0) + (part_score * part_w / 100.0) + (beh_score * beh_w / 100.0))

                self.table.setItem(row_idx, 0, QTableWidgetItem(str(s_num)))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(fn)))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(ln)))
                self.table.setItem(row_idx, 3,
                                   QTableWidgetItem(f"Ödev: {done_hw}/{total_hw} | Katılım: +{positives}/-{negatives}"))

                grade_item = QTableWidgetItem(str(final_grade))
                grade_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                font = QFont("Segoe UI", 11, QFont.Weight.Bold)
                grade_item.setFont(font)
                grade_item.setForeground(grade_color)

                self.table.setItem(row_idx, 4, grade_item)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Hesaplama esnasında hata oluştu: {str(e)}")