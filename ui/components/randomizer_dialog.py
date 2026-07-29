import math
import random
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QMessageBox)
from PyQt6.QtCore import Qt, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush, QTransform
from database.db_manager import db
from services.language_service import LanguageService
from services.audio_service import audio


def format_short_name(first_name, last_name, max_len=14):
    """Uzun isimleri çark dilimine sığacak şekilde akıllıca kısaltır."""
    first_name = str(first_name).strip()
    last_name = str(last_name).strip() if last_name else ""

    full = f"{first_name} {last_name[0]}." if last_name else first_name

    if len(full) <= max_len:
        return full

    parts = first_name.split()
    if len(parts) > 1:
        short_first = f"{parts[0][0]}. {' '.join(parts[1:])}"
        full = f"{short_first} {last_name[0]}." if last_name else short_first

    if len(full) > max_len:
        full = full[:max_len - 2] + ".."

    return full


class WheelLabel(QLabel):
    """Tam Şeffaf Zeminli HD Çark Bileşeni."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0.0
        self.students = []
        self.base_pixmap = None
        self.setFixedSize(360, 360)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Beyaz arka kutucuğu engellemek için tam şeffaf yapıyoruz
        self.setStyleSheet("background: transparent;")

    def get_angle(self):
        return self._angle

    def set_angle(self, angle):
        old_angle = self._angle
        self._angle = angle % 360
        self.update_transform()

        if self.students and len(self.students) > 0:
            angle_per_segment = 360.0 / len(self.students)
            if int(old_angle / angle_per_segment) != int(self._angle / angle_per_segment):
                audio.play_beep(950, 12)

    angle = pyqtProperty(float, get_angle, set_angle)

    def set_students(self, students):
        self.students = students
        self.render_wheel_pixmap_hd()
        self.update_transform()

    def render_wheel_pixmap_hd(self):
        if not self.students or len(self.students) == 0:
            return

        canvas_size = 720
        pixmap = QPixmap(canvas_size, canvas_size)
        # KRİTİK: Tuvali tam şeffaf renkle dolduruyoruz
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        center = canvas_size / 2.0
        outer_ring_radius = 340
        wheel_radius = 320

        # Dış Şık Altın/Krom Çerçeve
        painter.setBrush(QBrush(QColor("#2C3E50")))
        painter.setPen(QPen(QColor("#F39C12"), 8))
        painter.drawEllipse(int(center - outer_ring_radius), int(center - outer_ring_radius),
                           outer_ring_radius * 2, outer_ring_radius * 2)

        num_segments = len(self.students)
        angle_per_segment = 360.0 / num_segments

        colors = [
            QColor("#2563EB"), QColor("#D97706"), QColor("#059669"),
            QColor("#DC2626"), QColor("#7C3AED"), QColor("#0891B2"),
            QColor("#EA580C"), QColor("#4F46E5")
        ]

        rect_x = center - wheel_radius
        rect_y = center - wheel_radius
        wheel_diameter = wheel_radius * 2

        # Dilimler ve Metinler
        for i, student in enumerate(self.students):
            start_angle = i * angle_per_segment
            color = colors[i % len(colors)]

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#1E293B"), 3))
            painter.drawPie(int(rect_x), int(rect_y), int(wheel_diameter), int(wheel_diameter),
                            int(start_angle * 16), int(angle_per_segment * 16))

            # Akıllı Metin
            painter.save()
            mid_angle_rad = math.radians(start_angle + (angle_per_segment / 2.0))

            tx = center + (wheel_radius * 0.58) * math.cos(mid_angle_rad)
            ty = center - (wheel_radius * 0.58) * math.sin(mid_angle_rad)

            painter.translate(tx, ty)
            painter.rotate(-start_angle - (angle_per_segment / 2.0))

            font_size = 17 if num_segments <= 15 else (14 if num_segments <= 25 else 11)
            font = QFont("Segoe UI", font_size, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QColor("#FFFFFF"))

            fn = student['first_name'] if 'first_name' in student.keys() else ""
            ln = student['last_name'] if 'last_name' in student.keys() else ""
            display_name = format_short_name(fn, ln, max_len=14 if num_segments <= 15 else 10)

            painter.drawText(-100, -20, 200, 40, Qt.AlignmentFlag.AlignCenter, display_name)
            painter.restore()

        # Göbek Dairesi
        painter.setBrush(QBrush(QColor("#0F172A")))
        painter.setPen(QPen(QColor("#F39C12"), 5))
        painter.drawEllipse(int(center - 45), int(center - 45), 90, 90)

        # Göbek İçi Motif
        painter.setBrush(QBrush(QColor("#F39C12")))
        painter.drawEllipse(int(center - 12), int(center - 12), 24, 24)

        painter.end()
        self.base_pixmap = pixmap

    def update_transform(self):
        if not self.base_pixmap:
            return

        transform = QTransform()
        transform.translate(360, 360)
        transform.rotate(-self._angle)
        transform.translate(-360, -360)

        rotated = self.base_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        crop_x = (rotated.width() - 720) // 2
        crop_y = (rotated.height() - 720) // 2
        final_hd = rotated.copy(crop_x, crop_y, 720, 720)

        self.setPixmap(final_hd.scaled(360, 360, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))


class RandomizerDialog(QDialog):
    def __init__(self, class_id, parent=None):
        super().__init__(parent)
        self.class_id = class_id
        self.parent_view = parent
        self.selected_student_id = None
        self.selected_student_name = ""
        self.students = []

        title_text = "🎡 " + ("Çarkıfelek" if LanguageService.current_lang == "tr" else "Wheel of Fortune")
        self.setWindowTitle(title_text)
        self.setFixedSize(440, 580)
        self.setStyleSheet("QDialog { background-color: #0F172A; }")
        self.setup_ui()
        self.load_eligible_students()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # 1. KAZANAN KARTI (Açılmadığı sürece görünmez/şeffaf)
        self.lbl_result = QLabel("")
        self.lbl_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_result.setStyleSheet("""
            QLabel {
                font-size: 20px; font-weight: bold; color: #F8FAFC;
                padding: 10px; border-radius: 10px;
                background-color: rgba(30, 41, 59, 0.9);
                border: 2px solid #3B82F6;
            }
        """)
        self.lbl_result.setVisible(False)
        layout.addWidget(self.lbl_result)

        # 2. İBRE (Şeffaf zeminli)
        self.lbl_pointer = QLabel("▼")
        self.lbl_pointer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_pointer.setStyleSheet("""
            font-size: 36px; color: #F39C12; font-weight: bold;
            background: transparent;
            margin-bottom: -16px; margin-top: -5px;
        """)
        layout.addWidget(self.lbl_pointer)

        # 3. ŞEFFAF ÇARK
        self.wheel = WheelLabel(self)
        layout.addWidget(self.wheel, alignment=Qt.AlignmentFlag.AlignCenter)

        # 4. ÇEVİR BUTONU
        btn_text = "🎡 " + ("Çarkı Çevir!" if LanguageService.current_lang == "tr" else "Spin the Wheel!")
        self.btn_spin = QPushButton(btn_text)
        self.btn_spin.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F59E0B, stop:1 #D97706);
                color: #FFFFFF; padding: 12px; font-size: 16px; font-weight: bold;
                border-radius: 8px; border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FBBF24, stop:1 #F59E0B);
            }
            QPushButton:disabled { background-color: #475569; color: #94A3B8; }
        """)
        self.btn_spin.clicked.connect(self.start_spin)
        layout.addWidget(self.btn_spin)

        # 5. PUANLAMA BUTONLARI
        self.score_container = QHBoxLayout()
        self.score_container.setSpacing(8)

        self.btn_correct = QPushButton(LanguageService.get("correct"))
        self.btn_correct.setStyleSheet("""
            QPushButton { background-color: #10B981; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #059669; }
        """)
        self.btn_correct.clicked.connect(lambda: self.quick_score("Doğru", "Başarılı Katılım"))

        self.btn_wrong = QPushButton(LanguageService.get("wrong"))
        self.btn_wrong.setStyleSheet("""
            QPushButton { background-color: #EF4444; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #DC2626; }
        """)
        self.btn_wrong.clicked.connect(lambda: self.quick_score("Yanlış", "Hatalı Cevap"))

        self.btn_pass = QPushButton(LanguageService.get("pass"))
        self.btn_pass.setStyleSheet("""
            QPushButton { background-color: #8B5CF6; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #7C3AED; }
        """)
        self.btn_pass.clicked.connect(lambda: self.quick_score("Pas", "Cevap Vermedi / Pas Geçti"))

        self.score_container.addWidget(self.btn_correct)
        self.score_container.addWidget(self.btn_wrong)
        self.score_container.addWidget(self.btn_pass)

        layout.addLayout(self.score_container)
        self.toggle_score_buttons(False)

    def toggle_score_buttons(self, visible):
        self.btn_correct.setVisible(visible)
        self.btn_wrong.setVisible(visible)
        self.btn_pass.setVisible(visible)

    def load_eligible_students(self):
        try:
            self.students = db.get_eligible_students(self.class_id)
            if self.students and len(self.students) > 0:
                self.wheel.set_students(self.students)
            else:
                self.lbl_result.setText("⚠️ " + ("Bu sınıfta öğrenci bulunamadı." if LanguageService.current_lang == "tr" else "No students found."))
                self.lbl_result.setVisible(True)
                self.btn_spin.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load roster: {e}")

    def start_spin(self):
        if not self.students or len(self.students) == 0:
            return

        self.btn_spin.setEnabled(False)
        self.toggle_score_buttons(False)
        self.lbl_result.setVisible(False)

        self.winning_index = random.randint(0, len(self.students) - 1)

        num_students = len(self.students)
        angle_per_segment = 360.0 / num_students

        target_segment_angle = (self.winning_index * angle_per_segment) + (angle_per_segment / 2.0)
        target_angle = (90 - target_segment_angle) % 360

        total_rotation = (360 * 5) + target_angle

        self.anim = QPropertyAnimation(self.wheel, b"angle")
        self.anim.setDuration(4200)
        self.anim.setStartValue(self.wheel.angle)
        self.anim.setEndValue(self.wheel.angle + total_rotation)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.finished.connect(self.finalize_spin)

        self.anim.start()

    def finalize_spin(self):
        winner = self.students[self.winning_index]
        db.increment_selection_count(winner['id'])

        self.selected_student_id = winner['id']
        first_n = winner['first_name'] if 'first_name' in winner.keys() else ""
        last_n = winner['last_name'] if 'last_name' in winner.keys() else ""
        self.selected_student_name = f"{first_n} {last_n}".strip()

        self.lbl_result.setText(f"🎉  {self.selected_student_name}")
        self.lbl_result.setVisible(True)

        audio.play_beep(1200, 180)
        self.btn_spin.setEnabled(True)
        self.toggle_score_buttons(True)

        if self.parent_view and hasattr(self.parent_view, 'select_student_by_id'):
            self.parent_view.select_student_by_id(self.selected_student_id)

    def quick_score(self, status, message):
        if not self.selected_student_id:
            return

        try:
            db.add_log_entry(
                student_id=self.selected_student_id,
                log_type="Quick Score",
                category_tag="Derse Katılım",
                comment=f"Çarkıfelek: {status} ({message})"
            )
            QMessageBox.information(self, "Success", f"{self.selected_student_name} -> '{status}'")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save error: {str(e)}")