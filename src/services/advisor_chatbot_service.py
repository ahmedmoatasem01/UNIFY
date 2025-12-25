"""
Advisor Chatbot Service
Business logic for AI-powered academic advisor chatbot
"""
from repositories.repository_factory import RepositoryFactory
from services.intent_recognition_service import IntentRecognitionService
from services.ai_assistant_service import get_rag_engine
from datetime import datetime
from models.advisor_conversation import AdvisorConversation
from models.advisor_message import AdvisorMessage
from models.advisor_appointment import AdvisorAppointment


class AdvisorChatbotService:
    """Service for academic advisor chatbot functionality"""
    
    def __init__(self):
        """Initialize the advisor chatbot service"""
        self.intent_service = IntentRecognitionService()
        self.rag_engine = get_rag_engine()
        # Initialize fast LLM service for advisor chatbot (using Phi model for speed)
        self._init_llm_service()
    
    def _init_llm_service(self):
        """Initialize LLM service with fast model (Phi) for advisor chatbot"""
        try:
            from services.llm_service import LLMService
            # Try to use Phi model (fast and lightweight)
            self.llm_service = LLMService(provider='ollama', model='phi')
            if not self.llm_service.is_available():
                # Fallback to default if Phi not available
                from services.llm_service import get_llm_service
                self.llm_service = get_llm_service()
        except Exception as e:
            print(f"[Advisor Chatbot] Warning: LLM service not available: {e}")
            self.llm_service = None
    
    def process_message(self, student_id: int, message_text: str, conversation_id: int = None) -> dict:
        """
        Process a student message and generate a response
        
        Args:
            student_id: ID of the student sending the message
            message_text: The message text from the student
            conversation_id: Optional conversation ID (creates new if not provided)
            
        Returns:
            dict with conversation_id, response_text, intent, and confidence
        """
        # Get repositories
        conv_repo = RepositoryFactory.get_repository('advisor_conversation')
        msg_repo = RepositoryFactory.get_repository('advisor_message')
        
        # Detect intent
        intent_result = self.intent_service.detect_intent(message_text)
        intent = intent_result['intent']
        confidence = intent_result['confidence_score']
        conversation_type = self.intent_service.get_conversation_type(intent)
        
        # Get or create conversation
        if conversation_id:
            conversation = conv_repo.get_by_id(conversation_id)
            if not conversation or conversation.Student_ID != student_id:
                # Create new conversation if ID is invalid
                conversation = None
        else:
            conversation = None
        
        if not conversation:
            # Create new conversation
            conversation = AdvisorConversation(
                Student_ID=student_id,
                Conversation_Type=conversation_type,
                Status='active'
            )
            conversation = conv_repo.create(conversation)
        
        # Save student message
        student_msg = AdvisorMessage(
            Conversation_ID=conversation.Conversation_ID,
            Sender_Type='student',
            Message_Text=message_text,
            Intent=intent,
            Confidence_Score=confidence
        )
        student_msg = msg_repo.create(student_msg)
        
        # Generate AI response
        response = self._generate_response(student_id, message_text, intent, conversation_type)
        
        # Save AI response
        ai_msg = AdvisorMessage(
            Conversation_ID=conversation.Conversation_ID,
            Sender_Type='ai',
            Message_Text=response['answer'],
            Intent=intent,
            Confidence_Score=confidence
        )
        ai_msg = msg_repo.create(ai_msg)
        
        # Update conversation last message time
        conversation.Last_Message_At = datetime.now()
        conv_repo.update_last_message_at(conversation.Conversation_ID)
        
        return {
            'conversation_id': conversation.Conversation_ID,
            'response_text': response['answer'],
            'intent': intent,
            'confidence': confidence,
            'sources': response.get('sources', []),
            'conversation_type': conversation_type
        }
    
    def _generate_response(self, student_id: int, query: str, intent: str, conversation_type: str) -> dict:
        """
        Generate a response based on the query and intent
        
        Args:
            student_id: ID of the student
            query: The student's query
            intent: Detected intent
            conversation_type: Type of conversation
            
        Returns:
            dict with answer and sources
        """
        # Get student data for context
        student_repo = RepositoryFactory.get_repository('student')
        student = student_repo.get_by_id(student_id) if student_repo else None
        
        # Retrieve relevant documents from knowledge base
        relevant_docs = self.rag_engine.retrieve_relevant_docs(query, limit=3)
        
        # Check for course catalog request first
        query_lower = query.lower()
        if any(phrase in query_lower for phrase in ['course catalog', 'show courses', 'list courses', 'all courses', 'available courses', 'show me the course']):
            return self._handle_course_catalog_request(student_id, query, student)
        
        # Build specialized responses based on intent
        if intent == 'degree_planning':
            response = self._handle_degree_planning(student_id, query, relevant_docs, student)
        elif intent == 'course_selection':
            response = self._handle_course_selection(student_id, query, relevant_docs, student)
        elif intent == 'prerequisite_check':
            response = self._handle_prerequisite_check(student_id, query, relevant_docs, student)
        elif intent == 'policy_question':
            response = self._handle_policy_question(query, relevant_docs)
        elif intent == 'career_guidance':
            response = self._handle_career_guidance(student_id, query, relevant_docs, student)
        else:
            # Use general RAG response
            response = self.rag_engine.generate_answer(query, relevant_docs, user_context=None)
        
        return response
    
    def _handle_degree_planning(self, student_id: int, query: str, docs: list, student) -> dict:
        """Handle degree planning questions"""
        # Get enrollment data
        enrollment_repo = RepositoryFactory.get_repository('enrollment')
        course_repo = RepositoryFactory.get_repository('course')
        enrollments = enrollment_repo.get_by_student(student_id) if enrollment_repo else []
        
        # Count completed credits by getting Course credits
        completed_credits = 0
        if course_repo:
            for enrollment in enrollments:
                if getattr(enrollment, 'Status', '').lower() == 'completed' and getattr(enrollment, 'Grade', ''):
                    course = course_repo.get_by_id(enrollment.Course_ID)
                    if course and hasattr(course, 'Credits') and course.Credits:
                        completed_credits += int(course.Credits)
        
        answer = f"Based on your current progress:\n\n"
        answer += f"• Completed Credits: {completed_credits}\n"
        
        if student:
            answer += f"• Department: {student.Department or 'Not specified'}\n"
            if student.GPA:
                answer += f"• Current GPA: {student.GPA:.2f}\n"
        
        if docs:
            answer += f"\n\nHere's relevant information about degree requirements:\n\n"
            for doc in docs:
                answer += f"**{doc.Title}**: {doc.Content[:300]}...\n\n"
        else:
            answer += "\n\nFor detailed degree planning, I recommend scheduling an appointment with your academic advisor."
        
        return {
            'answer': answer,
            'sources': [{'kb_id': doc.KB_ID, 'title': doc.Title} for doc in docs]
        }
    
    def _handle_course_selection(self, student_id: int, query: str, docs: list, student) -> dict:
        """Handle course selection questions"""
        # Get available courses from course catalog
        course_repo = RepositoryFactory.get_repository('course')
        instructor_repo = RepositoryFactory.get_repository('instructor')
        courses = course_repo.get_all() if course_repo else []
        
        answer = "Here are course recommendations from our course catalog:\n\n"
        
        # Filter courses based on query keywords
        query_lower = query.lower()
        relevant_courses = []
        
        # First try exact matches in course names
        for course in courses:
            course_name = getattr(course, 'Course_Name', '') or ''
            if any(word in course_name.lower() for word in query_lower.split() if len(word) > 3):
                relevant_courses.append(course)
        
        # If no matches, show all courses (limit to 10)
        if not relevant_courses:
            relevant_courses = courses[:10]
        
        if relevant_courses:
            # Show top 5-8 courses
            for course in relevant_courses[:8]:
                credits = getattr(course, 'Credits', 0) or 0
                course_name = getattr(course, 'Course_Name', 'Unknown Course') or 'Unknown Course'
                course_id = getattr(course, 'Course_ID', None)
                
                # Try to get instructor info
                instructor_name = None
                if course.Instructor_ID and instructor_repo:
                    instructor = instructor_repo.get_by_id(course.Instructor_ID)
                    if instructor:
                        instructor_name = instructor.Department or 'Unknown'
                
                answer += f"• **{course_name}** ({credits} credits)"
                if instructor_name:
                    answer += f" - {instructor_name}"
                answer += f" [ID: {course_id}]\n"
            
            if len(courses) > len(relevant_courses):
                answer += f"\n\n*Showing {len(relevant_courses)} of {len(courses)} total courses. Ask for more details about any specific course.*\n"
        else:
            answer += "• No courses found matching your query. "
            answer += f"Our course catalog has {len(courses)} available courses.\n"
            answer += "• Try asking about specific course names or topics.\n"
            answer += "• Or ask me to show you all available courses.\n"
        
        if docs:
            answer += "\n\nAdditional information:\n\n"
            for doc in docs:
                answer += f"**{doc.Title}**: {doc.Content[:200]}...\n\n"
        
        return {
            'answer': answer,
            'sources': [{'kb_id': doc.KB_ID, 'title': doc.Title} for doc in docs]
        }
    
    def _handle_course_catalog_request(self, student_id: int, query: str, student) -> dict:
        """Handle course catalog requests"""
        course_repo = RepositoryFactory.get_repository('course')
        instructor_repo = RepositoryFactory.get_repository('instructor')
        courses = course_repo.get_all() if course_repo else []
        
        answer = f"**Course Catalog**\n\n"
        answer += f"We have {len(courses)} courses available:\n\n"
        
        if courses:
            # Group by department if possible, or just list all
            for idx, course in enumerate(courses[:20], 1):  # Show first 20
                credits = getattr(course, 'Credits', 0) or 0
                course_name = getattr(course, 'Course_Name', 'Unknown Course') or 'Unknown Course'
                course_id = getattr(course, 'Course_ID', None)
                
                # Try to get instructor info
                instructor_info = ""
                if course.Instructor_ID and instructor_repo:
                    instructor = instructor_repo.get_by_id(course.Instructor_ID)
                    if instructor and instructor.Department:
                        instructor_info = f" ({instructor.Department})"
                
                answer += f"{idx}. **{course_name}** - {credits} credits{instructor_info}\n"
            
            if len(courses) > 20:
                answer += f"\n*Showing 20 of {len(courses)} courses. Ask me about specific courses for more details.*\n"
        else:
            answer += "No courses found in the catalog at this time.\n"
        
        answer += "\n💡 **Tip**: Ask me about specific courses by name or ID to get detailed information!"
        
        return {
            'answer': answer,
            'sources': []
        }
    
    def _handle_prerequisite_check(self, student_id: int, query: str, docs: list, student) -> dict:
        """Handle prerequisite checking questions"""
        # Get student's completed courses
        enrollment_repo = RepositoryFactory.get_repository('enrollment')
        enrollments = enrollment_repo.get_by_student(student_id) if enrollment_repo else []
        
        completed_courses = [
            enrollment.Course_ID
            for enrollment in enrollments
            if getattr(enrollment, 'Status', '').lower() == 'completed' and enrollment.Course_ID
        ]
        
        answer = "Prerequisite Information:\n\n"
        answer += f"You have completed {len(completed_courses)} courses.\n\n"
        
        if docs:
            answer += "Based on the course catalog:\n\n"
            for doc in docs:
                answer += f"**{doc.Title}**: {doc.Content[:300]}...\n\n"
        else:
            answer += "To check specific prerequisites, please provide the course code or name. "
            answer += "You can also review prerequisites in the course catalog."
        
        return {
            'answer': answer,
            'sources': [{'kb_id': doc.KB_ID, 'title': doc.Title} for doc in docs]
        }
    
    def _handle_policy_question(self, query: str, docs: list) -> dict:
        """Handle academic policy questions"""
        # Use RAG engine for policy questions with fast LLM
        return self.rag_engine.generate_answer(
            query, 
            docs, 
            user_context=None,
            llm_service=self.llm_service if self.llm_service else None
        )
    
    def _handle_career_guidance(self, student_id: int, query: str, docs: list, student) -> dict:
        """Handle career guidance questions"""
        answer = "Career Guidance:\n\n"
        
        if student and student.Department:
            answer += f"Based on your major in {student.Department}, here are some career paths to consider:\n\n"
        else:
            answer += "Here are some general career guidance resources:\n\n"
        
        if docs:
            for doc in docs:
                answer += f"**{doc.Title}**: {doc.Content[:300]}...\n\n"
        else:
            answer += "• Explore internship opportunities through the career center\n"
            answer += "• Research career paths related to your major\n"
            answer += "• Consider elective courses that align with your career interests\n"
            answer += "• Schedule an appointment with a career counselor\n"
        
        return {
            'answer': answer,
            'sources': [{'kb_id': doc.KB_ID, 'title': doc.Title} for doc in docs]
        }
    
    def get_degree_progress(self, student_id: int) -> dict:
        """
        Get degree progress for a student
        
        Args:
            student_id: ID of the student
            
        Returns:
            dict with progress information
        """
        enrollment_repo = RepositoryFactory.get_repository('enrollment')
        student_repo = RepositoryFactory.get_repository('student')
        course_repo = RepositoryFactory.get_repository('course')
        
        enrollments = enrollment_repo.get_by_student(student_id) if enrollment_repo else []
        student = student_repo.get_by_id(student_id) if student_repo else None
        
        # Calculate completed credits by getting the Course for each completed enrollment
        completed_credits = 0
        if course_repo:
            for enrollment in enrollments:
                if getattr(enrollment, 'Status', '').lower() == 'completed':
                    # Get the course to get its credits
                    course = course_repo.get_by_id(enrollment.Course_ID)
                    if course and hasattr(course, 'Credits') and course.Credits:
                        completed_credits += int(course.Credits)
        
        # Calculate total enrolled credits (for reference)
        total_enrolled_credits = 0
        if course_repo:
            for enrollment in enrollments:
                course = course_repo.get_by_id(enrollment.Course_ID)
                if course and hasattr(course, 'Credits') and course.Credits:
                    total_enrolled_credits += int(course.Credits)
        
        # Typical degree requires 120-130 credits, but use total enrolled if it's higher (for students who haven't completed courses yet)
        total_required = max(120, total_enrolled_credits) if total_enrolled_credits > 0 else 120
        progress_percent = min(100, (completed_credits / total_required) * 100) if total_required > 0 else 0
        
        return {
            'student_id': student_id,
            'completed_credits': completed_credits,
            'total_required_credits': total_required,
            'remaining_credits': max(0, total_required - completed_credits),
            'progress_percent': round(progress_percent, 2),
            'gpa': float(student.GPA) if student and student.GPA else None,
            'department': student.Department if student else None
        }
    
    def get_course_recommendations(self, student_id: int) -> list:
        """
        Get course recommendations for a student
        
        Args:
            student_id: ID of the student
            
        Returns:
            list of recommended courses
        """
        course_repo = RepositoryFactory.get_repository('course')
        enrollment_repo = RepositoryFactory.get_repository('enrollment')
        student_repo = RepositoryFactory.get_repository('student')
        
        student = student_repo.get_by_id(student_id) if student_repo else None
        enrollments = enrollment_repo.get_by_student(student_id) if enrollment_repo else []
        
        # Get completed course IDs
        completed_course_ids = [
            enrollment.Course_ID
            for enrollment in enrollments
            if getattr(enrollment, 'Status', '').lower() == 'completed' and enrollment.Course_ID
        ]
        
        # Get all courses
        all_courses = course_repo.get_all() if course_repo else []
        
        # Filter out completed courses and return recommendations
        recommended = [
            course.to_dict()
            for course in all_courses
            if getattr(course, 'Course_ID', None) not in completed_course_ids
        ]
        
        # Limit to 10 recommendations
        return recommended[:10]
    
    def escalate_to_advisor(self, conversation_id: int, advisor_id: int, reason: str = None) -> bool:
        """
        Escalate a conversation to a human advisor
        
        Args:
            conversation_id: ID of the conversation
            advisor_id: ID of the advisor to escalate to
            reason: Optional reason for escalation
            
        Returns:
            bool indicating success
        """
        conv_repo = RepositoryFactory.get_repository('advisor_conversation')
        conversation = conv_repo.get_by_id(conversation_id)
        
        if not conversation:
            return False
        
        conversation.Status = 'escalated'
        conversation.Escalated_To_Advisor_ID = advisor_id
        conv_repo.update(conversation)
        
        return True


# Singleton instance
_advisor_chatbot_service_instance = None

def get_advisor_chatbot_service():
    """Get singleton instance of Advisor Chatbot Service"""
    global _advisor_chatbot_service_instance
    if _advisor_chatbot_service_instance is None:
        _advisor_chatbot_service_instance = AdvisorChatbotService()
    return _advisor_chatbot_service_instance
