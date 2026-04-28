from UserAuthenticator import UserAuthenticator

# =================================================================
# CONNECTION TEST SCRIPT
# =================================================================
# This script helps you verify that your Python code can "talk" 
# to your SQL Server database.
# =================================================================

# 1. SETTINGS: Change these values to match your environment
SERVER_NAME = 'localhost'  # Example: 'DESKTOP-ABC123' or '.'
DATABASE_NAME = 'AlMakhzan'

# 2. BUILD THE CONNECTION STRING
# We use curly braces {{ }} around the driver name because it's an f-string
conn_string = (
    f"Driver={{ODBC Driver 17 for SQL Server}};"
    f"Server={SERVER_NAME};"
    f"Database={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
)

def test_connection():
    print("--- Starting Connection Test ---")
    print(f"Targeting Server: {SERVER_NAME}")
    print(f"Targeting Database: {DATABASE_NAME}")
    
    # 3. INITIALIZE AUTHENTICATOR
    auth = UserAuthenticator(conn_string)
    
    # 4. VERIFY CONNECTION
    if auth.conn is not None:
        print("\n✅ SUCCESS: Connected to the database!")
        
        # Test 5: Try to count users to ensure table access works
        try:
            auth.cursor.execute("SELECT COUNT(*) FROM Users")
            count = auth.cursor.fetchone()[0]
            print(f"📊 Database Status: Found {count} users in the 'Users' table.")
        except Exception as e:
            print(f"⚠️ Warning: Connected, but couldn't read the 'Users' table: {e}")
            
    else:
        print("\n❌ FAILED: Could not connect to the database.")
        print("Tip: Make sure SQL Server is running and your SERVER_NAME is correct.")

if __name__ == "__main__":
    test_connection()
