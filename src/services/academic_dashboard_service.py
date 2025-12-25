"""
Academic Dashboard Service
Calculates GPA, cohort comparisons, and graduation timeline predictions
"""
from repositories.repository_factory import RepositoryFactory
from datetime import datetime, date
from typing import Dict, List, Optional


class AcademicDashboardService:
    """Service for academic dashboard calculations"""
    
    # Grade point mapping
    GRADE_POINTS = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'D-': 0.7,
        'F': 0.0, 'I': 0.0, 'W': 0.0
    }
    
    def __init__(self):
        self.enrollment_repo = RepositoryFactory.get_repository("enrollment")
        self.student_repo = RepositoryFactory.get_repository("student")
        self.course_repo = RepositoryFactory.get_repository("course")
    
    def get_dashboard_data(self, student_id: int) -> Dict:
        """Get complete academic dashboard data for a student"""
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return {}
        
        enrollments = self.enrollment_repo.get_by_student(student_id)
        
        # Calculate GPA
        gpa_data = self._calculate_gpa(enrollments)
        
        # Get course grades
        course_grades = self._get_course_grades(enrollments)
        
        # Get cohort comparison
        cohort_data = self._get_cohort_comparison(student)
        
        # Calculate graduation timeline
        graduation_timeline = self._calculate_graduation_timeline(student, enrollments)
        
        return {
            'student': {
                'student_id': student.Student_ID,
                'year_level': student.Year_Level,
                'department': student.Department,
                'current_gpa': student.GPA
            },
            'gpa': gpa_data,
            'course_grades': course_grades,
            'cohort_comparison': cohort_data,
            'graduation_timeline': graduation_timeline
        }
    
    def _calculate_gpa(self, enrollments: List) -> Dict:
        """Calculate cumulative and semester GPAs"""
        total_credits = 0
        total_grade_points = 0
        semester_gpas = {}
        
        for enrollment in enrollments:
            if enrollment.Status != 'completed' or not enrollment.Grade or not enrollment.Semester:
                continue
            
            course = self.course_repo.get_by_id(enrollment.Course_ID) if self.course_repo else None
            if not course:
                continue
            
            # Get credits - try different attribute names
            credits = 3  # Default
            if hasattr(course, 'Credits') and course.Credits:
                credits = course.Credits
            elif hasattr(course, 'Credit_Hours') and course.Credit_Hours:
                credits = course.Credit_Hours
            elif hasattr(course, 'credit_hours') and course.credit_hours:
                credits = course.credit_hours
            grade_point = self.GRADE_POINTS.get(enrollment.Grade.upper(), 0.0)
            
            total_credits += credits
            total_grade_points += grade_point * credits
            
            # Calculate semester GPA
            if enrollment.Semester not in semester_gpas:
                semester_gpas[enrollment.Semester] = {
                    'credits': 0,
                    'grade_points': 0,
                    'gpa': 0.0,
                    'courses': []
                }
            
            semester_gpas[enrollment.Semester]['credits'] += credits
            semester_gpas[enrollment.Semester]['grade_points'] += grade_point * credits
            semester_gpas[enrollment.Semester]['courses'].append({
                'course_id': enrollment.Course_ID,
                'grade': enrollment.Grade,
                'credits': credits
            })
        
        # Calculate semester GPAs
        for semester, data in semester_gpas.items():
            if data['credits'] > 0:
                data['gpa'] = round(data['grade_points'] / data['credits'], 2)
        
        cumulative_gpa = round(total_grade_points / total_credits, 2) if total_credits > 0 else 0.0
        
        return {
            'cumulative': cumulative_gpa,
            'total_credits': total_credits,
            'semester_gpas': semester_gpas
        }
    
    def _get_course_grades(self, enrollments: List) -> List[Dict]:
        """Get all course grades with details"""
        course_grades = []
        
        for enrollment in enrollments:
            if enrollment.Status != 'completed' or not enrollment.Grade:
                continue
            
            course = self.course_repo.get_by_id(enrollment.Course_ID) if self.course_repo else None
            if not course:
                continue
            
            # Get course name and code
            course_name = f'Course {enrollment.Course_ID}'
            course_code = f'CS{enrollment.Course_ID}'
            if hasattr(course, 'Course_Name') and course.Course_Name:
                course_name = course.Course_Name
            elif hasattr(course, 'course_name') and course.course_name:
                course_name = course.course_name
            
            if hasattr(course, 'Course_Code') and course.Course_Code:
                course_code = course.Course_Code
            elif hasattr(course, 'course_code') and course.course_code:
                course_code = course.course_code
            
            # Get credits
            credits = 3  # Default
            if hasattr(course, 'Credits') and course.Credits:
                credits = course.Credits
            elif hasattr(course, 'Credit_Hours') and course.Credit_Hours:
                credits = course.Credit_Hours
            
            course_grades.append({
                'course_id': enrollment.Course_ID,
                'course_name': course_name,
                'course_code': course_code,
                'grade': enrollment.Grade,
                'grade_point': self.GRADE_POINTS.get(enrollment.Grade.upper(), 0.0),
                'credits': credits,
                'semester': enrollment.Semester
            })
        
        # Sort by semester (most recent first)
        course_grades.sort(key=lambda x: x['semester'] or '', reverse=True)
        
        return course_grades
    
    def _get_cohort_comparison(self, student) -> Dict:
        """Compare student performance with their cohort (same year level and department)"""
        if not student.Year_Level or not student.Department:
            return {
                'cohort_size': 0,
                'cohort_avg_gpa': 0.0,
                'student_rank': 0,
                'percentile': 0,
                'comparison': 'no_data'
            }
        
        # Get all students in the same cohort
        all_students = self.student_repo.get_all()
        cohort_students = [
            s for s in all_students
            if s.Year_Level == student.Year_Level and s.Department == student.Department
        ]
        
        if len(cohort_students) < 2:
            return {
                'cohort_size': len(cohort_students),
                'cohort_avg_gpa': 0.0,
                'student_rank': 1,
                'percentile': 100,
                'comparison': 'insufficient_data'
            }
        
        # Calculate GPAs for all cohort students
        cohort_gpas = []
        for cohort_student in cohort_students:
            enrollments = self.enrollment_repo.get_by_student(cohort_student.Student_ID)
            gpa_data = self._calculate_gpa(enrollments)
            cohort_gpas.append({
                'student_id': cohort_student.Student_ID,
                'gpa': gpa_data['cumulative']
            })
        
        # Sort by GPA (descending)
        cohort_gpas.sort(key=lambda x: x['gpa'], reverse=True)
        
        # Find student's rank
        student_gpa_data = self._calculate_gpa(self.enrollment_repo.get_by_student(student.Student_ID))
        student_gpa = student_gpa_data['cumulative']
        
        student_rank = 1
        for i, cohort_data in enumerate(cohort_gpas, 1):
            if cohort_data['student_id'] == student.Student_ID:
                student_rank = i
                break
            elif cohort_data['gpa'] < student_gpa:
                student_rank = i
                break
        
        # Calculate average GPA
        avg_gpa = sum(c['gpa'] for c in cohort_gpas) / len(cohort_gpas) if cohort_gpas else 0.0
        
        # Calculate percentile
        percentile = round((1 - (student_rank - 1) / len(cohort_gpas)) * 100, 1) if cohort_gpas else 0
        
        # Determine comparison status
        if student_gpa > avg_gpa + 0.3:
            comparison = 'excellent'
        elif student_gpa > avg_gpa:
            comparison = 'above_average'
        elif student_gpa > avg_gpa - 0.3:
            comparison = 'average'
        else:
            comparison = 'below_average'
        
        return {
            'cohort_size': len(cohort_students),
            'cohort_avg_gpa': round(avg_gpa, 2),
            'student_gpa': round(student_gpa, 2),
            'student_rank': student_rank,
            'percentile': percentile,
            'comparison': comparison
        }
    
    def _calculate_graduation_timeline(self, student, enrollments: List) -> Dict:
        """Predict graduation timeline based on current progress"""
        if not student.Year_Level:
            return {
                'predicted_graduation': None,
                'credits_completed': 0,
                'credits_remaining': 0,
                'semesters_remaining': 0,
                'on_track': False
            }
        
        # Calculate completed credits
        completed_credits = 0
        for enrollment in enrollments:
            if enrollment.Status == 'completed' and enrollment.Grade:
                course = self.course_repo.get_by_id(enrollment.Course_ID) if self.course_repo else None
                if course:
                    # Get credits - try different attribute names
                    credits = 3  # Default
                    if hasattr(course, 'Credits') and course.Credits:
                        credits = course.Credits
                    elif hasattr(course, 'Credit_Hours') and course.Credit_Hours:
                        credits = course.Credit_Hours
                    completed_credits += credits
        
        # Typical graduation requirements (adjust based on your university)
        total_credits_required = 120  # Typical for 4-year program
        credits_per_semester = 15  # Typical full-time load
        
        credits_remaining = max(0, total_credits_required - completed_credits)
        semesters_remaining = (credits_remaining + credits_per_semester - 1) // credits_per_semester  # Ceiling division
        
        # Estimate graduation year
        current_year = datetime.now().year
        years_remaining = (semesters_remaining + 1) // 2  # Convert semesters to years
        predicted_graduation_year = current_year + years_remaining
        
        # Determine if on track
        expected_credits = student.Year_Level * 30  # Assuming 30 credits per year
        on_track = completed_credits >= expected_credits - 5  # Allow 5 credit buffer
        
        return {
            'predicted_graduation': f"Spring {predicted_graduation_year}" if semesters_remaining % 2 == 0 else f"Fall {predicted_graduation_year}",
            'predicted_graduation_year': predicted_graduation_year,
            'credits_completed': completed_credits,
            'credits_remaining': credits_remaining,
            'semesters_remaining': semesters_remaining,
            'on_track': on_track,
            'progress_percentage': round((completed_credits / total_credits_required) * 100, 1) if total_credits_required > 0 else 0
        }


def get_academic_dashboard_service():
    """Get singleton instance of Academic Dashboard Service"""
    global _dashboard_service_instance
    if '_dashboard_service_instance' not in globals():
        _dashboard_service_instance = AcademicDashboardService()
    return _dashboard_service_instance

