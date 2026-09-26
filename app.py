import streamlit as st
import requests, json, os

st.set_page_config(page_title="PakWeather AI", page_icon="🇵🇰", layout="centered")

CITIES_FILE = os.path.join(os.path.dirname(__file__), "pak_cities.json")
with open(CITIES_FILE, "r", encoding="utf-8") as f:
    PAK_CITIES = json.load(f)

st.title("🇵🇰 PakWeather AI")
st.caption("Pakistan's Smart Weather - Real Time | Mirpur Khas Supported")

city_names = [c["name"] for c in PAK_CITIES]
selected = st.selectbox("🔎 City Search", city_names, index=4)

city = next((c for c in PAK_CITIES if c["name"] == selected), None)

if city:
    lat, lon = city["lat"], city["lon"]
    st.subheader(f"📍 {city['name']}, {city['province']}")

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=weathercode,temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,rain_sum,precipitation_probability_max,windspeed_10m_max,sunrise,sunset&hourly=temperature_2m,precipitation_probability&timezone=auto&forecast_days=16"

    data = requests.get(url).json()
    curr = data.get("current_weather", {})
    daily = data.get("daily", {})

    c1, c2, c3 = st.columns(3)
    c1.metric("🌡️ Live Temp", f"{curr.get('temperature', '--')}°C")
    c2.metric("💨 Wind", f"{curr.get('windspeed', '--')} km/h")
    c3.metric("⏰ Time", curr.get('time', '')[11:16])

    st.divider()
    st.write("**📅 16 Days Forecast**")
    for i in range(len(daily.get("time", []))):
        st.write(f"**{daily['time'][i]}**: {daily['temperature_2m_min'][i]}°C - {daily['temperature_2m_max'][i]}°C | Rain {daily['precipitation_probability_max'][i]}% | Wind {daily['windspeed_10m_max'][i]} km/h")
