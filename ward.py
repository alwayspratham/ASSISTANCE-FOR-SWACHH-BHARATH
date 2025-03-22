import json

# Load the GeoJSON file
with open("wards.geojson", "r", encoding="utf-8") as file:
    geojson_data = json.load(file)

# Function to round coordinates
def round_coordinates(feature):
    if "geometry" in feature and "coordinates" in feature["geometry"]:
        coords = feature["geometry"]["coordinates"]

        def round_recursive(coordinates):
            if isinstance(coordinates[0], list):  # If nested list, recurse
                return [round_recursive(coord) for coord in coordinates]
            else:  # If individual coordinate (lon, lat)
                return [round(coordinates[0], 2), round(coordinates[1], 2)]

        feature["geometry"]["coordinates"] = round_recursive(coords)

# Apply rounding to all features
for feature in geojson_data.get("features", []):
    round_coordinates(feature)

# Save the updated GeoJSON file
with open("wards_rounded.geojson", "w", encoding="utf-8") as file:
    json.dump(geojson_data, file, indent=4)

print("✅ All coordinates rounded to two decimal places and saved in 'wards_rounded.geojson'.")
