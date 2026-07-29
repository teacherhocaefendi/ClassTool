import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QComboBox, QFrame, QScrollArea,
                             QListWidget, QListWidgetItem, QSpinBox, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag, QPixmap
from database.db_manager import db
from services.language_service import LanguageService


class FrontObjectWidget(QLabel):
    def __init__(self, obj_id, title, style_css, parent_layout_view, parent=None):
        super().__init__(parent)
        self.obj_id = obj_id
        self.title_text = title
        self.style_css = style_css
        self.parent_layout_view = parent_layout_view

        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(self.title_text)
        self.setStyleSheet(self.style_css)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            mime_data = QMimeData()
            mime_data.setText(f"FRONT_OBJ|{self.obj_id}")

            drag = QDrag(self)
            drag.setMimeData(mime_data)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and "FRONT_OBJ" in event.mimeData().text():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and "FRONT_OBJ" in event.mimeData().text():
            event.acceptProposedAction()

    def dropEvent(self, event):
        raw_data = event.mimeData().text()
        if "FRONT_OBJ" in raw_data:
            source_id = int(raw_data.split("|")[1])
            target_id = self.obj_id

            if source_id != target_id:
                self.parent_layout_view.swap_front_objects(source_id, target_id)
                event.acceptProposedAction()


class StudentListWidget(QListWidget):
    def __init__(self, view_parent=None, parent=None):
        super().__init__(parent)
        self.view_parent = view_parent
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QListWidget::item {
                padding: 8px; margin-bottom: 4px; border-radius: 6px; font-weight: bold; font-size: 13px;
            }
            QListWidget::item:hover { background-color: #DEEBFF; color: #0052CC; }
            QListWidget::item:selected { background-color: #0052CC; color: white; }
        """)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item or item.isHidden():
            return

        data_str = item.data(Qt.ItemDataRole.UserRole)
        if not data_str:
            return

        mime_data = QMimeData()
        mime_data.setText(f"FROM_POOL|{data_str}")

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        pixmap = QPixmap(90, 22)
        pixmap.fill(Qt.GlobalColor.transparent)
        drag.setPixmap(pixmap)
        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and "FROM_CHAIR" in event.mimeData().text():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and "FROM_CHAIR" in event.mimeData().text():
            event.acceptProposedAction()

    def dropEvent(self, event):
        raw_data = event.mimeData().text()
        if "FROM_CHAIR" in raw_data:
            parts = raw_data.split("|")
            student_id = int(parts[1])
            chair_id = int(parts[5])

            if self.view_parent:
                self.view_parent.unhide_student_in_pool(student_id)
                self.view_parent.clear_chair_by_id(chair_id)

            event.acceptProposedAction()


class ChairWidget(QLabel):
    def __init__(self, chair_id, view_parent, scale_factor=1.0, parent=None):
        super().__init__(parent)
        self.chair_id = chair_id
        self.view_parent = view_parent
        self.scale_factor = scale_factor
        self.student_data = None
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reset_chair()

    def reset_chair(self):
        self.student_data = None
        empty_text = "🪑 Boş" if LanguageService.current_lang == "tr" else "🪑 Empty"
        self.setText(empty_text)

        w = int(60 * self.scale_factor)
        h = int(35 * self.scale_factor)
        font_sz = max(9, int(11 * self.scale_factor))

        self.setStyleSheet(f"""
            QLabel {{
                color: #A5ADBA; border: 1px dashed #DFE1E6; border-radius: 6px;
                padding: 2px; font-size: {font_sz}px; font-weight: bold;
                min-width: {w}px; min-height: {h}px;
            }}
        """)

    def set_student(self, student_info):
        self.student_data = student_info
        gender = str(student_info.get('gender', '')).lower()

        w = int(60 * self.scale_factor)
        h = int(35 * self.scale_factor)
        font_sz = max(9, int(11 * self.scale_factor))

        if gender in ['female', 'kız']:
            emoji = "👧"
            style = f"""
                QLabel {{
                    background-color: #FCE4EC; color: #C2185B;
                    border: 2px solid #E91E63; border-radius: 6px;
                    padding: 2px; font-size: {font_sz}px; font-weight: bold;
                    min-width: {w}px; min-height: {h}px;
                }}
                QLabel:hover {{ background-color: #F8BBD0; }}
            """
        else:
            emoji = "👦"
            style = f"""
                QLabel {{
                    background-color: #E3F2FD; color: #1565C0;
                    border: 2px solid #1976D2; border-radius: 6px;
                    padding: 2px; font-size: {font_sz}px; font-weight: bold;
                    min-width: {w}px; min-height: {h}px;
                }}
                QLabel:hover {{ background-color: #BBDEFB; }}
            """

        self.setText(f"{emoji} {student_info['first_name']}\n{student_info['last_name']}")
        self.setStyleSheet(style)

    def mouseMoveEvent(self, event):
        if self.student_data and event.buttons() == Qt.MouseButton.LeftButton:
            mime_data = QMimeData()
            s = self.student_data
            mime_data.setText(f"FROM_CHAIR|{s['id']}|{s['first_name']}|{s['last_name']}|{s.get('gender', 'Male')}|{self.chair_id}")

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and ("FROM_POOL" in event.mimeData().text() or "FROM_CHAIR" in event.mimeData().text()):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and ("FROM_POOL" in event.mimeData().text() or "FROM_CHAIR" in event.mimeData().text()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        raw_data = event.mimeData().text()

        if "FROM_POOL" in raw_data:
            parts = raw_data.split("|")
            student_id = int(parts[1])
            first_name = parts[2]
            last_name = parts[3]
            gender = parts[4] if len(parts) > 4 else "Male"

            if self.student_data:
                self.view_parent.unhide_student_in_pool(self.student_data['id'])

            student_info = {'id': student_id, 'first_name': first_name, 'last_name': last_name, 'gender': gender}
            self.set_student(student_info)
            self.view_parent.hide_student_in_pool(student_id)
            event.acceptProposedAction()

        elif "FROM_CHAIR" in raw_data:
            parts = raw_data.split("|")
            source_student_id = int(parts[1])
            source_first = parts[2]
            source_last = parts[3]
            source_gender = parts[4]
            source_chair_id = int(parts[5])

            if source_chair_id == self.chair_id:
                return

            source_student = {
                'id': source_student_id,
                'first_name': source_first,
                'last_name': source_last,
                'gender': source_gender
            }

            target_student = self.student_data
            source_chair = self.view_parent.get_chair_by_id(source_chair_id)

            self.set_student(source_student)

            if target_student and source_chair:
                source_chair.set_student(target_student)
            elif source_chair:
                source_chair.reset_chair()

            event.acceptProposedAction()


class SeatingView(QWidget):
    def __init__(self):
        super().__init__()
        self.chairs = []
        self.current_model = "classic"
        self.zoom_factor = 1.0  # Zoom Ölçeği (1.0 = %100)

        self.front_objects_data = [
            {
                "id": 0,
                "text": "🗑️ Çöp Kutusu" if LanguageService.current_lang == "tr" else "🗑️ Trash Bin",
                "style": "background-color: #424242; color: #E0E0E0; font-weight: bold; border-radius: 6px; padding: 6px;",
                "stretch": 1
            },
            {
                "id": 1,
                "text": "🖥️ Akıllı Tahta" if LanguageService.current_lang == "tr" else "🖥️ Smart Board",
                "style": "background-color: #1B5E20; color: #FFFFFF; font-weight: bold; font-size: 14px; border: 2px solid #2E7D32; border-radius: 6px; padding: 8px;",
                "stretch": 3
            },
            {
                "id": 2,
                "text": "👨‍🏫 Öğretmen Masası" if LanguageService.current_lang == "tr" else "👨‍🏫 Teacher Desk",
                "style": "background-color: #5D4037; color: #FFECB3; font-weight: bold; font-size: 13px; border-radius: 6px; padding: 6px;",
                "stretch": 2
            }
        ]

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # SOL PANEL (HAVUZ)
        left_panel = QVBoxLayout()
        self.lbl_pool = QLabel(LanguageService.get("unassigned"))
        self.lbl_pool.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_panel.addWidget(self.lbl_pool)

        self.student_pool = StudentListWidget(view_parent=self)
        left_panel.addWidget(self.student_pool)
        main_layout.addLayout(left_panel, stretch=1)

        # SAĞ PANEL
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)

        # 1. ÜST BAR
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.class_selector = QComboBox()
        self.class_selector.setMinimumWidth(100)
        self.class_selector.currentIndexChanged.connect(self.on_class_changed)
        toolbar.addWidget(self.class_selector)

        self.layout_selector = QComboBox()
        self.layout_selector.setMinimumWidth(120)
        self.layout_selector.currentIndexChanged.connect(self.load_selected_layout)
        toolbar.addWidget(self.layout_selector)

        # ÇİFT MOD BUTONLARI
        self.btn_toggle_size = QPushButton("📐 Sınıf Ölçüleri" if LanguageService.current_lang == "tr" else "📐 Dimensions")
        self.btn_toggle_templates = QPushButton("🎨 Yerleşim Düzenleri" if LanguageService.current_lang == "tr" else "🎨 Layout Templates")

        btn_toggle_style = "padding: 6px 12px; font-weight: bold; border-radius: 6px; background-color: #172B4D; color: white;"
        self.btn_toggle_size.setStyleSheet(btn_toggle_style)
        self.btn_toggle_templates.setStyleSheet(btn_toggle_style)

        self.btn_toggle_size.clicked.connect(self.toggle_size_panel)
        self.btn_toggle_templates.clicked.connect(self.toggle_templates_panel)

        toolbar.addWidget(self.btn_toggle_size)
        toolbar.addWidget(self.btn_toggle_templates)

        # ZOOM (YAKINLAŞTIR / UZAKLAŞTIR) KONTROLLERİ
        self.btn_zoom_out = QPushButton("🔍 -")
        self.btn_zoom_in = QPushButton("🔍 +")
        self.btn_zoom_reset = QPushButton("100%")

        zoom_style = "padding: 5px 8px; font-weight: bold; border-radius: 4px; background-color: #242526; color: #E4E6EB; border: 1px solid #3A3B3C;"
        for zb in [self.btn_zoom_out, self.btn_zoom_in, self.btn_zoom_reset]:
            zb.setStyleSheet(zoom_style)

        self.btn_zoom_out.clicked.connect(lambda: self.adjust_zoom(-0.15))
        self.btn_zoom_in.clicked.connect(lambda: self.adjust_zoom(0.15))
        self.btn_zoom_reset.clicked.connect(lambda: self.set_zoom(1.0))

        toolbar.addWidget(self.btn_zoom_out)
        toolbar.addWidget(self.btn_zoom_reset)
        toolbar.addWidget(self.btn_zoom_in)

        toolbar.addStretch()
        right_panel.addLayout(toolbar)

        # 2. DÜZELTİLMİŞ SPINBOX PANELİ (Buton Çakışması Engellendi)
        self.panel_sizes = QFrame()
        self.panel_sizes.setStyleSheet("QFrame { background-color: #EBECF0; border-radius: 6px; padding: 4px; }")
        layout_sizes = QHBoxLayout(self.panel_sizes)
        layout_sizes.setContentsMargins(8, 4, 8, 4)

        # Spinbox Buton Çakışmasını Çözen Genişletilmiş QSS
        spin_style = """
            QSpinBox {
                padding-right: 25px; 
                padding-left: 8px;
                font-weight: bold; 
                font-size: 13px;
                border: 2px solid #C1C7D0; 
                border-radius: 6px; 
                min-width: 75px;
                min-height: 28px;
                background-color: white;
                color: #172B4D;
            }
            QSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 20px; border-left: 1px solid #C1C7D0; }
            QSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 20px; border-left: 1px solid #C1C7D0; }
        """

        self.lbl_b = QLabel(LanguageService.get("row_lbl"))
        self.lbl_b.setStyleSheet("font-weight: bold; color: #172B4D;")
        self.spin_blocks = QSpinBox()
        self.spin_blocks.setRange(1, 8)
        self.spin_blocks.setValue(3)
        self.spin_blocks.setStyleSheet(spin_style)

        self.lbl_r = QLabel(LanguageService.get("depth_lbl"))
        self.lbl_r.setStyleSheet("font-weight: bold; color: #172B4D;")
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(1, 10)
        self.spin_rows.setValue(5)
        self.spin_rows.setStyleSheet(spin_style)

        self.lbl_c = QLabel(LanguageService.get("seat_lbl"))
        self.lbl_c.setStyleSheet("font-weight: bold; color: #172B4D;")
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 4)
        self.spin_cols.setValue(2)
        self.spin_cols.setStyleSheet(spin_style)

        self.btn_apply_size = QPushButton(LanguageService.get("build_layout"))
        self.btn_apply_size.setStyleSheet("background-color: #0052CC; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;")
        self.btn_apply_size.clicked.connect(lambda: self.change_layout_model(self.current_model))

        layout_sizes.addWidget(self.lbl_b)
        layout_sizes.addWidget(self.spin_blocks)
        layout_sizes.addWidget(self.lbl_r)
        layout_sizes.addWidget(self.spin_rows)
        layout_sizes.addWidget(self.lbl_c)
        layout_sizes.addWidget(self.spin_cols)
        layout_sizes.addWidget(self.btn_apply_size)
        layout_sizes.addStretch()
        self.panel_sizes.setVisible(False)
        right_panel.addWidget(self.panel_sizes)

        # ŞABLON PANELI
        self.panel_templates = QFrame()
        self.panel_templates.setStyleSheet("QFrame { background-color: #EBECF0; border-radius: 6px; padding: 4px; }")
        layout_templates = QHBoxLayout(self.panel_templates)
        layout_templates.setContentsMargins(8, 4, 8, 4)

        self.btn_model_classic = QPushButton("🏢 Klasik" if LanguageService.current_lang == "tr" else "🏢 Rows")
        self.btn_model_u = QPushButton("🔄 U-Düzeni" if LanguageService.current_lang == "tr" else "🔄 U-Shape")
        self.btn_model_station = QPushButton("🧩 İstasyon/Küme" if LanguageService.current_lang == "tr" else "🧩 Stations")

        model_btn_style = "padding: 6px 12px; font-weight: bold; border-radius: 4px; background-color: #0052CC; color: white;"
        for b in [self.btn_model_classic, self.btn_model_u, self.btn_model_station]:
            b.setStyleSheet(model_btn_style)

        self.btn_model_classic.clicked.connect(lambda: self.change_layout_model("classic"))
        self.btn_model_u.clicked.connect(lambda: self.change_layout_model("u_shape"))
        self.btn_model_station.clicked.connect(lambda: self.change_layout_model("station"))

        layout_templates.addWidget(self.btn_model_classic)
        layout_templates.addWidget(self.btn_model_u)
        layout_templates.addWidget(self.btn_model_station)
        layout_templates.addStretch()
        self.panel_templates.setVisible(False)
        right_panel.addWidget(self.panel_templates)

        # 3. MASA ÇİZİM ALANI
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grid_container = QFrame()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(8)

        self.scroll_area.setWidget(self.grid_container)
        right_panel.addWidget(self.scroll_area, stretch=1)

        # 4. ALT İŞLEM BARI
        action_bar = QHBoxLayout()
        action_bar.setSpacing(8)

        self.btn_save_quick = QPushButton("💾 Hızlı Kaydet" if LanguageService.current_lang == "tr" else "💾 Quick Save")
        self.btn_save_quick.setStyleSheet("background-color: #36B37E; color: white; padding: 6px 12px; font-weight: bold; border-radius: 6px;")
        self.btn_save_quick.clicked.connect(self.quick_save_layout)

        self.btn_save_as = QPushButton("💾 Farklı Kaydet" if LanguageService.current_lang == "tr" else "💾 Save As")
        self.btn_save_as.setStyleSheet("background-color: #FF991F; color: #172B4D; padding: 6px 12px; font-weight: bold; border-radius: 6px;")
        self.btn_save_as.clicked.connect(self.save_layout_dialog)

        action_bar.addWidget(self.btn_save_quick)
        action_bar.addWidget(self.btn_save_as)
        action_bar.addStretch()
        right_panel.addLayout(action_bar)

        # 5. SINIF ÖNÜ ALANI
        front_container = QHBoxLayout()
        front_container.setSpacing(8)

        door_text = "🚪\nK\na\np\nı" if LanguageService.current_lang == "tr" else "🚪\nD\no\no\nr"
        self.door_label = QLabel(door_text)
        self.door_label.setStyleSheet("""
            QLabel {
                background-color: #8D6E63; color: #FFFFFF; font-weight: bold;
                font-size: 11px; border: 2px solid #5D4037; border-radius: 6px;
                padding: 4px; min-width: 28px; max-width: 32px;
            }
        """)
        self.door_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        front_container.addWidget(self.door_label)

        self.front_layout = QHBoxLayout()
        self.front_layout.setSpacing(8)
        self.render_front_objects()

        front_container.addLayout(self.front_layout, stretch=1)
        right_panel.addLayout(front_container)

        main_layout.addLayout(right_panel, stretch=3)

    def adjust_zoom(self, delta):
        new_factor = round(self.zoom_factor + delta, 2)
        if 0.5 <= new_factor <= 2.0:
            self.set_zoom(new_factor)

    def set_zoom(self, factor):
        self.zoom_factor = factor
        self.btn_zoom_reset.setText(f"{int(factor * 100)}%")
        # Zoom değiştikçe mevcut öğrencilerin yerini koruyarak yeniden ölçekle
        saved_chairs_state = [{'chair_id': c.chair_id, 'student_data': c.student_data} for c in self.chairs]
        self.generate_classroom_layout(self.current_model)
        for item in saved_chairs_state:
            c_id = item['chair_id']
            s_data = item['student_data']
            if c_id < len(self.chairs) and s_data:
                self.chairs[c_id].set_student(s_data)

    def toggle_size_panel(self):
        self.panel_templates.setVisible(False)
        self.panel_sizes.setVisible(not self.panel_sizes.isVisible())

    def toggle_templates_panel(self):
        self.panel_sizes.setVisible(False)
        self.panel_templates.setVisible(not self.panel_templates.isVisible())

    def render_front_objects(self):
        for i in reversed(range(self.front_layout.count())):
            item = self.front_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        for obj in self.front_objects_data:
            w = FrontObjectWidget(
                obj_id=obj["id"],
                title=obj["text"],
                style_css=obj["style"],
                parent_layout_view=self
            )
            self.front_layout.addWidget(w, stretch=obj["stretch"])

    def swap_front_objects(self, source_id, target_id):
        idx1 = next(i for i, item in enumerate(self.front_objects_data) if item["id"] == source_id)
        idx2 = next(i for i, item in enumerate(self.front_objects_data) if item["id"] == target_id)

        self.front_objects_data[idx1], self.front_objects_data[idx2] = \
            self.front_objects_data[idx2], self.front_objects_data[idx1]

        self.render_front_objects()

    def get_chair_by_id(self, chair_id):
        for chair in self.chairs:
            if chair.chair_id == chair_id:
                return chair
        return None

    def load_data(self):
        self.load_classes()

    def load_classes(self):
        self.class_selector.blockSignals(True)
        self.class_selector.clear()
        classes = db.get_classes()
        for cls in classes:
            self.class_selector.addItem(cls['name'], cls['id'])
        self.class_selector.blockSignals(False)

        if self.class_selector.count() > 0:
            self.on_class_changed()

    def on_class_changed(self):
        self.load_students_into_pool()
        self.refresh_layout_names_dropdown()

    def refresh_layout_names_dropdown(self):
        class_id = self.class_selector.currentData()
        if not class_id:
            return

        self.layout_selector.blockSignals(True)
        self.layout_selector.clear()

        layouts = db.get_seating_layouts(class_id)
        if layouts:
            for row in layouts:
                self.layout_selector.addItem(row['layout_name'], row['layout_json'])
        else:
            default_name = "Varsayılan Düzen" if LanguageService.current_lang == "tr" else "Default Layout"
            self.layout_selector.addItem(default_name, None)

        self.layout_selector.blockSignals(False)
        self.load_selected_layout()

    def load_selected_layout(self):
        json_data = self.layout_selector.currentData()
        if json_data:
            try:
                layout_data = json.loads(json_data)
                self.current_model = layout_data.get("model", "classic")
                blocks = layout_data.get("blocks", self.spin_blocks.value())
                rows = layout_data.get("rows", self.spin_rows.value())
                cols = layout_data.get("cols", self.spin_cols.value())

                self.spin_blocks.setValue(blocks)
                self.spin_rows.setValue(rows)
                self.spin_cols.setValue(cols)

                self.generate_classroom_layout(self.current_model)

                chairs_data = layout_data.get("chairs", [])
                if "front_objects" in layout_data:
                    self.front_objects_data = layout_data["front_objects"]
                    self.render_front_objects()

                for item in chairs_data:
                    chair_id = item['chair_id']
                    student_data = item['student_data']
                    if chair_id < len(self.chairs) and student_data:
                        self.chairs[chair_id].set_student(student_data)
                        self.hide_student_in_pool(student_data['id'])
                return
            except Exception:
                pass

        self.generate_classroom_layout("classic")

    def load_students_into_pool(self):
        self.student_pool.clear()
        students = db.get_students()
        for s in students:
            item = QListWidgetItem(f"{s['first_name']} {s['last_name']}")
            item.setData(Qt.ItemDataRole.UserRole, f"{s['id']}|{s['first_name']}|{s['last_name']}|{s['gender']}")
            self.student_pool.addItem(item)

    def hide_student_in_pool(self, student_id):
        for i in range(self.student_pool.count()):
            item = self.student_pool.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data and int(data.split("|")[0]) == student_id:
                item.setHidden(True)
                break

    def unhide_student_in_pool(self, student_id):
        for i in range(self.student_pool.count()):
            item = self.student_pool.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data and int(data.split("|")[0]) == student_id:
                item.setHidden(False)
                break

    def clear_chair_by_id(self, chair_id):
        chair = self.get_chair_by_id(chair_id)
        if chair:
            chair.reset_chair()

    def change_layout_model(self, model_type):
        self.current_model = model_type
        self.load_students_into_pool()
        self.generate_classroom_layout(model_type)

    def generate_classroom_layout(self, model_type):
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        self.chairs.clear()
        chair_counter = 0

        blocks = self.spin_blocks.value()
        rows = self.spin_rows.value()
        cols = self.spin_cols.value()

        # 1. KLASİK (SIRALI) DÜZEN
        if model_type == "classic":
            for r in range(rows):
                for b in range(blocks):
                    desk_frame = QFrame()
                    desk_frame.setStyleSheet("QFrame { border: 1px solid #3A3B3C; border-radius: 8px; padding: 2px; }")
                    desk_layout = QHBoxLayout(desk_frame)
                    desk_layout.setSpacing(2)

                    for _ in range(cols):
                        chair = ChairWidget(chair_id=chair_counter, view_parent=self, scale_factor=self.zoom_factor)
                        desk_layout.addWidget(chair)
                        self.chairs.append(chair)
                        chair_counter += 1

                    self.grid_layout.addWidget(desk_frame, r, b)

        # 2. GERÇEK GEOMETRİK U-DÜZENİ (Sol Kanat Dikey + Arka Kanat Yatay + Sağ Kanat Dikey)
        elif model_type == "u_shape":
            total_cols = max(blocks, 3)

            for r in range(rows):
                for c in range(total_cols):
                    is_left_wing = (c == 0)
                    is_right_wing = (c == total_cols - 1)
                    is_bottom_row = (r == rows - 1)

                    if is_left_wing or is_right_wing or is_bottom_row:
                        desk_frame = QFrame()
                        desk_frame.setStyleSheet("QFrame { border: 2px solid #FF991F; border-radius: 8px; padding: 2px; }")

                        # Yan kanatlarda sıralar DİKEY dizilir!
                        if is_left_wing or is_right_wing:
                            desk_layout = QVBoxLayout(desk_frame)
                        else:
                            desk_layout = QHBoxLayout(desk_frame)

                        desk_layout.setSpacing(2)

                        for _ in range(cols):
                            chair = ChairWidget(chair_id=chair_counter, view_parent=self, scale_factor=self.zoom_factor)
                            desk_layout.addWidget(chair)
                            self.chairs.append(chair)
                            chair_counter += 1

                        self.grid_layout.addWidget(desk_frame, r, c)

        # 3. DİNAMİK İSTASYON / KÜME MODELİ
        elif model_type == "station":
            for r in range(rows):
                for b in range(blocks):
                    desk_frame = QFrame()
                    desk_frame.setStyleSheet("QFrame { border: 2px solid #36B37E; border-radius: 8px; padding: 4px; background-color: rgba(54, 179, 126, 0.05); }")
                    desk_layout = QGridLayout(desk_frame)
                    desk_layout.setSpacing(2)

                    for i in range(cols):
                        chair = ChairWidget(chair_id=chair_counter, view_parent=self, scale_factor=self.zoom_factor)
                        desk_layout.addWidget(chair, i // 2, i % 2)
                        self.chairs.append(chair)
                        chair_counter += 1

                    self.grid_layout.addWidget(desk_frame, r, b)

    def quick_save_layout(self):
        class_id = self.class_selector.currentData()
        current_name = self.layout_selector.currentText()
        if not class_id or not current_name:
            return

        layout_data = {
            "model": self.current_model,
            "blocks": self.spin_blocks.value(),
            "rows": self.spin_rows.value(),
            "cols": self.spin_cols.value(),
            "chairs": [{'chair_id': c.chair_id, 'student_data': c.student_data} for c in self.chairs],
            "front_objects": self.front_objects_data
        }
        json_str = json.dumps(layout_data, ensure_ascii=False)
        db.save_seating_layout(class_id, current_name, json_str)

        msg = f"'{current_name}' güncellendi." if LanguageService.current_lang == "tr" else f"'{current_name}' updated."
        QMessageBox.information(self, "Başarılı" if LanguageService.current_lang == "tr" else "Success", msg)

    def save_layout_dialog(self):
        class_id = self.class_selector.currentData()
        if not class_id:
            return

        prompt_title = "Planı Kaydet" if LanguageService.current_lang == "tr" else "Save Layout"
        prompt_msg = "Lütfen bu oturma düzeni için bir isim girin:" if LanguageService.current_lang == "tr" else "Enter a name for this layout:"

        layout_name, ok = QInputDialog.getText(self, prompt_title, prompt_msg)
        if ok and layout_name.strip():
            layout_data = {
                "model": self.current_model,
                "blocks": self.spin_blocks.value(),
                "rows": self.spin_rows.value(),
                "cols": self.spin_cols.value(),
                "chairs": [{'chair_id': c.chair_id, 'student_data': c.student_data} for c in self.chairs],
                "front_objects": self.front_objects_data
            }
            json_str = json.dumps(layout_data, ensure_ascii=False)
            db.save_seating_layout(class_id, layout_name.strip(), json_str)

            msg = f"'{layout_name}' düzeni kaydedildi." if LanguageService.current_lang == "tr" else f"'{layout_name}' saved."
            QMessageBox.information(self, "Başarılı" if LanguageService.current_lang == "tr" else "Success", msg)
            self.refresh_layout_names_dropdown()

    def retranslate_ui(self):
        self.lbl_pool.setText(LanguageService.get("unassigned"))
        self.btn_toggle_size.setText("📐 Sınıf Ölçüleri" if LanguageService.current_lang == "tr" else "📐 Dimensions")
        self.btn_toggle_templates.setText("🎨 Yerleşim Düzenleri" if LanguageService.current_lang == "tr" else "🎨 Layout Templates")

        self.lbl_b.setText(LanguageService.get("row_lbl"))
        self.lbl_r.setText(LanguageService.get("depth_lbl"))
        self.lbl_c.setText(LanguageService.get("seat_lbl"))
        self.btn_apply_size.setText(LanguageService.get("build_layout"))

        self.btn_model_classic.setText("🏢 Klasik" if LanguageService.current_lang == "tr" else "🏢 Rows")
        self.btn_model_u.setText("🔄 U-Düzeni" if LanguageService.current_lang == "tr" else "🔄 U-Shape")
        self.btn_model_station.setText("🧩 İstasyon/Küme" if LanguageService.current_lang == "tr" else "🧩 Stations")

        self.btn_save_quick.setText("💾 Hızlı Kaydet" if LanguageService.current_lang == "tr" else "💾 Quick Save")
        self.btn_save_as.setText("💾 Farklı Kaydet" if LanguageService.current_lang == "tr" else "💾 Save As")

        door_text = "🚪\nK\na\np\nı" if LanguageService.current_lang == "tr" else "🚪\nD\no\no\nr"
        self.door_label.setText(door_text)

        tr_texts = ["🗑️ Çöp Kutusu", "🖥️ Akıllı Tahta", "👨‍🏫 Öğretmen Masası"]
        en_texts = ["🗑️ Trash Bin", "🖥️ Smart Board", "👨‍🏫 Teacher Desk"]
        texts = tr_texts if LanguageService.current_lang == "tr" else en_texts

        for obj in self.front_objects_data:
            obj["text"] = texts[obj["id"]]

        self.render_front_objects()

        for chair in self.chairs:
            if not chair.student_data:
                chair.reset_chair()