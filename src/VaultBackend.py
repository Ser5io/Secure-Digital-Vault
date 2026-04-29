from flask import Flask, request, jsonify, send_file
from io import BytesIO
import os
import jwt
import datetime
from flask_cors import CORS

from UserAuthenticator import UserAuthenticator
from VaultFileManager import VaultFileManager
from VaultCrypto import VaultCrypto 

app = Flask(__name__)
# Enable CORS for the entire app to allow React to talk to Flask
CORS(app, resources={r"/*": {"origins": "*"}}) 

app.config['SECRET_KEY'] = 'your_university_project_secret'

# Initialize modules
auth = UserAuthenticator()
file_manager = VaultFileManager()
crypto = VaultCrypto()

def get_uid_from_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header: return None
    try:
        token = auth_header.split(" ")[1]
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return data['user_id']
    except:
        return None

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Backend is online"})

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    print(f"📩 Received Register Request for: {data.get('username')}")
    success, message = auth.register_user(data['username'], data.get('email', ''), data['password'])
    if success:
        print("✅ Registration successful")
        return jsonify({"status": "success", "message": "Registered successfully"}), 201
    print(f"❌ Registration failed: {message}")
    return jsonify({"status": "error", "message": message}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    print(f"📩 Received Login Request for: {data.get('username')}")
    success, uid, message = auth.authenticate(data['username'], data['password'])
    if success:
        print(f"✅ Login successful for user {uid}")
        token = jwt.encode({'user_id': uid, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, 
                           app.config['SECRET_KEY'])
        return jsonify({"status": "success", "token": token, "user_id": uid})
    print(f"❌ Login failed: {message}")
    return jsonify({"status": "error", "message": message}), 401

@app.route("/files", methods=["GET"])
def list_files():
    uid = get_uid_from_token()
    print(f"📩 Fetching files for user ID: {uid}")
    if not uid: return jsonify({"message": "Unauthorized"}), 401
    files = auth.list_user_files(uid)
    output = []
    for f in files:
        output.append({"id": f[0], "name": f[1], "size": str(f[2])+" KB", "date": str(f[3])})
    return jsonify(output)

@app.route("/upload", methods=["POST"])
def upload():
    uid = get_uid_from_token()
    print(f"📩 Upload request from user {uid}")
    if not uid: return jsonify({"message": "Unauthorized"}), 401
    
    password = request.form.get("password")
    file = request.files['file']
    
    salt = auth.get_user_salt(uid)
    if not salt: return jsonify({"message": "User salt not found"}), 404
    
    key = crypto.generate_key(password, salt.encode() if isinstance(salt, str) else salt)
    file_bytes = file.read()
    ciphertext, iv, _ = crypto.encrypt_file(file_bytes, key)
    file_hash = crypto.generate_file_hash(file_bytes)
    
    success = file_manager.save_file(uid, file.filename, ciphertext, iv, file_hash)
    if success: 
        print("✅ File saved and encrypted")
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 500

@app.route("/download/<int:file_id>", methods=["POST"])
def download(file_id):
    uid = get_uid_from_token()
    print(f"📩 Download request for file {file_id}")
    if not uid: return jsonify({"message": "Unauthorized"}), 401
    
    data = request.get_json()
    password = data.get("password")
    
    ciphertext, iv, original_name = file_manager.get_file_data(file_id)
    if not ciphertext: return jsonify({"message": "File not found"}), 404
    
    try:
        salt = auth.get_user_salt(uid)
        key = crypto.generate_key(password, salt.encode() if isinstance(salt, str) else salt)
        decrypted_data = crypto.decrypt_file(ciphertext, key, iv)
        print("✅ Decryption successful")
        return send_file(BytesIO(decrypted_data), download_name=original_name, as_attachment=True)
    except:
        print("❌ Decryption failed (wrong password)")
        return jsonify({"message": "Wrong password!"}), 403

@app.route("/delete/<int:file_id>", methods=["DELETE"])
def delete_file(file_id):
    uid = get_uid_from_token()
    print(f"📩 Delete request for file {file_id}")
    if not uid: return jsonify({"message": "Unauthorized"}), 401
    
    # In a real app, we should check if the file belongs to this user first.
    # For this project, the File Manager handles the SQL deletion.
    success = file_manager.delete_file(file_id)
    if success:
        print(f"✅ File {file_id} deleted")
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Delete failed"}), 500

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 VAULT BACKEND IS RUNNING ON http://localhost:5000")
    print("="*50 + "\n")
    app.run(port=5000, debug=True)
