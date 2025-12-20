"""
Course Schedule Slot Repository
Handles database operations for course schedule slots
"""
from core.db_singleton import DatabaseConnection
from datetime import time
from typing import Optional, List, Dict


class CourseScheduleSlotRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all schedule slots"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Slot_ID, Course_ID, Course_Code, Section, Day, 
                       Start_Time, End_Time, Slot_Type, Sub_Type, Academic_Year, Term
                FROM Course_Schedule_Slot
                ORDER BY Course_Code, Section, Day, Start_Time
            """)
            rows = cursor.fetchall()
            slots = []
            for row in rows:
                slots.append({
                    'Slot_ID': row[0],
                    'Course_ID': row[1],
                    'Course_Code': row[2],
                    'Section': row[3],
                    'Day': row[4],
                    'Start_Time': row[5],
                    'End_Time': row[6],
                    'Slot_Type': row[7],
                    'Sub_Type': row[8],
                    'Academic_Year': row[9],
                    'Term': row[10]
                })
            return slots
        finally:
            conn.close()

    def get_by_course_code(self, course_code: str, academic_year: Optional[int] = None, term: Optional[str] = None):
        """Get slots by course code"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT Slot_ID, Course_ID, Course_Code, Section, Day, Start_Time, End_Time, Slot_Type, Sub_Type, Academic_Year, Term FROM Course_Schedule_Slot WHERE Course_Code = ?"
            params = [course_code]
            
            if academic_year:
                query += " AND Academic_Year = ?"
                params.append(academic_year)
            if term:
                query += " AND Term = ?"
                params.append(term)
            
            query += " ORDER BY Section, Day, Start_Time"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            slots = []
            for row in rows:
                slots.append({
                    'Slot_ID': row[0],
                    'Course_ID': row[1],
                    'Course_Code': row[2],
                    'Section': row[3],
                    'Day': row[4],
                    'Start_Time': row[5],
                    'End_Time': row[6],
                    'Slot_Type': row[7],
                    'Sub_Type': row[8],
                    'Academic_Year': row[9],
                    'Term': row[10]
                })
            return slots
        finally:
            conn.close()

    def create(self, slot_data: Dict):
        """Create a new schedule slot"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Course_Schedule_Slot 
                (Course_ID, Course_Code, Section, Day, Start_Time, End_Time, Slot_Type, Sub_Type, Academic_Year, Term)
                OUTPUT INSERTED.Slot_ID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                slot_data.get('Course_ID'),
                slot_data.get('Course_Code'),
                slot_data.get('Section'),
                slot_data.get('Day'),
                slot_data.get('Start_Time'),
                slot_data.get('End_Time'),
                slot_data.get('Slot_Type'),
                slot_data.get('Sub_Type'),
                slot_data.get('Academic_Year'),
                slot_data.get('Term')
            ))
            slot_id = cursor.fetchone()[0]
            conn.commit()
            return slot_id
        finally:
            conn.close()

    def create_batch(self, slots_data: List[Dict]):
        """Create multiple schedule slots in one transaction"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            created_ids = []
            for slot_data in slots_data:
                cursor.execute("""
                    INSERT INTO Course_Schedule_Slot 
                    (Course_ID, Course_Code, Section, Day, Start_Time, End_Time, Slot_Type, Sub_Type, Academic_Year, Term)
                    OUTPUT INSERTED.Slot_ID
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    slot_data.get('Course_ID'),
                    slot_data.get('Course_Code'),
                    slot_data.get('Section'),
                    slot_data.get('Day'),
                    slot_data.get('Start_Time'),
                    slot_data.get('End_Time'),
                    slot_data.get('Slot_Type'),
                    slot_data.get('Sub_Type'),
                    slot_data.get('Academic_Year'),
                    slot_data.get('Term')
                ))
                created_ids.append(cursor.fetchone()[0])
            conn.commit()
            return created_ids
        finally:
            conn.close()

    def delete_by_course_code(self, course_code: str):
        """Delete all slots for a course code"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Course_Schedule_Slot WHERE Course_Code = ?", (course_code,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

