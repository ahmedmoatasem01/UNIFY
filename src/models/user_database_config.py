"""
User Database Configuration Model
Stores database connection information for each user/tenant
"""

class UserDatabaseConfig:
    def __init__(self, config_id=None, user_id=None, db_type='sqlite', 
                 db_host=None, db_port=None, db_name=None, 
                 db_user=None, db_password=None, db_path=None,
                 is_active=True, created_date=None):
        self.Config_ID = config_id
        self.User_ID = user_id
        self.DB_Type = db_type  # sqlite, mysql, postgresql, sqlserver
        self.DB_Host = db_host
        self.DB_Port = db_port
        self.DB_Name = db_name
        self.DB_User = db_user
        self.DB_Password = db_password
        self.DB_Path = db_path  # For SQLite
        self.Is_Active = is_active
        self.Created_Date = created_date
    
    def to_dict(self):
        return {
            'Config_ID': self.Config_ID,
            'User_ID': self.User_ID,
            'DB_Type': self.DB_Type,
            'DB_Host': self.DB_Host,
            'DB_Port': self.DB_Port,
            'DB_Name': self.DB_Name,
            'DB_User': self.DB_User,
            'DB_Password': '****' if self.DB_Password else None,  # Never expose password
            'DB_Path': self.DB_Path,
            'Is_Active': self.Is_Active,
            'Created_Date': self.Created_Date
        }
    
    def get_connection_string(self):
        """Generate connection string based on database type"""
        if self.DB_Type == 'sqlite':
            return self.DB_Path or f'data/user_{self.User_ID}.db'
        elif self.DB_Type == 'mysql':
            return f"mysql://{self.DB_User}:{self.DB_Password}@{self.DB_Host}:{self.DB_Port or 3306}/{self.DB_Name}"
        elif self.DB_Type == 'postgresql':
            return f"postgresql://{self.DB_User}:{self.DB_Password}@{self.DB_Host}:{self.DB_Port or 5432}/{self.DB_Name}"
        elif self.DB_Type == 'sqlserver':
            return f"mssql://{self.DB_User}:{self.DB_Password}@{self.DB_Host}:{self.DB_Port or 1433}/{self.DB_Name}"
        return None
    
    def __repr__(self):
        return f"<UserDatabaseConfig {self.Config_ID}: User {self.User_ID} - {self.DB_Type}>"
