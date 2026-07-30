from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QPushButton, QStackedWidget, QLabel, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QTimer
from database.db_manager import db
from services.theme_and_log_service import logger, ThemeManager
from services.language_service import LanguageService

from ui.views.student_view import StudentView
from ui.components.timer_dialog import TimerDialog
from ui.components.settings_dialog import SettingsDialog
from ui.views.help_view import HelpView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Class Tool - Smart Board Tracker [Alpha 1.0]")
        self.setMinimumSize(1024, 600)
        self.resize(1280, 720)

        self.seating_view = None
        self.group_view = None
        self.homework_view = None
        self.analytics_view = None
        self.help_view = None

        self.setup_ui()
        self.apply_saved_theme()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. SIDEBAR
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QWidget { background-color: #172B4D; }
            QPushButton {
                background-color: transparent; color: #FFFFFF; text-align: left;
                padding: 14px 18px; font-size: 15px; font-weight: bold;
                border: none; border-bottom: 1px solid #2C3E5D;
            }
            QPushButton:hover { background-color: #0052CC; }
            QPushButton:checked { background-color: #0052CC; border-left: 5px solid #FF991F; }
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        logo_label = QLabel("Class Tool v1.0")
        logo_label.setStyleSheet("color: #FFFFFF; font-size: 22px; font-weight: bold; padding: 18px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        # SEKMELER (DÜZELTİLDİ: KILAVUZ BUTONU DAHİL EDİLDİ)
        self.btn_roster = QPushButton(LanguageService.get("roster"))
        self.btn_seating = QPushButton(LanguageService.get("seating"))
        self.btn_groups = QPushButton(LanguageService.get("groups"))
        self.btn_homework = QPushButton(LanguageService.get("homework"))
        self.btn_analytics = QPushButton(LanguageService.get("analytics"))
        self.btn_help = QPushButton(LanguageService.get("help_guide"))

        self.sidebar_buttons = [
            self.btn_roster, self.btn_seating, self.btn_groups,
            self.btn_homework, self.btn_analytics, self.btn_help
        ]

        for btn in self.sidebar_buttons:
            btn.setCheckable(True)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # DİL DEĞİŞTİRME BUTONU
        self.btn_lang = QPushButton("🌐 Dil: Türkçe" if LanguageService.current_lang == "tr" else "🌐 Lang: English")
        self.btn_lang.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #36B37E; text-align: left;
                padding: 10px 18px; font-size: 13px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #2C3E5D; }
        """)
        self.btn_lang.clicked.connect(self.toggle_language)
        sidebar_layout.addWidget(self.btn_lang)

        self.current_theme = ThemeManager.get_current_theme()
        self.btn_theme = QPushButton(
            LanguageService.get("dark_mode") if self.current_theme == "light" else LanguageService.get("light_mode"))
        self.btn_theme.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #FF991F; text-align: left;
                padding: 10px 18px; font-size: 13px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #2C3E5D; }
        """)
        self.btn_theme.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme)

        self.btn_settings = QPushButton(LanguageService.get("change_pin"))
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #A5ADBA; text-align: left;
                padding: 10px 18px; font-size: 13px; font-weight: bold; border: none;
            }
            QPushButton:hover { color: #FFFFFF; background-color: #0052CC; }
        """)
        self.btn_settings.clicked.connect(self.open_settings)
        sidebar_layout.addWidget(self.btn_settings)

        self.btn_timer = QPushButton(LanguageService.get("timer"))
        self.btn_timer.setStyleSheet("""
            QPushButton {
                background-color: #0052CC; color: #FFFFFF; text-align: center;
                padding: 14px; font-size: 15px; font-weight: bold;
                border: none; border-top: 1px solid #2C3E5D;
            }
            QPushButton:hover { background-color: #003e99; }
        """)
        self.btn_timer.clicked.connect(self.open_timer)
        sidebar_layout.addWidget(self.btn_timer)

        main_layout.addWidget(sidebar)

        # 2. STACKED WIDGET (DÜZELTİLDİ: TEKİL YÜKLEME VE BİNDİRME)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.student_view = StudentView()
        self.stacked_widget.addWidget(self.student_view)

        self.placeholder_1 = QWidget()
        self.placeholder_2 = QWidget()
        self.placeholder_3 = QWidget()
        self.placeholder_4 = QWidget()
        self.placeholder_5 = QWidget()

        self.stacked_widget.addWidget(self.placeholder_1)
        self.stacked_widget.addWidget(self.placeholder_2)
        self.stacked_widget.addWidget(self.placeholder_3)
        self.stacked_widget.addWidget(self.placeholder_4)
        self.stacked_widget.addWidget(self.placeholder_5)

        self.btn_roster.clicked.connect(lambda: self.switch_view(0, self.btn_roster))
        self.btn_seating.clicked.connect(lambda: self.switch_view(1, self.btn_seating))
        self.btn_groups.clicked.connect(lambda: self.switch_view(2, self.btn_groups))
        self.btn_homework.clicked.connect(lambda: self.switch_view(3, self.btn_homework))
        self.btn_analytics.clicked.connect(lambda: self.switch_view(4, self.btn_analytics))
        self.btn_help.clicked.connect(lambda: self.switch_view(5, self.btn_help))

        self.switch_view(0, self.btn_roster)

    def switch_view(self, index, active_button):
        if index == 1 and self.seating_view is None:
            from ui.views.seating_view import SeatingView
            self.seating_view = SeatingView()
            self.stacked_widget.removeWidget(self.placeholder_1)
            self.stacked_widget.insertWidget(1, self.seating_view)

        elif index == 2 and self.group_view is None:
            from ui.views.group_view import GroupView
            self.group_view = GroupView()
            self.stacked_widget.removeWidget(self.placeholder_2)
            self.stacked_widget.insertWidget(2, self.group_view)

        elif index == 3 and self.homework_view is None:
            from ui.views.homework_view import HomeworkView
            self.homework_view = HomeworkView()
            self.stacked_widget.removeWidget(self.placeholder_3)
            self.stacked_widget.insertWidget(3, self.homework_view)

        elif index == 4 and self.analytics_view is None:
            from ui.views.analytics_view import AnalyticsView
            self.analytics_view = AnalyticsView()
            self.stacked_widget.removeWidget(self.placeholder_4)
            self.stacked_widget.insertWidget(4, self.analytics_view)

        elif index == 5:
            if self.help_view is None:
                self.help_view = HelpView()
                self.stacked_widget.removeWidget(self.placeholder_5)
                self.stacked_widget.insertWidget(5, self.help_view)
            else:
                self.help_view.display_help_content(self.help_view.list_topics.currentRow())

        self.stacked_widget.setCurrentIndex(index)

        if index == 1 and self.seating_view:
            self.seating_view.load_data()
        elif index == 3 and self.homework_view:
            self.homework_view.load_classes()
        elif index == 4 and self.analytics_view:
            self.analytics_view.load_data()

        for btn in self.sidebar_buttons:
            btn.setChecked(False)

        active_button.setChecked(True)

    def check_todays_homework_notifications(self):
        try:
            todays_homeworks = db.get_todays_homeworks()
            if todays_homeworks:
                msg = "🔔 BUGÜN TESLİM EDİLECEK ÖDEVLER VAR:\n\n"
                for h in todays_homeworks:
                    msg += f"• Sınıf: {h['class_name']} — {h['title']}\n"
                QMessageBox.information(self, "Ödev Hatırlatıcı", msg)
        except Exception as e:
            logger.error(f"Homework notification error: {e}")

    def apply_saved_theme(self):
        app_inst = QApplication.instance()
        if app_inst:
            ThemeManager.apply_theme(app_inst, self.current_theme)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        ThemeManager.set_theme(self.current_theme)
        app_inst = QApplication.instance()
        if app_inst:
            ThemeManager.apply_theme(app_inst, self.current_theme)
        self.btn_theme.setText(
            LanguageService.get("dark_mode") if self.current_theme == "light" else LanguageService.get("light_mode"))

        # YENİ: Kılavuz ekranı yüklenmişse temasını anında yenile
        if hasattr(self, 'help_view') and self.help_view:
            self.help_view.refresh_theme()

    def toggle_language(self):
        new_lang = "en" if LanguageService.current_lang == "tr" else "tr"
        LanguageService.set_language(new_lang)

        # 1. Sol Menü Metinlerini Güncelle
        self.btn_roster.setText(LanguageService.get("roster"))
        self.btn_seating.setText(LanguageService.get("seating"))
        self.btn_groups.setText(LanguageService.get("groups"))
        self.btn_homework.setText(LanguageService.get("homework"))
        self.btn_analytics.setText(LanguageService.get("analytics"))
        self.btn_help.setText(LanguageService.get("help_guide"))
        self.btn_lang.setText("🌐 Dil: Türkçe" if new_lang == "tr" else "🌐 Lang: English")
        self.btn_theme.setText(
            LanguageService.get("dark_mode") if self.current_theme == "light" else LanguageService.get("light_mode"))
        self.btn_settings.setText(LanguageService.get("change_pin"))
        self.btn_timer.setText(LanguageService.get("timer"))

        # 2. Açık Olan Tüm Sekmelerin Metinlerini Anında Güncelle
        if hasattr(self, 'student_view') and hasattr(self.student_view, 'retranslate_ui'):
            self.student_view.retranslate_ui()

        if self.seating_view and hasattr(self.seating_view, 'retranslate_ui'):
            self.seating_view.retranslate_ui()

        if self.group_view and hasattr(self.group_view, 'retranslate_ui'):
            self.group_view.retranslate_ui()

        if self.homework_view and hasattr(self.homework_view, 'retranslate_ui'):
            self.homework_view.retranslate_ui()

        if self.analytics_view and hasattr(self.analytics_view, 'retranslate_ui'):
            self.analytics_view.retranslate_ui()

        if self.help_view and hasattr(self.help_view, 'retranslate_ui'):
            self.help_view.retranslate_ui()

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def open_timer(self):
        self.timer_window = TimerDialog(self)
        self.timer_window.show()

