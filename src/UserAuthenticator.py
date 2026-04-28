import bcrypt
import pyodbc  # Standard driver for SQL Server (T-SQL)

class UserAuthenticator:
    def __init__(self, connection_string=None):
        self.conn = None
        self.cursor = None

        if connection_string is None:
            # Added "Initial Catalog" which is another way to say "Database"
            self.conn_str = (
                "Driver={ODBC Driver 17 for SQL Server};"
                "Server=localhost;"
                "Database=AlMakhzan;"
                "Trusted_Connection=yes;"
            )
        else:
            self.conn_str = connection_string
        
        try:
            self.conn = pyodbc.connect(self.conn_str)
            self.cursor = self.conn.cursor()
            self.cursor.execute("USE AlMakhzan")
            print("✅ Database connected successfully.")
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            self.conn = None

    def register_user(self, username, email, password):
        if not self.cursor: return False
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            self.cursor.execute("{CALL AlMakhzan.dbo.sp_RegisterUser (?, ?)}", (username, hashed_password.decode('utf-8')))
            self.conn.commit()
            print(f"✅ User {username} registered.")
            return True
        except Exception as e:
            print(f"Registration Error: {e}")
            return False

    def authenticate(self, identifier, password):
        if not self.cursor: return False, None
        try:
            query = "SELECT id, password_hash FROM AlMakhzan.dbo.Users WHERE username = ?"
            self.cursor.execute(query, (identifier,))
            result = self.cursor.fetchone()

            if result:
                user_id = int(result[0])
                stored_hash = result[1].encode('utf-8')
                
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    print(f"🔓 Password correct for ID: {user_id}")
                    # Log Success
                    self._log_access(user_id, 'login', 'Success')
                    return True, user_id
                else:
                    # Log Failed
                    self._log_access(user_id, 'login', 'Failed')
            return False, None
        except Exception as e:
            print(f"Authentication Error: {e}")
            return False, None

    def _log_access(self, user_id, action, status):
        """
        Records the activity using the new sp_AddLogEntry name.
        """
        if not self.cursor: return
        try:
            ip_address = "127.0.0.1" 
            print(f"📝 Logging {action} for User {user_id}...")
            
            # Use the NEW procedure name
            self.cursor.execute("{CALL AlMakhzan.dbo.sp_AddLogEntry (?, ?, ?, ?)}", 
                                (user_id, action, status, ip_address))
            self.conn.commit()
            print("✅ Log entry successfully saved.")
        except Exception as e:
            print(f"❌ LOGGING FAILED: {e}")

    def get_all_logs(self):
        if not self.cursor: return
        try:
            # Check the table directly in our database
            self.cursor.execute("SELECT TOP 5 * FROM AlMakhzan.dbo.Access_Logs ORDER BY timestamp DESC")
            rows = self.cursor.fetchall()
            print("\n--- RECENT DATABASE LOGS ---")
            for row in rows:
                print(f"LogID: {row[0]} | UserID: {row[1]} | Action: {row[2]} | Status: {row[3]} | Time: {row[5]}")
        except Exception as e:
            print(f"Error reading logs: {e}")

if __name__ == "__main__":
    auth = UserAuthenticator()
    # Test with a user
    test_user = "yousefk" 
    test_pass = "SecurePass123"
    
    success, uid = auth.authenticate(test_user, test_pass)
    
    if success:
        print("✅ Login Success!")
    else:
        print("❌ Login Failed!")
        
    auth.get_all_logs()
