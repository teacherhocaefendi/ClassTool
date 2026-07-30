import hashlib
import base64
from cryptography.fernet import Fernet


def hash_pin(pin: str) -> str:
    """Yerel doğrulama için PIN'i SHA-256 kullanarak şifreler."""
    return hashlib.sha256(pin.encode('utf-8')).hexdigest()


def verify_pin(stored_hash: str, provided_pin: str) -> bool:
    """Verilen PIN'in saklanan hash ile eşleşip eşleşmediğini doğrular."""
    return stored_hash == hash_pin(provided_pin)


def get_fernet_key(key_str: str) -> bytes:
    """Metin anahtarını Fernet uyumlu 32-byte base64 anahtara dönüştürür."""
    key_hash = hashlib.sha256(key_str.encode()).digest()
    return base64.urlsafe_b64encode(key_hash)


def encrypt_file(file_path: str, key_str: str):
    """Dosyayı AES-256 (Fernet) ile kilitler."""
    try:
        fernet = Fernet(get_fernet_key(key_str))
        with open(file_path, 'rb') as f:
            data = f.read()

        try:
            fernet.decrypt(data)
            return  # Zaten şifreli
        except Exception:
            pass

        encrypted = fernet.encrypt(data)
        with open(file_path, 'wb') as f:
            f.write(encrypted)
    except Exception as e:
        # Circular import'u önlemek için logger'ı sadece ihtiyaç anında içeri aktarıyoruz
        from services.theme_and_log_service import logger
        logger.error(f"Şifreleme hatası: {e}")


def decrypt_file(file_path: str, key_str: str):
    """AES-256 ile kilitlenmiş dosyanın kilidini açar."""
    try:
        fernet = Fernet(get_fernet_key(key_str))
        with open(file_path, 'rb') as f:
            data = f.read()

        decrypted = fernet.decrypt(data)
        with open(file_path, 'wb') as f:
            f.write(decrypted)
    except Exception:
        pass