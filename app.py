import streamlit as st
from google import genai

st.set_page_config(page_title="Hızlı Asistan", page_icon="⚡", layout="centered")
st.title("⚡ Hızlı Gemini Asistanı (Kota Dostu)")

api_key = st.secrets.get("GOOGLE_API_KEY", "")
query = st.text_input("Ne öğrenmek istiyorsun?", placeholder="Örn: Python'da for döngüsü nasıl çalışır?")

if st.button("Hemen Gönder", type="primary"):
    if not api_key:
        st.error("API anahtarı bulunamadı.")
    elif not query:
        st.warning("Lütfen bir soru yaz.")
    else:
        try:
            with st.spinner("Düşünülüyor..."):
                client = genai.Client(api_key=api_key)
                
                # En basit ve hızlı model çağrısı (history yok)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=query
                )
                
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
            if "429" in str(e):
                st.info("İpucu: Lütfen 1-2 dakika bekleyip tekrar deneyin. Ücretsiz kota dolmuş olabilir.")
