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
# PROFESSIONAL CSS
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 0;
}

.subtitle {
    font-size: 18px;
    opacity: 0.7;
    margin-bottom: 25px;
}

.search-box {
    padding: 15px;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,0.25);
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🇵🇰 PakWeather AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Smart weather search and forecast for cities across Pakistan'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# CITY SEARCH API
# ============================================================

@st.cache_data(ttl=3600)
def search_cities(query):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": query,
        "count": 20,
        "language": "en",
        "format": "json"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        # Only Pakistan
        pakistan_results = []

        for location in results:

            country_code = location.get(
                "country_code",
                ""
            )

            country = location.get(
                "country",
                ""
            )

            if (
                country_code.upper() == "PK"
                or country.lower() == "pakistan"
            ):

                pakistan_results.append(location)

        return pakistan_results

    except Exception:

        return []


# ============================================================
# WEATHER API
# ============================================================

@st.cache_data(ttl=600)
def get_weather(
    latitude,
    longitude,
    timezone
):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "rain_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "wind_direction_10m_dominant",
            "sunrise",
            "sunset"
        ]),

        "timezone": timezone,

        "forecast_days": 16,

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# WEATHER DESCRIPTION
# ============================================================

def get_weather_description(code):

    weather_codes = {

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

        71: ("🌨️", "Slight snow"),

        73: ("🌨️", "Moderate snow"),

        75: ("❄️", "Heavy snow"),

        80: ("🌦️", "Rain showers"),

        81: ("🌧️", "Moderate rain showers"),

        82: ("⛈️", "Heavy rain showers"),

        85: ("🌨️", "Snow showers"),

        86: ("❄️", "Heavy snow showers"),

        95: ("⛈️", "Thunderstorm"),

        96: ("⛈️", "Thunderstorm with hail"),

        99: ("⛈️", "Severe thunderstorm")
    }

    return weather_codes.get(
        int(code),
        ("🌡️", "Weather")
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🇵🇰 PakWeather AI")

    st.success("🟢 Weather Service Online")

    st.divider()

    st.markdown("""
    ### Features

    🔎 Smart City Search

    🇵🇰 Pakistan Cities

    📅 16-Day Forecast

    🌡️ Temperature

    🌧️ Rain Probability

    💨 Wind Forecast

    📊 Interactive Charts

    🗺️ Location Map
    """)

    st.divider()

    st.caption(
        "Weather data powered by Open-Meteo."
    )


# ============================================================
# CITY SEARCH
# ============================================================

st.header("🔎 Search Pakistani City")

st.write(
    "Type a city name and select a matching Pakistani city."
)


city_query = st.text_input(
    "City Search",
    placeholder="🔍 Try: mul, kar, lah, isl, mur...",
    label_visibility="collapsed"
)


# ============================================================
# SEARCH
# ============================================================

if city_query.strip():

    query = city_query.strip()

    if len(query) < 2:

        st.info(
            "⌨️ Type at least 2 letters..."
        )

        st.stop()


    with st.spinner("🔎 Finding Pakistani cities..."):

        locations = search_cities(query)


    # ========================================================
    # NO RESULTS
    # ========================================================

    if not locations:

        st.warning(
            f"❌ No Pakistani city found for '{query}'."
        )

        st.info(
            "Try: Karachi, Lahore, Multan, Murree, "
            "Islamabad, Peshawar, Quetta..."
        )

        st.stop()


    # ========================================================
    # CREATE SUGGESTIONS
    # ========================================================

    city_options = {}

    for location in locations:

        city = location.get(
            "name",
            "Unknown"
        )

        province = location.get(
            "admin1",
            ""
        )

        country = location.get(
            "country",
            "Pakistan"
        )

        latitude = location.get(
            "latitude"
        )

        longitude = location.get(
            "longitude"
        )

        timezone = location.get(
            "timezone",
            "auto"
        )


        label = city

        if province:

            label += f" — {province}"

        label += " 🇵🇰"


        city_options[label] = {

            "name": city,

            "province": province,

            "country": country,

            "latitude": latitude,

            "longitude": longitude,

            "timezone": timezone
        }


    # ========================================================
    # CITY DROPDOWN
    # ========================================================

    st.subheader("📍 City Suggestions")

    selected_label = st.selectbox(

        "Select your city",

        options=list(
            city_options.keys()
        ),

        index=0,

        key="city_selector"
    )


    selected_city = city_options[
        selected_label
    ]


    # ========================================================
    # CITY INFORMATION
    # ========================================================

    city_name = selected_city["name"]

    province = selected_city["province"]

    latitude = float(
        selected_city["latitude"]
    )

    longitude = float(
        selected_city["longitude"]
    )

    timezone = selected_city["timezone"]


    st.success(
        f"📍 Selected: **{city_name}, "
        f"{province}, Pakistan**"
    )


    # ========================================================
    # LOCATION
    # ========================================================

    st.subheader("🗺️ City Location")

    map_data = pd.DataFrame({

        "latitude": [latitude],

        "longitude": [longitude]
    })


    st.map(
        map_data,

        latitude="latitude",

        longitude="longitude",

        zoom=8
    )


    # ========================================================
    # WEATHER
    # ========================================================

    st.divider()

    st.header("📅 Weather Forecast")


    today = date.today()

    maximum_date = (
        today + timedelta(days=15)
    )


    selected_date = st.date_input(

        "Select forecast date",

        value=today,

        min_value=today,

        max_value=maximum_date
    )


    # ========================================================
    # LOAD WEATHER
    # ========================================================

    try:

        with st.spinner(
            "🌦️ Loading latest weather..."
        ):

            weather = get_weather(

                latitude,

                longitude,

                timezone
            )


    except Exception as e:

        st.error(
            "❌ Weather data could not be loaded."
        )

        st.code(str(e))

        st.stop()


    daily = weather.get(
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
            "❌ Forecast unavailable for this date."
        )

        st.stop()


    i = dates.index(
        selected_date_string
    )


    # ========================================================
    # VALUES
    # ========================================================

    weather_code = daily[
        "weather_code"
    ][i]


    temp_max = daily[
        "temperature_2m_max"
    ][i]


    temp_min = daily[
        "temperature_2m_min"
    ][i]


    temp_mean = daily[
        "temperature_2m_mean"
    ][i]


    feels_like = daily[
        "apparent_temperature_max"
    ][i]


    rain = daily[
        "rain_sum"
    ][i]


    precipitation = daily[
        "precipitation_sum"
    ][i]


    rain_probability = daily[
        "precipitation_probability_max"
    ][i]


    wind = daily[
        "wind_speed_10m_max"
    ][i]


    wind_gust = daily[
        "wind_gusts_10m_max"
    ][i]


    icon, description = (
        get_weather_description(
            weather_code
        )
    )


    # ========================================================
    # MAIN WEATHER RESULT
    # ========================================================

    st.divider()


    st.header(
        f"{icon} {city_name} Weather"
    )


    st.write(
        f"📅 **{selected_date}**"
    )


    st.success(
        f"{icon} **{description}**"
    )


    # ========================================================
    # WEATHER CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "🌡️ Average",
            f"{temp_mean:.1f} °C"
        )


    with col2:

        st.metric(
            "🔺 Maximum",
            f"{temp_max:.1f} °C"
        )


    with col3:

        st.metric(
            "🔻 Minimum",
            f"{temp_min:.1f} °C"
        )


    with col4:

        st.metric(
            "☔ Rain Chance",
            f"{rain_probability}%"
        )


    # ========================================================
    # DETAILS
    # ========================================================

    st.subheader(
        "🌦️ Weather Details"
    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "🌧️ Rain",
            f"{rain:.1f} mm"
        )


    with c2:

        st.metric(
            "💧 Precipitation",
            f"{precipitation:.1f} mm"
        )


    with c3:

        st.metric(
            "💨 Wind",
            f"{wind:.1f} km/h"
        )


    with c4:

        st.metric(
            "💨 Wind Gust",
            f"{wind_gust:.1f} km/h"
        )


    # ========================================================
    # TEMPERATURE CHART
    # ========================================================

    st.divider()

    st.header(
        "📈 16-Day Temperature Forecast"
    )


    temperature_chart = go.Figure()


    temperature_chart.add_trace(

        go.Scatter(

            x=daily["time"],

            y=daily[
                "temperature_2m_max"
            ],

            mode="lines+markers",

            name="Maximum"
        )
    )


    temperature_chart.add_trace(

        go.Scatter(

            x=daily["time"],

            y=daily[
                "temperature_2m_mean"
            ],

            mode="lines+markers",

            name="Average"
        )
    )


    temperature_chart.add_trace(

        go.Scatter(

            x=daily["time"],

            y=daily[
                "temperature_2m_min"
            ],

            mode="lines+markers",

            name="Minimum"
        )
    )


    temperature_chart.update_layout(

        height=450,

        xaxis_title="Date",

        yaxis_title="Temperature °C",

        hovermode="x unified"
    )


    st.plotly_chart(

        temperature_chart,

        use_container_width=True
    )


    # ========================================================
    # RAIN CHART
    # ========================================================

    st.header(
        "🌧️ Rain Probability"
    )


    rain_chart = go.Figure()


    rain_chart.add_trace(

        go.Bar(

            x=daily["time"],

            y=daily[
                "precipitation_probability_max"
            ],

            name="Rain Probability"
        )
    )


    rain_chart.update_layout(

        height=400,

        xaxis_title="Date",

        yaxis_title="Probability %"
    )


    st.plotly_chart(

        rain_chart,

        use_container_width=True
    )


    # ========================================================
    # 16 DAY TABLE
    # ========================================================

    st.header(
        "📅 16-Day Forecast"
    )


    forecast_table = pd.DataFrame({

        "Date":
            daily["time"],

        "Min °C":
            daily[
                "temperature_2m_min"
            ],

        "Average °C":
            daily[
                "temperature_2m_mean"
            ],

        "Max °C":
            daily[
                "temperature_2m_max"
            ],

        "Rain %":
            daily[
                "precipitation_probability_max"
            ],

        "Rain mm":
            daily[
                "rain_sum"
            ],

        "Wind km/h":
            daily[
                "wind_speed_10m_max"
            ]
    })


    st.dataframe(

        forecast_table,

        use_container_width=True,

        hide_index=True
    )


else:

    # ========================================================
    # EMPTY SEARCH STATE
    # ========================================================

    st.info(
        "🔎 Start typing a Pakistani city name above."
    )


    st.markdown(
        """
        ### 🔥 Try these examples

        **mul** → Multan

        **kar** → Karachi

        **lah** → Lahore

        **isl** → Islamabad

        **mur** → Murree

        **pes** → Peshawar

        **que** → Quetta
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🇵🇰 PakWeather AI • Pakistan Weather Forecast Dashboard"
)

st.caption(
    "Weather data powered by Open-Meteo."
)