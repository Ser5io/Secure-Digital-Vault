import bcrypt
import pyodbc  # Standard driver for SQL Server (T-SQL)
import datetime

class UserAuthenticator:
    def __init__(self, connection_string=None):
        if connection_string is None:
            self.conn_str = (
                "Driver={ODBC Driver 17 for SQL Server};"
                "Server=localhost;"
                "Database=AlMakhzan;"
                "Trusted_Connection=yes;"
            )
        else:
            self.conn_str = connection_string
        
        # Test connection once during startup
        try:
            conn = self._get_connection()
            conn.close()
            print("✅ UserAuthenticator: DB Connection test successful.")
        except Exception as e:
            print(f"❌ Connection Error during initialization: {e}")

    def _get_connection(self):
        """Helper to create a fresh connection for every request to ensure thread-safety."""
        conn = pyodbc.connect(self.conn_str, autocommit=True)
        # No need for cursor.execute("USE AlMakhzan") if it's in the conn_str
        return conn

    def register_user(self, username, email, password):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if not username.strip() or not password.strip(): return False, "Empty fields"
            
            cursor.execute("SELECT id FROM AlMakhzan.dbo.Users WHERE username = ?", (username,))
            if cursor.fetchone(): return False, "the username is used"

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("{CALL AlMakhzan.dbo.sp_RegisterUser (?, ?, ?)}", (username, email, hashed_password.decode('utf-8')))
            return True, "Success"
        except Exception as e:
            return False, str(e)
        finally:
            if conn: conn.close()

    def get_user_email(self, user_id):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM AlMakhzan.dbo.Users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except:
            return None
        finally:
            if conn: conn.close()

    def store_mfa_code(self, user_id, code):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Delete old codes for this user
            cursor.execute("DELETE FROM AlMakhzan.dbo.MFA_Codes WHERE user_id = ?", (user_id,))
            # Store new code with 10 min expiry
            expiry = datetime.datetime.now() + datetime.timedelta(minutes=10)
            cursor.execute("INSERT INTO AlMakhzan.dbo.MFA_Codes (user_id, code, expires_at) VALUES (?, ?, ?)",
                                (user_id, code, expiry))
            return True
        except Exception as e:
            print(f"❌ Error storing MFA code: {e}")
            return False
        finally:
            if conn: conn.close()

    def verify_mfa_code(self, user_id, code):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT code, expires_at FROM AlMakhzan.dbo.MFA_Codes WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if not result: return False, "Code not found"
            
            stored_code, expires_at = result
            if datetime.datetime.now() > expires_at:
                return False, "Code expired"
            
            if stored_code == code:
                # Delete code after successful verification
                cursor.execute("DELETE FROM AlMakhzan.dbo.MFA_Codes WHERE user_id = ?", (user_id,))
                return True, "Success"
            else:
                return False, "Invalid code"
        except Exception as e:
            return False, str(e)
        finally:
            if conn: conn.close()

    def authenticate(self, identifier, password):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = "SELECT id, password_hash FROM AlMakhzan.dbo.Users WHERE username = ?"
            cursor.execute(query, (identifier,))
            result = cursor.fetchone()

            if result:
                user_id = int(result[0])
                stored_hash = result[1].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    self._log_access(user_id, 'login', 'Success')
                    return True, user_id, "Login successful"
                else:
                    self._log_access(user_id, 'login', 'Failed')
                    return False, None, "Incorrect password!"
            return False, None, "User not found!"
        except Exception as e:
            return False, None, str(e)
        finally:
            if conn: conn.close()

    def _log_access(self, user_id, action, status):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            ip_address = "127.0.0.1" 
            cursor.execute("{CALL AlMakhzan.dbo.sp_AddLogEntry (?, ?, ?, ?)}", 
                                (user_id, action, status, ip_address))
        except: pass
        finally:
            if conn: conn.close()

    def get_user_salt(self, user_id):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM AlMakhzan.dbo.Users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0][:29] if result else None
        except:
            return None
        finally:
            if conn: conn.close()

    def list_user_files(self, user_id):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("{CALL AlMakhzan.dbo.sp_GetMyFiles (?)}", (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching files: {e}")
            return []
        finally:
            if conn: conn.close()
