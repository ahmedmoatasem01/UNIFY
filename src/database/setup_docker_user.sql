-- =============================================
-- SQL Server Authentication Setup for Docker
-- =============================================
-- This script sets up SQL Server Authentication for Docker connections
--
-- IMPORTANT: 
-- 1. Some steps (like enabling Mixed Mode) require SSMS or server-level permissions
-- 2. Run this script as a user with sysadmin privileges
-- =============================================

USE master;
GO

-- =============================================
-- Step 1: Enable SQL Server Authentication (Mixed Mode)
-- =============================================
-- NOTE: This typically needs to be done through SSMS:
--   Right-click server → Properties → Security → 
--   Select "SQL Server and Windows Authentication mode"
--   Then restart SQL Server service
--
-- Or via T-SQL (requires sysadmin):
EXEC xp_instance_regwrite 
    N'HKEY_LOCAL_MACHINE', 
    N'Software\Microsoft\MSSQLServer\MSSQLServer',
    N'LoginMode', 
    REG_DWORD, 
    2;  -- 2 = Mixed Mode, 1 = Windows Auth only
GO

PRINT 'Mixed Mode authentication enabled. SQL Server service restart required for changes to take effect.';
GO

-- =============================================
-- Step 2: Create SQL Login User for Docker
-- =============================================
-- Create a login for Docker connections
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'docker_user')
BEGIN
    CREATE LOGIN docker_user 
    WITH PASSWORD = 'DockerUnify2024!@#',  -- Change this to a strong password
         DEFAULT_DATABASE = unify,
         CHECK_EXPIRATION = OFF,
         CHECK_POLICY = ON;
    PRINT 'Login ''docker_user'' created successfully.';
END
ELSE
BEGIN
    PRINT 'Login ''docker_user'' already exists.';
END
GO

-- =============================================
-- Step 3: Create User in unify Database
-- =============================================
USE unify;
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'docker_user')
BEGIN
    CREATE USER docker_user FOR LOGIN docker_user;
    PRINT 'User ''docker_user'' created in unify database.';
END
ELSE
BEGIN
    PRINT 'User ''docker_user'' already exists in unify database.';
END
GO

-- =============================================
-- Step 4: Grant Permissions
-- =============================================
-- Grant necessary permissions to docker_user
ALTER ROLE db_datareader ADD MEMBER docker_user;
ALTER ROLE db_datawriter ADD MEMBER docker_user;
ALTER ROLE db_ddladmin ADD MEMBER docker_user;  -- Allow schema changes if needed

-- Or grant more specific permissions:
-- GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO docker_user;
-- GRANT EXECUTE ON SCHEMA::dbo TO docker_user;

PRINT 'Permissions granted to docker_user.';
GO

-- =============================================
-- Step 5: Verify Setup
-- =============================================
SELECT 
    name AS LoginName,
    type_desc AS LoginType,
    is_disabled,
    default_database_name
FROM sys.server_principals
WHERE name = 'docker_user';

SELECT 
    dp.name AS UserName,
    dp.type_desc AS UserType,
    ISNULL(USER_NAME(dp.default_schema_name), 'dbo') AS DefaultSchema
FROM sys.database_principals dp
WHERE dp.name = 'docker_user';
GO

PRINT '=============================================';
PRINT 'Setup completed!';
PRINT '=============================================';
PRINT 'IMPORTANT:';
PRINT '1. RESTART SQL Server service for Mixed Mode to take effect';
PRINT '2. Change the password in this script before running in production';
PRINT '3. Use these credentials in Docker:';
PRINT '   DB_USER=docker_user';
PRINT '   DB_PASSWORD=DockerUnify2024!@#';
PRINT '=============================================';
GO

