import streamlit as st
import json
import os
from datetime import datetime
import re

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

def process_input(user_text):
    text = user_text.strip().lower()

    # Show today’s tasks
    if text == "ajke ki ki ase ?":
        today = today_str()
        tasks = [f"{i+1}. {r['text']}" for i, r in enumerate(reminders) if r["date"] == today]
        return "\n".join(tasks) if tasks else "No tasks for today."

    # Delete a task
    if text.startswith("delete "):
        try:
            index = int(text.split()[1]) - 1
            if 0 <= index < len(reminders):
                removed = reminders.pop(index)
                save_reminders()
                return f"Deleted: {removed['text']}"
            else:
                return "Invalid task number."
        except:
            return "To delete, write: delete [number]"

    # Edit a task
    if text.startswith("edit "):
        try:
            index = int(text.split()[1]) - 1
            if 0 <= index < len(reminders):
                st.session_state.editing_index = index
                st.session_state.editing_mode = True
                return f"Please type the new version of task {index+1}:"
            else:
                return "Invalid task number."
        except:
            return "To edit, write: edit [number]"

    # Handle edit message
    if st.session_state.get("editing_mode", False):
        idx = st.session_state.editing_index
        date = extract_date(text)
        if not date:
            return "Couldn't understand the date. Example: 25 tarik"
        reminders[idx] = {"text": text, "date": date}
        save_reminders()
        st.session_state.editing_mode = False
        return f"Task updated: {text}"

    # Add new task
    date = extract_date(text)
    if date:
        reminders.append({"text": text, "date": date})
        save_reminders()
        return f"Task saved: {text}"
    else:
        return "Couldn't find the date. Example: 25 tarik"

# UI
user_input = st.text_input("💬 What do you want to say?")

if user_input:
    response = process_input(user_input)
    st.markdown(f"**🤖 Bot:** {response}")

# Show all tasks
with st.expander("📋 Show all tasks"):
    if reminders:
        for i, task in enumerate(reminders, 1):
            st.write(f"{i}. {task['text']} ({task['date']})")
    else:
        st.write("No tasks saved.")
