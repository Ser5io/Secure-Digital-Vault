import os
import json
import uuid


class StorageService:
    def __init__(self):
        self.storage_dir = "vault_storage"
        self.db_file = "files_db.json"

        os.makedirs(self.storage_dir, exist_ok=True)

        if not os.path.exists(self.db_file):
            with open(self.db_file, "w") as f:
                json.dump({}, f)

    def _load_db(self):
        with open(self.db_file, "r") as f:
            return json.load(f)

    def _save_db(self, db):
        with open(self.db_file, "w") as f:
            json.dump(db, f, indent=4)

    def _build_path(self, stored_name):
        return os.path.join(self.storage_dir, stored_name)

    def read_raw_file(self, path):
        with open(path, "rb") as f:
            return f.read()

    def save_to_disk(self, user_id, file_path, data, nonce):
        db = self._load_db()

        file_id = str(max(map(int, db.keys()), default=0) + 1)
        stored_name = str(uuid.uuid4()) + ".bin"
        stored_path = self._build_path(stored_name)

        with open(stored_path, "wb") as f:
            f.write(data)

        db[file_id] = {
            "owner_id": user_id,
            "original_name": os.path.basename(file_path),
            "stored_name": stored_name,
            "nonce": nonce.hex()
        }

        self._save_db(db)

        return int(file_id)

    def fetch_from_disk(self, file_id):
        db = self._load_db()
        file_id = str(file_id)

        if file_id not in db:
            return None

        record = db[file_id]
        stored_name = record["stored_name"]
        stored_path = self._build_path(stored_name)

        if not os.path.exists(stored_path):
            return None

        with open(stored_path, "rb") as f:
            encrypted_data = f.read()

        return {
            "owner_id": record["owner_id"],
            "original_name": record["original_name"],
            "data": encrypted_data,
            "nonce": bytes.fromhex(record["nonce"])
        }

    def delete_file(self, file_id):
        db = self._load_db()
        file_id = str(file_id)

        if file_id not in db:
            return False

        record = db[file_id]
        stored_name = record["stored_name"]
        stored_path = self._build_path(stored_name)

        if os.path.exists(stored_path):
            os.remove(stored_path)

        del db[file_id]
        self._save_db(db)

        return True