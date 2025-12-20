# Test SQL Server Connection - Step by Step

## Current Status
✅ SQL Server (SQLEXPRESS) is **RUNNING**
❌ Connection is failing - likely server name or protocol issue

## Step 1: Test Connection in SSMS

Try connecting with these server names (one at a time):

### Option 1: localhost
```
Server name: localhost\SQLEXPRESS
Authentication: Windows Authentication
```

### Option 2: Dot notation
```
Server name: .\SQLEXPRESS
Authentication: Windows Authentication
```

### Option 3: Local
```
Server name: (local)\SQLEXPRESS
Authentication: Windows Authentication
```

### Option 4: Computer name
```
Server name: DESKTOP-V6DPJFP\SQLEXPRESS
Authentication: Windows Authentication
```

**Which one works?** Once you find the working name, note it down.

## Step 2: Enable TCP/IP Protocol (If Connection Still Fails)

1. **Open SQL Server Configuration Manager**
   - Press `Windows Key`
   - Type: `SQL Server Configuration Manager`
   - Press Enter

2. **Enable TCP/IP**:
   - Expand: **SQL Server Network Configuration**
   - Click: **Protocols for SQLEXPRESS**
   - Right-click **TCP/IP** → **Enable**
   - Right-click **Named Pipes** → **Enable** (optional but recommended)

3. **Restart SQL Server**:
   - Go back to Services (`services.msc`)
   - Right-click **SQL Server (SQLEXPRESS)** → **Restart**

4. **Try connecting again** in SSMS

## Step 3: Update Connection String (After Finding Working Name)

Once you know which server name works in SSMS, we'll update the connection string in:
- `src/core/db_singleton.py`

## Step 4: Verify Database Exists

After connecting successfully in SSMS:

1. Expand **Databases** in Object Explorer
2. Look for **unify** database
3. If it doesn't exist:
   - Right-click **Databases** → **New Database**
   - Name: `unify`
   - Click **OK**

## Quick Test Script

After finding the working server name, we can test with:

```powershell
# Set environment variable with working server name
$env:DB_HOST = "localhost\SQLEXPRESS"  # Use the name that worked
python src/database/check_unify_database.py
```

## Common Working Server Names

For **local SQL Server Express**:
- `localhost\SQLEXPRESS` ← **Try this first**
- `.\SQLEXPRESS`
- `(local)\SQLEXPRESS`

For **default instance**:
- `localhost`
- `.`
- `(local)`

