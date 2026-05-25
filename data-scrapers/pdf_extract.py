# This scripts downloads all pdfs from the given url. It checks for duplicates.

import os
import re
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_PAGE = "https://www.ncrb.gov.in/accidental-deaths-suicides-in-india-year-wise.html?year={year}"
BASE_SITE = "https://www.ncrb.gov.in"
DOWNLOAD_ROOT = "ncrb_crime_pdfs1"

START_YEAR = 1953
END_YEAR = 2022

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(HEADERS)

def safe_name(name: str) -> str:
    name = re.sub(r"[\\/*?:\"<>|]", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or "file"

def extract_pdf_links(year: int):
    pdf_links = []
    seen = set()
    url = BASE_PAGE.format(year=year)
    print(f"\nChecking year {year}: {url}")
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full_url = urljoin(BASE_SITE, href)
        if ".pdf" in href.lower() or href.lower().endswith(".pdf"):
            title = a.get_text(" ", strip=True)
            if not title:
                title = os.path.basename(href)
            key = (title, full_url)
            if key not in seen:
                seen.add(key)
                pdf_links.append((title, full_url))
    return pdf_links

def download_file(url: str, out_path: str):
    with session.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def main():
    os.makedirs(DOWNLOAD_ROOT, exist_ok=True)
    for year in range(END_YEAR, START_YEAR - 1, -1):
        try:
            links = extract_pdf_links(year)
            if not links:
                print(f"  No PDFs found for {year}")
                time.sleep(1)
                continue
            year_dir = os.path.join(DOWNLOAD_ROOT, str(year))
            os.makedirs(year_dir, exist_ok=True)
            print(f"  Found {len(links)} PDF(s)")
            for idx, (title, pdf_url) in enumerate(links, start=1):
                filename = safe_name(f"{idx:02d}_{title}.pdf")
                out_path = os.path.join(year_dir, filename)
                if os.path.exists(out_path):
                    print(f"    Skipping existing: {filename}")
                    continue
                print(f"    Downloading: {pdf_url}")
                try:
                    download_file(pdf_url, out_path)
                except Exception as e:
                    print(f"    Failed: {pdf_url} -> {e}")
                time.sleep(0.5)
        except Exception as e:
            print(f"  Error for year {year}: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()