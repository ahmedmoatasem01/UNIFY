"""
Appointment Controller for Instructors
Allows instructors to view appointments with students
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
from core.user_helper import get_user_data
from core.role_auth import requires_role

appointment_bp = Blueprint('appointment', __name__, url_prefix='/appointments')

# Initialize repository
try:
    appointment_repo = RepositoryFactory.get_repository('advisor_appointment')
except Exception as e:
    print(f"Warning: Appointment repository not available: {e}")
    appointment_repo = None


@appointment_bp.route('/instructor', methods=['GET'])
@requires_role('Instructor', 'TA')
def instructor_appointments():
    """View appointments for instructor"""
    try:
        user_id = session.get('user_id')
        user_data = get_user_data(user_id)
        
        # Get instructor ID
        instructor_repo = RepositoryFactory.get_repository('instructor')
        instructor = instructor_repo.get_by_user_id(user_id) if instructor_repo else None
        
        if not instructor:
            return redirect(url_for('overview.overview_page'))
        
        instructor_id = instructor.Instructor_ID
        
        # Get appointments for this instructor
        appointments = []
        if appointment_repo:
            appointments = appointment_repo.get_by_advisor(instructor_id)
        
        # Enrich with student information
        student_repo = RepositoryFactory.get_repository('student')
        user_repo = RepositoryFactory.get_repository('user')
        
        enriched_appointments = []
        for apt in appointments:
            student = student_repo.get_by_id(apt.Student_ID) if student_repo else None
            student_user = None
            if student and user_repo:
                student_user = user_repo.get_by_id(student.User_ID)
            
            enriched_appointments.append({
                'appointment_id': apt.Appointment_ID,
                'student_id': apt.Student_ID,
                'student_name': student_user.Username if student_user else f'Student {apt.Student_ID}',
                'scheduled_date': apt.Scheduled_Date.isoformat() if apt.Scheduled_Date else None,
                'reason': apt.Reason,
                'status': apt.Status,
                'instructor_response': getattr(apt, 'Instructor_Response', None)
            })
        
        return render_template('instructor_appointments.html', 
                             user_data=user_data,
                             appointments=enriched_appointments)
    except Exception as e:
        print(f"Error loading instructor appointments: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500


@appointment_bp.route('/api/instructor/<int:instructor_id>', methods=['GET'])
@requires_role('Instructor', 'TA')
def get_appointments_by_instructor(instructor_id):
    """Get appointments for an instructor (API endpoint)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if not appointment_repo:
            return jsonify({'error': 'Service unavailable'}), 503
        
        appointments = appointment_repo.get_by_advisor(instructor_id)
        
        # Enrich with student information
        student_repo = RepositoryFactory.get_repository('student')
        user_repo = RepositoryFactory.get_repository('user')
        
        result = []
        for apt in appointments:
            student = student_repo.get_by_id(apt.Student_ID) if student_repo else None
            student_user = None
            if student and user_repo:
                student_user = user_repo.get_by_id(student.User_ID)
            
            result.append({
                'appointment_id': apt.Appointment_ID,
                'student_id': apt.Student_ID,
                'student_name': student_user.Username if student_user else f'Student {apt.Student_ID}',
                'scheduled_date': apt.Scheduled_Date.isoformat() if apt.Scheduled_Date else None,
                'reason': apt.Reason,
                'status': apt.Status,
                'instructor_response': getattr(apt, 'Instructor_Response', None)
            })
        
        return jsonify(result)
    except Exception as e:
        print(f"Error getting appointments: {e}")
        return jsonify({'error': str(e)}), 500


@appointment_bp.route('/api/<int:appointment_id>/approve', methods=['POST'])
@requires_role('Instructor', 'TA')
def approve_appointment(appointment_id):
    """Approve a pending appointment request"""
    try:
        user_id = session.get('user_id')
        
        # Get instructor ID
        instructor_repo = RepositoryFactory.get_repository('instructor')
        instructor = instructor_repo.get_by_user_id(user_id) if instructor_repo else None
        
        if not instructor:
            return jsonify({'error': 'Instructor not found'}), 404
        
        # Get appointment
        appointment = appointment_repo.get_by_id(appointment_id) if appointment_repo else None
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        # Verify it belongs to this instructor
        if appointment.Advisor_ID != instructor.Instructor_ID:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Update status to 'scheduled'
        appointment.Status = 'scheduled'
        appointment.Instructor_Response = 'Appointment approved'
        
        updated = appointment_repo.update(appointment)
        
        if updated:
            return jsonify({
                'success': True,
                'message': 'Appointment approved successfully',
                'appointment': updated.to_dict()
            })
        else:
            return jsonify({'error': 'Failed to update appointment'}), 500
            
    except Exception as e:
        print(f"Error approving appointment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@appointment_bp.route('/api/<int:appointment_id>/reject', methods=['POST'])
@requires_role('Instructor', 'TA')
def reject_appointment(appointment_id):
    """Reject a pending appointment request"""
    try:
        user_id = session.get('user_id')
        data = request.json or {}
        rejection_message = data.get('message', 'I am busy at this time. Please choose another time.')
        
        # Get instructor ID
        instructor_repo = RepositoryFactory.get_repository('instructor')
        instructor = instructor_repo.get_by_user_id(user_id) if instructor_repo else None
        
        if not instructor:
            return jsonify({'error': 'Instructor not found'}), 404
        
        # Get appointment
        appointment = appointment_repo.get_by_id(appointment_id) if appointment_repo else None
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        # Verify it belongs to this instructor
        if appointment.Advisor_ID != instructor.Instructor_ID:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Update status to 'rejected' with response message
        appointment.Status = 'rejected'
        appointment.Instructor_Response = rejection_message.strip()
        
        updated = appointment_repo.update(appointment)
        
        if updated:
            return jsonify({
                'success': True,
                'message': 'Appointment rejected',
                'appointment': updated.to_dict()
            })
        else:
            return jsonify({'error': 'Failed to update appointment'}), 500
            
    except Exception as e:
        print(f"Error rejecting appointment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
