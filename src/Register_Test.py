from UserAuthenticator import UserAuthenticator

def run_test():
    # 1. Initialize
    auth = UserAuthenticator()
    
    if not auth.conn:
        print("❌ Cannot proceed: Database not connected.")
        return

    # 2. Try to register a unique test user
    # Note: I am adding '99' to the name to make it unique
    test_username = "TestUser_99"
    test_password = "SecretPassword123"
    
    print(f"\nAttempting to register: {test_username}...")
    
    success = auth.register_user(test_username, "test@example.com", test_password)
    
    if success:
        print(f"✅ Python says: {test_username} was saved!")
        
        # 3. Double Check: Try to find that user immediately
        print("🔍 Searching database for that user now...")
        auth.cursor.execute("SELECT id, username FROM Users WHERE username = ?", (test_username,))
        row = auth.cursor.fetchone()
        
        if row:
            print(f"🏆 FOUND IN DATABASE! User ID is: {row[0]}")
            print("You can now go to SQL App (SSMS) and Refresh your table to see it.")
        else:
            print("❓ Weird... Python said success but I can't find the row.")
    else:
        print("❌ Registration failed.")

if __name__ == "__main__":
    run_test()
