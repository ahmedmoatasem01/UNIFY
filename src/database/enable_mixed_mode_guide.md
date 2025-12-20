# Enable SQL Server Mixed Mode Authentication

## Method 1: Using SQL Server Management Studio (SSMS) - RECOMMENDED

1. **Open SQL Server Management Studio (SSMS)**
   - Connect to your SQL Server instance: `DESKTOP-V6DPJFP\SQLEXPRESS`

2. **Enable Mixed Mode Authentication**
   - Right-click on your server name in Object Explorer
   - Select **Properties**
   - Go to the **Security** page (left panel)
   - Under "Server authentication", select:
     - ✅ **SQL Server and Windows Authentication mode**
   - Click **OK**

3. **Restart SQL Server Service**
   - Open **Services** (services.msc)
   - Find **SQL Server (SQLEXPRESS)**
   - Right-click → **Restart**
   - Or use command: `net stop MSSQL$SQLEXPRESS` then `net start MSSQL$SQLEXPRESS`

4. **Verify the Setting**
   - Reconnect to SQL Server in SSMS
   - Try connecting with SQL Server Authentication

## Method 2: Using T-SQL (Requires Sysadmin)

If you have sysadmin privileges, you can run:

```sql
USE master;
GO

-- Enable Mixed Mode (2 = Mixed, 1 = Windows only)
EXEC xp_instance_regwrite 
    N'HKEY_LOCAL_MACHINE', 
    N'Software\Microsoft\MSSQLServer\MSSQLServer',
    N'LoginMode', 
    REG_DWORD, 
    2;
GO
```

**Then restart SQL Server service** (must restart for changes to take effect).

## Method 3: Using PowerShell (Run as Administrator)

```powershell
# Set Mixed Mode authentication
$instance = "SQLEXPRESS"
$regPath = "HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL16.$instance\MSSQLServer"
Set-ItemProperty -Path $regPath -Name LoginMode -Value 2

# Restart SQL Server service
Restart-Service "MSSQL`$$instance"
```

## After Enabling Mixed Mode

1. Run the `setup_docker_user.sql` script to create the Docker user
2. Restart SQL Server service if you used Method 1 or 3
3. Test the connection using the created credentials

## Security Notes

⚠️ **Important:**
- Change the default password in `setup_docker_user.sql` before using in production
- Use strong passwords for SQL logins
- Consider using SQL Server's password policy requirements
- Limit permissions to only what's needed (principle of least privilege)

