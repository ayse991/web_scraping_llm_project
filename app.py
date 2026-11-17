import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Web Scraping & LLM Asistanı",
    page_icon="🤖",
    layout="centered"
)

st.title("🌐 Akıllı İçerik & LLM Analiz Asistanı")
st.write("İster bir web sitesi linki ver, ister metni doğrudan yapıştır; Gemini senin için anında analiz etsin!")

# Sidebar - API Anahtarı
st.sidebar.header("Ayarlar")
api_key = st.sidebar.text_input(
    "Gemini API Key", 
    type="password", 
    value=st.secrets.get("GOOGLE_API_KEY", ""),
    help="Google AI Studio'dan aldığınız API anahtarınızı buraya girebilirsiniz."
)

# Girdi Yöntemi Seçimi
input_mode = st.radio("İşlem Türü Seç:", ["🔗 Web Sitesi URL'si", "✍️ Doğrudan Metin / İçerik Yapıştır"])

text_content = ""

if input_mode == "🔗 Web Sitesi URL'si":
    url = st.text_input("Taranacak Web Sitesi URL'si:", placeholder="https://example.com")
    if url and st.button("Veriyi Çek ve Analiz Et", type="primary"):
        try:
            with st.spinner("Web sitesinden veriler kazınıyor..."):
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
                    script_or_style.decompose()
                    
                text_content = soup.get_text(separator=' ', strip=True)[:12000]
                st.success("Veriler başarıyla kazındı!")
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")

else:
    text_content = st.text_area("Analiz edilmesini istediğin metni buraya yapıştır:", placeholder="Örn: ÖSYM 2024 taban puanları ve sıralamaları hakkında kopyaladığın yazılar...")
    if text_content and st.button("Metni Analiz Et", type="primary"):
        pass # Metin zaten hazır

# Ortak LLM Analiz Kısmı
if text_content and api_key:
    if st.button("Gemini ile Analiz Et", type="primary") or input_mode == "✍️ Doğrudan Metin / İçerik Yapıştır":
        # Eğer butonlar çakışmasın diye kontrol ekleyelim
        pass

# Daha sade ve akışkan bir tetikleme için buton mantığı:
if st.button("🤖 Gemini ile Analiz Başlat", type="primary"):
    if not api_key:
        st.error("Lütfen sol menüden Gemini API anahtarını gir.")
    elif not text_content:
        st.warning("Lütfen üstteki sekmelerden bir URL gir veya metin yapıştır.")
    else:
        with st.spinner("Gemini LLM içerigi analiz ediyor..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Aşağıdaki içeriği analiz et:
                1. Bu metin/sayfa ne hakkında? Kısa bir özet geç.
                2. Önemli başlıkları ve ana bilgileri maddeler halinde çıkar.
                
                İçerik:
                {text_content}
                """
                
                prediction = model.generate_content(prompt)
                
                st.subheader("🤖 Analiz Sonucu")
                st.markdown(prediction.text)
            except Exception as e:
                st.error(f"Analiz sırasında bir hata oluştu: {e}")
