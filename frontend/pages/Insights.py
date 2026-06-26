import streamlit as st
import api_client as api

st.set_page_config(page_title="Insights", page_icon="🧠", layout="wide")

if not st.session_state.get("access_token"):
    st.warning("Pehle login karo (Home page se).")
    st.stop()

st.title("🧠 Smart Insights")
st.caption("Tumhare check-in patterns se auto-generated insights.")

try:
    result = api.list_habits(per_page=100)
    habits = result["items"]
except api.APIError as e:
    st.error(e.message)
    st.stop()

if not habits:
    st.info("Pehle Dashboard se kuch habits add karo.")
    st.stop()

habit_names = {h["id"]: h["name"] for h in habits}
selected_id = st.selectbox("Habit chuno", options=list(habit_names.keys()), format_func=lambda x: habit_names[x])

try:
    data = api.get_insights(selected_id)
    for insight in data["insights"]:
        st.info(insight)

    if "consistency_pct" in data:
        st.metric("Overall Consistency", f"{data['consistency_pct']}%")
except api.APIError as e:
    st.error(e.message)