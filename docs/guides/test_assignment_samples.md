# Sample Assignment Data for AI Grading Testing

## Assignment 1: SQL Basics Quiz

### Assignment Details:
- **Title**: "SQL Basics Quiz - Database Queries"
- **Course**: Use any course from your database (e.g., "Database Systems", "CS 301")
- **Description**: "This assignment tests your understanding of basic SQL SELECT statements and filtering."
- **Instructions**: "Write SQL queries to answer the following questions. Submit your answers as a text file or directly in the text submission box."
- **Due Date**: 2024-12-20 23:59
- **Max Score**: 100
- **Assignment Type**: Quiz
- **Enable AI Auto-Grading**: Yes
- **Correct Answer**: 
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

### Student Submission 1 (CORRECT):
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

### Student Submission 2 (INCORRECT - Wrong WHERE condition):
```sql
-- Question 1: Select all students with grade above 85
SELECT * FROM students WHERE grade >= 85;

-- Question 2: Count courses by department
SELECT department, COUNT(*) as course_count 
FROM courses 
GROUP BY department;

-- Question 3: Insert a new enrollment
INSERT INTO enrollments (student_id, course_id, enrollment_date) 
VALUES (123, 456, '2024-01-15');
```
**Note**: Uses `>=` instead of `>` in Question 1 - this is the intentional wrong answer.

---

## Assignment 2: Python Programming Exercise

### Assignment Details:
- **Title**: "Python List Operations and Functions"
- **Course**: Use any programming course (e.g., "Introduction to Programming", "CS 101")
- **Description**: "Write Python functions to manipulate lists and demonstrate understanding of basic Python data structures."
- **Instructions**: "Write Python code for the following tasks. Ensure your code is properly formatted and includes comments."
- **Due Date**: 2024-12-25 23:59
- **Max Score**: 100
- **Assignment Type**: Homework
- **Enable AI Auto-Grading**: Yes
- **Correct Answer**:
```python
# Question 1: Write a function to find the maximum number in a list
def find_max(numbers):
    if not numbers:
        return None
    max_num = numbers[0]
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

# Question 2: Write a function to reverse a list
def reverse_list(lst):
    return lst[::-1]

# Question 3: Write a function to count occurrences of an element
def count_occurrences(lst, element):
    count = 0
    for item in lst:
        if item == element:
            count += 1
    return count

# Test cases
print(find_max([1, 5, 3, 9, 2]))  # Should output: 9
print(reverse_list([1, 2, 3, 4]))  # Should output: [4, 3, 2, 1]
print(count_occurrences([1, 2, 2, 3, 2], 2))  # Should output: 3
```

### Student Submission 1 (CORRECT):
```python
# Question 1: Write a function to find the maximum number in a list
def find_max(numbers):
    if not numbers:
        return None
    max_num = numbers[0]
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

# Question 2: Write a function to reverse a list
def reverse_list(lst):
    return lst[::-1]

# Question 3: Write a function to count occurrences of an element
def count_occurrences(lst, element):
    count = 0
    for item in lst:
        if item == element:
            count += 1
    return count

# Test cases
print(find_max([1, 5, 3, 9, 2]))  # Should output: 9
print(reverse_list([1, 2, 3, 4]))  # Should output: [4, 3, 2, 1]
print(count_occurrences([1, 2, 2, 3, 2], 2))  # Should output: 3
```

### Student Submission 2 (INCORRECT - Wrong reverse implementation):
```python
# Question 1: Write a function to find the maximum number in a list
def find_max(numbers):
    if not numbers:
        return None
    max_num = numbers[0]
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

# Question 2: Write a function to reverse a list
def reverse_list(lst):
    return list(reversed(lst))

# Question 3: Write a function to count occurrences of an element
def count_occurrences(lst, element):
    count = 0
    for item in lst:
        if item == element:
            count += 1
    return count

# Test cases
print(find_max([1, 5, 3, 9, 2]))  # Should output: 9
print(reverse_list([1, 2, 3, 4]))  # Should output: [4, 3, 2, 1]
print(count_occurrences([1, 2, 2, 3, 2], 2))  # Should output: 3
```
**Note**: Uses `list(reversed(lst))` instead of `lst[::-1]` - technically works but uses built-in function instead of slicing as expected.

---

## How to Use These Samples:

1. **Create Assignment 1** in the instructor portal:
   - Copy the Assignment 1 details above
   - Paste the "Correct Answer" into the "Correct Answer" field
   - Enable "AI Auto-Grading"

2. **Submit as Student** (Correct Answer):
   - Copy Student Submission 1 (CORRECT) text
   - Paste into the text submission box

3. **Submit as Student** (Incorrect Answer):
   - Create another submission or use a different student account
   - Copy Student Submission 2 (INCORRECT) text
   - Paste into the text submission box

4. **Repeat for Assignment 2** to test with different content type (Python code)

5. **Test AI Grading**:
   - As instructor, go to "View Submissions"
   - The AI should grade the correct submission with high score
   - The incorrect submission should receive lower score with feedback

---

## Quick Test Assignment (Simple Text):

### Assignment 3: Short Answer Question
- **Title**: "Explain Database Normalization"
- **Description**: "Explain the concept of database normalization in 2-3 sentences."
- **Correct Answer**: "Database normalization is the process of organizing data in a database to reduce redundancy and dependency. It involves dividing large tables into smaller, related tables and defining relationships between them. The main goals are to eliminate data redundancy, minimize data modification issues, and simplify database structure."

**Correct Student Answer**:
"Database normalization is the process of organizing data in a database to reduce redundancy and dependency. It involves dividing large tables into smaller, related tables and defining relationships between them. The main goals are to eliminate data redundancy, minimize data modification issues, and simplify database structure."

**Incorrect Student Answer**:
"Normalization means making the database faster by adding more indexes and storing everything in one big table."

