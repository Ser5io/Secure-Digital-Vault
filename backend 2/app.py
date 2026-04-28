from flask import Flask, request, jsonify, send_file
from io import BytesIO
import os
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from controllers.vault_controller import VaultController
from services.auth_service import AuthService, hash_password
from services.crypto_service import CryptoService
from services.storage_service_sql import StorageServiceSQL


app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)

UPLOAD_TEMP_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_TEMP_FOLDER, exist_ok=True)

auth = AuthService()
crypto = CryptoService()
storage = StorageServiceSQL()

controller = VaultController(auth, crypto, storage)


def get_user_id_from_token():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    try:
        token = auth_header.split(" ")[1]
    except IndexError:
        return None

    result = auth.verify_token(token)

    if result["status"] != "success":
        return None

    return result["user_id"]


@app.route("/")
def home():
    return jsonify({
        "message": "Secure Digital Vault API is running"
    })


@limiter.limit("5 per minute")
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        user_id = int(data.get("user_id"))
        password = data.get("password")

        result = auth.login(user_id, password)

        if result["status"] != "success":
            return jsonify(result), 401

        return jsonify(result), 200

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return jsonify({
            "status": "error",
            "message": "Login failed"
        }), 500


@limiter.limit("10 per minute")
@app.route("/upload", methods=["POST"])
def upload_file():
    temp_path = None

    try:
        user_id = get_user_id_from_token()

        if user_id is None:
            return jsonify({
                "status": "error",
                "message": "Unauthorized"
            }), 401

        password = request.form.get("password")
        uploaded_file = request.files.get("file")

        if not password:
            return jsonify({
                "status": "error",
                "message": "Password is required"
            }), 400

        if uploaded_file is None:
            return jsonify({
                "status": "error",
                "message": "No file uploaded"
            }), 400

        safe_name = secure_filename(uploaded_file.filename)

        if not safe_name:
            return jsonify({
                "status": "error",
                "message": "Invalid file name"
            }), 400

        temp_path = os.path.join(UPLOAD_TEMP_FOLDER, safe_name)
        uploaded_file.save(temp_path)

        result = controller.process_upload(user_id, temp_path, password)

        if result["status"] != "success":
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        return jsonify({
            "status": "error",
            "message": "Upload request failed"
        }), 500

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@limiter.limit("20 per minute")
@app.route("/download/<int:file_id>", methods=["POST"])
def download_file(file_id):
    try:
        user_id = get_user_id_from_token()

        if user_id is None:
            return jsonify({
                "status": "error",
                "message": "Unauthorized"
            }), 401

        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Invalid JSON body"
            }), 400

        password = data.get("password")

        if not password:
            return jsonify({
                "status": "error",
                "message": "Password is required"
            }), 400

        result = controller.process_download(user_id, file_id, password)

        if result["status"] != "success":
            return jsonify(result), 400

        file_bytes = result.get("file")
        file_name = result.get("file_name", f"file_{file_id}")

        return send_file(
            BytesIO(file_bytes),
            as_attachment=True,
            download_name=file_name,
            mimetype="application/octet-stream"
        )

    except Exception as e:
        print("DOWNLOAD ERROR:", str(e))
        return jsonify({
            "status": "error",
            "message": "Download request failed"
        }), 500


@limiter.limit("10 per minute")
@app.route("/delete/<int:file_id>", methods=["POST"])
def delete_file(file_id):
    try:
        user_id = get_user_id_from_token()

        if user_id is None:
            return jsonify({
                "status": "error",
                "message": "Unauthorized"
            }), 401

        result = controller.process_delete(user_id, file_id)

        if result["status"] != "success":
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        print("DELETE ERROR:", str(e))
        return jsonify({
            "status": "error",
            "message": "Delete request failed"
        }), 500
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not password or len(password) < 8:
          return jsonify({
        "status": "error",
        "message": "Password must be at least 8 characters"
    }), 400

        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "Missing data"
            }), 400

        password_hash = hash_password(password)

        conn = auth._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO dbo.Users (username, password_hash) VALUES (?, ?)",
            username,
            password_hash
        )

        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "User created"
        }), 201

    except Exception as e:
        print("REGISTER ERROR:", str(e))
        return jsonify({
            "status": "error",
            "message": "Register failed"
        }), 500


if __name__ == "__main__":
    app.run(debug=False)
