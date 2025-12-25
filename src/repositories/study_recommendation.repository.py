from core.db_singleton import DatabaseConnection
from models.study_recommendation import StudyRecommendation
from datetime import datetime


class StudyRecommendationRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all study recommendations"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Recommendation_ID, Student_ID, Course_ID, Topic, Resource_Type, 
                       Resource_Link, Reason, Relevance_Score, Generated_At 
                FROM StudyRecommendation
            """)
            rows = cursor.fetchall()
            recommendations = []
            for row in rows:
                recommendations.append(self._row_to_recommendation(row))
            return recommendations
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, recommendation_id):
        """Get study recommendation by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Recommendation_ID, Student_ID, Course_ID, Topic, Resource_Type, 
                       Resource_Link, Reason, Relevance_Score, Generated_At 
                FROM StudyRecommendation 
                WHERE Recommendation_ID = ?
            """, (recommendation_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_recommendation(row)
            return None
        finally:
            cursor.close()
            conn.close()

    def get_by_student(self, student_id, limit=20):
        """Get recommendations for a student, ordered by relevance"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP (?) Recommendation_ID, Student_ID, Course_ID, Topic, Resource_Type, 
                       Resource_Link, Reason, Relevance_Score, Generated_At 
                FROM StudyRecommendation 
                WHERE Student_ID = ?
                ORDER BY Relevance_Score DESC, Generated_At DESC
            """, (limit, student_id))
            rows = cursor.fetchall()
            recommendations = []
            for row in rows:
                recommendations.append(self._row_to_recommendation(row))
            return recommendations
        finally:
            cursor.close()
            conn.close()

    def get_by_course(self, student_id, course_id, limit=10):
        """Get recommendations for a student in a specific course"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP (?) Recommendation_ID, Student_ID, Course_ID, Topic, Resource_Type, 
                       Resource_Link, Reason, Relevance_Score, Generated_At 
                FROM StudyRecommendation 
                WHERE Student_ID = ? AND Course_ID = ?
                ORDER BY Relevance_Score DESC, Generated_At DESC
            """, (limit, student_id, course_id))
            rows = cursor.fetchall()
            recommendations = []
            for row in rows:
                recommendations.append(self._row_to_recommendation(row))
            return recommendations
        finally:
            cursor.close()
            conn.close()

    def get_by_topic(self, student_id, topic, limit=10):
        """Get recommendations for a student on a specific topic"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP (?) Recommendation_ID, Student_ID, Course_ID, Topic, Resource_Type, 
                       Resource_Link, Reason, Relevance_Score, Generated_At 
                FROM StudyRecommendation 
                WHERE Student_ID = ? AND Topic LIKE ?
                ORDER BY Relevance_Score DESC, Generated_At DESC
            """, (limit, student_id, f'%{topic}%'))
            rows = cursor.fetchall()
            recommendations = []
            for row in rows:
                recommendations.append(self._row_to_recommendation(row))
            return recommendations
        finally:
            cursor.close()
            conn.close()

    def get_by_resource_type(self, student_id, resource_type, limit=10):
        """Get recommendations by resource type"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP (?) Recommendation_ID, Student_ID, Course_ID, Topic, Resource_Type, 
                       Resource_Link, Reason, Relevance_Score, Generated_At 
                FROM StudyRecommendation 
                WHERE Student_ID = ? AND Resource_Type = ?
                ORDER BY Relevance_Score DESC, Generated_At DESC
            """, (limit, student_id, resource_type))
            rows = cursor.fetchall()
            recommendations = []
            for row in rows:
                recommendations.append(self._row_to_recommendation(row))
            return recommendations
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
                                                  Resource_Link, Reason, Relevance_Score) 
                OUTPUT INSERTED.Recommendation_ID 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (recommendation.Student_ID, recommendation.Course_ID, recommendation.Topic,
                  recommendation.Resource_Type, recommendation.Resource_Link, 
                  recommendation.Reason, recommendation.Relevance_Score))
            row = cursor.fetchone()
            if row:
                recommendation.Recommendation_ID = row[0]
            conn.commit()
            return recommendation
        finally:
            cursor.close()
            conn.close()

    def create_batch(self, recommendations):
        """Create multiple recommendations at once"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            for rec in recommendations:
                cursor.execute("""
                    INSERT INTO StudyRecommendation (Student_ID, Course_ID, Topic, Resource_Type, 
                                                      Resource_Link, Reason, Relevance_Score) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (rec.Student_ID, rec.Course_ID, rec.Topic, rec.Resource_Type,
                      rec.Resource_Link, rec.Reason, rec.Relevance_Score))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def delete(self, recommendation_id):
        """Delete a study recommendation by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM StudyRecommendation WHERE Recommendation_ID = ?", 
                          (recommendation_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def delete_old_recommendations(self, student_id, days=30):
        """Delete recommendations older than specified days"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM StudyRecommendation 
                WHERE Student_ID = ? AND Generated_At < DATEADD(day, -?, GETDATE())
            """, (student_id, days))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()

    def _row_to_recommendation(self, row):
        """Convert database row to StudyRecommendation object"""
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
