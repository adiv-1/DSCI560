import csv
import sys
import requests
import re
from bs4 import BeautifulSoup
from io import BytesIO
from PyPDF2 import PdfReader

"""
1) CSV Scraping
"""

csv_path = "../data/building_permits.csv"
preview_rows = 5

with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames or []

    print(f"First {preview_rows} rows:")
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(columns)

    missing_by_col = {c: 0 for c in columns}
    rows_printed = 0

    for row in reader:
        if rows_printed < preview_rows:
            writer.writerow([row.get(c, "") for c in columns])
            rows_printed += 1

        for c in columns:
            if not (row.get(c, "") or "").strip():
                missing_by_col[c] += 1

print("\nMissing values per column (non-zero):")
for col, cnt in sorted(missing_by_col.items(), key=lambda kv: kv[1], reverse=True):
    if cnt > 0:
        print(f"{col}: {cnt}")


"""
2) HTML Scraping
"""

html_url = "https://homerepairforum.com/"

# Extract (title, link) from the homepage
resp = requests.get(html_url, timeout=30)
resp.raise_for_status()
html = resp.text

soup = BeautifulSoup(html, "html.parser")

items = []
seen = set()

# Get links on page
for a in soup.select("a[href]"):
    title = a.get_text(" ", strip=True)
    href = (a.get("href") or "").strip()
    if not title or not href:
        continue

    if href.startswith("http://") or href.startswith("https://"):
        link = href
    elif href.startswith("/"):
        link = html_url + href
    else:
        link = html_url + "/" + href

    # Keep only actual forum links to (avoids Sign Up, Login, etc.)
    if "/forum/" not in link:
        continue

    key = (title, link)
    if key not in seen:
        seen.add(key)
        items.append(key)

print(f"URL: {html_url}")
print(f"Found {len(items)} links with text\n")

for title, link in items[:5]:
    print(f"- {title}\n  {link}")

# Save to CSV
html_output_path = "../data/repair_forum.csv"
with open(html_output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["title", "link"])
    writer.writerows(items)

print(f"\nSaved: {html_output_path}")


"""
3) PDF Scraping
"""

pdf_url = "https://housing.lacity.gov/wp-content/uploads/2021/08/TAH-Tenant-Request-For-Repair-Maintenance-Form.pdf"

# Download pdf
resp = requests.get(pdf_url, timeout=30)
resp.raise_for_status()
pdf_bytes = resp.content

# Extract text
reader = PdfReader(BytesIO(pdf_bytes))
text = "\n".join((p.extract_text() or "") for p in reader.pages)
text = re.sub(r"[ \t]+", " ", text).strip()

def extract_paragraph(needle):
    m = re.search(rf"({re.escape(needle)}.*?)(?:\n\s*\n|$)", text, flags=re.IGNORECASE | re.DOTALL)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

row = {
    # Fields
    "landlord_agent_name": "",
    "tenant_name": "",
    "address": "",
    "unit_number": "",
    "repair_description": "",
    "tenant_signature": "",
    "tenant_date": "",
    "received_by": "",
    "received_name_print": "",
    "received_signature": "",
    "received_date": "",
    # Legal paragraphs
    "lamc_45_33_2": extract_paragraph("L.A.M.C. 45.33(2)"),
    "ca_civil_code_1954_d1": extract_paragraph("California Civil Code 1954(d)1"),
    "lamc_45_35_f": extract_paragraph("Pursuant to L.A.M.C 45.35(F)"),
    # Raw text
    "raw_text": text,
}

# Write to CSV
pdf_output_path = "../data/maintenance_form.csv"
with open(pdf_output_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(row.keys()))
    w.writeheader()
    w.writerow(row)

print("Saved:", pdf_output_path)
