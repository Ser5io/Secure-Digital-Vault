from controllers.vault_controller import VaultController
from services.auth_service import AuthService
from services.crypto_service import CryptoService
from services.storage_service import StorageService


def main():
    auth = AuthService()
    crypto = CryptoService()
    storage = StorageService()

    controller = VaultController(auth, crypto, storage)

    user_id = 1
    password = "Password123"
    file_path = "test.txt"

    try:
        upload_result = controller.process_upload(user_id, file_path, password)

        if upload_result["status"] != "success":
            print("Upload failed")
            return

        print("Upload completed successfully")

        file_id = upload_result["file_id"]

        download_result = controller.process_download(user_id, file_id, password)

        if download_result["status"] != "success":
            print("Download failed")
            return

        print("Download completed successfully")

        delete_result = controller.process_delete(user_id, file_id)

        if delete_result["status"] != "success":
            print("Delete failed")
            return

        print("Delete completed successfully")

    except Exception:
        print("Something went wrong during testing")


if __name__ == "__main__":
    main()