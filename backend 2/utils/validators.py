import os
from utils.custom_exceptions import ValidationError

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

MAGIC_BYTES = {
    ".pdf": [b"%PDF"],
    ".png": [b"\x89PNG\r\n\x1a\n"],
    ".jpg": [b"\xff\xd8\xff"],
    ".jpeg": [b"\xff\xd8\xff"],
    ".txt": None
}


def validate_user_id(user_id):
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValidationError("Invalid user ID")


def validate_file_id(file_id):
    if not isinstance(file_id, int) or file_id <= 0:
        raise ValidationError("Invalid file ID")


def validate_password(password):
    if not isinstance(password, str):
        raise ValidationError("Invalid password")

    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")

    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one number")

    if not any(char.isalpha() for char in password):
        raise ValidationError("Password must contain at least one letter")


def validate_file_path(file_path):
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValidationError("Invalid file path")

    normalized_path = os.path.normpath(file_path)

    if ".." in normalized_path.split(os.sep):
        raise ValidationError("Path traversal attempt detected")

    if not os.path.isfile(normalized_path):
        raise ValidationError("File does not exist")

    file_size = os.path.getsize(normalized_path)

    if file_size == 0:
        raise ValidationError("Empty file is not allowed")

    if file_size > MAX_FILE_SIZE:
        raise ValidationError("File too large")

    _, ext = os.path.splitext(normalized_path)
    ext = ext.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("Invalid file type")

    validate_magic_bytes(normalized_path, ext)


def validate_magic_bytes(file_path, ext):
    expected_signatures = MAGIC_BYTES.get(ext)

  
    if expected_signatures is None:
        return

    with open(file_path, "rb") as file:
        file_start = file.read(16)

    if not any(file_start.startswith(signature) for signature in expected_signatures):
        raise ValidationError("File content does not match file extension")