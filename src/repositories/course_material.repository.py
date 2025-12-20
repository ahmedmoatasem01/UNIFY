"""
Course Material Repository
Handles database operations for course materials
"""
from core.db_singleton import DatabaseConnection
from models.course_material import CourseMaterial
from datetime import datetime


class CourseMaterialRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def get_all(self):
        """Get all active course materials"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Material_ID, Course_ID, Instructor_ID, Material_Title, Material_Type,
                       File_Path, Link_URL, Description, Week_Number, Topic, Upload_Date,
                       File_Size, Download_Count, Is_Active
                FROM CourseMaterial
                WHERE Is_Active = 1
                ORDER BY Upload_Date DESC
            """)
            rows = cursor.fetchall()
            materials = []
            for row in rows:
                materials.append(self._row_to_material(row))
            return materials
        finally:
            cursor.close()
            conn.close()
    
    def get_by_id(self, material_id):
        """Get course material by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Material_ID, Course_ID, Instructor_ID, Material_Title, Material_Type,
                       File_Path, Link_URL, Description, Week_Number, Topic, Upload_Date,
                       File_Size, Download_Count, Is_Active
                FROM CourseMaterial
                WHERE Material_ID = ? AND Is_Active = 1
            """, (material_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_material(row)
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_by_course(self, course_id):
        """Get all materials for a specific course"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Material_ID, Course_ID, Instructor_ID, Material_Title, Material_Type,
                       File_Path, Link_URL, Description, Week_Number, Topic, Upload_Date,
                       File_Size, Download_Count, Is_Active
                FROM CourseMaterial
                WHERE Course_ID = ? AND Is_Active = 1
                ORDER BY Week_Number ASC, Upload_Date DESC
            """, (course_id,))
            rows = cursor.fetchall()
            materials = []
            for row in rows:
                materials.append(self._row_to_material(row))
            return materials
        finally:
            cursor.close()
            conn.close()
    
    def get_by_course_and_week(self, course_id, week_number):
        """Get materials for a specific course and week"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Material_ID, Course_ID, Instructor_ID, Material_Title, Material_Type,
                       File_Path, Link_URL, Description, Week_Number, Topic, Upload_Date,
                       File_Size, Download_Count, Is_Active
                FROM CourseMaterial
                WHERE Course_ID = ? AND Week_Number = ? AND Is_Active = 1
                ORDER BY Topic ASC, Upload_Date DESC
            """, (course_id, week_number))
            rows = cursor.fetchall()
            materials = []
            for row in rows:
                materials.append(self._row_to_material(row))
            return materials
        finally:
            cursor.close()
            conn.close()
    
    def get_by_instructor(self, instructor_id):
        """Get all materials uploaded by a specific instructor"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Material_ID, Course_ID, Instructor_ID, Material_Title, Material_Type,
                       File_Path, Link_URL, Description, Week_Number, Topic, Upload_Date,
                       File_Size, Download_Count, Is_Active
                FROM CourseMaterial
                WHERE Instructor_ID = ? AND Is_Active = 1
                ORDER BY Upload_Date DESC
            """, (instructor_id,))
            rows = cursor.fetchall()
            materials = []
            for row in rows:
                materials.append(self._row_to_material(row))
            return materials
        finally:
            cursor.close()
            conn.close()
    
    def get_by_topic(self, course_id, topic):
        """Get materials for a specific topic"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Material_ID, Course_ID, Instructor_ID, Material_Title, Material_Type,
                       File_Path, Link_URL, Description, Week_Number, Topic, Upload_Date,
                       File_Size, Download_Count, Is_Active
                FROM CourseMaterial
                WHERE Course_ID = ? AND Topic = ? AND Is_Active = 1
                ORDER BY Week_Number ASC, Upload_Date DESC
            """, (course_id, topic))
            rows = cursor.fetchall()
            materials = []
            for row in rows:
                materials.append(self._row_to_material(row))
            return materials
        finally:
            cursor.close()
            conn.close()
    
    def create(self, material):
        """Create a new course material"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO CourseMaterial 
                (Course_ID, Instructor_ID, Material_Title, Material_Type, File_Path, Link_URL,
                 Description, Week_Number, Topic, Upload_Date, File_Size, Download_Count, Is_Active)
                OUTPUT INSERTED.Material_ID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                material.Course_ID,
                material.Instructor_ID,
                material.Material_Title,
                material.Material_Type,
                material.File_Path,
                material.Link_URL,
                material.Description,
                material.Week_Number,
                material.Topic,
                material.Upload_Date,
                material.File_Size,
                material.Download_Count,
                1 if material.Is_Active else 0
            ))
            material_id = cursor.fetchone()[0]
            conn.commit()
            material.Material_ID = material_id
            return material
        finally:
            cursor.close()
            conn.close()
    
    def update(self, material):
        """Update an existing course material"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE CourseMaterial
                SET Material_Title = ?, Material_Type = ?, File_Path = ?, Link_URL = ?,
                    Description = ?, Week_Number = ?, Topic = ?, File_Size = ?
                WHERE Material_ID = ?
            """, (
                material.Material_Title,
                material.Material_Type,
                material.File_Path,
                material.Link_URL,
                material.Description,
                material.Week_Number,
                material.Topic,
                material.File_Size,
                material.Material_ID
            ))
            conn.commit()
            return material
        finally:
            cursor.close()
            conn.close()
    
    def delete(self, material_id):
        """Soft delete a course material (set Is_Active = 0)"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE CourseMaterial
                SET Is_Active = 0
                WHERE Material_ID = ?
            """, (material_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    def increment_download_count(self, material_id):
        """Increment download count for a material"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE CourseMaterial
                SET Download_Count = Download_Count + 1
                WHERE Material_ID = ?
            """, (material_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def _row_to_material(self, row):
        """Convert database row to CourseMaterial object"""
        return CourseMaterial(
            Material_ID=row[0],
            Course_ID=row[1],
            Instructor_ID=row[2],
            Material_Title=row[3],
            Material_Type=row[4],
            File_Path=row[5],
            Link_URL=row[6],
            Description=row[7],
            Week_Number=row[8],
            Topic=row[9],
            Upload_Date=row[10],
            File_Size=row[11],
            Download_Count=row[12],
            Is_Active=bool(row[13])
        )

