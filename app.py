import streamlit as st
import pandas as pd
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime, timedelta

st.title("🚗 Smart Visit Planner")

geolocator = Nominatim(user_agent="visit_planner")

# Weather API (free)
WEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"

# Store clients
if "clients" not in st.session_state:
    st.session_state.clients = []

# Start location
st.header("Start Location")
start_address = st.text_input("Enter Start Address")

# Client input
st.header("Add Client")

name = st.text_input("Client Name")
address = st.text_input("Client Address")
availability_start = st.time_input("Available From")
availability_end = st.time_input("Available Until")

if st.button("Add Client"):
    st.session_state.clients.append({
        "name": name,
        "address": address,
        "start": availability_start,
        "end": availability_end
    })

# Display clients
if st.session_state.clients:
    st.subheader("Client List")
    df = pd.DataFrame(st.session_state.clients)
    st.table(df)

# Get coordinates
def get_coordinates(address):
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

# Get weather
def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
    response = requests.get(url).json()

    if "weather" in response:
        return response["weather"][0]["main"]
    return "Unknown"

# Travel time estimate
def estimate_travel_time(distance_km):
    avg_speed = 40  # km/h city average
    return distance_km / avg_speed

# Route optimization
def optimize_route(start_coord, clients):

    remaining = clients.copy()
    route = []
    current = start_coord
    current_time = datetime.now()

    while remaining:

        best_client = None
        best_score = 999999

        for client in remaining:

            distance = geodesic(current, client["coord"]).km
            travel_time = estimate_travel_time(distance)

            arrival_time = current_time + timedelta(hours=travel_time)

            # Availability check
            start_window = datetime.combine(datetime.today(), client["start"])
            end_window = datetime.combine(datetime.today(), client["end"])

            if arrival_time < start_window:
                wait_penalty = (start_window - arrival_time).seconds / 3600
            else:
                wait_penalty = 0

            if arrival_time > end_window:
                availability_penalty = 100
            else:
                availability_penalty = 0

            # Weather penalty
            weather_penalty = 5 if client["weather"] in ["Rain", "Storm"] else 0

            score = distance + wait_penalty + availability_penalty + weather_penalty

            if score < best_score:
                best_score = score
                best_client = client

        route.append(best_client)

        travel_distance = geodesic(current, best_client["coord"]).km
        travel_time = estimate_travel_time(travel_distance)

        current_time += timedelta(hours=travel_time)
        current = best_client["coord"]

        remaining.remove(best_client)

    return route

# Optimize route
if st.button("Optimize Visit Plan"):

    if not start_address:
        st.error("Enter start location")

    else:

        start_coord = get_coordinates(start_address)

        client_data = []

        for c in st.session_state.clients:

            coord = get_coordinates(c["address"])

            if coord:

                weather = get_weather(coord[0], coord[1])

                client_data.append({
                    "name": c["name"],
                    "address": c["address"],
                    "start": c["start"],
                    "end": c["end"],
                    "coord": coord,
                    "weather": weather
                })

        route = optimize_route(start_coord, client_data)

        st.header("📍 Suggested Visit Order")

        current = start_coord
        total_distance = 0
        results = []

        for i, client in enumerate(route, 1):

            distance = geodesic(current, client["coord"]).km
            total_distance += distance

            travel_time = estimate_travel_time(distance)

            results.append({
                "Order": i,
                "Client": client["name"],
                "Address": client["address"],
                "Distance (km)": round(distance,2),
                "Travel Time (hrs)": round(travel_time,2),
                "Weather": client["weather"]
            })

            current = client["coord"]

        result_df = pd.DataFrame(results)

        st.table(result_df)

        st.success(f"Total Distance: {round(total_distance,2)} km")
