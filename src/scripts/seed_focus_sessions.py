"""
Script to seed focus sessions for a specific student
Run this to add sample focus session data
"""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_singleton import DatabaseConnection
from models.focus_session import FocusSession
from repositories.repository_factory import RepositoryFactory

def seed_focus_sessions_for_student(email):
    """Add sample focus sessions for a student by email"""
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        
        # Find student by email (try exact match first, then partial match)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.Student_ID, s.User_ID, u.Email, u.Username
            FROM Student s
            INNER JOIN [User] u ON s.User_ID = u.User_ID
            WHERE u.Email = ? OR u.Email LIKE ? OR u.Username LIKE ?
        """, (email, f'%{email.split("@")[0]}%', f'%{email.split("@")[0]}%'))
        
        rows = cursor.fetchall()
        if not rows:
            print(f"[ERROR] Student with email '{email}' not found!")
            print("\nSearching for similar emails...")
            cursor.execute("""
                SELECT TOP 5 u.Email, u.Username, s.Student_ID
                FROM [User] u
                INNER JOIN Student s ON u.User_ID = s.User_ID
                WHERE u.Email LIKE '%ahmed%' OR u.Username LIKE '%ahmed%'
            """)
            similar = cursor.fetchall()
            if similar:
                print("Found similar students:")
                for row in similar:
                    print(f"  - Email: {row[0]}, Username: {row[1]}, Student_ID: {row[2]}")
            return False
        
        # Use first match
        row = rows[0]
        print(f"[INFO] Found {len(rows)} matching student(s), using first match")
        
        student_id = row[0]
        user_id = row[1]
        found_email = row[2] if len(row) > 2 else email
        found_username = row[3] if len(row) > 3 else 'N/A'
        print(f"[OK] Found student: Student_ID={student_id}, User_ID={user_id}")
        print(f"[INFO] Email: {found_email}, Username: {found_username}")
        
        # Initialize repository
        focus_repo = RepositoryFactory.get_repository("focus_session")
        focus_repo.create_table()
        
        # Create sample sessions - mix of today, yesterday, and last week
        now = datetime.now()
        sessions = []
        
        # Today's sessions (3 sessions)
        for i in range(3):
            start_time = now.replace(hour=9 + i*3, minute=0, second=0, microsecond=0) - timedelta(hours=i*3)
            if start_time > now:
                start_time = now - timedelta(hours=1)
            end_time = start_time + timedelta(minutes=25)
            duration = 25
            
            session = FocusSession(
                Student_ID=student_id,
                Duration=duration,
                Start_Time=start_time,
                End_Time=end_time,
                Completed=True
            )
            sessions.append(session)
        
        # Yesterday's sessions (2 sessions)
        yesterday = now - timedelta(days=1)
        for i in range(2):
            start_time = yesterday.replace(hour=10 + i*4, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(minutes=25)
            duration = 25
            
            session = FocusSession(
                Student_ID=student_id,
                Duration=duration,
                Start_Time=start_time,
                End_Time=end_time,
                Completed=True
            )
            sessions.append(session)
        
        # Last week's sessions (5 sessions spread across the week)
        for day_offset in range(1, 6):  # Monday to Friday
            day = now - timedelta(days=day_offset)
            for session_num in range(1, 2):  # 1 session per day
                start_time = day.replace(hour=14, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(minutes=25)
                duration = 25
                
                session = FocusSession(
                    Student_ID=student_id,
                    Duration=duration,
                    Start_Time=start_time,
                    End_Time=end_time,
                    Completed=True
                )
                sessions.append(session)
        
        # Add sessions to database
        print(f"\n[INFO] Creating {len(sessions)} focus sessions...")
        success_count = 0
        
        for session in sessions:
            try:
                created = focus_repo.create(session)
                success_count += 1
                print(f"[OK] Created session: {created.Start_Time.strftime('%Y-%m-%d %H:%M')} - {created.Duration} min")
            except Exception as e:
                print(f"[ERROR] Failed to create session: {e}")
        
        print(f"\n[SUCCESS] Created {success_count}/{len(sessions)} focus sessions!")
        
        # Calculate and display statistics
        all_sessions = focus_repo.get_by_student(student_id)
        completed_sessions = [s for s in all_sessions if s.Completed]
        total_minutes = sum(s.Duration for s in completed_sessions)
        today_sessions = [s for s in completed_sessions if s.Start_Time and s.Start_Time.date() == now.date()]
        
        print(f"\n[STATISTICS]")
        print(f"  Total Sessions: {len(completed_sessions)}")
        print(f"  Total Minutes: {total_minutes}")
        print(f"  Today's Sessions: {len(today_sessions)}")
        print(f"  Average Duration: {round(total_minutes / len(completed_sessions), 1) if completed_sessions else 0} min")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Focus Session Seeding Script")
    print("=" * 60)
    print()
    
    email = "ahmed.hasan@student.zewailcity.edu.e"
    print(f"Adding focus sessions for: {email}")
    print()
    
    seed_focus_sessions_for_student(email)
    
    print()
    print("=" * 60)
    print("Done! Check the Focus Sessions tab to see the data.")
    print("=" * 60)

