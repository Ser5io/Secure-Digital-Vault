"""
Unit Tests for VaultCrypto Module
==================================
Comprehensive test suite for the cryptographic engine.
"""

import pytest
import os
from vault_crypto import VaultCrypto


class TestVaultCryptoKeyGeneration:
    """Test password-to-key derivation functionality."""
    
    def test_generate_salt(self):
        """Test that generate_salt produces correct size random salts."""
        salt1 = VaultCrypto.generate_salt()
        salt2 = VaultCrypto.generate_salt()
        
        assert isinstance(salt1, bytes)
        assert isinstance(salt2, bytes)
        assert len(salt1) == 32
        assert len(salt2) == 32
        assert salt1 != salt2  # Different salts
    
    def test_generate_nonce(self):
        """Test that generate_nonce produces correct size random nonces."""
        nonce1 = VaultCrypto.generate_nonce()
        nonce2 = VaultCrypto.generate_nonce()
        
        assert isinstance(nonce1, bytes)
        assert isinstance(nonce2, bytes)
        assert len(nonce1) == 12
        assert len(nonce2) == 12
        assert nonce1 != nonce2  # Different nonces
    
    def test_generate_key_valid(self):
        """Test valid key generation."""
        password = "TestPassword123!"
        salt = VaultCrypto.generate_salt()
        
        key = VaultCrypto.generate_key(password, salt)
        
        assert isinstance(key, bytes)
        assert len(key) == 32  # 256-bit key
    
    def test_generate_key_consistency(self):
        """Test that same password and salt always produce same key."""
        password = "TestPassword123!"
        salt = VaultCrypto.generate_salt()
        
        key1 = VaultCrypto.generate_key(password, salt)
        key2 = VaultCrypto.generate_key(password, salt)
        
        assert key1 == key2
    
    def test_generate_key_different_salts(self):
        """Test that different salts produce different keys."""
        password = "TestPassword123!"
        salt1 = VaultCrypto.generate_salt()
        salt2 = VaultCrypto.generate_salt()
        
        key1 = VaultCrypto.generate_key(password, salt1)
        key2 = VaultCrypto.generate_key(password, salt2)
        
        assert key1 != key2
    
    def test_generate_key_empty_password(self):
        """Test that empty password raises ValueError."""
        salt = VaultCrypto.generate_salt()
        
        with pytest.raises(ValueError, match="Password cannot be empty"):
            VaultCrypto.generate_key("", salt)
    
    def test_generate_key_invalid_salt(self):
        """Test that invalid salt raises ValueError."""
        password = "TestPassword123!"
        
        with pytest.raises(ValueError, match="Salt must be 32 bytes"):
            VaultCrypto.generate_key(password, b"short")


class TestVaultCryptoEncryption:
    """Test file encryption/decryption functionality."""
    
    @pytest.fixture
    def crypto_setup(self):
        """Set up crypto engine with key for testing."""
        password = "TestPassword123!"
        salt = VaultCrypto.generate_salt()
        key = VaultCrypto.generate_key(password, salt)
        return VaultCrypto(), key, password, salt
    
    def test_encrypt_file_basic(self, crypto_setup):
        """Test basic file encryption."""
        crypto, key, _, _ = crypto_setup
        file_data = b"Test file content"
        
        ciphertext, nonce, _ = crypto.encrypt_file(file_data, key)
        
        assert isinstance(ciphertext, bytes)
        assert isinstance(nonce, bytes)
        assert len(nonce) == 12
        assert ciphertext != file_data
        assert len(ciphertext) >= len(file_data)
    
    def test_encrypt_file_with_nonce(self, crypto_setup):
        """Test encryption with provided nonce."""
        crypto, key, _, _ = crypto_setup
        file_data = b"Test file content"
        nonce = VaultCrypto.generate_nonce()
        
        ciphertext, returned_nonce, _ = crypto.encrypt_file(file_data, key, nonce)
        
        assert returned_nonce == nonce
    
    def test_encrypt_different_output(self, crypto_setup):
        """Test that same file encrypted with different nonces gives different output."""
        crypto, key, _, _ = crypto_setup
        file_data = b"Test file content"
        nonce1 = VaultCrypto.generate_nonce()
        nonce2 = VaultCrypto.generate_nonce()
        
        ciphertext1, _, _ = crypto.encrypt_file(file_data, key, nonce1)
        ciphertext2, _, _ = crypto.encrypt_file(file_data, key, nonce2)
        
        assert ciphertext1 != ciphertext2
    
    def test_encrypt_empty_file(self, crypto_setup):
        """Test encryption of empty file."""
        crypto, key, _, _ = crypto_setup
        file_data = b""
        
        ciphertext, nonce, _ = crypto.encrypt_file(file_data, key)
        
        assert isinstance(ciphertext, bytes)
        assert len(nonce) == 12
    
    def test_encrypt_invalid_key(self, crypto_setup):
        """Test that invalid key raises ValueError."""
        crypto, _, _, _ = crypto_setup
        file_data = b"Test file content"
        
        with pytest.raises(ValueError, match="Key must be 32 bytes"):
            crypto.encrypt_file(file_data, b"short_key")
    
    def test_decrypt_file_basic(self, crypto_setup):
        """Test basic file decryption."""
        crypto, key, _, _ = crypto_setup
        original_data = b"Test file content for decryption"
        
        ciphertext, nonce, _ = crypto.encrypt_file(original_data, key)
        decrypted_data = crypto.decrypt_file(ciphertext, key, nonce)
        
        assert decrypted_data == original_data
    
    def test_decrypt_wrong_key(self, crypto_setup):
        """Test that decryption with wrong key fails."""
        crypto, key, _, salt = crypto_setup
        original_data = b"Test file content"
        
        ciphertext, nonce, _ = crypto.encrypt_file(original_data, key)
        
        # Generate a different key
        wrong_key = VaultCrypto.generate_key("DifferentPassword", salt)
        
        with pytest.raises(ValueError, match="Decryption failed"):
            crypto.decrypt_file(ciphertext, wrong_key, nonce)
    
    def test_decrypt_wrong_nonce(self, crypto_setup):
        """Test that decryption with wrong nonce fails."""
        crypto, key, _, _ = crypto_setup
        original_data = b"Test file content"
        
        ciphertext, _, _ = crypto.encrypt_file(original_data, key)
        wrong_nonce = VaultCrypto.generate_nonce()
        
        with pytest.raises(ValueError, match="Decryption failed"):
            crypto.decrypt_file(ciphertext, key, wrong_nonce)
    
    def test_decrypt_tampered_ciphertext(self, crypto_setup):
        """Test that tampered ciphertext is detected."""
        crypto, key, _, _ = crypto_setup
        original_data = b"Test file content"
        
        ciphertext, nonce, _ = crypto.encrypt_file(original_data, key)
        
        # Tamper with ciphertext
        tampered = bytearray(ciphertext)
        tampered[0] ^= 0xFF
        
        with pytest.raises(ValueError, match="Decryption failed"):
            crypto.decrypt_file(bytes(tampered), key, nonce)


class TestVaultCryptoHashing:
    """Test file hashing and integrity verification."""
    
    def test_generate_file_hash_basic(self):
        """Test basic file hashing."""
        file_data = b"Test file content"
        hash_result = VaultCrypto.generate_file_hash(file_data)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64  # SHA-256 hex is 64 chars
        assert all(c in '0123456789abcdef' for c in hash_result)
    
    def test_generate_file_hash_consistency(self):
        """Test that same file always produces same hash."""
        file_data = b"Test file content"
        
        hash1 = VaultCrypto.generate_file_hash(file_data)
        hash2 = VaultCrypto.generate_file_hash(file_data)
        
        assert hash1 == hash2
    
    def test_generate_file_hash_different_files(self):
        """Test that different files produce different hashes."""
        file_data1 = b"Test file content 1"
        file_data2 = b"Test file content 2"
        
        hash1 = VaultCrypto.generate_file_hash(file_data1)
        hash2 = VaultCrypto.generate_file_hash(file_data2)
        
        assert hash1 != hash2
    
    def test_generate_file_hash_empty_file(self):
        """Test hashing of empty file."""
        file_data = b""
        hash_result = VaultCrypto.generate_file_hash(file_data)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64
    
    def test_verify_file_integrity_valid(self):
        """Test integrity verification with valid hash."""
        crypto = VaultCrypto()
        file_data = b"Test file content"
        
        original_hash = crypto.generate_file_hash(file_data)
        is_valid = crypto.verify_file_integrity(file_data, original_hash)
        
        assert is_valid is True
    
    def test_verify_file_integrity_invalid(self):
        """Test integrity verification fails with tampered file."""
        crypto = VaultCrypto()
        file_data = b"Test file content"
        
        original_hash = crypto.generate_file_hash(file_data)
        tampered_data = b"Tampered file content"
        is_valid = crypto.verify_file_integrity(tampered_data, original_hash)
        
        assert is_valid is False


class TestVaultCryptoIntegration:
    """Integration tests for full encryption/decryption workflow."""
    
    def test_full_workflow(self):
        """Test complete encrypt-decrypt workflow."""
        crypto = VaultCrypto()
        password = "MySecurePassword123!"
        original_file = b"This is confidential data that must be encrypted!"
        
        # Step 1: Key generation
        salt = crypto.generate_salt()
        key = crypto.generate_key(password, salt)
        
        # Step 2: Hash original
        original_hash = crypto.generate_file_hash(original_file)
        
        # Step 3: Encrypt
        ciphertext, nonce, _ = crypto.encrypt_file(original_file, key)
        
        # Step 4: Decrypt
        decrypted_file = crypto.decrypt_file(ciphertext, key, nonce)
        
        # Step 5: Verify
        assert decrypted_file == original_file
        assert crypto.verify_file_integrity(decrypted_file, original_hash)
    
    def test_large_file_encryption(self):
        """Test encryption of a large file."""
        crypto = VaultCrypto()
        password = "TestPassword123!"
        salt = crypto.generate_salt()
        key = crypto.generate_key(password, salt)
        
        # Create a 10MB file
        large_file = os.urandom(10 * 1024 * 1024)
        
        ciphertext, nonce, _ = crypto.encrypt_file(large_file, key)
        decrypted_file = crypto.decrypt_file(ciphertext, key, nonce)
        
        assert decrypted_file == large_file


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
