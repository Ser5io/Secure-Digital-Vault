import jwt
import datetime
import bcrypt
import pyodbc
import os


def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str):
    return bcrypt.checkpw(password.encode(), hashed.encode())


class AuthService:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")

    CONNECTION_STRING = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-B4R3O1H;"
        "DATABASE=SecureVaultDB;"
        "Trusted_Connection=yes;"
    )

    def _get_connection(self):
        return pyodbc.connect(self.CONNECTION_STRING)

    def get_user_salt(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT salt FROM dbo.Users WHERE id = ?",
            user_id
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise Exception("User not found")

        return row[0]

    def login(self, user_id, password):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT password_hash FROM dbo.Users WHERE id = ?",
                user_id
            )

            row = cursor.fetchone()
            conn.close()

            if not row:
                return {"status": "error", "message": "Invalid credentials"}

            stored_hash = row[0]

            if not verify_password(password, stored_hash):
                return {"status": "error", "message": "Invalid credentials"}

            token = jwt.encode(
                {
                    "user_id": user_id,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                },
                self.SECRET_KEY,
                algorithm="HS256"
            )

            return {"status": "success", "token": token}

        except Exception:
            return {"status": "error", "message": "Login failed"}

    def verify_token(self, token):
        try:
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=["HS256"]
            )

            return {"status": "success", "user_id": payload["user_id"]}

        except Exception:
            return {"status": "error", "message": "Invalid or expired token"}