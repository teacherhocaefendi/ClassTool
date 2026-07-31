from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QTextBrowser, QLabel)
from PyQt6.QtCore import Qt, QTimer
from services.theme_and_log_service import ThemeManager
from services.language_service import LanguageService


class HelpView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # SOL PANEL: Sade Konu Başlıkları
        left_layout = QVBoxLayout()
        self.lbl_topics = QLabel(LanguageService.get("guide_topics_title"))
        self.lbl_topics.setStyleSheet("font-size: 16px; font-weight: bold; color: #60A5FA;")
        left_layout.addWidget(self.lbl_topics)

        self.list_topics = QListWidget()
        self.list_topics.setFixedWidth(260)
        self.list_topics.setStyleSheet("""
            QListWidget {
                border: 2px solid #334155; border-radius: 8px; font-size: 14px; padding: 5px;
                background-color: #1E293B; color: #F8FAFC;
            }
            QListWidget::item {
                padding: 12px; margin-bottom: 5px; border-radius: 6px; font-weight: bold;
            }
            QListWidget::item:selected {
                background-color: #2563EB; color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #334155; color: #60A5FA;
            }
        """)

        self.load_topics()
        self.list_topics.currentRowChanged.connect(self.display_help_content)
        left_layout.addWidget(self.list_topics)
        main_layout.addLayout(left_layout)

        # SAĞ PANEL: İçerik Okuyucu
        right_layout = QVBoxLayout()
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        right_layout.addWidget(self.text_browser)
        main_layout.addLayout(right_layout, stretch=1)

        # İLK YÜKLEME DÜZELTMESİ:
        self.list_topics.setCurrentRow(0)
        self.display_help_content(0)

        # Render/Repaint işlemini garantiye almak için kısa zamanlayıcı ile zorla
        QTimer.singleShot(50, self.force_redraw)

    def force_redraw(self):
        """Pencere ilk çizildiğinde sağ paneldeki içeriklerin render olmasını zorlar."""
        if hasattr(self, 'text_browser'):
            self.text_browser.update()
            self.text_browser.repaint()

    def load_topics(self):
        self.list_topics.blockSignals(True)
        current_row = max(0, self.list_topics.currentRow())
        self.list_topics.clear()

        topics = LanguageService.get("guide_topics")
        if isinstance(topics, list):
            self.list_topics.addItems(topics)

        self.list_topics.setCurrentRow(current_row)
        self.list_topics.blockSignals(False)

    def refresh_theme(self):
        current_row = self.list_topics.currentRow()
        if current_row >= 0:
            self.display_help_content(current_row)

    def display_help_content(self, index):
        contents = self.get_contents_tr() if LanguageService.current_lang == "tr" else self.get_contents_en()
        is_dark = (ThemeManager.get_current_theme() == "dark")

        if is_dark:
            self.text_browser.setStyleSheet("""
                QTextBrowser {
                    background-color: #1E293B; border: 2px solid #334155; 
                    border-radius: 8px; padding: 20px; font-size: 15px; color: #F8FAFC;
                }
                h2 { color: #60A5FA; margin-bottom: 12px; }
                b { color: #38BDF8; }
                i { color: #94A3B8; }
                li { margin-bottom: 14px; }
            """)
        else:
            self.text_browser.setStyleSheet("""
                QTextBrowser {
                    background-color: #FFFFFF; border: 2px solid #DFE1E6; 
                    border-radius: 8px; padding: 20px; font-size: 15px; color: #172B4D;
                }
                h2 { color: #0052CC; margin-bottom: 12px; }
                b { color: #0747A6; }
                i { color: #5E6C84; }
                li { margin-bottom: 14px; }
            """)

        self.text_browser.setHtml(contents.get(index, ""))
        # İçerik değiştikten hemen sonra yeniden çizilmeye zorluyoruz
        self.text_browser.update()

    def get_contents_tr(self):
        return {
            0: """
                <h2>🚀 Başlangıç ve Temel Mantık</h2>
                <p><b>Class Tool</b>, sınıf içi etkileşimi artırmak, adil puanlama yapmak ve öğrenci gelişimini takip etmek için tasarlanmış dijital sınıf asistanınızdır.</p>
                <p style='color:#F59E0B; font-weight:bold;'>⚠️ ÖNEMLİ İLK KURAL:</p>
                <p>Uygulamayı kullanmaya başlamak için <b>mutlaka öncelikle bir sınıf oluşturmalı ve içerisine öğrencilerinizi eklemelisiniz.</b> Sınıf ve öğrenci verisi olmadan oturma planı, çarkıfelek ve grup oluşturucu çalışmayacaktır.</p>
                <ul>
                    <li>Sistem tamamen çevrimdışı (internetsiz) çalışır, verileriniz güvendedir.<br><br></li>
                    <li>Yalnızca yapay zeka ile öğrenci ekleme işleminde internet gereklidir.<br><br></li>
                    <li>Sınıfınızdaki akıllı tahtadan veya kişisel bilgisayarınızdan rahatça kullanabilirsiniz.<br><br></li>
                    <li>Sol menüyü kullanarak ana modüller arasında geçiş yapabilirsiniz.</li>
                </ul>
                <p><i>İpucu: Ekranın sol alt köşesindeki <b>☀️ Açık Mod / 🌙 Koyu Mod</b> butonunu kullanarak sınıfın aydınlığına göre tahta parlamasını önleyebilirsiniz.</i></p>
            """,
            1: """
                <h2>🏫 Sınıf ve Öğrenci İşlemleri</h2>
                <p>Uygulamaya sınıf ve öğrenci eklemek çok basittir.</p>
                <ul>
                    <li><b>1. Sınıf Oluşturma:</b> Sol menüden <i>'Öğrenci Listesi'</i> sekmesine tıklayın. Üstteki 'Sınıf Yönetimi' butonuna basarak yeni sınıfınızı tanımlayın.<br><br></li>
                    <li><b>2. Öğrenci Ekleme:</b> 'Veri İşlemleri' bölümünden öğrencilerinizi tek tek girebilirsiniz.<br><br></li>
                    <li><b>3. Yapay Zeka ile Liste Aktarma (Görsel / Metin):</b> E-Okul'dan kopyaladığınız listeyi veya <b>temiz ve net çekilmiş bir sınıf listesi fotoğrafını</b> <i>'Yapay Zeka Tarayıcı'</i> alanına yükleyerek saniyeler içinde otomatik ayrıştırabilirsiniz. Excel dosyalarınızı da doğrudan içeri aktarabilirsiniz.</li>
                </ul>
            """,
            2: """
                <h2>🪑 Oturma Planı Nasıl Yapılır?</h2>
                <p>Oturma Planı modülü, sınıfınızın fiziksel haritasını dijital ortama aktarmanızı sağlar.</p>
                <ol>
                    <li>Sol menüden <b>Oturma Planı</b> sekmesine geçin.<br><br></li>
                    <li>Sağ üstteki <b>📐 Sınıf Ölçüleri</b> butonuna tıklayarak sıra/blok sayılarını girin ve 'Kur' butonuna basın. Veya hazır şablonlardan (U-Düzeni, Küme) birini seçin.<br><br></li>
                    <li>Sol taraftaki 'Yerleşmeyen Öğrenciler' listesinden öğrencileri farenizle/parmağınızla tutarak boş sıralara sürükleyip bırakın.<br><br></li>
                    <li>Öğrencilerin yerini değiştirmek için bir sıradaki öğrenciyi diğerinin üzerine sürüklemeniz yeterlidir.<br><br></li>
                    <li>Düzeni kurduktan sonra mutlaka <b>💾 Hızlı Kaydet</b> butonuna basarak planı kaydedin.</li>
                </ol>
            """,
            3: """
                <h2>🧩 Akıllı Gruplar Oluşturma</h2>
                <p>Etkinlikler veya projeler için öğrencileri saniyeler içinde gruplara ayırabilirsiniz.</p>
                <ul>
                    <li><b>Grup Büyüklüğü:</b> İkili, 3'lü, 4'lü veya 5'li gruplar oluşturabilirsiniz.<br><br></li>
                    <li><b>⚙️ Kurallar:</b> 'Kurallar' butonuna tıklayarak grupların <i>Cinsiyet Dağılımına</i> göre adil bir şekilde dağıtılmasını sağlayabilirsiniz.<br><br></li>
                    <li>Grupları oluşturduktan sonra 'Grupları Kaydet' diyerek bu dağılımı veritabanında saklayabilir, bir sonraki derste aynı gruplarla devam edebilirsiniz.</li>
                </ul>
            """,
            4: """
                <h2>⚡ Derse Katılım ve Çarkıfelek</h2>
                <p>Öğrenci seçmek, derse kaldırmak veya anlık değerlendirme yapmak için bu alanı kullanın.</p>
                <ul>
                    <li><b>Hızlı Puanlama:</b> 'Öğrenci Listesi' > 'Ders & Katılım' sekmesinden bir öğrenci seçip Doğru/Yanlış verebilirsiniz.<br><br></li>
                    <li><b>🎡 Çarkıfelek (Rastgele Seçim):</b> Sınıfta heyecan yaratmak ve adil seçim yapmak için çarkıfeleği kullanın. Çark, daha önce hiç seçilmemiş veya en az seçilmiş öğrencilere öncelik vererek adaleti sağlar.<br><br></li>
                    <li>Çarkta çıkan öğrenciye anında değerlendirme yapabilir, bu verileri daha sonra karnede görebilirsiniz.</li>
                </ul>
            """,
            5: """
                <h2>📊 Raporlar ve Sözlü Notu</h2>
                <p>Dönem sonlarında veya veli toplantılarında işinizi en çok kolaylaştıracak modüldür.</p>
                <ul>
                    <li><b>Sözlü Notu Hesapla:</b> 'Öğrenci Listesi' > 'Veri İşlemleri' altındaki <i>Sözlü Notu Hesapla</i> aracıyla, öğrencilerin ödev teslim oranları ve derse katılım (artı/eksi) istatistiklerini istediğiniz yüzdelik ağırlıklarla çarpıp otomatik e-okul notu üretebilirsiniz.<br><br></li>
                    <li><b>Gelişim Raporu (PDF):</b> Bir öğrencinin profiline girip 'PDF Rapor İndir' derseniz, o öğrencinin tüm performansını ve kazandığı rozetleri şık bir karne olarak veliye gönderebilirsiniz.<br><br></li>
                    <li><b>Analizler:</b> Sol menüdeki 'Analizler' sekmesi sınıfın genel ödev ve katılım haritasını Excel formatında almanızı sağlar.</li>
                </ul>
            """,
            6: """
                <h2>⚙️ Güvenlik (USB) ve Yedekleme</h2>
                <p>Verilerinizi kaybetmemek ve tahtanızı meraklı öğrencilerden korumak için güvenlik ayarlarını kullanın.</p>
                <ul>
                    <li><b>USB Güvenlik Anahtarı:</b> Sol alttaki 'Şifre Değiştir' (Ayarlar) menüsünden boş bir flash belleği sisteme tanıtabilirsiniz. Artık şifre girmek yerine, tahtaya flash belleği taktığınız an kilit otomatik açılır.<br><br></li>
                    <li><b>Yedekleme:</b> Evdeki bilgisayarınızda planladığınız oturma düzenini veya eklediğiniz öğrencileri 'Yedek Dışarı Aktar' diyerek flash belleğinize alabilir, okuldaki tahtaya 'Yedek İçe Aktar' diyerek anında aktarabilirsiniz.</li>
                </ul>
            """,
            7: """
                <h2>💻 Geliştirici & İletişim Bilgileri</h2>
                <p>Class Tool uygulaması ders içi verimliliği artırmak ve öğretmenlerin yükünü hafifletmek amacıyla geliştirilmiştir.</p>
                <ul>
                    <li><b>Geliştirici:</b> Ammar Yakşi<br><br></li>
                    <li><b>Instagram:</b> @ammar_yksi011<br><br></li>
                    <li><b>GitHub Reposu:</b> github.com/teacherhocaefendi/ClassTool<br><br></li>
                </ul>
                <p>Soru, görüş, öneri veya hata bildirimleriniz için yukarıdaki adreslerden doğrudan iletişime geçebilirsiniz.</p>
            """
        }

    def get_contents_en(self):
        return {
            0: """
                <h2>🚀 Getting Started & Fundamental Rules</h2>
                <p><b>Class Tool</b> is your digital classroom assistant designed to boost engagement, ensure fair scoring, and track student progress.</p>
                <p style='color:#F59E0B; font-weight:bold;'>⚠️ IMPORTANT FIRST RULE:</p>
                <p>To start using the app, <b>you must first create a class and add your students.</b> Seating charts, wheel of fortune, and group generators won't work without active class data.</p>
                <ul>
                    <li>The system works completely offline, keeping your data safe.<br><br></li>
                    <li>Internet is only required when using the AI Vision student list scanner.<br><br></li>
                    <li>Easily operate on your smart board or personal computer.<br><br></li>
                    <li>Use the sidebar to navigate between main modules.</li>
                </ul>
                <p><i>Tip: Use the <b>☀️ Light / 🌙 Dark Mode</b> button at the bottom left to prevent board glare according to classroom lighting.</i></p>
            """,
            1: """
                <h2>🏫 Class & Student Management</h2>
                <p>Adding classes and student rosters is extremely simple.</p>
                <ul>
                    <li><b>1. Creating a Class:</b> Click <i>'Student Roster'</i> on the left menu. Open 'Class Management' at the top and create your new class.<br><br></li>
                    <li><b>2. Adding Students:</b> You can add students manually under the 'Data Operations' tab.<br><br></li>
                    <li><b>3. Import with AI (Image / Text):</b> Paste text copied from school portals or upload a <b>clear photo of a printed class list</b> into the <i>'AI Scanner'</i> to parse students automatically in seconds. Direct Excel import is also supported.</li>
                </ul>
            """,
            2: """
                <h2>🪑 How to Create a Seating Chart?</h2>
                <p>The Seating Chart module translates your physical classroom layout into a digital interactive map.</p>
                <ol>
                    <li>Switch to the <b>Seating Chart</b> tab on the sidebar.<br><br></li>
                    <li>Click <b>📐 Dimensions</b> at the top right, set row and block counts, then click 'Build'. Or pick a ready template (U-Shape, Stations).<br><br></li>
                    <li>Drag unassigned students from the left panel onto empty desks.<br><br></li>
                    <li>Drag a student over another to swap their seats instantly.<br><br></li>
                    <li>After setting up the layout, always click <b>💾 Quick Save</b> to save your changes.</li>
                </ol>
            """,
            3: """
                <h2>🧩 Creating Smart Groups</h2>
                <p>Divide students into activity or project groups in seconds.</p>
                <ul>
                    <li><b>Group Size:</b> Create pairs, groups of 3, 4, or 5.<br><br></li>
                    <li><b>⚙️ Rules:</b> Click 'Rules' to enforce balanced <i>Gender Mix</i> across groups.<br><br></li>
                    <li>Click 'Save Groups' to store the arrangement in the database for future lessons.</li>
                </ul>
            """,
            4: """
                <h2>⚡ Lesson Participation & Wheel of Fortune</h2>
                <p>Use this area for random student selection, board calls, and real-time evaluation.</p>
                <ul>
                    <li><b>Quick Scoring:</b> Select a student under 'Lesson & Participation' and click Correct/Wrong.<br><br></li>
                    <li><b>🎡 Wheel of Fortune (Random Pick):</b> Engage the class with an animated wheel. The wheel algorithm prioritizes unpicked students to ensure absolute fairness.<br><br></li>
                    <li>Evaluate the picked student instantly to record performance metrics.</li>
                </ul>
            """,
            5: """
                <h2>📊 Reports & Oral Grades</h2>
                <p>Designed to streamline report card preparation and parent-teacher meetings.</p>
                <ul>
                    <li><b>Calculate Oral Grade:</b> Use the <i>Oral Grade Calculator</i> tool under 'Data Operations' to combine homework submission rates and participation points with custom weight percentages.<br><br></li>
                    <li><b>Student Progress PDF:</b> Open a student profile and click 'Export PDF' to generate an official report card with all performance badges.<br><br></li>
                    <li><b>Analytics:</b> The 'Analytics' module allows exporting overall class homework and participation data to Excel.</li>
                </ul>
            """,
            6: """
                <h2>⚙️ Security (USB) & Data Backups</h2>
                <p>Protect your data and secure your board against unauthorized student access.</p>
                <ul>
                    <li><b>USB Dongle Key:</b> Register any blank USB drive under 'Change PIN' (Settings). The system will unlock automatically whenever the USB key is plugged in.<br><br></li>
                    <li><b>Portable Backup:</b> Export your database to a USB drive using 'Export Backup' to transfer your seating charts and classes between home and school computers seamlessly.</li>
                </ul>
            """,
            7: """
                <h2>💻 Developer & Contact Info</h2>
                <p>Class Tool is developed to improve classroom interaction and reduce administrative workload for teachers.</p>
                <ul>
                    <li><b>Developer:</b> Ammar Yakşi<br><br></li>
                    <li><b>Instagram:</b> @ammar_yksi011<br><br></li>
                    <li><b>GitHub Repo:</b> github.com/teacherhocaefendi/ClassTool<br><br></li>
                </ul>
                <p>For questions, suggestions, or feedback, feel free to reach out via the contacts above.</p>
            """
        }

    def retranslate_ui(self):
        self.lbl_topics.setText(LanguageService.get("guide_topics_title"))
        self.load_topics()
        self.refresh_theme()