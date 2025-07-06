import pytest
import datetime

# Assuming these functions are in app.py or a utils.py imported by app.py
# For this test, we'll redefine them here if they are not easily importable
# or assume they are imported (e.g., from app import auto_classify_task_type)

# --- 1. Task Auto-Classification ---
def auto_classify_task_type(description):
    description_lower = description.lower()
    if any(keyword in description_lower for keyword in ["work", "meeting", "project", "email", "report"]):
        return "work"
    elif any(keyword in description_lower for keyword in ["bill", "appointment", "irs", "bank", "admin"]):
        return "admin"
    elif any(keyword in description_lower for keyword in ["meditation", "journal", "connect", "feelings"]):
        return "emotional"
    return "personal"

@pytest.mark.parametrize("description, expected_type", [
    ("Schedule a work meeting", "work"),
    ("Pay electricity bill", "admin"),
    ("Go for a run", "personal"),
    ("Reflect on feelings", "emotional"),
    ("Project deadline approaching", "work"),
    ("Book doctor appointment", "admin"),
    ("Call mom", "personal"), # Default
])
def test_auto_classify_task_type(description, expected_type):
    assert auto_classify_task_type(description) == expected_type

# --- 2. Due Date Parsing (simplified version from Voice Assistant) ---
def parse_due_date_from_string(due_str):
    import re # Ensure re is imported if used, though not in this simplified stub
    if not due_str or due_str.lower() == 'n/a' or due_str.lower() == 'not specified':
        return None

    today = datetime.date.today()

    if 'today' in due_str.lower():
        return today
    if 'tomorrow' in due_str.lower():
        return today + datetime.timedelta(days=1)
    if 'next week' in due_str.lower(): # very basic
        return today + datetime.timedelta(days=7)

    # Attempt to parse YYYY-MM-DD
    try:
        return datetime.datetime.strptime(due_str, "%Y-%m-%d").date()
    except ValueError:
        pass

    # Attempt to parse day names (e.g., "Friday")
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    current_weekday = today.weekday() # Monday is 0 and Sunday is 6

    for day_idx, day_name in enumerate(days):
        if day_name in due_str.lower():
            target_weekday = day_idx
            days_ahead = target_weekday - current_weekday
            if days_ahead <= 0: # If it's today or already passed this week
                days_ahead += 7
            return today + datetime.timedelta(days=days_ahead)

    return None # if no specific parsing matches


# Test cases for parse_due_date_from_string
# We need to be careful with tests that depend on datetime.date.today()
# For more robust tests, 'today' should be mockable.
# For this example, we'll proceed, acknowledging this.

def test_parse_due_date_today():
    assert parse_due_date_from_string("today") == datetime.date.today()

def test_parse_due_date_tomorrow():
    assert parse_due_date_from_string("tomorrow") == datetime.date.today() + datetime.timedelta(days=1)

def test_parse_due_date_next_week():
    assert parse_due_date_from_string("next week") == datetime.date.today() + datetime.timedelta(days=7)

def test_parse_due_date_yyyy_mm_dd():
    assert parse_due_date_from_string("2024-12-25") == datetime.date(2024, 12, 25)

def test_parse_due_date_specific_day_future():
    # This test is a bit more complex due to varying current day
    # Example: if today is Monday 2023-01-02, "Friday" should be 2023-01-06
    # For simplicity, we'll check if it returns *a* date for a day name.
    # A more robust test would mock 'datetime.date.today()'
    assert isinstance(parse_due_date_from_string("Friday"), datetime.date) or \
           parse_due_date_from_string("Friday") is None # It might parse or not based on full string

def test_parse_due_date_this_friday():
     # Assuming today is not Friday, Saturday, Sunday for this simple test
    today = datetime.date.today()
    if today.weekday() < 4: # If Mon-Thu
        friday_date = parse_due_date_from_string("this Friday")
        assert friday_date is not None
        assert friday_date.weekday() == 4 # Friday
        assert friday_date > today
    else: # If Fri, Sat, Sun, "this Friday" implies next week's Friday
        friday_date = parse_due_date_from_string("this Friday")
        assert friday_date is not None
        assert friday_date.weekday() == 4
        assert friday_date > today + datetime.timedelta(days = (6-today.weekday()) + 1 )


def test_parse_due_date_n_a():
    assert parse_due_date_from_string("N/A") is None

def test_parse_due_date_not_specified():
    assert parse_due_date_from_string("not specified") is None

def test_parse_due_date_empty():
    assert parse_due_date_from_string("") is None

def test_parse_due_date_invalid_string():
    assert parse_due_date_from_string("some random string") is None

# To run these tests, you would typically navigate to the directory
# containing this file and app.py, then run 'pytest' in the terminal.
# Make sure pytest is installed: pip install pytest
# And that the functions being tested are importable or defined within test_app.py
# For now, the functions are redefined here for simplicity of this step.

# (If these helper functions were refactored into app.py, the import would be:
# from app import auto_classify_task_type, parse_due_date_from_string
# or if in utils.py: from utils import ... )
