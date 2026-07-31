import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QMessageBox
from PyQt6.QtCore import Qt
from services.update_service import UpdateDownloaderWorker, apply_update_and_restart


class UpdateProgressDialog(QDialog):
    def __init__(self, download_url, version_str, changelog, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.version_str = version_str
        self.changelog = changelog

        self.setWindowTitle(f"🚀 Güncelleme Yükleniyor - v{version_str}")
        self.setFixedSize(420, 200)
        # Kullanıcının indirme bitmeden pencereyi kapatmasını engelle
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        self.setup_ui()
        self.start_download()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        self.lbl_status = QLabel(f"<b>ClassTool v{self.version_str} indiriliyor...</b>")
        self.lbl_status.setStyleSheet("font-size: 14px; color: #0052CC;")
        layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #DFE1E6; 
                border-radius: 6px; 
                text-align: center; 
                font-weight: bold; 
                height: 25px;
            }
            QProgressBar::chunk { 
                background-color: #36B37E; 
                border-radius: 4px; 
            }
        """)
        layout.addWidget(self.progress_bar)

        self.lbl_info = QLabel("Lütfen indirme tamamlanana kadar uygulamayı kapatmayın.")
        self.lbl_info.setStyleSheet("font-size: 12px; color: #5E6C84;")
        layout.addWidget(self.lbl_info)

    def start_download(self):
        # Dosyayı kullanıcının İndirilenler (Downloads) klasörüne indiriyoruz
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        target_path = os.path.join(downloads_folder, f"ClassTool_v{self.version_str}.exe")

        self.downloader = UpdateDownloaderWorker(self.download_url, target_path)
        # Yüzde değiştikçe progress bar'ı güncelle
        self.downloader.progress.connect(self.progress_bar.setValue)
        self.downloader.finished.connect(self.on_download_finished)
        self.downloader.error.connect(self.on_download_error)
        self.downloader.start()

    def on_download_finished(self, downloaded_file):
        self.lbl_status.setText("<b>İndirme Tamamlandı! Otomatik kuruluyor...</b>")
        self.progress_bar.setValue(100)

        # 1. adımda yazdığımız script fonksiyonunu çağırıp uygulamayı güncelliyoruz
        apply_update_and_restart(downloaded_file)

    def on_download_error(self, err_msg):
        QMessageBox.critical(self, "İndirme Hatası", f"Güncelleme indirilirken bir hata oluştu:\n{err_msg}")
        self.reject()