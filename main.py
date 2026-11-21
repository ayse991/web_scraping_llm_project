"""CV - İş İlanı Uyum Analizi
CV her zaman elle girilir. İlan ise elle girilebilir ya da web scraping ile toplanır.
Çalıştırma: python main.py
"""
from scraper_bs import scrape_with_bs
from scraper_selenium import scrape_with_selenium
from analyzer import analyze


def read_multiline(title):
    """Kullanıcıdan çok satırlı metin alır. Yapıştırdıktan sonra yeni satıra BITTI yaz."""
    print(f"\n{title} (yapıştırın, sonra yeni satıra BITTI yazıp Enter'a basın):")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "BITTI":
            break
        lines.append(line)
    return "\n".join(lines)


def main():
    # 1) CV'yi elle gir
    cv_text = read_multiline("CV metnini girin")

    # 2) İlan kaynağını seç
    print("\nİlan kaynağı:\n 1) Elle gir\n 2) Beautiful Soup ile topla\n 3) Selenium ile topla")
    secim = input("Seçiminiz (1/2/3): ").strip()

    if secim == "2":
        jobs = scrape_with_bs(limit=5)
    elif secim == "3":
        jobs = scrape_with_selenium(limit=5)
    else:
        baslik = input("\nPozisyon adı: ")
        aciklama = read_multiline("İlan metnini girin")
        jobs = [{"title": baslik, "company": "-", "description": aciklama}]
    print(f"\n{len(jobs)} ilan analiz ediliyor...\n")

    # 3) LLM ile analiz
    results = []
    for job in jobs:
        res = analyze(cv_text, job)
        results.append((job, res))

    # 4) Uyum oranına göre sırala ve yazdır
    results.sort(key=lambda x: x[1]["uyum_yuzdesi"], reverse=True)
    for job, res in results:
        print("=" * 50)
        print(f"{job['title']} ({job['company']})  ->  %{res['uyum_yuzdesi']} uyum")
        print("Eşleşen beceriler:", ", ".join(res["eslesen_beceriler"]))
        print("Eksik beceriler  :", ", ".join(res["eksik_beceriler"]))
        print("Özet:", res["ozet"])


if __name__ == "__main__":
    main()
