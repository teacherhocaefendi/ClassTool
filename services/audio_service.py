from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, QTimer


class AudioService:
    _player = None
    _audio_output = None

    @classmethod
    def init_audio(cls):
        if cls._player is None:
            cls._player = QMediaPlayer()
            cls._audio_output = QAudioOutput()
            cls._player.setAudioOutput(cls._audio_output)
            cls._audio_output.setVolume(0.8)  # %80 Ses Seviyesi

    @classmethod
    def play_beep(cls, frequency=800, duration_ms=200):
        """Sistem uyarı sesi üretir (Harici MP3 gerektirmez)."""
        try:
            from PyQt6.QtWidgets import QApplication
            QApplication.beep()
        except Exception:
            pass


audio = AudioService()