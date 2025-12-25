# 🎓 Unify - Student Assistant Platform

<div align="center">

![Unify Logo](https://img.shields.io/badge/Unify-Student%20Assistant-blue?style=for-the-badge)

**A comprehensive student management system with AI-powered features**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Database Setup](#-database-setup)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Testing](#-testing)
- [Architecture](#-architecture)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Unify** is a modern, full-featured student assistant platform designed to help students manage their academic life efficiently. It combines course management, task tracking, AI-powered note summarization, schedule optimization, and more into a single, intuitive interface.

### Key Highlights

- ✅ **Complete Database Integration** - All features connected to SQL Server
- ✅ **AI-Powered Summarization** - Automatic note summarization using Hugging Face models
- ✅ **Smart Course Registration** - AI conflict-free schedule optimization
- ✅ **Pomodoro Focus Timer** - Built-in productivity timer
- ✅ **Real-time Dashboard** - Dynamic overview with live statistics
- ✅ **Clean Architecture** - Service layer pattern for maintainability

---

## ✨ Features

### 📚 **Course Management**
- Course registration with conflict detection
- AI-powered schedule optimization
- Transcript viewing with GPA calculation
- Enrollment tracking with grades and semesters

### 📝 **Task Management**
- Create, update, and delete tasks
- Priority levels (High, Medium, Low)
- Due date tracking
- Status management (Pending, Completed)
- **Pomodoro Focus Timer** integrated
- **Focus Session Tracking** - Track study sessions with statistics
- **Smart Study Plans** - AI-powered personalized study plans

### 🎯 **Smart Study Plan Generator (FR-AI-4)**
- **AI-Powered Task Decomposition** - Break complex assignments into manageable tasks
- **Intelligent Schedule Generation** - Analyze deadlines and generate daily/weekly schedules
- **Adaptive Planning** - Adjust plans based on productivity and completion rates
- **Resource Recommendations** - RAG-powered study material suggestions
- **Progress Tracking** - Monitor completion rates and adjust plans dynamically
- **Course Integration** - Link study plans to enrolled courses
- **Time Estimation** - AI suggests optimal time allocations for tasks

### 📊 **Focus Session Tracking (FR17)**
- Track study sessions with duration and completion status
- View statistics: Total sessions, total minutes, today's sessions, average duration
- **AI-Powered Feedback** - Get personalized study recommendations based on patterns
- Integration with Pomodoro timer
- Historical data tracking for productivity analysis

### 🤖 **AI Note Summarization**
- Upload PDF, DOCX, or TXT files
- Automatic text extraction
- AI-powered summarization using DistilBART model
- Save summaries to database
- View and manage AI-generated notes

### 📋 **Assignment Management System**
- **Instructor/TA Features:**
  - Create and upload assignments with due dates
  - Upload solution files for reference
  - Provide correct answers for AI auto-grading
  - View all student submissions
  - Manual grading override when needed
  - Review student requests for grade reconsideration
- **Student Features:**
  - View all assignments with due dates
  - Submit assignments with file uploads
  - View grades and feedback
  - Request manual review of AI-graded assignments
  - See assignment status (submitted, graded, pending review)
- **AI Auto-Grading:**
  - Automatic grading using LLM (Ollama/OpenAI/Anthropic)
  - Confidence scoring for grades
  - Always auto-applied (no manual approval needed)
  - Fallback to simple comparison if LLM unavailable
  - Grade notifications when updated

### 🎓 **Advisor Appointment System**
- **Student Features:**
  - Schedule appointments with instructors/advisors
  - View appointment status (pending, scheduled, rejected, completed)
  - See instructor responses and feedback
  - Track appointment history
- **Instructor/TA Features:**
  - View all student appointment requests
  - Approve or reject appointments
  - Provide feedback messages to students
  - Manage appointment calendar
- **Status Management:**
  - Color-coded status indicators (green/yellow/red)
  - Pending approval workflow
  - Automatic notifications

### 🔔 **Notification System**
- Real-time notification bell icon
- Unread notification badge
- Dropdown notification list
- Mark as read functionality
- Role-based notifications
- Database-backed notification storage

### 📅 **Schedule & Calendar**
- Class schedule management
- Calendar events tracking
- Today's schedule view
- Upcoming events notifications

### 🔔 **Smart Reminders**
- Priority alerts for urgent tasks
- Today's agenda view
- Upcoming timeline (7-day view)
- Quick add reminder functionality

### 📊 **Dashboard & Overview**
- Real-time statistics from database
- Active courses count
- Pending tasks count
- Upcoming events count
- Today's class schedule
- Latest notifications
- **Academic Dashboard (Students Only)**:
  - Cumulative GPA calculation and display
  - Course grades overview
  - Cohort comparison (rank, percentile, performance vs batch average)
  - Graduation timeline prediction
  - Credits progress tracking

### 👤 **User Management**
- Role-based access control (RBAC) for Students, Instructors, TAs
- Secure authentication with SHA256 password hashing
- User profiles with role-based avatars
- Session management
- Role-specific navigation and features

---

## 🛠️ Technology Stack

### **Backend**
- **Python 3.8+**
- **Flask** - Web framework
- **SQL Server** - Database (also supports MySQL)
- **PyODBC** - Database connectivity

### **Frontend**
- **HTML5** - Structure
- **CSS3** - Styling (with custom dark theme)
- **JavaScript (ES6+)** - Interactivity
- **Font Awesome** - Icons

### **AI/ML**
- **Transformers** (Hugging Face) - AI models
- **DistilBART-CNN-12-6** - Summarization model
- **Ollama** - Local LLM integration (llama3, mistral, phi)
- **OpenAI API** - Cloud LLM support (optional)
- **Anthropic Claude** - Alternative LLM provider (optional)
- **RAG Engine** - Retrieval-Augmented Generation for resource recommendations
- **PyPDF2** - PDF text extraction
- **python-docx** - DOCX text extraction

### **Architecture**
- **Service Layer Pattern** - Business logic separation
- **Repository Pattern** - Data access abstraction
- **Blueprint Pattern** - Modular routing

---

## 📦 Installation

### **Prerequisites**

- Python 3.8 or higher
- SQL Server (or MySQL)
- pip (Python package manager)
- Git

### **Step 1: Clone the Repository**

```bash
git clone <repository-url>
cd Unify/UNIFY
```

### **Step 2: Create Virtual Environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### **Step 3: Install Dependencies**

```bash
cd src
pip install -r requirements.txt
```

**If requirements.txt doesn't exist, install manually:**

```bash
pip install flask
pip install pyodbc
pip install transformers
pip install torch
pip install pandas
pip install openpyxl
pip install PyPDF2
pip install python-docx
pip install werkzeug
```

### **Step 4: Download AI Model (Optional)**

For AI note summarization:

```bash
python tests/utils/download_model.py
```

Or manually download from: https://huggingface.co/sshleifer/distilbart-cnn-12-6

---

## 🗄️ Database Setup

### **Step 1: Create Database**

**For SQL Server:**
```sql
CREATE DATABASE unify;
GO
```

**For MySQL:**
```sql
CREATE DATABASE unify;
```

### **Step 2: Run Schema**

```bash
# SQL Server
sqlcmd -S localhost -d unify -i src/database/schema.sql

# MySQL
mysql -u root -p unify < src/database/schema.sql
```

### **Step 3: Import Sample Data (Optional)**

```bash
# SQL Server
sqlcmd -S localhost -d unify -i database_sample_data_with_real_courses.sql

# MySQL
mysql -u root -p unify < database_sample_data_with_real_courses.sql
```

### **Step 4: Import Course Schedule**

```bash
cd src
python database/import_schedule_from_excel.py
```

This imports all courses from `data/Schedule 2025.xlsx` into the database.

---

## ⚙️ Configuration

### **Database Configuration**

Edit `src/config/dbconfig.py`:

```python
# SQL Server
DB_CONFIG = {
    'server': 'localhost',
    'database': 'unify',
    'username': 'your_username',
    'password': 'your_password',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

# MySQL (alternative)
DB_CONFIG = {
    'host': 'localhost',
    'database': 'unify',
    'user': 'root',
    'password': 'your_password'
}
```

### **Flask Configuration**

Edit `src/app.py`:

```python
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
```

**For production, use environment variables:**

```bash
export SECRET_KEY='your-production-secret-key'
```

---

## 🚀 Usage

### **Start the Application**

```bash
cd UNIFY/src
python app.py
```

The application will start on `http://localhost:5000`

### **Default Login Credentials**

After importing sample data:

- **Username:** `ahmed_hasan`
- **Password:** `password123`

Or check `database_sample_data_with_real_courses.sql` for all users.

### **Access Pages**

- **Login:** `http://localhost:5000/auth/login`
- **Overview:** `http://localhost:5000/overview`
- **Tasks:** `http://localhost:5000/tasks`
- **Course Registration:** `http://localhost:5000/course-registration`
- **AI Assistant:** `http://localhost:5000/ai-assistant`
- **Transcript:** `http://localhost:5000/transcript`
- **Smart Reminders:** `http://localhost:5000/reminders`
- **Messages:** `http://localhost:5000/messages`
- **Schedule:** `http://localhost:5000/schedule`
- **Calendar:** `http://localhost:5000/calendar`

---

## 🧪 Testing

### **Running Tests**

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_factory.py tests/test_singleton.py -v
pytest tests/test_nfr_requirements.py -v

# Using unittest
python tests/run_tests.py
```

### **Test Coverage**

- **Functional Tests:** 59+ tests
  - Models, Repositories, Factory, Singleton
  - Controllers, Services, Integration
  - Error Handling

- **Non-Functional Tests:** 24 tests
  - Performance, Reliability, Security
  - Scalability, Integrity, Usability, Availability

**Total:** 83+ automated tests

### **Test Evidence**

- `tests/FUNCTIONAL_TESTING_EVIDENCE.txt` - Functional test documentation
- `tests/NON_FUNCTIONAL_TESTING_EVIDENCE.txt` - NFR test documentation
- `tests/test_report.txt` - Latest test execution report

For detailed testing documentation, see `PROJECT_DOCUMENTATION.txt` section 1.
- **Notes & AI Summarizer:** `http://localhost:5000/notes`

---

## 🏗️ Architecture

### **Clean Architecture Pattern**

```
┌─────────────────────────────────────┐
│      Presentation Layer            │
│  (Controllers - HTTP Handling)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Business Logic Layer          │
│  (Services - AI, Optimization)     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Data Access Layer             │
│  (Repositories - Database)         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Database (SQL Server)         │
└─────────────────────────────────────┘
```

### **Key Components**

1. **Controllers** - Handle HTTP requests/responses
2. **Services** - Business logic (AI, optimization)
3. **Repositories** - Database operations
4. **Models** - Data structures
5. **Templates** - HTML views
6. **Static** - CSS, JavaScript, assets

---

## 📡 API Endpoints

### **Authentication**
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### **Tasks**
- `GET /tasks/api/user` - Get user's tasks
- `POST /tasks/api` - Create new task
- `PUT /tasks/api/<id>` - Update task
- `DELETE /tasks/api/<id>` - Delete task
- `GET /tasks/api/focus-sessions/stats` - Get focus session statistics
- `GET /tasks/api/study-plans` - Get all study plans for user
- `POST /tasks/api/study-plans/generate` - Generate new AI study plan
- `GET /tasks/api/study-plans/<id>` - Get study plan details
- `GET /tasks/api/study-plans/<id>/tasks` - Get tasks for a study plan
- `GET /tasks/api/study-plans/<id>/recommendations` - Get RAG-powered resource recommendations
- `PUT /tasks/api/study-plans/tasks/<id>` - Update study task status
- `GET /tasks/api/courses/enrolled` - Get enrolled courses for study plan

### **Course Registration**
- `GET /course-registration/api/courses` - Get available courses
- `POST /course-registration/api/optimize` - Optimize schedule
- `POST /course-registration/api/enroll` - Enroll in courses

### **AI Notes**
- `POST /api/summarize` - Summarize uploaded file
- `GET /api/notes` - Get all AI notes
- `GET /api/notes/<id>` - Get specific note
- `DELETE /api/notes/<id>` - Delete note

### **Assignments**
- `GET /assignments` - Get all assignments (role-based)
- `GET /assignments/<id>` - Get assignment details
- `POST /assignments/create` - Create new assignment (Instructor/TA)
- `PUT /assignments/<id>/edit` - Edit assignment (Instructor/TA)
- `POST /assignments/<id>/submit` - Submit assignment (Student)
- `GET /assignments/<id>/submissions` - View submissions (Instructor/TA)
- `POST /assignments/api/submissions/<id>/grade` - Grade submission
- `POST /assignments/api/submissions/<id>/request-review` - Request grade review (Student)

### **Advisor Appointments**
- `GET /advisor/appointments` - Get student appointments
- `POST /advisor/appointments` - Create appointment request (Student)
- `POST /api/<id>/approve` - Approve appointment (Instructor/TA)
- `POST /api/<id>/reject` - Reject appointment (Instructor/TA)
- `GET /api/advisor/appointments/student/<id>` - Get appointments by student

### **Notifications**
- `GET /api/notifications` - Get all notifications
- `GET /api/notifications/unread` - Get unread notifications
- `PUT /api/notifications/<id>/read` - Mark notification as read

### **Transcript**
- `GET /transcript/api/data` - Get transcript data with GPA

### **Calendar**
- `GET /calendar/api/user` - Get user's calendar events
- `POST /calendar/api` - Create calendar event

### **Overview**
- `GET /overview/` - Get dashboard statistics

---

## 📁 Project Structure

```
UNIFY/
├── src/
│   ├── app.py                      # Main Flask application
│   ├── config/
│   │   └── dbconfig.py            # Database configuration
│   ├── controllers/                # HTTP request handlers
│   │   ├── auth_controller.py
│   │   ├── task_controller.py
│   │   ├── assignment_controller.py
│   │   ├── appointment_controller.py
│   │   ├── advisor_chatbot_controller.py
│   │   ├── notification_controller.py
│   │   ├── course_registration_controller.py
│   │   ├── AI_Note_controller.py
│   │   └── ...
│   ├── services/                   # Business logic layer
│   │   ├── ai_note_service.py
│   │   ├── ai_grading_service.py
│   │   ├── ai_assistant_service.py
│   │   ├── assignment_service.py
│   │   ├── advisor_chatbot_service.py
│   │   ├── notification_service.py
│   │   ├── course_optimization_service.py
│   │   └── llm_service.py
│   ├── repositories/               # Data access layer
│   │   ├── task.repository.py
│   │   ├── assignment.repository.py
│   │   ├── assignment_submission.repository.py
│   │   ├── study_plan.repository.py
│   │   ├── study_task.repository.py
│   │   ├── focus_session.repository.py
│   │   ├── advisor_appointment.repository.py
│   │   ├── notification.repository.py
│   │   ├── enrollment.repository.py
│   │   └── ...
│   ├── models/                     # Data models
│   │   ├── task.py
│   │   ├── assignment.py
│   │   ├── assignment_submission.py
│   │   ├── study_plan.py
│   │   ├── study_task.py
│   │   ├── focus_session.py
│   │   ├── advisor_appointment.py
│   │   ├── notification.py
│   │   ├── student.py
│   │   └── ...
│   ├── database/
│   │   ├── schema.sql              # Database schema
│   │   └── import_schedule_from_excel.py
│   ├── scripts/                    # Utility scripts
│   │   ├── seed_notifications.py
│   │   ├── seed_focus_sessions.py
│   │   └── find_student.py
│   ├── templates/                  # HTML templates
│   │   ├── overview.html
│   │   ├── tasks.html
│   │   ├── student_assignments.html
│   │   ├── assignment_detail.html
│   │   ├── instructor_assignments.html
│   │   ├── create_assignment.html
│   │   ├── edit_assignment.html
│   │   ├── view_submissions.html
│   │   ├── advisor_chatbot.html
│   │   ├── instructor_appointments.html
│   │   └── ...
│   ├── static/
│   │   ├── styles/                 # CSS files
│   │   └── scripts/                # JavaScript files
│   └── core/
│       ├── db_singleton.py         # Database connection singleton
│       ├── user_helper.py          # User data helper
│       └── role_auth.py             # RBAC decorators
├── database_sample_data_with_real_courses.sql
├── README.md
└── requirements.txt
```

---

## 🎨 Features in Detail

### **🍅 Pomodoro Focus Timer & Focus Sessions**

Integrated into the Tasks page:
- 25-minute focus sessions
- 5-minute short breaks
- 15-minute long breaks
- Progress tracking
- Daily statistics
- Keyboard shortcuts (Space = Start/Pause, R = Reset)
- **Automatic session tracking** - Sessions saved to database
- **Statistics dashboard** - View total sessions, minutes, averages
- **AI feedback** - Personalized study recommendations based on patterns

### **🤖 AI Note Summarization**

- Supports PDF, DOCX, and TXT files
- Automatic text extraction
- Chunk-based summarization for long texts
- Saves original and summary to database
- View and manage all summaries

### **📊 Smart Course Registration**

- Search courses by code
- View available sections
- AI-powered conflict detection
- Automatic schedule optimization
- One-click enrollment

### **📈 Real-time Dashboard**

- Live statistics from database
- Today's schedule
- Pending tasks count
- Upcoming events
- Latest notifications

### **🎯 Smart Study Plans**

- **AI-Powered Generation** - Create personalized study plans based on courses and deadlines
- **Task Decomposition** - Break assignments into manageable subtasks
- **Resource Recommendations** - Get RAG-powered study material suggestions
- **Progress Tracking** - Monitor completion with visual progress bars
- **Adaptive Planning** - Plans adjust based on your productivity
- **Course Integration** - Link plans to specific courses
- **Time Estimation** - AI suggests optimal time allocations

### **📋 Assignment Management**

- **For Instructors/TAs:**
  - Create assignments with due dates and instructions
  - Upload solution files for reference
  - Set correct answers for AI grading
  - View and grade all student submissions
  - Handle review requests from students
  
- **For Students:**
  - View all assignments with due dates
  - Submit assignments with file uploads
  - Receive instant AI-graded feedback
  - Request manual review if needed
  - Track submission status

- **AI Auto-Grading:**
  - Uses LLM (Ollama/OpenAI) for intelligent grading
  - Provides confidence scores
  - Always auto-applied for instant feedback
  - Fallback mechanisms for reliability

### **🎓 Advisor Appointments**

- **Student Features:**
  - Schedule appointments with instructors
  - View appointment status and instructor responses
  - Track appointment history
  
- **Instructor Features:**
  - View all appointment requests
  - Approve or reject with feedback
  - Manage appointment calendar

### **🔔 Notification System**

- Real-time notification bell with unread count
- Dropdown list of all notifications
- Mark as read functionality
- Role-based notification delivery
- Database-backed persistent storage

---

## 🔐 Security Features

- **Password Hashing** - SHA256 encryption
- **Session Management** - Secure Flask sessions
- **Authentication** - Required for all pages
- **SQL Injection Prevention** - Parameterized queries
- **File Upload Validation** - Allowed extensions only

---

## 🧪 Testing

### **Running Tests**

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_factory.py tests/test_singleton.py -v
pytest tests/test_nfr_requirements.py -v

# Using unittest
python tests/run_tests.py
```

### **Test Coverage**

- **Functional Tests:** 59+ tests
  - Models, Repositories, Factory, Singleton
  - Controllers, Services, Integration
  - Error Handling

- **Non-Functional Tests:** 24 tests
  - Performance, Reliability, Security
  - Scalability, Integrity, Usability, Availability

**Total:** 83+ automated tests

### **Test Evidence**

- `tests/FUNCTIONAL_TESTING_EVIDENCE.txt` - Functional test documentation
- `tests/NON_FUNCTIONAL_TESTING_EVIDENCE.txt` - NFR test documentation
- `tests/test_report.txt` - Latest test execution report

### **Utility Scripts**

```bash
# Test database connection
python src/utils/test_db_connection.py

# Create test user
python src/utils/create_test_user.py

# Add student to test user
python src/utils/add_student_to_test_user.py
```

For detailed testing documentation, see `PROJECT_DOCUMENTATION.txt` section 1.

---

## 📝 Database Migrations

### **Add Grade and Semester to Enrollment**

```bash
# SQL Server
sqlcmd -S localhost -d unify -i src/database/migrations/add_grade_semester_to_enrollment.sql
```

---

## 🐛 Troubleshooting

### **Database Connection Issues**

1. Check `src/config/dbconfig.py` settings
2. Verify SQL Server is running
3. Check firewall settings
4. Test connection: `python tests/test_connection.py`

### **AI Model Not Loading**

1. Ensure internet connection (first download)
2. Run: `python tests/utils/download_model.py`
3. Check disk space (models are large)
4. Verify transformers library is installed

### **Import Schedule Fails**

1. Check `data/Schedule 2025.xlsx` exists
2. Verify pandas and openpyxl are installed
3. Check file format matches expected columns

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### **Code Style**

- Follow PEP 8 for Python
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused (single responsibility)

---

## 📄 License

This project is part of **CSAI 203 - Team 27** coursework.

---

## 👥 Team

**CSAI 203 - Team 27**

- Development Team
- Zewail City University

---

## 📚 Documentation

### **Complete Project Documentation**

For comprehensive documentation including:
- Testing methodology (manual + automated)
- User documentation (installation, usage, configuration)
- Technical documentation (architecture, MVC, API endpoints, database schema)

**See: `PROJECT_DOCUMENTATION.txt`** (5-page comprehensive document)

### **Quick References**

- [API Endpoints](#-api-endpoints)
- [Architecture Guide](#-architecture)
- [Testing Guide](#-testing)
- [Installation Guide](#-installation)

### **Additional Documentation**

- `docs/guides/` - Feature-specific guides
  - AI Assistant guides
  - LLM Integration guides
  - Multi-tenant setup guides
  - Refactoring summaries

- `tests/FUNCTIONAL_TESTING_EVIDENCE.txt` - Functional test evidence
- `tests/NON_FUNCTIONAL_TESTING_EVIDENCE.txt` - NFR test evidence
- `FINAL_STRUCTURE_REPORT.md` - Project structure analysis

---

## 🚧 Roadmap

- [x] Smart Study Plan Generator (FR-AI-4)
- [x] Focus Session Tracking (FR17)
- [x] AI-Powered Assignment Grading
- [x] Resource Recommendations using RAG
- [x] Advisor Appointment System
- [x] Notification System
- [ ] Email notifications
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Integration with Google Calendar
- [ ] Multi-language support
- [ ] Dark/Light theme toggle (enhanced)
- [ ] Export transcript to PDF
- [ ] Group study features
- [ ] Advanced task decomposition with dependencies
- [ ] Study plan templates library

---

## 📞 Support

For issues, questions, or contributions:

1. Check existing documentation
2. Review troubleshooting section
3. Open an issue on GitHub
4. Contact the development team

---

## 🙏 Acknowledgments

- **Hugging Face** - For AI models and transformers library
- **Flask** - Web framework
- **Font Awesome** - Icons
- **Zewail City University** - Academic support

---

<div align="center">

**Made with ❤️ by CSAI 203 - Team 27**

[⬆ Back to Top](#-unify---student-assistant-platform)

</div>
