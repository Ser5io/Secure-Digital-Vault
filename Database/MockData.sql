INSERT INTO Users (username, password_hash) VALUES
('Sarah_Admin', 'hash_abc_123'),
('Omar_User', 'hash_def_456'),
('Laila_Dev', 'hash_ghi_789'),
('Yara_Manager', 'hash_789_def'),
('Ahmed_Guest', 'hash_000_xyz');

-- ملفات سارة (Sarah_Admin) - ملفات إدارة ونظام
INSERT INTO Files (user_id, original_name, stored_name, file_path, file_size, encryption_iv, file_hash) VALUES 
(1, 'System_Config.xml', 'enc_001.dat', 'C:/Data/001.dat', 102400, 0x9876543210FEDCBA9876543210FEDCBA, 'ha1'), -- 100KB
(1, 'Admin_Report_Q1.pdf', 'enc_002.dat', 'C:/Data/002.dat', 5242880, 0xABCDEF1234567890ABCDEF1234567890, 'ha2'); -- 5MB

-- ملفات عمر (Omar_User) - ملفات شخصية
INSERT INTO Files (user_id, original_name, stored_name, file_path, file_size, encryption_iv, file_hash) VALUES 
(2, 'My_Photo.jpg', 'enc_003.dat', 'C:/Data/003.dat', 2097152, 0x1A2B3C4D5E6F708192A3B4C5D6E7F809, 'ho1'), -- 2MB
(2, 'Reading_List.txt', 'enc_004.dat', 'C:/Data/004.dat', 5120, 0xFFFF0000AAAA5555EEEE1111BBBB2222, 'ho2'); -- 5KB

-- ملفات ليلى (Laila_Dev) - ملفات برمجة (كبيرة)
INSERT INTO Files (user_id, original_name, stored_name, file_path, file_size, encryption_iv, file_hash) VALUES 
(3, 'Source_Code_v1.zip', 'enc_005.dat', 'C:/Data/005.dat', 15728640, 0x01230123012301230123012301230123, 'hl1'), -- 15MB
(3, 'Database_Dump.sql', 'enc_006.dat', 'C:/Data/006.dat', 104857600, 0xDEADBEEFCAFEBABE1234567890ABCDEF, 'hl2'); -- 100MB

-- ملفات يارا (Yara_Manager) - ملفات مالية
INSERT INTO Files (user_id, original_name, stored_name, file_path, file_size, encryption_iv, file_hash) VALUES 
(4, 'Budget_2026.xlsx', 'enc_007.dat', 'C:/Data/007.dat', 3145728, 0x8A7B6C5D4E3F21098A7B6C5D4E3F2109, 'hy1'); -- 3MB

-- ملفات أحمد (Ahmed_Guest) - ملف واحد بسيط
INSERT INTO Files (user_id, original_name, stored_name, file_path, file_size, encryption_iv, file_hash) VALUES 
(5, 'Welcome_Guide.pdf', 'enc_008.dat', 'C:/Data/008.dat', 1048576, 0x5555AAAA5555AAAA5555AAAA5555AAAA, 'ha_g1'); -- 1MB

INSERT INTO Access_Logs (user_id, action, status, ip_address) VALUES 
(1, 'login', 'Success', '192.168.1.1'),   -- سارة دخلت
(1, 'upload', 'Success', '192.168.1.1'),  -- سارة رفعت ملف
(2, 'login', 'Success', '192.168.1.50'),  -- عمر دخل
(2, 'download', 'Success', '192.168.1.50'),-- عمر حمل ملف
(3, 'login', 'Success', '10.0.0.5'),      -- ليلى دخلت
(3, 'delete', 'Failed', '10.0.0.5'),      -- ليلى حاولت تحذف ملف وفشلت (تجربة خطأ)
(4, 'login', 'Failed', '172.16.5.1'),     -- يارا حاولت تدفع وفشلت (خطأ باسوورد مثلاً)
(5, 'login', 'Success', '192.168.1.100'); -- أحمد دخل