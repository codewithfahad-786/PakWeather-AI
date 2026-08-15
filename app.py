# ============================================================
# 🇵🇰 PakWeather AI
# Professional Pakistan Weather Forecast Dashboard
# Streamlit Frontend + Railway FastAPI Backend
# ============================================================

import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PakWeather AI",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "https://pakweather-ai-production.up.railway.app"

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 44px;
        font-weight: 800;
        margin-bottom: 2px;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.70;
        margin-bottom: 25px;
    }

    .status-box {
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 15px;
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
# BACKEND FUNCTIONS
# ============================================================

@st.cache_data(ttl=300)
def check_backend():

    try:

        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except Exception:

        return None


@st.cache_data(ttl=600)
def search_cities(query):

    try:

        response = requests.get(
            f"{BACKEND_URL}/cities",
            params={"query": query},
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return data

    except Exception as e:

        return {
            "error": str(e)
        }


@st.cache_data(ttl=600)
def get_forecast(latitude, longitude, elevation):

    try:

        response = requests.get(
            f"{BACKEND_URL}/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "elevation": elevation
            },
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        return {
            "error": str(e)
        }


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

        56: ("🌧️", "Freezing drizzle"),

        57: ("🌧️", "Dense freezing drizzle"),

        61: ("🌦️", "Slight rain"),

        63: ("🌧️", "Moderate rain"),

        65: ("🌧️", "Heavy rain"),

        66: ("🌧️", "Freezing rain"),

        67: ("🌧️", "Heavy freezing rain"),

        71: ("🌨️", "Slight snowfall"),

        73: ("🌨️", "Moderate snowfall"),

        75: ("❄️", "Heavy snowfall"),

        77: ("❄️", "Snow grains"),

        80: ("🌦️", "Slight rain showers"),

        81: ("🌧️", "Moderate rain showers"),

        82: ("⛈️", "Violent rain showers"),

        85: ("🌨️", "Slight snow showers"),

        86: ("❄️", "Heavy snow showers"),

        95: ("⛈️", "Thunderstorm"),

        96: ("⛈️", "Thunderstorm with hail"),

        99: ("⛈️", "Thunderstorm with heavy hail")

    }

    return descriptions.get(
        int(code),
        ("🌡️", "Weather information")
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ PakWeather AI")

    backend_status = check_backend()

    if backend_status:

        st.success("🟢 Backend Online")

    else:

        st.error("🔴 Backend Offline")

    st.divider()

    st.markdown(
        """
        ### Features

        🔎 Smart Pakistan City Search

        📅 16-Day Weather Forecast

        🌡️ Temperature Forecast

        🌧️ Rain Probability

        💨 Wind Forecast

        📈 Interactive Charts

        🗺️ Location Map

        🚂 Railway FastAPI Backend
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
    "Start typing a Pakistani city name to see suggestions."
)

city_query = st.text_input(
    "City name",
    placeholder="Type: m, mu, mul, kar, lah, isl...",
    label_visibility="collapsed"
)

# ============================================================
# CITY SEARCH LOGIC
# ============================================================

if city_query.strip():

    query = city_query.strip()

    if len(query) < 1:

        st.info(
            "⌨️ Type a city name."
        )

    else:

        with st.spinner("🔎 Finding Pakistani cities..."):

            city_response = search_cities(query)

        # Backend error

        if "error" in city_response:

            st.error(
                "❌ Unable to connect to city search service."
            )

            st.code(
                city_response["error"]
            )

        else:

            # ------------------------------------------------
            # HANDLE DIFFERENT API RESPONSE FORMATS
            # ------------------------------------------------

            if isinstance(city_response, dict):

                locations = (
                    city_response.get("cities")
                    or city_response.get("results")
                    or city_response.get("data")
                    or []
                )

            elif isinstance(city_response, list):

                locations = city_response

            else:

                locations = []

            # ------------------------------------------------
            # NO RESULTS
            # ------------------------------------------------

            if not locations:

                st.warning(
                    f"⚠️ No Pakistani city found for '{query}'."
                )

                st.info(
                    "Try: kar, lah, mul, isl, pes, que, mur..."
                )

            else:

                st.subheader(
                    "📍 City Suggestions"
                )

                # ------------------------------------------------
                # CREATE CITY LABELS
                # ------------------------------------------------

                city_labels = []

                for location in locations:

                    name = location.get(
                        "name",
                        "Unknown City"
                    )

                    province = location.get(
                        "province",
                        location.get(
                            "admin1",
                            ""
                        )
                    )

                    country = location.get(
                        "country",
                        "Pakistan"
                    )

                    if province:

                        label = (
                            f"{name} — "
                            f"{province}, "
                            f"{country}"
                        )

                    else:

                        label = (
                            f"{name}, "
                            f"{country}"
                        )

                    city_labels.append(label)

                # ------------------------------------------------
                # CITY SELECTOR
                # ------------------------------------------------

                selected_index = st.selectbox(
                    "Matching Pakistani Cities",
                    range(len(city_labels)),
                    format_func=lambda i: city_labels[i],
                    key="city_selector"
                )

                selected_city = locations[
                    selected_index
                ]

                # ------------------------------------------------
                # LOCATION DATA
                # ------------------------------------------------

                city_name = selected_city.get(
                    "name",
                    "Unknown City"
                )

                province = selected_city.get(
                    "province",
                    selected_city.get(
                        "admin1",
                        "Pakistan"
                    )
                )

                latitude = float(
                    selected_city.get(
                        "latitude",
                        0
                    )
                )

                longitude = float(
                    selected_city.get(
                        "longitude",
                        0
                    )
                )

                elevation = float(
                    selected_city.get(
                        "elevation",
                        0
                    )
                )

                # ------------------------------------------------
                # SELECTED CITY
                # ------------------------------------------------

                st.success(
                    f"📍 **{city_name}, "
                    f"{province}, Pakistan**"
                )

                # ------------------------------------------------
                # LOCATION INFORMATION
                # ------------------------------------------------

                info1, info2, info3 = st.columns(3)

                info1.metric(
                    "Latitude",
                    f"{latitude:.4f}°"
                )

                info2.metric(
                    "Longitude",
                    f"{longitude:.4f}°"
                )

                info3.metric(
                    "Elevation",
                    f"{elevation:.0f} m"
                )

                # ------------------------------------------------
                # MAP
                # ------------------------------------------------

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
                    zoom=8
                )

                # ====================================================
                # DATE SELECTION
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

                with st.spinner(
                    "🌦️ Loading weather forecast..."
                ):

                    forecast = get_forecast(
                        latitude,
                        longitude,
                        elevation
                    )

                # ------------------------------------------------
                # FORECAST ERROR
                # ------------------------------------------------

                if "error" in forecast:

                    st.error(
                        "❌ Forecast service error."
                    )

                    st.code(
                        forecast["error"]
                    )

                else:

                    # ====================================================
                    # EXTRACT FORECAST DATA
                    # ====================================================

                    daily = forecast.get(
                        "daily",
                        {}
                    )

                    dates = daily.get(
                        "time",
                        []
                    )

                    selected_date_string = str(
                        selected_date
                    )

                    if selected_date_string not in dates:

                        st.error(
                            "❌ Selected date is not available."
                        )

                    else:

                        index = dates.index(
                            selected_date_string
                        )

                        weather_code = daily.get(
                            "weather_code",
                            [0]
                        )[index]

                        temp_max = daily.get(
                            "temperature_2m_max",
                            [None]
                        )[index]

                        temp_min = daily.get(
                            "temperature_2m_min",
                            [None]
                        )[index]

                        temp_mean = daily.get(
                            "temperature_2m_mean",
                            [None]
                        )[index]

                        precipitation = daily.get(
                            "precipitation_sum",
                            [0]
                        )[index]

                        rain_probability = daily.get(
                            "precipitation_probability_max",
                            [0]
                        )[index]

                        wind_max = daily.get(
                            "wind_speed_10m_max",
                            [0]
                        )[index]

                        wind_gust = daily.get(
                            "wind_gusts_10m_max",
                            [0]
                        )[index]

                        wind_direction = daily.get(
                            "wind_direction_10m_dominant",
                            [0]
                        )[index]

                        sunrise = daily.get(
                            "sunrise",
                            ["N/A"]
                        )[index]

                        sunset = daily.get(
                            "sunset",
                            ["N/A"]
                        )

                        # ====================================================
                        # WEATHER DESCRIPTION
                        # ====================================================

                        icon, description = (
                            weather_description(
                                weather_code
                            )
                        )

                        # ====================================================
                        # WEATHER HEADER
                        # ====================================================

                        st.divider()

                        st.header(
                            f"{icon} Weather Forecast"
                        )

                        st.subheader(
                            f"{city_name}, Pakistan"
                        )

                        st.write(
                            f"📅 {selected_date}"
                        )

                        st.success(
                            f"{icon} **{description}**"
                        )

                        # ====================================================
                        # WEATHER METRICS
                        # ====================================================

                        c1, c2, c3, c4 = st.columns(4)

                        c1.metric(
                            "🌡️ Average",
                            f"{temp_mean:.1f} °C"
                            if temp_mean is not None
                            else "N/A"
                        )

                        c2.metric(
                            "🔺 Maximum",
                            f"{temp_max:.1f} °C"
                            if temp_max is not None
                            else "N/A"
                        )

                        c3.metric(
                            "🔻 Minimum",
                            f"{temp_min:.1f} °C"
                            if temp_min is not None
                            else "N/A"
                        )

                        c4.metric(
                            "☔ Rain Probability",
                            f"{rain_probability}%"
                            if rain_probability is not None
                            else "N/A"
                        )

                        # ====================================================
                        # ADDITIONAL WEATHER INFORMATION
                        # ====================================================

                        st.subheader(
                            "🌦️ Additional Information"
                        )

                        w1, w2, w3, w4 = st.columns(4)

                        w1.metric(
                            "🌧️ Precipitation",
                            f"{precipitation:.1f} mm"
                            if precipitation is not None
                            else "N/A"
                        )

                        w2.metric(
                            "💨 Max Wind",
                            f"{wind_max:.1f} km/h"
                            if wind_max is not None
                            else "N/A"
                        )

                        w3.metric(
                            "💨 Wind Gust",
                            f"{wind_gust:.1f} km/h"
                            if wind_gust is not None
                            else "N/A"
                        )

                        w4.metric(
                            "🧭 Wind Direction",
                            f"{wind_direction:.0f}°"
                            if wind_direction is not None
                            else "N/A"
                        )

                        # ====================================================
                        # SUNRISE / SUNSET
                        # ====================================================

                        s1, s2 = st.columns(2)

                        s1.metric(
                            "🌅 Sunrise",
                            str(sunrise)[11:16]
                        )

                        s2.metric(
                            "🌇 Sunset",
                            str(sunset)[11:16]
                        )

                        # ====================================================
                        # TEMPERATURE CHART
                        # ====================================================

                        st.divider()

                        st.header(
                            "📈 16-Day Temperature Forecast"
                        )

                        fig_temp = go.Figure()

                        fig_temp.add_trace(
                            go.Scatter(
                                x=daily["time"],
                                y=daily[
                                    "temperature_2m_max"
                                ],
                                mode="lines+markers",
                                name="Maximum Temperature"
                            )
                        )

                        fig_temp.add_trace(
                            go.Scatter(
                                x=daily["time"],
                                y=daily[
                                    "temperature_2m_min"
                                ],
                                mode="lines+markers",
                                name="Minimum Temperature"
                            )
                        )

                        fig_temp.add_trace(
                            go.Scatter(
                                x=daily["time"],
                                y=daily[
                                    "temperature_2m_mean"
                                ],
                                mode="lines+markers",
                                name="Average Temperature"
                            )
                        )

                        fig_temp.update_layout(
                            height=450,
                            xaxis_title="Date",
                            yaxis_title="Temperature (°C)",
                            hovermode="x unified"
                        )

                        st.plotly_chart(
                            fig_temp,
                            use_container_width=True
                        )

                        # ====================================================
                        # RAIN CHART
                        # ====================================================

                        st.header(
                            "🌧️ Rain Probability & Precipitation"
                        )

                        fig_rain = go.Figure()

                        fig_rain.add_trace(
                            go.Bar(
                                x=daily["time"],
                                y=daily[
                                    "precipitation_probability_max"
                                ],
                                name="Rain Probability (%)"
                            )
                        )

                        fig_rain.update_layout(
                            height=400,
                            xaxis_title="Date",
                            yaxis_title="Probability (%)",
                            hovermode="x unified"
                        )

                        st.plotly_chart(
                            fig_rain,
                            use_container_width=True
                        )

                        # ====================================================
                        # WIND CHART
                        # ====================================================

                        st.header(
                            "💨 Wind Forecast"
                        )

                        fig_wind = go.Figure()

                        fig_wind.add_trace(
                            go.Scatter(
                                x=daily["time"],
                                y=daily[
                                    "wind_speed_10m_max"
                                ],
                                mode="lines+markers",
                                name="Maximum Wind"
                            )
                        )

                        fig_wind.update_layout(
                            height=350,
                            xaxis_title="Date",
                            yaxis_title="Wind Speed (km/h)",
                            hovermode="x unified"
                        )

                        st.plotly_chart(
                            fig_wind,
                            use_container_width=True
                        )

                        # ====================================================
                        # FORECAST TABLE
                        # ====================================================

                        st.header(
                            "📋 Forecast Details"
                        )

                        forecast_table = pd.DataFrame(
                            {
                                "Date": daily["time"],
                                "Min °C": daily[
                                    "temperature_2m_min"
                                ],
                                "Avg °C": daily[
                                    "temperature_2m_mean"
                                ],
                                "Max °C": daily[
                                    "temperature_2m_max"
                                ],
                                "Rain %": daily[
                                    "precipitation_probability_max"
                                ],
                                "Rain mm": daily[
                                    "precipitation_sum"
                                ],
                                "Wind km/h": daily[
                                    "wind_speed_10m_max"
                                ]
                            }
                        )

                        st.dataframe(
                            forecast_table,
                            use_container_width=True,
                            hide_index=True
                        )

# ============================================================
# DEFAULT MESSAGE
# ============================================================

else:

    st.info(
        "⌨️ Start typing a Pakistani city name above "
        "to search for weather."
    )

    st.markdown(
        """
        ### 🌦️ How to use PakWeather AI

        **1️⃣ Search a city**

        Type any Pakistani city name.

        Example:

        `mul` → Multan

        `kar` → Karachi

        `lah` → Lahore

        `isl` → Islamabad

        `mur` → Murree

        **2️⃣ Select a city**

        Choose the matching city from suggestions.

        **3️⃣ Select a date**

        Select any available date in the forecast.

        **4️⃣ View weather**

        Get temperature, rain probability,
        wind, sunrise, sunset and interactive charts.
        """
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
