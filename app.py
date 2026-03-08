import streamlit as st
import pandas as pd
import requests
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="Smart Visit Planner", layout="wide")

st.title("AI Smart Client Visit Planner")

st.sidebar.header("Starting Location")

start_lat = st.sidebar.number_input("Start Latitude", value=11.0168)
start_lon = st.sidebar.number_input("Start Longitude", value=76.9558)

API_KEY = "YOUR_OPENWEATHER_API_KEY"

st.subheader("Enter Client Details")

client_text = st.text_area(
"Format: Client,Latitude,Longitude,Availability",
"""Udumalpet Client,10.5880,77.2470,09:00-11:00
Tiruppur Client,11.1085,77.3411,11:30-13:30
Coimbatore Client,11.0168,76.9558,14:00-16:00"""
)

# WEATHER FUNCTION
def get_weather(lat, lon):

    try:
        url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        res=requests.get(url).json()

        weather=res["weather"][0]["main"]
        temp=res["main"]["temp"]

        return weather,temp

    except:
        return "Unknown",0


# TRAFFIC ESTIMATION
def estimate_traffic(distance):

    if distance < 10:
        factor = 1.2
    elif distance < 50:
        factor = 1.4
    else:
        factor = 1.6

    travel_time = distance * factor

    return round(travel_time,2)


# WEATHER SCORE
def weather_score(weather):

    if weather == "Clear":
        return 1
    elif weather == "Clouds":
        return 2
    elif weather == "Rain":
        return 4
    else:
        return 3


# AVAILABILITY PRIORITY
def availability_priority(time_range):

    start_time=time_range.split("-")[0]

    t=datetime.strptime(start_time,"%H:%M")

    return t.hour


# PARSE INPUT
def parse_clients(text):

    clients=[]

    lines=text.split("\n")

    for line in lines:

        parts=line.split(",")

        clients.append({
            "Client":parts[0],
            "Latitude":float(parts[1]),
            "Longitude":float(parts[2]),
            "Availability":parts[3]
        })

    return pd.DataFrame(clients)


if st.button("Generate Smart Visit Plan"):

    df=parse_clients(client_text)

    start=(start_lat,start_lon)

    results=[]

    for i,row in df.iterrows():

        client_location=(row["Latitude"],row["Longitude"])

        distance=geodesic(start,client_location).km

        weather,temp=get_weather(row["Latitude"],row["Longitude"])

        traffic=estimate_traffic(distance)

        availability_score=availability_priority(row["Availability"])

        weather_penalty=weather_score(weather)

        # PRIORITY FORMULA
        score=(availability_score*5)+(distance*1)+(traffic*1)+(weather_penalty*3)

        results.append({
            "Client":row["Client"],
            "Latitude":row["Latitude"],
            "Longitude":row["Longitude"],
            "Availability":row["Availability"],
            "Distance_km":round(distance,2),
            "Traffic_Est":traffic,
            "Weather":weather,
            "Temperature":temp,
            "Score":score
        })

    route_df=pd.DataFrame(results)

    route_df=route_df.sort_values("Score")

    st.subheader("Optimized Visit Order")

    st.dataframe(route_df[[
        "Client",
        "Availability",
        "Distance_km",
        "Traffic_Est",
        "Weather",
        "Temperature"
    ]])

    st.subheader("Route Map")

    m=folium.Map(location=[start_lat,start_lon],zoom_start=9)

    folium.Marker(
        [start_lat,start_lon],
        tooltip="Start Location",
        icon=folium.Icon(color="green")
    ).add_to(m)

    coords=[[start_lat,start_lon]]

    for i,row in route_df.iterrows():

        folium.Marker(
            [row["Latitude"],row["Longitude"]],
            tooltip=f"{row['Client']}",
            popup=f"Weather: {row['Weather']}",
            icon=folium.Icon(color="blue")
        ).add_to(m)

        coords.append([row["Latitude"],row["Longitude"]])

    folium.PolyLine(coords,color="red",weight=3).add_to(m)

    st_folium(m,width=900,height=500)
