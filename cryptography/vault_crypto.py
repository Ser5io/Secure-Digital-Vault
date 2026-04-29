"""
VaultCrypto: The Cryptographic Engine
======================================
Handles all encryption/decryption operations for the Secure Digital Vault.

This module implements:
- AES-256 encryption in GCM (Galois/Counter Mode) for authenticated encryption
- PBKDF2 key derivation for converting passwords to encryption keys
- File hashing with SHA-256 for integrity verification
- Secure nonce/IV generation

Security Notes:
- GCM mode provides both confidentiality and authenticity
- PBKDF2 uses 100,000 iterations to resist brute-force attacks
- All sensitive operations are constant-time resistant where possible
"""

import os
import hashlib
import hmac
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend


class VaultCrypto:
    """
    Core cryptographic engine for the Secure Digital Vault.
    
    Handles all encryption, decryption, and hashing operations using
    industry-standard cryptographic algorithms.
    """
    
    # Cryptographic Constants
    KEY_SIZE = 32  # 256 bits for AES-256
    NONCE_SIZE = 12  # 96 bits (12 bytes) - standard for GCM
    SALT_SIZE = 32  # 256 bits for PBKDF2 salt
    TAG_SIZE = 16  # 128 bits - GCM authentication tag
    PBKDF2_ITERATIONS = 100_000  # Iterations for key derivation
    
    def __init__(self):
        """Initialize the VaultCrypto engine."""
        self.backend = default_backend()
    
    @staticmethod
    def generate_salt() -> bytes:
        """
        Generate a cryptographically secure random salt.
        
        Returns:
            bytes: A 256-bit (32-byte) random salt
        """
        return os.urandom(VaultCrypto.SALT_SIZE)
    
    @staticmethod
    def generate_nonce() -> bytes:
        """
        Generate a cryptographically secure random nonce (Number Used Once).
        
        Returns:
            bytes: A 96-bit (12-byte) random nonce
        
        Note:
            Each encryption operation must use a unique nonce with the same key.
            Reusing a nonce with the same key completely breaks GCM security.
        """
        return os.urandom(VaultCrypto.NONCE_SIZE)
    
    @staticmethod
    def generate_key(password: str, salt: bytes) -> bytes:
        """
        Derive a 256-bit encryption key from a password using PBKDF2.
        
        Args:
            password (str): The user's password or passphrase
            salt (bytes): A random salt (should be generated with generate_salt())
        
        Returns:
            bytes: A 256-bit (32-byte) encryption key
        
        Raises:
            ValueError: If password is empty or salt is invalid
            TypeError: If inputs are not of the correct type
        
        Security Considerations:
            - PBKDF2 with 100,000 iterations provides resistance to brute-force attacks
            - Different salts produce different keys from the same password
            - The salt should be unique for each password
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        if not isinstance(salt, bytes) or len(salt) != VaultCrypto.SALT_SIZE:
            raise ValueError(f"Salt must be {VaultCrypto.SALT_SIZE} bytes")
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=VaultCrypto.KEY_SIZE,
            salt=salt,
            iterations=VaultCrypto.PBKDF2_ITERATIONS,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode('utf-8'))
        return key
    
    @staticmethod
    def encrypt_file(file_bytes: bytes, key: bytes, nonce: bytes = None) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt file data using AES-256-GCM.
        
        Args:
            file_bytes (bytes): The raw file data to encrypt
            key (bytes): The 256-bit encryption key (from generate_key())
            nonce (bytes, optional): A 96-bit nonce. If None, generates a random one.
        
        Returns:
            Tuple[bytes, bytes, bytes]: (ciphertext, nonce, tag)
                - ciphertext: Encrypted file data
                - nonce: The nonce used (needed for decryption)
                - tag: GCM authentication tag (embedded in ciphertext by cryptography library)
        
        Raises:
            ValueError: If key or file_bytes are invalid
            TypeError: If inputs are not of the correct type
        
        Security Considerations:
            - GCM mode provides both encryption and authentication
            - The returned nonce must be transmitted with the ciphertext
            - Each encryption with the same key MUST use a unique nonce
            - The authentication tag proves the ciphertext hasn't been tampered with
        """
        if not isinstance(file_bytes, bytes):
            raise TypeError("file_bytes must be bytes")
        
        if not isinstance(key, bytes) or len(key) != VaultCrypto.KEY_SIZE:
            raise ValueError(f"Key must be {VaultCrypto.KEY_SIZE} bytes")
        
        if nonce is None:
            nonce = VaultCrypto.generate_nonce()
        
        if not isinstance(nonce, bytes) or len(nonce) != VaultCrypto.NONCE_SIZE:
            raise ValueError(f"Nonce must be {VaultCrypto.NONCE_SIZE} bytes")
        
        cipher = AESGCM(key)
        
        # encrypt() returns ciphertext with GCM tag appended
        ciphertext = cipher.encrypt(nonce, file_bytes, None)
        
        return ciphertext, nonce, None  # tag is embedded in ciphertext
    
    @staticmethod
    def decrypt_file(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
        """
        Decrypt file data using AES-256-GCM.
        
        Args:
            ciphertext (bytes): The encrypted file data (with GCM tag appended)
            key (bytes): The 256-bit encryption key (must match the key used for encryption)
            nonce (bytes): The 96-bit nonce used during encryption
        
        Returns:
            bytes: The decrypted original file data
        
        Raises:
            ValueError: If key, nonce, or ciphertext are invalid
            cryptography.exceptions.InvalidTag: If the authentication tag verification fails
                (indicates the ciphertext has been tampered with)
            TypeError: If inputs are not of the correct type
        
        Security Considerations:
            - Automatic authentication tag verification ensures data integrity
            - If the tag verification fails, an exception is raised (fail-safe)
            - The nonce must be the exact nonce used during encryption
            - Decryption with a different key will fail authentication
        """
        if not isinstance(ciphertext, bytes):
            raise TypeError("ciphertext must be bytes")
        
        if not isinstance(key, bytes) or len(key) != VaultCrypto.KEY_SIZE:
            raise ValueError(f"Key must be {VaultCrypto.KEY_SIZE} bytes")
        
        if not isinstance(nonce, bytes) or len(nonce) != VaultCrypto.NONCE_SIZE:
            raise ValueError(f"Nonce must be {VaultCrypto.NONCE_SIZE} bytes")
        
        if len(ciphertext) < VaultCrypto.TAG_SIZE:
            raise ValueError("Ciphertext too short (must include GCM tag)")
        
        cipher = AESGCM(key)
        
        try:
            plaintext = cipher.decrypt(nonce, ciphertext, None)
            return plaintext
        except Exception as e:
            raise ValueError(f"Decryption failed - possible data tampering or wrong key: {str(e)}")
    
    @staticmethod
    def generate_file_hash(file_bytes: bytes) -> str:
        """
        Generate a SHA-256 cryptographic hash of file data.
        
        Args:
            file_bytes (bytes): The file data to hash
        
        Returns:
            str: Hexadecimal string representation of the SHA-256 hash
        
        Raises:
            TypeError: If file_bytes is not of the correct type
        
        Security Considerations:
            - SHA-256 produces a 256-bit (32-byte) hash
            - This hash serves as a "fingerprint" for integrity verification
            - Even a single bit change in the file produces a completely different hash
            - Useful for detecting file tampering or corruption
            - Can be stored alongside the encrypted file for integrity checks
        
        Example:
            >>> original_hash = VaultCrypto.generate_file_hash(file_data)
            >>> # ... later, after decrypt ...
            >>> new_hash = VaultCrypto.generate_file_hash(decrypted_data)
            >>> if original_hash == new_hash:
            ...     print("File integrity verified!")
        """
        if not isinstance(file_bytes, bytes):
            raise TypeError("file_bytes must be bytes")
        
        hash_obj = hashlib.sha256(file_bytes)
        return hash_obj.hexdigest()
    
    @staticmethod
    def constant_time_compare(a: bytes, b: bytes) -> bool:
        """
        Compare two byte strings in constant time.
        
        Args:
            a (bytes): First byte string
            b (bytes): Second byte string
        
        Returns:
            bool: True if equal, False otherwise
        
        Security Considerations:
            - Uses hmac.compare_digest() to prevent timing attacks
            - Timing attacks can leak information about secret data
            - This should be used when comparing cryptographic values
        """
        return hmac.compare_digest(a, b)
    
    def verify_file_integrity(self, file_bytes: bytes, expected_hash: str) -> bool:
        """
        Verify that a file hasn't been tampered with using SHA-256 hash.
        
        Args:
            file_bytes (bytes): The file data to verify
            expected_hash (str): The original hash (from generate_file_hash())
        
        Returns:
            bool: True if hashes match, False otherwise
        
        Example:
            >>> is_valid = crypto.verify_file_integrity(decrypted_data, original_hash)
        """
        current_hash = self.generate_file_hash(file_bytes)
        return self.constant_time_compare(
            current_hash.encode(),
            expected_hash.encode()
        )


# ============================================================================
# Example Usage (for testing and demonstration)
# ============================================================================

if __name__ == "__main__":
    """
    Demonstration of the VaultCrypto cryptographic engine.
    
    This shows how to:
    1. Generate a secure key from a password
    2. Encrypt file data
    3. Decrypt file data
    4. Verify file integrity
    """
    
    print("=" * 70)
    print("VaultCrypto - Cryptographic Engine Demonstration")
    print("=" * 70)
    
    # Initialize the crypto engine
    crypto = VaultCrypto()
    
    # Step 1: Generate a salt and derive a key from password
    print("\n[Step 1] Key Derivation")
    print("-" * 70)
    password = "MySecureVaultPassword123!"
    salt = crypto.generate_salt()
    print(f"Password: {password}")
    print(f"Salt (hex): {salt.hex()[:32]}...")
    
    key = crypto.generate_key(password, salt)
    print(f"Derived Key (hex): {key.hex()}")
    print(f"Key Size: {len(key)} bytes (256-bit)")
    
    # Step 2: Create sample file data
    print("\n[Step 2] Sample File Data")
    print("-" * 70)
    sample_file = b"This is confidential vault data that needs to be encrypted!"
    original_hash = crypto.generate_file_hash(sample_file)
    print(f"File Content: {sample_file.decode()}")
    print(f"Original Hash (SHA-256): {original_hash}")
    
    # Step 3: Encrypt the file
    print("\n[Step 3] File Encryption (AES-256-GCM)")
    print("-" * 70)
    ciphertext, nonce, _ = crypto.encrypt_file(sample_file, key)
    print(f"Nonce (hex): {nonce.hex()}")
    print(f"Ciphertext (hex): {ciphertext.hex()[:64]}...")
    print(f"Ciphertext Size: {len(ciphertext)} bytes")
    
    # Step 4: Decrypt the file
    print("\n[Step 4] File Decryption")
    print("-" * 70)
    decrypted_data = crypto.decrypt_file(ciphertext, key, nonce)
    print(f"Decrypted Content: {decrypted_data.decode()}")
    
    # Step 5: Verify integrity
    print("\n[Step 5] Integrity Verification")
    print("-" * 70)
    decrypted_hash = crypto.generate_file_hash(decrypted_data)
    print(f"Decrypted Hash (SHA-256): {decrypted_hash}")
    
    is_valid = crypto.verify_file_integrity(decrypted_data, original_hash)
    print(f"Hashes Match: {is_valid}")
    print(f"File Integrity: {'✓ VERIFIED' if is_valid else '✗ FAILED'}")
    
    # Step 6: Security demonstration - show tampering detection
    print("\n[Step 6] Tampering Detection")
    print("-" * 70)
    tampered_ciphertext = bytearray(ciphertext)
    tampered_ciphertext[0] ^= 0xFF  # Flip all bits in first byte
    
    print("Attempting to decrypt tampered ciphertext...")
    try:
        crypto.decrypt_file(bytes(tampered_ciphertext), key, nonce)
        print("✗ SECURITY FAILURE: Tampered data was accepted!")
    except ValueError as e:
        print(f"✓ SECURITY SUCCESS: Tampering detected!")
        print(f"   Error: {str(e)[:50]}...")
    
    print("\n" + "=" * 70)
    print("Demonstration Complete")
    print("=" * 70)
