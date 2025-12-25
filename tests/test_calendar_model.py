"""
Unit tests for Calendar model
Tests the Calendar model's core functionality including initialization and serialization
"""
import unittest
import sys
import os
from datetime import date, time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from src.models.calendar import Calendar


class TestCalendarModel(unittest.TestCase):
    """Test cases for Calendar model"""
    
    def test_calendar_initialization_with_all_fields(self):
        """Test Calendar can be initialized with all fields"""
        event_date = date(2024, 12, 25)
        event_time = time(14, 30, 0)
        calendar = Calendar(
            Event_ID=1,
            Student_ID=100,
            Title="Test Event",
            Date=event_date,
            Time=event_time,
            Source="manual"
        )
        self.assertEqual(calendar.Event_ID, 1)
        self.assertEqual(calendar.Student_ID, 100)
        self.assertEqual(calendar.Title, "Test Event")
        self.assertEqual(calendar.Date, event_date)
        self.assertEqual(calendar.Time, event_time)
        self.assertEqual(calendar.Source, "manual")
    
    def test_calendar_initialization_minimal(self):
        """Test Calendar can be initialized with minimal fields"""
        calendar = Calendar()
        self.assertIsNone(calendar.Event_ID)
        self.assertEqual(calendar.Student_ID, 0)
        self.assertEqual(calendar.Title, "")
        self.assertIsNone(calendar.Date)
        self.assertIsNone(calendar.Time)
        self.assertIsNone(calendar.Source)
    
    def test_calendar_to_dict(self):
        """Test Calendar.to_dict() returns correct dictionary representation"""
        event_date = date(2024, 12, 25)
        event_time = time(14, 30, 0)
        calendar = Calendar(
            Event_ID=1,
            Student_ID=100,
            Title="Test Event",
            Date=event_date,
            Time=event_time,
            Source="manual"
        )
        calendar_dict = calendar.to_dict()
        
        self.assertEqual(calendar_dict['Event_ID'], 1)
        self.assertEqual(calendar_dict['Student_ID'], 100)
        self.assertEqual(calendar_dict['Title'], "Test Event")
        self.assertEqual(calendar_dict['Date'], event_date)
        self.assertEqual(calendar_dict['Time'], event_time)
        self.assertEqual(calendar_dict['Source'], "manual")
        self.assertEqual(len(calendar_dict), 6)


if __name__ == '__main__':
    unittest.main()

