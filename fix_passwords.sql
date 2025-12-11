-- ============================================================
-- Fix Password Hashes - UPDATE Script
-- This updates all existing users with the correct password hash
-- Password for all users: password123
-- ============================================================

USE unify;
GO

PRINT '============================================================';
PRINT 'Updating password hashes for all users...';
PRINT 'New password for ALL users: password123';
PRINT '============================================================';

-- Update all users with the correct SHA256 hash of "password123"
UPDATE [User]
SET Password_Hash = 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'
WHERE Password_Hash IN ('hashed_password_1', 'hashed_password_2', 'hashed_password_3', 
                        'hashed_password_4', 'hashed_password_5', 'hashed_password_6');

PRINT '';
PRINT 'Password update complete!';
PRINT '';
PRINT '============================================================';
PRINT 'LOGIN CREDENTIALS (Updated)';
PRINT '============================================================';
PRINT '';
PRINT 'All users now have password: password123';
PRINT '';
PRINT 'Student Accounts:';
PRINT '  Email: ahmed.hasan@student.zewailcity.edu.eg';
PRINT '  Email: sara.mohamed@student.zewailcity.edu.eg';
PRINT '  Email: mohamed.ali@student.zewailcity.edu.eg';
PRINT '';
PRINT 'Instructor Accounts:';
PRINT '  Email: khalid.ahmed@zewailcity.edu.eg';
PRINT '  Email: nour.mohamed@zewailcity.edu.eg';
PRINT '  Email: amr.sayed@zewailcity.edu.eg';
PRINT '';
PRINT '============================================================';
PRINT 'Next Steps:';
PRINT '1. Go to: http://localhost:5000/login';
PRINT '2. Login with any email above';
PRINT '3. Password: password123';
PRINT '4. Navigate to Transcript page!';
PRINT '============================================================';
GO

-- Verify the update
SELECT User_ID, Username, Email, 
       CASE 
         WHEN Password_Hash = 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f' 
         THEN 'CORRECT (password123)' 
         ELSE 'WRONG' 
       END AS Password_Status
FROM [User];
GO

