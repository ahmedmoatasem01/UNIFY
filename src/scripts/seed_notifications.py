"""
Script to seed the notification database with sample data
Run this script to populate the database with test notifications
"""
import sys
import os

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)  # Go up one level from scripts/ to src/
sys.path.insert(0, src_dir)

from repositories.repository_factory import RepositoryFactory
from models.notification import Notification
from models.user import User
from datetime import datetime, timedelta


def seed_notifications():
    """Seed the database with sample notifications"""
    print("Starting notification seeding...")
    
    try:
        # Get repositories
        notification_repo = RepositoryFactory.get_repository('notification')
        user_repo = RepositoryFactory.get_repository('user')
        
        # Create table if it doesn't exist
        print("Creating notification table...")
        notification_repo.create_table()
        print("[OK] Notification table created/verified")
        
        # Get all users
        users = user_repo.get_all()
        if not users:
            print("[WARNING] No users found in database. Please create users first.")
            return
        
        print(f"Found {len(users)} users in database")
        
        # Sample notifications to create for each user
        sample_notifications = [
            {
                'title': 'Welcome to Unify!',
                'message': 'Welcome to the Unify student management system. Start exploring your courses and schedule.',
                'type': 'system',
                'priority': 'medium'
            },
            {
                'title': 'Task Reminder: Assignment Due Soon',
                'message': 'You have a task due soon: Complete Database Design Project. Due in 2 days.',
                'type': 'task',
                'priority': 'high',
                'action_url': '/tasks'
            },
            {
                'title': 'Grade Update Available',
                'message': 'Your grade for "Introduction to Computer Science" has been updated. Check your transcript.',
                'type': 'grade',
                'priority': 'medium',
                'action_url': '/transcript'
            },
            {
                'title': 'New Announcement',
                'message': 'Spring semester registration opens next week. Make sure to register for your courses.',
                'type': 'announcement',
                'priority': 'low'
            },
            {
                'title': 'Upcoming Assignment',
                'message': 'Assignment "Web Development Project" is due in 3 days. Don\'t forget to submit!',
                'type': 'assignment',
                'priority': 'high',
                'action_url': '/tasks'
            },
            {
                'title': 'Course Registration Reminder',
                'message': 'Don\'t forget to register for next semester courses. The registration deadline is approaching.',
                'type': 'system',
                'priority': 'medium',
                'action_url': '/course-registration'
            },
            {
                'title': 'New Message Received',
                'message': 'You have received a new message from your instructor. Check your messages.',
                'type': 'message',
                'priority': 'low',
                'action_url': '/messages'
            }
        ]
        
        created_count = 0
        for user in users:
            user_id = user.User_ID
            username = getattr(user, 'Username', f'User {user_id}')
            
            print(f"\nProcessing user {user_id} ({username})...")
            
            # Create notifications for this user
            for i, sample in enumerate(sample_notifications):
                # Check if notification already exists
                existing = notification_repo.get_by_user(user_id, limit=100)
                if any(n.Title == sample['title'] for n in existing):
                    print(f"  ⏭ Skipped (already exists): {sample['title']}")
                    continue  # Skip if already exists
                
                notification = Notification(
                    User_ID=user_id,
                    Title=sample['title'],
                    Message=sample['message'],
                    Type=sample['type'],
                    Priority=sample['priority'],
                    Is_Read=False if i % 2 == 0 else True,  # Mix of read and unread
                    Action_URL=sample.get('action_url'),
                    Created_At=datetime.now() - timedelta(hours=i*2)
                )
                
                notification_repo.create(notification)
                created_count += 1
                print(f"  [OK] Created: {sample['title']}")
        
        print(f"\n[OK] Seeding complete! Created {created_count} notifications")
        
        # Show summary
        print("\n=== Summary ===")
        for user in users:
            count = notification_repo.get_unread_count(user.User_ID)
            total = len(notification_repo.get_by_user(user.User_ID))
            username = getattr(user, 'Username', f'User {user.User_ID}')
            print(f"User {user.User_ID} ({username}): {total} total, {count} unread")
        
    except Exception as e:
        print(f"[ERROR] Error seeding notifications: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = seed_notifications()
    sys.exit(0 if success else 1)
