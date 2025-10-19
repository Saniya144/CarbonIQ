import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

BACKEND_URL = st.secrets["API_BASE"]

st.title("📊 Emission Dashboard")

st.subheader("📊 Emissions Summary")

try:
    res = requests.get(f"{BACKEND_URL}/emissions/summary")
    if res.status_code == 200:
        summary_data = res.json()

        if not summary_data:
            st.warning("No emission data found. Please upload a file first.")
        else:
            # Flatten nested scope/category data
            flat_data = []
            for scope, cats in summary_data.items():
                for category, value in cats.items():
                    flat_data.append({"Scope": scope, "Category": category, "Emissions (kgCO₂e)": value})

            df_summary = pd.DataFrame(flat_data)

            view_mode = st.radio(
                "View Mode:",
                ["By Scope", "By Category"],
                horizontal=True,
            )

            if view_mode == "By Scope":
                # Aggregate by Scope
                df_view = df_summary.groupby("Scope", as_index=False)["Emissions (kgCO₂e)"].sum()

                fig = px.bar(
                    df_view,
                    x="Scope",
                    y="Emissions (kgCO₂e)",
                    color="Scope",
                    text_auto=True,
                    title="Total Emissions by Scope",
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.dataframe(df_view, use_container_width=True)
                st.plotly_chart(fig, use_container_width=True)

            else:  # By Category
                df_view = df_summary.groupby("Category", as_index=False)["Emissions (kgCO₂e)"].sum()

                fig = px.bar(
                    df_view,
                    x="Category",
                    y="Emissions (kgCO₂e)",
                    color="Category",
                    text_auto=True,
                    title="Total Emissions by Category",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.dataframe(df_view, use_container_width=True)
                st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Failed to retrieve summary from backend.")
except Exception as e:
    st.error(f"Error connecting to backend: {e}")

# -----------------------------
# Section 2: Detailed Transactions
# -----------------------------
st.divider()


st.subheader("🧾 Detailed Transactions")

try:
    res_tx = requests.get(f"{BACKEND_URL}/transactions")
    if res_tx.status_code == 200:
        df_tx = pd.DataFrame(res_tx.json())
        if not df_tx.empty:
            st.dataframe(df_tx, use_container_width=True)
        else:
            st.info("No transactions found yet.")
    else:
        st.error("Failed to retrieve transactions.")
except Exception as e:
    st.error(f"Error fetching transactions: {e}")
