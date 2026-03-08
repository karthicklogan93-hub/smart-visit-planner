import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import requests
from datetime import datetime

st.title("Smart Client Visit Planner")

st.write("Enter client information to generate optimized visit order")

# Starting Location
st.header("Starting Location")
start_lat = st.number_input("Start Latitude", value=13.0827)
start_lon = st.number_input("Start Longitude", value=80.2707)

start_location = (start_lat, start_lon)

# Number of Clients
num_clients = st.number_input("Number of Clients", min_value=1, max_value=10, value=3)

clients = []

st.header("Client Details")

for i in range(int(num_clients)):

    st.subheader(f"Client {i+1}")

    name = st.text_input(f"Client Name {i+1}")

    coords = st.text_input(
        f"Latitude,Longitude {i+1}",
        placeholder="Example: 13.0827,80.2707"
    )

    availability = st.text_input(
        f"Availability Time {i+1} (Example: 09:30 AM)"
    )

    lat, lon = None, None

    if coords:
        try:
            lat, lon = map(float, coords.split(","))
        except:
            pass

    clients.append({
        "name": name,
        "lat": lat,
        "lon": lon,
        "availability": availability
    })

# Weather API
def get_weather(lat, lon):

    try:

        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

        r = requests.get(url)

        data = r.json()

        code = data["current_weather"]["weathercode"]

        if code <= 3:
            return "Good"

        else:
            return "Bad"

    except:
        return "Unknown"


# Traffic Estimation
def estimate_traffic(distance):

    if distance < 5:
        return "Low", 1

    elif distance < 15:
        return "Medium", 1.2

    else:
        return "High", 1.5


# Convert time
def convert_time(t):

    try:
        return datetime.strptime(t, "%I:%M %p")
    except:
        return datetime.strptime("11:59 PM", "%I:%M %p")


# Generate Plan
if st.button("Generate Visit Plan"):

    results = []

    for client in clients:

        if client["lat"] is None:
            continue

        location = (client["lat"], client["lon"])

        distance = geodesic(start_location, location).km

        traffic, traffic_factor = estimate_traffic(distance)

        weather = get_weather(client["lat"], client["lon"])

        time_value = convert_time(client["availability"])

        results.append({

            "Client": client["name"],
            "Availability": client["availability"],
            "TimeValue": time_value,
            "Distance_km": round(distance,2),
            "Traffic": traffic,
            "TrafficFactor": traffic_factor,
            "Weather": weather

        })

    df = pd.DataFrame(results)

    if len(df) == 0:
        st.warning("Enter valid client data")
        st.stop()

    # Weather priority
    df["WeatherPriority"] = df["Weather"].map({
        "Good":0,
        "Bad":1,
        "Unknown":2
    })

    # Sorting Logic
    df = df.sort_values(

        by=[
            "TimeValue",
            "Distance_km",
            "TrafficFactor",
            "WeatherPriority"
        ]

    )

    st.header("Recommended Visit Order")

    for i,row in df.iterrows():

        st.write(

            f"{df.index.get_loc(i)+1}. {row['Client']} | "
            f"{row['Availability']} | "
            f"{row['Distance_km']} km | "
            f"Traffic: {row['Traffic']} | "
            f"Weather: {row['Weather']}"

        )

    st.dataframe(df)
