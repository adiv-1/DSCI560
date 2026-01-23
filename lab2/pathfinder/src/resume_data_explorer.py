import requests
import pdfplumber
from pdf2image import convert_from_path
import os
import re
import pytesseract

pdf_url = "https://sdm.mit.edu/wp-content/uploads/2017/04/2017-Resume-Book-for-Web-SDM.pdf"

response = requests.get(pdf_url)
response.raise_for_status()

pdf_bytes = response.content

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(parent_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

pdf_path = os.path.join(data_dir, 'sdm_resumes.pdf')
with open(pdf_path, 'wb') as f:
    f.write(pdf_bytes)

