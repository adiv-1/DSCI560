from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import unicodedata

def clean_text(text):
    if not text:
        return ""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").strip()

def parse_url(url, csv_output):
    # 1) Launch headless browser
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    browser.get(url)
    
    # wait for content to render
    time.sleep(3)
    
    # 2) Get page HTML
    html = browser.page_source
    soup = BeautifulSoup(html, "lxml")
    
    browser.quit()
    
    # 3) Extract text blocks
    rows = []
    current_h1 = None
    current_h2 = None
    current_h3 = None
    
    for el in soup.find_all(["h1", "h2", "h3", "p", "li"]):
    
        tag = el.name
        text = clean_text(el.get_text(separator=" ", strip=True))
    
        if not text:
            continue
    
        if tag == "h1":
            current_h1 = text
            current_h2 = None
            current_h3 = None
    
        elif tag == "h2":
            current_h2 = text
            current_h3 = None
    
        elif tag == "h3":
            current_h3 = text
    
        else:
            rows.append({
                "section_h1": current_h1,
                "section_h2": current_h2,
                "section_h3": current_h3,
                "content_type": tag,
                "text": text
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(csv_output, index=False)
    
    print(f"Extracted {len(df)} rows of text data")

url_list = [
    "https://findtreatment.gov/what-to-expect/treatment",
    "https://findtreatment.gov/what-to-expect/payment",
    "https://findtreatment.gov/what-to-expect/addiction",
    "https://findtreatment.gov/what-to-expect/mental-health"
]

output_list = [
    "../data/findtreatment_treatment.csv",
    "../data/findtreatment_payment.csv",
    "../data/findtreatment_addiction.csv",
    "../data/findtreatment_mental-health.csv"
]

for i in range(0, len(url_list)):
    parse_url(url_list[i], output_list[i])