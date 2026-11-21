"""Yöntem 1: requests + Beautiful Soup (statik sayfalar için hızlı ve basit)."""
import requests
from bs4 import BeautifulSoup

URL = "https://realpython.github.io/fake-jobs/"  # scraping alıştırması için hazırlanmış site


def parse_jobs(html, limit):
    """HTML'den ilan listesini çıkarır (Selenium scraper'ı da bu fonksiyonu kullanır)."""
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for card in soup.select("div.card-content")[:limit]:
        link = card.find_all("a")[-1]["href"]  # son link = "Apply" (ilan detayı)
        jobs.append({
            "title": card.select_one("h2.title").get_text(strip=True),
            "company": card.select_one("h3.company").get_text(strip=True),
            "location": card.select_one("p.location").get_text(strip=True),
            "link": link,
        })
    return jobs


def get_description(html):
    """İlan detay sayfasından açıklama metnini alır."""
    soup = BeautifulSoup(html, "html.parser")
    box = soup.select_one("div.content")
    return box.get_text(" ", strip=True) if box else ""


def scrape_with_bs(limit=5):
    html = requests.get(URL, timeout=15).text
    jobs = parse_jobs(html, limit)
    for job in jobs:
        detail = requests.get(job["link"], timeout=15).text
        job["description"] = get_description(detail)
    return jobs
