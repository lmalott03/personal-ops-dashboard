import streamlit as st
from datetime import datetime, date
import pandas as pd
from db import init_db, add_task, list_tasks, update_task_status, delete_task, add_note, list_notes, get_note, update_note, delete_note, set_setting, get_setting
from services.calendar import parse_ics
from services.weather import geocode_city, get_forecast

st.set_page_config(page_title="Personal Ops Dashboard", page_icon="✅", layout="wide")

# Initialize DB
init_db()

# Sidebar settings
st.sidebar.header("Settings")
city = st.sidebar.text_input("Home city", value=get_setting("home_city", "Maryville"))
if st.sidebar.button("Save settings"):
    set_setting("home_city", city)
    st.sidebar.success("Saved")

st.sidebar.markdown("---")
uploaded_ics = st.sidebar.file_uploader("Import .ics calendar", type=["ics"])

tabs = st.tabs(["Tasks", "Calendar", "Notes", "Weather"])

# ---- Tasks Tab ----
with tabs[0]:
    st.subheader("Tasks")
    with st.form("task_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3,2,2])
        with col1:
            title = st.text_input("Title")
        with col2:
            due = st.date_input("Due date", value=None)
        with col3:
            tag = st.text_input("Tag", placeholder="course, work, etc.")
        col4, col5, col6 = st.columns([2,2,2])
        with col4:
            priority = st.selectbox("Priority", ["Low", "Normal", "High"], index=1)
        with col5:
            est = st.number_input("Est. minutes", min_value=0, step=5, value=0)
        with col6:
            add = st.form_submit_button("Add Task")
        if add:
            due_str = due.isoformat() if isinstance(due, date) else None
            if title.strip():
                add_task(title.strip(), due_str, tag.strip() or None, priority, int(est) if est else None)
                st.success("Task added")
            else:
                st.error("Title required")

    st.markdown("### Open Tasks")
    tasks = list_tasks(include_done=False)
    if tasks:
        df = pd.DataFrame(tasks)
        # Pretty columns
        df = df[["id", "title", "due_date", "tag", "priority", "est_min"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
        ids = [t["id"] for t in tasks]
        colA, colB = st.columns(2)
        with colA:
            done_id = st.number_input("Mark done by ID", min_value=0, step=1, value=0)
            if st.button("Mark done"):
                if done_id in ids:
                    update_task_status(int(done_id), "done")
                    st.success(f"Task {int(done_id)} marked done")
                else:
                    st.error("Invalid ID")
        with colB:
            del_id = st.number_input("Delete by ID", min_value=0, step=1, value=0, key="del_id")
            if st.button("Delete task"):
                if del_id in ids:
                    delete_task(int(del_id))
                    st.warning(f"Task {int(del_id)} deleted")
                else:
                    st.error("Invalid ID")
    else:
        st.info("No open tasks. Add one above.")

    st.markdown("### Completed")
    done = pd.DataFrame([t for t in list_tasks(include_done=True) if t['status']=='done'])
    if not done.empty:
        st.dataframe(done[["id","title","due_date","tag","priority","est_min"]], use_container_width=True, hide_index=True)
    else:
        st.caption("No completed tasks yet.")

# ---- Calendar Tab ----
with tabs[1]:
    st.subheader("Upcoming (next 14 days)")
    if uploaded_ics is not None:
        events = parse_ics(uploaded_ics.read())
        if events:
            ev_df = pd.DataFrame([{
                "title": e["title"],
                "start": e["start"].strftime("%Y-%m-%d %H:%M"),
                "end": e["end"].strftime("%Y-%m-%d %H:%M") if e["end"] else "",
                "location": e["location"],
            } for e in events])
            st.dataframe(ev_df, use_container_width=True, hide_index=True)
        else:
            st.info("No events in the next 14 days.")
    else:
        st.caption("Upload a .ics file in the sidebar to view upcoming events.")

# ---- Notes Tab ----
with tabs[2]:
    st.subheader("Notes")
    notes = list_notes()
    left, right = st.columns([1,2])
    with left:
        st.markdown("**Your notes**")
        titles = [f"{n['id']}: {n['title']}" for n in notes] if notes else []
        selected = st.selectbox("Select", options=["(new)"] + titles if titles else ["(new)"])
        if st.button("New note"):
            add_note("Untitled", "")
            st.experimental_rerun()
        if selected != "(new)":
            sel_id = int(selected.split(":")[0])
            if st.button("Delete selected"):
                delete_note(sel_id)
                st.success("Deleted")
                st.experimental_rerun()
    with right:
        if selected == "(new)":
            st.write("Create a new note on the left, then edit here.")
        else:
            sel_id = int(selected.split(":")[0])
            note = get_note(sel_id)
            title = st.text_input("Title", value=note["title"] or "")
            body = st.text_area("Body (Markdown)", value=note["body_md"] or "", height=250)
            if st.button("Save note"):
                update_note(sel_id, title, body)
                st.success("Saved")

# ---- Weather Tab ----
with tabs[3]:
    st.subheader("Weather")
    if st.button("Fetch weather for city"):
        geo = geocode_city(city)
        if not geo:
            st.error("City not found")
        else:
            data = get_forecast(geo["lat"], geo["lon"])
            current = data.get("current_weather", {})
            daily = data.get("daily", {})
            if current:
                st.metric("Current temp (°C)", current.get("temperature"))
                st.write(f"Wind {current.get('windspeed')} km/h")
            if daily:
                daily_df = pd.DataFrame({
                    "date": daily.get("time", []),
                    "t_max": daily.get("temperature_2m_max", []),
                    "t_min": daily.get("temperature_2m_min", []),
                    "precip_sum": daily.get("precipitation_sum", []),
                    "weathercode": daily.get("weathercode", []),
                })
                st.markdown("**7-day forecast**")
                st.dataframe(daily_df, use_container_width=True, hide_index=True)
            st.caption("Source: Open-Meteo")
