import streamlit as st
from bs4 import BeautifulSoup
import google.generativeai as genai
import urllib.parse
import requests

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Akıllı Web Arama & LLM Asistanı",
    page_icon="🤖",
    layout="centered"
)

st.title("🔍 Akıllı Web Arama & LLM Analiz Asistanı")
st.write("Aramak istediğin kelimeyi yaz, uygulama web'de arasın ve Gemini senin için anında analiz etsin!")

# Sidebar - API Anahtarı
st.sidebar.header("Ayarlar")
api_key = st.sidebar.text_input(
    "Gemini API Key", 
    type="password", 
    value=st.secrets.get("GOOGLE_API_KEY", ""),
    help="Google AI Studio'dan aldığınız API anahtarınızı buraya girebilirsiniz."
)

# Arama Kutusu
query = st.text_input("Ne aramak veya analiz ettirmek istiyorsun?", placeholder="Örn: ösym 2024 sıralama, python mülakat soruları...")

if st.button("Web'de Ara ve Analiz Et", type="primary"):
    if not api_key:
        st.error("Lütfen sol menüden Gemini API anahtarını gir.")
    elif not query:
        st.warning("Lütfen aramak istediğin bir kelime veya konu yaz.")
    else:
        try:
            with st.spinner("Web'de aranıyor ve veriler toplanıyor..."):
                # DuckDuckGo üzerinden arama yapıp sonuçları çekme (API anahtarı gerektirmeyen pratik yöntem)
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                
                response = requests.get(search_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Arama sonuçlarındaki başlık ve snippet'leri (özetleri) topla
                results = []
                for a in soup.find_all('a', class_='result__snippet', limit=5):
                    results.append(a.get_text(strip=True))
                
                # Eğer snippet bulunamazsa genel metni al
                if not results:
                    for a in soup.find_all('a', class_='result__title', limit=5):
                        results.append(a.get_text(strip=True))
                        
                combined_text = " ".join(results)
                
                if not combined_text:
                    st.warning("Aradığın konuyla ilgili web üzerinde yeterli içerik bulunamadı. Başka bir kelime deneyebilirsin.")
                else:
                    st.success("Web verileri başarıyla bulundu!")

            with st.spinner("Gemini LLM bilgileri analiz ediyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Kullanıcının yaptığı arama: "{query}"
                Aşağıda bu arama sonucunda web'den elde edilen veriler bulunmaktadır. Bu verileri analiz et:
                1. Bu arama konusu hakkında kapsamlı ve net bir özet sun.
                2. Önemli detayları, sayısal verileri veya ana bilgileri maddeler halinde çıkar.
                
                Web Verileri:
                {combined_text}
                """
                
                prediction = model.generate_content(prompt)
                
                st.subheader("🤖 Gemini Analiz Sonucu")
                st.
