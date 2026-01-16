import os
import csv
from bs4 import BeautifulSoup

file = open("../data/raw_data/web_data.html", "r", encoding="utf-8")
content = file.read()
file.close()

soup = BeautifulSoup(content, 'html.parser')

stocks = []

cards = soup.find_all('a', class_=lambda x: x and 'MarketCard-container' in str(x))

if len(cards) == 0:
    cards = soup.find_all(class_=lambda x: x and 'MarketCard' in str(x))

for card in cards:
    sym = card.find(class_=lambda x: x and 'MarketCard-symbol' in str(x))
    pos = card.find(class_=lambda x: x and 'MarketCard-stockPosition' in str(x))
    chg = card.find(class_=lambda x: x and 'MarketCard-change' in str(x))
    
    sym_text = ""
    pos_text = ""
    chg_text = ""
    
    if sym:
        sym_text = sym.get_text(strip=True)
    if pos:
        pos_text = pos.get_text(strip=True)
    if chg:
        chg_text = chg.get_text(strip=True)
    
    if sym_text != "":
        temp = []
        temp.append(sym_text)
        temp.append(pos_text)
        temp.append(chg_text)
        stocks.append(temp)

file = open("../data/processed_data/market_data.csv", "w", newline="", encoding="utf-8")
csv_writer = csv.writer(file)
csv_writer.writerow(["marketCard_symbol", "marketCard_stockPosition", "marketCard_changePct"])
file.close()

file = open("../data/processed_data/market_data.csv", "a", newline="", encoding="utf-8")
csv_writer = csv.writer(file)
for temp in stocks:
    csv_writer.writerow(temp)
file.close()

articles = []

items = soup.find_all('li', class_=lambda x: x and 'LatestNews-item' in str(x))

for i in items:
    time = i.find(class_=lambda x: x and 'LatestNews-timestamp' in str(x))
    heading = i.find(class_=lambda x: x and 'LatestNews-headline' in str(x))
    url = i.find('a', class_=lambda x: x and 'LatestNews-headline' in str(x))
    
    time_str = ""
    heading_str = ""
    url_str = ""
    
    if time:
        time_str = time.get_text(strip=True)
    if heading:
        heading_str = heading.get_text(strip=True)
    if url:
        url_str = url.get('href', "")
    
    if heading_str != "":
        if time_str != "":
            if heading_str.startswith(time_str):
                heading_str = heading_str.replace(time_str, "", 1)
                heading_str = heading_str.strip()
        
        temp = []
        temp.append(time_str)
        temp.append(heading_str)
        temp.append(url_str)
        articles.append(temp)

file = open("../data/processed_data/news_data.csv", "w", newline="", encoding="utf-8")
csv_writer = csv.writer(file)
csv_writer.writerow(["LatestNews_timestamp", "title", "link"])
file.close()

file = open("../data/processed_data/news_data.csv", "a", newline="", encoding="utf-8")
csv_writer = csv.writer(file)
for temp in articles:
    csv_writer.writerow(temp)
file.close()
