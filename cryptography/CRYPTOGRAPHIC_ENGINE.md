# The Cryptographic Engine - Branch Documentation

## Overview

The `the-cryptographic-engine` branch introduces the core cryptographic module for the Secure Digital Vault project. This module implements industry-standard encryption, key derivation, and hashing algorithms to provide secure data protection.

## What's New

### Files Added

1. **`vault_crypto.py`** - Main cryptographic engine module
2. **`test_vault_crypto.py`** - Comprehensive test suite

## Core Components

### VaultCrypto Class

The main class that handles all cryptographic operations in the vault.

#### Key Features

- **AES-256-GCM Encryption**: Authenticated encryption providing both confidentiality and integrity
- **PBKDF2 Key Derivation**: Converts user passwords into cryptographic keys with 100,000 iterations
- **SHA-256 Hashing**: File fingerprinting for integrity verification
- **Nonce Management**: Secure random nonce generation for each encryption operation

#### Cryptographic Constants

```python
KEY_SIZE = 32           # 256 bits for AES-256
NONCE_SIZE = 12         # 96 bits for GCM
SALT_SIZE = 32          # 256 bits for PBKDF2
TAG_SIZE = 16           # 128 bits for GCM authentication tag
PBKDF2_ITERATIONS = 100_000  # Iterations for key derivation
```

## API Reference

### Key Generation

```python
# Generate a random salt
salt = VaultCrypto.generate_salt()

# Derive a key from password and salt
key = VaultCrypto.generate_key(password="MyPassword", salt=salt)
```

### Encryption

```python
# Encrypt a file
ciphertext, nonce, _ = VaultCrypto.encrypt_file(
    file_bytes=file_data,
    key=key
)
```

**Returns:**
- `ciphertext`: Encrypted data with GCM tag
- `nonce`: Random nonce used for encryption (needed for decryption)
- `_`: Authentication tag (embedded in ciphertext)

### Decryption

```python
# Decrypt a file
original_data = VaultCrypto.decrypt_file(
    ciphertext=ciphertext,
    key=key,
    nonce=nonce
)
```

**Important:** If the GCM tag verification fails, an exception is raised, preventing use of tampered data.

### File Hashing

```python
# Generate SHA-256 hash of a file
file_hash = VaultCrypto.generate_file_hash(file_bytes=file_data)

# Verify file integrity
is_valid = crypto.verify_file_integrity(file_data, original_hash)
```

## Security Properties

### GCM Mode Benefits

- **Authenticated Encryption**: Detects any modification to the ciphertext
- **Nonce-Based**: Each encryption with the same key uses a unique nonce
- **Fail-Safe**: Invalid tags cause decryption to raise an exception

### PBKDF2 Key Derivation

- **100,000 Iterations**: Resists brute-force password attacks
- **SHA-256 Based**: Uses industry-standard hash function
- **Salted**: Random salt prevents rainbow table attacks

### Integrity Verification

- **SHA-256 Hashing**: Creates a cryptographic fingerprint
- **Change Detection**: Any bit change in the file produces different hash
- **Tampering Prevention**: Used alongside GCM for defense-in-depth

## Example Usage

### Complete Encryption/Decryption Workflow

```python
from vault_crypto import VaultCrypto

# Initialize crypto engine
crypto = VaultCrypto()

# Step 1: Generate encryption key from password
password = "MySecurePassword123!"
salt = crypto.generate_salt()
key = crypto.generate_key(password, salt)

# Step 2: Generate file hash for integrity
file_data = b"Confidential document content"
original_hash = crypto.generate_file_hash(file_data)

# Step 3: Encrypt the file
ciphertext, nonce, _ = crypto.encrypt_file(file_data, key)

# Step 4: Decrypt the file
decrypted_data = crypto.decrypt_file(ciphertext, key, nonce)

# Step 5: Verify integrity
is_valid = crypto.verify_file_integrity(decrypted_data, original_hash)
assert is_valid, "File integrity check failed!"
```

### Detecting Tampering

```python
# If someone tampers with the ciphertext...
tampered_ciphertext = bytearray(ciphertext)
tampered_ciphertext[0] ^= 0xFF  # Flip bits

# Decryption will fail automatically
try:
    crypto.decrypt_file(bytes(tampered_ciphertext), key, nonce)
except ValueError as e:
    print(f"Tampering detected: {e}")
```

## Dependencies

```
cryptography>=41.0.0
pytest>=7.0.0  # For running tests
```

Install with:
```bash
pip install cryptography pytest
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest test_vault_crypto.py -v

# Run specific test class
pytest test_vault_crypto.py::TestVaultCryptoEncryption -v

# Run with coverage
pytest test_vault_crypto.py --cov=vault_crypto
```

### Test Coverage

- **Key Generation**: Salt generation, key derivation, consistency, error handling
- **Encryption**: Basic encryption, nonce handling, empty files, invalid inputs
- **Decryption**: Basic decryption, wrong key detection, tampering detection
- **Hashing**: Hash generation, consistency, file verification
- **Integration**: Full workflows, large files, end-to-end security

## Security Considerations

### Best Practices

1. **Generate Unique Salt**: Always use a unique salt for each password
2. **Store Salt**: Salt can be stored unencrypted alongside ciphertext
3. **Unique Nonce**: Each encryption with the same key MUST use a unique nonce
4. **Store Nonce**: Nonce must be transmitted with ciphertext
5. **Key Management**: Keys should be kept in memory and never logged

### Potential Risks

- **Nonce Reuse**: Reusing a nonce with the same key completely breaks GCM security
- **Key Exposure**: If an encryption key is compromised, all ciphertexts using it are insecure
- **Weak Passwords**: Users should use strong passwords for key derivation

## Future Enhancements

- [ ] Key rotation mechanism
- [ ] Key wrapping for at-rest key storage
- [ ] Hardware security module (HSM) integration
- [ ] Compliance with additional standards (FIPS 140-2, etc.)
- [ ] Performance optimizations for streaming large files

## Contributing

When working with this cryptographic code:

1. Never modify the cryptographic algorithms without thorough security review
2. Run all tests before committing changes
3. Add tests for any new cryptographic functionality
4. Document security implications of changes
5. Follow the existing code style and structure

## References

- [NIST SP 800-132: PBKDF2](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-132.pdf)
- [RFC 5116: AEAD Interface](https://tools.ietf.org/html/rfc5116)
- [The Cryptography Handbook](https://cryptography.io/)
- [GCM Mode Security Properties](https://en.wikipedia.org/wiki/Galois/Counter_Mode)
