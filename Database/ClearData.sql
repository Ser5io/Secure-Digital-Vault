-- Clear all records and reset the database to a fresh state
USE AlMakhzan;
GO

-- 1. Delete all data
-- We delete from dependent tables first (though CASCADE would handle this if we deleted Users)
DELETE FROM MFA_Codes;
DELETE FROM Access_Logs;
DELETE FROM Files;
DELETE FROM Users;

-- 2. Reset Identity seeds
-- This ensures the next record created will have an ID of 1
DBCC CHECKIDENT ('Users', RESEED, 0);
DBCC CHECKIDENT ('Files', RESEED, 0);
DBCC CHECKIDENT ('Access_Logs', RESEED, 0);
DBCC CHECKIDENT ('MFA_Codes', RESEED, 0);
GO

PRINT '✅ All records removed and identity seeds reset successfully.';
