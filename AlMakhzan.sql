-- =============================================
-- الجزء الأول: إنشاء الجداول (Schema)
-- =============================================

-- 1. إنشاء جدول المستخدمين (Users Table)
CREATE TABLE Users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);

-- 2. إنشاء جدول الملفات (Files Table)
CREATE TABLE Files (
    file_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    original_name NVARCHAR(255) NOT NULL,
    stored_name NVARCHAR(255) NOT NULL UNIQUE,
    file_path NVARCHAR(MAX) NOT NULL,
    file_size BIGINT, -- العمود الجديد لحجم الملف
    upload_date DATETIME DEFAULT GETDATE(),
    encryption_iv VARBINARY(16),
    file_hash NVARCHAR(64),
    CONSTRAINT FK_Files_Users FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- 3. إنشاء جدول سجلات الدخول (Access_Logs Table)
CREATE TABLE Access_Logs (
    log_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    action NVARCHAR(20) CHECK (action IN ('upload', 'download', 'delete', 'login')),
    status NVARCHAR(10) CHECK (status IN ('Success', 'Failed')), -- العمود الجديد لحالة العملية
    ip_address NVARCHAR(45) NOT NULL,
    timestamp DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Logs_Users FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);
GO -- تفصل بين إنشاء الجداول وإنشاء البروسيدجرز

-- 1. إضافة مستخدم جديد (Register)
CREATE OR ALTER PROCEDURE sp_AddUser
    @username NVARCHAR(50),
    @password_hash NVARCHAR(255)
AS
BEGIN
    INSERT INTO Users (username, password_hash)
    VALUES (@username, @password_hash);
END;
GO

-- 2. رفع ملف بشكل آمن (Secure Upload)
-- يقوم برفع الملف وتسجيل العملية في الـ Logs في خطوة واحدة
CREATE OR ALTER PROCEDURE sp_SecureUpload
    @user_id INT,
    @original_name NVARCHAR(255),
    @stored_name NVARCHAR(255),
    @file_path NVARCHAR(MAX),
    @file_size BIGINT,
    @encryption_iv VARBINARY(16),
    @file_hash NVARCHAR(64),
    @ip_address NVARCHAR(45)
AS
BEGIN
    BEGIN TRY
        -- إدخال بيانات الملف
        INSERT INTO Files (user_id, original_name, stored_name, file_path, file_size, encryption_iv, file_hash)
        VALUES (@user_id, @original_name, @stored_name, @file_path, @file_size, @encryption_iv, @file_hash);

        -- تسجيل نجاح العملية
        INSERT INTO Access_Logs (user_id, action, status, ip_address)
        VALUES (@user_id, 'upload', 'Success', @ip_address);
    END TRY
    BEGIN CATCH
        -- في حال حدوث أي خطأ، يتم تسجيل محاولة فاشلة
        INSERT INTO Access_Logs (user_id, action, status, ip_address)
        VALUES (@user_id, 'upload', 'Failed', @ip_address);
        
        -- إظهار رسالة الخطأ للـ Backend
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR(@ErrorMessage, 16, 1);
    END CATCH
END;
GO

-- 3. جلب ملفات المستخدم فقط (Access Control)
-- تضمن أمنياً أن المستخدم لا يطلب إلا ملفاته هو فقط
CREATE OR ALTER PROCEDURE sp_GetMyFiles
    @user_id INT
AS
BEGIN
    SELECT file_id, original_name, CAST(file_size / 1024.0 AS DECIMAL(10,2)) AS size_KB, upload_date
    FROM Files
    WHERE user_id = @user_id
    ORDER BY upload_date DESC;
END;
GO

-- 4. تسجيل عملية (Manual Logging)
-- تُستخدم لتسجيل أي عمليات أخرى مثل التحميل أو الحذف
CREATE OR ALTER PROCEDURE sp_LogAction
    @user_id INT,
    @action NVARCHAR(20),
    @status NVARCHAR(10),
    @ip_address NVARCHAR(45)
AS
BEGIN
    INSERT INTO Access_Logs (user_id, action, status, ip_address)
    VALUES (@user_id, @action, @status, @ip_address);
END;
GO
-- =============================================
-- الجزء الثاني: إدارة الصلاحيات (Permission Management)
-- =============================================

-- 1. إنشاء حساب الدخول والمستخدم للـ Backend (إذا لم يكن موجوداً)
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'BackendAppUser')
BEGIN
    CREATE LOGIN BackendAppUser WITH PASSWORD = 'Strong_Password_123!';
END
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'BackendAppUser')
BEGIN
    CREATE USER BackendAppUser FOR LOGIN BackendAppUser;
END
GO

-- 2. منح صلاحية التنفيذ فقط (Grant Execute Only)
GRANT EXECUTE TO BackendAppUser;

-- 3. تأمين الجداول ضد الوصول المباشر (Security Hardening)
DENY SELECT, INSERT, UPDATE, DELETE ON Users TO BackendAppUser;
DENY SELECT, INSERT, UPDATE, DELETE ON Files TO BackendAppUser;
DENY SELECT, INSERT, UPDATE, DELETE ON Access_Logs TO BackendAppUser;
GO