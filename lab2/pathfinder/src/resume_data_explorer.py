import requests
import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract
import os
import re
import pandas as pd

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

def extract_section(text, section_name):
    pattern = rf'{section_name}(.*?)(?=\n[A-Z][A-Z\s]+\n|$)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

def extract_education(text):
    education_section = extract_section(text, 'EDUCATION')
    universities = re.findall(r'([A-Z][A-Za-z\s&]+(?:Institute|University|College|School)[^\n]*)', education_section)
    degrees = re.findall(r'(M\.S\.|B\.S\.|B\.Sc\.|Ph\.D\.|MBA|Master|Bachelor)[^\n]*', education_section)
    dates = re.findall(r'(\d{4}\s*[-–]\s*(?:\d{4}|Present))', education_section)
    
    return {
        'universities': ', '.join(universities),
        'degrees': ', '.join(degrees),
        'graduation_dates': ', '.join(dates)
    }

def extract_experience(text):
    experience_section = extract_section(text, 'EXPERIENCE')
    companies = re.findall(r'^([A-Z][A-Za-z\s&\.]+)\s+[A-Z][a-z]', experience_section, re.MULTILINE)
    job_titles = re.findall(r'^([A-Z][A-Za-z\s/]+(?:Engineer|Manager|Analyst|Intern|Developer|Operations|Strategy|Specialist|Consultant)[^\n]*)', experience_section, re.MULTILINE)
    dates = re.findall(r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s*[-–]\s*(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|Present))', experience_section)
    bullets = re.findall(r'•\s*([^\n•]+)', experience_section)
    
    return {
        'companies': ', '.join(companies),
        'job_titles': ', '.join(job_titles),
        'experience_dates': ', '.join(dates),
        'num_bullet_points': len(bullets)
    }

resumes = []
current_resume_text = []
current_name = None

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages):
        if page_num == 0:
            continue
        
        text = page.extract_text()
        
        if not text or len(text.strip()) < 50:
            images = convert_from_bytes(pdf_bytes, first_page=page_num+1, last_page=page_num+1)
            if images:
                text = pytesseract.image_to_string(images[0])
        
        lines = text.split('\n')
        first_line = lines[0].strip() if lines else ""
        name_match = re.match(r'^[A-Z][A-Z\s\.]+$', first_line)
        
        if name_match and len(first_line.split()) >= 2:
            if current_resume_text and current_name:
                full_text = '\n'.join(current_resume_text)
                education = extract_education(full_text)
                experience = extract_experience(full_text)
                
                resumes.append({
                    'name': current_name,
                    'full_text': full_text,
                    **education,
                    **experience
                })
            
            current_name = first_line
            current_resume_text = [text]
        else:
            current_resume_text.append(text)

if current_resume_text and current_name:
    full_text = '\n'.join(current_resume_text)
    education = extract_education(full_text)
    experience = extract_experience(full_text)
    
    resumes.append({
        'name': current_name,
        **education,
        **experience
    })

df = pd.DataFrame(resumes)
csv_path = os.path.join(data_dir, 'sdm_resumes_structured.csv')
df.to_csv(csv_path, index=False)
