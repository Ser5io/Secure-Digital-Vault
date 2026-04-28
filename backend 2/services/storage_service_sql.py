import pyodbc
import os
import uuid


class StorageServiceSQL:
    def __init__(self):
        self.connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-B4R3O1H;"
            "DATABASE=SecureVaultDB;"
            "Trusted_Connection=yes;"
        )

        self.storage_dir = "vault_storage"
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_connection(self):
        return pyodbc.connect(self.connection_string)

    def read_raw_file(self, path):
        with open(path, "rb") as f:
            return f.read()

    def save_to_disk(self, user_id, file_path, data, nonce, file_hash, ip="127.0.0.1"):
        stored_name = str(uuid.uuid4()) + ".bin"
        stored_path = os.path.join(self.storage_dir, stored_name)

        with open(stored_path, "wb") as f:
            f.write(data)

        file_size = os.path.getsize(stored_path)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            EXEC sp_SecureUpload ?, ?, ?, ?, ?, ?, ?, ?
        """,
            user_id,
            os.path.basename(file_path),
            stored_name,
            stored_path,
            file_size,
            nonce.hex(),
            file_hash,
            ip
        )

        row = cursor.fetchone()
        conn.commit()
        conn.close()

        return int(row[0])

    def fetch_from_disk(self, file_id):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, original_name, file_path, encryption_nonce
            FROM Files
            WHERE file_id = ?
        """, file_id)

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        user_id, original_name, file_path, nonce = row

        if not os.path.exists(file_path):
            return None

        with open(file_path, "rb") as f:
            encrypted_data = f.read()

        return {
            "owner_id": user_id,
            "original_name": original_name,
            "data": encrypted_data,
            "nonce": bytes.fromhex(nonce)
        }

    def delete_file(self, file_id):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT file_path FROM Files WHERE file_id = ?", file_id)
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False

        file_path = row[0]

        if os.path.exists(file_path):
            os.remove(file_path)

        cursor.execute("DELETE FROM Files WHERE file_id = ?", file_id)

        conn.commit()
        conn.close()

        return True