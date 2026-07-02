import streamlit as st
import pandas as pd
import api_client as api

st.set_page_config(page_title="Leaderboard", page_icon="🏆", layout="wide")

if not st.session_state.get("access_token"):
    st.warning("Pehle login karo (Home page se).")
    st.stop()

st.title("🏆 Leaderboard")
st.caption("Top users by XP (email partially hidden for privacy).")

def generate_ranks(n):
    medals = ["🥇", "🥈", "🥉"]
    return [medals[i] if i < 3 else str(i + 1) for i in range(n)]

try:
    data = api.get_leaderboard()

    if not data:
        st.info("Abhi koi data nahi hai.")
        st.stop()

    df = pd.DataFrame(data)

    # SAFE rank generation (no mismatch possible)
    df.insert(0, "Rank", generate_ranks(len(df)))

    # Optional: email masking
    if "email" in df.columns:
        df["email"] = df["email"].apply(
            lambda x: x.split("@")[0][:3] + "***@" + x.split("@")[1]
            if "@" in x else x
        )

    st.dataframe(
        df[["Rank", "email", "level", "xp"]],
        use_container_width=True,
        hide_index=True,
    )

except api.APIError as e:
    st.error(e.message)
except Exception as e:
    st.error(str(e))