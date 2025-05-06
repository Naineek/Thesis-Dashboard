import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
from streamlit_folium import st_folium
import folium
from datetime import timedelta

# ========== PAGE CONFIGURATION ==========
st.set_page_config(page_title="Urban Traffic Prediction & Monitoring Dashboard", layout="wide")

# ========== SIDEBAR ==========
with st.sidebar:
    import streamlit_autorefresh
    streamlit_autorefresh.st_autorefresh(interval=1000, key="clock_refresh")
    st.markdown("### ⏰ Current Time")
    st.write(datetime.datetime.now().strftime("%A, %d %B %Y\n%I:%M:%S %p"))

    st.title("Control Panel")
    st.markdown("### 📍 Location & Direction")
    selected_location = st.selectbox("Select Location", [
        "Aristocrat Hotel", 
        "Street no. 240/144 Intersection near Novotel", 
        "Near Biswa Bangla Gate"
    ])
    
    selected_direction = st.radio("Select Direction", ["Airport Bound", "Kolkata Bound"])
    selected_mode = st.selectbox("Select Vehicle Type", ['Car', '2 Wheeler', 'Bus', 'Truck', 'Bicycle', 'Pedestrian', 'Auto', 'Others'])

    # Special Event Option
    st.markdown("### 📅 Day Type")
    day_type = st.radio("Select Traffic Day Type", ['Normal Day', 'Holiday/Festival', 'Special Event'])
    
    st.markdown("### 🟢 System Status")
    st.write(f"Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write("Predictions refresh every 5 minutes.")

    st.markdown("## Emergency Alert")
    alert_level = st.selectbox("Set Alert Level", ["None", "Medium", "High", "Critical"])

    st.markdown("## 📢 Feedback")
    with st.form("feedback_form"):
        feedback = st.text_area("Submit Feedback/Issues (Only for Civic Use)", "")
        submitted = st.form_submit_button("Submit")
        if submitted and feedback.strip():
            st.success("✅ Feedback submitted. Thank you!")

# ========== HEADER ==========
st.markdown("""
    <h1 style='text-align: center; color: crimson; font-family: Georgia;'>🚦 Urban Traffic Prediction & Monitoring Dashboard</h1>
    <h4 style='text-align: center; font-style: italic;'>Developed by: <strong>Naineek Chandra</strong></h4>
    <h5 style='text-align: center;'>Institution: <strong>Indian Institute of Engineering Science and Technology, Shibpur (IIEST)</strong></h5>
    <h6 style='text-align: center;'>Supervisors: Dr. Tuhin Subhra Maparu and Dr. Krishanu Santra</strong></h6>
    <p style='text-align: center;'>This dashboard provides short-term traffic predictions based on historical and real time data and helps in sending immediate responses to the police during emergencies.</p>
    <p style='text-align: center; font-size: small;'>&copy; 2025 All rights reserved</p>
""", unsafe_allow_html=True)

# ========== SIMULATED DATA ==========
def simulate_traffic_data(day_type):
    vehicle_types = ['Car', '2 Wheeler', 'Bus', 'Truck', 'Bicycle', 'Pedestrian', 'Auto', 'Others']
    timestamp = pd.date_range(end=pd.Timestamp.now(), periods=24 * 6, freq='5min')
    multiplier = {"Normal Day": 1, "Holiday/Festival": 0.6, "Special Event": 1.4}[day_type]
    data = {'Time': timestamp}
    for vt in vehicle_types:
        base = np.random.randint(50, 150)
        data[vt] = (base + np.random.randint(-10, 15, size=len(timestamp))) * multiplier
    df = pd.DataFrame(data)
    return df

traffic_df = simulate_traffic_data(day_type)
traffic_df['Time_30min'] = traffic_df['Time'].dt.floor('30min')

# ========== EMERGENCY ALERT ==========
st.markdown("---")
if alert_level != "None":
    if alert_level == "Medium":
        st.markdown(f"<div style='color: brown; font-size: 20px;'>🚨 EMERGENCY LEVEL: {alert_level.upper()}</div>", unsafe_allow_html=True)
        st.markdown("**Action Required**: Notify police and adjust signal timing as needed.")
    elif alert_level == "High":
        st.markdown(f"<div style='color: orange; font-size: 20px;'>🚨 EMERGENCY LEVEL: {alert_level.upper()}</div>", unsafe_allow_html=True)
        st.markdown("**Action Required**: Immediate traffic management intervention needed to reduce congestion in critical areas.")
    elif alert_level == "Critical":
        st.markdown(f"<div style='color: red; font-size: 20px;'>🚨 EMERGENCY LEVEL: {alert_level.upper()}</div>", unsafe_allow_html=True)
        st.markdown("**Action Required**: Urgent intervention required. Police and emergency services must be notified immediately.")
else:
    st.success("✅ Traffic is under control. No emergency action required.")

# ========== FORECAST ==========
def generate_forecast_intervals(start_time, intervals):
    return [(start_time + timedelta(minutes=i), start_time + timedelta(minutes=i + 5)) for i in intervals]

now = datetime.datetime.now()
forecast_intervals = generate_forecast_intervals(now, [5, 15, 30, 60, 120])
forecast_times = [f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}" for start, end in forecast_intervals]

# Manual refresh
if st.sidebar.button("🔄 Refresh Predictions"):
    st.experimental_rerun()

# PCU Calculation
pcu_factors = {"Car": 1.0, "2 Wheeler": 0.5, "Bus": 2.5, "Truck": 3.0,
               "Bicycle": 0.4, "Pedestrian": 0.2, "Auto": 1.2, "Others": 3.5}

def get_los(pcu):
    if pcu <= 1440: return "A"
    elif pcu <= 2880: return "B"
    elif pcu <= 4320: return "C"
    elif pcu <= 5760: return "D"
    elif pcu <= 7200: return "E"
    else: return "F"

# ========= Create Forecast Rows =========
forecast_counts = {
    "Car": np.random.randint(15, 65, 5),
    "2 Wheeler": np.random.randint(12, 50, 5),
    "Bus": np.random.randint(5, 22, 5),
    "Truck": np.random.randint(1, 5, 5),
    "Bicycle": np.random.randint(2, 14, 5),
    "Pedestrian": np.random.randint(3, 15, 5),
    "Auto": np.random.randint(5, 20, 5),
    "Others": np.random.randint(2, 10, 5)
}

df_modes = pd.DataFrame({
    "Forecasted Time": forecast_times,
    "Duration": ["5 min", "15 min", "30 min", "1 hour", "2 hour"],
    **forecast_counts
})

# ===== Add Present (Now) Row =====
latest_row = traffic_df.iloc[-1]
end_time = latest_row["Time"]
start_time = end_time - pd.Timedelta(minutes=5)
current_time = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"

vehicle_types = list(pcu_factors.keys())

present_values = df_modes.iloc[0][vehicle_types]
present_values = (present_values * np.random.uniform(0.85, 1.15)).astype(int)

now_row = {
    "Forecasted Time": f"{current_time}<br><b>Present Count</b>",
    "Duration": "Last <br> 5 min",
    **present_values.to_dict()
}
now_row["Total PCU"] = int(sum(now_row[vt] * pcu_factors[vt] for vt in vehicle_types) * 20)
los_value = get_los(now_row["Total PCU"])
now_row["Predicted LOS"] = f"{los_value}<br><b>Present LOS</b>"

# Compute PCU and LOS for forecasts
df_modes["Total PCU"] = (sum(df_modes[vt] * pcu_factors[vt] for vt in vehicle_types) * 20).astype(int)
df_modes["Predicted LOS"] = df_modes["Total PCU"].apply(get_los)

# Insert Now row at the top
df_modes = pd.concat([pd.DataFrame([now_row]), df_modes], ignore_index=True)

# === LOS Colour Scale ===
los_colors = {
    "A": "#d4edda",  # Green
    "B": "#cce5ff",  # Blue
    "C": "#fff3cd",  # Yellow
    "D": "#ffeeba",  # Orange
    "E": "#f8d7da",  # Pink
    "F": "#f5c6cb"   # Red
}

def highlight_los(val):
    color = los_colors.get(val, "#ffffff")
    return f'background-color: {color}'

def highlight_now_row(row):
    forecast_time = str(row["Forecasted Time"])
    if "Present Count" in forecast_time:
        return ['background-color: #e0f7fa'] * len(row)
    else:
        return [''] * len(row)

columns_to_show = [
    "Duration", "Car", "2 Wheeler", "Bus", "Truck",
    "Bicycle", "Pedestrian", "Auto", "Others", "Total PCU", "Predicted LOS"
]
styled_df = df_modes[["Forecasted Time"] + columns_to_show].style\
    .applymap(highlight_los, subset=["Predicted LOS"])\
    .apply(highlight_now_row, axis=1)\
    .set_properties(**{'text-align': 'center'})\
    .set_table_styles(
        [{'selector': 'td, th', 'props': [('border', '1px solid #ccc'), ('padding', '4px')]}],
        overwrite=False
    )

st.markdown("##  🕒 Short Term Prediction of all Modes (Auto-Updated every 5 minutes)")
columns_to_show = [
    "Duration", "Car", "2 Wheeler", "Bus", "Truck",
    "Bicycle", "Pedestrian", "Auto", "Others", "Total PCU", "Predicted LOS"
]
st.markdown(
    """
    <style>
        thead th { text-align: center !important; }
        td, th {
            border: 1px solid #ccc !important;
            padding: 4px !important;
            text-align: center !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

# === LOS Legend ===
los_legend_html = "<b>LOS Colour Scale:</b> - " + ' '.join([
    f'<span style="background-color:{color}; padding:3px 8px; margin-right:5px; border-radius:4px;">LOS {k}</span>'
    for k, color in los_colors.items()
])
st.markdown(f"<div style='margin-top: 10px;'>{los_legend_html}</div>", unsafe_allow_html=True)

# ========== ACTIONABLE INSIGHTS ==========
st.markdown("---")
st.markdown("## 📊 Recommended Actions")

# Simulate real-time LOS (replace with your model's output)
predicted_los = "E"

if predicted_los in ["E", "F"]:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Dynamic Signal Control")
        st.markdown("- Adjust timings on **Street 144** and **Street 240** junction signal")
        st.markdown("- Mode: `Auto` or `Manual Override`")

        st.markdown("### ✅ Public Transport Notification")
        st.markdown("- Alert **WBTC Fleets** (Routes: `S30`, `AC12`)")
        st.markdown("- Delay warning sent")

        st.markdown("### ✅ Public Advisory")
        if st.button("📝 Generate Advisory"):
            st.code(
                "Traffic Alert: Heavy congestion near Biswa Bangla Gate from 5:30–6:15 PM. Use alternate routes via Street 280."
            )

    with col2:
        st.markdown("### ✅ Suggested Diversions")
        if st.button("🗺️ View Diversion Map"):
            st.map()  # Replace with your actual map

        st.markdown("### ✅ Enforcement Boost")
        st.markdown("- Activate `ANPR` cameras")
        st.markdown("- Priority: **Techno India Stretch**")

else:
    st.success("✅ Traffic is stable. No immediate action required.")

# ========== SUMMARY ==========
st.markdown("---")
st.markdown("## 🔍 Traffic Summary")
col1, col2, col3 = st.columns(3)

peak_vehicle = traffic_df.iloc[:, 1:-1].sum().idxmax()
col1.metric("🚗 Peak Vehicle", peak_vehicle)

# Peak time now displayed in 5-minute intervals (e.g., "1:05 - 1:10")
peak_time_idx = traffic_df.loc[traffic_df.iloc[:, 1:-1].sum(axis=1).idxmax(), 'Time']
col2.metric("🕒 Peak Time", f"{peak_time_idx.strftime('%I:%M')} - {peak_time_idx + timedelta(minutes=5):%I:%M}")

# Total volume for the 5-minute period at peak time
total_volume_peak = int(traffic_df.loc[traffic_df['Time'] == peak_time_idx].iloc[:, 1:-1].sum().sum())
col3.metric("📊 Total Volume (5 mins)", total_volume_peak)

# ========== VEHICLE MODE SHARE ==========
st.markdown("### 🚙 Vehicle Mode Share")
mode_total = traffic_df.iloc[:, 1:-1].sum()
fig_pie = px.pie(names=mode_total.index, values=mode_total.values, title="Vehicle Distribution")
st.plotly_chart(fig_pie, use_container_width=True)

# ========== LINE PLOT ==========
st.markdown(f"### 📈 Actual vs Predicted Volume for **{selected_mode}**")
traffic_df['Predicted'] = traffic_df[selected_mode] * (1 + np.random.uniform(-0.05, 0.05, size=len(traffic_df)))
fig_line = px.line(traffic_df, x='Time', y=[selected_mode, 'Predicted'],
                   labels={'value': 'Vehicle Count'}, title=f'{selected_mode} - Actual vs Predicted')
st.plotly_chart(fig_line, use_container_width=True)

# ========== HEATMAP ==========
st.markdown("### 🔥 Congestion Pattern Heatmap")
heatmap_df = traffic_df.set_index('Time').iloc[:, :-2].T
fig_heat = px.imshow(heatmap_df, aspect='auto', color_continuous_scale='Viridis')
st.plotly_chart(fig_heat, use_container_width=True)

# ========== INTERACTIVE MAP ==========
st.markdown("---")
st.markdown("### 🗺️ Interactive Traffic Map (Newtown)")
m = folium.Map(location=[22.5818, 88.4819], zoom_start=14)
congestion_data = [
    (22.5818, 88.4819, "Heavy", "#FF0000"),
    (22.5850, 88.4880, "Medium", "#FFA500"),
    (22.5790, 88.4750, "Low", "#00FF00")
]
for lat, lon, severity, color in congestion_data:
    folium.CircleMarker(
        location=[lat, lon],
        radius=20,
        popup=f"{severity} Congestion",
        color=color,
        fill=True,
        fill_opacity=0.6
    ).add_to(m)
with st.container():
    st.markdown(
        """
        <style>
        .folium-map {
            margin-bottom: -50px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st_folium(m, width=700, height=400)

# ========== WEATHER CONDITIONS ==========
st.markdown("---")
st.markdown("## 🌦️ Weather Conditions")

weather_conditions = ["Sunny", "Partly Cloudy", "Rainy", "Thunderstorm", "Foggy"]
temperatures = np.round(np.random.uniform(24, 36), 1)
humidity = np.random.randint(40, 90)
wind_speed = np.round(np.random.uniform(5, 20), 1)
selected_weather = np.random.choice(weather_conditions)

weather_icon = {
    "Sunny": "☀️",
    "Partly Cloudy": "⛅",
    "Rainy": "🌧️",
    "Thunderstorm": "⛈️",
    "Foggy": "🌫️"
}[selected_weather]

col_weather1, col_weather2, col_weather3, col_weather4 = st.columns(4)
col_weather1.metric("Condition", f"{weather_icon} {selected_weather}")
col_weather2.metric("Temperature (°C)", f"{temperatures}")
col_weather3.metric("Humidity (%)", f"{humidity}")
col_weather4.metric("Wind Speed (km/h)", f"{wind_speed}")

# ========== ENVIRONMENT ==========
st.markdown("---")
st.markdown("## 🌱 Environmental Impact")
col4, col5, col6 = st.columns(3)
col4.metric("CO₂ (g/km)", round(np.random.uniform(200, 500), 2))
col5.metric("Noise (dB)", round(np.random.uniform(65, 85), 1))
col6.metric("AQI", int(np.random.uniform(70, 150)))

# ========== INCIDENTS ==========
st.markdown("---")
st.markdown("## 🚧 Incident & Alert Log")
incident_data = {
    "Time": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M")],
    "Type": ["Accident"],
    "Location": ["MAR, Newtown"],
    "Severity": ["High"]
}
st.table(pd.DataFrame(incident_data))

with st.form("incident_form"):
    type_ = st.selectbox("Incident Type", ["Accident", "Breakdown", "Obstruction"])
    location = st.text_input("Location")
    severity = st.selectbox("Severity", ["Low", "Medium", "High"])
    submit_incident = st.form_submit_button("Report Incident")
    if submit_incident:
        st.success(f"✅ Incident reported at {location} - {type_} ({severity})")

# ========== HELP ==========
st.markdown("---")
st.markdown("## ❓ Help & Documentation")
st.info("""
- **Prediction Horizon:** 5 mins to 2 hour forecast of individual modes.
- **Vehicle Type Filter:** Focus on one mode (e.g., Bus, Pedestrian).
- **Day Type:** Adjust data for holidays, events.
- **Emergency Levels:** None → Medium → High → Critical.
- **Map:** Visual congestion intensity by zone.
- **Feedback:** Civic staff can report issues live.
""")

# ========== FOOTER ==========
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: small;'>📍 Developed for Civic and Government Stakeholders | Prototype Demo - Traffic Forecasting & Monitoring</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: small;'>&copy; 2025 All rights reserved</p>", unsafe_allow_html=True)
