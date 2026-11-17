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

# API Anahtarını doğrudan Streamlit Secrets'tan güvenli bir şekilde alıyoruz
api_key = st.secrets.get("GOOGLE_API_KEY", "")

# Arama Kutusu
query = st.text_input("Ne aramak veya analiz ettirmek istiyorsun?", placeholder="Örn: ösym 2024 sıralama, python mülakat soruları...")

if st.button("Web'de Ara and Analiz Et", type="primary"):
    if not api_key:
        st.error("Streamlit Secrets içinde GOOGLE_API_KEY bulunamadı. Lütfen ayarlarınızı kontrol edin.")
    elif not query:
        st.warning("Lütfen aramak istediğin bir kelime veya konu yaz.")
    else:
        try:
            with st.spinner("Web'de hızla aranıyor..."):
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                
                # Timeout süresi hız için 5 saniyeye düşürüldü
                response = requests.get(search_url, headers=headers, timeout=5)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Veri miktarını optimize etmek için limit 3'e düşürüldü
                results = []
                for a in soup.find_all('a', class_='result__snippet', limit=3):
                    results.append(a.get_text(strip=True))
                
                if not results:
                    for a in soup.find_all('a', class_='result__title', limit=3):
                        results.append(a.get_text(strip=True))
                        
                combined_text = " ".join(results)
                
                if not combined_text:
                    st.warning("Aradığın konuyla ilgili web üzerinde yeterli içerik bulunamadı.")
                else:
                    st.success("Veriler toplandı, Gemini analiz ediyor...")

            with st.spinner("Yapay zeka yanıtı hazırlıyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3.8-flash')
                
                prompt = f"""
                Arama konusu: "{query}"
                Özet veriler:
                {combined_text}
                
                Bu verileri kullanarak net, öz ve hızlı bir özet sun, önemli maddeleri listele.
                """
                
                prediction = model.generate_content(prompt)
                
                st.subheader("🤖 Gemini Analiz Sonucu")
                st.markdown(prediction.text)

        except Exception as e:
            st.error(f"İşlem sırasında bir hata oluştu: {e}")
