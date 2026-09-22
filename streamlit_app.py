"""Streamlit deployment entrypoint for the AI City Intelligence Platform."""

from datetime import datetime

import streamlit as st
from pydantic import ValidationError

from api.schemas.air_quality import AirQualityRequest
from api.schemas.traffic import TrafficRequest
from api.schemas.transport import TransportRequest
from api.schemas.waste import WasteRequest
from api.services.air_quality_services import predict_air_quality
from api.services.traffic_services import predict_traffic
from api.services.transport_services import _valid_cities, predict_transport
from api.services.waste_services import _valid_categories, predict_waste


st.set_page_config(
    page_title="AI City Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def show_result(
    title: str, value: int, status_label: str, status_value: str, recommendation: str
) -> None:
    first, second, third = st.columns(3)
    first.metric(title, f"{value:,}")
    second.metric(status_label, status_value)
    third.metric("Status", "Complete")
    st.info(recommendation)


def show_error(error: Exception) -> None:
    st.error(str(error))


st.title("AI City Intelligence Platform")
st.caption("Traffic, air quality, waste management, and public-transport decision support")

with st.sidebar:
    st.header("About this app")
    st.write("Select a module, enter the available operational data, and receive a model-based estimate.")
    st.warning("Waste results are scenario estimates and should be validated against local collection records.")
    st.caption("Models are loaded locally from the repository's `models/` folder.")

traffic_tab, aqi_tab, waste_tab, transport_tab = st.tabs([
    "Traffic", "Air Quality", "Waste", "Transport"
])

with traffic_tab:
    st.subheader("Traffic Volume Prediction")
    st.caption("Estimate traffic volume from weather and calendar conditions.")
    with st.form("traffic_form"):
        first, second, third, fourth = st.columns(4)
        temp = first.number_input("Temperature (Kelvin)", min_value=0.0, value=288.0)
        rain = second.number_input("Rainfall (mm/hour)", min_value=0.0, value=0.0)
        snow = third.number_input("Snowfall (mm/hour)", min_value=0.0, value=0.0)
        clouds = fourth.number_input("Cloud cover (%)", min_value=0.0, max_value=100.0, value=40.0)
        hour = first.number_input("Hour", min_value=0, max_value=23, value=8)
        day_of_week = second.selectbox("Day of week", range(7), format_func=lambda day: [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
        ][day])
        month = third.number_input("Month", min_value=1, max_value=12, value=6)
        is_weekend = fourth.selectbox("Weekend", [0, 1], format_func=lambda value: "Yes" if value else "No")
        submitted = st.form_submit_button("Predict Traffic", use_container_width=True)

    if submitted:
        try:
            result = predict_traffic(TrafficRequest(
                temp=temp, rain_1h=rain, snow_1h=snow, clouds_all=clouds,
                hour=hour, day_of_week=day_of_week, month=month, is_weekend=is_weekend,
            ))
            show_result(
                "Predicted vehicles/hour", result["predicted_traffic_volume"],
                "Congestion", result["congestion_level"], result["recommendation"],
            )
        except (ValidationError, ValueError) as error:
            show_error(error)

with aqi_tab:
    st.subheader("Air Quality Estimation")
    st.caption("Estimate AQI from measured pollutant concentrations.")
    with st.form("aqi_form"):
        first, second, third, fourth = st.columns(4)
        city = first.selectbox("City", ["Bangalore", "Chennai", "Delhi", "Kolkata", "Mumbai"])
        measured_at = second.date_input("Measurement date")
        measured_time = third.time_input("Measurement time")
        pm25 = fourth.number_input("PM2.5", min_value=0.0, value=50.0)
        pm10 = first.number_input("PM10", min_value=0.0, value=80.0)
        no = second.number_input("NO", min_value=0.0, value=10.0)
        no2 = third.number_input("NO2", min_value=0.0, value=25.0)
        nox = fourth.number_input("NOx", min_value=0.0, value=30.0)
        nh3 = first.number_input("NH3", min_value=0.0, value=15.0)
        co = second.number_input("CO", min_value=0.0, value=0.8)
        so2 = third.number_input("SO2", min_value=0.0, value=12.0)
        o3 = fourth.number_input("O3", min_value=0.0, value=35.0)
        submitted = st.form_submit_button("Estimate AQI", use_container_width=True)

    if submitted:
        try:
            result = predict_air_quality(AirQualityRequest(
                city=city,
                datetime=datetime.combine(measured_at, measured_time),
                **{"PM2.5": pm25, "PM10": pm10, "NO": no, "NO2": no2, "NOx": nox,
                   "NH3": nh3, "CO": co, "SO2": so2, "O3": o3},
            ))
            first, second, third = st.columns(3)
            first.metric("Predicted AQI", result["predicted_aqi"])
            second.metric("AQI category", result["aqi_category"])
            third.metric("Risk score", f"{result['risk_score']}%")
        except (ValidationError, ValueError) as error:
            show_error(error)

with waste_tab:
    st.subheader("Waste Management Scenario Estimate")
    st.caption("Estimate daily waste generation from city, waste-type, and infrastructure conditions.")
    categories = _valid_categories()
    with st.form("waste_form"):
        first, second, third, fourth = st.columns(4)
        city = first.selectbox("City", sorted(categories["city"]))
        waste_type = second.selectbox("Waste type", sorted(categories["waste_type"]))
        disposal_method = third.selectbox("Disposal method", sorted(categories["disposal_method"]))
        recycling_rate = fourth.number_input("Recycling rate (%)", min_value=0.0, max_value=100.0, value=50.0)
        population_density = first.number_input("Population density", min_value=0.0, value=10000.0)
        efficiency = second.number_input("Municipal efficiency (1-10)", min_value=1.0, max_value=10.0, value=5.0)
        campaigns = third.number_input("Awareness campaigns", min_value=0, value=5)
        landfill_capacity = fourth.number_input("Landfill capacity (tons)", min_value=0.0, value=50000.0)
        initiatives = first.number_input("Waste reduction initiatives", min_value=0.0, value=5.0)
        symbiosis = second.number_input("Industrial symbiosis index", min_value=0.0, value=5.0)
        participation = third.number_input("Community participation score", min_value=0.0, value=5.0)
        green_technology = fourth.number_input("Green technology adoption", min_value=0.0, value=5.0)
        infrastructure_rating = first.number_input("Recycling infrastructure rating", min_value=0.0, value=50.0)
        submitted = st.form_submit_button("Estimate Waste", use_container_width=True)

    if submitted:
        try:
            result = predict_waste(WasteRequest(
                city=city, waste_type=waste_type, disposal_method=disposal_method,
                recycling_rate=recycling_rate, population_density=population_density,
                municipal_efficiency_score=efficiency, awareness_campaigns_count=campaigns,
                landfill_capacity_tons=landfill_capacity,
                waste_reduction_initiatives=initiatives,
                industrial_symbiosis_index=symbiosis,
                community_participation_score=participation,
                green_technology_adoption=green_technology,
                recycling_infrastructure_rating=infrastructure_rating,
            ))
            show_result(
                "Predicted tons/day", result["predicted_waste_tons_per_day"],
                "Collection priority", result["collection_priority"], result["recommendation"],
            )
            st.caption(result["model_note"])
        except (ValidationError, ValueError) as error:
            show_error(error)

with transport_tab:
    st.subheader("Transport Demand Prediction")
    st.caption("Estimate daily passenger demand from bus infrastructure and service operations.")
    with st.form("transport_form"):
        first, second, third, fourth = st.columns(4)
        city = first.selectbox("City", sorted(_valid_cities()))
        year_start = second.selectbox("Year", [2015, 2016, 2017, 2018])
        daily_trips = third.number_input("Daily trips", min_value=0.1, value=245.0)
        trip_length = fourth.number_input("Daily trip length (km)", min_value=0.1, value=16546.0)
        total_buses = first.number_input("Total buses", min_value=1, value=170)
        terminals = second.number_input("Bus terminals", min_value=0, value=20)
        stands = third.number_input("Bus stands", min_value=0, value=5)
        stops = fourth.number_input("Bus stops", min_value=0, value=30)
        submitted = st.form_submit_button("Predict Passenger Demand", use_container_width=True)

    if submitted:
        try:
            result = predict_transport(TransportRequest(
                city=city, year_start=year_start, daily_trips=daily_trips,
                daily_trip_length_km=trip_length, total_buses=total_buses,
                bus_terminals=terminals, bus_stands=stands, bus_stops=stops,
            ))
            show_result(
                "Predicted daily passengers", result["predicted_daily_passengers"],
                "Crowd level", result["crowd_level"], result["recommendation"],
            )
        except (ValidationError, ValueError) as error:
            show_error(error)
