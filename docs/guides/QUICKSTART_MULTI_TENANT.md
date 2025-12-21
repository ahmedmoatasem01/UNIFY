# Quick Start: Multi-Tenant Database System

## What You Get

Each user gets their own **separate database** for complete data isolation and security!

```
User 1 → Database 1 (only User 1's data)
User 2 → Database 2 (only User 2's data)
User 3 → Database 3 (only User 3's data)
```

## Setup in 3 Steps

### Step 1: Create Configuration Table (One-time setup)

```powershell
cd c:\Users\Acer\Desktop\Unify\UNIFY\src\utils
python setup_user_database.py
```

Press **1** → Enter → Done! ✅

### Step 2: Initialize User Databases

**Option A - All Users at Once:**
```powershell
python setup_user_database.py
```
Press **3** → Type `yes` → Enter → Done! ✅

**Option B - Specific User:**
```powershell
python setup_user_database.py
```
Press **2** → Enter User ID → Select `sqlite` → Done! ✅

### Step 3: Enable Multi-Tenant Mode

**PowerShell:**
```powershell
$env:MULTI_TENANT_MODE="true"
python app.py
```

**OR Create `.env` file:**
```
MULTI_TENANT_MODE=true
```

Then start app:
```powershell
python app.py
```

## That's It! 🎉

Now every user has their own database automatically!

## Test It

```powershell
# In the setup utility
python setup_user_database.py
```
Press **4** → Enter User ID → Test connection!

## What Happens?

### When User Registers:
1. User account created in main database
2. Personal database created automatically (SQLite file)
3. Tables created (Tasks, Notes, Events, etc.)

### When User Logs In:
1. Session created
2. Database context switches to user's database
3. All queries use user's database

### When User Logs Out:
1. Database context cleared
2. Returns to main database

## File Structure

```
src/
├── data/
│   └── users/
│       ├── user_1.db   ← User 1's database
│       ├── user_2.db   ← User 2's database
│       └── user_3.db   ← User 3's database
├── core/
│   ├── db_singleton.py         ← Updated with multi-tenant
│   └── multi_tenant_db.py      ← New! Multi-tenant manager
├── models/
│   └── user_database_config.py ← New! DB config model
├── repositories/
│   └── user_database_config.repository.py ← New! DB config repo
└── utils/
    └── setup_user_database.py  ← New! Setup utility
```

## Features

✅ **Auto-creation**: New users get databases automatically  
✅ **SQLite default**: No extra setup needed  
✅ **SQL Server support**: For enterprise needs  
✅ **MySQL & PostgreSQL**: Optional database types  
✅ **Secure**: Complete data isolation between users  
✅ **Backward compatible**: Works with existing code  

## Disable Multi-Tenant Mode

Just don't set the environment variable:

```powershell
# Remove or comment out
# $env:MULTI_TENANT_MODE="true"

python app.py
```

System works in single-database mode!

## Troubleshooting

### "Table User_Database_Config doesn't exist"
**Fix:** Run Step 1 again

### "User database not found"
**Fix:** Run Step 2 for that user

### "Connection error"
**Fix:** Check if user database file exists:
```powershell
ls src\data\users\
```

## Advanced: SQL Server per User

```powershell
python setup_user_database.py
```

Press **2** → Enter User ID → Select `sqlserver` → Enter:
- Host: `localhost\SQLEXPRESS`
- Port: `1433`
- Database Name: `user_1_db`
- User: `sa`
- Password: `your_password`

Done! User now has SQL Server database.

## Need Help?

1. Read `README_MULTI_TENANT.md` for full documentation
2. Check setup utility (option 4) to test connections
3. Review logs for error messages

## What's Created?

### Main Database (SQL Server):
```sql
-- New table for storing user DB configs
User_Database_Config (
    Config_ID,
    User_ID,
    DB_Type,      -- 'sqlite', 'sqlserver', etc.
    DB_Path,      -- For SQLite
    DB_Host,      -- For SQL Server
    ...
)
```

### Each User Database (SQLite):
```sql
-- Standard tables for each user
Tasks
Notes
Events
-- Add more as needed
```

## Benefits

🔒 **Security**: Users can't access each other's data  
📊 **Scalability**: Easy to move users to different servers  
🚀 **Performance**: No contention between users  
💾 **Backup**: Backup each user independently  
🔧 **Flexibility**: Different database types per user  

## Example Usage in Code

The magic happens automatically!

```python
# In your controllers/routes
from flask import session
from core.db_singleton import DatabaseConnection

@app.route('/my-tasks')
def get_tasks():
    # Database context is ALREADY SET from login!
    db = DatabaseConnection.get_instance()
    
    # This queries the CURRENT USER's database automatically!
    tasks = db.fetch_all("SELECT * FROM Tasks")
    
    return jsonify(tasks)
```

No extra code needed! 🎯

## Next Steps

1. ✅ Run the 3-step setup above
2. 📚 Read `README_MULTI_TENANT.md` for details
3. 🧪 Test with multiple users
4. 🚀 Deploy with confidence!

---

**Questions?** Check the full documentation in `README_MULTI_TENANT.md`
