import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.title("⚙️ Settings & Data Management")

st.markdown("#### Upload Transactions")
uploaded_file = st.file_uploader("Upload a CSV of transactions", type=["csv"])
if uploaded_file:
    files = {"file": uploaded_file.getvalue()}
    resp = requests.post(f"{BACKEND_URL}/upload", files={"file": (uploaded_file.name, uploaded_file, "text/csv")})
    if resp.status_code == 200:
        st.success("File uploaded successfully!")
    else:
        st.error(f"Upload failed: {resp.text}")

st.markdown("---")
st.markdown("#### Admin Tools")

if st.button("🗑️ Clear Database"):
    resp = requests.delete(f"{BACKEND_URL}/admin/reset")
    if resp.status_code == 200:
        st.success("Database cleared successfully!")
    else:
        st.error("Error clearing database.")
