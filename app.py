import re
from collections import Counter

import streamlit as st

from scraper import extract_text_from_pdf, fetch_job_text_from_url

st.set_page_config(
    page_title="Akıllı CV ve Pozisyon Eşleştirme Aracı",
    page_icon="📄",
    layout="wide",
)

STOPWORDS = {
    "ve", "ile", "icin", "için", "bir", "bu", "da", "de", "ta", "te", "den", "dan",
    "olan", "olarak", "gibi", "daha", "cok", "çok", "en", "hem", "veya", "ya", "ama",
    "ancak", "ise", "ki", "mi", "mu", "mı", "mü", "tum", "tüm", "her", "kadar",
    "sonra", "once", "önce", "uzere", "üzere", "gore", "göre", "sahip", "olmak",
    "alaninda", "alanında", "konusunda", "icin", "ile", "olan", "yer", "alan",
    "the", "and", "for", "with", "that", "this", "from", "are", "you", "your",
    "will", "have", "has", "our", "work", "team", "role", "job", "experience",
    "skills", "years", "using", "ability", "strong", "knowledge",
}


def tokenize(text: str) -> list[str]:
    normalized = text.lower()
    tokens = re.findall(r"[a-zçğıöşü0-9+#.-]{2,}", normalized)
    return [t for t in tokens if t not in STOPWORDS and not t.isdigit()]


def analyze_cv_and_job_local(cv_text: str, job_text: str) -> str:
    cv_tokens = tokenize(cv_text)
    job_tokens = tokenize(job_text)

    cv_set = set(cv_tokens)
    job_counts = Counter(job_tokens)

    # İlanda en sık geçen anlamlı kelimeleri önceliklendir
    prioritized_job_terms = [word for word, _ in job_counts.most_common(40)]
    if not prioritized_job_terms:
        prioritized_job_terms = sorted(set(job_tokens))

    matched_terms = [term for term in prioritized_job_terms if term in cv_set]
    missing_terms = [term for term in prioritized_job_terms if term not in cv_set]

    total_target = max(len(prioritized_job_terms), 1)
    score = round((len(matched_terms) / total_target) * 100)
    score = max(0, min(100, score))

    matched_preview = ", ".join(matched_terms[:15]) if matched_terms else "Belirgin ortak anahtar kelime bulunamadı."
    missing_preview = ", ".join(missing_terms[:15]) if missing_terms else "Öne çıkan eksik anahtar kelime görünmüyor."

    top_missing_for_cv = missing_terms[:6]
    if top_missing_for_cv:
        suggestions_lines = [
            f"- **{term}** kavramını gerçek proje veya deneyim maddelerinde geçerli bir bağlamda vurgula."
            for term in top_missing_for_cv
        ]
    else:
        suggestions_lines = [
            "- Mevcut projelerindeki somut çıktıları (kullanılan araçlar, teslim edilen özellikler, ekip/süreç katkısı) netleştir."
        ]

    interview_topics = missing_terms[:3] if missing_terms else matched_terms[:3]
    if not interview_topics:
        interview_topics = ["Proje mimarisi", "Problem çözme yaklaşımı", "Takım içi iletişim"]

    return f"""
### 1. Genel Uyum Skoru (0-100): **{score} / 100**
İlandaki öne çıkan **{len(prioritized_job_terms)}** anahtar terimden **{len(matched_terms)}** tanesi özgeçmiş metninde doğrudan eşleşti.

### 2. Güçlü Eşleşmeler
Öne çıkan ortak terimler: {matched_preview}

### 3. Eksik / Geliştirilmesi Gereken Alanlar
İlanda öne çıkıp özgeçmişte doğrudan geçmeyen terimler: {missing_preview}

### 4. CV İçin Somut İyileştirme Önerileri
{chr(10).join(suggestions_lines)}

### 5. Mülakat Hazırlık İpuçları
- **{interview_topics[0]}** başlığında yaptığın pratikleri ve örnek senaryoları net biçimde anlatmaya hazırlan.
- **{interview_topics[1] if len(interview_topics) > 1 else "Teknik Araçlar"}** ile ilgili hangi araçları kullandığını ve hangi zorlukları çözdüğünü somutlaştır.
- **{interview_topics[2] if len(interview_topics) > 2 else "Süreç & Teslimat"}** konusunda ilan gereksinimlerine nasıl uyum sağlayabileceğini kısa örneklerle açıkla.
""".strip()


st.title("📄 Akıllı CV ve Pozisyon Eşleştirme Aracı")
st.caption("API anahtarı gerektirmeden özgeçmiş ile pozisyon ilanını yerel metin analiziyle karşılaştırır.")

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
    if not final_cv_text:
        st.error("Lütfen bir CV dosyası yükle veya CV metni gir.")
    elif not final_job_text:
        st.error("Lütfen bir ilan URL'si çek veya ilan metni gir.")
    else:
        report = analyze_cv_and_job_local(
            cv_text=final_cv_text,
            job_text=final_job_text,
        )
        st.subheader("Analiz Sonucu")
        st.markdown(report)
