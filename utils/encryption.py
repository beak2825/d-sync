"""Encryption/decryption utilities for d-sync"""

from cryptography.fernet import Fernet
from pathlib import Path
import os
from .config import ENCRYPTION_KEY_FILE


class EncryptionManager:
    """Manages file encryption and decryption"""

    def __init__(self):
        self.key_file = ENCRYPTION_KEY_FILE
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)

    def _load_or_create_key(self) -> bytes:
        """Load encryption key from file or create a new one"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Secure file permissions
            os.chmod(self.key_file, 0o600)
            return key

    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using Fernet symmetric encryption"""
        return self.cipher.encrypt(data)

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using Fernet symmetric decryption"""
        return self.cipher.decrypt(encrypted_data)

    def encrypt_file(self, file_path: Path) -> bytes:
        """Encrypt entire file and return encrypted bytes"""
        with open(file_path, 'rb') as f:
            data = f.read()
        return self.encrypt_data(data)

    def decrypt_file(self, encrypted_data: bytes, output_path: Path):
        """Decrypt data and write to file"""
        decrypted_data = self.decrypt_data(encrypted_data)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
