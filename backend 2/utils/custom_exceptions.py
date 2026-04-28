class VaultError(Exception):
    pass


class ValidationError(VaultError):
    pass


class AuthenticationError(VaultError):
    pass


class AuthorizationError(VaultError):
    pass


class FileOperationError(VaultError):
    pass


class EncryptionError(VaultError):
    pass