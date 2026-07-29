import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QComboBox, QScrollArea, QFrame,
                             QMessageBox, QDialog, QFormLayout)
from PyQt6.QtCore import Qt
from database.db_manager import db
from services.group_service import GroupService
from services.language_service import LanguageService


class GroupSettingsDialog(QDialog):
    def __init__(self, current_rules, parent=None):
        super().__init__(parent)
        self.setWindowTitle(LanguageService.get("rules_dialog_title"))
        self.setFixedSize(360, 240)
        self.rules = current_rules.copy()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title_text = "Grup Kurallarını Yapılandır" if LanguageService.current_lang == "tr" else "Configure Grouping Rules"
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()

        self.btn_gender = QPushButton()
        self.update_toggle_btn(self.btn_gender, self.rules['balance_gender'], LanguageService.get("equal_gender"))
        self.btn_gender.clicked.connect(lambda: self.toggle_rule('balance_gender', self.btn_gender, LanguageService.get("equal_gender")))

        self.btn_traits = QPushButton()
        self.update_toggle_btn(self.btn_traits, self.rules['balance_traits'], LanguageService.get("balance_traits"))
        self.btn_traits.clicked.connect(lambda: self.toggle_rule('balance_traits', self.btn_traits, LanguageService.get("balance_traits")))

        lbl_gender = "Cinsiyet Dağılımı:" if LanguageService.current_lang == "tr" else "Gender Mix:"
        lbl_profile = "Profil Dengesi:" if LanguageService.current_lang == "tr" else "Profile Mix:"

        form.addRow(lbl_gender, self.btn_gender)
        form.addRow(lbl_profile, self.btn_traits)
        layout.addLayout(form)

        btn_save = QPushButton(LanguageService.get("apply_rules"))
        btn_save.setStyleSheet("background-color: #0052CC; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

    def toggle_rule(self, key, btn, label_text):
        self.rules[key] = not self.rules[key]
        self.update_toggle_btn(btn, self.rules[key], label_text)

    def update_toggle_btn(self, btn, is_on, label_text):
        if is_on:
            btn.setText(f"🟢 ON ({label_text})")
            btn.setStyleSheet("background-color: #36B37E; color: white; padding: 8px; font-weight: bold; border-radius: 4px; border: none;")
        else:
            random_txt = "Rastgele" if LanguageService.current_lang == "tr" else "Random"
            btn.setText(f"🔴 OFF ({random_txt})")
            btn.setStyleSheet("background-color: #FF5630; color: white; padding: 8px; font-weight: bold; border-radius: 4px; border: none;")


class GroupView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_groups = []
        self.rules = {
            'balance_gender': False,
            'balance_traits': False
        }
        self.setup_ui()
        self.load_classes()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        toolbar_layout = QHBoxLayout()

        self.class_selector = QComboBox()
        self.class_selector.currentIndexChanged.connect(self.load_latest_group_history)
        toolbar_layout.addWidget(self.class_selector)

        self.size_selector = QComboBox()
        if LanguageService.current_lang == "tr":
            self.size_selector.addItems(["İkili (2)", "3'lü Grup", "4'lü Grup", "5'li Grup"])
        else:
            self.size_selector.addItems(["Pairs (2)", "Groups of 3", "Groups of 4", "Groups of 5"])
        toolbar_layout.addWidget(self.size_selector)

        self.btn_rules = QPushButton(LanguageService.get("rules_btn"))
        self.btn_rules.setStyleSheet("""
            QPushButton { padding: 10px 15px; font-size: 14px; font-weight: bold; border-radius: 5px; }
        """)
        self.btn_rules.clicked.connect(self.open_rules_dialog)
        toolbar_layout.addWidget(self.btn_rules)

        self.btn_generate = QPushButton(LanguageService.get("generate_groups"))
        self.btn_generate.setStyleSheet("""
            QPushButton { background-color: #36B37E; color: white; padding: 10px 15px;
                          font-size: 14px; font-weight: bold; border-radius: 5px; }
            QPushButton:hover { background-color: #2b8f65; }
        """)
        self.btn_generate.clicked.connect(self.generate_groups)
        toolbar_layout.addWidget(self.btn_generate)

        self.btn_save = QPushButton(LanguageService.get("save_groups"))
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: #0052CC; color: white; padding: 10px 15px;
                          font-size: 14px; font-weight: bold; border-radius: 5px; }
            QPushButton:hover { background-color: #003e99; }
        """)
        self.btn_save.clicked.connect(self.save_groups_to_db)
        toolbar_layout.addWidget(self.btn_save)

        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background-color: transparent;")

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(20)

        self.scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll_area)

    def open_rules_dialog(self):
        dialog = GroupSettingsDialog(self.rules, self)
        if dialog.exec():
            self.rules = dialog.rules

    def load_classes(self):
        self.class_selector.blockSignals(True)
        self.class_selector.clear()
        classes = db.get_classes()
        for cls in classes:
            self.class_selector.addItem(cls['name'], cls['id'])
        self.class_selector.blockSignals(False)

        if self.class_selector.count() > 0:
            self.class_selector.setCurrentIndex(0)
            self.load_latest_group_history()

    def generate_groups(self):
        class_id = self.class_selector.currentData()
        if not class_id:
            return

        size_mapping = {0: 2, 1: 3, 2: 4, 3: 5}
        group_size = size_mapping[self.size_selector.currentIndex()]

        raw_groups = GroupService.generate_groups(
            class_id=class_id,
            group_size=group_size,
            balance_gender=self.rules['balance_gender'],
            balance_traits=self.rules['balance_traits']
        )

        self.current_groups = []
        for g in raw_groups:
            group_list = []
            for s in g:
                group_list.append({
                    'id': s['id'],
                    'first_name': s['first_name'],
                    'last_name': s['last_name'],
                    'gender': s['gender']
                })
            self.current_groups.append(group_list)

        self.render_groups(self.current_groups)

    def render_groups(self, groups):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        cols = 3
        for index, group in enumerate(groups):
            row = index // cols
            col = index % cols

            group_title = f"Grup {index + 1}" if LanguageService.current_lang == "tr" else f"Group {index + 1}"
            card = self.create_group_card(group_title, group)
            self.grid_layout.addWidget(card, row, col)

    def create_group_card(self, title, members):
        card = QFrame()
        card.setStyleSheet("QFrame { border: 2px solid #DFE1E6; border-radius: 8px; padding: 10px; }")
        card_layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0052CC; border: none;")
        card_layout.addWidget(title_label)

        for student in members:
            dot_color = "#FF5630" if str(student['gender']).lower() in ['female', 'kız'] else "#0052CC"
            member_label = QLabel(f"<font color='{dot_color}'>●</font> {student['first_name']} {student['last_name']}")
            member_label.setStyleSheet("font-size: 15px; border: none;")
            card_layout.addWidget(member_label)

        card_layout.addStretch()
        return card

    def save_groups_to_db(self):
        class_id = self.class_selector.currentData()
        if not class_id or not self.current_groups:
            msg = "Kaydedilecek grup bulunamadı." if LanguageService.current_lang == "tr" else "No groups to save."
            QMessageBox.warning(self, "Uyarı" if LanguageService.current_lang == "tr" else "Warning", msg)
            return

        try:
            json_str = json.dumps(self.current_groups, ensure_ascii=False)
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO group_history (class_id, group_structure_json) VALUES (?, ?)",
                               (class_id, json_str))
                conn.commit()

            msg = "Grup yapısı veritabanına kaydedildi." if LanguageService.current_lang == "tr" else "Group layout successfully saved."
            QMessageBox.information(self, "Başarılı" if LanguageService.current_lang == "tr" else "Success", msg)
        except Exception as e:
            QMessageBox.critical(self, "Hata" if LanguageService.current_lang == "tr" else "Error", str(e))

    def load_latest_group_history(self):
        class_id = self.class_selector.currentData()
        if not class_id:
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT group_structure_json FROM group_history 
                    WHERE class_id = ? ORDER BY id DESC LIMIT 1
                """, (class_id,))
                row = cursor.fetchone()

                if row and row['group_structure_json']:
                    self.current_groups = json.loads(row['group_structure_json'])
                    self.render_groups(self.current_groups)
                else:
                    self.render_groups([])
        except Exception:
            self.render_groups([])

    def retranslate_ui(self):
        self.btn_rules.setText(LanguageService.get("rules_btn"))
        self.btn_generate.setText(LanguageService.get("generate_groups"))
        self.btn_save.setText(LanguageService.get("save_groups"))

        idx = self.size_selector.currentIndex()
        self.size_selector.blockSignals(True)
        self.size_selector.clear()
        if LanguageService.current_lang == "tr":
            self.size_selector.addItems(["İkili (2)", "3'lü Grup", "4'lü Grup", "5'li Grup"])
        else:
            self.size_selector.addItems(["Pairs (2)", "Groups of 3", "Groups of 4", "Groups of 5"])
        self.size_selector.setCurrentIndex(idx)
        self.size_selector.blockSignals(False)

        if self.current_groups:
            self.render_groups(self.current_groups)