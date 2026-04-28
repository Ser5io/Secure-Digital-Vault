USE AlMakhzan;
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Access_Logs')
BEGIN
	CREATE TABLE Access_Logs (
		log_id INT IDENTITY(1,1) PRIMARY KEY,
		user_id INT NOT NULL,
		action NVARCHAR(20),
		status NVARCHAR(10),
		ip_address NVARCHAR(45) NOT NULL,
		timestamp DATETIME DEFAULT GETDATE(),
		CONSTRAINT FK_Logs_Users FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
	);
END
GO

CREATE OR ALTER PROCEDURE dbo.sp_AddLogEntry
	@user_id INT,
	@action NVARCHAR(20),
	@status NVARCHAR(10),
	@ip_address NVARCHAR(45)
AS
BEGIN
	INSERT INTO dbo.Access_Logs (user_id, action, status, ip_address)
	VALUES (@user_id, @action, @status, @ip_address);
END
GO