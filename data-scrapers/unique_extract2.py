# Uses playwright to change the language of the site to English
# This script extracts PDF links from the given url. It also maintains a record of downloaded links to avoid duplicates across different sites.

import os
import re
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_PAGE = "https://www.ncrb.gov.in/crime-in-india-year-wise.html?year={year}"
BASE_SITE = "https://www.ncrb.gov.in"
DOWNLOAD_ROOT = "ncrb_crime_pdfs/crime-in-india"

START_YEAR = 1953
END_YEAR = 2024

LINKS_FILE = "links.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(HEADERS)

def load_links():
    if not os.path.exists(LINKS_FILE):
        return set()
    with open(LINKS_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_link(url):
    with open(LINKS_FILE, "a") as f:
        f.write(url + "\n")

all_links = load_links()

def safe_name(name: str) -> str:
    name = re.sub(r"[\\/*?:\"<>|]", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or "file"

def extract_pdf_links(page, year):
    url = BASE_PAGE.format(year=year)
    print(f"\nChecking year {year}: {url}")
    page.goto(url, timeout=60000)
    page.wait_for_load_state("networkidle")
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full_url = urljoin(BASE_SITE, href)
        if ".pdf" in href.lower():
            title = a.get_text(" ", strip=True)
            if not title:
                title = os.path.basename(href)
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
    print(f"Loaded {len(all_links)} existing links")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.ncrb.gov.in")
        page.wait_for_load_state("networkidle")
        try:
            page.click("text=English", timeout=5000)
            page.wait_for_load_state("networkidle")
            print("Switched to English")
        except:
            print("English button not found / already English")
        for year in range(END_YEAR, START_YEAR - 1, -1):
            try:
                links = extract_pdf_links(page, year)
                if not links:
                    print(f"  No PDFs found for {year}")
                    continue
                year_dir = os.path.join(DOWNLOAD_ROOT, str(year))
                os.makedirs(year_dir, exist_ok=True)
                print(f"  Found {len(links)} PDF(s)")
                idx = 1
                for title, pdf_url in links:
                    if pdf_url in all_links:
                        print(f"    Skipping duplicate")
                        continue
                    all_links.add(pdf_url)
                    save_link(pdf_url)
                    filename = safe_name(f"{idx:02d}_{title}.pdf")
                    out_path = os.path.join(year_dir, filename)
                    if os.path.exists(out_path):
                        print(f"    Already exists: {filename}")
                        continue
                    print(f"    Downloading: {pdf_url}")
                    try:
                        download_file(pdf_url, out_path)
                        idx += 1
                    except Exception as e:
                        print(f"    Failed: {e}")
                    time.sleep(0.3)
            except Exception as e:
                print(f"  Error for year {year}: {e}")
        browser.close()
    print(f"\nTotal unique links stored: {len(all_links)}")

if __name__ == "__main__":
    main()