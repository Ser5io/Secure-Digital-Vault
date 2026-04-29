import bcrypt
import pyodbc  # Standard driver for SQL Server (T-SQL)

class UserAuthenticator:
    def __init__(self, connection_string=None):
        self.conn = None
        self.cursor = None

        if connection_string is None:
            self.conn_str = (
                "Driver={ODBC Driver 17 for SQL Server};"
                "Server=localhost;"
                "Database=AlMakhzan;"
                "Trusted_Connection=yes;"
            )
        else:
            self.conn_str = connection_string
        
        try:
            self.conn = pyodbc.connect(self.conn_str, autocommit=True)
            self.cursor = self.conn.cursor()
            self.cursor.execute("USE AlMakhzan")
            print("✅ UserAuthenticator: Connected to AlMakhzan.")
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            self.conn = None

    def register_user(self, username, email, password):
        if not self.cursor: return False, "No connection"
        if not username.strip() or not password.strip(): return False, "Empty fields"
        
        self.cursor.execute("SELECT id FROM AlMakhzan.dbo.Users WHERE username = ?", (username,))
        if self.cursor.fetchone(): return False, "the username is used"

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            self.cursor.execute("{CALL AlMakhzan.dbo.sp_RegisterUser (?, ?)}", (username, hashed_password.decode('utf-8')))
            return True, "Success"
        except Exception as e:
            return False, str(e)

    def authenticate(self, identifier, password):
        if not self.cursor: return False, None, "No connection"
        try:
            query = "SELECT id, password_hash FROM AlMakhzan.dbo.Users WHERE username = ?"
            self.cursor.execute(query, (identifier,))
            result = self.cursor.fetchone()

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

    def _log_access(self, user_id, action, status):
        try:
            ip_address = "127.0.0.1" 
            self.cursor.execute("{CALL AlMakhzan.dbo.sp_AddLogEntry (?, ?, ?, ?)}", 
                                (user_id, action, status, ip_address))
        except: pass

    def get_user_salt(self, user_id):
        self.cursor.execute("SELECT password_hash FROM AlMakhzan.dbo.Users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0][:29] if result else None

    def list_user_files(self, user_id):
        """Fixed: Fetch files specifically from our database."""
        try:
            self.cursor.execute("{CALL AlMakhzan.dbo.sp_GetMyFiles (?)}", (user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching files: {e}")
            return []
