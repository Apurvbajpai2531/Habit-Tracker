import streamlit as st
import api_client as api

st.set_page_config(page_title="Dashboard", page_icon="📋", layout="wide")

if not st.session_state.get("access_token"):
    st.warning("Pehle login karo (Home page se).")
    st.stop()

st.title("📋 Dashboard")

# ---------- Add new habit ----------
with st.sidebar:
    st.header("➕ Naya Habit")
    with st.form("new_habit_form", clear_on_submit=True):
        name = st.text_input("Habit ka naam")
        category = st.selectbox(
            "Category", ["general", "health", "study", "fitness", "mindfulness"]
        )
        submitted = st.form_submit_button("Add Habit", use_container_width=True)

    if submitted:
        if not name.strip():
            st.warning("Naam likho pehle")
        else:
            try:
                api.create_habit(name.strip(), category)
                st.success("Habit add ho gaya!")
                st.rerun()
            except api.APIError as e:
                st.error(e.message)

# ---------- List habits ----------
try:
    result = api.list_habits()
    habits = result["items"]
except api.APIError as e:
    st.error(e.message)
    st.stop()

if not habits:
    st.info("Abhi koi habit nahi hai. Sidebar se ek add karo.")
else:
    cols = st.columns(2)
    for idx, habit in enumerate(habits):
        with cols[idx % 2]:
            with st.container(border=True):
                top = st.columns([3, 1])
                top[0].subheader(habit["name"])
                top[0].caption(f"Category: {habit['category']}")
                if top[1].button("🗑️", key=f"del_{habit['id']}"):
                    try:
                        api.delete_habit(habit["id"])
                        st.rerun()
                    except api.APIError as e:
                        st.error(e.message)

                stat_cols = st.columns(2)
                stat_cols[0].metric("Total check-ins", habit.get("total_checkins", 0))
                avg_mood = habit.get("avg_mood")
                stat_cols[1].metric("Avg mood", avg_mood if avg_mood else "—")

                mood = st.slider(
                    "Aaj ka mood (1=bad, 5=great)", 1, 5, 3, key=f"mood_{habit['id']}"
                )
                note = st.text_input("Note (optional)", key=f"note_{habit['id']}")

if st.button("✅ Mark done today", key=f"checkin_{habit['id']}", use_container_width=True):
                    try:
                        result = api.checkin(habit["id"], mood, note or None)
                        if result.get("leveled_up"):
                            st.balloons()
                            st.success(f"🎉 Level Up! Ab tum Level {result['level']} ho!")
                        else:
                            st.success(f"Check-in saved! +{result.get('earned_xp', 0)} XP 🎯")
                        st.rerun()
                    except api.APIError as e:
                        st.error(e.message)