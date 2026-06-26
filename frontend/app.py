import streamlit as st
import api_client as api

st.set_page_config(page_title="Habit Tracker", page_icon="✅", layout="wide")

# ---------- Session defaults ----------
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user" not in st.session_state:
    st.session_state.user = None


def show_logged_in_view():
    st.success(f"Logged in as **{st.session_state.user['email']}**")
    st.write("👈 Sidebar se **Dashboard** ya **Analytics** page open karo.")
    if st.button("Logout"):
        st.session_state.access_token = None
        st.session_state.user = None
        st.rerun()


def show_auth_forms():
    st.title("✅ Habit + Mood Tracker")
    st.caption("Apne habits track karo, mood ke saath. Pehle login/register karo.")

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if not email or not password:
                st.warning("Email aur password dono daalo")
            else:
                try:
                    data = api.login(email, password)
                    st.session_state.access_token = data["access_token"]
                    st.session_state.user = data["user"]
                    st.rerun()
                except api.APIError as e:
                    st.error(e.message)

    with tab_register:
        with st.form("register_form"):
            email = st.text_input("Email", key="reg_email")
            password = st.text_input(
                "Password (kam se kam 6 characters)", type="password", key="reg_password"
            )
            confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
            submitted = st.form_submit_button("Account banao", use_container_width=True)

        if submitted:
            if not email or not password:
                st.warning("Email aur password dono daalo")
            elif password != confirm:
                st.warning("Password match nahi ho rahe")
            else:
                try:
                    data = api.register(email, password)
                    st.session_state.access_token = data["access_token"]
                    st.session_state.user = data["user"]
                    st.success("Account ban gaya! Redirecting...")
                    st.rerun()
                except api.APIError as e:
                    st.error(e.message)
                    if e.details:
                        st.caption(str(e.details))


# ---------- Router ----------
if st.session_state.access_token:
    show_logged_in_view()
else:
    show_auth_forms()


def show_logged_in_view():
    user = st.session_state.user
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"Logged in as **{user['email']}**")
        st.write("👈 Sidebar se Dashboard, Analytics, Insights ya Leaderboard kholo.")
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.user = None
            st.rerun()

    # ---- XP / Level bar ----
    try:
        me = api.get_me()
        level = me["level"]
        xp = me["xp"]
        xp_needed = me["xp_for_next_level"]
        st.subheader(f"🏅 Level {level}")
        progress = min(xp / xp_needed, 1.0) if xp_needed else 1.0
        st.progress(progress, text=f"{xp} / {xp_needed} XP")
    except api.APIError:
        pass