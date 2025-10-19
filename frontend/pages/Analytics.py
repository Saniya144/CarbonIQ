import streamlit as st
import requests
import pandas as pd
import plotly.express as px

BACKEND_URL = st.secrets["API_BASE"]

st.title("📈 Analytics")

st.write("Backend health:", requests.get(f"{BACKEND_URL}/health").text)

st.subheader("📈 Emission Trends Over Time")

try:
    res = requests.get(f"{BACKEND_URL}/analytics/trends")
    if res.status_code == 200:
        trend_data = res.json()
        if trend_data:
            df_trends = pd.DataFrame(trend_data)
            st.dataframe(df_trends, use_container_width=True)

            # Plot monthly emission trend
            fig = px.line(
                df_trends,
                x="month",
                y="emissions",
                markers=True,
                title="Monthly Emission Trends",
                labels={"month": "Month", "emissions": "Emissions (kgCO₂e)"},
                line_shape="linear",
                color_discrete_sequence=["#4C9F70"]
            )
            fig.update_layout(yaxis=dict(showgrid=True, zeroline=True))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No trend data available.")
    else:
        st.error("Failed to fetch analytics data.")
except Exception as e:
    st.error(f"Error connecting to backend: {e}")

st.markdown("## ♻️ Scope Breakdown")
try:
    res = requests.get(f"{BACKEND_URL}/analytics/scope_breakdown")
    if res.status_code == 200:
        scope_data = res.json()
        if scope_data:
            df_scope = pd.DataFrame(list(scope_data.items()), columns=["Scope", "Emissions (kgCO2e)"])
            fig_scope = px.pie(df_scope, names="Scope", values="Emissions (kgCO2e)",
                               color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_scope)
        else:
            st.warning("No scope breakdown data available.")
    else:
        st.error("Failed to retrieve scope breakdown data.")
except Exception as e:
    st.error(f"Error connecting to backend: {e}")

st.markdown("## 🔮 Emission Forecast (Next 3 Months)")
try:
    res = requests.get(f"{BACKEND_URL}/analytics/forecast")
    if res.status_code == 200:
        forecast = res.json()
        if forecast:
            df_forecast = pd.DataFrame(forecast)
            st.dataframe(df_forecast)

            if not df_forecast.empty:
                fig_forecast = px.line(df_forecast, x="month", y="predicted_emissions",
                                       markers=True, title="Predicted Emissions (kgCO2e)")
                st.plotly_chart(fig_forecast)
        else:
            st.warning("No forecast data available.")
    else:
        st.error("Failed to retrieve forecast data.")
except Exception as e:
    st.error(f"Error connecting to backend: {e}")
