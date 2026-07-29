import hashlib
import base64
from cryptography.fernet import Fernet


def hash_pin(pin: str) -> str:
    """Hashes a PIN using SHA-256 for local verification."""
    return hashlib.sha256(pin.encode('utf-8')).hexdigest()


def verify_pin(stored_hash: str, provided_pin: str) -> bool:
    """Verifies a provided PIN against the stored hash."""
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

        # Zaten şifreli mi kontrol etmek için deneme yapalım, değilse şifreleyelim
        try:
            fernet.decrypt(data)
            # Zaten şifreliymiş, tekrar şifreleme
            return
        except Exception:
            pass

        encrypted = fernet.encrypt(data)
        with open(file_path, 'wb') as f:
            f.write(encrypted)
    except Exception as e:
        print(f"Encryption error: {e}")


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
        # Dosya zaten şifresizse veya ilk kez oluşturuluyorsa pas geç
        pass