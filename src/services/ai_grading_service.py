"""
AI Grading Service
Handles automatic grading of assignments using AI
"""
from services.llm_service import get_llm_service
from repositories.repository_factory import RepositoryFactory
from models.grading_suggestion import GradingSuggestion
import json


class AIGradingService:
    """Service for AI-powered assignment grading"""
    
    def __init__(self):
        self.llm_service = get_llm_service()
        self.grading_suggestion_repo = RepositoryFactory.get_repository('grading_suggestion')
        self.assignment_repo = RepositoryFactory.get_repository('assignment')
        self.submission_repo = RepositoryFactory.get_repository('assignment_submission')
        self.assignment_service = None
    
    def auto_grade_submission(self, submission_id: int) -> dict:
        """
        Automatically grade a submission using AI
        
        Args:
            submission_id: ID of the submission to grade
            
        Returns:
            dict with grade, feedback, and confidence score
        """
        try:
            print(f"[AUTO-GRADE] Starting auto-grading for submission {submission_id}")
            
            # Get submission
            submission = self.submission_repo.get_by_id(submission_id)
            if not submission:
                print(f"[AUTO-GRADE] ERROR: Submission {submission_id} not found")
                raise ValueError("Submission not found")
            
            print(f"[AUTO-GRADE] Found submission: Assignment_ID={submission.Assignment_ID}, Has_Text={bool(submission.Submission_Text)}, Has_File={bool(submission.File_Path)}")
            
            # Get assignment
            assignment = self.assignment_repo.get_by_id(submission.Assignment_ID)
            if not assignment:
                print(f"[AUTO-GRADE] ERROR: Assignment {submission.Assignment_ID} not found")
                raise ValueError("Assignment not found")
            
            print(f"[AUTO-GRADE] Found assignment: Title={assignment.Title}, Is_Auto_Graded={assignment.Is_Auto_Graded}, Has_Correct_Answer={bool(assignment.Correct_Answer)}")
            
            # Check if auto-grading is enabled
            if not assignment.Is_Auto_Graded:
                print(f"[AUTO-GRADE] Skipping: Auto-grading not enabled")
                return {
                    'error': 'Auto-grading is not enabled for this assignment'
                }
            
            # Check if correct answer is provided
            if not assignment.Correct_Answer:
                print(f"[AUTO-GRADE] Skipping: No correct answer provided")
                return {
                    'error': 'No correct answer provided for auto-grading'
                }
            
            # Get submission text
            submission_text = submission.Submission_Text or ""
            print(f"[AUTO-GRADE] Submission text length: {len(submission_text)}")
            
            # If file is submitted, we'd need to extract text (for now, only handle text submissions)
            if not submission_text and submission.File_Path:
                print(f"[AUTO-GRADE] File-based submission detected, but text extraction not implemented")
                # TODO: Extract text from file (PDF, DOCX, etc.)
                return {
                    'error': 'File-based submissions require text extraction (not yet implemented). Please submit text directly.'
                }
            
            if not submission_text:
                print(f"[AUTO-GRADE] ERROR: No submission text found")
                return {
                    'error': 'No submission text found'
                }
            
            # Use LLM to compare submission with correct answer
            print(f"[AUTO-GRADE] Calling _grade_with_ai...")
            grade_result = self._grade_with_ai(
                submission_text=submission_text,
                correct_answer=assignment.Correct_Answer,
                max_score=assignment.Max_Score,
                assignment_title=assignment.Title
            )
            
            print(f"[AUTO-GRADE] Grade result: {grade_result}")
            
            # Create grading suggestion
            suggestion = GradingSuggestion(
                Submission_ID=submission_id,
                Suggested_Grade=grade_result.get('grade', 0),
                Confidence_Score=grade_result.get('confidence', 0.8),
                Feedback_Suggestions=json.dumps([grade_result.get('feedback', '')]),
                Flagged_For_Review=grade_result.get('flagged', False),
                Flag_Reason=grade_result.get('flag_reason'),
                Accepted=None  # Not yet accepted/rejected by instructor
            )
            
            # Always auto-apply the grade (students can request review if they disagree)
            confidence = grade_result.get('confidence', 0)
            grade = grade_result.get('grade', 0)
            feedback = grade_result.get('feedback', '')
            
            print(f"[AUTO-GRADE] Auto-applying grade: {grade} (confidence: {confidence:.2f})")
            print(f"[AUTO-GRADE] Student can request manual review if they disagree with the AI grade")
            
            # Always auto-apply the grade - students can request review
            self._apply_grade(submission_id, grade, feedback, is_ai_graded=True)
            
            # Save grading suggestion if repository is available (optional, for tracking)
            if self.grading_suggestion_repo:
                print(f"[AUTO-GRADE] Saving grading suggestion...")
                self.grading_suggestion_repo.create_table()
                created_suggestion = self.grading_suggestion_repo.create(suggestion)
                print(f"[AUTO-GRADE] Grading suggestion saved: {created_suggestion.Suggestion_ID if created_suggestion else 'Failed'}")
            else:
                print(f"[AUTO-GRADE] NOTE: Grading suggestion repository not available (grade still applied)")
            
            return grade_result
            
        except Exception as e:
            print(f"Error in auto_grade_submission: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e)
            }
    
    def _grade_with_ai(self, submission_text: str, correct_answer: str, max_score: float, assignment_title: str) -> dict:
        """
        Use AI to grade the submission
        
        Args:
            submission_text: Student's submission
            correct_answer: Correct answer from assignment
            max_score: Maximum possible score
            assignment_title: Title of the assignment
            
        Returns:
            dict with grade, feedback, confidence, etc.
        """
        print(f"[AUTO-GRADE] _grade_with_ai called: LLM service available={self.llm_service is not None and self.llm_service.is_available() if self.llm_service else False}")
        
        if not self.llm_service or not self.llm_service.is_available():
            print(f"[AUTO-GRADE] LLM not available, using fallback simple comparison")
            # Fallback: simple string comparison
            return self._simple_grade_comparison(submission_text, correct_answer, max_score)
        
        try:
            # Create prompt for LLM
            prompt = f"""You are an AI grading assistant. Please grade the following student submission.

Assignment: {assignment_title}
Maximum Score: {max_score}

CORRECT ANSWER:
{correct_answer}

STUDENT SUBMISSION:
{submission_text}

Please provide:
1. A numerical grade (0 to {max_score})
2. Detailed feedback explaining what was correct and what was incorrect
3. A confidence score (0.0 to 1.0) indicating how certain you are about the grade

Respond in the following JSON format:
{{
    "grade": <number between 0 and {max_score}>,
    "feedback": "<detailed feedback text>",
    "confidence": <number between 0.0 and 1.0>,
    "flagged": <true if submission needs manual review, false otherwise>,
    "flag_reason": "<reason for flagging, if any>"
}}

Be thorough and fair in your grading. If the submission is close to correct but has minor errors, deduct points appropriately."""
            
            # Get response from LLM
            print(f"[AUTO-GRADE] Calling LLM service...")
            response = self.llm_service.generate(
                prompt=prompt,
                context=None,
                system_prompt="You are an AI grading assistant. Provide accurate, fair grades and detailed feedback."
            )
            print(f"[AUTO-GRADE] LLM response received (length: {len(response) if response else 0})")
            
            # Parse JSON response
            try:
                # Try to extract JSON from response
                response_text = response.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith('```'):
                    lines = response_text.split('\n')
                    response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                
                grade_data = json.loads(response_text)
                
                # Validate and clamp grade
                grade = float(grade_data.get('grade', 0))
                grade = max(0, min(max_score, grade))  # Clamp between 0 and max_score
                
                return {
                    'grade': grade,
                    'feedback': grade_data.get('feedback', 'Graded automatically by AI.'),
                    'confidence': float(grade_data.get('confidence', 0.7)),
                    'flagged': grade_data.get('flagged', False),
                    'flag_reason': grade_data.get('flag_reason')
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, try simple grade extraction
                return self._parse_grade_from_text(response, max_score)
                
        except Exception as e:
            print(f"Error in LLM grading, using fallback: {e}")
            return self._simple_grade_comparison(submission_text, correct_answer, max_score)
    
    def _simple_grade_comparison(self, submission_text: str, correct_answer: str, max_score: float) -> dict:
        """Fallback grading using simple text comparison"""
        submission_lower = submission_text.lower().strip()
        correct_lower = correct_answer.lower().strip()
        
        # Exact match = full score
        if submission_lower == correct_lower:
            return {
                'grade': max_score,
                'feedback': 'Perfect match with the correct answer.',
                'confidence': 1.0,
                'flagged': False
            }
        
        # Check similarity (simple word overlap)
        submission_words = set(submission_lower.split())
        correct_words = set(correct_lower.split())
        
        if len(correct_words) == 0:
            return {
                'grade': max_score * 0.5,
                'feedback': 'Cannot determine correctness - manual review recommended.',
                'confidence': 0.3,
                'flagged': True,
                'flag_reason': 'Empty or invalid correct answer'
            }
        
        overlap = len(submission_words.intersection(correct_words))
        similarity = overlap / len(correct_words) if len(correct_words) > 0 else 0
        
        grade = max_score * similarity
        
        feedback = f"Similarity: {similarity:.0%}. "
        if similarity >= 0.9:
            feedback += "Very close to correct answer."
        elif similarity >= 0.7:
            feedback += "Mostly correct with some differences."
        elif similarity >= 0.5:
            feedback += "Partially correct."
        else:
            feedback += "Significantly different from correct answer. Manual review recommended."
        
        # Confidence should match similarity - higher similarity = higher confidence
        # For similarity >= 0.7, use at least 0.7 confidence so it auto-applies
        confidence = max(0.6, min(1.0, similarity + 0.1))  # Scale similarity to confidence
        
        return {
            'grade': grade,
            'feedback': feedback,
            'confidence': confidence,
            'flagged': similarity < 0.7,
            'flag_reason': 'Low similarity score - manual review recommended' if similarity < 0.7 else None
        }
    
    def _parse_grade_from_text(self, text: str, max_score: float) -> dict:
        """Try to extract grade from LLM text response"""
        import re
        
        # Try to find grade in text
        grade_match = re.search(r'grade[:\s]+(\d+\.?\d*)', text, re.IGNORECASE)
        if grade_match:
            grade = float(grade_match.group(1))
            grade = max(0, min(max_score, grade))
        else:
            grade = max_score * 0.7  # Default to 70% if can't parse
        
        return {
            'grade': grade,
            'feedback': text[:500],  # First 500 chars as feedback
            'confidence': 0.5,
            'flagged': True,
            'flag_reason': 'Could not parse structured response from AI'
        }
    
    def _apply_grade(self, submission_id: int, grade: float, feedback: str, is_ai_graded: bool = True):
        """Apply the AI-generated grade to the submission"""
        try:
            print(f"[AUTO-GRADE] Applying grade {grade} to submission {submission_id} (AI Graded: {is_ai_graded})")
            from services.assignment_service import get_assignment_service
            assignment_service = get_assignment_service()
            
            # Get submission to find assignment
            submission = self.submission_repo.get_by_id(submission_id)
            if submission:
                assignment = self.assignment_repo.get_by_id(submission.Assignment_ID)
                if assignment:
                    # For AI-graded assignments, use NULL for Graded_By (foreign key constraint)
                    # The Is_AI_Graded flag indicates it was graded by AI
                    # For manual grading, use the assignment creator's ID
                    graded_by = None if is_ai_graded else assignment.Created_By
                    print(f"[AUTO-GRADE] Grading submission as AI-graded (Graded_By={graded_by}, Is_AI_Graded={is_ai_graded})")
                    result = assignment_service.grade_submission(
                        submission_id=submission_id,
                        grade=grade,
                        feedback=feedback,
                        graded_by=graded_by,
                        is_ai_graded=is_ai_graded
                    )
                    print(f"[AUTO-GRADE] Grade applied successfully: {result.Status if result else 'Failed'}")
                    if result:
                        print(f"[AUTO-GRADE] Submission status: {result.Status}, Grade: {result.Grade}, Is_AI_Graded: {result.Is_AI_Graded}")
                else:
                    print(f"[AUTO-GRADE] ERROR: Assignment not found")
            else:
                print(f"[AUTO-GRADE] ERROR: Submission not found")
        except Exception as e:
            print(f"[AUTO-GRADE] Error applying auto-grade: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise - grading suggestion is still saved


def get_ai_grading_service():
    """Factory function to get AIGradingService instance"""
    return AIGradingService()

