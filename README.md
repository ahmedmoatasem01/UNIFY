# 🎓 Unify - Student Assistant Platform

<div align="center">

![Unify Logo](https://img.shields.io/badge/Unify-Student%20Assistant-blue?style=for-the-badge)
![CI Pipeline](https://github.com/YOUR-USERNAME/UNIFY/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11-blue)

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
- [Architecture](#-architecture)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
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

### 🤖 **AI Note Summarization**
- Upload PDF, DOCX, or TXT files
- Automatic text extraction
- AI-powered summarization using DistilBART model
- Save summaries to database
- View and manage AI-generated notes

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

### 👤 **User Management**
- Role-based access (Student, Instructor, Admin)
- Secure authentication with SHA256 password hashing
- User profiles with role-based avatars
- Session management

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

- **Login:** `http://localhost:5000/login`
- **Overview:** `http://localhost:5000/overview`
- **Tasks:** `http://localhost:5000/tasks`
- **Course Registration:** `http://localhost:5000/course-registration`
- **Transcript:** `http://localhost:5000/transcript`
- **Smart Reminders:** `http://localhost:5000/reminders`
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

### **Course Registration**
- `GET /course-registration/api/courses` - Get available courses
- `POST /course-registration/api/optimize` - Optimize schedule
- `POST /course-registration/api/enroll` - Enroll in courses

### **AI Notes**
- `POST /api/summarize` - Summarize uploaded file
- `GET /api/notes` - Get all AI notes
- `GET /api/notes/<id>` - Get specific note
- `DELETE /api/notes/<id>` - Delete note

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
│   │   ├── course_registration_controller.py
│   │   ├── AI_Note_controller.py
│   │   └── ...
│   ├── services/                   # Business logic layer
│   │   ├── ai_note_service.py
│   │   └── course_optimization_service.py
│   ├── repositories/               # Data access layer
│   │   ├── task.repository.py
│   │   ├── enrollment.repository.py
│   │   └── ...
│   ├── models/                     # Data models
│   │   ├── task.py
│   │   ├── student.py
│   │   └── ...
│   ├── database/
│   │   ├── schema.sql              # Database schema
│   │   └── import_schedule_from_excel.py
│   ├── templates/                  # HTML templates
│   │   ├── overview.html
│   │   ├── tasks.html
│   │   └── ...
│   ├── static/
│   │   ├── styles/                 # CSS files
│   │   └── scripts/                # JavaScript files
│   └── core/
│       ├── db_singleton.py         # Database connection singleton
│       └── user_helper.py          # User data helper
├── database_sample_data_with_real_courses.sql
├── README.md
└── requirements.txt
```

---

## 🎨 Features in Detail

### **🍅 Pomodoro Focus Timer**

Integrated into the Tasks page:
- 25-minute focus sessions
- 5-minute short breaks
- 15-minute long breaks
- Progress tracking
- Daily statistics
- Keyboard shortcuts (Space = Start/Pause, R = Reset)

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

---

## 🔐 Security Features

- **Password Hashing** - SHA256 encryption
- **Session Management** - Secure Flask sessions
- **Authentication** - Required for all pages
- **SQL Injection Prevention** - Parameterized queries
- **File Upload Validation** - Allowed extensions only

---

## 🧪 Testing

### **Test Database Connection**

```bash
python tests/test_connection.py
```

### **Test AI Model**

```bash
python tests/test_huggingface_connection.py
```

### **Create Test User**

```bash
python tests/create_test_user.py
```

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

Additional documentation:

- [AI Note Service Architecture](AI_NOTE_SERVICE_ARCHITECTURE.md)
- [Overview Database Connection](OVERVIEW_DATABASE_CONNECTED.md)
- [Pomodoro Timer Feature](POMODORO_TIMER_FEATURE.md)
- [Smart Reminders Summary](SMART_REMINDERS_SUMMARY.md)
- [Course Import Guide](IMPORT_COURSES_GUIDE.md)

---

## 🚧 Roadmap

- [ ] Email notifications
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Integration with Google Calendar
- [ ] Multi-language support
- [ ] Dark/Light theme toggle (enhanced)
- [ ] Export transcript to PDF
- [ ] Group study features

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
