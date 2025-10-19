import streamlit as st
import requests

BACKEND_URL = st.secrets["API_BASE"]

st.title("💡 Carbon Insights")

try:
    response = requests.get(f"{BACKEND_URL}/analytics/insights")
    data = response.json()
    if "insights" in data:
        for i, insight in enumerate(data["insights"], 1):
            st.markdown(f"**{i}.** {insight}")
    else:
        st.info(data.get("message", "No insights available yet."))
except Exception as e:
    st.error(f"Error fetching insights: {e}")
