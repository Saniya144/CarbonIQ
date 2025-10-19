import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# -----------------------------
# Backend API URL
# -----------------------------
BACKEND_URL = st.secrets["API_BASE"]  # make sure FastAPI is running

# -----------------------------
# Streamlit Page Config
# -----------------------------
# st.set_page_config(page_title="CarbonIQ Dashboard", layout="wide")
# st.title("🌍 CarbonIQ Dashboard")

# st.sidebar.markdown("### 🧰 Admin Tools")
# if st.sidebar.button("Clear Database"):
#     resp = requests.delete(f"{BACKEND_URL}/admin/reset")
#     if resp.status_code == 200:
#         st.sidebar.success("Database cleared successfully!")


st.set_page_config(page_title="CarbonIQ Dashboard", page_icon="🌍", layout="wide")

st.title("🌍 CarbonIQ")
st.markdown("Welcome to your Carbon Accounting Dashboard!")

st.sidebar.success("Use the sidebar to navigate between pages.")





# -----------------------------
# Section 1: File Upload
# -----------------------------
# st.subheader("📂 Upload Transactions CSV")

# uploaded_file = st.file_uploader("Upload a CSV file with your transactions", type=["csv"])

# if uploaded_file:
#     try:
#         with st.spinner("Uploading to backend and processing..."):
#             files = {"file": uploaded_file.getvalue()}
#             res = requests.post(f"{BACKEND_URL}/upload", files={"file": uploaded_file})
#         if res.status_code == 200:
#             st.success("✅ File uploaded and processed successfully!")
#         else:
#             st.error(f"Upload failed: {res.text}")
#     except Exception as e:
#         st.error(f"Error connecting to backend: {e}")

# st.divider()

# -----------------------------
# Section 2: Emissions Summary
# -----------------------------
# st.subheader("📊 Emissions Summary")

# try:
#     res = requests.get(f"{BACKEND_URL}/emissions/summary")
#     if res.status_code == 200:
#         summary_data = res.json()

#         if not summary_data:
#             st.warning("No emission data found. Please upload a file first.")
#         else:
#             # Flatten nested scope/category data
#             flat_data = []
#             for scope, cats in summary_data.items():
#                 for category, value in cats.items():
#                     flat_data.append({"Scope": scope, "Category": category, "Emissions (kgCO₂e)": value})

#             df_summary = pd.DataFrame(flat_data)

#             view_mode = st.radio(
#                 "View Mode:",
#                 ["By Scope", "By Category"],
#                 horizontal=True,
#             )

#             if view_mode == "By Scope":
#                 # Aggregate by Scope
#                 df_view = df_summary.groupby("Scope", as_index=False)["Emissions (kgCO₂e)"].sum()

#                 fig = px.bar(
#                     df_view,
#                     x="Scope",
#                     y="Emissions (kgCO₂e)",
#                     color="Scope",
#                     text_auto=True,
#                     title="Total Emissions by Scope",
#                     color_discrete_sequence=px.colors.qualitative.Set2
#                 )
#                 st.dataframe(df_view, use_container_width=True)
#                 st.plotly_chart(fig, use_container_width=True)

#             else:  # By Category
#                 df_view = df_summary.groupby("Category", as_index=False)["Emissions (kgCO₂e)"].sum()

#                 fig = px.bar(
#                     df_view,
#                     x="Category",
#                     y="Emissions (kgCO₂e)",
#                     color="Category",
#                     text_auto=True,
#                     title="Total Emissions by Category",
#                     color_discrete_sequence=px.colors.qualitative.Pastel
#                 )
#                 st.dataframe(df_view, use_container_width=True)
#                 st.plotly_chart(fig, use_container_width=True)

#     else:
#         st.error("Failed to retrieve summary from backend.")
# except Exception as e:
#     st.error(f"Error connecting to backend: {e}")


# -----------------------------
# Section 3: Analytics - Emission Trends
# -----------------------------
# st.subheader("📈 Emission Trends Over Time")

# try:
#     res = requests.get(f"{BACKEND_URL}/analytics/trends")
#     if res.status_code == 200:
#         trend_data = res.json()
#         if trend_data:
#             df_trends = pd.DataFrame(trend_data)
#             st.dataframe(df_trends, use_container_width=True)

#             # Plot monthly emission trend
#             fig = px.line(
#                 df_trends,
#                 x="month",
#                 y="emissions",
#                 markers=True,
#                 title="Monthly Emission Trends",
#                 labels={"month": "Month", "emissions": "Emissions (kgCO₂e)"},
#                 line_shape="linear",
#                 color_discrete_sequence=["#4C9F70"]
#             )
#             fig.update_layout(yaxis=dict(showgrid=True, zeroline=True))
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.warning("No trend data available.")
#     else:
#         st.error("Failed to fetch analytics data.")
# except Exception as e:
#     st.error(f"Error connecting to backend: {e}")


# -----------------------------
# Section 4: Transactions Table
# -----------------------------
# st.subheader("🧾 Detailed Transactions")

# try:
#     res_tx = requests.get(f"{BACKEND_URL}/transactions")
#     if res_tx.status_code == 200:
#         df_tx = pd.DataFrame(res_tx.json())
#         if not df_tx.empty:
#             st.dataframe(df_tx, use_container_width=True)
#         else:
#             st.info("No transactions found yet.")
#     else:
#         st.error("Failed to retrieve transactions.")
# except Exception as e:
#     st.error(f"Error fetching transactions: {e}")


# -----------------------------
# Section 5: Analytics - Scope Breakdown and Emission Forecast
# -----------------------------
# st.markdown("## ♻️ Scope Breakdown")
# scope_data = requests.get(f"{BACKEND_URL}/analytics/scope_breakdown").json()
# df_scope = pd.DataFrame(list(scope_data.items()), columns=["Scope", "Emissions (kgCO2e)"])
# fig_scope = px.pie(df_scope, names="Scope", values="Emissions (kgCO2e)",
#                    color_discrete_sequence=px.colors.qualitative.Set2)
# st.plotly_chart(fig_scope)

# st.markdown("## 🔮 Emission Forecast (Next 3 Months)")
# forecast = requests.get(f"{BACKEND_URL}/analytics/forecast").json()
# df_forecast = pd.DataFrame(forecast)
# st.dataframe(df_forecast)

# if not df_forecast.empty:
#     fig_forecast = px.line(df_forecast, x="month", y="predicted_emissions",
#                            markers=True, title="Predicted Emissions (kgCO2e)")
#     st.plotly_chart(fig_forecast)
