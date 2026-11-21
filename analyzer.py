"""LLM (Google Gemini) ile CV - ilan uyum analizi."""
import json
import os
import requests

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

PROMPT = """Sen deneyimli bir işe alım uzmanısın.
Aşağıdaki CV ile iş ilanını karşılaştır ve uyumu 0-100 arası bir yüzde olarak puanla.
Sadece şu JSON formatında cevap ver:
{{"uyum_yuzdesi": <sayı>, "eslesen_beceriler": [..], "eksik_beceriler": [..], "ozet": "<2 cümlelik Türkçe yorum>"}}

İŞ İLANI:
Pozisyon: {title}
Açıklama: {description}

CV:
{cv}
"""


def analyze(cv_text, job):
    api_key = os.environ["GEMINI_API_KEY"]
    prompt = PROMPT.format(title=job["title"], description=job["description"], cv=cv_text)
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
    }
    r = requests.post(API_URL, params={"key": api_key}, json=body, timeout=60)
    r.raise_for_status()
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)
