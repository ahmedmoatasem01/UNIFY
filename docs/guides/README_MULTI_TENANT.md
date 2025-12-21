# Multi-Tenant Database System

## Overview

The Unify application now supports **multi-tenant architecture** where each user can have their own separate database. This provides complete data isolation between users and enables better scalability and security.

## Features

✅ **Per-User Databases** - Each user gets their own database  
✅ **Multiple Database Types** - Support for SQLite, SQL Server, MySQL, PostgreSQL  
✅ **Automatic Initialization** - Databases are created automatically on user registration  
✅ **Seamless Switching** - Context automatically switches based on logged-in user  
✅ **Backward Compatible** - Can be disabled to use single shared database  
✅ **Secure Storage** - Database credentials stored securely in main database  

## Architecture

```
Main/Admin Database (SQL Server)
├── Users Table
├── User_Database_Config Table
└── ... (shared tables)

User 1 Database (SQLite/SQL Server)
├── Tasks
├── Notes
├── Events
└── ... (user-specific data)

User 2 Database (SQLite/SQL Server)
├── Tasks
├── Notes
├── Events
└── ... (user-specific data)
```

## How It Works

1. **Main Database**: Stores user accounts, authentication, and database configurations
2. **User Databases**: Each user has their own database for their personal data
3. **Context Switching**: When a user logs in, the system switches to their database
4. **Automatic Creation**: New user databases are created on registration

## Setup Instructions

### Step 1: Create Configuration Table

Run the setup utility to create the `User_Database_Config` table:

```powershell
cd src\utils
python setup_user_database.py
```

Select option **1** to create the configuration table.

### Step 2: Initialize User Databases

You have three options:

**Option A: Initialize All Users**
```powershell
python setup_user_database.py
```
Select option **3** to initialize databases for all existing users.

**Option B: Initialize Specific User**
```powershell
python setup_user_database.py
```
Select option **2** and enter the user ID.

**Option C: Automatic on Registration**
- New users get databases automatically when they register
- No manual setup needed

### Step 3: Enable Multi-Tenant Mode

Set the environment variable:

**Windows (PowerShell):**
```powershell
$env:MULTI_TENANT_MODE="true"
```

**Windows (CMD):**
```cmd
set MULTI_TENANT_MODE=true
```

**Or create a `.env` file:**
```
MULTI_TENANT_MODE=true
```

### Step 4: Start the Application

```powershell
python app.py
```

The application will now use per-user databases!

## Database Types

### SQLite (Default)

- **Location**: `src/data/users/user_{id}.db`
- **Pros**: Simple, no configuration, portable
- **Cons**: Limited concurrent writes
- **Best For**: Small to medium workloads

```python
# Automatically configured for each user
# No setup required
```

### SQL Server

- **Pros**: High performance, enterprise features
- **Cons**: Requires server setup
- **Best For**: Large deployments, high concurrency

```python
# Configuration when initializing:
initialize_user_database(
    user_id=1,
    db_type='sqlserver',
    db_host='localhost\\SQLEXPRESS',
    db_port=1433,
    db_name='user_1_db',
    db_user='sa',
    db_password='password'
)
```

### MySQL

- **Pros**: Popular, well-supported
- **Cons**: Requires mysql-connector-python
- **Best For**: Web applications

```bash
pip install mysql-connector-python
```

### PostgreSQL

- **Pros**: Advanced features, open source
- **Cons**: Requires psycopg2
- **Best For**: Complex queries, JSON data

```bash
pip install psycopg2-binary
```

## Usage Examples

### In Controllers

```python
from flask import session
from core.db_singleton import DatabaseConnection

def my_route():
    # Database context is automatically set from session
    db = DatabaseConnection.get_instance()
    
    # All queries now use the logged-in user's database
    results = db.fetch_all("SELECT * FROM Tasks")
    return jsonify(results)
```

### Manual Context Switching

```python
from core.db_singleton import DatabaseConnection

db = DatabaseConnection.get_instance()

# Switch to user 5's database
db.set_user_context(5)

# Query user 5's data
tasks = db.fetch_all("SELECT * FROM Tasks")

# Clear context (returns to main database)
db.clear_user_context()
```

### Using Multi-Tenant Manager

```python
from core.multi_tenant_db import MultiTenantDatabaseManager

db_manager = MultiTenantDatabaseManager()

# Set current user
db_manager.set_current_user(user_id)

# Get user's connection
conn = db_manager.get_user_connection()

# Execute queries
results = db_manager.fetch_all("SELECT * FROM Tasks", user_id=user_id)

# Execute updates
db_manager.execute_update(
    "INSERT INTO Tasks (Title, Description) VALUES (?, ?)",
    ("New Task", "Task description"),
    user_id=user_id
)
```

## Configuration

### User_Database_Config Table Schema

```sql
CREATE TABLE User_Database_Config (
    Config_ID INT PRIMARY KEY IDENTITY(1,1),
    User_ID INT NOT NULL UNIQUE,
    DB_Type NVARCHAR(50) NOT NULL DEFAULT 'sqlite',
    DB_Host NVARCHAR(255),
    DB_Port INT,
    DB_Name NVARCHAR(255),
    DB_User NVARCHAR(255),
    DB_Password NVARCHAR(255),  -- Encrypted in production!
    DB_Path NVARCHAR(500),
    Is_Active BIT DEFAULT 1,
    Created_Date DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
)
```

### Standard User Database Tables

Each user database includes:

- **Tasks**: User's tasks and to-dos
- **Notes**: Personal notes
- **Events**: Calendar events
- (Additional tables as needed)

## Testing

### Test User Database

```powershell
cd src\utils
python setup_user_database.py
```

Select option **4** and enter a user ID to test their database connection.

### Test in Python

```python
from core.multi_tenant_db import MultiTenantDatabaseManager

# Initialize
db_manager = MultiTenantDatabaseManager()

# Test connection
config = db_manager.initialize_user_database(1, db_type='sqlite')
print(f"Database created: {config['db_path']}")

# Test query
db_manager.execute_update(
    "INSERT INTO Tasks (Title) VALUES (?)",
    ("Test Task",),
    user_id=1
)

results = db_manager.fetch_all("SELECT * FROM Tasks", user_id=1)
print(f"Found {len(results)} tasks")
```

## Migration from Single Database

If you're migrating from a single shared database:

### Option 1: Copy Data Per User

```python
from core.db_singleton import DatabaseConnection
from core.multi_tenant_db import MultiTenantDatabaseManager

# Get main database connection
main_db = DatabaseConnection.get_instance()
main_db.clear_user_context()

# Get all users
users = main_db.fetch_all("SELECT User_ID FROM Users")

# Initialize databases
db_manager = MultiTenantDatabaseManager()

for user in users:
    user_id = user[0]
    
    # Initialize user database
    db_manager.initialize_user_database(user_id, db_type='sqlite')
    
    # Copy user's data
    # Tasks
    tasks = main_db.fetch_all(
        "SELECT * FROM Tasks WHERE User_ID = ?",
        (user_id,)
    )
    
    for task in tasks:
        db_manager.execute_update(
            "INSERT INTO Tasks (Title, Description, Due_Date) VALUES (?, ?, ?)",
            (task[1], task[2], task[3]),  # Adjust indices
            user_id=user_id
        )
    
    print(f"Migrated data for user {user_id}")
```

### Option 2: Keep Shared Database

Simply don't enable multi-tenant mode. The system works in single-database mode by default.

## Security Considerations

### Database Credentials

⚠️ **Important**: The current implementation stores database passwords in plain text. For production:

```python
# Use encryption for passwords
from cryptography.fernet import Fernet

# Generate key (store securely!)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt password before storing
encrypted_password = cipher.encrypt(password.encode())

# Decrypt when loading
decrypted_password = cipher.decrypt(encrypted_password).decode()
```

### Access Control

- Users can only access their own database
- Context switching requires authentication
- Admin users can access any database (implement carefully!)

### Backup Strategy

```powershell
# Backup all user databases
$users = Get-ChildItem -Path "src\data\users\*.db"
foreach ($db in $users) {
    Copy-Item $db.FullName "backups\$(Get-Date -Format 'yyyyMMdd')_$($db.Name)"
}
```

## Troubleshooting

### Issue: "User database not found"

**Solution**: Initialize the user's database:
```powershell
python src\utils\setup_user_database.py
# Select option 2, enter user ID
```

### Issue: "Connection failed"

**Solution**: Check database configuration:
```python
from core.multi_tenant_db import MultiTenantDatabaseManager

db_manager = MultiTenantDatabaseManager()
config = db_manager.load_user_db_config(user_id)
print(config)
```

### Issue: "Wrong database context"

**Solution**: Verify context is set:
```python
from core.db_singleton import DatabaseConnection

db = DatabaseConnection.get_instance()
print(f"Current user: {db.current_user_id}")
```

### Issue: "Table not found"

**Solution**: Create tables in user database:
```python
from core.multi_tenant_db import MultiTenantDatabaseManager

db_manager = MultiTenantDatabaseManager()
conn = db_manager.get_user_connection(user_id)
cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS MyTable (
        ID INTEGER PRIMARY KEY,
        Data TEXT
    )
""")
conn.commit()
conn.close()
```

## Performance Optimization

### Connection Pooling

For high-traffic applications, implement connection pooling:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

def get_pooled_engine(connection_string):
    return create_engine(
        connection_string,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20
    )
```

### Caching

Cache database configurations:

```python
# Already implemented in MultiTenantDatabaseManager
self.user_db_configs = {}  # Config cache
```

### Database Sharding

For very large deployments, consider sharding by user groups:

```
Server 1: Users 1-1000
Server 2: Users 1001-2000
Server 3: Users 2001-3000
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Create user data directory
RUN mkdir -p src/data/users

# Set environment
ENV MULTI_TENANT_MODE=true

# Run application
CMD ["python", "app.py"]
```

### Volume Mounting

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./src/data/users:/app/src/data/users
    environment:
      - MULTI_TENANT_MODE=true
```

## API Endpoints

### Database Management API (Optional)

You can create admin endpoints:

```python
@app.route('/admin/user/<int:user_id>/database/info')
def get_user_db_info(user_id):
    # Require admin authentication
    from repositories.repository_factory import RepositoryFactory
    
    repo = RepositoryFactory.get_repository('user_database_config')
    config = repo.get_by_user_id(user_id)
    
    return jsonify(config.to_dict())

@app.route('/admin/user/<int:user_id>/database/initialize', methods=['POST'])
def initialize_user_db(user_id):
    # Require admin authentication
    from core.multi_tenant_db import MultiTenantDatabaseManager
    
    db_manager = MultiTenantDatabaseManager()
    config = db_manager.initialize_user_database(user_id, db_type='sqlite')
    
    return jsonify({'success': True, 'config': config})
```

## Monitoring

Track database usage:

```python
import os
from pathlib import Path

def get_user_database_stats():
    """Get statistics about user databases"""
    users_dir = Path('src/data/users')
    
    stats = {
        'total_databases': 0,
        'total_size_mb': 0,
        'databases': []
    }
    
    for db_file in users_dir.glob('*.db'):
        size_mb = db_file.stat().st_size / (1024 * 1024)
        stats['total_databases'] += 1
        stats['total_size_mb'] += size_mb
        
        stats['databases'].append({
            'name': db_file.name,
            'size_mb': round(size_mb, 2),
            'modified': db_file.stat().st_mtime
        })
    
    return stats
```

## Future Enhancements

Potential improvements:

1. **Automatic Scaling**: Auto-create new database servers based on load
2. **Database Replication**: Replicate user databases for high availability
3. **Cross-User Collaboration**: Share data between specific users
4. **Database Analytics**: Track usage patterns per user
5. **Automated Backups**: Schedule regular backups per user
6. **Multi-Region Support**: Distribute databases geographically

## Support

For issues or questions:

1. Check this documentation
2. Run the setup utility diagnostics
3. Check application logs
4. Review database configurations

---

**Note**: Always backup your databases before making configuration changes!
