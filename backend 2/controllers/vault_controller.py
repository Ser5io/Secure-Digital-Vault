import logging

from utils.validators import (
    validate_user_id,
    validate_file_id,
    validate_password,
    validate_file_path,
)
from utils.custom_exceptions import AuthorizationError, FileOperationError


logging.basicConfig(
    filename="vault.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class VaultController:
    def __init__(self, auth, crypto, storage):
        self.auth = auth
        self.crypto = crypto
        self.storage = storage

    def process_upload(self, user_id, file_path, password):
        try:
            logger.info("Upload started for user_id=%s", user_id)

            validate_user_id(user_id)
            validate_password(password)
            validate_file_path(file_path)

            salt = self.auth.get_user_salt(user_id)
            key = self.crypto.generate_key(password, salt)

            file_bytes = self.storage.read_raw_file(file_path)

            if len(file_bytes) > MAX_FILE_SIZE:
                logger.warning("Upload failed: file too large for user_id=%s", user_id)
                return {
                    "status": "error",
                    "message": "File too large"
                }

            file_hash = self.crypto.generate_file_hash(file_bytes)

            encrypted, nonce = self.crypto.encrypt_file(file_bytes, key)

            file_id = self.storage.save_to_disk(
                user_id,
                file_path,
                encrypted,
                nonce,
                file_hash
            )

            logger.info("Upload successful for user_id=%s, file_id=%s", user_id, file_id)

            return {
                "status": "success",
                "message": "File uploaded successfully",
                "file_id": file_id
            }

        except Exception as e:
            logger.error("Upload failed for user_id=%s: %s", user_id, str(e))

            return {
                "status": "error",
                "message": "Upload failed"
            }

    def process_download(self, user_id, file_id, password):
        try:
            logger.info("Download started for user_id=%s, file_id=%s", user_id, file_id)

            validate_user_id(user_id)
            validate_file_id(file_id)
            validate_password(password)

            file_data = self.storage.fetch_from_disk(file_id)

            if not file_data:
                raise FileOperationError("File not found")

            if file_data["owner_id"] != user_id:
                logger.warning(
                    "Unauthorized download attempt: user_id=%s, file_id=%s",
                    user_id,
                    file_id
                )
                raise AuthorizationError("Not allowed")

            salt = self.auth.get_user_salt(user_id)
            key = self.crypto.generate_key(password, salt)

            decrypted = self.crypto.decrypt_file(
                file_data["data"],
                key,
                file_data["nonce"]
            )

            logger.info("Download successful for user_id=%s, file_id=%s", user_id, file_id)

            return {
                "status": "success",
                "message": "File downloaded successfully",
                "file": decrypted,
                "file_name": file_data.get("original_name", f"file_{file_id}")
            }

        except Exception as e:
            logger.error(
                "Download failed for user_id=%s, file_id=%s: %s",
                user_id,
                file_id,
                str(e)
            )

            return {
                "status": "error",
                "message": "Download failed"
            }

    def process_delete(self, user_id, file_id):
        try:
            logger.info("Delete started for user_id=%s, file_id=%s", user_id, file_id)

            validate_user_id(user_id)
            validate_file_id(file_id)

            file_data = self.storage.fetch_from_disk(file_id)

            if not file_data:
                raise FileOperationError("File not found")

            if file_data["owner_id"] != user_id:
                logger.warning(
                    "Unauthorized delete attempt: user_id=%s, file_id=%s",
                    user_id,
                    file_id
                )
                raise AuthorizationError("Not allowed")

            deleted = self.storage.delete_file(file_id)

            if not deleted:
                raise FileOperationError("Delete failed")

            logger.info("Delete successful for user_id=%s, file_id=%s", user_id, file_id)

            return {
                "status": "success",
                "message": "File deleted successfully"
            }

        except Exception as e:
            logger.error(
                "Delete failed for user_id=%s, file_id=%s: %s",
                user_id,
                file_id,
                str(e)
            )

            return {
                "status": "error",
                "message": "Delete failed"
            }