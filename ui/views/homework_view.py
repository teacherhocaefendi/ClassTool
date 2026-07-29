from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QCalendarWidget, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QTextCharFormat, QColor, QFont
from database.db_manager import db
from services.theme_and_log_service import ThemeManager
from services.language_service import LanguageService


class ClickableTableWidget(QTableWidget):
    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if not item:
            self.clearSelection()
            self.clearFocus()
        super().mousePressEvent(event)


class HomeworkView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_homework_id = None
        self._highlighted_qdates = []
        self._last_selected_date = None
        self.setup_ui()
        self.load_classes()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        left_panel = QVBoxLayout()
        self.lbl_title = QLabel(LanguageService.get("homework_title"))
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_panel.addWidget(self.lbl_title)

        self.class_selector = QComboBox()
        self.class_selector.currentIndexChanged.connect(self.on_class_changed)
        left_panel.addWidget(self.class_selector)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(self.on_date_changed)
        left_panel.addWidget(self.calendar)

        self.txt_title = QLineEdit()
        self.txt_title.setPlaceholderText("Enter Homework Title (e.g., Unit 4 Workbook Ex. 2)")
        left_panel.addWidget(self.txt_title)

        self.btn_assign = QPushButton(LanguageService.get("assign_homework"))
        self.btn_assign.setStyleSheet(
            "background-color: #0052CC; color: white; padding: 12px; font-size: 14px; font-weight: bold; border-radius: 5px;")
        self.btn_assign.clicked.connect(self.assign_homework)
        left_panel.addWidget(self.btn_assign)

        left_panel.addStretch()
        main_layout.addLayout(left_panel, stretch=1)

        right_panel = QVBoxLayout()
        self.lbl_checklist_header = QLabel(LanguageService.get("select_date_prompt"))
        self.lbl_checklist_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #0052CC;")
        right_panel.addWidget(self.lbl_checklist_header)

        self.table = ClickableTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            LanguageService.get("no"),
            LanguageService.get("first_name"),
            LanguageService.get("done_btn"),
            LanguageService.get("missing_btn")
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        right_panel.addWidget(self.table)

        self.btn_save_checks = QPushButton(LanguageService.get("save_status"))
        self.btn_save_checks.setStyleSheet(
            "background-color: #36B37E; color: white; padding: 12px; font-size: 15px; font-weight: bold; border-radius: 5px;")
        self.btn_save_checks.clicked.connect(self.save_checks)
        right_panel.addWidget(self.btn_save_checks)

        main_layout.addLayout(right_panel, stretch=2)

    def load_classes(self):
        self.class_selector.blockSignals(True)
        self.class_selector.clear()
        classes = db.get_classes()
        for cls in classes:
            self.class_selector.addItem(cls['name'], cls['id'])
        self.class_selector.blockSignals(False)
        self.on_class_changed()

    def on_class_changed(self):
        self.highlight_homework_dates()
        self.on_date_changed()

    def highlight_homework_dates(self):
        default_format = QTextCharFormat()
        for qdate in self._highlighted_qdates:
            self.calendar.setDateTextFormat(qdate, default_format)
        self._highlighted_qdates = []

        class_id = self.class_selector.currentData()
        if not class_id:
            return

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#FF991F"))
        highlight_format.setForeground(QColor("#FFFFFF"))
        highlight_format.setFontWeight(QFont.Weight.Bold)

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT due_date FROM homeworks WHERE class_id = ?", (class_id,))
            rows = cursor.fetchall()

        for row in rows:
            date_str = row['due_date']
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            if qdate.isValid():
                self.calendar.setDateTextFormat(qdate, highlight_format)
                self._highlighted_qdates.append(qdate)
        self.update_selected_date_visual()

    def update_selected_date_visual(self):
        selected_date = self.calendar.selectedDate()
        if self._last_selected_date and self._last_selected_date not in self._highlighted_qdates:
            self.calendar.setDateTextFormat(self._last_selected_date, QTextCharFormat())

        current_theme = ThemeManager.get_current_theme()
        select_format = QTextCharFormat()

        if current_theme == "dark":
            select_format.setBackground(QColor("#3A3B3C"))
            select_format.setForeground(QColor("#E4E6EB"))
        else:
            select_format.setBackground(QColor("#0052CC"))
            select_format.setForeground(QColor("#FFFFFF"))

        select_format.setFontWeight(QFont.Weight.Bold)
        self.calendar.setDateTextFormat(selected_date, select_format)
        self._last_selected_date = selected_date

    def on_date_changed(self):
        self.update_selected_date_visual()
        class_id = self.class_selector.currentData()
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")

        if not class_id:
            return

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title FROM homeworks WHERE class_id = ? AND due_date = ? ORDER BY id DESC LIMIT 1",
                (class_id, selected_date))
            homework = cursor.fetchone()

        if homework:
            self.selected_homework_id = homework['id']
            self.load_students_for_checking(class_id, homework['title'], homework['id'])
        else:
            self.selected_homework_id = None
            self.lbl_checklist_header.setText(f"📋 No homework assigned for {selected_date}")
            self.table.setRowCount(0)

    def assign_homework(self):
        class_id = self.class_selector.currentData()
        title = self.txt_title.text().strip()
        due_date = self.calendar.selectedDate().toString("yyyy-MM-dd")

        if not class_id or not title:
            QMessageBox.warning(self, "Warning", "Please enter a homework title.")
            return

        db.add_homework(class_id, title, due_date)
        QMessageBox.information(self, "Success", f"Homework assigned to {due_date} successfully!")
        self.txt_title.clear()
        self.highlight_homework_dates()
        self.on_date_changed()

    def load_students_for_checking(self, class_id, homework_title, homework_id):
        self.lbl_checklist_header.setText(f"📋 Checking: {homework_title}")
        saved_checks = {}
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT student_id, status FROM homework_checks WHERE homework_id = ?", (homework_id,))
            for row in cursor.fetchall():
                saved_checks[row['student_id']] = row['status']
            cursor.execute("SELECT id, student_number, first_name, last_name FROM students WHERE class_id = ?",
                           (class_id,))
            students = cursor.fetchall()

        self.table.setRowCount(len(students))
        btn_style_done = "QPushButton { background-color: transparent; color: #36B37E; border: 2px solid #36B37E; border-radius: 6px; font-weight: bold; min-width: 90px; max-width: 100px; min-height: 26px; max-height: 26px; } QPushButton:checked { background-color: #36B37E; color: white; }"
        btn_style_missing = "QPushButton { background-color: transparent; color: #FF5630; border: 2px solid #FF5630; border-radius: 6px; font-weight: bold; min-width: 90px; max-width: 100px; min-height: 26px; max-height: 26px; } QPushButton:checked { background-color: #FF5630; color: white; }"

        for row, s in enumerate(students):
            self.table.setRowHeight(row, 44)
            no_item = QTableWidgetItem(str(s['student_number']))
            no_item.setData(Qt.ItemDataRole.UserRole, s['id'])
            no_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item = QTableWidgetItem(f"{s['first_name']} {s['last_name']}")
            self.table.setItem(row, 0, no_item)
            self.table.setItem(row, 1, name_item)

            btn_done = QPushButton(LanguageService.get("done_btn"))
            btn_done.setCheckable(True)
            btn_done.setStyleSheet(btn_style_done)

            btn_missing = QPushButton(LanguageService.get("missing_btn"))
            btn_missing.setCheckable(True)
            btn_missing.setStyleSheet(btn_style_missing)

            def on_done_clicked(checked, bd=btn_done, bm=btn_missing):
                if checked: bm.setChecked(False)

            def on_missing_clicked(checked, bd=btn_done, bm=btn_missing):
                if checked: bd.setChecked(False)

            btn_done.clicked.connect(on_done_clicked)
            btn_missing.clicked.connect(on_missing_clicked)

            status = saved_checks.get(s['id'], None)
            if status == "Done":
                btn_done.setChecked(True)
            elif status == "Missing":
                btn_missing.setChecked(True)

            w_done, w_missing = QWidget(), QWidget()
            l_done, l_missing = QHBoxLayout(w_done), QHBoxLayout(w_missing)
            l_done.setContentsMargins(0, 0, 0, 0);
            l_missing.setContentsMargins(0, 0, 0, 0)
            l_done.setAlignment(Qt.AlignmentFlag.AlignCenter);
            l_missing.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l_done.addWidget(btn_done);
            l_missing.addWidget(btn_missing)
            self.table.setCellWidget(row, 2, w_done);
            self.table.setCellWidget(row, 3, w_missing)

    def save_checks(self):
        if not self.selected_homework_id:
            QMessageBox.warning(self, "Warning", "Please select a valid homework date first.")
            return

        checks_data = []
        for row in range(self.table.rowCount()):
            student_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            w_done = self.table.cellWidget(row, 2)
            w_missing = self.table.cellWidget(row, 3)
            btn_done = w_done.findChild(QPushButton) if w_done else None
            btn_missing = w_missing.findChild(QPushButton) if w_missing else None

            status = "Unchecked"
            if btn_done and btn_done.isChecked():
                status = "Done"
            elif btn_missing and btn_missing.isChecked():
                status = "Missing"
            checks_data.append({'student_id': student_id, 'status': status})

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM homework_checks WHERE homework_id = ?", (self.selected_homework_id,))
            conn.commit()

        db.save_homework_checks(self.selected_homework_id, checks_data)
        QMessageBox.information(self, "Saved", "Homework statuses recorded to database.")

    def retranslate_ui(self):
        self.lbl_title.setText(LanguageService.get("homework_title"))
        self.btn_assign.setText(LanguageService.get("assign_homework"))

        # Eğer bir tarih seçili değilse boş metni çevir, seçiliyse dokunma.
        if not self.selected_homework_id:
            self.lbl_checklist_header.setText(LanguageService.get("select_date_prompt"))

        self.btn_save_checks.setText(LanguageService.get("save_status"))
        self.table.setHorizontalHeaderLabels([
            LanguageService.get("no"),
            LanguageService.get("first_name"),
            LanguageService.get("done_btn"),
            LanguageService.get("missing_btn")
        ])