"""
Study Recommendation Repository
Handles database operations for study recommendations
"""
from models.study_recommendation import StudyRecommendation
from core.db_singleton import DatabaseConnection
from datetime import datetime


class StudyRecommendationRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def create_table(self):
        """Create StudyRecommendation table if it doesn't exist"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[StudyRecommendation]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE StudyRecommendation (
                        Recommendation_ID INT IDENTITY(1,1) PRIMARY KEY,
                        Student_ID INT NOT NULL,
                        Course_ID INT,
                        Topic NVARCHAR(255),
                        Resource_Type NVARCHAR(50),
                        Resource_Link NVARCHAR(500),
                        Reason NVARCHAR(MAX),
                        Relevance_Score DECIMAL(3,2),
                        Generated_At DATETIME DEFAULT GETDATE(),
                        FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
                        FOREIGN KEY (Course_ID) REFERENCES Course(Course_ID)
                    )
                END
            """)
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def create(self, recommendation):
        """Create a new study recommendation"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO StudyRecommendation (Student_ID, Course_ID, Topic, Resource_Type, 
                                                Resource_Link, Reason, Relevance_Score, Generated_At)
                OUTPUT INSERTED.Recommendation_ID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recommendation.Student_ID,
                recommendation.Course_ID,
                recommendation.Topic,
                recommendation.Resource_Type,
                recommendation.Resource_Link,
                recommendation.Reason,
                recommendation.Relevance_Score,
                recommendation.Generated_At
            ))
            row = cursor.fetchone()
            if row:
                recommendation.Recommendation_ID = row[0]
            conn.commit()
            return recommendation
        finally:
            cursor.close()
            conn.close()
    
    def get_by_student(self, student_id):
        """Get all recommendations for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Recommendation_ID, Student_ID, Course_ID, Topic, Resource_Type,
                       Resource_Link, Reason, Relevance_Score, Generated_At
                FROM StudyRecommendation WHERE Student_ID = ? ORDER BY Relevance_Score DESC, Generated_At DESC
            """, (student_id,))
            rows = cursor.fetchall()
            return [self._map_to_object(row) for row in rows] if rows else []
        finally:
            cursor.close()
            conn.close()
    
    def _map_to_object(self, row):
        """Map database row to StudyRecommendation object"""
        if not row:
            return None
        return StudyRecommendation(
            Recommendation_ID=row[0],
            Student_ID=row[1],
            Course_ID=row[2],
            Topic=row[3],
            Resource_Type=row[4],
            Resource_Link=row[5],
            Reason=row[6],
            Relevance_Score=row[7],
            Generated_At=row[8]
        )

