"""
Python script to insert sample data into the database
This can be run as an alternative to running the SQL script directly
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.db_singleton import DatabaseConnection
from datetime import datetime, timedelta
import json

def insert_sample_data():
    """Insert sample data into the database"""
    db = DatabaseConnection()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        print("Inserting sample data...")
        
        # Insert Users
        print("  - Inserting Users...")
        users_data = [
            (1, 'john_doe', 'john.doe@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
            (2, 'jane_smith', 'jane.smith@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
            (3, 'prof_brown', 'prof.brown@university.edu', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
            (4, 'prof_wilson', 'prof.wilson@university.edu', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
            (5, 'alice_student', 'alice@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
            (6, 'bob_student', 'bob@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
        ]
        
        for user_id, username, email, pwd_hash in users_data:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM [User] WHERE User_ID = ?)
                    INSERT INTO [User] (User_ID, Username, Email, Password_Hash, Created_At)
                    VALUES (?, ?, ?, ?, GETDATE())
                """, (user_id, user_id, username, email, pwd_hash))
            except Exception as e:
                print(f"    Warning: User {user_id} might already exist: {e}")
        
        # Insert Students
        print("  - Inserting Students...")
        students_data = [
            (1, 1, 'Computer Science', 2, 3.5),
            (2, 2, 'Computer Science', 3, 3.8),
            (5, 5, 'Computer Science', 1, 3.2),
            (6, 6, 'Engineering', 2, 3.6),
        ]
        
        for student_id, user_id, dept, year, gpa in students_data:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM Student WHERE Student_ID = ?)
                    INSERT INTO Student (Student_ID, User_ID, Department, Year_Level, GPA)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, student_id, user_id, dept, year, gpa))
            except Exception as e:
                print(f"    Warning: Student {student_id} might already exist: {e}")
        
        # Insert Instructors
        print("  - Inserting Instructors...")
        instructors_data = [
            (1, 3, 'Computer Science', 'Building A, Room 201', 'prof.brown@university.edu'),
            (2, 4, 'Computer Science', 'Building A, Room 205', 'prof.wilson@university.edu'),
        ]
        
        for instr_id, user_id, dept, office, email in instructors_data:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM Instructor WHERE Instructor_ID = ?)
                    INSERT INTO Instructor (Instructor_ID, User_ID, Department, Office, Email)
                    VALUES (?, ?, ?, ?, ?)
                """, (instr_id, instr_id, user_id, dept, office, email))
            except Exception as e:
                print(f"    Warning: Instructor {instr_id} might already exist: {e}")
        
        # Insert Courses
        print("  - Inserting Courses...")
        courses_data = [
            (1, 'Introduction to Programming', 3, 1),
            (2, 'Data Structures and Algorithms', 4, 1),
            (3, 'Database Systems', 3, 2),
            (4, 'Web Development', 3, 2),
            (5, 'Machine Learning', 4, 1),
        ]
        
        for course_id, name, credits, instr_id in courses_data:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM Course WHERE Course_ID = ?)
                    INSERT INTO Course (Course_ID, Course_Name, Credits, Instructor_ID, Schedule)
                    VALUES (?, ?, ?, ?, 'TBA')
                """, (course_id, course_id, name, credits, instr_id))
            except Exception as e:
                print(f"    Warning: Course {course_id} might already exist: {e}")
        
        # Insert Course Schedule Slots
        print("  - Inserting Course Schedule Slots...")
        slots_data = [
            (1, 1, 'CS 101', 1, 'Monday', '10:00', '11:30', 'lecture', 'LCTR', 2024, 'SPRING'),
            (2, 1, 'CS 101', 1, 'Wednesday', '10:00', '11:30', 'lecture', 'LCTR', 2024, 'SPRING'),
            (4, 2, 'CS 201', 1, 'Tuesday', '14:00', '16:00', 'lecture', 'LCTR', 2024, 'SPRING'),
            (5, 2, 'CS 201', 1, 'Thursday', '14:00', '16:00', 'lecture', 'LCTR', 2024, 'SPRING'),
            (7, 3, 'CS 301', 1, 'Monday', '13:00', '14:30', 'lecture', 'LCTR', 2024, 'SPRING'),
            (8, 3, 'CS 301', 1, 'Wednesday', '13:00', '14:30', 'lecture', 'LCTR', 2024, 'SPRING'),
        ]
        
        for slot_id, course_id, code, section, day, start, end, stype, subtype, year, term in slots_data:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM Course_Schedule_Slot WHERE Slot_ID = ?)
                    INSERT INTO Course_Schedule_Slot (Slot_ID, Course_ID, Course_Code, Section, Day, Start_Time, End_Time, Slot_Type, Sub_Type, Academic_Year, Term)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (slot_id, slot_id, course_id, code, section, day, start, end, stype, subtype, year, term))
            except Exception as e:
                print(f"    Warning: Schedule slot {slot_id} might already exist: {e}")
        
        # Insert Enrollments
        print("  - Inserting Enrollments...")
        enrollments_data = [
            (1, 1, 1, 'enrolled', None, 'Spring 2024'),
            (2, 1, 2, 'enrolled', None, 'Spring 2024'),
            (3, 1, 3, 'completed', 'A', 'Fall 2023'),
            (4, 2, 2, 'enrolled', None, 'Spring 2024'),
            (5, 2, 3, 'enrolled', None, 'Spring 2024'),
        ]
        
        for enroll_id, student_id, course_id, status, grade, semester in enrollments_data:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM Enrollment WHERE Enrollment_ID = ?)
                    INSERT INTO Enrollment (Enrollment_ID, Student_ID, Course_ID, Status, Grade, Semester)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (enroll_id, enroll_id, student_id, course_id, status, grade, semester))
            except Exception as e:
                print(f"    Warning: Enrollment {enroll_id} might already exist: {e}")
        
        # Insert Tasks
        print("  - Inserting Tasks...")
        due_date1 = datetime.now() + timedelta(days=7)
        due_date2 = datetime.now() + timedelta(days=14)
        
        tasks_data = [
            (1, 1, 'Complete Programming Assignment 1', due_date1, 'high', 'pending'),
            (2, 1, 'Study for Midterm Exam', due_date2, 'high', 'pending'),
            (3, 2, 'Database Project - Phase 1', due_date1, 'high', 'pending'),
        ]
        
        for task_id, student_id, title, due_date, priority, status in tasks_data:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM [Task] WHERE Task_ID = ?)
                    INSERT INTO [Task] (Task_ID, Student_ID, Task_Title, Due_Date, Priority, Status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (task_id, task_id, student_id, title, due_date, priority, status))
            except Exception as e:
                print(f"    Warning: Task {task_id} might already exist: {e}")
        
        # Insert Messages
        print("  - Inserting Messages...")
        msg_time1 = datetime.now() - timedelta(hours=2)
        msg_time2 = datetime.now() - timedelta(hours=1)
        
        messages_data = [
            (1, 3, 1, 'Hi John, please submit your assignment by Friday.', msg_time1, 0),
            (2, 1, 3, 'Thank you professor, I will submit it on time.', msg_time2, 1),
            (3, 2, 1, 'Hey John, can you help me with the database assignment?', datetime.now() - timedelta(hours=5), 0),
        ]
        
        for msg_id, sender_id, receiver_id, text, timestamp, is_read in messages_data:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM [Message] WHERE Message_ID = ?)
                    INSERT INTO [Message] (Message_ID, Sender_ID, Receiver_ID, Message_Text, Timestamp, Is_Read)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (msg_id, msg_id, sender_id, receiver_id, text, timestamp, is_read))
            except Exception as e:
                print(f"    Warning: Message {msg_id} might already exist: {e}")
        
        # Insert Calendar Events
        print("  - Inserting Calendar Events...")
        event_date1 = datetime.now().date() + timedelta(days=14)
        event_date2 = datetime.now().date() + timedelta(days=2)
        
        events_data = [
            (1, 1, 'Programming Midterm Exam', event_date1, '10:00', 'Course'),
            (2, 1, 'Study Group Meeting', event_date2, '18:00', 'Student'),
            (3, 2, 'Database Project Presentation', datetime.now().date() + timedelta(days=21), '14:00', 'Course'),
        ]
        
        for event_id, student_id, title, date, time_str, source in events_data:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM Calendar WHERE Event_ID = ?)
                    INSERT INTO Calendar (Event_ID, Student_ID, Title, Date, Time, Source)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (event_id, event_id, student_id, title, date, time_str, source))
            except Exception as e:
                print(f"    Warning: Calendar event {event_id} might already exist: {e}")
        
        # Insert Reminders
        print("  - Inserting Reminders...")
        reminder_time1 = datetime.now() + timedelta(days=13)
        
        reminders_data = [
            (1, 1, 1, reminder_time1, 'pending'),
            (2, 1, 2, datetime.now() + timedelta(days=2), 'pending'),
        ]
        
        for rem_id, student_id, event_id, rem_time, status in reminders_data:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM Reminder WHERE Reminder_ID = ?)
                    INSERT INTO Reminder (Reminder_ID, Student_ID, Event_ID, Reminder_Time, Status)
                    VALUES (?, ?, ?, ?, ?)
                """, (rem_id, rem_id, student_id, event_id, rem_time, status))
            except Exception as e:
                print(f"    Warning: Reminder {rem_id} might already exist: {e}")
        
        # Insert User Settings for all users
        print("  - Inserting User Settings...")
        cursor.execute("""
            INSERT INTO [User_Settings] (User_ID, email_notifications, push_notifications, calendar_reminders, assignment_deadlines, theme, language)
            SELECT User_ID, 1, 1, 1, 1, 'dark', 'en'
            FROM [User]
            WHERE User_ID NOT IN (SELECT User_ID FROM User_Settings)
        """)
        
        conn.commit()
        print("\n✅ Sample data inserted successfully!")
        print("\nDefault credentials:")
        print("  - Student: john.doe@example.com / password123")
        print("  - Student: jane.smith@example.com / password123")
        print("  - Instructor: prof.brown@university.edu / password123")
        print("  - Instructor: prof.wilson@university.edu / password123")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error inserting sample data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("INSERTING SAMPLE DATA INTO UNIFY DATABASE")
    print("=" * 60)
    insert_sample_data()

