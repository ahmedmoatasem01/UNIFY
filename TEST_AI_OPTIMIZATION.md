# AI Course Conflict Optimization - Testing Guide

## ✅ What It Does

The AI optimization uses a **backtracking algorithm** to find conflict-free course schedules.

### **Key Features:**

1. **Time Conflict Detection**
   - Checks if two time slots overlap on the same day
   - Formula: `start1 < end2 AND start2 < end1`

2. **Backtracking Algorithm**
   - Tries different section combinations
   - Backtracks when conflict is found
   - Finds optimal solution automatically

3. **Smart Section Selection**
   - Tests all possible section combinations
   - Picks the first conflict-free combination
   - Handles lectures + labs + tutorials

## 🧪 How to Test

### Test Case 1: **No Conflicts** (Should Work)

1. Go to: `http://localhost:5000/course-registration`
2. Add these courses (example):
   - CSAI 101
   - MATH 101
   - IT 101
3. Click **"Optimize Schedule"**
4. ✅ Should show: **"Schedule optimized successfully"**
5. ✅ Should display: Visual calendar with no overlapping slots

---

### Test Case 2: **With Conflicts** (Should Find Solution)

1. Add 5-6 courses that might have conflicts
2. Click **"Optimize Schedule"**
3. ✅ AI should **automatically find** sections that don't conflict
4. ✅ Different sections than what you initially selected

Example:
- You select CSAI 101 (Section 1, conflicts with MATH 101 Section 1)
- AI picks CSAI 101 Section 2 instead
- Result: No conflicts!

---

### Test Case 3: **Impossible Schedule** (Should Warn)

1. Add 10+ courses (too many)
2. Click **"Optimize Schedule"**
3. ✅ Should show: **"No conflict-free combination found"**
4. ✅ Suggests: Remove some courses

---

## 🔍 How the Algorithm Works

### Step 1: **Load Schedule Slots**
```
For each course:
  - Get all sections from database
  - Get all time slots (lectures, labs, tutorials)
```

### Step 2: **Backtracking Search**
```python
def dfs(course_index, chosen_slots):
    if all courses processed:
        return chosen_slots  # Success!
    
    current_course = courses[course_index]
    
    for each section of current_course:
        if no conflicts with chosen_slots:
            # Try this section
            result = dfs(course_index + 1, chosen_slots + this_section)
            if result found:
                return result
    
    return None  # No solution with current path
```

### Step 3: **Conflict Detection**
```
For new slot (e.g., Monday 10:00-11:00):
  For each existing slot:
    If same day AND times overlap:
      CONFLICT! Try different section
```

### Step 4: **Time Overlap Check**
```
Overlap if: start1 < end2 AND start2 < end1

Example:
  Slot A: 10:00-11:00
  Slot B: 10:30-11:30
  
  Check: 10:00 < 11:30 AND 10:30 < 11:00
  Result: TRUE (conflict!)
```

---

## 📊 Database Integration

### Data Flow:

1. **Frontend** sends: `["CSAI 101", "MATH 101", "IT 101"]`
2. **Backend** queries:
   ```sql
   SELECT Course_Code, Section, Day, Start_Time, End_Time
   FROM Course_Schedule_Slot
   WHERE Course_Code IN (?, ?, ?)
   ```
3. **Optimizer** runs backtracking
4. **Returns**: Optimal schedule with specific sections
5. **Frontend** displays: Visual calendar

---

## ✅ Verification Checklist

### **The Optimizer Should:**

- ✅ Fetch all sections from database
- ✅ Check time overlaps correctly
- ✅ Find conflict-free combinations
- ✅ Handle lectures AND labs together
- ✅ Return sorted schedule (by day/time)
- ✅ Handle edge cases (no solution, empty input)

### **Test Scenarios:**

| Test | Input | Expected Output |
|------|-------|-----------------|
| 1. Simple (3 courses) | CSAI 101, MATH 101, IT 101 | ✅ Success |
| 2. Many sections | Course with 5 sections | ✅ Picks best one |
| 3. Lab + Lecture | Course with both | ✅ No conflict between them |
| 4. Same time conflicts | 2 courses, Monday 10am | ✅ Picks different sections |
| 5. Impossible | 10+ conflicting courses | ⚠️ "No solution" message |

---

## 🚨 Common Issues

### Issue 1: **"No matching courses in schedule"**
- **Cause**: Course codes not in database
- **Fix**: Run import script to load Schedule 2025.xlsx

### Issue 2: **"No conflict-free combination found"**
- **Cause**: Too many courses or all sections conflict
- **Fix**: Remove some courses or choose different courses

### Issue 3: **Optimization takes too long**
- **Cause**: Too many sections to try (exponential growth)
- **Fix**: Limit to 5-6 courses max

---

## 🧪 SQL Test: Verify Schedule Data

Run this to ensure data is loaded:

```sql
USE unify;
GO

-- Check if courses have multiple sections
SELECT 
    Course_Code, 
    COUNT(DISTINCT Section) as Num_Sections,
    COUNT(*) as Total_Slots
FROM Course_Schedule_Slot
GROUP BY Course_Code
ORDER BY Num_Sections DESC;

-- Example: Check specific course sections
SELECT 
    Course_Code, 
    Section, 
    Day, 
    Start_Time, 
    End_Time, 
    Slot_Type
FROM Course_Schedule_Slot
WHERE Course_Code = 'CSAI 101'  -- Change to your course
ORDER BY Section, Day, Start_Time;
GO
```

---

## ✅ Expected Behavior

### When You Click "Optimize":

1. **Frontend** collects selected courses
2. **POST** to `/course-registration/api/optimize`
3. **Backend** runs backtracking algorithm
4. **Returns** JSON with conflict-free schedule
5. **Frontend** displays visual calendar

### Success Response:
```json
{
  "status": "ok",
  "message": "Schedule optimized successfully",
  "schedule": [
    {
      "course_code": "CSAI 101",
      "section": 2,
      "day": "MON",
      "start": "10:00",
      "end": "11:00",
      "type": "LECTURE"
    },
    ...
  ]
}
```

### Failure Response:
```json
{
  "status": "no_solution",
  "message": "No conflict-free combination of sections was found.",
  "schedule": null
}
```

---

## 🎯 Final Test

1. **Login** to your app
2. **Go to** Course Registration
3. **Add 3-4 courses**
4. **Click "Optimize Schedule"**
5. **Verify**:
   - ✅ No time conflicts in the visual calendar
   - ✅ Each course shows a specific section
   - ✅ Success message appears
6. **Click "Enroll"**
7. **Check database**:
   ```sql
   SELECT * FROM Enrollment WHERE Student_ID = 1;
   ```
8. ✅ Should see enrolled courses

---

## 🚀 The Algorithm is Working If:

- ✅ It finds conflict-free schedules
- ✅ It tries different sections automatically
- ✅ It handles lectures + labs correctly
- ✅ It detects time overlaps accurately
- ✅ It returns "no solution" when impossible

**Try it now with real courses!** 🎉

