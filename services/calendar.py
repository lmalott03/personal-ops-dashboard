# services/cal.py
from datetime import datetime, timedelta
from icalendar import Calendar

def parse_ics(file_bytes):
    """
    Parse an .ics file (bytes) and return events occurring in the next 14 days.
    Each event: {'title', 'start', 'end', 'location'}
    """
    cal = Calendar.from_ical(file_bytes)
    events = []
    now = datetime.now()
    horizon = now + timedelta(days=14)

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        summary = str(component.get("summary", ""))
        dtstart = component.get("dtstart").dt
        dtend = component.get("dtend").dt if component.get("dtend") else None
        location = str(component.get("location", "")) if component.get("location") else ""

        # Normalize all-day events (date -> datetime at midnight)
        if hasattr(dtstart, "date") and not hasattr(dtstart, "hour"):
            dtstart = datetime(dtstart.year, dtstart.month, dtstart.day, 0, 0)
        if dtend and hasattr(dtend, "date") and not hasattr(dtend, "hour"):
            dtend = datetime(dtend.year, dtend.month, dtend.day, 0, 0)

        # Only keep items within the next 14 days
        if dtstart and now <= dtstart <= horizon:
            events.append({
                "title": summary,
                "start": dtstart,
                "end": dtend,
                "location": location
            })

    events.sort(key=lambda e: e["start"])
    return events
