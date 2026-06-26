import streamlit as st
import pandas as pd
import api_client as api

st.set_page_config(page_title="Leaderboard", page_icon="🏆", layout="wide")

if not st.session_state.get("access_token"):
    st.warning("Pehle login karo (Home page se).")
    st.stop()

st.title("🏆 Leaderboard")
st.caption("Top 10 users by XP (email partially hidden for privacy).")

try:
    data = api.get_leaderboard()
    if not data:
        st.info("Abhi koi data nahi hai.")
    else:
        df = pd.DataFrame(data)
        df.index = df.index + 1
        df.insert(0, "Rank", ["🥇", "🥈", "🥉"] + [str(i) for i in range(4, len(df) + 1)])
        df = df.drop(columns=df.index.name, errors="ignore")
        st.dataframe(df[["Rank", "email", "level", "xp"]], use_container_width=True, hide_index=True)
except api.APIError as e:
    st.error(e.message)