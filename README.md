# 🔐 Secure Digital Vault

Secure Digital Vault is a high-security, modular Password and File Manager. It combines military-grade encryption with advanced defense mechanisms like Multi-Factor Authentication (MFA) and Denial-of-Service (DoS) mitigation.

## 🚀 Key Features

-   **Zero-Knowledge Encryption**: Files are encrypted client-side (via password) using **AES-256-GCM**.
-   **Strong Key Derivation**: Uses **PBKDF2-HMAC-SHA256** with 100,000 iterations to protect against brute-force.
-   **Multi-Factor Authentication (MFA)**: Secure 6-digit verification codes sent via Gmail SMTP.
-   **DoS & Brute-Force Protection**: 
    -   **Sliding Window Rate Limiting** on authentication and API routes.
    -   **Payload Capping**: Maximum 5MB request size to prevent memory exhaustion.
-   **Full-Stack Architecture**: Modern React frontend with a modular Flask backend.
-   **Database**: Microsoft SQL Server (T-SQL) for robust data management and logging.

---

## 🛠️ Tech Stack

-   **Frontend**: React, Tailwind CSS, JWT.
-   **Backend**: Python (Flask), `flask-limiter`, `cryptography`.
-   **Database**: SQL Server (MSSQL), `pyodbc`.
-   **Security**: AES-GCM, PBKDF2, Bcrypt.

---

## ⚙️ Installation & Setup

### 1. Prerequisites
-   Python 3.8+
-   Node.js & npm
-   SQL Server (Express or Developer edition)
-   Gmail account (for MFA)

### 2. Database Configuration
1.  Open **SQL Server Management Studio (SSMS)**.
2.  Run `Database/AlMakhzan.sql` to create the schema and stored procedures.
3.  Run `Database/MFA_Update.sql` to add the MFA and email support.

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
# Gmail SMTP Configuration
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-google-app-password

# Application Secret
SECRET_KEY=your_project_secret_here
```

### 4. Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python src/VaultBackend.py
```

### 5. Frontend Setup
```bash
cd frontend
npm install
npm start
```

---

## 🧪 Security Testing

### Rate Limit Verification (Stress Test)
To verify the DoS mitigation system, run the controlled stress testing script:
```bash
python src/StressTest.py
```
This script simulates concurrent login attempts to verify that the **Sliding Window** rate limiter correctly blocks excess traffic with a `429 Too Many Requests` status.

---

## 🔒 Cryptographic Implementation

-   **Encryption**: `AES-256-GCM` provides both confidentiality and authenticity.
-   **Hashing**: `SHA-256` for file integrity verification.
-   **Passwords**: Master passwords are never stored; only `Bcrypt` hashes are saved in the database.
-   **Sessions**: Stateless `JWT` tokens with a 1-hour expiration.

---


---

## 📜 License
This project is for educational and professional demonstration purposes.
