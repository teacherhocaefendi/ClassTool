import json
import urllib.request
from PyQt6.QtCore import QThread, pyqtSignal

# PyCharm'ın dizini rahat bulabilmesi için sys.path importu:
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_VERSION
# GitHub kullanıcı adın ve repo adınla burayı güncelleyeceksin:
# Örn: https://raw.githubusercontent.com/ammar/ClassTool/main/version.json
GITHUB_USERNAME = "teacherhocaefendi"  # Buraya GitHub kullanıcı adını yaz
REPO_NAME = "ClassTool"            # Reponun tam adı

UPDATE_CHECK_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/version.json"


class UpdateCheckWorker(QThread):
    """Arka planda GitHub üzerinden yeni sürüm kontrolü yapar."""
    update_available = pyqtSignal(dict)
    no_update = pyqtSignal()
    error = pyqtSignal(str)

    def run(self):
        try:
            req = urllib.request.Request(
                UPDATE_CHECK_URL,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    remote_version = data.get("version", "1.0.0")

                    if self.is_newer_version(remote_version, APP_VERSION):
                        self.update_available.emit(data)
                    else:
                        self.no_update.emit()
        except Exception as e:
            # İnternet olmaması veya repoya ulaşılamaması durumunda uygulamanın çökmesini engeller
            self.error.emit(str(e))

    @staticmethod
    def is_newer_version(remote, current):
        """Semantik sürüm karşılaştırması yapar (Örn: "1.1.0" > "1.0.0")."""
        try:
            r_parts = [int(x) for x in remote.split('.')]
            c_parts = [int(x) for x in current.split('.')]
            return r_parts > c_parts
        except Exception:
            return False