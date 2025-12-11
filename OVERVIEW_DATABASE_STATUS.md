# Overview Page - Database Connection Status

## ❌ **NOT FULLY Connected to Database**

The Overview page is currently showing **hardcoded/empty data** instead of real database data.

---

## 🔍 Current Status

### ✅ **What's Connected:**
- User data (name, role) from database

### ❌ **What's NOT Connected:**

| Section | Status | Issue |
|---------|--------|-------|
| **Notifications** | ❌ Not connected | No data passed from backend |
| **Statistics Cards** | ❌ Not connected | Shows 0 or hardcoded values |
| **Today's Schedule** | ❌ Not connected | Shows empty state |
| **Active Courses** | ❌ Not connected | Shows 0 |
| **Active Tasks** | ❌ Not connected | Shows 0 |
| **Upcoming Events** | ❌ Not connected | Shows 0 |

---

## 📊 Current Implementation

### **Backend** (`app.py`):

```python
@app.route('/overview')
def overview():
    user_id = session.get('user_id')
    user = get_user_data(user_id)
    return render_template('overview.html', user=user, user_data=user)
```

❌ **Problem:** Only passes user data, no statistics or schedule data!

### **Frontend** (`overview.html`):

```html
<h3>{{ stats.total_courses if stats else 0 }}</h3>  <!-- stats is None, shows 0 -->
<h3>{{ stats.active_tasks if stats else 0 }}</h3>   <!-- stats is None, shows 0 -->
{% if today_schedule %}  <!-- today_schedule is None, shows empty -->
```

❌ **Problem:** Template expects data that isn't being provided!

---

## ✅ **What SHOULD Be Implemented**

### **1. Fetch Real Statistics from Database**

```python
@app.route('/overview')
def overview():
    user_id = session.get('user_id')
    user_data = get_user_data(user_id)
    
    # Get student_id
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if student:
        # Get enrolled courses
        enrollment_repo = RepositoryFactory.get_repository("enrollment")
        enrollments = enrollment_repo.get_by_student(student.Student_ID)
        total_courses = len([e for e in enrollments if e.Status == 'enrolled'])
        
        # Get active tasks
        task_repo = RepositoryFactory.get_repository("task")
        tasks = task_repo.get_by_student(student.Student_ID)
        active_tasks = len([t for t in tasks if t.Status == 'pending'])
        
        # Get upcoming calendar events
        calendar_repo = RepositoryFactory.get_repository("calendar")
        events = calendar_repo.get_by_student(student.Student_ID)
        upcoming_events = len(events)
        
        # Get today's schedule
        schedule_repo = RepositoryFactory.get_repository("schedule")
        today_schedule = schedule_repo.get_by_student_and_day(
            student.Student_ID, 
            datetime.now().strftime('%A')
        )
        
        stats = {
            'total_courses': total_courses,
            'active_tasks': active_tasks,
            'upcoming_events': upcoming_events,
            'completed_assignments': 0  # Would need Assignment table
        }
    else:
        stats = {
            'total_courses': 0,
            'active_tasks': 0,
            'upcoming_events': 0,
            'completed_assignments': 0
        }
        today_schedule = []
    
    return render_template(
        'overview.html', 
        user_data=user_data,
        stats=stats,
        today_schedule=today_schedule,
        notifications=[]  # Would fetch from Notification table if exists
    )
```

---

## 🎯 Data Sources (All Available in Database)

| Stat | Table | Query |
|------|-------|-------|
| **Total Courses** | `Enrollment` | `SELECT COUNT(*) WHERE Status='enrolled'` |
| **Active Tasks** | `Task` | `SELECT COUNT(*) WHERE Status='pending'` |
| **Upcoming Events** | `Calendar` | `SELECT COUNT(*) WHERE Date >= TODAY` |
| **Today's Schedule** | `Schedule` | `SELECT * WHERE Day=TODAY AND Student_ID=?` |
| **Notifications** | `Message`? | `SELECT * WHERE Receiver_ID=? ORDER BY Date DESC` |

---

## 🔧 Required Changes

### **File to Edit:** `UNIFY/src/app.py`

**Replace:**
```python
@app.route('/overview')
@app.route('/dashboard')
def overview():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_id = session.get('user_id', DEFAULT_USER_ID)
    user = get_user_data(user_id)
    return render_template('overview.html', user=user, user_data=user)
```

**With:** (See full implementation below)

---

## 📝 Complete Solution

Create `UNIFY/src/controllers/overview_controller.py`:

```python
from flask import Blueprint, render_template, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
from core.user_helper import get_user_data
from datetime import datetime, date

overview_bp = Blueprint("overview", __name__, url_prefix="/overview")

@overview_bp.route("/")
def overview_page():
    """Overview page with real database statistics"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session.get('user_id')
    user_data = get_user_data(user_id)
    
    # Get student
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    stats = {
        'total_courses': 0,
        'active_tasks': 0,
        'upcoming_events': 0,
        'completed_assignments': 0
    }
    today_schedule = []
    notifications = []
    
    if student:
        # Get enrolled courses count
        enrollment_repo = RepositoryFactory.get_repository("enrollment")
        enrollments = enrollment_repo.get_by_student(student.Student_ID)
        stats['total_courses'] = len([e for e in enrollments if e.Status == 'enrolled'])
        
        # Get active tasks count
        task_repo = RepositoryFactory.get_repository("task")
        tasks = task_repo.get_by_student(student.Student_ID)
        stats['active_tasks'] = len([t for t in tasks if t.Status == 'pending'])
        
        # Get upcoming calendar events count
        calendar_repo = RepositoryFactory.get_repository("calendar")
        events = calendar_repo.get_by_student(student.Student_ID)
        today = date.today()
        upcoming = [e for e in events if e.Date and e.Date >= today]
        stats['upcoming_events'] = len(upcoming)
        
        # Get today's schedule
        schedule_repo = RepositoryFactory.get_repository("schedule")
        schedules = schedule_repo.get_by_student(student.Student_ID)
        today_day = datetime.now().strftime('%A').upper()[:3]  # MON, TUE, etc.
        
        today_schedule = []
        for sched in schedules:
            if sched.Day and sched.Day.upper() == today_day:
                today_schedule.append({
                    'time': f"{sched.Start_Time.strftime('%I:%M %p')} - {sched.End_Time.strftime('%I:%M %p')}" if sched.Start_Time and sched.End_Time else 'TBA',
                    'course_name': sched.Course_Code if sched.Course_Code else 'Course',
                    'instructor': sched.Instructor if sched.Instructor else 'TBA',
                    'location': sched.Location if sched.Location else 'TBA',
                    'type': sched.Type if sched.Type else 'Lecture'
                })
        
        # Sort by time
        today_schedule.sort(key=lambda x: x['time'])
        
        # Get notifications (from Message table)
        message_repo = RepositoryFactory.get_repository("message")
        messages = message_repo.get_by_receiver(student.Student_ID)
        notifications = [
            {
                'title': msg.Subject if msg.Subject else 'Notification',
                'message': msg.Content if msg.Content else '',
                'time': msg.Sent_Date.strftime('%I:%M %p') if msg.Sent_Date else 'Now',
                'type': 'message',
                'read': False
            }
            for msg in messages[:5]
        ]
    
    return render_template(
        'overview.html',
        user_data=user_data,
        stats=stats,
        today_schedule=today_schedule,
        notifications=notifications
    )
```

Then register in `app.py`:
```python
from controllers.overview_controller import overview_bp
app.register_blueprint(overview_bp)
```

And update the routes:
```python
# Keep old routes for backwards compatibility
@app.route('/overview')
@app.route('/dashboard')
def overview_redirect():
    return redirect('/overview/')
```

---

## 🧪 Testing

### **Before (Current):**
- Total Courses: **0**
- Active Tasks: **0**
- Upcoming Events: **0**
- Today's Schedule: **Empty**

### **After (With Database):**
- Total Courses: **Real count from Enrollment table**
- Active Tasks: **Real count from Task table**
- Upcoming Events: **Real count from Calendar table**
- Today's Schedule: **Real schedule from Schedule table**

---

## 📊 Current vs. Expected

| Feature | Current | Should Be |
|---------|---------|-----------|
| **Notifications** | Empty | Real messages from database |
| **Course Count** | 0 | Count of enrolled courses |
| **Tasks Count** | 0 | Count of pending tasks |
| **Events Count** | 0 | Count of upcoming calendar events |
| **Today's Schedule** | Empty | Real schedule for today |

---

## 🎯 Summary

### **Current State:**
❌ Overview page shows **no real data**
❌ All statistics show **0**
❌ Today's schedule is **empty**
❌ No notifications shown

### **Required:**
✅ Fetch data from `Enrollment` table
✅ Fetch data from `Task` table
✅ Fetch data from `Calendar` table
✅ Fetch data from `Schedule` table
✅ Fetch data from `Message` table

### **Impact:**
Users see a **lifeless dashboard** instead of a **dynamic overview** of their academic status.

---

## 🚀 Recommendation

**HIGH PRIORITY** - Fix this to provide real value to users!

The Overview page is the **first thing students see** when they log in. It should show:
- Real course enrollment status
- Actual pending tasks
- Today's actual class schedule
- Real notifications/messages

Without database connection, it's just a **static template** with no value.

**Let me implement this for you!** 🎯

