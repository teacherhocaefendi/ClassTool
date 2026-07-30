import random
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen


class Particle:
    def __init__(self, width, height):
        self.x = random.uniform(0, width)
        self.y = random.uniform(-100, -10)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(3, 8)
        self.size = random.uniform(6, 12)
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-5, 5)

        colors = [
            "#FF5630", "#FF991F", "#36B37E", "#0052CC",
            "#6554C0", "#00B8D9", "#FFAB00", "#FF5252"
        ]
        self.color = QColor(random.choice(colors))

    def update(self):
        self.x += self.vx + math.sin(self.y / 10) * 0.5
        self.y += self.vy
        self.angle += self.spin


class ConfettiWidget(QWidget):
    """Ekran üzerinde şeffaf bir katman olarak beliren ve konfeti patlatan bileşen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setStyleSheet("background: transparent;")

        self.particles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.active_ticks = 0

    def start_confetti(self, duration_ms=2500):
        if self.parent():
            self.resize(self.parent().size())
            self.raise_()

        self.particles = [Particle(self.width(), self.height()) for _ in range(120)]
        self.active_ticks = duration_ms // 30
        self.show()
        self.timer.start(30)

    def update_particles(self):
        self.active_ticks -= 1
        for p in self.particles:
            p.update()

        self.update()

        if self.active_ticks <= 0 and all(p.y > self.height() for p in self.particles):
            self.timer.stop()
            self.hide()

    def paintEvent(self, event):
        if not self.particles:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for p in self.particles:
            if 0 <= p.y <= self.height():
                painter.save()
                painter.translate(p.x, p.y)
                painter.rotate(p.angle)

                painter.setBrush(QBrush(p.color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(QRectF(-p.size / 2, -p.size / 2, p.size, p.size / 1.5))

                painter.restore()

        painter.end()