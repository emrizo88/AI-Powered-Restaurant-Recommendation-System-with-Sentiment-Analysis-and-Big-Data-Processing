import pandas as pd
import json
from math import radians, sin, cos, sqrt, atan2

# Load the Yelp business dataset (business.json file)
file_path = "D:\Profesional\IRS_Semestres\IRS_Semestre_7\Intro_BigData\Dataset\yelp_academic_dataset_business.json"  # Update with your file path

# Load the business data into a pandas DataFrame
business_data = []
with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        business_data.append(json.loads(line))

df_business = pd.DataFrame(business_data)

# Check categories to see if 'Restaurant' is included
df_business['categories'] = df_business['categories'].fillna('')

# Filter the dataset to include only restaurants
df_restaurants = df_business[df_business['categories'].str.contains('Restaurant', na=False)]

# Additionally, filter for only Philadelphia-based restaurants
df_philadelphia_restaurants = df_restaurants[df_restaurants['city'].str.lower() == 'philadelphia']

# Define the location for Philadelphia (latitude and longitude)
philadelphia_lat = 39.9526
philadelphia_lon = -75.1652

# Haversine function to calculate distance in kilometers
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Calculate the distance for each restaurant in Philadelphia
df_philadelphia_restaurants['distance_km'] = df_philadelphia_restaurants.apply(
    lambda row: haversine(philadelphia_lat, philadelphia_lon, row['latitude'], row['longitude']),
    axis=1
)

# Save ALL the relevant columns for Philadelphia restaurants
df_philadelphia_restaurants.to_csv('philadelphia_restaurants_with_distance.csv', index=False)

# Display the first few rows of the dataset for verification
print(df_philadelphia_restaurants[['name', 'latitude', 'longitude', 'stars', 'review_count', 'distance_km']].head())
