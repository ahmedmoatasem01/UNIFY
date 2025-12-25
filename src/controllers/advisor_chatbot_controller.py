"""
Advisor Chatbot Controller
HTTP request handlers for AI Academic Advisor Chatbot endpoints
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
from services.advisor_chatbot_service import get_advisor_chatbot_service
from models.advisor_conversation import AdvisorConversation
from models.advisor_message import AdvisorMessage
from models.advisor_appointment import AdvisorAppointment
from datetime import datetime

advisor_chatbot_bp = Blueprint('advisor_chatbot', __name__, url_prefix='/api/advisor')

# Initialize repositories
try:
    conv_repo = RepositoryFactory.get_repository('advisor_conversation')
    msg_repo = RepositoryFactory.get_repository('advisor_message')
    appointment_repo = RepositoryFactory.get_repository('advisor_appointment')
    
    # Initialize tables
    conv_repo.create_table()
    msg_repo.create_table()
    appointment_repo.create_table()
except Exception as e:
    print(f"Warning: Advisor Chatbot repositories not available: {e}")
    conv_repo = None
    msg_repo = None
    appointment_repo = None

# Initialize service
advisor_service = get_advisor_chatbot_service()


@advisor_chatbot_bp.route('/chat/conversations/student/<int:student_id>', methods=['GET'])
def get_conversations_by_student(student_id):
    """Get all conversations for a student"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if not conv_repo:
            return jsonify({'error': 'Service unavailable'}), 503
        
        conversations = conv_repo.get_by_student(student_id)
        return jsonify([conv.to_dict() for conv in conversations])
    
    except Exception as e:
        print(f"Error getting conversations: {e}")
        return jsonify({'error': str(e)}), 500


@advisor_chatbot_bp.route('/chat/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        student_id = data.get('student_id')
        conversation_type = data.get('conversation_type')
        
        if not student_id:
            return jsonify({'error': 'student_id is required'}), 400
        
        if not conv_repo:
            return jsonify({'error': 'Service unavailable'}), 503
        
        conversation = AdvisorConversation(
            Student_ID=student_id,
            Conversation_Type=conversation_type,
            Status='active'
        )
        conversation = conv_repo.create(conversation)
        
        return jsonify(conversation.to_dict()), 201
    
    except Exception as e:
        print(f"Error creating conversation: {e}")
        return jsonify({'error': str(e)}), 500


@advisor_chatbot_bp.route('/chat/conversations/<int:conversation_id>/messages', methods=['GET'])
def get_messages_by_conversation(conversation_id):
    """Get all messages for a conversation"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if not msg_repo:
            return jsonify({'error': 'Service unavailable'}), 503
        
        messages = msg_repo.get_by_conversation(conversation_id)
        return jsonify([msg.to_dict() for msg in messages])
    
    except Exception as e:
        print(f"Error getting messages: {e}")
        return jsonify({'error': str(e)}), 500


@advisor_chatbot_bp.route('/chat/conversations/<conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """Send a message in a conversation"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        message_text = data.get('message_text', '').strip()
        
        if not message_text:
            return jsonify({'error': 'message_text is required'}), 400
        
        # Get student_id from session
        user_id = session.get('user_id')
        student_repo = RepositoryFactory.get_repository('student')
        student = student_repo.get_by_user_id(user_id) if student_repo else None
        
        if not student:
            return jsonify({'error': 'Student record not found'}), 404
        
        student_id = student.Student_ID
        
        # Handle conversation_id - can be "new" or a number
        conv_id = None
        if conversation_id != 'new':
            try:
                conv_id = int(conversation_id)
                if conv_id <= 0:
                    conv_id = None
            except (ValueError, TypeError):
                conv_id = None
        
        # Process message through chatbot service
        result = advisor_service.process_message(student_id, message_text, conv_id)
        
        return jsonify({
            'success': True,
            'conversation_id': result['conversation_id'],
            'response_text': result['response_text'],
            'intent': result['intent'],
            'confidence': result['confidence'],
            'sources': result.get('sources', [])
        })
    
    except Exception as e:
        print(f"Error sending message: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@advisor_chatbot_bp.route('/chat/escalate/<int:conversation_id>', methods=['POST'])
def escalate_conversation(conversation_id):
    """Escalate a conversation to a human advisor"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        advisor_id = data.get('advisor_id')
        reason = data.get('reason')
        
        if not advisor_id:
            return jsonify({'error': 'advisor_id is required'}), 400
        
        success = advisor_service.escalate_to_advisor(conversation_id, advisor_id, reason)
        
        if success:
            return jsonify({'success': True, 'message': 'Conversation escalated successfully'})
        else:
            return jsonify({'error': 'Failed to escalate conversation'}), 400
    
    except Exception as e:
        print(f"Error escalating conversation: {e}")
        return jsonify({'error': str(e)}), 500


@advisor_chatbot_bp.route('/appointments/student/<int:student_id>', methods=['GET'])
def get_appointments_by_student(student_id):
    """Get all appointments for a student"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if not appointment_repo:
            return jsonify({'error': 'Service unavailable'}), 503
        
        upcoming_only = request.args.get('upcoming', 'false').lower() == 'true'
        
        if upcoming_only:
            appointments = appointment_repo.get_upcoming_by_student(student_id)
        else:
            appointments = appointment_repo.get_by_student(student_id)
        
        return jsonify([appt.to_dict() for appt in appointments])
    
    except Exception as e:
        print(f"Error getting appointments: {e}")
        return jsonify({'error': str(e)}), 500


@advisor_chatbot_bp.route('/appointments', methods=['POST'])
def create_appointment():
    """Create a new appointment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        student_id = data.get('student_id')
        advisor_id = data.get('advisor_id')
        scheduled_date_str = data.get('scheduled_date')
        reason = data.get('reason')
        created_from_conversation_id = data.get('created_from_conversation_id')
        
        if not student_id or not advisor_id or not scheduled_date_str:
            return jsonify({'error': 'student_id, advisor_id, and scheduled_date are required'}), 400
        
        # Parse scheduled date
        try:
            scheduled_date = datetime.fromisoformat(scheduled_date_str.replace('Z', '+00:00'))
        except:
            return jsonify({'error': 'Invalid scheduled_date format. Use ISO format.'}), 400
        
        if not appointment_repo:
            return jsonify({'error': 'Service unavailable'}), 503
        
        appointment = AdvisorAppointment(
            Student_ID=student_id,
            Advisor_ID=advisor_id,
            Scheduled_Date=scheduled_date,
            Reason=reason,
            Status='scheduled',
            Created_From_Conversation_ID=created_from_conversation_id
        )
        appointment = appointment_repo.create(appointment)
        
        return jsonify(appointment.to_dict()), 201
    
    except Exception as e:
        print(f"Error creating appointment: {e}")
        return jsonify({'error': str(e)}), 500


@advisor_chatbot_bp.route('/degree-progress/student/<int:student_id>', methods=['GET'])
def get_degree_progress(student_id):
    """Get degree progress for a student"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        progress = advisor_service.get_degree_progress(student_id)
        return jsonify(progress)
    
    except Exception as e:
        print(f"Error getting degree progress: {e}")
        return jsonify({'error': str(e)}), 500


@advisor_chatbot_bp.route('/course-recommendations/student/<int:student_id>', methods=['GET'])
def get_course_recommendations(student_id):
    """Get course recommendations for a student"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        recommendations = advisor_service.get_course_recommendations(student_id)
        return jsonify(recommendations)
    
    except Exception as e:
        print(f"Error getting course recommendations: {e}")
        return jsonify({'error': str(e)}), 500


@advisor_chatbot_bp.route('/course-catalog', methods=['GET'])
def get_course_catalog():
    """Get course catalog - all available courses"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        course_repo = RepositoryFactory.get_repository('course')
        instructor_repo = RepositoryFactory.get_repository('instructor')
        
        courses = course_repo.get_all() if course_repo else []
        
        # Build catalog with instructor information
        catalog = []
        for course in courses:
            course_dict = course.to_dict()
            
            # Get instructor information
            if course.Instructor_ID and instructor_repo:
                instructor = instructor_repo.get_by_id(course.Instructor_ID)
                if instructor:
                    course_dict['instructor'] = {
                        'name': instructor.Department or 'Unknown',
                        'department': instructor.Department,
                        'email': instructor.Email
                    }
            
            catalog.append(course_dict)
        
        return jsonify({
            'courses': catalog,
            'total': len(catalog)
        })
    
    except Exception as e:
        print(f"Error getting course catalog: {e}")
        return jsonify({'error': str(e)}), 500


@advisor_chatbot_bp.route('/advisors', methods=['GET'])
def get_advisors():
    """Get list of available advisors (instructors)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        instructor_repo = RepositoryFactory.get_repository('instructor')
        user_repo = RepositoryFactory.get_repository('user')
        
        instructors = instructor_repo.get_all() if instructor_repo else []
        
        # Build advisor list with user information
        advisors = []
        for instructor in instructors:
            advisor_dict = instructor.to_dict()
            
            # Get user information
            if instructor.User_ID and user_repo:
                try:
                    user = user_repo.get_by_id(instructor.User_ID)
                    if user:
                        advisor_dict['name'] = getattr(user, 'Username', 'Advisor')
                        advisor_dict['email'] = getattr(user, 'Email', instructor.Email)
                        advisor_dict['username'] = getattr(user, 'Username', '')
                except:
                    # Fallback if user not found
                    advisor_dict['name'] = f"Advisor {instructor.Instructor_ID}"
                    advisor_dict['email'] = instructor.Email or ''
            
            advisors.append(advisor_dict)
        
        return jsonify(advisors)
    
    except Exception as e:
        print(f"Error getting advisors: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# Frontend route
@advisor_chatbot_bp.route('/chat', methods=['GET'])
def advisor_chatbot_page():
    """Advisor Chatbot main page"""
    try:
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        
        # Get student_id from session
        user_id = session.get('user_id')
        student_repo = RepositoryFactory.get_repository('student')
        student = student_repo.get_by_user_id(user_id) if student_repo else None
        
        if not student:
            print(f"[Advisor Chatbot] Student record not found for user_id: {user_id}")
            return redirect(url_for('login_page'))
        
        print(f"[Advisor Chatbot] Rendering page for student_id: {student.Student_ID}")
        return render_template('advisor_chatbot.html', student_id=student.Student_ID)
    except Exception as e:
        print(f"[Advisor Chatbot] Error rendering page: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading page: {str(e)}", 500
