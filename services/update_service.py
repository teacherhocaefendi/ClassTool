import os
import sys
import json
import time  # <-- YENİ EKLENDİ
import urllib.request
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal
import ctypes

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_VERSION

GITHUB_USERNAME = "teacherhocaefendi"
REPO_NAME = "ClassTool"

UPDATE_CHECK_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/version.json"


class UpdateCheckWorker(QThread):
    """Arka planda GitHub üzerinden yeni sürüm kontrolü yapar."""
    update_available = pyqtSignal(dict)
    no_update = pyqtSignal()
    error = pyqtSignal(str)

    def run(self):
        try:
            # Önbelleği (Cache) baypass etmek için dinamik timestamp ekliyoruz
            cache_buster = int(time.time())
            url_with_nocache = f"{UPDATE_CHECK_URL}?nocache={cache_buster}"

            req = urllib.request.Request(
                url_with_nocache,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Cache-Control': 'no-cache'
                }
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    # 1.2.0 sabit değerini kaldırdık, boş string yaptık
                    remote_version = data.get("version", "").strip()

                    if remote_version and self.is_newer_version(remote_version, APP_VERSION):
                        self.update_available.emit(data)
                    else:
                        self.no_update.emit()
        except Exception as e:
            self.error.emit(str(e))

    @staticmethod
    def is_newer_version(remote, current):
        try:
            r_parts = [int(x) for x in remote.split('.')]
            c_parts = [int(x) for x in current.split('.')]
            return r_parts > c_parts
        except Exception:
            return False


# ... (Dosyanın geri kalanı olan UpdateDownloaderWorker ve apply_update_and_restart kısımları aynı kalacak) ...


class UpdateDownloaderWorker(QThread):
    """Yeni sürüm EXE dosyasını arka planda yüzde bildirimi yaparak indirir."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, download_url, target_path, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.target_path = target_path

    def run(self):
        try:
            req = urllib.request.Request(
                self.download_url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                total_size = int(response.info().get('Content-Length', 0))
                bytes_downloaded = 0
                block_size = 8192

                with open(self.target_path, 'wb') as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        bytes_downloaded += len(buffer)
                        f.write(buffer)
                        if total_size > 0:
                            percent = int((bytes_downloaded / total_size) * 100)
                            self.progress.emit(percent)

            self.finished.emit(self.target_path)
        except Exception as e:
            self.error.emit(str(e))


def apply_update_and_restart(installer_path):
    """
    Inno Setup ile oluşturulmuş Kurulum EXE'sini (Setup) arka planda yönetici yetkisiyle çalıştırır.
    """
    if not getattr(sys, 'frozen', False):
        print(f"[TEST MODU] Setup dosyası indirildi: {installer_path}. EXE modunda Inno Setup tetiklenecekti.")
        return

    # Inno Setup Parametreleri
    args = '/SILENT /SUPPRESSMSGBOXES /NORESTART'

    try:
        # Windows API (ShellExecuteW) kullanarak 'runas' ile yönetici izni istiyoruz
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",            # Yönetici haklarıyla çalıştır
            installer_path,     # Çalıştırılacak Setup.exe
            args,               # Parametreler (/SILENT vs.)
            None,
            1                   # SW_SHOWNORMAL
        )
        # Mevcut uygulamayı kapat ki Inno Setup dosyaları değiştirebilsin
        sys.exit(0)
    except Exception as e:
        print(f"Yönetici yetkisi ile çalıştırma hatası: {e}")