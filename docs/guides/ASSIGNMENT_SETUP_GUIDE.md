# Assignment Setup Guide for AI Auto-Grading

## 🤖 What LLM is Used?

The AI grading uses **Ollama** (local LLM) by default. It will automatically:
1. Try to use models in this order of preference:
   - `llama3` (preferred)
   - `mistral`
   - `phi` (fastest, good for quick grading)
   - Any other available model in Ollama

2. **To use Ollama:**
   - Install Ollama: https://ollama.ai
   - Run: `ollama pull llama3` (or `mistral` or `phi`)
   - Make sure Ollama is running on `http://localhost:11434`

3. **If Ollama is not available:**
   - The system will fall back to simple text comparison
   - Grades will still be generated but may be less accurate

---

## 📝 Where to Put Assignment Content

When creating an assignment, here's what goes where:

### 1. **Title** ✅
- The name of the assignment
- Example: "SQL Basics Quiz"

### 2. **Description** ✅
- General information about the assignment
- What it covers, context, etc.
- Example: "This assignment tests your understanding of basic SQL SELECT statements and filtering."

### 3. **Instructions** ✅ (This is where QUESTIONS go!)
- **PUT YOUR QUESTIONS HERE!**
- This is what students see
- Example:
```
Write SQL queries to answer the following questions:

Question 1: Select all students with grade above 85
Question 2: Count courses by department  
Question 3: Insert a new enrollment for student 123 in course 456
```

### 4. **Correct Answer** ✅ (This is what AI uses to grade!)
- **PUT THE CORRECT ANSWER HERE!**
- This is what the AI compares student submissions against
- Only shown when "Enable AI Auto-Grading" is checked
- Example:
```sql
-- Question 1: Select all students with grade above 85
SELECT * FROM students WHERE grade > 85;

-- Question 2: Count courses by department
SELECT department, COUNT(*) as course_count 
FROM courses 
GROUP BY department;

-- Question 3: Insert a new enrollment
INSERT INTO enrollments (student_id, course_id, enrollment_date) 
VALUES (123, 456, '2024-01-15');
```

---

## 🎯 Complete Example Setup

### Assignment Form Fields:

**Title:**
```
SQL Basics Quiz - Database Queries
```

**Description:**
```
This assignment covers basic SQL queries and database design concepts. 
Students will practice writing SELECT statements and designing simple ER diagrams.
```

**Instructions:** (Questions for students)
```
Instructions:
1. Complete all SQL queries in the provided file
2. Design an ER diagram for a library management system
3. Submit your work as a text submission
4. Include your name and student ID on the first page
5. Late submissions will be penalized 10% per day

Questions:
Question 1: Write a SQL query to select all students with grade above 85
Question 2: Write a SQL query to count courses by department
Question 3: Write a SQL query to insert a new enrollment
```

**Correct Answer:** (What AI uses to grade - hidden from students)
```
-- Question 1: Select all students with grade above 85
SELECT * FROM students WHERE grade > 85;

-- Question 2: Count courses by department
SELECT department, COUNT(*) as course_count 
FROM courses 
GROUP BY department;

-- Question 3: Insert a new enrollment
INSERT INTO enrollments (student_id, course_id, enrollment_date) 
VALUES (123, 456, '2024-01-15');
```

**Enable AI Auto-Grading:** ☑️ Check this box

---

## 🔄 How It Works:

1. **Student sees:** Title, Description, and Instructions (questions)
2. **Student submits:** Their answers in the text submission box
3. **AI compares:** Student submission vs. "Correct Answer"
4. **AI grades:** Automatically assigns grade (0 to max_score)
5. **Student sees:** Grade and feedback immediately (if confidence ≥ 70%)

---

## ⚠️ Important Notes:

- **Instructions** = Questions students see and answer
- **Correct Answer** = What AI uses to grade (students don't see this)
- Both should have similar structure for best results
- For coding assignments, format matters (indentation, syntax, etc.)
- For essay/short answer, AI will compare meaning/semantics

---

## 🛠️ Troubleshooting:

**If grading isn't working:**
1. Check if Ollama is running: `ollama list`
2. Check console/terminal for errors
3. Make sure "Enable AI Auto-Grading" is checked
4. Make sure "Correct Answer" field is filled
5. Check if student submitted text (not just a file)

**If grades seem wrong:**
- The AI uses semantic comparison, not exact match
- Check the confidence score (should be ≥ 0.7 for auto-grade)
- You can manually adjust grades in "View Submissions"

