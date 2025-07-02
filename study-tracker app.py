import streamlit as st
import datetime
import pandas as pd
import random
import json
import os
import base64
from pathlib import Path
from streamlit_option_menu import option_menu
from minimal_pomodoro import show_minimal_pomodoro

# --- Page Config ---
st.set_page_config(page_title="📘 Productivity Hub", page_icon="⏳", layout="centered")
with st.sidebar:
    st.markdown("## ☕ Productivity Hub")  # 👈 Makes the sidebar "real"
# --- Background Wallpaper (from local image) ---
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
        background-repeat: no-repeat;
        background-attachment: fixed;
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
        overflow-x: hidden;
    }}

    /* Transparent base layout */
    [data-testid="stAppViewContainer"],
    [data-testid="stToolbar"],
    [data-testid="stVerticalBlock"],
    .main, .block-container {{
        background: transparent !important;
        box-shadow: none !important;
    }}

    /* ✨ Translucent Sidebar with Blur */
    section[data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: inset 0 0 10px #ffffff20, 0 0 20px #ffffff40;
        border-right: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px 0 0 12px;
    }}

    /* Match inner items for clean look */
    section[data-testid="stSidebar"] * {{
        background-color: transparent !important;
        color: #ffffffcc !important;
    }}

    /* 🚫 Arrow / toggle removal (all cases) */
    header[data-testid="stHeader"],
    button[data-testid="collapsed-control"],
    div[data-testid="collapsed-control"],
    [data-testid*="collapsed-control"],
    [title*="sidebar"],
    [aria-label*="sidebar"],
    [data-testid*="toggle"],
    button[title="Toggle sidebar"],
    button[title="Close sidebar"],
    button[title="Open sidebar"] {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
        position: absolute !important;
        z-index: -9999 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar Navigation ---
with st.sidebar:
    section = option_menu(
        menu_title="📘 Menu",
        options=["✅ To-Do List", "📚 Study Tracker", "⏱️ Pomodoro Timer", "📈 Reports", "💬 Motivation"],
        icons=["check2-square", "book", "hourglass-split", "bar-chart", "chat-left-dots"],
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "inherit", "font-size": "20px"},
            "nav-link": {
                "color": "inherit", "font-size": "18px", "text-align": "left", "padding": "10px 12px",
                "--hover-color": "rgba(255,255,255,0.05)"
            },
            "nav-link-selected": {"background-color": "#1a1a1a"},
        }
    )

# --- File Paths ---
DATA_FILE = "study_log.csv"
TODO_FILE = "todo_data.json"

# --- Helper Functions ---
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

# --- Sections ---
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
        "Don't watch the clock; do what it does. Keep going. – Sam Levenson",
        "Discipline is choosing between what you want now and what you want most. – Abraham Lincoln",
        "You don’t have to be great to start, but you have to start to be great. – Zig Ziglar"
    ]
    st.markdown(f"🎯 *{random.choice(quotes)}*")
