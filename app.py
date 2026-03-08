import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd

st.title("🚗 Smart Client Visit Planner")

# Initialize geocoder
geolocator = Nominatim(user_agent="visit_planner")

# Store client data
if "clients" not in st.session_state:
    st.session_state.clients = []

# Starting location
st.header("Start Location")
start_address = st.text_input("Enter Start Address")

# Client input section
st.header("Add Client")

client_name = st.text_input("Client Name")
client_address = st.text_input("Client Address")

if st.button("Add Client"):
    if client_name and client_address:
        st.session_state.clients.append({
            "name": client_name,
            "address": client_address
        })
        st.success(f"{client_name} added")

# Show client list
if st.session_state.clients:
    st.subheader("Client List")

    df = pd.DataFrame(st.session_state.clients)
    st.table(df)

# Function to convert address to coordinates
def get_coordinates(address):
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

# Route optimization
def optimize_route(start_coord, clients):

    remaining = clients.copy()
    route = []
    current = start_coord

    while remaining:

        nearest = min(
            remaining,
            key=lambda x: geodesic(current, x["coord"]).km
        )

        route.append(nearest)
        current = nearest["coord"]
        remaining.remove(nearest)

    return route

# Optimize button
if st.button("Optimize Visit Route"):

    if not start_address:
        st.error("Please enter start location")

    else:

        start_coord = get_coordinates(start_address)

        if not start_coord:
            st.error("Start location not found")

        else:

            client_coords = []

            for client in st.session_state.clients:

                coord = get_coordinates(client["address"])

                if coord:
                    client_coords.append({
                        "name": client["name"],
                        "address": client["address"],
                        "coord": coord
                    })

            route = optimize_route(start_coord, client_coords)

            st.header("📍 Suggested Visit Order")

            current = start_coord
            total_distance = 0

            results = []

            for i, client in enumerate(route, 1):

                distance = geodesic(current, client["coord"]).km
                total_distance += distance

                results.append({
                    "Order": i,
                    "Client": client["name"],
                    "Address": client["address"],
                    "Distance from previous (km)": round(distance,2)
                })

                current = client["coord"]

            result_df = pd.DataFrame(results)

            st.table(result_df)

            st.success(f"Total Travel Distance: {round(total_distance,2)} km")
