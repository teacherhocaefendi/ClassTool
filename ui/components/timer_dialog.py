from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTabWidget, QWidget
from PyQt6.QtCore import QTimer, Qt, QTime
from services.language_service import LanguageService


class TimerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(LanguageService.get("timer_title"))
        self.resize(640, 420)
        self.setMinimumSize(500, 350)

        # Kronometre ve Geri Sayım Değişkenleri
        self.stopwatch_time = QTime(0, 0, 0, 0)
        self.stopwatch_timer = QTimer(self)
        self.stopwatch_timer.timeout.connect(self.update_stopwatch)

        self.countdown_time = QTime(0, 5, 0)
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #3A3B3C; border-radius: 6px; background-color: #18191A; }
            QTabBar::tab { background: #242526; color: #E4E6EB; padding: 10px 20px; font-weight: bold; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #0052CC; color: #FFFFFF; }
        """)

        # Sekme 1: Geri Sayım
        self.tab_countdown = QWidget()
        self.setup_countdown_ui()
        self.tabs.addTab(self.tab_countdown, LanguageService.get("countdown"))

        # Sekme 2: Kronometre
        self.tab_stopwatch = QWidget()
        self.setup_stopwatch_ui()
        self.tabs.addTab(self.tab_stopwatch, LanguageService.get("stopwatch"))

        main_layout.addWidget(self.tabs)

    def setup_countdown_ui(self):
        layout = QVBoxLayout(self.tab_countdown)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        self.lbl_countdown = QLabel("05:00")
        # Dijital Saat Görünümü (Parlak Turkuaz/Yeşil)
        self.lbl_countdown.setStyleSheet("font-size: 72px; font-weight: bold; color: #36B37E; font-family: monospace;")
        self.lbl_countdown.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_countdown)

        # Süre ekleme butonları
        btn_layout = QHBoxLayout()
        for mins in [1, 5, 10, 40]:
            b = QPushButton(f"+{mins} Dk")
            b.setStyleSheet("background-color: #242526; color: #E4E6EB; border: 1px solid #3A3B3C; padding: 8px 12px; font-weight: bold; border-radius: 6px;")
            b.clicked.connect(lambda _, m=mins: self.add_countdown_time(m))
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        # Kontrol Butonları
        ctrl_layout = QHBoxLayout()
        self.btn_cd_start = QPushButton(LanguageService.get("start"))
        self.btn_cd_pause = QPushButton(LanguageService.get("pause"))
        self.btn_cd_reset = QPushButton(LanguageService.get("reset"))

        self.btn_cd_start.setStyleSheet("background-color: #36B37E; color: white; padding: 10px 20px; font-weight: bold; border-radius: 6px;")
        self.btn_cd_pause.setStyleSheet("background-color: #FF991F; color: white; padding: 10px 20px; font-weight: bold; border-radius: 6px;")
        self.btn_cd_reset.setStyleSheet("background-color: #FF5630; color: white; padding: 10px 20px; font-weight: bold; border-radius: 6px;")

        self.btn_cd_start.clicked.connect(self.start_countdown)
        self.btn_cd_pause.clicked.connect(self.pause_countdown)
        self.btn_cd_reset.clicked.connect(self.reset_countdown)

        ctrl_layout.addWidget(self.btn_cd_start)
        ctrl_layout.addWidget(self.btn_cd_pause)
        ctrl_layout.addWidget(self.btn_cd_reset)
        layout.addLayout(ctrl_layout)

    def setup_stopwatch_ui(self):
        layout = QVBoxLayout(self.tab_stopwatch)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)

        self.lbl_stopwatch = QLabel("00:00.00")
        # Parlak Dijital Kronometre Rengi
        self.lbl_stopwatch.setStyleSheet("font-size: 72px; font-weight: bold; color: #4FC3F7; font-family: monospace;")
        self.lbl_stopwatch.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_stopwatch)

        ctrl_layout = QHBoxLayout()
        self.btn_sw_start = QPushButton(LanguageService.get("start"))
        self.btn_sw_pause = QPushButton(LanguageService.get("pause"))
        self.btn_sw_reset = QPushButton(LanguageService.get("reset"))

        self.btn_sw_start.setStyleSheet("background-color: #36B37E; color: white; padding: 10px 25px; font-weight: bold; border-radius: 6px;")
        self.btn_sw_pause.setStyleSheet("background-color: #FF991F; color: white; padding: 10px 25px; font-weight: bold; border-radius: 6px;")
        self.btn_sw_reset.setStyleSheet("background-color: #FF5630; color: white; padding: 10px 25px; font-weight: bold; border-radius: 6px;")

        self.btn_sw_start.clicked.connect(self.start_stopwatch)
        self.btn_sw_pause.clicked.connect(self.pause_stopwatch)
        self.btn_sw_reset.clicked.connect(self.reset_stopwatch)

        ctrl_layout.addWidget(self.btn_sw_start)
        ctrl_layout.addWidget(self.btn_sw_pause)
        ctrl_layout.addWidget(self.btn_sw_reset)
        layout.addLayout(ctrl_layout)

    # Kronometre Fonksiyonları
    def start_stopwatch(self):
        self.stopwatch_timer.start(10)

    def pause_stopwatch(self):
        self.stopwatch_timer.stop()

    def reset_stopwatch(self):
        self.stopwatch_timer.stop()
        self.stopwatch_time = QTime(0, 0, 0, 0)
        self.lbl_stopwatch.setText("00:00.00")

    def update_stopwatch(self):
        self.stopwatch_time = self.stopwatch_time.addMSecs(10)
        self.lbl_stopwatch.setText(self.stopwatch_time.toString("mm:ss.z")[:-1])

    # Geri Sayım Fonksiyonları
    def start_countdown(self):
        if self.countdown_time.isValid() and (self.countdown_time.minute() > 0 or self.countdown_time.second() > 0):
            self.countdown_timer.start(1000)

    def pause_countdown(self):
        self.countdown_timer.stop()

    def reset_countdown(self):
        self.countdown_timer.stop()
        self.countdown_time = QTime(0, 5, 0)
        self.lbl_countdown.setText("05:00")

    def add_countdown_time(self, mins):
        self.countdown_time = self.countdown_time.addSecs(mins * 60)
        self.lbl_countdown.setText(self.countdown_time.toString("mm:ss"))

    def update_countdown(self):
        if self.countdown_time.minute() == 0 and self.countdown_time.second() == 0:
            self.countdown_timer.stop()
            return
        self.countdown_time = self.countdown_time.addSecs(-1)
        self.lbl_countdown.setText(self.countdown_time.toString("mm:ss"))