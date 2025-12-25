# Smart Study Plan Generator (FR-AI-4)

## Overview
The Smart Study Plan Generator is an AI-powered feature that creates personalized study plans based on course content, deadlines, and student learning patterns. It integrates seamlessly with the existing UNIFY platform's task and focus session systems.

## Features

### 1. **Intelligent Schedule Generation**
- Analyzes upcoming deadlines, exam dates, and course content
- Generates daily/weekly study schedules automatically
- Breaks down large assignments into manageable tasks
- Suggests optimal study times based on focus session history

### 2. **Adaptive Planning**
- Adapts study plans based on student's productivity patterns
- Adjusts plans when deadlines change or new assignments are added
- Learns from student's completion rates
- Optimizes for student's peak performance hours

### 3. **Task Decomposition**
- AI-powered breakdown of complex assignments into smaller subtasks
- Suggests time allocations for each subtask
- Creates dependencies between tasks
- Estimates completion times based on historical data

### 4. **Resource Recommendations**
- Suggests study materials (notes, videos, practice problems) based on course topics
- Uses RAG (Retrieval-Augmented Generation) to retrieve relevant content
- Recommends external resources (textbooks, online courses)
- Links to related course materials

### 5. **Progress Tracking and Adjustments**
- Tracks study plan completion rates
- Automatically adjusts plans when student falls behind
- Sends reminders for upcoming study sessions
- Provides motivation and encouragement messages

## Architecture

### Database Schema

#### StudyPlan Table
Stores personalized study plans for students.

```sql
CREATE TABLE StudyPlan (
    Plan_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    Course_ID INT,
    Plan_Name NVARCHAR(255) NOT NULL,
    Start_Date DATE NOT NULL,
    End_Date DATE NOT NULL,
    Status NVARCHAR(20) CHECK (Status IN ('active', 'paused', 'completed', 'archived')),
    Completion_Percentage DECIMAL(5,2) DEFAULT 0,
    Created_At DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
    FOREIGN KEY (Course_ID) REFERENCES Course(Course_ID)
);
```

#### StudyTask Table
Stores individual tasks within study plans with hierarchical support.

```sql
CREATE TABLE StudyTask (
    Task_ID INT IDENTITY(1,1) PRIMARY KEY,
    Plan_ID INT NOT NULL,
    Parent_Task_ID INT,  -- For subtasks
    Task_Title NVARCHAR(255) NOT NULL,
    Description NVARCHAR(MAX),
    Estimated_Hours DECIMAL(4,1),
    Actual_Hours DECIMAL(4,1),
    Due_Date DATETIME,
    Priority NVARCHAR(10) CHECK (Priority IN ('low', 'medium', 'high')),
    Status NVARCHAR(20) CHECK (Status IN ('pending', 'in_progress', 'completed', 'skipped')),
    Suggested_Resources NVARCHAR(MAX),  -- JSON array
    Created_At DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (Plan_ID) REFERENCES StudyPlan(Plan_ID),
    FOREIGN KEY (Parent_Task_ID) REFERENCES StudyTask(Task_ID)
);
```

#### StudyRecommendation Table
Stores AI-generated resource recommendations.

```sql
CREATE TABLE StudyRecommendation (
    Recommendation_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    Course_ID INT,
    Topic NVARCHAR(255),
    Resource_Type NVARCHAR(50),  -- 'note', 'video', 'practice', 'textbook'
    Resource_Link NVARCHAR(500),
    Reason NVARCHAR(MAX),
    Relevance_Score DECIMAL(3,2),  -- 0.00 to 1.00
    Generated_At DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
    FOREIGN KEY (Course_ID) REFERENCES Course(Course_ID)
);
```

### File Structure

```
src/
├── models/
│   ├── study_plan.py              # StudyPlan model
│   ├── study_task.py              # StudyTask model with hierarchical support
│   └── study_recommendation.py    # StudyRecommendation model
├── repositories/
│   ├── study_plan.repository.py           # CRUD operations for plans
│   ├── study_task.repository.py           # CRUD operations for tasks
│   └── study_recommendation.repository.py # CRUD operations for recommendations
├── services/
│   ├── study_plan_service.py              # Core business logic
│   └── task_decomposition_service.py      # AI task decomposition
├── controllers/
│   └── study_plan_controller.py           # HTTP request handlers
├── templates/
│   ├── study_plans.html                   # Study plans list page
│   └── study_plan_detail.html             # Study plan detail page
└── static/
    ├── styles/
    │   └── study_plans.css                # Premium dark-mode styling
    └── scripts/
        └── study_plans.js                 # Client-side interactivity
```

## API Endpoints

### Study Plans

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/study-plans/student/<student_id>` | Get all study plans for a student |
| POST | `/api/study-plans/generate` | Generate a new study plan |
| GET | `/api/study-plans/<plan_id>` | Get a specific study plan |
| PUT | `/api/study-plans/<plan_id>` | Update a study plan |
| DELETE | `/api/study-plans/<plan_id>` | Delete a study plan |
| GET | `/api/study-plans/<plan_id>/analytics` | Get plan analytics |
| POST | `/api/study-plans/<plan_id>/adjust` | Adjust plan based on progress |

### Study Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/study-plans/<plan_id>/tasks` | Get all tasks for a plan |
| POST | `/api/study-plans/<plan_id>/tasks` | Create a new task |
| PUT | `/api/study-plans/tasks/<task_id>` | Update a task |
| DELETE | `/api/study-plans/tasks/<task_id>` | Delete a task |

### Recommendations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/study-plans/recommendations/student/<student_id>` | Get recommendations for a student |

## Installation & Setup

### 1. Database Setup

Run the SQL schema to create the necessary tables:

```bash
# Connect to your SQL Server database and run:
sqlcmd -S your_server -d your_database -i database/study_plan_schema.sql
```

### 2. Dependencies

All required dependencies are already included in the UNIFY platform. No additional packages needed.

### 3. Configuration

The feature is automatically registered in the Flask application. No additional configuration required.

## Usage

### Creating a Study Plan

1. Navigate to `/study-plans`
2. Click "Create New Plan"
3. Fill in the plan details:
   - Plan name
   - Course (optional)
   - Start and end dates
   - Option to include existing assignments
4. Click "Generate Study Plan"

The AI will:
- Analyze your existing tasks and deadlines
- Break down complex assignments into subtasks
- Schedule tasks based on your productivity patterns
- Generate resource recommendations

### Managing Tasks

1. Open a study plan
2. View all tasks organized by status
3. Add new tasks manually or let AI decompose them
4. Update task status, actual hours, and priority
5. Track progress with real-time completion percentage

### Viewing Recommendations

AI-generated recommendations appear in the sidebar:
- Relevant notes and study materials
- Practice problems
- Video tutorials
- Textbook references

### Adjusting Plans

Click "Adjust Plan" to:
- Reschedule overdue tasks
- Optimize remaining schedule
- Update completion estimates

## AI Components

### 1. Task Decomposition Engine

Located in `task_decomposition_service.py`, this service:
- Identifies task types (writing, project, exam prep, etc.)
- Applies appropriate decomposition templates
- Estimates time requirements
- Suggests optimal priorities

**Task Types Supported:**
- Writing assignments (essays, reports, papers)
- Programming projects
- Exam preparation
- Research tasks
- Presentations
- Problem sets

### 2. Productivity Pattern Analysis

Analyzes focus session history to:
- Identify peak productivity hours
- Calculate average session duration
- Determine completion rates
- Optimize task scheduling

### 3. Time Estimation

Uses historical data to:
- Predict task completion times
- Adjust estimates based on student's past performance
- Account for task complexity

### 4. Resource Recommendation System

**Current Implementation:**
- Template-based recommendations
- Resource type categorization

**Future Enhancement (RAG Integration):**
- Vector database for course materials
- Semantic search for relevant resources
- Context-aware recommendations

## Design Features

### Premium Dark Mode UI
- Glassmorphism effects with backdrop blur
- Smooth gradient accents (primary: #6366f1, secondary: #8b5cf6)
- Micro-animations for enhanced UX
- Responsive grid layouts

### Interactive Elements
- Real-time progress tracking
- Drag-and-drop task reordering (future)
- Inline editing
- Modal-based workflows

### Accessibility
- Semantic HTML structure
- ARIA labels
- Keyboard navigation support
- High contrast ratios

## Integration Points

### With Existing Systems

1. **Task System**
   - Imports existing assignments
   - Creates tasks from study plan
   - Syncs completion status

2. **Focus Session System**
   - Analyzes productivity patterns
   - Suggests optimal study times
   - Tracks actual vs. estimated hours

3. **Course System**
   - Links plans to courses
   - Considers class schedules
   - Accesses course materials

4. **Calendar System**
   - Schedules study sessions
   - Sends reminders
   - Blocks study time

5. **Notes System**
   - Recommends relevant notes
   - Links to course materials
   - Suggests review topics

## Performance Optimization

### Database Indexes
- Student_ID, Course_ID, Status on StudyPlan
- Plan_ID, Parent_Task_ID, Status, Due_Date on StudyTask
- Student_ID, Relevance_Score on StudyRecommendation

### Caching Strategy (Future)
- Cache active plans per student
- Cache productivity patterns
- Cache recommendations

### Query Optimization
- Uses stored procedures for complex analytics
- Implements views for common queries
- Batch operations for recommendations

## Security & Access Control

### Student Access
- Create and manage their own study plans
- View their own tasks and recommendations
- Update task status and hours

### Instructor/TA Access
- View aggregated study plan analytics for their courses
- Monitor student progress
- Identify struggling students

### Advisor Access
- View student study plans
- Provide guidance and feedback
- Track academic progress

## Future Enhancements

### Phase 2: Advanced AI
- [ ] Integration with LLM APIs (OpenAI, Gemini) for better task decomposition
- [ ] RAG implementation for resource recommendations
- [ ] Natural language plan generation
- [ ] Automated progress reports

### Phase 3: Collaboration
- [ ] Study group plans
- [ ] Peer task sharing
- [ ] Collaborative study sessions
- [ ] Social accountability features

### Phase 4: Analytics
- [ ] Predictive analytics for success
- [ ] Learning style adaptation
- [ ] Performance forecasting
- [ ] Personalized study strategies

## Troubleshooting

### Common Issues

**Issue:** Plans not generating
- Check database connection
- Verify student has existing tasks
- Check date range validity

**Issue:** Tasks not decomposing
- Ensure estimated hours > 4.0
- Check task title and description
- Verify auto_decompose flag is set

**Issue:** No recommendations appearing
- Check if student has enrolled courses
- Verify recommendation generation logic
- Check database for existing recommendations

## Testing

### Manual Testing Checklist
- [ ] Create a new study plan
- [ ] Add tasks manually
- [ ] Auto-decompose a large task
- [ ] Update task status
- [ ] View progress updates
- [ ] Adjust plan
- [ ] View recommendations
- [ ] Delete a plan

### API Testing
Use tools like Postman or curl:

```bash
# Get student plans
curl http://localhost:5000/api/study-plans/student/1

# Create a plan
curl -X POST http://localhost:5000/api/study-plans/generate \
  -H "Content-Type: application/json" \
  -d '{"plan_name":"Test Plan","start_date":"2025-01-01","end_date":"2025-01-31"}'
```

## Contributing

When extending this feature:
1. Follow the existing code structure
2. Use repository factory for data access
3. Implement proper error handling
4. Add appropriate logging
5. Update this documentation

## License

Part of the UNIFY platform. All rights reserved.

## Support

For issues or questions:
- Check the troubleshooting section
- Review the code documentation
- Contact the development team

---

**Version:** 1.0.0  
**Last Updated:** December 25, 2025  
**Author:** UNIFY Development Team
