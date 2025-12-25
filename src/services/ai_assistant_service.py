"""
AI Assistant Service
Business logic for RAG (Retrieval-Augmented Generation) Engine
"""
from repositories.repository_factory import RepositoryFactory
from datetime import datetime, date
import re


class RAGEngine:
    """Simple RAG (Retrieval-Augmented Generation) Engine"""
    
    def __init__(self):
        """Initialize RAG Engine with repositories"""
        self.kb_repo = None
        try:
            self.kb_repo = RepositoryFactory.get_repository('knowledge_base')
        except Exception as e:
            print(f"[RAG Engine] Warning: Knowledge base repository not available: {e}")
    
    def retrieve_relevant_docs(self, query, limit=3):
        """Retrieve relevant documents from knowledge base"""
        if not self.kb_repo:
            return []
        
        # Extract keywords from query
        keywords = self._extract_keywords(query)
        
        # Search for relevant documents
        relevant_docs = []
        for keyword in keywords:
            docs = self.kb_repo.search(keyword, limit=limit)
            relevant_docs.extend(docs)
        
        # Remove duplicates and limit results
        seen_ids = set()
        unique_docs = []
        for doc in relevant_docs:
            if doc.KB_ID not in seen_ids:
                seen_ids.add(doc.KB_ID)
                unique_docs.append(doc)
                if len(unique_docs) >= limit:
                    break
        
        return unique_docs
    
    def retrieve_user_context(self, user_id):
        """Retrieve user-specific data from database (tasks, schedule, calendar)"""
        user_context = {
            'tasks': [],
            'schedule': None,
            'calendar_events': [],
            'upcoming_deadlines': [],
            'today_tasks': []
        }
        
        try:
            # Get task repository
            task_repo = RepositoryFactory.get_repository('task')
            tasks = task_repo.get_by_user_id(user_id) if task_repo else []
            
            # Get schedule repository
            schedule_repo = RepositoryFactory.get_repository('schedule')
            schedules = schedule_repo.get_by_user_id(user_id) if schedule_repo else []
            
            # Get student to access calendar
            student_repo = RepositoryFactory.get_repository('student')
            student = student_repo.get_by_user_id(user_id) if student_repo else None
            
            # Get calendar events if student exists
            if student:
                calendar_repo = RepositoryFactory.get_repository('calendar')
                calendar_events = calendar_repo.get_by_student(student.Student_ID) if calendar_repo else []
                user_context['calendar_events'] = calendar_events
            
            # Process tasks
            today = date.today()
            
            for task in tasks:
                task_info = {
                    'title': getattr(task, 'Task_Title', 'Unknown Task'),
                    'due_date': getattr(task, 'Due_Date', None),
                    'priority': getattr(task, 'Priority', 'Medium'),
                    'status': getattr(task, 'Status', 'Pending')
                }
                user_context['tasks'].append(task_info)
                
                # Check if due today or upcoming
                if task_info['due_date']:
                    if isinstance(task_info['due_date'], datetime):
                        due_date_only = task_info['due_date'].date()
                        if due_date_only == today:
                            user_context['today_tasks'].append(task_info)
                        elif due_date_only > today:
                            user_context['upcoming_deadlines'].append(task_info)
                    elif isinstance(task_info['due_date'], date):
                        if task_info['due_date'] == today:
                            user_context['today_tasks'].append(task_info)
                        elif task_info['due_date'] > today:
                            user_context['upcoming_deadlines'].append(task_info)
            
            # Sort upcoming deadlines by date
            user_context['upcoming_deadlines'].sort(key=lambda x: x['due_date'] if x['due_date'] else date.max)
            
            # Get schedule
            if schedules and len(schedules) > 0:
                user_context['schedule'] = schedules[0]
                
        except Exception as e:
            print(f"[RAG Engine] Error retrieving user context: {e}")
            import traceback
            traceback.print_exc()
        
        return user_context
    
    def _extract_keywords(self, text):
        """Extract meaningful keywords from text"""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                     'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'should', 'could', 'may', 'might', 'must', 'can', 'what',
                     'when', 'where', 'who', 'why', 'how', 'which', 'this', 'that', 'these',
                     'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your',
                     'his', 'her', 'its', 'our', 'their'}
        
        # Convert to lowercase and split
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Return top 10 keywords
    
    def generate_answer(self, query, relevant_docs, user_context=None, llm_service=None):
        """Generate answer based on retrieved documents and user context"""
        # If no docs and no user context, return default message
        if not relevant_docs and not user_context:
            return {
                'answer': "I apologize, but I couldn't find relevant information in my knowledge base to answer your question. Please try rephrasing your question or ask about topics related to courses, schedules, academic information, or university policies.",
                'sources': [],
                'confidence': 'low'
            }
        
        # Format user context for LLM/template
        context_text = ""
        if user_context:
            context_parts = []
            
            # Today's tasks
            if user_context.get('today_tasks'):
                context_parts.append("Tasks due today:")
                for task in user_context['today_tasks']:
                    due_str = ""
                    if task['due_date']:
                        if isinstance(task['due_date'], datetime):
                            due_str = f" (due {task['due_date'].strftime('%I:%M %p')})"
                    context_parts.append(f"  - {task['title']}{due_str} [{task['priority']} priority]")
            
            # Upcoming deadlines
            if user_context.get('upcoming_deadlines'):
                context_parts.append("\nUpcoming deadlines:")
                for task in user_context['upcoming_deadlines'][:5]:  # Next 5 deadlines
                    due_str = ""
                    if task['due_date']:
                        if isinstance(task['due_date'], datetime):
                            due_str = f" (due {task['due_date'].strftime('%B %d at %I:%M %p')})"
                        elif isinstance(task['due_date'], date):
                            due_str = f" (due {task['due_date'].strftime('%B %d')})"
                    context_parts.append(f"  - {task['title']}{due_str} [{task['priority']} priority]")
            
            # Calendar events (schedule)
            if user_context.get('calendar_events'):
                today_events = [e for e in user_context['calendar_events'] 
                               if getattr(e, 'Date', None) == date.today()]
                if today_events:
                    context_parts.append("\nToday's schedule:")
                    for event in today_events:
                        time_str = f" at {getattr(event, 'Time', '')}" if getattr(event, 'Time', None) else ""
                        context_parts.append(f"  - {getattr(event, 'Title', 'Event')}{time_str}")
            
            if context_parts:
                context_text = "\n\nYour Personal Information:\n" + "\n".join(context_parts)
        
        # Try to use LLM if available
        if llm_service:
            try:
                print(f"[RAG Engine] Using Ollama ({llm_service.provider}) to generate answer")
                # Add user context to the documents
                enhanced_docs = list(relevant_docs) if relevant_docs else []
                if context_text:
                    # Create a virtual document for user context
                    context_doc = type('obj', (object,), {
                        'KB_ID': -1,  # Special ID for user context
                        'Title': 'Your Personal Data',
                        'Content': context_text,
                        'Category': 'Personal',
                        'Keywords': 'tasks schedule deadlines calendar'
                    })()
                    enhanced_docs.insert(0, context_doc)  # Put user context first
                
                result = llm_service.generate_rag_response(query, enhanced_docs)
                answer = result['answer']
                confidence = result['confidence']
            except Exception as e:
                print(f"[RAG Engine] Ollama error, falling back to Unify Model: {e}")
                # Fallback to Unify Model (template-based generation)
                answer = self._generate_simple_answer(query, relevant_docs, user_context)
                confidence = 'high' if len(relevant_docs) >= 2 else 'medium'
        else:
            # Use Unify Model (template-based generation)
            print(f"[RAG Engine] Using Unify Model (template-based) to generate answer")
            answer = self._generate_simple_answer(query, relevant_docs, user_context)
            confidence = 'high' if len(relevant_docs) >= 2 else 'medium'
        
        # Prepare sources (exclude user context document)
        sources = [
            {
                'kb_id': doc.KB_ID,
                'title': doc.Title,
                'category': doc.Category,
                'excerpt': doc.Content[:200] + '...' if len(doc.Content) > 200 else doc.Content
            }
            for doc in relevant_docs if hasattr(doc, 'KB_ID') and doc.KB_ID != -1
        ]
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': confidence
        }
    
    def _generate_simple_answer(self, query, docs, user_context=None):
        """Generate a simple answer from documents (template-based)"""
        if len(docs) == 0:
            # Check if we have user context for personal questions
            if user_context:
                query_lower = query.lower()
                if any(word in query_lower for word in ['today', 'deadline', 'due', 'schedule', 'lecture']):
                    return self._answer_from_user_context(query, user_context)
            return "No relevant information found."
        
        # Check query type
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['what', 'define', 'definition', 'meaning']):
            # Definitional question
            main_doc = docs[0]
            answer = f"Based on the information I found:\n\n{main_doc.Content}\n\n"
            if len(docs) > 1:
                answer += f"Additionally, {docs[1].Title} mentions: {docs[1].Content[:150]}..."
            return answer
        
        elif any(word in query_lower for word in ['how', 'steps', 'process', 'procedure']):
            # Procedural question
            answer = "Here's how to proceed:\n\n"
            for i, doc in enumerate(docs[:2], 1):
                answer += f"{i}. **{doc.Title}**: {doc.Content}\n\n"
            return answer
        
        elif any(word in query_lower for word in ['when', 'time', 'date', 'schedule', 'lecture', 'deadline', 'due']):
            # Temporal question - check user context first
            answer = ""
            
            # Check for user-specific data
            if user_context:
                # Today's tasks/deadlines
                if any(word in query_lower for word in ['today', 'now', 'deadline', 'due']):
                    if user_context.get('today_tasks'):
                        answer += "**Tasks due today:**\n\n"
                        for task in user_context['today_tasks']:
                            due_str = ""
                            if task['due_date']:
                                if isinstance(task['due_date'], datetime):
                                    due_str = f" (due {task['due_date'].strftime('%I:%M %p')})"
                            answer += f"- {task['title']}{due_str} [{task['priority']} priority]\n"
                        answer += "\n"
                    
                    if user_context.get('upcoming_deadlines'):
                        answer += "**Upcoming deadlines:**\n\n"
                        for task in user_context['upcoming_deadlines'][:5]:
                            due_str = ""
                            if task['due_date']:
                                if isinstance(task['due_date'], datetime):
                                    due_str = f" (due {task['due_date'].strftime('%B %d at %I:%M %p')})"
                                elif isinstance(task['due_date'], date):
                                    due_str = f" (due {task['due_date'].strftime('%B %d')})"
                            answer += f"- {task['title']}{due_str} [{task['priority']} priority]\n"
                        answer += "\n"
                
                # Schedule/lecture times
                if any(word in query_lower for word in ['lecture', 'schedule', 'class', 'today']):
                    today = date.today()
                    if user_context.get('calendar_events'):
                        today_events = [e for e in user_context['calendar_events'] 
                                       if getattr(e, 'Date', None) == today]
                        if today_events:
                            answer += "**Today's schedule:**\n\n"
                            for event in today_events:
                                time_str = f" at {getattr(event, 'Time', '')}" if getattr(event, 'Time', None) else ""
                                answer += f"- {getattr(event, 'Title', 'Event')}{time_str}\n"
                            answer += "\n"
            
            # Add knowledge base info if available
            if docs:
                if answer:
                    answer += "**General information:**\n\n"
                else:
                    answer = "Regarding timing and schedules:\n\n"
                for doc in docs[:2]:
                    answer += f"**{doc.Title}**: {doc.Content}\n\n"
            
            return answer if answer else "I don't have schedule information available at the moment."
        
        elif any(word in query_lower for word in ['where', 'location', 'place']):
            # Location question
            answer = "Location information:\n\n"
            for doc in docs[:2]:
                answer += f"**{doc.Title}**: {doc.Content}\n\n"
            return answer
        
        elif any(word in query_lower for word in ['who', 'contact', 'responsible']):
            # Person/contact question
            answer = "Contact information:\n\n"
            for doc in docs[:2]:
                answer += f"**{doc.Title}**: {doc.Content}\n\n"
            return answer
        
        else:
            # General question
            answer = f"Based on the information available:\n\n**{docs[0].Title}**\n{docs[0].Content}\n\n"
            if len(docs) > 1:
                answer += f"Additionally, here's information from **{docs[1].Title}**:\n{docs[1].Content[:200]}..."
            return answer
    
    def _answer_from_user_context(self, query, user_context):
        """Generate answer from user context when no KB docs found"""
        query_lower = query.lower()
        answer = ""
        
        if any(word in query_lower for word in ['deadline', 'due', 'task']):
            if user_context.get('today_tasks'):
                answer += "**Tasks due today:**\n\n"
                for task in user_context['today_tasks']:
                    due_str = ""
                    if task['due_date'] and isinstance(task['due_date'], datetime):
                        due_str = f" (due {task['due_date'].strftime('%I:%M %p')})"
                    answer += f"- {task['title']}{due_str} [{task['priority']} priority]\n"
            
            if user_context.get('upcoming_deadlines'):
                if answer:
                    answer += "\n"
                answer += "**Upcoming deadlines:**\n\n"
                for task in user_context['upcoming_deadlines'][:5]:
                    due_str = ""
                    if task['due_date']:
                        if isinstance(task['due_date'], datetime):
                            due_str = f" (due {task['due_date'].strftime('%B %d at %I:%M %p')})"
                        elif isinstance(task['due_date'], date):
                            due_str = f" (due {task['due_date'].strftime('%B %d')})"
                    answer += f"- {task['title']}{due_str} [{task['priority']} priority]\n"
        
        if any(word in query_lower for word in ['schedule', 'lecture', 'class', 'today']):
            today = date.today()
            if user_context.get('calendar_events'):
                today_events = [e for e in user_context['calendar_events'] 
                               if getattr(e, 'Date', None) == today]
                if today_events:
                    if answer:
                        answer += "\n"
                    answer += "**Today's schedule:**\n\n"
                    for event in today_events:
                        time_str = f" at {getattr(event, 'Time', '')}" if getattr(event, 'Time', None) else ""
                        answer += f"- {getattr(event, 'Title', 'Event')}{time_str}\n"
        
        return answer if answer else "I don't have that information in your personal data at the moment."


# Singleton instance
_rag_engine_instance = None

def get_rag_engine():
    """Get singleton instance of RAG Engine"""
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()
    return _rag_engine_instance
