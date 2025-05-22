import streamlit as st
import json
import os
from datetime import datetime, timedelta
import re
import csv

st.set_page_config(page_title="Smart Reminder Bot")
st.title("🤖 Smart Reminder Bot")

# Load or create reminders
if not os.path.exists("reminders.json"):
    with open("reminders.json", "w") as f:
        json.dump([], f)

with open("reminders.json", "r") as f:
    reminders = json.load(f)

def save_reminders():
    with open("reminders.json", "w") as f:
        json.dump(reminders, f, indent=2)

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def tomorrow_str():
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

def extract_date(text):
    match = re.search(r"(\d+)\s*tarik", text)
    if match:
        day = int(match.group(1))
        try:
            now = datetime.now()
            date = datetime(now.year, now.month, day)
            return date.strftime("%Y-%m-%d")
        except:
            return None
    return None

def extract_time(text):
    match = re.search(r"(\d{1,2})\s*tai", text)
    if match:
        hour = int(match.group(1))
        if 0 <= hour <= 23:
            return f"{hour:02d}:00"
    return ""

def process_input(user_text):
    text = user_text.strip().lower()

    if not text.startswith("mama"):
        return "Commands must start with **mama**."

    text = text[4:].strip()  # Remove "mama"

    if "ajke ki ki ase" in text:
        today = today_str()
        tasks = [r for r in sorted(reminders, key=lambda r: (r["date"], r["time"]))]
        today_tasks = [f"- {r['text']} ({r['time']})" for r in tasks if r["date"] == today]
        return "\n".join(today_tasks) if today_tasks else "Mama, ajker jonno kono task nai."

    if "kalke ki ki ase" in text:
        tomorrow = tomorrow_str()
        tasks = [r for r in sorted(reminders, key=lambda r: (r["date"], r["time"]))]
        tomorrow_tasks = [f"- {r['text']} ({r['time']})" for r in tasks if r["date"] == tomorrow]
        return "\n".join(tomorrow_tasks) if tomorrow_tasks else "Mama, kalker jonno kono task nai."

    if re.search(r"\d+\s*tarik.*ki ki ase", text):
        date = extract_date(text)
        if not date:
            return "Mama, bujhte parlam na koto tarik bolcho."
        tasks = [r for r in sorted(reminders, key=lambda r: (r["date"], r["time"]))]
        matched = [f"- {r['text']} ({r['time']})" for r in tasks if r["date"] == date]
        return "\n".join(matched) if matched else f"Mama, {date} tarike kono task nai."

    if text.startswith("delete "):
        try:
            index = int(text.split()[1]) - 1
            if 0 <= index < len(reminders):
                removed = reminders.pop(index)
                save_reminders()
                return f"Mama, delete korlam: {removed['text']}"
            else:
                return "Mama, invalid task number."
        except:
            return "Mama, likho: delete [number]"

    if text.startswith("edit "):
        try:
            index = int(text.split()[1]) - 1
            if 0 <= index < len(reminders):
                st.session_state.editing_index = index
                st.session_state.editing_mode = True
                return f"Mama, task {index+1} edit korte chaile notun version ta likho:"
            else:
                return "Mama, invalid task number."
        except:
            return "Mama, likho: edit [number]"

    if st.session_state.get("editing_mode", False):
        idx = st.session_state.editing_index
        date = extract_date(text)
        time = extract_time(text)
        if not date:
            return "Mama, tarik bujhte parlam na. Example: 25 tarik"
        reminders[idx] = {"text": text, "date": date, "time": time}
        save_reminders()
        st.session_state.editing_mode = False
        return f"Mama, update kore dilam: {text}"

    date = extract_date(text)
    time = extract_time(text)
    if date:
        reminders.append({"text": text, "date": date, "time": time})
        save_reminders()
        return f"Mama, save kore dilam: {text}"
    else:
        return "Mama, tarik thik moto dao. Example: 25 tarik"

# UI
user_input = st.text_input("💬 Bolo Mama...")

if user_input:
    response = process_input(user_input)
    st.markdown(f"**🤖 Mama Bot:** {response}")

# Show all tasks sorted by date+time
with st.expander("📋 Show all tasks (sorted by date & time)"):
    if reminders:
        sorted_reminders = sorted(reminders, key=lambda r: (r["date"], r["time"]))
        for i, task in enumerate(sorted_reminders, 1):
            st.write(f"{i}. {task['text']} ({task['date']} {task['time']})")
    else:
        st.write("Mama, ektao task nai ekhono.")

# Export buttons
st.markdown("### 📤 Export Tasks")
if reminders:
    # CSV
    csv_file = "tasks.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "date", "time"])
        writer.writeheader()
        for row in reminders:
            writer.writerow(row)
    with open(csv_file, "rb") as f:
        st.download_button("⬇️ Download as CSV", f, file_name="tasks.csv", mime="text/csv")

    # TXT
    txt_file = "tasks.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        for i, r in enumerate(sorted(reminders, key=lambda r: (r["date"], r["time"])), 1):
            f.write(f"{i}. {r['text']} ({r['date']} {r['time']})\n")
    with open(txt_file, "rb") as f:
        st.download_button("⬇️ Download as TXT", f, file_name="tasks.txt", mime="text/plain")
else:
    st.info("Mama, export korar moto kono task nai.")
