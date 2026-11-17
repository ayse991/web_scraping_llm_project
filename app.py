import streamlit as st
import pandas as pd
from scraper import scraper_fonksiyonun # Kendi scraper fonksiyonunu buraya bağla

st.title("Web Scraping & LLM Projesi")
st.write("Üniversite Projesi - Web Scraping ve LLM Entegrasyonu")

# Kullanıcıdan girdi alma
url_input = st.text_input("Taranacak Web Sitesi URL'sini Girin:")

if st.button("Veriyi Çek ve Analiz Et"):
    if url_input:
        with st.spinner("Veriler kazınıyor ve LLM ile işleniyor..."):
            # Buraya scraper ve LLM kodunu ekleyeceksin
            # Ornek: sonuc = scraper_fonksiyonun(url_input)
            
            st.success("İşlem tamamlandı!")
            st.write("Sonuçlar burada görünecek.")
    else:
        st.warning("Lütfen geçerli bir URL girin.")
