"""
Models Package
Import all models for easy access
"""
from models.user import User
from models.student import Student
from models.instructor import Instructor
from models.course import Course
from models.enrollment import Enrollment
from models.task import Task
from models.schedule import Schedule
from models.note import Note
from models.message import Message
from models.transcript import Transcript
from models.calendar import Calendar
from models.reminder import Reminder
from models.focus_session import FocusSession
from models.teaching_assistant import TeachingAssistant
from models.advisor_conversation import AdvisorConversation
from models.advisor_message import AdvisorMessage
from models.advisor_appointment import AdvisorAppointment
from models.notification import Notification
from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission

__all__ = [
    'User',
    'Student',
    'Instructor',
    'Course',
    'Enrollment',
    'Task',
    'Schedule',
    'Note',
    'Message',
    'Transcript',
    'Calendar',
    'Reminder',
    'FocusSession',
    'TeachingAssistant',
    'AdvisorConversation',
    'AdvisorMessage',
    'AdvisorAppointment',
    'Notification',
    'Assignment',
    'AssignmentSubmission'
]

