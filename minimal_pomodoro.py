import streamlit as st
import time

def show_minimal_pomodoro():
    st.title("🎯 Minimalist Focus Timer")

    # --- Task input ---
    task = st.text_input("🎯 What are you focusing on?")
    if task:
        st.markdown(f"🔎 **Focusing on:** _{task}_")

    # --- Session state setup ---
    if "mpomo_status" not in st.session_state:
        st.session_state.mpomo_status = "Stopped"
        st.session_state.mpomo_mode = "Work"
        st.session_state.mpomo_time_left = 25 * 60

    # --- Duration controls ---
    col1, col2, col3 = st.columns(3)
    with col1:
        work_time = st.selectbox("Work", [15, 20, 25, 30, 45, 60], index=2)
    with col2:
        break_short = st.selectbox("Short Break", [3, 5, 7, 10], index=1)
    with col3:
        break_long = st.selectbox("Long Break", [10, 15, 20], index=1)

    # --- Duration mapping ---
    durations = {
        "Work": work_time,
        "Short Break": break_short,
        "Long Break": break_long
    }

    # --- Auto-sync timer when stopped and durations change ---
    if st.session_state.mpomo_status == "Stopped":
        new_time = durations[st.session_state.mpomo_mode] * 60
        if st.session_state.mpomo_time_left != new_time:
            st.session_state.mpomo_time_left = new_time

    # --- Timer display ---
    st.markdown("---")
    st.subheader(f"🧠 Mode: {st.session_state.mpomo_mode}")

    def format_time(sec):
        m, s = divmod(sec, 60)
        return f"{m:02d}:{s:02d}"

    st.markdown(
        f"<h1 style='text-align:center; font-size:72px;'>{format_time(st.session_state.mpomo_time_left)}</h1>",
        unsafe_allow_html=True
    )

    # --- Play/Pause toggle ---
    center_col = st.columns(3)[1]
    with center_col:
        if st.session_state.mpomo_status == "Running":
            if st.button("⏸️"):
                st.session_state.mpomo_status = "Paused"
        else:
            if st.button("▶️"):
                st.session_state.mpomo_status = "Running"

    # --- Reset + Mode selection ---
    col_reset, col_mode = st.columns([1, 2])
    with col_reset:
        if st.button("🔁 Reset"):
            st.session_state.mpomo_status = "Stopped"
            st.session_state.mpomo_time_left = durations[st.session_state.mpomo_mode] * 60

    with col_mode:
        mode = st.radio("Mode", list(durations.keys()), horizontal=True,
                        index=list(durations.keys()).index(st.session_state.mpomo_mode))
        if mode != st.session_state.mpomo_mode:
            st.session_state.mpomo_mode = mode
            st.session_state.mpomo_status = "Stopped"
            st.session_state.mpomo_time_left = durations[mode] * 60

    # --- Countdown logic ---
    if st.session_state.mpomo_status == "Running":
        if st.session_state.mpomo_time_left > 0:
            time.sleep(1)
            st.session_state.mpomo_time_left -= 1
            st.rerun()
        else:
            st.session_state.mpomo_status = "Stopped"
            st.balloons()
            st.success("🎉 Time's up!")