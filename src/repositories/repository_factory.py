import importlib.util
import os

# Get the directory containing this file
_repo_dir = os.path.dirname(os.path.abspath(__file__))

# Import repositories using importlib to handle dots in filenames
def _import_repository(filename, class_name):
    """Import a repository class from a file with dots in the name"""
    # Use importlib to load the module by file path
    spec = importlib.util.spec_from_file_location(
        filename.replace('.', '_'),  # Replace dots with underscores for module name
        os.path.join(_repo_dir, filename + '.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)

AINoteRepository = _import_repository('ai_note.repository', 'AINoteRepository')
UserRepository = _import_repository('user.repository', 'UserRepository')
StudentRepository = _import_repository('student.repository', 'StudentRepository')
InstructorRepository = _import_repository('instructor.repository', 'InstructorRepository')
CourseRepository = _import_repository('course.repository', 'CourseRepository')
EnrollmentRepository = _import_repository('enrollment.repository', 'EnrollmentRepository')
TaskRepository = _import_repository('task.repository', 'TaskRepository')
ScheduleRepository = _import_repository('schedule.repository', 'ScheduleRepository')
NoteRepository = _import_repository('note.repository', 'NoteRepository')
MessageRepository = _import_repository('message.repository', 'MessageRepository')
TranscriptRepository = _import_repository('transcript.repository', 'TranscriptRepository')
CalendarRepository = _import_repository('calendar.repository', 'CalendarRepository')
ReminderRepository = _import_repository('reminder.repository', 'ReminderRepository')
FocusSessionRepository = _import_repository('focus_session.repository', 'FocusSessionRepository')
TeachingAssistantRepository = _import_repository('teaching_assistant.repository', 'TeachingAssistantRepository')
UserSettingsRepository = _import_repository('user_settings.repository', 'UserSettingsRepository')


# Import CourseScheduleSlotRepository
CourseScheduleSlotRepository = _import_repository('course_schedule_slot.repository', 'CourseScheduleSlotRepository')


class RepositoryFactory:
    @staticmethod
    def get_repository(entity_type):
        entity_type = entity_type.lower()
        
        if entity_type == "user":
            return UserRepository()
        elif entity_type == "ai_note":
            return AINoteRepository()
        elif entity_type == "student":
            return StudentRepository()
        elif entity_type == "instructor":
            return InstructorRepository()
        elif entity_type == "course":
            return CourseRepository()
        elif entity_type == "enrollment":
            return EnrollmentRepository()
        elif entity_type == "task":
            return TaskRepository()
        elif entity_type == "schedule":
            return ScheduleRepository()
        elif entity_type == "note":
            return NoteRepository()
        elif entity_type == "message":
            return MessageRepository()
        elif entity_type == "transcript":
            return TranscriptRepository()
        elif entity_type == "calendar":
            return CalendarRepository()
        elif entity_type == "reminder":
            return ReminderRepository()
        elif entity_type == "focus_session":
            return FocusSessionRepository()
        elif entity_type == "teaching_assistant" or entity_type == "ta":
            return TeachingAssistantRepository()
        elif entity_type == "course_schedule_slot" or entity_type == "schedule_slot":
            return CourseScheduleSlotRepository()
        elif entity_type == "user_settings" or entity_type == "settings":
            return UserSettingsRepository()
        else:
            raise ValueError(f"Unknown repository type: {entity_type}")
