from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os


class CryptoService:
    AAD = b"secure-digital-vault"

    def generate_key(self, password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=300000,
        )
        return kdf.derive(password.encode())

    def encrypt_file(self, data, key):
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)

        encrypted = aesgcm.encrypt(nonce, data, self.AAD)

        return encrypted, nonce

    def decrypt_file(self, data, key, nonce):
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, data, self.AAD)

    def generate_file_hash(self, data):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data)
        return digest.finalize().hex()