"""
User Database Configuration Repository
Manages database connection configurations for users
"""
from models.user_database_config import UserDatabaseConfig
from core.db_singleton import DatabaseConnection

class UserDatabaseConfigRepository:
    def __init__(self):
        # Use main/admin database for storing user database configs
        self.db = DatabaseConnection.get_instance()
    
    def create_table(self):
        """Create user database config table if it doesn't exist"""
        query = """
        CREATE TABLE IF NOT EXISTS User_Database_Config (
            Config_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            User_ID INTEGER NOT NULL UNIQUE,
            DB_Type TEXT NOT NULL DEFAULT 'sqlite',
            DB_Host TEXT,
            DB_Port INTEGER,
            DB_Name TEXT,
            DB_User TEXT,
            DB_Password TEXT,
            DB_Path TEXT,
            Is_Active INTEGER DEFAULT 1,
            Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
        )
        """
        self.db.execute_update(query)
    
    def add(self, config):
        """Add a new user database configuration"""
        query = """
        INSERT INTO User_Database_Config 
        (User_ID, DB_Type, DB_Host, DB_Port, DB_Name, DB_User, DB_Password, DB_Path, Is_Active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            config.User_ID,
            config.DB_Type,
            config.DB_Host,
            config.DB_Port,
            config.DB_Name,
            config.DB_User,
            config.DB_Password,
            config.DB_Path,
            1 if config.Is_Active else 0
        )
        return self.db.execute_update(query, params)
    
    def get_by_user_id(self, user_id):
        """Get database configuration for a user"""
        query = "SELECT * FROM User_Database_Config WHERE User_ID = ? AND Is_Active = 1"
        result = self.db.fetch_one(query, (user_id,))
        return self._map_to_object(result) if result else None
    
    def get_by_id(self, config_id):
        """Get database configuration by ID"""
        query = "SELECT * FROM User_Database_Config WHERE Config_ID = ?"
        result = self.db.fetch_one(query, (config_id,))
        return self._map_to_object(result) if result else None
    
    def get_all(self):
        """Get all database configurations"""
        query = "SELECT * FROM User_Database_Config ORDER BY Created_Date DESC"
        results = self.db.fetch_all(query)
        return [self._map_to_object(row) for row in results] if results else []
    
    def update(self, config):
        """Update user database configuration"""
        query = """
        UPDATE User_Database_Config
        SET DB_Type = ?, DB_Host = ?, DB_Port = ?, DB_Name = ?, 
            DB_User = ?, DB_Password = ?, DB_Path = ?, Is_Active = ?
        WHERE Config_ID = ?
        """
        params = (
            config.DB_Type,
            config.DB_Host,
            config.DB_Port,
            config.DB_Name,
            config.DB_User,
            config.DB_Password,
            config.DB_Path,
            1 if config.Is_Active else 0,
            config.Config_ID
        )
        return self.db.execute_update(query, params)
    
    def delete(self, config_id):
        """Delete (deactivate) a database configuration"""
        query = "UPDATE User_Database_Config SET Is_Active = 0 WHERE Config_ID = ?"
        return self.db.execute_update(query, (config_id,))
    
    def _map_to_object(self, row):
        """Map database row to UserDatabaseConfig object"""
        if not row:
            return None
        return UserDatabaseConfig(
            config_id=row[0],
            user_id=row[1],
            db_type=row[2] if len(row) > 2 else 'sqlite',
            db_host=row[3] if len(row) > 3 else None,
            db_port=row[4] if len(row) > 4 else None,
            db_name=row[5] if len(row) > 5 else None,
            db_user=row[6] if len(row) > 6 else None,
            db_password=row[7] if len(row) > 7 else None,
            db_path=row[8] if len(row) > 8 else None,
            is_active=bool(row[9]) if len(row) > 9 else True,
            created_date=row[10] if len(row) > 10 else None
        )
