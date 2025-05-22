import streamlit as st
import json
import os
from datetime import datetime, timedelta
import dateparser

st.title("🤖 Smart Reminder Bot")

# Load or create reminders
if not os.path.exists("reminders.json"):
    with open("reminders.json", "w") as f:
        json.dump([], f)

with open("reminders.json", "r") as f:
    reminders = json.load(f)

# Save reminders
def save_reminders():
    with open("reminders.json", "w") as f:
        json.dump(reminders, f, indent=2)

# Show all reminders
def show_all():
    if not reminders:
        return "Kono task nei."
    lines = []
    for i, task in enumerate(reminders, start=1):
        lines.append(f"{i}. {task['text']} ({task['date']})")
    return "\n".join(lines)

# Edit a reminder
def edit_task(index, new_text):
    if index < 1 or index > len(reminders):
        return "Invalid task number."
    parsed_date = dateparser.parse(new_text, languages=["bn", "en"])
    if not parsed_date:
        return "Date bujhte parini. Try again with a clear date."
    reminders[index - 1] = {
        "text": new_text,
        "date": parsed_date.strftime("%Y-%m-%d")
    }
    save_reminders()
    return f"Task {index} edit kora hoyeche."

# Delete a reminder
def delete_task(index):
    if index < 1 or index > len(reminders):
        return "Invalid task number."
    removed = reminders.pop(index - 1)
    save_reminders()
    return f"Task delete kora hoyeche: {removed['text']}"

# Process input
def process_input(user_text):
    global editing_mode, editing_index

    if user_text.lower().strip() == "shob task dekhao":
        return show_all()

    if user_text.lower().startswith("delete"):
        try:
            index = int(user_text.split()[1])
            return delete_task(index)
        except:
            return "Delete er jonno likho: delete [number]"

    if user_text.lower().startswith("edit"):
        try:
            index = int(user_text.split()[1])
            st.session_state.editing_index = index
            st.session_state.editing_mode = True
            return f"Type your new task for number {index}:"
        except:
            return "Edit er jonno likho: edit [number]"

    if st.session_state.get("editing_mode", False):
        index = st.session_state.editing_index
        st.session_state.editing_mode = False
        return edit_task(index, user_text)

    parsed_date = dateparser.parse(user_text, languages=['bn', 'en'])

    if "mone rakh" in user_text or "mone rakhis" in user_text:
        if parsed_date:
            reminders.append({
                "text": user_text,
                "date": parsed_date.strftime("%Y-%m-%d")
            })
            save_reminders()
            return f"Thik ache. Mone rekhechi: {user_text}"
        else:
            return "Tarik bujhte parini. '25 tarik', 'ajke', 'kalke' use koro."

    elif "ajke" in user_text:
        today = datetime.now().strftime("%Y-%m-%d")
        today_tasks = [r["text"] for r in reminders if r["date"] == today]
        return "Ajker kaj:\n" + "\n".join(today_tasks) if today_tasks else "Ajke kono kaj nei."

    elif "kalke" in user_text:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        tasks = [r["text"] for r in reminders if r["date"] == tomorrow]
        return "Kalker kaj:\n" + "\n".join(tasks) if tasks else "Kal kono kaj nei."

    return "Bujhte parlam na. Arktu clear kore bolo."

# Input UI
user_input = st.text_input("Tumi ki bolte chao?")

if user_input:
    answer = process_input(user_input)
    st.markdown(f"**🤖 Bot:** {answer}")
