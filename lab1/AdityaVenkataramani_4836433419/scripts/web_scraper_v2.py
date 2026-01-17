import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url = "https://www.cnbc.com/world/?region=world"

os.makedirs("../data/raw_data_v2", exist_ok=True)
os.makedirs("../data/processed_data_v2", exist_ok=True)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")
browser = webdriver.Chrome(service=service, options=options)

browser.get(url)
time.sleep(3)

WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='MarketCard-container']")))

html_news = browser.page_source
browser.quit()

with  open("../data/raw_data_v2/web_data.html", "w", encoding="utf-8") as f:
    f.write(html_news)

file = open("../data/raw_data_v2/web_data.html", "r", encoding="utf-8")
lines = file.readlines()
file.close()

for i in range(10):
    print(lines[i])
