import os
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd

# Get the absolute path of wards.geojson
file_path = os.path.join(os.path.dirname(__file__), "..", "wards.geojson")

# Load ward data
ward_data = gpd.read_file(file_path)  # Use the correct path

def get_ward(lat, lon):
    try:
        user_location = Point(lon, lat)  # Shapely Point for geospatial comparison

        # Find the matching ward by checking which polygon contains the point
        ward_match = ward_data[ward_data.geometry.contains(user_location)]

        if not ward_match.empty:
            ward_name = ward_match.iloc[0]["WARD_NO"]  # Adjust column name if different
            print(f"Matched Ward: {ward_name}")  # Debugging
            return ward_name
        else:
            print("❌ No matching ward found")
            return "Ward not found"
    except Exception as e:
        print(f"Error in get_ward: {e}")
        return "Error"
