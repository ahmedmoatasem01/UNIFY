"""
Assignment Service
Business logic for assignment management
"""
from repositories.repository_factory import RepositoryFactory
from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission
from datetime import datetime


class AssignmentService:
    def __init__(self):
        self.assignment_repo = RepositoryFactory.get_repository('assignment')
        self.submission_repo = RepositoryFactory.get_repository('assignment_submission')
        self.course_repo = RepositoryFactory.get_repository('course')
    
    def create_assignment(self, course_id, title, description, instructions, due_date, 
                         max_score, assignment_type, created_by, allowed_file_types=None,
                         max_file_size_mb=10, solution_path=None, solution_file_name=None,
                         correct_answer=None, is_auto_graded=False):
        """Create a new assignment"""
        assignment = Assignment(
            Course_ID=course_id,
            Title=title,
            Description=description,
            Instructions=instructions,
            Due_Date=due_date,
            Max_Score=max_score,
            Assignment_Type=assignment_type,
            Allowed_File_Types=allowed_file_types,
            Max_File_Size_MB=max_file_size_mb,
            Created_By=created_by,
            Solution_Path=solution_path,
            Solution_File_Name=solution_file_name,
            Correct_Answer=correct_answer,
            Is_Auto_Graded=is_auto_graded
        )
        return self.assignment_repo.create(assignment)
    
    def get_assignments_by_course(self, course_id):
        """Get all assignments for a course"""
        return self.assignment_repo.get_by_course(course_id)
    
    def get_assignments_by_creator(self, instructor_id):
        """Get all assignments created by an instructor/TA"""
        return self.assignment_repo.get_by_creator(instructor_id)
    
    def get_assignment(self, assignment_id):
        """Get assignment by ID"""
        return self.assignment_repo.get_by_id(assignment_id)
    
    def update_assignment(self, assignment):
        """Update an assignment"""
        return self.assignment_repo.update(assignment)
    
    def delete_assignment(self, assignment_id):
        """Delete an assignment"""
        return self.assignment_repo.delete(assignment_id)
    
    def submit_assignment(self, assignment_id, student_id, file_path=None, file_name=None, submission_text=None):
        """Submit an assignment"""
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValueError("Assignment not found")
        
        # Check if already submitted
        existing = self.submission_repo.get_by_student_and_assignment(student_id, assignment_id)
        
        # Determine if late
        now = datetime.now()
        status = 'late' if now > assignment.Due_Date else 'submitted'
        
        if existing:
            # Update existing submission
            existing.File_Path = file_path
            existing.File_Name = file_name
            existing.Submission_Text = submission_text
            existing.Submitted_At = now
            existing.Status = status
            updated = self.submission_repo.update(existing)
            submission = updated if updated else existing
        else:
            # Create new submission
            submission = AssignmentSubmission(
                Assignment_ID=assignment_id,
                Student_ID=student_id,
                File_Path=file_path,
                File_Name=file_name,
                Submission_Text=submission_text,
                Status=status
            )
            submission = self.submission_repo.create(submission)
        
        # Trigger AI auto-grading if enabled
        print(f"[AUTO-GRADE] Checking auto-grading: Is_Auto_Graded={assignment.Is_Auto_Graded}, Correct_Answer={'Yes' if assignment.Correct_Answer else 'No'}")
        if assignment.Is_Auto_Graded and assignment.Correct_Answer:
            try:
                print(f"[AUTO-GRADE] Triggering auto-grading for submission {submission.Submission_ID}")
                from services.ai_grading_service import get_ai_grading_service
                ai_grading_service = get_ai_grading_service()
                result = ai_grading_service.auto_grade_submission(submission.Submission_ID)
                print(f"[AUTO-GRADE] Auto-grading result: {result}")
                
                # Reload submission from database to get the updated grade
                if 'error' not in result:
                    updated = self.submission_repo.get_by_id(submission.Submission_ID)
                    if updated:
                        submission = updated
                        print(f"[AUTO-GRADE] Submission updated with grade: {submission.Grade}")
            except Exception as e:
                print(f"[AUTO-GRADE] Error triggering AI auto-grading: {e}")
                import traceback
                traceback.print_exc()
                # Don't fail the submission if auto-grading fails
        else:
            print(f"[AUTO-GRADE] Skipping auto-grading: Is_Auto_Graded={assignment.Is_Auto_Graded}, Has_Correct_Answer={bool(assignment.Correct_Answer)}")
        
        return submission
    
    def get_submissions_by_assignment(self, assignment_id):
        """Get all submissions for an assignment"""
        return self.submission_repo.get_by_assignment(assignment_id)
    
    def get_submissions_by_student(self, student_id):
        """Get all submissions by a student"""
        return self.submission_repo.get_by_student(student_id)
    
    def get_assignment_by_submission(self, submission_id):
        """Get assignment for a submission"""
        submission = self.submission_repo.get_by_id(submission_id)
        if submission:
            return self.assignment_repo.get_by_id(submission.Assignment_ID)
        return None
    
    def grade_submission(self, submission_id, grade, feedback, graded_by, is_ai_graded=False):
        """Grade a submission"""
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValueError("Submission not found")
        
        submission.Grade = grade
        submission.Feedback = feedback
        submission.Graded_By = graded_by  # NULL for AI-graded, Instructor_ID for manual grading
        submission.Graded_At = datetime.now()
        submission.Is_AI_Graded = is_ai_graded
        # Always set status to 'graded' when a grade is applied (whether AI or manual)
        # Review requests are handled separately
        submission.Status = 'graded'
        # Clear review request flag when manually graded (not AI)
        if not is_ai_graded:
            submission.Review_Requested = False
        
        updated = self.submission_repo.update(submission)
        if updated:
            return updated
        else:
            raise ValueError("Failed to update submission")


def get_assignment_service():
    """Factory function to get AssignmentService instance"""
    return AssignmentService()
