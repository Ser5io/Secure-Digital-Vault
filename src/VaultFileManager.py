import os
import uuid
import pyodbc

class VaultFileManager:
    def __init__(self, storage_path="vault_storage"):
        self.storage_dir = storage_path
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            
        self.conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost;"
            "Database=AlMakhzan;"
            "Trusted_Connection=yes;"
        )

    def _get_connection(self):
        conn = pyodbc.connect(self.conn_str, autocommit=True)
        conn.cursor().execute("USE AlMakhzan")
        return conn

    def save_file(self, user_id, original_name, encrypted_data, iv, file_hash, ip_address="127.0.0.1"):
        stored_name = str(uuid.uuid4()) + ".enc"
        full_path = os.path.join(self.storage_dir, stored_name)
        
        with open(full_path, "wb") as f:
            f.write(encrypted_data)
            
        file_size = os.path.getsize(full_path)

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Ensure IV is bytes for SQL VARBINARY
            binary_iv = pyodbc.Binary(iv) if isinstance(iv, bytes) else iv
            
            cursor.execute("{CALL AlMakhzan.dbo.sp_SecureUpload (?, ?, ?, ?, ?, ?, ?, ?)}", 
                (user_id, original_name, stored_name, full_path, file_size, binary_iv, file_hash, ip_address))
            
            conn.close()
            return True
        except Exception as e:
            print(f"❌ DB Save Error: {e}")
            return False

    def list_user_files(self, user_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("{CALL AlMakhzan.dbo.sp_GetMyFiles (?)}", (user_id,))
            files = cursor.fetchall()
            conn.close()
            return files
        except Exception as e:
            print(f"❌ Retrieval Error: {e}")
            return []

    def get_file_data(self, file_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT file_path, encryption_iv, original_name FROM AlMakhzan.dbo.Files WHERE file_id = ?", (file_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                path, iv, name = row
                with open(path, "rb") as f: data = f.read()
                return data, iv, name
            return None, None, None
        except Exception as e:
            return None, None, None

    def delete_file(self, file_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM AlMakhzan.dbo.Files WHERE file_id = ?", (file_id,))
            row = cursor.fetchone()
            if row:
                if os.path.exists(row[0]): os.remove(row[0])
                cursor.execute("DELETE FROM AlMakhzan.dbo.Files WHERE file_id = ?", (file_id,))
                conn.close()
                return True
            return False
        except: return False
