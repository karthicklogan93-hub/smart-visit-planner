import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import requests
import itertools

st.title("🚗 Smart Client Visit Planner")

st.write("Enter client details below")

# Doctor / user starting location
st.header("Your Starting Location")
start_lat = st.number_input("Start Latitude", value=13.0827)
start_lon = st.number_input("Start Longitude", value=80.2707)

start_location = (start_lat, start_lon)

# Number of clients
num_clients = st.number_input("Number of Clients", min_value=1, max_value=10, value=3)

clients = []

st.header("Client Details")

for i in range(int(num_clients)):
    st.subheader(f"Client {i+1}")
    
    name = st.text_input(f"Client Name {i+1}")
    
    coord = st.text_input(
        f"Latitude,Longitude {i+1}",
        placeholder="Example: 13.0827,80.2707"
    )

    availability = st.selectbox(
        f"Availability {i+1}",
        ["AM", "PM"],
        key=i
    )

    if coord:
        try:
            lat, lon = map(float, coord.split(","))
        except:
            lat, lon = None, None
    else:
        lat, lon = None, None

    clients.append({
        "name": name,
        "lat": lat,
        "lon": lon,
        "availability": availability
    })


# Weather API (free)
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url)
        data = response.json()
        weather_code = data["current_weather"]["weathercode"]

        if weather_code < 3:
            return "Good"
        else:
            return "Bad"
    except:
        return "Unknown"


# Traffic estimation (simple logic)
def estimate_traffic(distance):

    if distance < 5:
        return "Low", 1

    elif distance < 15:
        return "Medium", 1.2

    else:
        return "High", 1.5


# Optimization
if st.button("Generate Smart Visit Plan"):

    valid_clients = [c for c in clients if c["lat"] is not None]

    if len(valid_clients) == 0:
        st.warning("Please enter valid client coordinates")
        st.stop()

    results = []

    for client in valid_clients:

        loc = (client["lat"], client["lon"])

        distance = geodesic(start_location, loc).km

        traffic, multiplier = estimate_traffic(distance)

        weather = get_weather(client["lat"], client["lon"])

        results.append({
            "name": client["name"],
            "availability": client["availability"],
            "distance": distance,
            "traffic": traffic,
            "traffic_factor": multiplier,
            "weather": weather,
            "lat": client["lat"],
            "lon": client["lon"]
        })

    df = pd.DataFrame(results)

    # Convert priority to numeric
    df["availability_priority"] = df["availability"].map({"AM":0,"PM":1})
    df["weather_priority"] = df["weather"].map({"Good":0,"Bad":1,"Unknown":2})

    # Smart sorting
    df = df.sort_values(
        by=[
            "availability_priority",
            "distance",
            "traffic_factor",
            "weather_priority"
        ]
    )

    st.header("📍 Recommended Visit Order")

    for i,row in df.iterrows():

        st.write(
            f"{df.index.get_loc(i)+1}. {row['name']} | "
            f"{row['availability']} | "
            f"{round(row['distance'],2)} km | "
            f"Traffic: {row['traffic']} | "
            f"Weather: {row['weather']}"
        )

    st.dataframe(df)        ["AM", "PM"],
        key=i
    )

    if coord:
        try:
            lat, lon = map(float, coord.split(","))
        except:
            lat, lon = None, None
    else:
        lat, lon = None, None

    clients.append({
        "name": name,
        "lat": lat,
        "lon": lon,
        "availability": availability
    })


# Weather API (free)
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url)
        data = response.json()
        weather_code = data["current_weather"]["weathercode"]

        if weather_code < 3:
            return "Good"
        else:
            return "Bad"
    except:
        return "Unknown"


# Traffic estimation (simple logic)
def estimate_traffic(distance):

    if distance < 5:
        return "Low", 1

    elif distance < 15:
        return "Medium", 1.2

    else:
        return "High", 1.5


# Optimization
if st.button("Generate Smart Visit Plan"):

    valid_clients = [c for c in clients if c["lat"] is not None]

    if len(valid_clients) == 0:
        st.warning("Please enter valid client coordinates")
        st.stop()

    results = []

    for client in valid_clients:

        loc = (client["lat"], client["lon"])

        distance = geodesic(start_location, loc).km

        traffic, multiplier = estimate_traffic(distance)

        weather = get_weather(client["lat"], client["lon"])

        results.append({
            "name": client["name"],
            "availability": client["availability"],
            "distance": distance,
            "traffic": traffic,
            "traffic_factor": multiplier,
            "weather": weather,
            "lat": client["lat"],
            "lon": client["lon"]
        })

    df = pd.DataFrame(results)

    # Convert priority to numeric
    df["availability_priority"] = df["availability"].map({"AM":0,"PM":1})
    df["weather_priority"] = df["weather"].map({"Good":0,"Bad":1,"Unknown":2})

    # Smart sorting
    df = df.sort_values(
        by=[
            "availability_priority",
            "distance",
            "traffic_factor",
            "weather_priority"
        ]
    )

    st.header("📍 Recommended Visit Order")

    for i,row in df.iterrows():

        st.write(
            f"{df.index.get_loc(i)+1}. {row['name']} | "
            f"{row['availability']} | "
            f"{round(row['distance'],2)} km | "
            f"Traffic: {row['traffic']} | "
            f"Weather: {row['weather']}"
        )

    st.dataframe(df)
