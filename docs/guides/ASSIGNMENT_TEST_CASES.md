# Assignment Test Cases for Testing

## Test Case 1: Database Normalization Explanation

### Assignment Details:
- **Title**: "Database Normalization - Short Answer"
- **Course**: Select any database-related course from your system
- **Description**: "Explain the concept of database normalization in your own words."
- **Instructions**: "Write a clear explanation of what database normalization is, why it's important, and provide a brief example. Your answer should be 2-3 paragraphs."
- **Due Date**: Set to a future date (e.g., 2025-01-15 23:59)
- **Max Score**: 100
- **Assignment Type**: Quiz
- **Enable AI Auto-Grading**: ✅ Yes
- **Correct Answer / Solution**:
```
Database normalization is the process of organizing data in a database to reduce redundancy and dependency. It involves dividing large tables into smaller, related tables and defining relationships between them through foreign keys.

The main goals of normalization are to eliminate data redundancy, minimize data modification issues (insert, update, delete anomalies), and simplify database structure. By splitting data into normalized tables, we ensure that each piece of data is stored in only one place, which makes the database more efficient and easier to maintain.

For example, instead of storing student information and course information in one large table that repeats student details for each course enrollment, normalization would separate this into Students, Courses, and Enrollments tables. This reduces storage space, prevents inconsistencies, and makes it easier to update student information in one place.
```

### Student Submission 1 (CORRECT - Should get high score):
```
Database normalization is the process of organizing data in a database to reduce redundancy and dependency. It involves dividing large tables into smaller, related tables and defining relationships between them through foreign keys.

The main goals of normalization are to eliminate data redundancy, minimize data modification issues (insert, update, delete anomalies), and simplify database structure. By splitting data into normalized tables, we ensure that each piece of data is stored in only one place, which makes the database more efficient and easier to maintain.

For example, instead of storing student information and course information in one large table that repeats student details for each course enrollment, normalization would separate this into Students, Courses, and Enrollments tables. This reduces storage space, prevents inconsistencies, and makes it easier to update student information in one place.
```

### Student Submission 2 (INCORRECT - Should get low score):
```
Normalization means making the database faster by adding more indexes and storing everything in one big table. The more indexes you have, the faster queries run. You should put all student data and course data together in one table so you can access everything quickly without joins.
```

**Expected Behavior**: 
- Submission 1 should receive a high grade (85-100) with positive feedback
- Submission 2 should receive a low grade (0-30) with feedback explaining that the student's understanding is incorrect

---

## Test Case 2: Algorithm Complexity Analysis

### Assignment Details:
- **Title**: "Time Complexity Analysis"
- **Course**: Select any algorithms/data structures course
- **Description**: "Analyze and explain the time complexity of common algorithms."
- **Instructions**: "For each of the following operations, explain the time complexity using Big O notation and provide a brief explanation:\n\n1. Linear search in an unsorted array\n2. Binary search in a sorted array\n3. Bubble sort algorithm"
- **Due Date**: Set to a future date (e.g., 2025-01-20 23:59)
- **Max Score**: 100
- **Assignment Type**: Homework
- **Enable AI Auto-Grading**: ✅ Yes
- **Correct Answer / Solution**:
```
1. Linear search in an unsorted array:
   Time Complexity: O(n)
   Explanation: In the worst case, we need to check every element in the array once to find the target or determine it's not present. This requires n comparisons where n is the number of elements.

2. Binary search in a sorted array:
   Time Complexity: O(log n)
   Explanation: Binary search works by repeatedly dividing the search space in half. At each step, we eliminate half of the remaining elements. This logarithmic behavior means we need at most log₂(n) comparisons.

3. Bubble sort algorithm:
   Time Complexity: O(n²)
   Explanation: Bubble sort requires nested loops. The outer loop runs n times, and the inner loop runs n-i times in the worst case. This results in approximately n²/2 comparisons, which simplifies to O(n²) in Big O notation.
```

### Student Submission 1 (CORRECT - Should get high score):
```
1. Linear search in an unsorted array:
   Time Complexity: O(n)
   Explanation: In the worst case, we need to check every element in the array once to find the target or determine it's not present. This requires n comparisons where n is the number of elements.

2. Binary search in a sorted array:
   Time Complexity: O(log n)
   Explanation: Binary search works by repeatedly dividing the search space in half. At each step, we eliminate half of the remaining elements. This logarithmic behavior means we need at most log₂(n) comparisons.

3. Bubble sort algorithm:
   Time Complexity: O(n²)
   Explanation: Bubble sort requires nested loops. The outer loop runs n times, and the inner loop runs n-i times in the worst case. This results in approximately n²/2 comparisons, which simplifies to O(n²) in Big O notation.
```

### Student Submission 2 (PARTIALLY CORRECT - Should get medium score):
```
1. Linear search in an unsorted array:
   Time Complexity: O(n)
   Explanation: We check each element one by one.

2. Binary search in a sorted array:
   Time Complexity: O(n)
   Explanation: We still need to look through the array to find the element.

3. Bubble sort algorithm:
   Time Complexity: O(n²)
   Explanation: There are two nested loops so it's n squared.
```

**Expected Behavior**:
- Submission 1 should receive a high grade (90-100) with positive feedback
- Submission 2 should receive a medium grade (40-60) with feedback noting that binary search complexity is incorrect (should be O(log n), not O(n))

---

## How to Use These Test Cases:

### Step 1: Create Assignments (As Instructor/Doctor)
1. Log in as an instructor/doctor
2. Go to **Assignments** → **Create Assignment**
3. Fill in the details from Test Case 1 or 2
4. **IMPORTANT**: 
   - Enable "AI Auto-Grading" checkbox
   - Paste the "Correct Answer / Solution" text into the "Correct Answer" field
   - Set a future due date
5. Click **Create Assignment**

### Step 2: Submit as Student (Correct Answer)
1. Log in as a student enrolled in the course
2. Go to **Assignments**
3. Click on the assignment
4. Copy the "Student Submission 1 (CORRECT)" text
5. Paste into the text submission box
6. Click **Submit Assignment**
7. **Expected**: Grade should appear automatically (AI-graded) with high score

### Step 3: Submit as Student (Incorrect Answer)
1. Either use a different student account OR resubmit the assignment
2. Copy the "Student Submission 2 (INCORRECT)" text
3. Paste into the text submission box
4. Click **Submit Assignment**
5. **Expected**: Grade should appear automatically with low/medium score and feedback

### Step 4: Test Review Request Feature
1. As student, view the assignment detail page
2. If grade is low, click **Request Manual Review**
3. Add a comment (e.g., "I believe my answer deserves more credit")
4. Click **Submit Review Request**
5. **Expected**: Status should change to "Review Requested"

### Step 5: Test Instructor Review (As Instructor/Doctor)
1. Log in as instructor/doctor
2. Go to **Assignments** → Select the assignment → **View Submissions**
3. **Expected**: You should see a yellow alert box showing "Review Requested by Student" with the student's comment
4. Click **Edit Grade**
5. Adjust the grade and add feedback
6. Click **Update Grade**
7. **Expected**: Review request flag should be cleared, grade updated

### Step 6: Verify Student Notification (As Student)
1. Log in as the student who requested review
2. Go to **Assignments** → View the assignment
3. **Expected**: 
   - Should see "Grade Updated After Review" notification (green box)
   - Badge should show "Graded by Instructor" instead of "AI Graded"
   - Updated grade and feedback should be visible

---

## Quick Testing Checklist:

- [ ] Assignment created successfully
- [ ] AI auto-grading works (grade appears after submission)
- [ ] Correct answer gets high score
- [ ] Incorrect answer gets low score
- [ ] Feedback is provided by AI
- [ ] Student can request review
- [ ] Instructor sees review request
- [ ] Instructor can manually grade after review
- [ ] Student sees "Grade Updated After Review" notification
- [ ] Status badges display correctly (AI Graded vs Graded by Instructor)

---

## Notes:

- These test cases use **text submissions** (not file uploads)
- Both test cases enable **AI Auto-Grading**
- Test Case 1 focuses on **conceptual understanding** (database normalization)
- Test Case 2 focuses on **technical knowledge** (algorithm complexity)
- Use future dates for due dates to avoid "late" status issues
- Make sure the course you select has enrolled students for testing

