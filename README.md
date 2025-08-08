# Personal Ops Dashboard (Streamlit + SQLite)

A simple, local, no-HTML dashboard for tasks, calendar, notes, and weather. Built with Streamlit and SQLite.

## Quickstart
1. Create and activate a virtual environment.
2. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Features in v1
- Tasks: add, list, complete, delete. Fields: title, due date, tag, priority, est minutes.
- Calendar: upload a `.ics` file to see the next 14 days of events.
- Notes: quick markdown notes saved locally.
- Weather: enter a city and see today + 7-day forecast via Open-Meteo.

## Roadmap
- [ ] Saved filters and quick stats (total estimated minutes this week)
- [ ] Pomodoro focus mode
- [ ] Daily digest (today's tasks + classes + weather)
- [ ] AI helper for time estimates and breaking tasks into steps
- [ ] Google Calendar write access

## Repo Layout
```
personal-ops-dashboard/
  app.py
  db.py
  services/
    calendar.py
    weather.py
  assets/
  requirements.txt
  README.md
```
