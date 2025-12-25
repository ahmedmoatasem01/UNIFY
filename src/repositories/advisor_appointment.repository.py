"""
Advisor Appointment Repository
Handles database operations for advisor appointments
"""
from models.advisor_appointment import AdvisorAppointment
from core.db_singleton import DatabaseConnection
from datetime import datetime


class AdvisorAppointmentRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def create_table(self):
        """Create advisor appointment table if it doesn't exist"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[AdvisorAppointment]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE AdvisorAppointment (
                        Appointment_ID INT IDENTITY(1,1) PRIMARY KEY,
                        Student_ID INT NOT NULL,
                        Advisor_ID INT NOT NULL,
                        Scheduled_Date DATETIME NOT NULL,
                        Reason NVARCHAR(MAX),
                        Status NVARCHAR(20) CHECK (Status IN ('pending', 'scheduled', 'completed', 'cancelled', 'rejected')) DEFAULT 'pending',
                        Instructor_Response NVARCHAR(MAX),
                        Created_From_Conversation_ID INT,
                        FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
                        FOREIGN KEY (Advisor_ID) REFERENCES Instructor(Instructor_ID),
                        FOREIGN KEY (Created_From_Conversation_ID) REFERENCES AdvisorConversation(Conversation_ID)
                    )
                END
            """)
            
            # Add Instructor_Response column if it doesn't exist (for existing tables)
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[AdvisorAppointment]') AND name = 'Instructor_Response')
                    BEGIN
                        ALTER TABLE AdvisorAppointment ADD Instructor_Response NVARCHAR(MAX)
                    END
                """)
                
                # Update CHECK constraint for Status column to include 'pending' and 'rejected'
                cursor.execute("""
                    DECLARE @ConstraintName NVARCHAR(200)
                    DECLARE @SQL NVARCHAR(MAX)
                    
                    -- Find and drop existing Status check constraints
                    DECLARE constraint_cursor CURSOR FOR
                    SELECT cc.name 
                    FROM sys.check_constraints cc
                    INNER JOIN sys.columns c ON c.object_id = cc.parent_object_id AND c.column_id = cc.parent_column_id
                    WHERE cc.parent_object_id = OBJECT_ID(N'[dbo].[AdvisorAppointment]')
                    AND c.name = 'Status'
                    
                    OPEN constraint_cursor
                    FETCH NEXT FROM constraint_cursor INTO @ConstraintName
                    
                    WHILE @@FETCH_STATUS = 0
                    BEGIN
                        SET @SQL = 'ALTER TABLE [dbo].[AdvisorAppointment] DROP CONSTRAINT [' + @ConstraintName + ']'
                        EXEC sp_executesql @SQL
                        FETCH NEXT FROM constraint_cursor INTO @ConstraintName
                    END
                    
                    CLOSE constraint_cursor
                    DEALLOCATE constraint_cursor
                """)
                
                # Add new constraint with all allowed values
                cursor.execute("""
                    IF NOT EXISTS (
                        SELECT * FROM sys.check_constraints 
                        WHERE name = 'CK_AdvisorAppointment_Status' 
                        AND parent_object_id = OBJECT_ID(N'[dbo].[AdvisorAppointment]')
                    )
                    BEGIN
                        ALTER TABLE AdvisorAppointment
                        ADD CONSTRAINT CK_AdvisorAppointment_Status 
                        CHECK (Status IN ('pending', 'scheduled', 'completed', 'cancelled', 'rejected'))
                    END
                """)
            except Exception as e:
                print(f"Warning: Could not update Status constraint or add Instructor_Response column: {e}")
            
            conn.commit()
        except Exception as e:
            print(f"Error creating AdvisorAppointment table: {e}")
            import traceback
            traceback.print_exc()
        finally:
            cursor.close()
            conn.close()
    
    def create(self, appointment):
        """Create a new appointment"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO AdvisorAppointment (Student_ID, Advisor_ID, Scheduled_Date, Reason, Status, Created_From_Conversation_ID, Instructor_Response)
            OUTPUT INSERTED.Appointment_ID
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(
                query,
                (appointment.Student_ID, appointment.Advisor_ID, appointment.Scheduled_Date,
                 appointment.Reason, appointment.Status, appointment.Created_From_Conversation_ID,
                 getattr(appointment, 'Instructor_Response', None))
            )
            row = cursor.fetchone()
            if row:
                appointment.Appointment_ID = row[0]
            conn.commit()
            return appointment
        finally:
            cursor.close()
            conn.close()
    
    def get_by_id(self, appointment_id):
        """Get appointment by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Appointment_ID, Student_ID, Advisor_ID, Scheduled_Date, Reason, Status, Created_From_Conversation_ID, Instructor_Response "
                "FROM AdvisorAppointment WHERE Appointment_ID = ?",
                (appointment_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._map_to_object(row)
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_by_student(self, student_id):
        """Get all appointments for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Appointment_ID, Student_ID, Advisor_ID, Scheduled_Date, Reason, Status, Created_From_Conversation_ID, Instructor_Response "
                "FROM AdvisorAppointment WHERE Student_ID = ? ORDER BY Scheduled_Date DESC",
                (student_id,)
            )
            rows = cursor.fetchall()
            return [self._map_to_object(row) for row in rows] if rows else []
        finally:
            cursor.close()
            conn.close()
    
    def get_upcoming_by_student(self, student_id):
        """Get upcoming appointments for a student (includes pending, scheduled, and future appointments)"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT Appointment_ID, Student_ID, Advisor_ID, Scheduled_Date, Reason, Status, Created_From_Conversation_ID, Instructor_Response
                FROM AdvisorAppointment 
                WHERE Student_ID = ? 
                AND (Status IN ('pending', 'scheduled', 'completed') OR Scheduled_Date >= GETDATE())
                ORDER BY Scheduled_Date ASC
                """,
                (student_id,)
            )
            rows = cursor.fetchall()
            return [self._map_to_object(row) for row in rows] if rows else []
        finally:
            cursor.close()
            conn.close()
    
    def get_by_advisor(self, advisor_id):
        """Get all appointments for an advisor"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Appointment_ID, Student_ID, Advisor_ID, Scheduled_Date, Reason, Status, Created_From_Conversation_ID, Instructor_Response "
                "FROM AdvisorAppointment WHERE Advisor_ID = ? ORDER BY Scheduled_Date DESC",
                (advisor_id,)
            )
            rows = cursor.fetchall()
            return [self._map_to_object(row) for row in rows] if rows else []
        finally:
            cursor.close()
            conn.close()
    
    def update(self, appointment):
        """Update an appointment"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE AdvisorAppointment SET Scheduled_Date = ?, Reason = ?, Status = ?, Instructor_Response = ? WHERE Appointment_ID = ?",
                (appointment.Scheduled_Date, appointment.Reason, appointment.Status, 
                 getattr(appointment, 'Instructor_Response', None), appointment.Appointment_ID)
            )
            conn.commit()
            return appointment
        finally:
            cursor.close()
            conn.close()
    
    def _map_to_object(self, row):
        """Map database row to AdvisorAppointment object"""
        if not row:
            return None
        return AdvisorAppointment(
            Appointment_ID=row[0],
            Student_ID=row[1],
            Advisor_ID=row[2],
            Scheduled_Date=row[3],
            Reason=row[4],
            Status=row[5],
            Created_From_Conversation_ID=row[6] if len(row) > 6 else None,
            Instructor_Response=row[7] if len(row) > 7 else None
        )
