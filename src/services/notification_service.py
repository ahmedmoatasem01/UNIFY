"""
Notification Service
Business logic for notifications
"""
from repositories.repository_factory import RepositoryFactory
from models.notification import Notification
from datetime import datetime, timedelta


class NotificationService:
    def __init__(self):
        try:
            self.notification_repo = RepositoryFactory.get_repository('notification')
            self.task_repo = RepositoryFactory.get_repository('task')
            self.enrollment_repo = RepositoryFactory.get_repository('enrollment')
        except Exception as e:
            print(f"Warning: Error initializing NotificationService: {e}")
            self.notification_repo = None
            self.task_repo = None
            self.enrollment_repo = None
    
    def get_notifications(self, user_id, limit=None, unread_only=False):
        """Get notifications for a user"""
        if not self.notification_repo:
            return []
        return self.notification_repo.get_by_user(user_id, limit=limit, unread_only=unread_only)
    
    def get_unread_count(self, user_id):
        """Get count of unread notifications"""
        if not self.notification_repo:
            return 0
        return self.notification_repo.get_unread_count(user_id)
    
    def create_notification(self, user_id, title, message, notification_type='system', priority='medium', action_url=None):
        """Create a new notification"""
        if not self.notification_repo:
            raise ValueError("Notification repository not available")
        notification = Notification(
            User_ID=user_id,
            Title=title,
            Message=message,
            Type=notification_type,
            Priority=priority,
            Is_Read=False,
            Action_URL=action_url
        )
        return self.notification_repo.create(notification)
    
    def mark_as_read(self, notification_id):
        """Mark a notification as read"""
        if not self.notification_repo:
            return False
        return self.notification_repo.mark_as_read(notification_id)
    
    def mark_all_as_read(self, user_id):
        """Mark all notifications as read for a user"""
        if not self.notification_repo:
            return 0
        return self.notification_repo.mark_all_as_read(user_id)
    
    def delete_notification(self, notification_id):
        """Delete a notification"""
        if not self.notification_repo:
            return False
        return self.notification_repo.delete(notification_id)
    
    def generate_task_reminders(self, user_id):
        """Generate notifications for tasks due soon"""
        if not self.task_repo:
            return
        
        # Get student_id from user_id
        student_repo = RepositoryFactory.get_repository('student')
        student = student_repo.get_by_user_id(user_id) if student_repo else None
        if not student:
            return
        
        tasks = self.task_repo.get_by_student(student.Student_ID) if self.task_repo else []
        now = datetime.now()
        
        for task in tasks:
            if task.Status == 'completed' or not hasattr(task, 'Due_Date') or not task.Due_Date:
                continue
            
            if isinstance(task.Due_Date, str):
                try:
                    due_date = datetime.fromisoformat(task.Due_Date.replace('Z', '+00:00'))
                except:
                    continue
            else:
                due_date = task.Due_Date
            
            # Check if notification already exists
            notifications = self.notification_repo.get_by_user(user_id)
            existing = any(
                n.Type == 'task' and 
                n.Title and task.Task_Name in n.Title 
                for n in notifications
            )
            
            if existing:
                continue
            
            # 24 hours before
            if now + timedelta(hours=24) >= due_date and now < due_date:
                self.create_notification(
                    user_id=user_id,
                    title=f"Task due soon: {task.Task_Name}",
                    message=f"Your task '{task.Task_Name}' is due in 24 hours.",
                    notification_type='task',
                    priority='medium',
                    action_url='/tasks'
                )
            # 1 hour before
            elif now + timedelta(hours=1) >= due_date and now < due_date:
                self.create_notification(
                    user_id=user_id,
                    title=f"Task due soon: {task.Task_Name}",
                    message=f"Your task '{task.Task_Name}' is due in 1 hour!",
                    notification_type='task',
                    priority='urgent',
                    action_url='/tasks'
                )


def get_notification_service():
    """Factory function to get NotificationService instance"""
    return NotificationService()
