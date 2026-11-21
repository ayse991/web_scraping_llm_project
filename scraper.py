from io import BytesIO
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """PDF dosyasından sayfa sayfa düz metin çıkarır."""
    reader = PdfReader(BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def fetch_job_text_from_url(url: str, max_chars: int = 12000) -> str:
    """İlan URL'sinden sayfa metnini çeker ve fazla boşlukları temizler."""
    cleaned_url = url.strip()
    if not cleaned_url.startswith(("http://", "https://")):
        raise ValueError("URL 'http://' veya 'https://' ile başlamalıdır.")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(cleaned_url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    raw_text = soup.get_text(separator="\n")
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    return "\n".join(lines)[:max_chars]
