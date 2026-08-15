# ============================================================
# 🇵🇰 PakWeather AI
# Professional Pakistan Weather Forecast Dashboard
# Streamlit Frontend + FastAPI Railway Backend
# ============================================================

import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta

# ============================================================
# CONFIG
# ============================================================

BACKEND_URL = "https://pakweather-ai-production.up.railway.app"

st.set_page_config(
    page_title="PakWeather AI",
    page_icon="🇵🇰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 44px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.75;
        margin-bottom: 25px;
    }

    .city-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 15px;
    }

    .small-text {
        font-size: 14px;
        opacity: 0.7;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🇵🇰 PakWeather AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered Pakistan weather forecasting dashboard'
    '</div>',
    unsafe_allow_html=True
)

# ============================================================
# WEATHER DESCRIPTION
# ============================================================

def weather_description(code):

    descriptions = {
        0: ("☀️", "Clear sky"),
        1: ("🌤️", "Mainly clear"),
        2: ("⛅", "Partly cloudy"),
        3: ("☁️", "Overcast"),

        45: ("🌫️", "Fog"),
        48: ("🌫️", "Rime fog"),

        51: ("🌦️", "Light drizzle"),
        53: ("🌦️", "Moderate drizzle"),
        55: ("🌧️", "Dense drizzle"),

        61: ("🌦️", "Slight rain"),
        63: ("🌧️", "Moderate rain"),
        65: ("🌧️", "Heavy rain"),

        71: ("🌨️", "Slight snowfall"),
        73: ("🌨️", "Moderate snowfall"),
        75: ("❄️", "Heavy snowfall"),

        80: ("🌦️", "Slight rain showers"),
        81: ("🌧️", "Moderate rain showers"),
        82: ("⛈️", "Violent rain showers"),

        95: ("⛈️", "Thunderstorm"),
        96: ("⛈️", "Thunderstorm with hail"),
        99: ("⛈️", "Thunderstorm with heavy hail")
    }

    return descriptions.get(
        int(code),
        ("🌡️", "Weather information")
    )

# ============================================================
# BACKEND HEALTH
# ============================================================

@st.cache_data(ttl=60)
def check_backend():

    try:

        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=10
        )

        if response.status_code == 200:
            return True

        return False

    except Exception:
        return False


# ============================================================
# CITY SEARCH
# ============================================================

@st.cache_data(ttl=3600)
def search_cities(query):

    try:

        response = requests.get(
            f"{BACKEND_URL}/cities",
            params={"query": query},
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        return data.get("cities", [])

    except Exception as e:

        st.error(
            f"❌ City search failed: {e}"
        )

        return []


# ============================================================
# SPECIFIC DATE FORECAST
# ============================================================

@st.cache_data(ttl=600)
def get_forecast(
    latitude,
    longitude,
    forecast_date
):

    try:

        response = requests.get(
            f"{BACKEND_URL}/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "forecast_date": str(forecast_date)
            },
            timeout=25
        )

        response.raise_for_status()

        return response.json()

    except requests.HTTPError as e:

        try:
            detail = response.json().get(
                "detail",
                str(e)
            )
        except Exception:
            detail = str(e)

        raise Exception(detail)

    except Exception as e:

        raise Exception(str(e))


# ============================================================
# FULL 16-DAY FORECAST
# ============================================================

@st.cache_data(ttl=600)
def get_full_forecast(
    latitude,
    longitude
):

    try:

        response = requests.get(
            f"{BACKEND_URL}/weather",
            params={
                "latitude": latitude,
                "longitude": longitude
            },
            timeout=25
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        raise Exception(str(e))


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ PakWeather AI")

    if check_backend():

        st.success(
            "🟢 Backend Online"
        )

    else:

        st.error(
            "🔴 Backend Offline"
        )

    st.divider()

    st.markdown(
        """
        ### Features

        🔎 Smart Pakistan City Search

        📍 Automatic Location Detection

        📅 16-Day Weather Forecast

        🌡️ Temperature Forecast

        🌧️ Rain Probability

        💨 Wind Forecast

        📈 Interactive Charts

        🗺️ Location Map

        ⚡ FastAPI Backend
        """
    )

    st.divider()

    st.caption(
        "Weather data powered by Open-Meteo"
    )


# ============================================================
# CITY SEARCH
# ============================================================

st.header("🔎 Search Pakistani City")

st.write(
    "Start typing a Pakistani city name to see matching suggestions."
)

city_query = st.text_input(
    "City Name",
    placeholder="Type: m, mu, mul, multan...",
    label_visibility="collapsed"
)

# ============================================================
# CITY SUGGESTIONS
# ============================================================

if city_query.strip():

    if len(city_query.strip()) < 2:

        st.info(
            "⌨️ Type at least 2 letters."
        )

    else:

        with st.spinner(
            "🔎 Searching Pakistani cities..."
        ):

            cities = search_cities(
                city_query.strip()
            )

        if cities:

            st.subheader(
                "📍 Matching Pakistani Cities"
            )

            # Remove duplicate city/province combinations
            unique_cities = []

            seen = set()

            for city in cities:

                key = (
                    city.get("name"),
                    city.get("province")
                )

                if key not in seen:

                    seen.add(key)
                    unique_cities.append(city)

            city_labels = []

            for city in unique_cities:

                name = city.get(
                    "name",
                    "Unknown"
                )

                province = city.get(
                    "province",
                    ""
                )

                if province:

                    label = (
                        f"📍 {name}, "
                        f"{province}, Pakistan"
                    )

                else:

                    label = (
                        f"📍 {name}, Pakistan"
                    )

                city_labels.append(label)

            selected_index = st.selectbox(
                "Select City",
                range(len(city_labels)),
                format_func=lambda i:
                    city_labels[i],
                key="selected_city"
            )

            selected_city = unique_cities[
                selected_index
            ]

            # ====================================================
            # CITY INFORMATION
            # ====================================================

            city_name = selected_city.get(
                "name",
                "Unknown"
            )

            province = selected_city.get(
                "province",
                ""
            )

            latitude = float(
                selected_city.get(
                    "latitude"
                )
            )

            longitude = float(
                selected_city.get(
                    "longitude"
                )
            )

            elevation = selected_city.get(
                "elevation"
            )

            timezone = selected_city.get(
                "timezone",
                "auto"
            )

            st.success(
                f"📍 **{city_name}, "
                f"{province}, Pakistan**"
            )

            # ====================================================
            # CITY DETAILS
            # ====================================================

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Latitude",
                f"{latitude:.4f}°"
            )

            c2.metric(
                "Longitude",
                f"{longitude:.4f}°"
            )

            if elevation is not None:

                c3.metric(
                    "Elevation",
                    f"{float(elevation):.0f} m"
                )

            else:

                c3.metric(
                    "Elevation",
                    "N/A"
                )

            # ====================================================
            # MAP
            # ====================================================

            st.subheader(
                "🗺️ City Location"
            )

            map_data = pd.DataFrame(
                {
                    "lat": [latitude],
                    "lon": [longitude]
                }
            )

            st.map(
                map_data,
                latitude="lat",
                longitude="lon",
                zoom=9
            )

            # ====================================================
            # DATE
            # ====================================================

            st.divider()

            st.header(
                "📅 Select Forecast Date"
            )

            today = date.today()

            selected_date = st.date_input(
                "Forecast date",
                value=today,
                min_value=today,
                max_value=(
                    today +
                    timedelta(days=15)
                )
            )

            # ====================================================
            # GET FORECAST
            # ====================================================

            if st.button(
                "🌦️ Check Weather",
                type="primary",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "🌦️ Getting latest weather forecast..."
                    ):

                        forecast = get_forecast(
                            latitude,
                            longitude,
                            selected_date
                        )

                    # =================================================
                    # FORECAST DATA
                    # =================================================

                    weather_code = forecast.get(
                        "weather_code"
                    )

                    temperature = forecast.get(
                        "temperature",
                        {}
                    )

                    temp_min = temperature.get(
                        "minimum"
                    )

                    temp_avg = temperature.get(
                        "average"
                    )

                    temp_max = temperature.get(
                        "maximum"
                    )

                    apparent_max = forecast.get(
                        "apparent_temperature_max"
                    )

                    apparent_min = forecast.get(
                        "apparent_temperature_min"
                    )

                    precipitation = forecast.get(
                        "precipitation_mm"
                    )

                    rain = forecast.get(
                        "rain_mm"
                    )

                    rain_probability = forecast.get(
                        "rain_probability"
                    )

                    wind_speed = forecast.get(
                        "wind_speed_kmh"
                    )

                    wind_gust = forecast.get(
                        "wind_gust_kmh"
                    )

                    icon, description = (
                        weather_description(
                            weather_code
                        )
                    )

                    # =================================================
                    # RESULT HEADER
                    # =================================================

                    st.divider()

                    st.header(
                        f"{icon} Weather Forecast"
                    )

                    st.markdown(
                        f"### 📍 {city_name}, "
                        f"{province}, Pakistan"
                    )

                    st.caption(
                        f"📅 {selected_date.strftime('%A, %d %B %Y')}"
                    )

                    # =================================================
                    # MAIN WEATHER CARDS
                    # =================================================

                    c1, c2, c3, c4 = st.columns(4)

                    c1.metric(
                        "🌡️ Average",
                        f"{temp_avg:.1f} °C"
                    )

                    c2.metric(
                        "🔺 Maximum",
                        f"{temp_max:.1f} °C"
                    )

                    c3.metric(
                        "🔻 Minimum",
                        f"{temp_min:.1f} °C"
                    )

                    c4.metric(
                        "🌧️ Rain Chance",
                        f"{rain_probability}%"
                    )

                    st.success(
                        f"{icon} **{description}**"
                    )

                    # =================================================
                    # FEELS LIKE
                    # =================================================

                    st.subheader(
                        "🌡️ Feels Like"
                    )

                    c1, c2 = st.columns(2)

                    c1.metric(
                        "Minimum Feels Like",
                        f"{apparent_min:.1f} °C"
                    )

                    c2.metric(
                        "Maximum Feels Like",
                        f"{apparent_max:.1f} °C"
                    )

                    # =================================================
                    # RAIN + WIND
                    # =================================================

                    st.subheader(
                        "🌧️ Rain & Wind"
                    )

                    c1, c2, c3 = st.columns(3)

                    c1.metric(
                        "Precipitation",
                        f"{precipitation:.1f} mm"
                    )

                    c2.metric(
                        "Rain",
                        f"{rain:.1f} mm"
                    )

                    c3.metric(
                        "Wind",
                        f"{wind_speed:.1f} km/h"
                    )

                    st.info(
                        f"💨 Maximum wind gust: "
                        f"**{wind_gust:.1f} km/h**"
                    )

                    # =================================================
                    # 16 DAY FORECAST
                    # =================================================

                    st.divider()

                    st.header(
                        "📈 16-Day Temperature Forecast"
                    )

                    with st.spinner(
                        "Loading extended forecast..."
                    ):

                        full_forecast = (
                            get_full_forecast(
                                latitude,
                                longitude
                            )
                        )

                    daily = full_forecast.get(
                        "daily",
                        {}
                    )

                    dates = daily.get(
                        "time",
                        []
                    )

                    max_temps = daily.get(
                        "temperature_2m_max",
                        []
                    )

                    min_temps = daily.get(
                        "temperature_2m_min",
                        []
                    )

                    mean_temps = daily.get(
                        "temperature_2m_mean",
                        []
                    )

                    if dates:

                        fig = go.Figure()

                        fig.add_trace(
                            go.Scatter(
                                x=dates,
                                y=max_temps,
                                mode="lines+markers",
                                name="Maximum"
                            )
                        )

                        fig.add_trace(
                            go.Scatter(
                                x=dates,
                                y=min_temps,
                                mode="lines+markers",
                                name="Minimum"
                            )
                        )

                        fig.add_trace(
                            go.Scatter(
                                x=dates,
                                y=mean_temps,
                                mode="lines+markers",
                                name="Average"
                            )
                        )

                        fig.update_layout(
                            height=450,
                            xaxis_title="Date",
                            yaxis_title="Temperature (°C)",
                            hovermode="x unified",
                            margin=dict(
                                l=20,
                                r=20,
                                t=40,
                                b=20
                            )
                        )

                        st.plotly_chart(
                            fig,
                            use_container_width=True
                        )

                    # =================================================
                    # FORECAST TABLE
                    # =================================================

                    st.subheader(
                        "📋 Forecast Details"
                    )

                    forecast_table = pd.DataFrame(
                        {
                            "Date": dates,
                            "Min °C": min_temps,
                            "Average °C": mean_temps,
                            "Max °C": max_temps
                        }
                    )

                    st.dataframe(
                        forecast_table,
                        use_container_width=True,
                        hide_index=True
                    )

                except Exception as e:

                    st.error(
                        "❌ Forecast service error."
                    )

                    st.code(
                        str(e)
                    )

        else:

            st.warning(
                "⚠️ No Pakistani city found. "
                "Try another spelling."
            )

else:

    st.info(
        "⌨️ Start typing a city name "
        "to see Pakistani city suggestions."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🇵🇰 PakWeather AI | "
    "Streamlit Frontend | "
    "FastAPI Backend on Railway | "
    "Weather data by Open-Meteo"
)
