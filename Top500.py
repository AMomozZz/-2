import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.caifuzhongwen.com/fortune500/paiming/global500/2023_%E4%B8%96%E7%95%8C500%E5%BC%BA.htm"

response = requests.get(url)
response.encoding = 'utf-8'

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table', {'id': 'ui-table2'})
    
    headers = table.find('thead').text.strip().split('\n')[:2]
    
    rows = []
    for tr in table.find_all('tr')[1:]:
        cells = tr.find_all('td')
        row = (int(cells[0].find('i', {'class':'rank'}).text.strip()), cells[1].text.strip())
        rows.append(row)
        
        print(rows)
        
    df_fortune500 = pd.DataFrame(rows, columns=headers)
    
    print(df_fortune500.head())
else:
    print("Failed to fetch the webpage content")
