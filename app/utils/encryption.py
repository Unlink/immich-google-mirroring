"""
Encryption utilities for sensitive data
"""
from cryptography.fernet import Fernet
import os
import base64
import hashlib


class EncryptionHelper:
    """Helper for encrypting/decrypting sensitive data"""
    
    def __init__(self):
        secret_key = os.getenv("APP_SECRET_KEY", "changeme-generate-random-key")
        # Derive a proper Fernet key from the secret
        key_bytes = hashlib.sha256(secret_key.encode()).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext to base64 string"""
        if not plaintext:
            return ""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt base64 string to plaintext"""
        if not ciphertext:
            return ""
        decrypted = self.fernet.decrypt(ciphertext.encode())
        return decrypted.decode()


# Global instance
encryption = EncryptionHelper()
