import streamlit as st
import json
import os
from datetime import datetime
import re

st.title("🤖 Smart Reminder Bot (Bangla Date Parser)")

# Load or create reminders file
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

def extract_date(user_text):
    match = re.search(r'(\d+)\s*tarik', user_text)
    if match:
        try:
            day = int(match.group(1))
            now = datetime.now()
            task_date = datetime(now.year, now.month, day)
            return task_date.strftime("%Y-%m-%d")
        except:
            return None
    return None

def extract_time(user_text):
    match = re.search(r'(\d+)\s*tai', user_text)
    if match:
        return match.group(1) + " tai"
    return ""

def show_all():
    if not reminders:
        return "Kono task nei."
    lines = []
    for i, task in enumerate(reminders, start=1):
        lines.append(f"{i}. {task['text']} ({task['date']})")
    return "\n".join(lines)

def edit_task(index, new_text):
    date = extract_date(new_text)
    if not date:
        return "Tarik bujhte parini. Example: 25 tarik"
    reminders[index - 1] = {
        "text": new_text,
        "date": date
    }
    save_reminders()
    return f"Task {index} edit kora hoyeche."

def delete_task(index):
    if index < 1 or index > len(reminders):
        return "Invalid task number."
    removed = reminders.pop(index - 1)
    save_reminders()
    return f"Task delete kora holo: {removed['text']}"

def process_input(user_text):
    text = user_text.strip().lower()

    if text == "ajke ki ki ase ?":
        today = today_str()
        today_tasks = [f"{i+1}. {r['text']}" for i, r in enumerate(reminders) if r["date"] == today]
        return "Ajker task:\n" + "\n".join(today_tasks) if today_tasks else "Ajke kono task nei."

    if text.startswith("delete"):
        try:
            index = int(text.split()[1])
            return delete_task(index)
        except:
            return "Delete er jonno likho: delete [number]"

    if text.startswith("edit"):
        try:
            index = int(text.split()[1])
            st.session_state.editing_index = index
            st.session_state.editing_mode = True
            return f"Task {index} edit korte chaile notun task bolo:"
        except:
            return "Edit er jonno likho: edit [number]"

    if st.session_state.get("editing_mode", False):
        index = st.session_state.editing_index
        st.session_state.editing_mode = False
        return edit_task(index, user_text)

    # Attempt to add new task
    date = extract_date(user_text)
    if not date:
        return "Tarik bujhte parini. Example: 25 tarik a class ase"

    reminders.append({
        "text": user_text,
        "date": date
    })
    save_reminders()
    return f"Task mone rekhechi: {user_text}"

# UI Input
user_input = st.text_input("Tumi ki bolte chao?")

if user_input:
    response = process_input(user_input)
    st.markdown(f"**🤖 Bot:** {response}")
