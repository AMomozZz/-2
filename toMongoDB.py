import pandas as pd
from pymongo import MongoClient
from geopy.geocoders import Nominatim

client = MongoClient('localhost', 27017)
geolocator = Nominatim(user_agent="institution_geocoder")

def get_privacy_without_numbers(province):
        lst = province.split(' ')
        r = [word for word in lst if not any(char.isdigit() for char in word)]
        return ' '.join(r)

def geocode_with_cache(location_names):
        if type(location_names) is str:
                lst = location_names.split(';')
                r = []
                for location_name in lst:
                        if '), ' in location_name:
                                name = location_name.split('(')[0].replace(' ', '')
                                location_name = location_name.split('), ')[1].split('.')[0]
                                country = location_name.split(', ')[-1].split(' ')[-1]
                                if len(location_name.split(', ')) >= 2:
                                        province = get_privacy_without_numbers(location_name.split(', ')[-2])
                                        location_name = province + ', ' + country
                                else:
                                        province = ''
                                        location_name = country
                                # print(f"{location_name},", end='')
                                location = geolocator.geocode(location_name, timeout=10)
                                if location:
                                        # print(f"{location.latitude},{location.longitude}")
                                        r.append([name, location.latitude, location.longitude])
                                # else:
                                        # print(f"{location_name}")
                                        # print()
                        # else: print(f"{location_name}")
                return r
        else:
                # print(f"{location_names},", end='')
                # print(f"{float('nan')},{float('nan')}")
                return []

data = pd.read_csv('./三_量子传感_2_2107条.csv')

# non_nan_counts_AB = data[['TI', 'RP', 'AF']].count()
# print(non_nan_counts_AB)

client.drop_database('test2')
db = client['test2']
collection = db['paper']

for index, row in data.iterrows():
        lst = geocode_with_cache(row['RP'])
        for i in lst:
                one = collection.find_one({"person": i[0]})

                if one:
                        current_list = one.get("article")
                        
                        new_element = {
                                        'article_name': row['TI'], 'isbn': row['BN'],
                                        'author': row['AF'], 'language': row['LA'], 'type': row['DT']
                                        }
                        current_list.append(new_element)
                        
                        update_result = collection.update_one(
                                {"person": i[0]},
                                {"$set": {"article": current_list}}
                        )
                        print(i[0], "... update\n")
                else:
                        now = {
                                'person': i[0],
                                'location': (i[1], i[2]),
                                'article': [{
                                        'article_name': row['TI'], 'isbn': row['BN'],
                                        'author': row['AF'], 'language': row['LA'], 'type': row['DT']
                                        }]
                                }
                        collection.insert_one(now)
                        print(i[0], "... done\n")

client.close()
