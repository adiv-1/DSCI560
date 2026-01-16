import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

url = "https://www.cnbc.com/world/?region=world"

os.makedirs("../data/raw_data", exist_ok=True)
os.makedirs("../data/processed_data", exist_ok=True)

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

browser.get(url)

time.sleep(3)

try:
    card = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='MarketCard-container']"))
    )
    time.sleep(2)
except:
    pass

try:
    news_list = browser.find_element(By.CSS_SELECTOR, "[class*='LatestNews-list']")
    for i in range(10):
        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", news_list)
        time.sleep(2)
except:
    pass

html = browser.page_source
browser.quit()

file = open("../data/raw_data/web_data.html", "w", encoding="utf-8")
file.write(html)
file.close()

file = open("../data/raw_data/web_data.html", "r", encoding="utf-8")
lines = file.readlines()
file.close()

for i in range(10):
    print(lines[i])
