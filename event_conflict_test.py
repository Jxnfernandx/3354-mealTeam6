from datetime import datetime
import pytest

# ---- Unit under test ----

def find_event_conflict(new_event, existing_events):
    new_start = new_event['start']
    new_end = new_event['end']

    for old_event in existing_events:
        old_start = old_event['start']
        old_end = old_event['end']
        # check overlap
        if (new_start < old_end) and (new_end > old_start):
            return old_event  # conflicting event
    return None


# ---- Helpers & Fixtures ----

def make_time(hour: int, minute: int = 0) -> datetime:
    """Create a datetime object for a fixed date with given hour/minute."""
    # Date is arbitrary; only time-of-day matters for these tests.
    return datetime(2025, 1, 1, hour, minute)


@pytest.fixture
def existing_events():
    """Common existing events used in all tests except test_empty_calendar."""
    return [
        {
            "title": "Team Meeting",
            "start": make_time(10, 0),  # 10:00
            "end": make_time(11, 0),    # 11:00
        },
        {
            "title": "Lunch Break",
            "start": make_time(12, 0),  # 12:00
            "end": make_time(13, 0),    # 13:00
        },
    ]


# ---- Test Cases ----

def test_no_conflict(existing_events):
    """
    Event occurs after all existing events.
    Input: 14:00 - 15:00
    Expected: None
    """
    new_event = {
        "title": "Afternoon Work Session",
        "start": make_time(14, 0),
        "end": make_time(15, 0),
    }

    result = find_event_conflict(new_event, existing_events)
    assert result is None


def test_direct_overlap(existing_events):
    """
    Event starts during an existing event.
    Input: 10:30 - 11:30
    Expected: Conflict
    """
    new_event = {
        "title": "Client Call",
        "start": make_time(10, 30),
        "end": make_time(11, 30),
    }

    result = find_event_conflict(new_event, existing_events)
    assert result is not None
    # It should conflict with "Team Meeting"
    assert result["title"] == "Team Meeting"


def test_partial_overlap_start(existing_events):
    """
    Event starts before and ends during an existing event.
    Input: 09:30 - 10:30
    Expected: Conflict ('Team Meeting')
    """
    new_event = {
        "title": "Prep Time",
        "start": make_time(9, 30),
        "end": make_time(10, 30),
    }

    result = find_event_conflict(new_event, existing_events)
    assert result is not None
    assert result["title"] == "Team Meeting"


def test_engulfing_overlap(existing_events):
    """
    Event starts before and ends after an existing event.
    Input: 09:00 - 11:30
    Expected: Conflict
    """
    new_event = {
        "title": "Workshop",
        "start": make_time(9, 0),
        "end": make_time(11, 30),
    }

    result = find_event_conflict(new_event, existing_events)
    assert result is not None
    # It at least conflicts with "Team Meeting"
    assert result["title"] == "Team Meeting"


def test_boundary_no_conflict(existing_events):
    """
    Event starts exactly when an existing event ends.
    Input: 11:00 - 12:00
    Expected: None (no conflict at boundary)
    """
    new_event = {
        "title": "Quick Sync",
        "start": make_time(11, 0),
        "end": make_time(12, 0),
    }

    result = find_event_conflict(new_event, existing_events)
    assert result is None


def test_empty_calendar():
    """
    Event is added to an empty calendar.
    Input: 09:00 - 10:00
    Expected: None
    """
    existing_events = []

    new_event = {
        "title": "Morning Focus Time",
        "start": make_time(9, 0),
        "end": make_time(10, 0),
    }

    result = find_event_conflict(new_event, existing_events)
    assert result is None
