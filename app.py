import streamlit as st
import google.generativeai as genai

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Hızlı Web & Gemini Asistanı",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Hızlı Web & Gemini Asistanı")
st.write("Aramak istediğin konuyu yaz, saniyeler içinde güncel web verileriyle analiz edilsin!")

# API Anahtarını Streamlit Secrets'tan alıyoruz
api_key = st.secrets.get("GOOGLE_API_KEY", "")

query = st.text_input("Ne aramak veya öğrenmek istiyorsun?", placeholder="Örn: ösym takvimi, python son sürüm yenilikleri...")

if st.button("Hemen Getir", type="primary"):
    if not api_key:
        st.error("Streamlit Secrets içinde GOOGLE_API_KEY bulunamadı.")
    elif not query:
        st.warning("Lütfen bir şeyler yaz.")
    else:
        try:
            with st.spinner("Anında aranıyor ve analiz ediliyor..."):
                genai.configure(api_key=api_key)
                
                # Gemini'nin dahili arama aracıyla hızlı ve güncel yanıt
                model = genai.GenerativeModel(
                    model_name='gemini-3.8-flash',
                    tools=[{"google_search": {}}]
                )
                
                response = model.generate_content(query)
                
                st.subheader("🤖 Anlık Analiz Sonucu")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
