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
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PakWeather AI",
    page_icon="🇵🇰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# BACKEND URL
# ============================================================

BACKEND_URL = "https://pakweather-ai-production.up.railway.app"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
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
    '<div class="subtitle">AI-powered Pakistan weather forecasting dashboard</div>',
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

        56: ("🌦️", "Freezing drizzle"),

        57: ("🌧️", "Heavy freezing drizzle"),

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

        86: ("🌨️", "Heavy snow showers"),

        95: ("⛈️", "Thunderstorm"),

        96: ("⛈️", "Thunderstorm with hail"),

        99: ("⛈️", "Thunderstorm with heavy hail")

    }

    try:
        return descriptions.get(
            int(code),
            ("🌡️", "Weather information")
        )
    except:
        return ("🌡️", "Weather information")


# ============================================================
# API FUNCTIONS
# ============================================================

@st.cache_data(ttl=600)
def search_cities(query):

    url = f"{BACKEND_URL}/cities"

    params = {
        "query": query
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# GET SINGLE DATE FORECAST
# ============================================================

@st.cache_data(ttl=600)
def get_forecast(
    latitude,
    longitude,
    forecast_date
):

    url = f"{BACKEND_URL}/forecast"

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "forecast_date": str(forecast_date)

    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# GET 16 DAY FORECAST
# ============================================================

@st.cache_data(ttl=600)
def get_16_day_forecast(
    latitude,
    longitude
):

    url = f"{BACKEND_URL}/weather"

    params = {

        "latitude": latitude,

        "longitude": longitude

    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ PakWeather AI")

    try:

        health = requests.get(
            f"{BACKEND_URL}/health",
            timeout=10
        )

        if health.status_code == 200:

            st.success(
                "🟢 Forecast Service Online"
            )

        else:

            st.warning(
                "🟡 Backend response issue"
            )

    except:

        st.error(
            "🔴 Backend Offline"
        )

    st.divider()

    st.markdown(
        """
        **Features**

        🔎 Smart City Search

        🇵🇰 Pakistani Cities

        📅 16-Day Forecast

        🌡️ Temperature

        🌡️ Feels Like Temperature

        🌧️ Rain Probability

        💨 Wind Forecast

        🧭 Wind Direction

        📈 Interactive Charts

        🗺️ Location Map
        """
    )

    st.divider()

    st.caption(
        "Weather data by Open-Meteo"
    )

    st.caption(
        "Backend: FastAPI + Railway"
    )


# ============================================================
# CITY SEARCH
# ============================================================

st.header("🔎 Search Pakistani City")

st.write(
    "Start typing a Pakistani city name to see matching suggestions."
)

city_query = st.text_input(
    "Search City",
    placeholder="e.g. Multan, Lahore, Karachi, Islamabad...",
    label_visibility="collapsed"
)


# ============================================================
# CITY SEARCH
# ============================================================

if city_query.strip():

    if len(city_query.strip()) < 2:

        st.info(
            "⌨️ Type at least 2 letters."
        )

        st.stop()

    try:

        with st.spinner(
            "🔎 Searching Pakistani cities..."
        ):

            city_data = search_cities(
                city_query.strip()
            )

        locations = city_data.get(
            "cities",
            []
        )

    except requests.exceptions.RequestException as e:

        st.error(
            f"❌ City search failed: {e}"
        )

        st.stop()

    except Exception as e:

        st.error(
            f"❌ Unexpected error: {e}"
        )

        st.stop()


    # ========================================================
    # CITY SUGGESTIONS
    # ========================================================

    if not locations:

        st.warning(
            "⚠️ No Pakistani city found. Try another name."
        )

        st.stop()


    st.subheader(
        "📍 Matching Pakistani Cities"
    )


    city_labels = []


    for city in locations:

        name = city.get(
            "name",
            "Unknown"
        )

        province = city.get(
            "province",
            ""
        )

        label = name

        if province:

            label += f", {province}"

        label += ", Pakistan"

        city_labels.append(label)


    selected_index = st.selectbox(

        "Select City",

        range(len(city_labels)),

        format_func=lambda i:
            f"📍 {city_labels[i]}"

    )


    selected_city = locations[
        selected_index
    ]


    # ========================================================
    # CITY INFORMATION
    # ========================================================

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

    elevation = selected_city.get(
        "elevation"
    )


    st.success(
        f"📍 **{city_name}, {province}, Pakistan**"
    )


    # ========================================================
    # LOCATION DETAILS
    # ========================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Latitude",
            f"{latitude:.4f}°"
        )


    with col2:

        st.metric(
            "Longitude",
            f"{longitude:.4f}°"
        )


    with col3:

        if elevation is not None:

            st.metric(
                "Elevation",
                f"{float(elevation):.0f} m"
            )

        else:

            st.metric(
                "Elevation",
                "N/A"
            )


    # ========================================================
    # MAP
    # ========================================================

    st.subheader(
        "🗺️ City Location"
    )


    map_data = pd.DataFrame({

        "lat": [latitude],

        "lon": [longitude]

    })


    st.map(
        map_data,
        latitude="lat",
        longitude="lon",
        zoom=8
    )


    # ========================================================
    # DATE SELECTOR
    # ========================================================

    st.divider()

    st.header(
        "📅 Select Forecast Date"
    )


    today = date.today()

    maximum_date = (
        today + timedelta(days=15)
    )


    selected_date = st.date_input(

        "Forecast date",

        value=today,

        min_value=today,

        max_value=maximum_date

    )


    # ========================================================
    # LOAD FORECAST
    # ========================================================

    try:

        with st.spinner(
            "🌦️ Loading weather forecast..."
        ):

            forecast = get_forecast(

                latitude,

                longitude,

                selected_date

            )


    except requests.exceptions.HTTPError as e:

        st.error(
            f"❌ Forecast service error.\n\n{e}"
        )

        st.stop()


    except requests.exceptions.RequestException as e:

        st.error(
            f"❌ Could not connect to backend.\n\n{e}"
        )

        st.stop()


    except Exception as e:

        st.error(
            f"❌ Forecast error.\n\n{e}"
        )

        st.stop()


    # ========================================================
    # READ FORECAST DATA
    # ========================================================

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


    # ========================================================
    # FEELS LIKE
    #
    # IMPORTANT:
    # Backend returns:
    # apparent_temperature_min
    # apparent_temperature_max
    # ========================================================

    feels_like_min = forecast.get(
        "apparent_temperature_min"
    )


    feels_like_max = forecast.get(
        "apparent_temperature_max"
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


    wind_direction = forecast.get(
        "wind_direction"
    )


    # ========================================================
    # WEATHER DESCRIPTION
    # ========================================================

    icon, description = weather_description(
        weather_code
    )


    # ========================================================
    # WEATHER HEADER
    # ========================================================

    st.divider()

    st.header(
        f"{icon} Weather Forecast"
    )


    st.subheader(
        f"📍 {city_name}, {province}, Pakistan"
    )


    st.write(
        f"📅 **{selected_date.strftime('%A, %d %B %Y')}**"
    )


    # ========================================================
    # MAIN WEATHER CARDS
    # ========================================================

    c1, c2, c3, c4 = st.columns(4)


    with c1:

        if temp_avg is not None:

            st.metric(
                "🌡️ Average",
                f"{float(temp_avg):.1f} °C"
            )

        else:

            st.metric(
                "🌡️ Average",
                "N/A"
            )


    with c2:

        if temp_max is not None:

            st.metric(
                "🔺 Maximum",
                f"{float(temp_max):.1f} °C"
            )

        else:

            st.metric(
                "🔺 Maximum",
                "N/A"
            )


    with c3:

        if temp_min is not None:

            st.metric(
                "🔻 Minimum",
                f"{float(temp_min):.1f} °C"
            )

        else:

            st.metric(
                "🔻 Minimum",
                "N/A"
            )


    with c4:

        if rain_probability is not None:

            st.metric(
                "🌧️ Rain Chance",
                f"{float(rain_probability):.0f}%"
            )

        else:

            st.metric(
                "🌧️ Rain Chance",
                "N/A"
            )


    st.success(
        f"{icon} **{description}**"
    )


    # ========================================================
    # FEELS LIKE
    # ========================================================

    st.header(
        "🌡️ Feels Like"
    )


    f1, f2 = st.columns(2)


    with f1:

        if feels_like_min is not None:

            st.metric(
                "Minimum Feels Like",
                f"{float(feels_like_min):.1f} °C"
            )

        else:

            st.metric(
                "Minimum Feels Like",
                "N/A"
            )


    with f2:

        if feels_like_max is not None:

            st.metric(
                "Maximum Feels Like",
                f"{float(feels_like_max):.1f} °C"
            )

        else:

            st.metric(
                "Maximum Feels Like",
                "N/A"
            )


    # ========================================================
    # RAIN & WIND
    # ========================================================

    st.header(
        "🌧️ Rain & Wind"
    )


    r1, r2, r3 = st.columns(3)


    with r1:

        if precipitation is not None:

            st.metric(
                "Precipitation",
                f"{float(precipitation):.1f} mm"
            )

        else:

            st.metric(
                "Precipitation",
                "N/A"
            )


    with r2:

        if rain is not None:

            st.metric(
                "Rain",
                f"{float(rain):.1f} mm"
            )

        else:

            st.metric(
                "Rain",
                "N/A"
            )


    with r3:

        if wind_speed is not None:

            st.metric(
                "Wind Speed",
                f"{float(wind_speed):.1f} km/h"
            )

        else:

            st.metric(
                "Wind Speed",
                "N/A"
            )


    # ========================================================
    # WIND DETAILS
    # ========================================================

    wind_col1, wind_col2 = st.columns(2)


    with wind_col1:

        if wind_gust is not None:

            st.info(
                f"💨 **Maximum Wind Gust:** "
                f"{float(wind_gust):.1f} km/h"
            )


    with wind_col2:

        if wind_direction is not None:

            st.info(
                f"🧭 **Wind Direction:** "
                f"{float(wind_direction):.0f}°"
            )


    # ========================================================
    # 16 DAY FORECAST
    # ========================================================

    st.divider()

    st.header(
        "📈 16-Day Temperature Forecast"
    )


    try:

        with st.spinner(
            "📊 Loading 16-day forecast..."
        ):

            forecast_16 = get_16_day_forecast(

                latitude,

                longitude

            )


        daily = forecast_16.get(
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


        # ====================================================
        # CHART
        # ====================================================

        fig = go.Figure()


        fig.add_trace(

            go.Scatter(

                x=dates,

                y=max_temps,

                mode="lines+markers",

                name="Maximum Temperature",

                hovertemplate=
                "%{x}<br>"
                "Max: %{y:.1f} °C"
                "<extra></extra>"

            )

        )


        fig.add_trace(

            go.Scatter(

                x=dates,

                y=min_temps,

                mode="lines+markers",

                name="Minimum Temperature",

                hovertemplate=
                "%{x}<br>"
                "Min: %{y:.1f} °C"
                "<extra></extra>"

            )

        )


        fig.add_trace(

            go.Scatter(

                x=dates,

                y=mean_temps,

                mode="lines+markers",

                name="Average Temperature",

                hovertemplate=
                "%{x}<br>"
                "Average: %{y:.1f} °C"
                "<extra></extra>"

            )

        )


        fig.update_layout(

            height=450,

            xaxis_title="Date",

            yaxis_title="Temperature (°C)",

            hovermode="x unified",

            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0
            )

        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # ====================================================
        # FORECAST TABLE
        # ====================================================

        st.subheader(
            "📋 Forecast Details"
        )


        table_data = pd.DataFrame({

            "Date": dates,

            "Min °C": min_temps,

            "Average °C": mean_temps,

            "Max °C": max_temps

        })


        table_data["Date"] = pd.to_datetime(
            table_data["Date"]
        ).dt.strftime(
            "%d %b %Y"
        )


        st.dataframe(

            table_data,

            use_container_width=True,

            hide_index=True

        )


    except Exception as e:

        st.warning(
            f"⚠️ 16-day forecast could not be loaded: {e}"
        )


# ============================================================
# INITIAL SCREEN
# ============================================================

else:

    st.info(
        "⌨️ Start typing a Pakistani city name above."
    )

    st.markdown(
        """
        ### 🇵🇰 Explore Pakistan Weather

        Search for cities such as:

        **Multan • Lahore • Karachi • Islamabad • "
        Peshawar • Quetta • Bahawalpur • Murree • Faisalabad**
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🇵🇰 PakWeather AI | Streamlit Frontend | "
    "FastAPI Backend on Railway | Weather data by Open-Meteo"
)
