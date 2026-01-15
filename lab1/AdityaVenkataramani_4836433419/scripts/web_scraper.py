import os
import requests

link = "https://www.cnbc.com/world/?region=world"

os.makedirs("../data/raw_data", exist_ok = True)
os.makedirs("../data/processed_data", exist_ok = True)

headers = {"User-Agent": "Mozilla/5,0"}

raw_data = requests.get(link, headers = headers, timeout = 10)

with open("../data/raw_data/web_data.html", "w", encoding = "utf-8") as f:
    f.write(raw_data.text)

with open("../data/raw_data/web_data.html", "r", encoding = "utf-8") as f:
    lines = f.readlines()
    for i in range(10):
        print(lines[i])
