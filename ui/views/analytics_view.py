from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QFrame)
from PyQt6.QtCore import Qt
from services.report_service import ReportService
from services.language_service import LanguageService


class AnalyticsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        toolbar_layout = QHBoxLayout()
        self.btn_refresh = QPushButton(LanguageService.get("refresh_data"))
        self.btn_refresh.setStyleSheet("""
            QPushButton { 
                background-color: #0052CC; color: white; padding: 10px 20px;
                font-size: 15px; font-weight: bold; border-radius: 5px; 
            }
            QPushButton:hover { background-color: #003e99; }
        """)
        self.btn_refresh.clicked.connect(self.load_data)
        toolbar_layout.addWidget(self.btn_refresh)
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # ÖZET KARTLARI
        cards_layout = QHBoxLayout()
        self.card_hw_total = self.create_summary_card(LanguageService.get("analytics_title_hw_done"), "0", "hw_done")
        self.card_hw_missing = self.create_summary_card(LanguageService.get("analytics_title_hw_miss"), "0", "hw_miss")
        self.card_count = self.create_summary_card(LanguageService.get("analytics_title_total"), "0", "total")

        cards_layout.addWidget(self.card_hw_total)
        cards_layout.addWidget(self.card_hw_missing)
        cards_layout.addWidget(self.card_count)
        layout.addLayout(cards_layout)

        # TABLO
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            LanguageService.get("no"),
            LanguageService.get("first_name"),
            LanguageService.get("analytics_title_hw_done"),
            LanguageService.get("analytics_title_hw_miss"),
            LanguageService.get("net_part"),
            LanguageService.get("net_beh")
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)

        layout.addWidget(self.table)

    def create_summary_card(self, title, default_val, obj_name):
        frame = QFrame()
        frame.setStyleSheet("QFrame { border: 2px solid #3A3B3C; border-radius: 8px; padding: 10px; }")
        l = QVBoxLayout(frame)

        lbl_title = QLabel(title)
        lbl_title.setObjectName(f"title_{obj_name}")
        lbl_title.setStyleSheet("font-size: 13px; font-weight: bold;")

        lbl_val = QLabel(default_val)
        lbl_val.setStyleSheet("font-size: 24px; font-weight: bold; color: #0052CC;")
        lbl_val.setObjectName("value_label")

        l.addWidget(lbl_title)
        l.addWidget(lbl_val)
        return frame

    def load_data(self):
        self.table.setSortingEnabled(False)
        analytics_data = ReportService.calculate_analytics()
        self.table.setRowCount(len(analytics_data))

        total_done = 0
        total_missing = 0

        for row_idx, data in enumerate(analytics_data):
            self.table.setItem(row_idx, 0, self.create_item(data['student_number']))
            self.table.setItem(row_idx, 1, self.create_item(data['name']))

            done_cnt = data['homework_done']
            missing_cnt = data['homework_missing']
            total_done += done_cnt
            total_missing += missing_cnt

            item_done = self.create_numeric_item(done_cnt)
            item_done.setForeground(Qt.GlobalColor.darkGreen) if done_cnt > 0 else None

            item_missing = self.create_numeric_item(missing_cnt)
            item_missing.setForeground(Qt.GlobalColor.darkRed) if missing_cnt > 0 else None

            self.table.setItem(row_idx, 2, item_done)
            self.table.setItem(row_idx, 3, item_missing)
            self.table.setItem(row_idx, 4, self.create_numeric_item(data['participation_net']))
            self.table.setItem(row_idx, 5, self.create_numeric_item(data['behavior_net']))

        count = len(analytics_data)
        self.card_hw_total.findChild(QLabel, "value_label").setText(str(total_done))
        self.card_hw_missing.findChild(QLabel, "value_label").setText(str(total_missing))
        self.card_count.findChild(QLabel, "value_label").setText(str(count))

        self.table.setSortingEnabled(True)

    def create_item(self, text):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def create_numeric_item(self, value):
        item = QTableWidgetItem()
        item.setData(Qt.ItemDataRole.DisplayRole, int(value))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def retranslate_ui(self):
        self.btn_refresh.setText(LanguageService.get("refresh_data"))
        self.card_hw_total.findChild(QLabel, "title_hw_done").setText(LanguageService.get("analytics_title_hw_done"))
        self.card_hw_missing.findChild(QLabel, "title_hw_miss").setText(LanguageService.get("analytics_title_hw_miss"))
        self.card_count.findChild(QLabel, "title_total").setText(LanguageService.get("analytics_title_total"))

        self.table.setHorizontalHeaderLabels([
            LanguageService.get("no"),
            LanguageService.get("first_name"),
            LanguageService.get("analytics_title_hw_done"),
            LanguageService.get("analytics_title_hw_miss"),
            LanguageService.get("net_part"),
            LanguageService.get("net_beh")
        ])