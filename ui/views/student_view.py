from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QFileDialog, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
import pandas as pd
from database.db_manager import db
from ui.components.add_student_dialog import AddStudentDialog
from ui.components.edit_student_dialog import EditStudentDialog
from ui.components.randomizer_dialog import RandomizerDialog as RandomPicker
from ui.components.scoring_dialog import ScoringDialog
from ui.components.profile_dialog import ProfileDialog
from ui.components.class_manager_dialog import ClassManagerDialog
from ui.components.class_notes_dialog import ClassNotesDialog
from ui.components.import_dialog import ImportDialog
from services.report_service import ReportService
from services.language_service import LanguageService
from ui.components.oral_grade_dialog import OralGradeDialog

class StudentView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_category_index = None
        self.current_class_id = None
        self.setup_ui()
        self.class_selector.currentIndexChanged.connect(self.on_class_changed)
        self.load_classes()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # 1. ANA KATEGORİ BUTONLARI
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setSpacing(10)

        self.class_selector = QComboBox()
        self.class_selector.setMinimumWidth(140)
        top_bar_layout.addWidget(self.class_selector)

        self.btn_cat_class = QPushButton(LanguageService.get("class_mgmt"))
        self.btn_cat_data = QPushButton(LanguageService.get("data_ops"))
        self.btn_cat_actions = QPushButton(LanguageService.get("lesson_part"))
        self.btn_cat_tools = QPushButton(LanguageService.get("student_tools"))

        cat_btn_style = """
            QPushButton {
                padding: 10px 15px;
                font-size: 14px; font-weight: bold; border-radius: 6px;
            }
            QPushButton:checked { background-color: #0052CC; color: #FFFFFF; border: none; }
        """

        self.category_buttons = [
            self.btn_cat_class, self.btn_cat_data, self.btn_cat_actions, self.btn_cat_tools
        ]

        for idx, btn in enumerate(self.category_buttons):
            btn.setCheckable(True)
            btn.setStyleSheet(cat_btn_style)
            btn.clicked.connect(lambda checked, i=idx: self.toggle_category_panel(i))
            top_bar_layout.addWidget(btn)

        top_bar_layout.addStretch()
        main_layout.addLayout(top_bar_layout)

        # 2. ALT AÇILIR PANEL
        self.sub_panel = QFrame()
        self.sub_panel.setStyleSheet("""
            QFrame { border: 1px solid #DFE1E6; border-radius: 6px; padding: 5px; }
            QPushButton {
                padding: 8px 14px; font-size: 13px; font-weight: bold; border-radius: 4px; border: none;
            }
        """)
        self.sub_panel_layout = QHBoxLayout(self.sub_panel)
        self.sub_panel_layout.setContentsMargins(10, 5, 10, 5)
        self.sub_panel_layout.setSpacing(10)
        self.sub_panel.setVisible(False)

        main_layout.addWidget(self.sub_panel)
        self.setup_sub_panels()

        # 3. VERİ TABLOSU (Çökme Korumalı Standart QTableWidget)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            LanguageService.get("no"),
            LanguageService.get("first_name"),
            LanguageService.get("last_name"),
            LanguageService.get("gender")
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)

        main_layout.addWidget(self.table)

    def setup_sub_panels(self):
        # --- 0: SINIF YÖNETİMİ ---
        self.panel_class_widget = QWidget()
        l0 = QHBoxLayout(self.panel_class_widget)
        l0.setContentsMargins(0, 0, 0, 0)

        self.btn_new_class = QPushButton(LanguageService.get("new_class"))
        self.btn_notes = QPushButton(LanguageService.get("class_notes"))
        self.btn_delete_class = QPushButton(LanguageService.get("delete_class"))

        self.btn_new_class.setStyleSheet("background-color: #0052CC; color: white;")
        self.btn_notes.setStyleSheet("background-color: #FF991F; color: #172B4D;")
        self.btn_delete_class.setStyleSheet("background-color: #FF5630; color: white;")

        self.btn_new_class.clicked.connect(self.open_class_manager)
        self.btn_notes.clicked.connect(self.open_class_notes)
        self.btn_delete_class.clicked.connect(self.delete_current_class)

        l0.addWidget(self.btn_new_class)
        l0.addWidget(self.btn_notes)
        l0.addWidget(self.btn_delete_class)
        l0.addStretch()

        # --- 1: VERİ İŞLEMLERİ ---
        self.panel_data_widget = QWidget()
        l1 = QHBoxLayout(self.panel_data_widget)
        l1.setContentsMargins(0, 0, 0, 0)

        self.btn_add_student = QPushButton(LanguageService.get("add_student"))
        self.btn_import_excel = QPushButton(LanguageService.get("import_excel"))
        self.btn_import_text = QPushButton(LanguageService.get("import_text"))
        self.btn_export = QPushButton(LanguageService.get("export_excel"))

        # YENİ BUTON: Sözlü Notu Hesapla
        self.btn_oral_grade = QPushButton(
            "📊 Sözlü Notu Hesapla" if LanguageService.current_lang == "tr" else "📊 Oral Grade")

        self.btn_add_student.setStyleSheet("background-color: #0052CC; color: white;")
        self.btn_import_excel.setStyleSheet("background-color: #0052CC; color: white;")
        self.btn_import_text.setStyleSheet("background-color: #0052CC; color: white;")
        self.btn_export.setStyleSheet("background-color: #36B37E; color: white;")

        # Yeni butonun stili (Turuncu/Altın)
        self.btn_oral_grade.setStyleSheet("background-color: #F39C12; color: #172B4D;")

        self.btn_add_student.clicked.connect(self.open_add_student_dialog)
        self.btn_import_excel.clicked.connect(self.import_from_excel)
        self.btn_import_text.clicked.connect(self.open_import_dialog)
        self.btn_export.clicked.connect(self.export_class_analytics_to_excel)

        # Yeni butonun bağlantısı
        self.btn_oral_grade.clicked.connect(self.open_oral_grade_dialog)

        l1.addWidget(self.btn_add_student)
        l1.addWidget(self.btn_import_excel)
        l1.addWidget(self.btn_import_text)
        l1.addWidget(self.btn_export)
        l1.addWidget(self.btn_oral_grade)  # Mizanpaja eklendi
        l1.addStretch()

        # --- 2: DERS & KATILIM ---
        self.panel_actions_widget = QWidget()
        l2 = QHBoxLayout(self.panel_actions_widget)
        l2.setContentsMargins(0, 0, 0, 0)

        self.btn_correct = QPushButton(LanguageService.get("correct"))
        self.btn_wrong = QPushButton(LanguageService.get("wrong"))
        self.btn_pass = QPushButton(LanguageService.get("pass"))
        self.btn_random = QPushButton(LanguageService.get("random_pick"))

        self.btn_correct.setStyleSheet("background-color: #36B37E; color: white;")
        self.btn_wrong.setStyleSheet("background-color: #FF5630; color: white;")
        self.btn_pass.setStyleSheet("background-color: #6554C0; color: white;")
        self.btn_random.setStyleSheet("background-color: #FF991F; color: #172B4D;")

        self.btn_correct.clicked.connect(lambda: self.quick_score("Doğru", "Başarılı Katılım"))
        self.btn_wrong.clicked.connect(lambda: self.quick_score("Yanlış", "Hatalı Cevap"))
        self.btn_pass.clicked.connect(lambda: self.quick_score("Pas", "Cevap Vermedi / Pas Geçti"))
        self.btn_random.clicked.connect(self.open_randomizer)

        l2.addWidget(self.btn_correct)
        l2.addWidget(self.btn_wrong)
        l2.addWidget(self.btn_pass)
        l2.addWidget(self.btn_random)
        l2.addStretch()

        # --- 3: ÖĞRENCİ ARAÇLARI ---
        self.panel_tools_widget = QWidget()
        l3 = QHBoxLayout(self.panel_tools_widget)
        l3.setContentsMargins(0, 0, 0, 0)

        self.btn_edit = QPushButton(LanguageService.get("edit_info"))
        self.btn_score = QPushButton(LanguageService.get("detailed_score"))
        self.btn_profile = QPushButton(LanguageService.get("profile_notes"))
        self.btn_delete_student = QPushButton(LanguageService.get("delete_student"))

        self.btn_edit.setStyleSheet("background-color: #FF991F; color: #172B4D;")
        self.btn_score.setStyleSheet("background-color: #0052CC; color: white;")
        self.btn_profile.setStyleSheet("background-color: #172B4D; color: white;")
        self.btn_delete_student.setStyleSheet("background-color: #FF5630; color: white;")

        self.btn_edit.clicked.connect(self.open_edit_student_dialog)
        self.btn_score.clicked.connect(self.open_scoring_dialog)
        self.btn_profile.clicked.connect(self.open_profile_dialog)
        self.btn_delete_student.clicked.connect(self.delete_selected_student)

        l3.addWidget(self.btn_edit)
        l3.addWidget(self.btn_score)
        l3.addWidget(self.btn_profile)
        l3.addWidget(self.btn_delete_student)
        l3.addStretch()

        self.sub_widgets = [
            self.panel_class_widget,
            self.panel_data_widget,
            self.panel_actions_widget,
            self.panel_tools_widget
        ]

    def toggle_category_panel(self, index):
        if self.active_category_index == index:
            self.sub_panel.setVisible(False)
            self.category_buttons[index].setChecked(False)
            self.active_category_index = None
            return

        for b in self.category_buttons:
            b.setChecked(False)

        for i in reversed(range(self.sub_panel_layout.count())):
            w = self.sub_panel_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        selected_widget = self.sub_widgets[index]
        self.sub_panel_layout.addWidget(selected_widget)
        selected_widget.show()

        self.sub_panel.setVisible(True)
        self.category_buttons[index].setChecked(True)
        self.active_category_index = index

    def load_classes(self):
        current_selection = self.class_selector.currentData()
        self.class_selector.blockSignals(True)
        self.class_selector.clear()

        classes = db.get_classes()

        for cls in classes:
            self.class_selector.addItem(cls['name'], cls['id'])

        if current_selection:
            index = self.class_selector.findData(current_selection)
            if index >= 0:
                self.class_selector.setCurrentIndex(index)
        elif self.class_selector.count() > 0:
            self.class_selector.setCurrentIndex(0)

        self.current_class_id = self.class_selector.currentData()
        self.class_selector.blockSignals(False)
        self.on_class_changed(self.class_selector.currentIndex())

    def on_class_changed(self, index=0):
        if self.class_selector.count() > 0:
            self.current_class_id = self.class_selector.currentData()
            self.load_students(self.current_class_id)
        else:
            self.table.setRowCount(0)

    def load_students(self, class_id):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        if not class_id:
            return

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, student_number, first_name, last_name, gender FROM students WHERE class_id = ?",
                           (class_id,))
            students = cursor.fetchall()

        self.table.setRowCount(len(students))
        for row_idx, student in enumerate(students):
            try:
                num_val = int(student['student_number'])
            except ValueError:
                num_val = student['student_number']

            number_item = QTableWidgetItem()
            number_item.setData(Qt.ItemDataRole.DisplayRole, num_val)
            number_item.setData(Qt.ItemDataRole.UserRole, student['id'])

            self.table.setItem(row_idx, 0, number_item)
            self.table.setItem(row_idx, 1, QTableWidgetItem(student['first_name']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(student['last_name']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(student['gender']))

        self.table.setSortingEnabled(True)

    def open_class_notes(self):
        class_id = self.class_selector.currentData()
        class_name = self.class_selector.currentText()
        if not class_id:
            return
        dialog = ClassNotesDialog(class_id, class_name, self)
        dialog.exec()

    def export_class_analytics_to_excel(self):
        class_name = self.class_selector.currentText()
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Save {class_name} Report", f"{class_name}_Report.xlsx", "Excel Files (*.xlsx)",
            options=QFileDialog.Option.DontUseNativeDialog
        )
        if not file_path:
            return

        try:
            ReportService.export_to_styled_excel(class_name, file_path)
            QMessageBox.information(self, "Success", f"Report successfully exported to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"An error occurred during export:\n{str(e)}")

    def open_edit_student_dialog(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Lütfen düzenlemek için bir öğrenci seçin.")
            return

        row = selected_rows[0].row()
        student_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        student_data = {
            'number': self.table.item(row, 0).text(),
            'first_name': self.table.item(row, 1).text(),
            'last_name': self.table.item(row, 2).text(),
            'gender': self.table.item(row, 3).text()
        }

        dialog = EditStudentDialog(student_data, self)
        if dialog.exec():
            updated = dialog.updated_data
            db.update_student(
                student_id=student_id,
                student_number=updated['number'],
                first_name=updated['first_name'],
                last_name=updated['last_name'],
                gender=updated['gender']
            )
            self.on_class_changed(self.class_selector.currentIndex())

    def open_class_manager(self):
        dialog = ClassManagerDialog(self)
        if dialog.exec():
            self.load_classes()

    def delete_current_class(self):
        class_id = self.class_selector.currentData()
        class_name = self.class_selector.currentText()
        if not class_id:
            return

        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"'{class_name}' sınıfını silmek istediğinize emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_class(class_id)
            self.load_classes()

    def delete_selected_student(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Lütfen silmek için bir öğrenci seçin.")
            return

        row = selected_rows[0].row()
        student_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        student_name = f"{self.table.item(row, 1).text()} {self.table.item(row, 2).text()}"

        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"{student_name} adlı öğrenciyi silmek istediğinize emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_student(student_id)
            self.on_class_changed(self.class_selector.currentIndex())

    def open_add_student_dialog(self):
        dialog = AddStudentDialog(self)
        if dialog.exec():
            data = dialog.student_data
            db.add_student(
                class_id=self.current_class_id,
                student_number=data['student_number'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                gender=data['gender']
            )
            self.on_class_changed(self.class_selector.currentIndex())

    def import_from_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Class List (Excel)", "", "Excel Files (*.xlsx *.xls)",
                                                   options=QFileDialog.Option.DontUseNativeDialog)
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip().str.lower()
            expected_columns = ['number', 'first_name', 'last_name', 'gender']
            if not all(col in df.columns for col in expected_columns):
                QMessageBox.warning(self, "Format Error",
                                    "Excel file must contain columns: Number, First_Name, Last_Name, Gender")
                return

            students_data = []
            for index, row in df.iterrows():
                students_data.append({
                    'number': str(row['number']).replace('.0', ''),
                    'first_name': str(row['first_name']).strip().capitalize(),
                    'last_name': str(row['last_name']).strip().capitalize(),
                    'gender': str(row['gender']).strip().capitalize()
                })

            db.add_multiple_students(self.current_class_id, students_data)
            self.on_class_changed(self.class_selector.currentIndex())
            QMessageBox.information(self, "Success", f"Successfully imported {len(students_data)} students.")

        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"An error occurred while reading the file:\n{str(e)}")

    def open_import_dialog(self):
        if not hasattr(self, 'current_class_id') or not self.current_class_id:
            QMessageBox.warning(self, "Error", "Please select or create a class first.")
            return

        dialog = ImportDialog(self.current_class_id, self)
        if dialog.exec():
            self.on_class_changed(self.class_selector.currentIndex())

    def open_randomizer(self):
        class_id = self.class_selector.currentData()
        if not class_id:
            QMessageBox.warning(self, "Warning", "Lütfen önce bir sınıf seçin.")
            return

        dialog = RandomPicker(class_id, parent=None)
        dialog.exec()

    def open_scoring_dialog(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a student from the list first.")
            return
        row = selected_rows[0].row()
        student_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        full_name = f"{self.table.item(row, 1).text()} {self.table.item(row, 2).text()}"
        dialog = ScoringDialog(student_id, full_name, self)
        dialog.exec()

    def open_profile_dialog(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a student from the list first.")
            return
        row = selected_rows[0].row()
        student_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        full_name = f"{self.table.item(row, 1).text()} {self.table.item(row, 2).text()}"
        dialog = ProfileDialog(student_id, full_name, self)
        dialog.exec()

    def quick_score(self, status, message):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen listeden bir öğrenci seçin.")
            return

        row = selected_rows[0].row()
        student_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        student_name = f"{self.table.item(row, 1).text()} {self.table.item(row, 2).text()}"

        try:
            db.add_log_entry(
                student_id=student_id,
                log_type="Quick Score",
                category_tag="Derse Katılım",
                comment=f"Hızlı Puanlama: {status} ({message})"
            )
            QMessageBox.information(self, "Başarılı", f"{student_name} için '{status}' kaydedildi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt eklenirken hata oluştu: {str(e)}")

    def select_student_by_id(self, student_id):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == student_id:
                self.table.selectRow(row)
                self.table.scrollToItem(item)
                break

    def retranslate_ui(self):
        self.btn_cat_class.setText(LanguageService.get("class_mgmt"))
        self.btn_cat_data.setText(LanguageService.get("data_ops"))
        self.btn_cat_actions.setText(LanguageService.get("lesson_part"))
        self.btn_cat_tools.setText(LanguageService.get("student_tools"))

        self.btn_new_class.setText(LanguageService.get("new_class"))
        self.btn_notes.setText(LanguageService.get("class_notes"))
        self.btn_delete_class.setText(LanguageService.get("delete_class"))

        self.btn_add_student.setText(LanguageService.get("add_student"))
        self.btn_import_excel.setText(LanguageService.get("import_excel"))
        self.btn_import_text.setText(LanguageService.get("import_text"))
        self.btn_export.setText(LanguageService.get("export_excel"))

        self.btn_correct.setText(LanguageService.get("correct"))
        self.btn_wrong.setText(LanguageService.get("wrong"))
        self.btn_pass.setText(LanguageService.get("pass"))
        self.btn_random.setText(LanguageService.get("random_pick"))

        self.btn_edit.setText(LanguageService.get("edit_info"))
        self.btn_score.setText(LanguageService.get("detailed_score"))
        self.btn_profile.setText(LanguageService.get("profile_notes"))
        self.btn_delete_student.setText(LanguageService.get("delete_student"))

        self.table.setHorizontalHeaderLabels([
            LanguageService.get("no"),
            LanguageService.get("first_name"),
            LanguageService.get("last_name"),
            LanguageService.get("gender")
        ])

    def open_oral_grade_dialog(self):
        class_id = self.class_selector.currentData()
        class_name = self.class_selector.currentText()
        if not class_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir sınıf seçin.")
            return

        dialog = OralGradeDialog(class_id, class_name, self)
        dialog.exec()