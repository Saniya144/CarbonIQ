import streamlit as st
import requests
import pandas as pd
from io import StringIO 

BACKEND_URL = st.secrets["API_BASE"]

st.title("⚙️ Settings & Data Management")

st.markdown("#### Upload Transactions")
uploaded_file = st.file_uploader("Upload a CSV of transactions", type=["csv"])

# if uploaded_file:
#     files = {"file": uploaded_file.getvalue()}
#     resp = requests.post(f"{BACKEND_URL}/upload", files={"file": (uploaded_file.name, uploaded_file, "text/csv")})
#     if resp.status_code == 200:
#         st.success("File uploaded successfully!")
#     else:
#         st.error(f"Upload failed: {resp.text}")


if uploaded_file is not None:
    st.success("✅ File uploaded successfully!")

    # Step 1: Preview raw data
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Raw Uploaded Data")
    st.dataframe(df)

    # Step 2: Ask user whether to auto-categorize
    if st.button("🔍 Auto-Categorize Using AI"):
        with st.spinner("Categorizing transactions using AI..."):
            # Send file to backend /ml/categorize
            files = {"file": ("transactions.csv", uploaded_file.getvalue(), "text/csv")}
            response = requests.post(f"{BACKEND_URL}/ml/categorize", files=files)

            if response.status_code == 200:
                data = response.json()
                df_pred = pd.DataFrame(data)

                st.success("✅ Categorization complete!")
                st.subheader("🤖 AI-Predicted Categories")
                st.dataframe(df_pred)

                # Step 3: Allow user to review/edit predictions
                st.info("You can review and edit the predicted categories below before uploading.")
                edited_df = st.data_editor(df_pred, num_rows="dynamic")

                # Step 4: Upload finalized data to backend
                if st.button("⬆️ Upload to CarbonIQ for Emission Calculation"):
                    # Convert edited dataframe to CSV and send to /upload
                    csv_buffer = StringIO()
                    edited_df.to_csv(csv_buffer, index=False)
                    files = {"file": ("transactions_final.csv", csv_buffer.getvalue(), "text/csv")}

                    upload_response = requests.post(f"{BACKEND_URL}/upload", files=files)
                    if upload_response.status_code == 200:
                        st.success("✅ Data uploaded successfully and emissions calculated!")
                    else:
                        st.error("Upload failed. Please check backend logs.")
            else:
                st.error("❌ Categorization failed. Check backend or model logs.")



st.markdown("---")
st.markdown("#### Admin Tools")

if st.button("🗑️ Clear Database"):
    resp = requests.delete(f"{BACKEND_URL}/admin/reset")
    if resp.status_code == 200:
        st.success("Database cleared successfully!")
    else:
        st.error("Error clearing database.")