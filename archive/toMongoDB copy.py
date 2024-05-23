import random
import pandas as pd
from pymongo import MongoClient

data = pd.read_csv('./geocoded_locations.csv')

client = MongoClient('localhost', 27017)

db = client['test']

data['LowScore'] = 0.0
data['MeanScore'] = 0.0
data['HighScore'] = 0.0
data['Publication'] = 0

for i in range(3):
        collection = db['subject' + str(i)]

        for index, row in data.iterrows():
                scores = [round(random.random() * 100.0,1) for _ in range(random.randint(10,15))]
                average = round(sum(scores) / len(scores),1)
                scores.sort()
                p = random.randint(100, 100000)
                
                now = {'institution': row['Institution'], 'lowScore': scores[0], 'meanScore': average, 'highScore': scores[-1], 'publication': p}
                collection.insert_one(now)
                
                data.at[index, 'MeanScore'] = round((row['Publication'] * row['MeanScore'] + p * average) / (row['Publication'] + p), 1)
                data.at[index, 'Publication'] += p
                data.at[index, 'LowScore'] = scores[0] if i == 0 or scores[0] < row['LowScore'] else row['LowScore']
                data.at[index, 'HighScore'] = scores[-1] if i == 0 or scores[-1] > row['HighScore'] else row['HighScore']
                
                # print(now, "... done")
        print(data)

collection = db['institution']

for index, row in data.iterrows():
        now = {'institution': row['Institution'], 'latitude': row['Latitude'], 'longitude': row['Longitude'], 
                'lowScore': row['LowScore'], 'meanScore': row['MeanScore'], 'highScore': row['HighScore'], 'publication': row['Publication']}
        collection.insert_one(now)
        # print(now, "... done")


# 关闭连接
client.close()
