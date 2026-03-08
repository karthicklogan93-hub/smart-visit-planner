import streamlit as st
import pandas as pd
import requests
from geopy.distance import geodesic
from datetime import datetime

st.title("🌍 Smart Client Visit Planner")

st.write("Enter client details in the format:")
st.code("ClientName, Latitude, Longitude, AvailabilityStart-End in format (00:00-24:00)")

start_lat = st.number_input("Start Latitude", value=13.0827)
start_lon = st.number_input("Start Longitude", value=80.2707)

client_input = st.text_area(
"Enter Clients",
"""ClientA,13.0674,80.2376,10:00-12:00
ClientB,13.0352,80.2223,13:00-15:00
ClientC,13.1200,80.2950,09:00-11:00"""
)

API_KEY = "968fe0ce80c15dc1ba42bc3cdf544746"

def get_weather(lat,lon):

    url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    try:
        res=requests.get(url).json()
        weather=res["weather"][0]["main"]
        temp=res["main"]["temp"]
        return f"{weather} {temp}°C"
    except:
        return "Unavailable"

def parse_clients(text):

    clients=[]
    lines=text.strip().split("\n")

    for line in lines:

        parts=line.split(",")

        name=parts[0]
        lat=float(parts[1])
        lon=float(parts[2])
        availability=parts[3]

        clients.append({
            "name":name,
            "lat":lat,
            "lon":lon,
            "availability":availability
        })

    return clients


def optimize_route(start,clients):

    route=[]
    remaining=clients.copy()
    current=start

    while remaining:

        nearest=min(
            remaining,
            key=lambda x: geodesic(current,(x["lat"],x["lon"])).km
        )

        dist=geodesic(current,(nearest["lat"],nearest["lon"])).km

        weather=get_weather(nearest["lat"],nearest["lon"])

        route.append({
            "Client":nearest["name"],
            "Latitude":nearest["lat"],
            "Longitude":nearest["lon"],
            "Availability":nearest["availability"],
            "Weather":weather,
            "Distance_km":round(dist,2)
        })

        current=(nearest["lat"],nearest["lon"])
        remaining.remove(nearest)

    return route


if st.button("Generate Smart Visit Plan"):

    clients=parse_clients(client_input)

    start=(start_lat,start_lon)

    route=optimize_route(start,clients)

    df=pd.DataFrame(route)

    st.success("Recommended Visit Order")

    st.dataframe(df)

    total=df["Distance_km"].sum()

    st.write("### Total Distance")
    st.write(round(total,2),"km")
