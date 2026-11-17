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

st.title("🌐 Web Scraping & LLM Analiz Projesi")
st.write("Hedef web sitesinden içerik kazıyan ve Gemini LLM ile analiz eden tek dosyalık uygulama.")

# Sidebar - API Anahtarı ve Ayarlar
st.sidebar.header("Ayarlar")
api_key = st.sidebar.text_input(
    "Gemini API Key", 
    type="password", 
    value=st.secrets.get("GOOGLE_API_KEY", ""),
    help="Google AI Studio'dan aldığınız API anahtarınızı buraya girebilirsiniz."
)

# Ana Ekran - URL Girdisi
url = st.text_input("Taranacak Web Sitesi URL'si:", placeholder="https://example.com")

# İşlem Butonu
if st.button("Veriyi Çek ve Analiz Et", type="primary"):
    if not url:
        st.warning("Lütfen taranacak bir URL girin.")
    elif not api_key:
        st.error("Lütfen bir Gemini API anahtarı girin.")
    else:
        try:
            # 1. Adım: Web Scraping
            with st.spinner("Web sitesinden veriler kazınıyor..."):
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # HTML çözümleme
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Gereksiz etiketleri temizle (script, style vb.)
                for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
                    script_or_style.decompose()
                    
                # Metinleri al ve çok uzunsa kırp
                raw_text = soup.get_text(separator=' ', strip=True)
                text_content = raw_text[:12000] # LLM token sınırı için güvenli uzunluk

            st.success("Veriler başarıyla kazındı!")

            # 2. Adım: LLM Analizi
            with st.spinner("Gemini LLM ile içerik analiz ediliyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Aşağıda bir web sitesinden kazınan metin bulunmaktadır. Bu metni analiz et:
                1. Bu site/sayfa ne hakkında? Kısa bir özet geç.
                2. Önemli başlıkları ve ana bilgileri maddeler halinde çıkar.
                
                İçerik:
                {text_content}
                """
                
                prediction = model.generate_content(prompt)
                
                # Sonucu Göster
                st.subheader("🤖 LLM Analiz Sonucu")
                st.markdown(prediction.text)
                
                # İsteğe bağlı ham metni gösterme
                with st.expander("Kazınan Ham Metin Örneği"):
                    st.write(text_content[:2000] + "...")

        except Exception as e:
            st.error(f"İşlem sırasında bir hata oluştu: {e}")
