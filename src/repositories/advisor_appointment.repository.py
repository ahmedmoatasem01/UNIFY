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
        self.db = DatabaseConnection.get_instance()
    
    def create_table(self):
        """Create advisor appointment table if it doesn't exist"""
        try:
            query = """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AdvisorAppointment' AND xtype='U')
            CREATE TABLE AdvisorAppointment (
                Appointment_ID INT IDENTITY(1,1) PRIMARY KEY,
                Student_ID INT NOT NULL,
                Advisor_ID INT NOT NULL,
                Scheduled_Date DATETIME NOT NULL,
                Reason NVARCHAR(MAX),
                Status NVARCHAR(20) CHECK (Status IN ('scheduled', 'completed', 'cancelled')) DEFAULT 'scheduled',
                Created_From_Conversation_ID INT,
                FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
                FOREIGN KEY (Advisor_ID) REFERENCES Instructor(Instructor_ID),
                FOREIGN KEY (Created_From_Conversation_ID) REFERENCES AdvisorConversation(Conversation_ID)
            )
            """
            self.db.execute_update(query)
        except Exception as e:
            print(f"Error creating AdvisorAppointment table: {e}")
            import traceback
            traceback.print_exc()
    
    def create(self, appointment):
        """Create a new appointment"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO AdvisorAppointment (Student_ID, Advisor_ID, Scheduled_Date, Reason, Status, Created_From_Conversation_ID)
            OUTPUT INSERTED.Appointment_ID
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(
                query,
                (appointment.Student_ID, appointment.Advisor_ID, appointment.Scheduled_Date,
                 appointment.Reason, appointment.Status, appointment.Created_From_Conversation_ID)
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
                "SELECT Appointment_ID, Student_ID, Advisor_ID, Scheduled_Date, Reason, Status, Created_From_Conversation_ID "
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
                "SELECT Appointment_ID, Student_ID, Advisor_ID, Scheduled_Date, Reason, Status, Created_From_Conversation_ID "
                "FROM AdvisorAppointment WHERE Student_ID = ? ORDER BY Scheduled_Date DESC",
                (student_id,)
            )
            rows = cursor.fetchall()
            return [self._map_to_object(row) for row in rows] if rows else []
        finally:
            cursor.close()
            conn.close()
    
    def get_upcoming_by_student(self, student_id):
        """Get upcoming appointments for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT Appointment_ID, Student_ID, Advisor_ID, Scheduled_Date, Reason, Status, Created_From_Conversation_ID
                FROM AdvisorAppointment 
                WHERE Student_ID = ? AND Status = 'scheduled' AND Scheduled_Date >= GETDATE()
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
                "SELECT Appointment_ID, Student_ID, Advisor_ID, Scheduled_Date, Reason, Status, Created_From_Conversation_ID "
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
                "UPDATE AdvisorAppointment SET Scheduled_Date = ?, Reason = ?, Status = ? WHERE Appointment_ID = ?",
                (appointment.Scheduled_Date, appointment.Reason, appointment.Status, appointment.Appointment_ID)
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
            Created_From_Conversation_ID=row[6] if len(row) > 6 else None
        )
