# AR_map.py
import pandas as pd
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium
from AR_constants import DEFAULT_ZOOM, RADIUS_KM

def build_map(df):
    m = folium.Map(location=[df["latitude"].mean(), df["longitude"].mean()], zoom_start=DEFAULT_ZOOM)
    for _, row in df.dropna(subset=["latitude", "longitude"]).iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=f"{row['address']}<br>{row['style']}<br>{row['price']} THB",
            icon=folium.Icon(color="blue", icon="home")
        ).add_to(m)
    return m

def within_radius(row, center, radius_km=RADIUS_KM):
    if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):
        return geodesic((row["latitude"], row["longitude"]), center).km <= radius_km
    return False

def folium_click(df, width=700, height=500):
    m = build_map(df)
    map_data = st_folium(m, width=width, height=height)
    return map_data
