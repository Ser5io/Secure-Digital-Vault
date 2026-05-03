-- MFA and Email Support Update
USE AlMakhzan;
GO

-- 1. Update Users table to include email
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Users') AND name = 'email')
BEGIN
    ALTER TABLE Users ADD email NVARCHAR(100);
END
GO

-- 2. Create MFA_Codes table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID('MFA_Codes') AND type in (N'U'))
BEGIN
    CREATE TABLE MFA_Codes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NOT NULL,
        code NVARCHAR(6) NOT NULL,
        expires_at DATETIME NOT NULL,
        CONSTRAINT FK_MFA_Users FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
    );
END
GO

-- 3. Update sp_RegisterUser to handle email
CREATE OR ALTER PROCEDURE sp_RegisterUser
    @username NVARCHAR(50),
    @email NVARCHAR(100),
    @password_hash NVARCHAR(255)
AS
BEGIN
    INSERT INTO Users (username, email, password_hash)
    VALUES (@username, @email, @password_hash);
END;
GO
