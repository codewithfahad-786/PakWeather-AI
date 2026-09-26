import streamlit as st
import requests, json, os
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="PakWeather AI", page_icon="🇵🇰", layout="wide")

# --- Load Local Cities ---
CITIES_FILE = os.path.join(os.path.dirname(__file__), "pak_cities.json")
with open(CITIES_FILE, "r", encoding="utf-8") as f:
    LOCAL_CITIES = json.load(f)

# --- Helper: Search Any City in Pakistan ---
def search_any_pak_city(query):
    query = query.lower()
    # 1. Pehle local file me search
    local_result = [c for c in LOCAL_CITIES if query in c["name"].lower()]

    # 2. Agar local me na mile to Online Geocoding API se search (Poore Pakistan ki)
    if len(local_result) < 5 and len(query) >= 2:
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=10&language=en&format=json&countryCode=PK"
            r = requests.get(geo_url, timeout=5).json()
            if r.get("results"):
                for g in r["results"]:
                    # Duplicate check
                    if not any(c["name"].lower() == g["name"].lower() for c in local_result):
                        local_result.append({
                            "name": g["name"],
                            "province": g.get("admin1", "Pakistan"),
                            "country": "Pakistan",
                            "lat": g["latitude"],
                            "lon": g["longitude"]
                        })
        except:
            pass
    return local_result[:10]

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=weathercode,temperature_2m_max,temperature_2m_min,temperature_2m_mean,apparent_temperature_max,apparent_temperature_min,precipitation_sum,rain_sum,precipitation_probability_max,windspeed_10m_max,windgusts_10m_max,sunrise,sunset&hourly=temperature_2m,precipitation_probability,relativehumidity_2m,windspeed_10m&timezone=auto&forecast_days=16"
    return requests.get(url, timeout=10).json()

# --- UI ---
st.title("🇵🇰 PakWeather AI - Smart Weather")
st.markdown("Android App jaisa hi, ab Web par | Kisi bhi shehar ka naam likho")

# Search Box like Android App
col1, col2 = st.columns([3,1])
with col1:
    search_query = st.text_input("🔎 City Search Karo (e.g. Mirpur Khas, Karachi, Umerkot, Digri...)", value="Mirpur Khas", placeholder="City name likho...")
with col2:
    st.write("")
    search_btn = st.button("Search", use_container_width=True)

if search_query:
    results = search_any_pak_city(search_query)

    if not results:
        st.error(f"'{search_query}' naam ka koi shehar Pakistan me nahi mila.")
    else:
        # Agar 1 se zyada results hain to selectbox dikhao
        city_options = {f"{c['name']} - {c['province']}": c for c in results}
        selected_label = st.selectbox(f"📍 {len(results)} Cities mili, select karo:", list(city_options.keys()))
        city = city_options[selected_label]

        lat, lon = city["lat"], city["lon"]

        with st.spinner(f"{city['name']} ka mausam load ho raha hai..."):
            data = get_weather(lat, lon)

        current = data.get("current_weather", {})
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})

        # --- Top Metrics like Android App ---
        st.divider()
        st.subheader(f"📍 {city['name']}, {city.get('province','Pakistan')}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🌡️ Current Temp", f"{current.get('temperature','--')}°C", f"Feels {daily.get('apparent_temperature_max',[0])[0] if daily.get('apparent_temperature_max') else '--'}°C")
        m2.metric("💨 Wind Speed", f"{current.get('windspeed','--')} km/h")
        m3.metric("🌧️ Rain Today", f"{daily.get('rain_sum',[0])[0] if daily.get('rain_sum') else 0} mm")
        m4.metric("💧 Rain Chance", f"{daily.get('precipitation_probability_max',[0])[0] if daily.get('precipitation_probability_max') else 0}%")

        # --- Hourly Chart ---
        c1, c2 = st.columns([2,1])
        with c1:
            st.subheader("⏰ 24 Ghante ka Forecast")
            if hourly.get("time"):
                df_hourly = pd.DataFrame({
                    "Time": pd.to_datetime(hourly["time"][:24]),
                    "Temp (°C)": hourly["temperature_2m"][:24],
                    "Rain %": hourly["precipitation_probability"][:24]
                })
                fig = px.line(df_hourly, x="Time", y="Temp (°C)", markers=True, title="Aaj ka Temperature Graph")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_hourly, use_container_width=True, hide_index=True)

        with c2:
            st.subheader("🗺️ Location Map")
            st.map(pd.DataFrame([{"lat": lat, "lon": lon}]), zoom=7)
            st.write(f"**Latitude:** {lat}")
            st.write(f"**Longitude:** {lon}")
            st.write(f"**Sunrise:** {daily.get('sunrise',['--'])[0][11:] if daily.get('sunrise') else '--'}")
            st.write(f"**Sunset:** {daily.get('sunset',['--'])[0][11:] if daily.get('sunset') else '--'}")

        # --- 16 Days Forecast like Android App ---
        st.divider()
        st.subheader("📅 16 Din ka Forecast (Android App Jaisa)")

        if daily.get("time"):
            cols = st.columns(4)
            for i in range(len(daily["time"])):
                with cols[i % 4]:
                    with st.container(border=True):
                        st.write(f"**{daily['time'][i]}**")
                        st.write(f"🔺 {daily['temperature_2m_max'][i]}°C | 🔻 {daily['temperature_2m_min'][i]}°C")
                        st.write(f"Avg: {daily['temperature_2m_mean'][i]}°C")
                        st.write(f"🌧️ {daily['rain_sum'][i]}mm ({daily['precipitation_probability_max'][i]}%)")
                        st.write(f"💨 {daily['windspeed_10m_max'][i]} km/h")

st.sidebar.success("Android App direct API use karti hai, Web App bhi same API use karti hai. Dono alag alag chalengi.")
