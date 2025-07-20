import streamlit as st

def require_login():
    if "user" not in st.session_state:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "ansh.k96" and password == "ina1234":
                st.session_state["user"] = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect username or password")
                st.stop()
        st.stop()  # This ensures the rest of the app doesn't run until logged in