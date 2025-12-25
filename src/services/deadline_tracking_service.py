"""
Deadline Tracking Service
Handles automatic deadline tracking from tasks, assignments, and calendar events
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from repositories.repository_factory import RepositoryFactory
from services.deadline_notification_service import DeadlineNotificationService


class DeadlineTrackingService:
    def __init__(self):
        self.notification_service = DeadlineNotificationService()
        self.task_repo = RepositoryFactory.get_repository("task")
        self.calendar_repo = RepositoryFactory.get_repository("calendar")
        self.notification_repo = RepositoryFactory.get_repository("deadline_notification")

    def sync_task_deadlines(self, user_id: int) -> int:
        """Sync deadlines from tasks for a user"""
        created_count = 0
        
        # Get student_id from user_id
        student_repo = RepositoryFactory.get_repository("student")
        student = student_repo.get_by_user_id(user_id)
        if not student:
            return 0
        
        # Get all tasks for the student
        tasks = self.task_repo.get_by_student(student.Student_ID)
        
        for task in tasks:
            if task.Due_Date and task.Status != "completed":
                # Check if deadline notification already exists
                existing = self.notification_repo.get_by_source("task", task.Task_ID)
                
                if not existing:
                    # Create deadline notification
                    try:
                        due_date = task.Due_Date
                        if isinstance(due_date, str):
                            try:
                                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                            except:
                                due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                        
                        if due_date > datetime.now():
                            self.notification_service.create_deadline_notification(
                                user_id=user_id,
                                deadline_type="task",
                                source_id=task.Task_ID,
                                source_type="task",
                                deadline_date=due_date,
                                title=f"Task: {task.Task_Title}",
                                description=f"Task due date",
                                priority=task.Priority if hasattr(task, 'Priority') else "medium"
                            )
                            created_count += 1
                    except Exception as e:
                        print(f"Error creating deadline for task {task.Task_ID}: {e}")
                        continue
        
        return created_count

    def sync_calendar_deadlines(self, user_id: int) -> int:
        """Sync deadlines from calendar events for a user"""
        created_count = 0
        
        # Get student_id from user_id
        student_repo = RepositoryFactory.get_repository("student")
        student = student_repo.get_by_user_id(user_id)
        if not student:
            return 0
        
        # Get calendar events for the student
        try:
            calendar_events = self.calendar_repo.get_by_student_id(student.Student_ID)
        except:
            calendar_events = []
        
        for event in calendar_events:
            if hasattr(event, 'Event_Date') and event.Event_Date:
                # Check if deadline notification already exists
                existing = self.notification_repo.get_by_source("calendar_event", event.Event_ID)
                
                if not existing:
                    try:
                        event_date = event.Event_Date
                        if isinstance(event_date, str):
                            try:
                                event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
                            except:
                                event_date = datetime.strptime(event_date, '%Y-%m-%d %H:%M:%S')
                        
                        if event_date > datetime.now():
                            title = getattr(event, 'Event_Title', 'Calendar Event')
                            self.notification_service.create_deadline_notification(
                                user_id=user_id,
                                deadline_type="calendar",
                                source_id=event.Event_ID,
                                source_type="calendar_event",
                                deadline_date=event_date,
                                title=f"Event: {title}",
                                description=getattr(event, 'Description', None),
                                priority="medium"
                            )
                            created_count += 1
                    except Exception as e:
                        print(f"Error creating deadline for calendar event {event.Event_ID}: {e}")
                        continue
        
        return created_count

    def sync_all_deadlines(self, user_id: int) -> Dict[str, int]:
        """Sync all deadlines from different sources"""
        results = {
            'tasks': 0,
            'calendar': 0,
            'total': 0
        }
        
        results['tasks'] = self.sync_task_deadlines(user_id)
        results['calendar'] = self.sync_calendar_deadlines(user_id)
        results['total'] = results['tasks'] + results['calendar']
        
        return results

    def cleanup_completed_deadlines(self, user_id: Optional[int] = None, days: int = 30):
        """Clean up old completed deadlines"""
        if user_id:
            notifications = self.notification_repo.get_by_user_id(user_id)
        else:
            notifications = self.notification_repo.get_all()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for notification in notifications:
            if notification.Status == "completed" and notification.Deadline_Date:
                deadline = notification.Deadline_Date
                if isinstance(deadline, str):
                    try:
                        deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    except:
                        try:
                            deadline = datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S')
                        except:
                            continue
                
                if deadline < cutoff_date:
                    self.notification_service.delete_deadline_notification(notification.Notification_ID)
                    deleted_count += 1
        
        return deleted_count

