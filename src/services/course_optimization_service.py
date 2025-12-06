"""
Course Registration Optimization Service
Handles conflict-free schedule optimization
"""
from datetime import time
from typing import List, Dict, Optional
from repositories.repository_factory import RepositoryFactory


class CourseOptimizationService:
    def __init__(self):
        from core.db_singleton import DatabaseConnection
        self.db_connection = DatabaseConnection()

    def time_to_minutes(self, hhmm: str) -> int:
        """Convert 'HH:MM' string to minutes since midnight"""
        if isinstance(hhmm, time):
            return hhmm.hour * 60 + hhmm.minute
        h, m = hhmm.split(":")
        return int(h) * 60 + int(m)

    def intervals_overlap(self, a_start: str, a_end: str, b_start: str, b_end: str) -> bool:
        """Check if two time intervals overlap"""
        s1, e1 = self.time_to_minutes(a_start), self.time_to_minutes(a_end)
        s2, e2 = self.time_to_minutes(b_start), self.time_to_minutes(b_end)
        return s1 < e2 and s2 < e1

    def detect_time_value(self, val) -> str:
        """Convert time value to 'HH:MM' string"""
        if isinstance(val, time):
            return val.strftime("%H:%M")
        s = str(val)
        if len(s) >= 5 and s[2] == ":":
            return s[:5]
        return s

    def get_course_schedule_slots(self, course_codes: List[str], academic_year: int = 2025, term: str = "SPRING"):
        """
        Get all schedule slots for given course codes from database
        Returns: Dict[course_code, Dict[section_num, List[slots]]]
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            
            if not course_codes:
                return {}
            
            # Build query with placeholders
            placeholders = ','.join(['?' for _ in course_codes])
            query = f"""
                SELECT Slot_ID, Course_ID, Course_Code, Section, Day, 
                       Start_Time, End_Time, Slot_Type, Sub_Type
                FROM Course_Schedule_Slot
                WHERE Course_Code IN ({placeholders})
                AND Academic_Year = ?
                AND Term = ?
                ORDER BY Course_Code, Section, Day, Start_Time
            """
            
            params = list(course_codes) + [academic_year, term]
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            section_map = {}
            for row in rows:
                course_code = row[2]  # Course_Code
                section = row[3]  # Section
                day = row[4]  # Day
                start_time = self.detect_time_value(row[5])  # Start_Time
                end_time = self.detect_time_value(row[6])  # End_Time
                slot_type = row[7]  # Slot_Type
                sub_type = row[8]  # Sub_Type
                
                if course_code not in section_map:
                    section_map[course_code] = {}
                
                if section not in section_map[course_code]:
                    section_map[course_code][section] = []
                
                section_map[course_code][section].append({
                    "course_code": course_code,
                    "course_name": course_code,  # Will be filled from Course table if needed
                    "type": slot_type,
                    "sub_type": sub_type,
                    "section": int(section),
                    "day": day,
                    "start": start_time,
                    "end": end_time,
                })
            
            return section_map
        finally:
            conn.close()

    def is_compatible(self, existing_slots: List[Dict], new_slots: List[Dict]) -> bool:
        """Check if new_slots can be added without conflict with existing_slots"""
        for ns in new_slots:
            for es in existing_slots:
                if ns["day"] != es["day"]:
                    continue
                if self.intervals_overlap(ns["start"], ns["end"], es["start"], es["end"]):
                    return False
        return True

    def backtracking_optimizer(self, section_map: Dict) -> Optional[List[Dict]]:
        """
        Backtracking algorithm to find conflict-free schedule
        Returns: List of slots if solution found, None otherwise
        """
        courses = list(section_map.keys())
        courses.sort()  # deterministic order
        n = len(courses)
        solution_slots = []

        def dfs(i, chosen_slots):
            if i == n:
                return chosen_slots
            course_code = courses[i]
            for section_num, sec_slots in section_map[course_code].items():
                if self.is_compatible(chosen_slots, sec_slots):
                    new_slots = chosen_slots + sec_slots
                    result = dfs(i + 1, new_slots)
                    if result is not None:
                        return result
            return None

        return dfs(0, [])

    def optimize_schedule(self, course_codes: List[str], academic_year: int = 2025, term: str = "SPRING") -> Dict:
        """
        Main optimization function
        Returns: {
            "status": "ok" | "no_solution" | "error",
            "schedule": List[Dict] or None,
            "message": str
        }
        """
        if not course_codes:
            return {"status": "error", "message": "No course codes provided.", "schedule": None}

        section_map = self.get_course_schedule_slots(course_codes, academic_year, term)
        
        if not section_map:
            return {"status": "error", "message": "No matching courses in schedule.", "schedule": None}

        solution = self.backtracking_optimizer(section_map)
        
        if solution is None:
            return {
                "status": "no_solution",
                "message": "No conflict-free combination of sections was found.",
                "schedule": None
            }

        # Sort solution by day then start time
        day_order = {"SAT": 0, "SUN": 1, "MON": 2, "TUES": 3, "WED": 4, "THURS": 5}
        solution_sorted = sorted(solution, key=lambda slot: (
            day_order.get(str(slot["day"]).upper(), 99),
            self.time_to_minutes(slot["start"]),
        ))

        return {
            "status": "ok",
            "schedule": solution_sorted,
            "message": "Schedule optimized successfully"
        }

