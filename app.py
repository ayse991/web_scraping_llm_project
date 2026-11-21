import os
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from google import genai

from scraper import extract_text_from_pdf, fetch_job_text_from_url

load_dotenv()

st.set_page_config(
    page_title="Akıllı CV ve Pozisyon Eşleştirme Aracı",
    page_icon="📄",
    layout="wide",
)


def resolve_api_key(sidebar_key: str) -> Optional[str]:
    key = (sidebar_key or "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    return key or None


def analyze_cv_and_job(
    api_key: str,
    cv_text: str,
    job_text: str,
    model_name: str = "gemini-3.8-flash",
) -> str:
    client = genai.Client(api_key=api_key)

    prompt = f"""
Sen deneyimli bir teknik işe alım uzmanı ve kariyer danışmanısın.
Aşağıdaki ÖZGEÇMİŞ (CV) ile POZİSYON İLANI metnini karşılaştır ve net, yapılandırılmış Türkçe bir analiz üret.

Şu 5 başlığı mutlaka kullan:
1. **Genel Uyum Skoru (0-100):** Puan ve kısa gerekçe.
2. **Güçlü Eşleşmeler:** İlanla örtüşen beceri, proje ve deneyimler.
3. **Eksik / Geliştirilmesi Gereken Alanlar:** İlanda geçen ama CV'de zayıf kalan veya hiç olmayan noktalar.
4. **CV İçin Somut İyileştirme Önerileri:** Madde madde ifadeleri güçlendirme ve anahtar kelime önerileri.
5. **Mülakat Hazırlık İpuçları:** Bu ilana özel öne çıkabilecek 3 odak konu.

--- ÖZGEÇMİŞ ---
{cv_text[:15000]}

--- POZİSYON İLANI ---
{job_text[:15000]}
"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
    return response.text or "Yanıt oluşturulamadı."


st.title("📄 Akıllı CV ve Pozisyon Eşleştirme Aracı")
st.caption("Özgeçmişin ile pozisyon ilanını karşılaştırarak uyum analizi ve geliştirme önerileri sunar.")

with st.sidebar:
    st.header("Ayarlar")
    api_key_input = st.text_input(
        "Gemini API Anahtarı",
        type="password",
        help="İstersen proje klasöründeki .env dosyasına GEMINI_API_KEY olarak da ekleyebilirsin.",
    )
    model_choice = st.selectbox(
        "Model Seçimi",
        options=["gemini-3.8-flash", "gemini-3.8-pro"],
        index=0,
    )

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("1. Özgeçmiş (CV)")
    uploaded_cv = st.file_uploader("PDF veya TXT dosyası yükle", type=["pdf", "txt"])
    cv_manual_text = st.text_area(
        "Veya CV metnini yapıştır",
        height=240,
        placeholder="Eğitim, projeler, teknik yetenekler, deneyimler...",
    )

    extracted_cv_text = ""
    if uploaded_cv is not None:
        if uploaded_cv.type == "application/pdf" or uploaded_cv.name.lower().endswith(".pdf"):
            try:
                extracted_cv_text = extract_text_from_pdf(uploaded_cv.getvalue())
            except Exception as exc:
                st.error(f"PDF okunurken hata oluştu: {exc}")
        else:
            extracted_cv_text = uploaded_cv.getvalue().decode("utf-8", errors="ignore")

    final_cv_text = cv_manual_text.strip() or extracted_cv_text.strip()

with col_right:
    st.subheader("2. Pozisyon İlanı")
    job_url = st.text_input(
        "İlan Sayfası URL'si (Opsiyonel)",
        placeholder="https://...",
    )
    job_manual_text = st.text_area(
        "İlan metnini yapıştır (URL çekemezse buradaki metin kullanılır)",
        height=240,
        placeholder="Aranan nitelikler, sorumluluklar, gereksinimler...",
    )

    if job_url.strip() and st.button("URL'den İlan Metnini Çek"):
        try:
            fetched_text = fetch_job_text_from_url(job_url.strip())
            st.session_state["fetched_job_text"] = fetched_text
            st.success("İlan metni başarıyla çekildi.")
        except Exception as exc:
            st.warning(f"Sayfa doğrudan çekilemedi ({exc}). İlan metnini sağdaki alana yapıştırarak devam edebilirsin.")

    final_job_text = (
        job_manual_text.strip()
        or st.session_state.get("fetched_job_text", "").strip()
    )

st.divider()

if st.button("Eşleştirme Analizi Yap", type="primary"):
    active_key = resolve_api_key(api_key_input)
    if not active_key:
        st.error("Sol menüdeki kutuya Gemini API anahtarını gir veya `.env` dosyasına `GEMINI_API_KEY` tanımla.")
    elif not final_cv_text:
        st.error("Lütfen bir CV dosyası yükle veya CV metni gir.")
    elif not final_job_text:
        st.error("Lütfen bir ilan URL'si çek veya ilan metni gir.")
    else:
        with st.spinner("CV ve pozisyon ilanı analiz ediliyor..."):
            try:
                report = analyze_cv_and_job(
                    api_key=active_key,
                    cv_text=final_cv_text,
                    job_text=final_job_text,
                    model_name=model_choice,
                )
                st.subheader("Analiz Sonucu")
                st.markdown(report)
            except Exception as exc:
                st.error(f"Analiz sırasında bir hata oluştu: {exc}")
