import folium
import pandas as pd

def create_map(df):
    """
    Create a Folium map centered on the average coordinates of the PG dataset.
    
    Parameters:
        df (pd.DataFrame): Filtered dataset with Latitude & Longitude

    Returns:
        folium.Map: Map object with PG/Hostel markers
    """
    if df.empty or "Latitude" not in df.columns or "Longitude" not in df.columns:
        return folium.Map(location=[19.0760, 72.8777], zoom_start=12)  # Default to Mumbai

    avg_lat = df["Latitude"].mean()
    avg_lon = df["Longitude"].mean()

    map_ = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

    for _, row in df.iterrows():
        if pd.notnull(row["Latitude"]) and pd.notnull(row["Longitude"]):
            popup_text = f"{row['Name']} ({row['Type']}) - ₹{row['Price']}"
            tooltip_text = f"{row['Area']}, {row['City']}"
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=popup_text,
                tooltip=tooltip_text,
                icon=folium.Icon(color="blue", icon="home", prefix='fa')
            ).add_to(map_)

    return map_
