import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

url = "https://www.onetonline.org/find/career?c=0"

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', class_='table')
tbody = table.find('tbody')
rows = tbody.find_all('tr')

data = []

for row in rows:
    cells = row.find_all('td')
    
    if len(cells) >= 4:
        career_cluster = cells[0].text.strip()
        sub_cluster = cells[1].text.strip()
        code = cells[2].text.strip()
        
        occupation_cell = cells[3]
        occupation_link = occupation_cell.find('a')
        
        if occupation_link:
            occupation_name = occupation_link.text.strip()
            occupation_url = occupation_link.get('href', '')
            
            if occupation_url and not occupation_url.startswith('http'):
                occupation_url = 'https://www.onetonline.org' + occupation_url
            
            data.append({
                'career_cluster': career_cluster,
                'sub_cluster': sub_cluster,
                'code': code,
                'occupation': occupation_name,
                'url': occupation_url
            })

df = pd.DataFrame(data)

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(parent_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

csv_path = os.path.join(data_dir, 'onet_careers.csv')
df.to_csv(csv_path, index=False)

print(df.head())