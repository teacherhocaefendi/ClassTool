import math
import random
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtProperty, QPropertyAnimation, QEasingCurve, QTimer, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush, QTransform, QPainterPath
from database.db_manager import db
from services.language_service import LanguageService
from services.badge_service import BadgeService
from services.audio_service import audio
from ui.components.confetti_widget import ConfettiWidget


def format_short_name(first_name, last_name, max_len=12):
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


class WoodWheelLabel(QLabel):
    """İnce Çerçeveli, Tam Transparan Dönen Çark Bileşeni."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0.0
        self.students = []
        self.wheel_pixmap = None
        self.setFixedSize(380, 380)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: transparent;")

    def get_angle(self):
        return self._angle

    def set_angle(self, angle):
        old_angle = self._angle
        self._angle = angle % 360
        self.update_display()

        if self.students and len(self.students) > 0:
            angle_per_segment = 360.0 / len(self.students)
            if int(old_angle / angle_per_segment) != int(self._angle / angle_per_segment):
                audio.play_beep(950, 12)

    angle = pyqtProperty(float, get_angle, set_angle)

    def set_students(self, students):
        self.students = students
        self.render_wheel_only_hd()
        self.update_display()

    def render_wheel_only_hd(self):
        if not self.students or len(self.students) == 0:
            return

        size = 380
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        center = size / 2.0
        wheel_radius = 175.0
        num_segments = len(self.students)
        angle_per_segment = 360.0 / num_segments

        pastel_colors = [
            QColor("#2563EB"), QColor("#F43F5E"), QColor("#D97706"),
            QColor("#10B981"), QColor("#8B5CF6"), QColor("#06B6D4")
        ]

        for i, student in enumerate(self.students):
            start_angle = i * angle_per_segment
            mid_angle = start_angle + (angle_per_segment / 2.0)
            color = pastel_colors[i % len(pastel_colors)]

            path = QPainterPath()
            path.moveTo(center, center)
            path.arcTo(
                center - wheel_radius, center - wheel_radius,
                wheel_radius * 2, wheel_radius * 2,
                start_angle, angle_per_segment
            )
            path.closeSubpath()

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#DC2626"), 2))
            painter.drawPath(path)

            painter.save()
            mid_angle_rad = math.radians(mid_angle)

            tx = center + (wheel_radius * 0.58) * math.cos(mid_angle_rad)
            ty = center - (wheel_radius * 0.58) * math.sin(mid_angle_rad)

            painter.translate(tx, ty)
            painter.rotate(-mid_angle)

            font_size = 11 if num_segments <= 12 else (9 if num_segments <= 20 else 8)
            font = QFont("Segoe UI", font_size, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QColor("#FFFFFF"))

            fn = student['first_name'] if 'first_name' in student.keys() else ""
            ln = student['last_name'] if 'last_name' in student.keys() else ""
            display_name = format_short_name(fn, ln, max_len=12 if num_segments <= 12 else 8)

            painter.drawText(-60, -15, 120, 30, Qt.AlignmentFlag.AlignCenter, display_name)
            painter.restore()

        # Dış Çerçeve
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#F59E0B"), 5))
        painter.drawEllipse(int(center - wheel_radius), int(center - wheel_radius), int(wheel_radius * 2),
                            int(wheel_radius * 2))

        # Çark Üzerindeki Minik Pimler
        for i in range(num_segments):
            p_angle = math.radians(i * angle_per_segment)
            px = center + (wheel_radius - 6) * math.cos(p_angle)
            py = center - (wheel_radius - 6) * math.sin(p_angle)
            painter.setBrush(QBrush(QColor("#F8FAFC")))
            painter.setPen(QPen(QColor("#475569"), 1))
            painter.drawEllipse(int(px - 4), int(py - 4), 8, 8)

        # Orta Göbek
        painter.setBrush(QBrush(QColor("#FBBF24")))
        painter.setPen(QPen(QColor("#DC2626"), 2))
        painter.drawEllipse(int(center - 22), int(center - 22), 44, 44)

        painter.setBrush(QBrush(QColor("#1E293B")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(center - 7), int(center - 7), 14, 14)

        painter.end()
        self.wheel_pixmap = pixmap

    def update_display(self):
        if not self.wheel_pixmap:
            return

        size = 380
        combined = QPixmap(size, size)
        combined.fill(Qt.GlobalColor.transparent)

        painter = QPainter(combined)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        center = size / 2.0

        transform = QTransform()
        transform.translate(center, center)
        transform.rotate(-self._angle)
        transform.translate(-center, -center)

        rotated_wheel = self.wheel_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)

        crop_x = (rotated_wheel.width() - size) // 2
        crop_y = (rotated_wheel.height() - size) // 2
        painter.drawPixmap(0, 0, rotated_wheel, crop_x, crop_y, size, size)

        painter.end()
        self.setPixmap(combined)


class RandomizerDialog(QDialog):
    def __init__(self, class_id, parent=None):
        super().__init__(parent)
        self.class_id = class_id
        self.parent_view = parent
        self.selected_student = None
        self.students = []

        title_text = "🎡 " + ("Çarkıfelek" if LanguageService.current_lang == "tr" else "Wheel of Fortune")
        self.setWindowTitle(title_text)
        self.setFixedSize(760, 460)
        self.setStyleSheet("QDialog { background-color: #0F172A; }")
        self.setup_ui()
        self.load_eligible_students()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ================= SOL PANEL (ÇARK) =================
        left_box = QVBoxLayout()
        left_box.setSpacing(5)

        self.lbl_pointer = QLabel("▼")
        self.lbl_pointer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_pointer.setStyleSheet("""
            font-size: 34px; color: #DC2626; font-weight: bold;
            background: transparent; margin-bottom: -16px; z-index: 10;
        """)
        left_box.addWidget(self.lbl_pointer)

        self.wheel = WoodWheelLabel(self)
        left_box.addWidget(self.wheel, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_text = LanguageService.get("spin")
        self.btn_spin = QPushButton(btn_text)
        self.btn_spin.setFixedHeight(42)
        self.btn_spin.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F59E0B, stop:1 #D97706);
                color: #FFFFFF; font-size: 15px; font-weight: bold; border-radius: 8px; border: none;
            }
            QPushButton:hover { background: #FBBF24; color: #1E293B; }
            QPushButton:disabled { background-color: #334155; color: #64748B; }
        """)
        self.btn_spin.clicked.connect(self.start_spin)
        left_box.addWidget(self.btn_spin)

        main_layout.addLayout(left_box, stretch=1)

        # ================= SAĞ PANEL (SADE KART & DEĞERLENDİRME) =================
        self.right_card = QFrame()
        self.right_card.setStyleSheet("""
            QFrame {
                background-color: #1E293B; border-radius: 12px;
                border: 2px solid #334155; padding: 20px;
            }
        """)
        right_layout = QVBoxLayout(self.right_card)
        right_layout.setSpacing(15)

        right_layout.addStretch()

        # Şanslı Öğrenci İsmi
        self.lbl_winner_name = QLabel("🎡 Çarkı Çevirin")
        self.lbl_winner_name.setStyleSheet("font-size: 26px; font-weight: bold; color: #F8FAFC;")
        self.lbl_winner_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.lbl_winner_name)

        # Varsa Rozetler (Rozeti yoksa bu alan gizlenir/yer kaplamaz)
        self.lbl_badges = QLabel("")
        self.lbl_badges.setStyleSheet("font-size: 14px; color: #F59E0B; font-weight: bold;")
        self.lbl_badges.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_badges.setVisible(False)
        right_layout.addWidget(self.lbl_badges)

        right_layout.addStretch()

        # Şık Anlık Toast Bildirimi
        self.lbl_toast = QLabel("")
        self.lbl_toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_toast.setStyleSheet("""
            QLabel {
                background-color: #10B981; color: white; font-weight: bold;
                padding: 8px; border-radius: 6px; font-size: 13px;
            }
        """)
        self.lbl_toast.setVisible(False)
        right_layout.addWidget(self.lbl_toast)

        # Esnek Değerlendirme Başlığı
        lbl_score_title = QLabel(LanguageService.get("evaluation"))
        lbl_score_title.setStyleSheet("color: #94A3B8; font-weight: bold; font-size: 13px;")
        right_layout.addWidget(lbl_score_title)

        # Çift Emojilerden Arındırılmış Tekil Şık Butonlar
        btn_grid = QHBoxLayout()
        btn_grid.setSpacing(10)

        # LanguageService'den dönen yazının içinde emoji varsa temizleyip tek emoji ekliyoruz
        correct_txt = LanguageService.get("correct").replace("✅", "").strip()
        wrong_txt = LanguageService.get("wrong").replace("❌", "").strip()
        pass_txt = LanguageService.get("pass").replace("⏭️", "").strip()

        self.btn_correct = QPushButton(f"✅ {correct_txt}")
        self.btn_correct.setFixedHeight(44)
        self.btn_correct.setStyleSheet("""
            QPushButton { background-color: #10B981; color: white; font-weight: bold; border-radius: 8px; border: none; font-size: 14px; }
            QPushButton:hover { background-color: #059669; }
        """)
        self.btn_correct.clicked.connect(lambda: self.quick_score("Doğru", "Başarılı Katılım"))

        self.btn_wrong = QPushButton(f"❌ {wrong_txt}")
        self.btn_wrong.setFixedHeight(44)
        self.btn_wrong.setStyleSheet("""
            QPushButton { background-color: #EF4444; color: white; font-weight: bold; border-radius: 8px; border: none; font-size: 14px; }
            QPushButton:hover { background-color: #DC2626; }
        """)
        self.btn_wrong.clicked.connect(lambda: self.quick_score("Yanlış", "Hatalı Cevap"))

        self.btn_pass = QPushButton(f"⏭️ {pass_txt}")
        self.btn_pass.setFixedHeight(44)
        self.btn_pass.setStyleSheet("""
            QPushButton { background-color: #8B5CF6; color: white; font-weight: bold; border-radius: 8px; border: none; font-size: 14px; }
            QPushButton:hover { background-color: #7C3AED; }
        """)
        self.btn_pass.clicked.connect(lambda: self.quick_score("Pas", "Cevap Vermedi / Pas Geçti"))

        btn_grid.addWidget(self.btn_correct)
        btn_grid.addWidget(self.btn_wrong)
        btn_grid.addWidget(self.btn_pass)
        right_layout.addLayout(btn_grid)

        main_layout.addWidget(self.right_card, stretch=1)

        self.confetti = ConfettiWidget(self)
        self.toggle_score_buttons(False)

    def toggle_score_buttons(self, enabled):
        self.btn_correct.setEnabled(enabled)
        self.btn_wrong.setEnabled(enabled)
        self.btn_pass.setEnabled(enabled)

    def load_eligible_students(self):
        try:
            self.students = db.get_eligible_students(self.class_id)
            if self.students and len(self.students) > 0:
                self.wheel.set_students(self.students)
            else:
                self.lbl_winner_name.setText("⚠️ Öğrenci Yok")
                self.btn_spin.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Öğrenci listesi alınamadı: {e}")

    def start_spin(self):
        if not self.students or len(self.students) == 0:
            return

        self.btn_spin.setEnabled(False)
        self.toggle_score_buttons(False)
        self.lbl_toast.setVisible(False)
        self.lbl_winner_name.setText("🌀 Çevriliyor...")
        self.lbl_badges.setVisible(False)

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
        self.selected_student = winner

        first_n = winner['first_name'] if 'first_name' in winner.keys() else ""
        last_n = winner['last_name'] if 'last_name' in winner.keys() else ""
        full_name = f"{first_n} {last_n}".strip()

        self.lbl_winner_name.setText(f"🎉 {full_name}")

        badges = BadgeService.get_student_badges(winner['id'])
        if badges:
            badge_str = " ".join([f"{b['icon']} {b['title']}" for b in badges])
            self.lbl_badges.setText(f"Rozetler: {badge_str}")
            self.lbl_badges.setVisible(True)
        else:
            self.lbl_badges.setVisible(False)

        self.confetti.start_confetti(2500)
        audio.play_beep(1200, 180)

        self.btn_spin.setEnabled(True)
        self.toggle_score_buttons(True)

        if self.parent_view and hasattr(self.parent_view, 'select_student_by_id'):
            self.parent_view.select_student_by_id(winner['id'])

    def quick_score(self, status, message):
        if not self.selected_student:
            return

        try:
            db.add_log_entry(
                student_id=self.selected_student['id'],
                log_type="Quick Score",
                category_tag="Derse Katılım",
                comment=f"Çarkıfelek: {status} ({message})"
            )

            self.lbl_toast.setText(f"✅ {self.selected_student['first_name']} -> '{status}' kaydedildi.")
            self.lbl_toast.setVisible(True)

            QTimer.singleShot(1100, self.accept)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt eklenirken hata oluştu: {str(e)}")