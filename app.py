import streamlit as st
import google.generativeai as genai

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Hızlı Gemini Asistanı",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Hızlı Gemini Asistanı")
st.write("Aramak veya öğrenmek istediğin konuyu yaz, Gemini anında analiz etsin!")

# API Anahtarını doğrudan Streamlit Secrets'tan güvenli bir şekilde alıyoruz
api_key = st.secrets.get("GOOGLE_API_KEY", "")

# Soru Kutusu
query = st.text_input("Ne öğrenmek istiyorsun?", placeholder="Örn: python mülakat soruları, ösym tarihleri...")

if st.button("Hemen Analiz Et", type="primary"):
    if not api_key:
        st.error("Streamlit Secrets içinde GOOGLE_API_KEY bulunamadı. Lütfen ayarlarınızı kontrol edin.")
    elif not query:
        st.warning("Lütfen bir konu yaz.")
    else:
        try:
            with st.spinner("Yapay zeka yanıtı hazırlıyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3.8-flash')
                
                prompt = f"""
                Şu konu hakkında kapsamlı, net ve maddeler halinde bir analiz sun:
                "{query}"
                """
                
                prediction = model.generate_content(prompt)
                
                st.subheader("🤖 Gemini Analiz Sonucu")
                st.markdown(prediction.text)

        except Exception as e:
            st.error(f"İşlem sırasında bir hata oluştu: {e}")
