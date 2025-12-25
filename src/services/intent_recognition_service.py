"""
Intent Recognition Service
Detects the intent of student queries for routing and appropriate responses
"""
import re


class IntentRecognitionService:
    """Service to recognize intent from student queries"""
    
    # Intent patterns - keywords and phrases that indicate specific intents
    INTENT_PATTERNS = {
        'degree_planning': [
            r'\b(degree|graduation|requirements|credits|credit hours|major requirements)\b',
            r'\b(when can I graduate|how many credits|what do I need|missing requirements)\b',
            r'\b(time to graduation|degree progress|track my progress)\b'
        ],
        'course_selection': [
            r'\b(which course|courses should I take|recommend courses|course suggestions)\b',
            r'\b(what classes|next semester|registration|enroll)\b',
            r'\b(course sequence|prerequisites|pre-requisites|pre req)\b',
            r'\b(difficult courses|hard classes|course load)\b'
        ],
        'prerequisite_check': [
            r'\b(prerequisite|pre-requisite|prereq|required before)\b',
            r'\b(can I take|am I eligible|do I have the requirements)\b',
            r'\b(what do I need before|what courses are required)\b'
        ],
        'policy_question': [
            r'\b(policy|policies|deadline|registration deadline|drop deadline)\b',
            r'\b(how to|how do I|what is the process|procedure)\b',
            r'\b(gpa|grade point average|grading|transcript)\b',
            r'\b(withdrawal|withdraw|drop policy|retake)\b'
        ],
        'career_guidance': [
            r'\b(career|job|internship|opportunities|research)\b',
            r'\b(what can I do with|career path|job prospects)\b',
            r'\b(electives for career|career-related courses)\b'
        ],
        'academic_support': [
            r'\b(help|support|resources|tutoring|study)\b',
            r'\b(struggling|difficulty|need help|academic support)\b',
            r'\b(where can I get help|tutoring services)\b'
        ],
        'course_information': [
            r'\b(what is|tell me about|information about|details about)\b',
            r'\b(course description|syllabus|course content)\b',
            r'\b(who teaches|instructor|professor|schedule)\b'
        ]
    }
    
    # Default intent if none match
    DEFAULT_INTENT = 'general_inquiry'
    
    def detect_intent(self, query: str) -> dict:
        """
        Detect intent from a query
        
        Args:
            query: The user's query text
            
        Returns:
            dict with 'intent' and 'confidence_score'
        """
        query_lower = query.lower()
        
        # Count matches for each intent
        intent_scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower, re.IGNORECASE))
                score += matches
            
            if score > 0:
                intent_scores[intent] = score
        
        # If no matches, return default intent
        if not intent_scores:
            return {
                'intent': self.DEFAULT_INTENT,
                'confidence_score': 0.3
            }
        
        # Get the intent with highest score
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        # Calculate confidence (normalized score, max 1.0)
        max_possible_score = sum(len(patterns) for patterns in self.INTENT_PATTERNS.values())
        confidence = min(0.95, 0.5 + (best_intent[1] / max(len(query.split()), 1)) * 0.5)
        
        return {
            'intent': best_intent[0],
            'confidence_score': round(confidence, 2)
        }
    
    def get_conversation_type(self, intent: str) -> str:
        """
        Map intent to conversation type
        
        Args:
            intent: The detected intent
            
        Returns:
            Conversation type string
        """
        intent_to_type = {
            'degree_planning': 'degree_planning',
            'course_selection': 'course_selection',
            'prerequisite_check': 'course_selection',
            'policy_question': 'policy',
            'career_guidance': 'career',
            'academic_support': 'policy',
            'course_information': 'course_selection',
            'general_inquiry': 'policy'
        }
        
        return intent_to_type.get(intent, 'policy')
