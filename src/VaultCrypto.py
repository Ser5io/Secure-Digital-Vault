import os
import hashlib
import hmac
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class VaultCrypto:
    """
    Core cryptographic engine for the Secure Digital Vault.
    Handles AES-256-GCM encryption and PBKDF2 key derivation.
    """
    
    KEY_SIZE = 32  
    NONCE_SIZE = 12
    SALT_SIZE = 32
    PBKDF2_ITERATIONS = 100_000
    
    @staticmethod
    def generate_salt() -> bytes:
        return os.urandom(VaultCrypto.SALT_SIZE)
    
    @staticmethod
    def generate_nonce() -> bytes:
        return os.urandom(VaultCrypto.NONCE_SIZE)
    
    @staticmethod
    def generate_key(password: str, salt: bytes) -> bytes:
        if not password:
            raise ValueError("Password cannot be empty")
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=VaultCrypto.KEY_SIZE,
            salt=salt,
            iterations=VaultCrypto.PBKDF2_ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))
    
    @staticmethod
    def encrypt_file(file_bytes: bytes, key: bytes, nonce: bytes = None) -> Tuple[bytes, bytes, bytes]:
        if nonce is None:
            nonce = VaultCrypto.generate_nonce()
        
        cipher = AESGCM(key)
        # encrypt() returns ciphertext with GCM tag appended
        ciphertext = cipher.encrypt(nonce, file_bytes, None)
        return ciphertext, nonce, None
    
    @staticmethod
    def decrypt_file(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
        cipher = AESGCM(key)
        try:
            return cipher.decrypt(nonce, ciphertext, None)
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def generate_file_hash(file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    def verify_file_integrity(self, file_bytes: bytes, expected_hash: str) -> bool:
        current_hash = self.generate_file_hash(file_bytes)
        return hmac.compare_digest(current_hash.encode(), expected_hash.encode())
