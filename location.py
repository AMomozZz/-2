import pandas as pd
from geopy.geocoders import Nominatim

data = pd.read_csv('./ScimagoIR 2024 - Overall Rank.csv')

institutions = data['Institution'].tolist()

geolocator = Nominatim(user_agent="my_geocoder_app")

print(geolocator.geocode("PQ H3A 2A7, Canada"))

exit()

def geocode_with_cache(location_name, i):
        location = geolocator.geocode(location_name, timeout=10)
        if location:
                with open('geocoded_locations.csv', 'a') as file:
                        file.write(f'"{location_name}",{location.latitude},{location.longitude}\n')
                print(f"{i}, {location_name},{location.latitude},{location.longitude}")

for i in range(len(institutions)):
        geocode_with_cache(institutions[i], i)
