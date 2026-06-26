import pandas as pd
import plotly.express as px
import streamlit as st
import api_client as api

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

if not st.session_state.get("access_token"):
    st.warning("Pehle login karo (Home page se).")
    st.stop()

st.title("📊 Analytics")

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
selected_id = st.selectbox(
    "Habit chuno", options=list(habit_names.keys()), format_func=lambda x: habit_names[x]
)

try:
    checkins = api.get_checkins(selected_id)
except api.APIError as e:
    st.error(e.message)
    st.stop()

if not checkins:
    st.info("Is habit ke liye abhi koi check-in nahi hai.")
else:
    df = pd.DataFrame(checkins)
    df["done_on"] = pd.to_datetime(df["done_on"])
    df = df.sort_values("done_on")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total check-ins", len(df))
    col2.metric("Average mood", round(df["mood"].mean(), 2))
    col3.metric("Best mood day", df.loc[df["mood"].idxmax(), "done_on"].strftime("%d %b"))

    fig = px.line(
        df, x="done_on", y="mood", markers=True,
        title=f"Mood trend — {habit_names[selected_id]}",
        labels={"done_on": "Date", "mood": "Mood (1-5)"},
    )
    fig.update_yaxes(range=[0.5, 5.5], dtick=1)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📝 Notes log")
    notes_df = df[df["note"].notna()][["done_on", "mood", "note"]]
    if notes_df.empty:
        st.caption("Koi notes nahi likhi gayi abhi tak.")
    else:
        st.dataframe(notes_df, use_container_width=True, hide_index=True)