-- =============================================
-- Quick Setup: Docker User for UNIFY Database
-- =============================================
-- Run this script AFTER enabling Mixed Mode Authentication
-- Run as a user with sysadmin or sufficient privileges
-- =============================================

USE master;
GO

-- Create login (change password as needed)
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'docker_user')
BEGIN
    CREATE LOGIN docker_user 
    WITH PASSWORD = 'DockerUnify2024!@#',  -- ⚠️ CHANGE THIS PASSWORD
         DEFAULT_DATABASE = unify,
         CHECK_EXPIRATION = OFF,
         CHECK_POLICY = ON;
    PRINT '✓ Login created: docker_user';
END
ELSE
    PRINT '✓ Login already exists: docker_user';
GO

USE unify;
GO

-- Create user in unify database
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'docker_user')
BEGIN
    CREATE USER docker_user FOR LOGIN docker_user;
    PRINT '✓ User created in unify database';
END
ELSE
    PRINT '✓ User already exists in unify database';
GO

-- Grant permissions
ALTER ROLE db_datareader ADD MEMBER docker_user;
ALTER ROLE db_datawriter ADD MEMBER docker_user;
PRINT '✓ Permissions granted (read/write access)';
GO

-- Display summary
SELECT 
    'Login' AS Type,
    name AS Name,
    type_desc AS Details
FROM sys.server_principals
WHERE name = 'docker_user'

UNION ALL

SELECT 
    'Database User' AS Type,
    name AS Name,
    type_desc AS Details
FROM sys.database_principals
WHERE name = 'docker_user';
GO

PRINT '';
PRINT '========================================';
PRINT 'Docker User Setup Complete!';
PRINT '========================================';
PRINT 'Use these environment variables:';
PRINT '  DB_USER=docker_user';
PRINT '  DB_PASSWORD=DockerUnify2024!@#';
PRINT '========================================';
GO

