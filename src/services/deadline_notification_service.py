"""
Deadline Notification Service
Handles deadline notification business logic
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from repositories.repository_factory import RepositoryFactory
from models.deadline_notification import DeadlineNotification
from models.deadline_alert_schedule import DeadlineAlertSchedule


class DeadlineNotificationService:
    def __init__(self):
        self.notification_repo = RepositoryFactory.get_repository("deadline_notification")
        self.alert_schedule_repo = RepositoryFactory.get_repository("deadline_alert_schedule")
        self.preference_repo = RepositoryFactory.get_repository("deadline_notification_preference")

    def create_deadline_notification(
        self,
        user_id: int,
        deadline_type: str,
        source_id: int,
        source_type: str,
        deadline_date: datetime,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium"
    ) -> DeadlineNotification:
        """Create a new deadline notification and schedule alerts"""
        # Create the notification
        notification = DeadlineNotification(
            User_ID=user_id,
            Deadline_Type=deadline_type,
            Source_ID=source_id,
            Source_Type=source_type,
            Deadline_Date=deadline_date,
            Title=title,
            Description=description,
            Priority=priority,
            Status="active"
        )
        
        notification = self.notification_repo.create(notification)
        
        # Get user preferences for alert intervals
        preference = self.preference_repo.get_by_user_and_type(user_id, deadline_type)
        if not preference:
            preference = self.preference_repo.get_by_user_and_type(user_id, "all")
        
        # Default alert intervals if no preference
        alert_intervals = [4320, 1440, 60]  # 3 days, 1 day, 1 hour
        if preference:
            alert_intervals = preference.get_alert_intervals_list()
        
        # Create alert schedules
        if preference and preference.In_App_Enabled:
            for interval_minutes in alert_intervals:
                if deadline_date > datetime.now() + timedelta(minutes=interval_minutes):
                    alert_schedule = DeadlineAlertSchedule(
                        Notification_ID=notification.Notification_ID,
                        Alert_Time_Before_Deadline=interval_minutes,
                        Alert_Type="in_app",
                        Is_Sent=False
                    )
                    self.alert_schedule_repo.create(alert_schedule)
        
        return notification

    def get_user_deadlines(self, user_id: int, status: Optional[str] = None) -> List[DeadlineNotification]:
        """Get all deadline notifications for a user, optionally filtered by status"""
        notifications = self.notification_repo.get_by_user_id(user_id)
        if status:
            notifications = [n for n in notifications if n.Status == status]
        return notifications

    def get_upcoming_deadlines(self, user_id: int, limit: int = 10) -> List[DeadlineNotification]:
        """Get upcoming deadline notifications for a user"""
        return self.notification_repo.get_upcoming(user_id, limit)

    def get_urgent_deadlines(self, user_id: int, hours: int = 24) -> List[DeadlineNotification]:
        """Get urgent deadline notifications (within specified hours)"""
        return self.notification_repo.get_urgent(user_id, hours)

    def mark_deadline_completed(self, notification_id: int) -> bool:
        """Mark a deadline notification as completed"""
        return self.notification_repo.mark_completed(notification_id)

    def update_deadline_notification(
        self,
        notification_id: int,
        deadline_date: Optional[datetime] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[DeadlineNotification]:
        """Update a deadline notification"""
        notification = self.notification_repo.get_by_id(notification_id)
        if not notification:
            return None
        
        if deadline_date is not None:
            notification.Deadline_Date = deadline_date
        if title is not None:
            notification.Title = title
        if description is not None:
            notification.Description = description
        if priority is not None:
            notification.Priority = priority
        if status is not None:
            notification.Status = status
        
        return self.notification_repo.update(notification)

    def delete_deadline_notification(self, notification_id: int) -> bool:
        """Delete a deadline notification and its alert schedules"""
        # Delete alert schedules first (due to foreign key)
        schedules = self.alert_schedule_repo.get_by_notification_id(notification_id)
        for schedule in schedules:
            self.alert_schedule_repo.delete(schedule.Schedule_ID)
        
        # Delete the notification
        return self.notification_repo.delete(notification_id)

    def check_and_update_overdue(self, user_id: Optional[int] = None):
        """Check for overdue deadlines and update their status"""
        if user_id:
            notifications = self.notification_repo.get_by_user_id(user_id)
        else:
            notifications = self.notification_repo.get_all()
        
        now = datetime.now()
        updated_count = 0
        
        for notification in notifications:
            if notification.Status == "active" and notification.Deadline_Date:
                deadline = notification.Deadline_Date
                if isinstance(deadline, str):
                    try:
                        deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    except:
                        try:
                            deadline = datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S')
                        except:
                            continue
                
                if deadline < now:
                    self.notification_repo.mark_overdue(notification.Notification_ID)
                    updated_count += 1
        
        return updated_count

    def get_deadline_calendar(self, user_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
        """Get deadlines formatted for calendar view"""
        notifications = self.notification_repo.get_by_user_id(user_id)
        
        if start_date:
            notifications = [n for n in notifications if n.Deadline_Date and n.Deadline_Date >= start_date]
        if end_date:
            notifications = [n for n in notifications if n.Deadline_Date and n.Deadline_Date <= end_date]
        
        calendar_items = []
        for notification in notifications:
            if notification.Deadline_Date:
                deadline = notification.Deadline_Date
                if isinstance(deadline, str):
                    try:
                        deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    except:
                        try:
                            deadline = datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S')
                        except:
                            continue
                
                calendar_items.append({
                    'id': notification.Notification_ID,
                    'title': notification.Title,
                    'start': deadline.isoformat(),
                    'deadline_type': notification.Deadline_Type,
                    'priority': notification.Priority,
                    'status': notification.Status,
                    'description': notification.Description
                })
        
        return calendar_items

