USE AlMakhzan;
GO

-- ======================================================
-- DASHBOARD & UPLOAD FIX SCRIPT
-- ======================================================
-- 1. Ensure the Files Table structure is correct
-- 2. Clean up old procedures
-- 3. Create fixed procedures with VALUES clause
-- ======================================================

-- 1. Create Files table if it's missing or broken
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Files')
BEGIN
    CREATE TABLE Files (
        file_id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NOT NULL,
        original_name NVARCHAR(255) NOT NULL,
        stored_name NVARCHAR(255) NOT NULL UNIQUE,
        file_path NVARCHAR(MAX) NOT NULL,
        file_size BIGINT,
        upload_date DATETIME DEFAULT GETDATE(),
        encryption_iv VARBINARY(MAX),
        file_hash NVARCHAR(64),
        CONSTRAINT FK_Files_Users FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
    );
END
GO

-- 2. Drop old versions to prevent "Object already exists" errors
IF OBJECT_ID('dbo.sp_SecureUpload', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_SecureUpload;
IF OBJECT_ID('dbo.sp_GetMyFiles', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_GetMyFiles;
GO

-- 3. The Fixed Secure Upload Procedure (Added missing VALUES clause)
CREATE PROCEDURE dbo.sp_SecureUpload
	@user_id INT,
	@original_name NVARCHAR(255),
	@stored_name NVARCHAR(255),
	@file_path NVARCHAR(MAX),
	@file_size BIGINT,
	@encryption_iv VARBINARY(MAX),
	@file_hash NVARCHAR(64),
	@ip_address NVARCHAR(45)
AS
BEGIN
	BEGIN TRY
		INSERT INTO AlMakhzan.dbo.Files (user_id, original_name, stored_name, file_path, file_size, encryption_iv, file_hash)
		VALUES (@user_id, @original_name, @stored_name, @file_path, @file_size, @encryption_iv, @file_hash);

		-- Use the new AddLogEntry procedure
		EXEC AlMakhzan.dbo.sp_AddLogEntry @user_id, 'upload', 'Success', @ip_address;
	END TRY
	BEGIN CATCH
		EXEC AlMakhzan.dbo.sp_AddLogEntry @user_id, 'upload', 'Failed', @ip_address;
		THROW;
	END CATCH
END;
GO

-- 4. The Fixed GetMyFiles Procedure
CREATE PROCEDURE dbo.sp_GetMyFiles
	@user_id INT
AS
BEGIN
	SELECT file_id, original_name, CAST(file_size / 1024.0 AS DECIMAL(10,2)) AS size_KB, upload_date
	FROM AlMakhzan.dbo.Files
	WHERE user_id = @user_id
	ORDER BY upload_date DESC;
END;
GO
