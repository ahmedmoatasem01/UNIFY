"""Schedule loader utility for fetching schedule data."""
import os
from datetime import date, timedelta

try:
    import pandas as pd
except ImportError:
    pd = None

DATA_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'Schedule 2025.xlsx'))


def load_schedule_data():
    """Attempt to load the schedule Excel into a pandas DataFrame.

    Returns the DataFrame on success or None on failure (missing pandas or file issues).
    """
    if pd is None:
        return None
    if not os.path.exists(DATA_FILE):
        return None
    try:
        df = pd.read_excel(DATA_FILE)
        return df
    except Exception:
        return None


def _df_to_items(df):
    """Convert a DataFrame to a list of schedule dicts with normalized keys.

    Expected keys returned: date (datetime.date), time, course, instructor, location, type
    """
    cols = {c.lower(): c for c in df.columns}

    def find_col(substrs):
        for s in substrs:
            for k in cols:
                if s in k:
                    return cols[k]
        return None

    date_col = find_col(['date', 'day', 'datetime'])
    time_col = find_col(['time', 'start'])
    course_col = find_col(['course', 'subject'])
    instr_col = find_col(['instructor', 'teacher', 'lecturer'])
    loc_col = find_col(['location', 'room', 'venue'])
    type_col = find_col(['type', 'kind'])

    items = []
    for _, row in df.iterrows():
        # parse date
        dt = None
        if date_col is not None:
            try:
                dt = pd.to_datetime(row[date_col]).date()
            except Exception:
                dt = None

        def getval(c):
            if c is None:
                return ''
            try:
                v = row[c]
                if pd.isna(v):
                    return ''
                return str(v)
            except Exception:
                return ''

        items.append({
            'date': dt,
            'time': getval(time_col),
            'course': getval(course_col),
            'instructor': getval(instr_col),
            'location': getval(loc_col),
            'type': getval(type_col) or 'class'
        })

    return items


def get_today_schedule():
    """Return a list of schedule items for today.

    Each item is a dict with keys: time, course, instructor, location, type
    """
    df = load_schedule_data()
    if df is not None:
        items = _df_to_items(df)
        today = date.today()
        todays = [
            {k: v for k, v in it.items() if k != 'date'} 
            for it in items 
            if it.get('date') == today
        ]
        return todays

    # Fallback sample data if no Excel/pandas available
    return [
        {
            'time': '09:00 - 10:30',
            'course': 'Data Structures',
            'instructor': 'Dr. A. Smith',
            'location': 'Room 101',
            'type': 'lecture'
        },
        {
            'time': '13:00 - 14:30',
            'course': 'Algorithms',
            'instructor': 'Dr. B. Jones',
            'location': 'Lab 3',
            'type': 'tutorial'
        },
    ]


def get_week_schedule():
    """Return schedule items for the coming 7 days (including today)."""
    df = load_schedule_data()
    if df is not None:
        items = _df_to_items(df)
        today = date.today()
        end = today + timedelta(days=6)
        week = [
            {k: v for k, v in it.items() if k != 'date'} 
            for it in items 
            if it.get('date') and today <= it.get('date') <= end
        ]
        return week

    # Fallback sample covering a week
    return [
        {
            'time': '09:00 - 10:30',
            'course': 'Data Structures',
            'instructor': 'Dr. A. Smith',
            'location': 'Room 101',
            'type': 'lecture'
        },
        {
            'time': '11:00 - 12:30',
            'course': 'Computer Networks',
            'instructor': 'Dr. C. Lee',
            'location': 'Room 202',
            'type': 'lecture'
        },
    ]
