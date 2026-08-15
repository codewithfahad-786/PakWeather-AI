
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
# BACKEND CONFIGURATION
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
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 10px;
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
# HELPER FUNCTIONS
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
        56: ("🌧️", "Light freezing drizzle"),
        57: ("🌧️", "Dense freezing drizzle"),
        61: ("🌦️", "Slight rain"),
        63: ("🌧️", "Moderate rain"),
        65: ("🌧️", "Heavy rain"),
        66: ("🌧️", "Light freezing rain"),
        67: ("🌧️", "Heavy freezing rain"),
        71: ("🌨️", "Slight snow"),
        73: ("🌨️", "Moderate snow"),
        75: ("❄️", "Heavy snow"),
        77: ("🌨️", "Snow grains"),
        80: ("🌦️", "Slight rain showers"),
        81: ("🌧️", "Moderate rain showers"),
        82: ("⛈️", "Violent rain showers"),
        85: ("🌨️", "Slight snow showers"),
        86: ("❄️", "Heavy snow showers"),
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


def safe_number(value, decimals=1, suffix=""):

    if value is None:
        return "N/A"

    try:
        return f"{float(value):.{decimals}f}{suffix}"
    except:
        return "N/A"


# ============================================================
# BACKEND API FUNCTIONS
# ============================================================

@st.cache_data(ttl=300)
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


@st.cache_data(ttl=300)
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


@st.cache_data(ttl=300)
def get_16_day_weather(
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

    st.success("🟢 Backend Online")

    st.divider()

    st.markdown(
        """
        **Features**

        🔎 Smart Pakistan City Search

        📅 16-Day Forecast

        🌡️ Temperature

        🌡️ Feels Like Temperature

        🌧️ Rain Probability

        💨 Wind Forecast

        📈 Interactive Charts

        🗺️ Location Map

        🌅 Sunrise & Sunset
        """
    )

    st.divider()

    st.caption(
        "Frontend: Streamlit"
    )

    st.caption(
        "Backend: FastAPI + Railway"
    )

    st.caption(
        "Weather Data: Open-Meteo"
    )


# ============================================================
# CITY SEARCH
# ============================================================

st.header("🔎 Search Pakistani City")

st.write(
    "Start typing a Pakistani city name to see matching suggestions."
)

city_query = st.text_input(
    "City Search",
    placeholder="e.g. Multan, Karachi, Lahore, Islamabad...",
    label_visibility="collapsed"
)


# ============================================================
# CITY SEARCH RESULTS
# ============================================================

if city_query.strip():

    if len(city_query.strip()) < 1:

        st.info(
            "⌨️ Type a city name."
        )

    else:

        try:

            with st.spinner(
                "🔎 Searching Pakistani cities..."
            ):

                city_response = search_cities(
                    city_query.strip()
                )

            cities = city_response.get(
                "cities",
                []
            )

            if not cities:

                st.warning(
                    "⚠️ No Pakistani city found. "
                    "Try another spelling."
                )

                st.stop()

            st.subheader(
                "📍 Matching Pakistani Cities"
            )

            # ------------------------------------------------
            # CITY SELECTOR
            # ------------------------------------------------

            city_labels = []

            for city in cities:

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
                options=range(len(city_labels)),
                format_func=lambda i: city_labels[i],
                key="selected_city"
            )

            selected_city = cities[
                selected_index
            ]

            # ------------------------------------------------
            # CITY DATA
            # ------------------------------------------------

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

            timezone = selected_city.get(
                "timezone",
                "auto"
            )

            # ------------------------------------------------
            # CITY INFORMATION
            # ------------------------------------------------

            st.success(
                f"📍 **{city_name}, "
                f"{province}, Pakistan**"
            )

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
                zoom=9
            )

            # =================================================
            # DATE SELECTION
            # =================================================

            st.divider()

            st.header(
                "📅 Select Forecast Date"
            )

            today = date.today()

            selected_date = st.date_input(
                "Forecast date",
                value=today,
                min_value=today,
                max_value=today + timedelta(days=15)
            )

            # =================================================
            # SELECTED DATE FORECAST
            # =================================================

            try:

                with st.spinner(
                    "🌦️ Loading weather forecast..."
                ):

                    forecast_data = get_forecast(
                        latitude,
                        longitude,
                        selected_date
                    )

                # ------------------------------------------------
                # BASIC DATA
                # ------------------------------------------------

                temperature = forecast_data.get(
                    "temperature",
                    {}
                )

                apparent = forecast_data.get(
                    "apparent_temperature",
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

                feels_min = apparent.get(
                    "minimum"
                )

                feels_max = apparent.get(
                    "maximum"
                )

                weather_code = forecast_data.get(
                    "weather_code"
                )

                precipitation = forecast_data.get(
                    "precipitation_mm",
                    0
                )

                rain = forecast_data.get(
                    "rain_mm",
                    0
                )

                rain_probability = forecast_data.get(
                    "rain_probability",
                    0
                )

                wind_speed = forecast_data.get(
                    "wind_speed_kmh",
                    0
                )

                wind_gust = forecast_data.get(
                    "wind_gust_kmh",
                    0
                )

                wind_direction = forecast_data.get(
                    "wind_direction"
                )

                sunrise = forecast_data.get(
                    "sunrise"
                )

                sunset = forecast_data.get(
                    "sunset"
                )

                icon, description = weather_description(
                    weather_code
                )

                # =================================================
                # WEATHER HEADER
                # =================================================

                st.divider()

                st.header(
                    f"{icon} Weather Forecast"
                )

                st.subheader(
                    f"📍 {city_name}, "
                    f"{province}, Pakistan"
                )

                st.write(
                    f"📅 **{selected_date.strftime('%A, %d %B %Y')}**"
                )

                # =================================================
                # TEMPERATURE CARDS
                # =================================================

                st.markdown("### 🌡️ Temperature")

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "🌡️ Average",
                    safe_number(
                        temp_avg,
                        1,
                        " °C"
                    )
                )

                c2.metric(
                    "🔺 Maximum",
                    safe_number(
                        temp_max,
                        1,
                        " °C"
                    )
                )

                c3.metric(
                    "🔻 Minimum",
                    safe_number(
                        temp_min,
                        1,
                        " °C"
                    )
                )

                c4.metric(
                    "🌧️ Rain Chance",
                    safe_number(
                        rain_probability,
                        0,
                        "%"
                    )
                )

                st.success(
                    f"{icon} **{description}**"
                )

                # =================================================
                # FEELS LIKE
                # =================================================

                st.markdown(
                    "### 🌡️ Feels Like"
                )

                c1, c2 = st.columns(2)

                c1.metric(
                    "Minimum Feels Like",
                    safe_number(
                        feels_min,
                        1,
                        " °C"
                    )
                )

                c2.metric(
                    "Maximum Feels Like",
                    safe_number(
                        feels_max,
                        1,
                        " °C"
                    )
                )

                # =================================================
                # RAIN & WIND
                # =================================================

                st.markdown(
                    "### 🌧️ Rain & Wind"
                )

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Precipitation",
                    safe_number(
                        precipitation,
                        1,
                        " mm"
                    )
                )

                c2.metric(
                    "Rain",
                    safe_number(
                        rain,
                        1,
                        " mm"
                    )
                )

                c3.metric(
                    "Wind Speed",
                    safe_number(
                        wind_speed,
                        1,
                        " km/h"
                    )
                )

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "💨 Maximum Wind Gust",
                    safe_number(
                        wind_gust,
                        1,
                        " km/h"
                    )
                )

                if wind_direction is not None:

                    c2.metric(
                        "🧭 Wind Direction",
                        f"{float(wind_direction):.0f}°"
                    )

                else:

                    c2.metric(
                        "🧭 Wind Direction",
                        "N/A"
                    )

                c3.metric(
                    "🏔️ Elevation",
                    safe_number(
                        elevation,
                        0,
                        " m"
                    )
                )

                # =================================================
                # SUN
                # =================================================

                st.markdown(
                    "### 🌅 Sun Information"
                )

                c1, c2 = st.columns(2)

                c1.metric(
                    "🌅 Sunrise",
                    sunrise if sunrise else "N/A"
                )

                c2.metric(
                    "🌇 Sunset",
                    sunset if sunset else "N/A"
                )

                # =================================================
                # 16 DAY FORECAST
                # =================================================

                st.divider()

                st.header(
                    "📈 16-Day Temperature Forecast"
                )

                try:

                    with st.spinner(
                        "📊 Loading 16-day forecast..."
                    ):

                        full_weather = get_16_day_weather(
                            latitude,
                            longitude
                        )

                    daily = full_weather.get(
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
                                name="Maximum °C"
                            )
                        )

                        fig.add_trace(
                            go.Scatter(
                                x=dates,
                                y=mean_temps,
                                mode="lines+markers",
                                name="Average °C"
                            )
                        )

                        fig.add_trace(
                            go.Scatter(
                                x=dates,
                                y=min_temps,
                                mode="lines+markers",
                                name="Minimum °C"
                            )
                        )

                        fig.update_layout(
                            height=450,
                            xaxis_title="Date",
                            yaxis_title="Temperature (°C)",
                            hovermode="x unified",
                            legend_title="Temperature"
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
                                "Max °C": max_temps,
                                "Average °C": mean_temps,
                                "Min °C": min_temps
                            }
                        )

                        forecast_table[
                            "Date"
                        ] = pd.to_datetime(
                            forecast_table["Date"]
                        ).dt.strftime(
                            "%d %b %Y"
                        )

                        st.dataframe(
                            forecast_table,
                            use_container_width=True,
                            hide_index=True
                        )

                except requests.RequestException as e:

                    st.warning(
                        f"⚠️ 16-day forecast unavailable: {e}"
                    )

                except Exception as e:

                    st.warning(
                        f"⚠️ Chart error: {e}"
                    )

            except requests.HTTPError as e:

                st.error(
                    "❌ Forecast service error."
                )

                st.code(
                    str(e)
                )

            except requests.RequestException as e:

                st.error(
                    "❌ Could not connect to Railway backend."
                )

                st.code(
                    str(e)
                )

            except Exception as e:

                st.error(
                    "❌ Unexpected forecast error."
                )

                st.code(
                    str(e)
                )

        except requests.HTTPError as e:

            st.error(
                "❌ City search service error."
            )

            st.code(
                str(e)
            )

        except requests.RequestException as e:

            st.error(
                "❌ Could not connect to backend."
            )

            st.code(
                str(e)
            )

        except Exception as e:

            st.error(
                "❌ Unexpected error."
            )

            st.code(
                str(e)
            )


else:

    st.info(
        "⌨️ Start typing a Pakistani city name "
        "to see matching suggestions."
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
