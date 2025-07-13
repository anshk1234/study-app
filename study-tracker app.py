import streamlit as st
import datetime
import pandas as pd
import random
import json
import os
import base64
import time
from pathlib import Path
from streamlit_option_menu import option_menu
from minimal_pomodoro import show_minimal_pomodoro
from streamlit_lottie import st_lottie

# Page setup
st.set_page_config(page_title="📘 Productivity Hub", page_icon="⏳", layout="centered")

# Load local Lottie file
def load_lottiefile(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# Splash animation on first launch
if "show_intro" not in st.session_state:
    st.session_state.show_intro = True

if st.session_state.show_intro:
    lottie_intro = load_lottiefile("animation.json")
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<h1 style='text-align:center;'>Welcome to Productivity Hub!</h1>", unsafe_allow_html=True)
        st_lottie(lottie_intro, height=280, speed=1.2, loop=False)
        time.sleep(3)
    placeholder.empty()
    st.session_state.show_intro = False

# Background wallpaper
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image_path = Path("image.jpg")
if bg_image_path.exists():
    encoded_img = get_base64(bg_image_path)
    st.markdown(
        f"""
        <style>
        html, body, .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_img}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        [data-testid="stAppViewContainer"], .main, .block-container {{
            background: transparent !important;
        }}
        section[data-testid="stSidebar"] {{
            background-color: rgba(255,255,255,0.08) !important;
            backdrop-filter: blur(12px);
            border-radius: 12px 0 0 12px;
            border-right: 1px solid rgba(255,255,255,0.2);
        }}
        section[data-testid="stSidebar"] * {{
            color: #ffffffcc !important;
            background-color: transparent !important;
        }}
        button[title="Toggle sidebar"] {{
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 9999;
            background-color: rgba(255,255,255,0.2);
            border: none;
            border-radius: 8px;
            padding: 6px 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Sidebar menu
with st.sidebar:
    section = option_menu(
        menu_title="📘 Menu",
        options=["✅ To-Do List", "📚 Study Tracker", "⏱️ Pomodoro Timer", "📈 Reports", "💬 Motivation"],
        icons=["check2-square", "book", "hourglass-split", "bar-chart", "chat-left-dots"],
        default_index=0
    )

# File paths
DATA_FILE = "study_log.csv"
TODO_FILE = "todo_data.json"

# Helper functions
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["date", "task", "hours"])
        df.to_csv(DATA_FILE, index=False)
        return df

def save_study_entry(date, task, hours):
    df = load_data()
    new = pd.DataFrame([{"date": date, "task": task, "hours": hours}])
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as file:
            return json.load(file)
    return []

def save_todos(todos):
    with open(TODO_FILE, "w") as file:
        json.dump(todos, file)

# Main sections
if section == "✅ To-Do List":
    st.title("✅ To-Do List")
    if "todos" not in st.session_state:
        st.session_state.todos = load_todos()

    new_task = st.text_input("Add a new task")
    if st.button("➕ Add Task") and new_task.strip():
        st.session_state.todos.append({"task": new_task.strip(), "done": False})
        save_todos(st.session_state.todos)

    for i, item in enumerate(st.session_state.todos):
        cols = st.columns([0.05, 0.8, 0.15])
        checked = cols[0].checkbox("", value=item["done"], key=f"todo_{i}")
        cols[1].markdown(f"{'~~' if checked else ''}{item['task']}{'~~' if checked else ''}")
        if cols[2].button("🗑️", key=f"del_{i}"):
            st.session_state.todos.pop(i)
            save_todos(st.session_state.todos)
            st.rerun()
        else:
            item["done"] = checked
    save_todos(st.session_state.todos)

elif section == "📚 Study Tracker":
    st.title("📚 Log Study Hours")
    today = datetime.date.today()
    task = st.text_input("Subject/Topic Studied")
    hours = st.slider("Hours Studied", 0.0, 12.0, 1.0, 0.25)

    if st.button("📝 Log Study"):
        if task.strip():
            save_study_entry(today, task.strip(), hours)
            st.success(f"✅ Logged: {task} for {hours} hour(s)")
        else:
            st.warning("Please enter a study topic.")

    st.subheader("📄 Today's Study Log")
    df = load_data()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    today_logs = df[df["date"] == today]

    if not today_logs.empty:
        st.table(today_logs[["task", "hours"]].sort_values(by="hours", ascending=False))
    else:
        st.info("No logs for today yet.")

elif section == "⏱️ Pomodoro Timer":
    show_minimal_pomodoro()

elif section == "📈 Reports":
    st.title("📈 Study Reports")
    view = st.radio("View by:", ["Daily", "Weekly", "Monthly"], horizontal=True)
    df = load_data()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    today = datetime.date.today()

    if view == "Daily":
        data = df[df["date"] == today]
    elif view == "Weekly":
        data = df[df["date"] >= (today - datetime.timedelta(days=6))]
    else:
        data = df[df["date"] >= (today - datetime.timedelta(days=30))]

    if not data.empty:
        chart = data.groupby("task")["hours"].sum().reset_index()
        st.bar_chart(chart.set_index("task"))
        st.dataframe(data.sort_values(by="date", ascending=False))
    else:
        st.warning("No data found for this period.")

elif section == "💬 Motivation":
    st.title("💬 Daily Motivation")
    quotes = [
        "Believe you can and you're halfway there. – Theodore Roosevelt",
        "Success is the sum of small efforts repeated daily. – James Clear",
        "Discipline is choosing between what you want now and what you want most. – Abraham Lincoln",
        "Don’t watch the clock; do what it does. Keep going. – Sam Levenson",
        "You don’t have to be great to start, but you have to start to be great. – Zig Ziglar"
    ]
    st.markdown(f"🎯 *{random.choice(quotes)}*")
