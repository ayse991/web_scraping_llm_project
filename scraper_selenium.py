"""Yöntem 2: Selenium (gerçek tarayıcı açar; JavaScript ile yüklenen sayfalar için gerekli)."""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scraper_bs import URL, parse_jobs, get_description


def scrape_with_selenium(limit=5):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")           # pencere açmadan çalış
    options.add_argument("--no-sandbox")             # GitHub ortamı için gerekli
    options.add_argument("--disable-dev-shm-usage")  # GitHub ortamı için gerekli
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(URL)
        # İlan kartları yüklenene kadar bekle
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.card-content"))
        )
        jobs = parse_jobs(driver.page_source, limit)  # sayfa kaynağını Beautiful Soup ile ayrıştır
        for job in jobs:
            driver.get(job["link"])                   # her ilanın detay sayfasına git
            job["description"] = get_description(driver.page_source)
        return jobs
    finally:
        driver.quit()

