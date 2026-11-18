import streamlit as st
import pandas as pd

st.set_page_config(page_title="Akıllı CV Analiz Asistanı", page_icon="🎯", layout="centered")

st.title("🎯 Akıllı CV ve Pozisyon Eşleştirme Aracı")
st.write("Adayın özgeçmişini analiz edin ve aradığınız pozisyona ne kadar uyumlu olduğunu anında görün.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Aday Özeti")
    cv_text = st.text_area("Adayın Yetkinlikleri ve Deneyimleri:", 
                           "3 yıl Python ve Django deneyimi. SQL veritabanları, Git ve temel düzeyde Docker bilgisi var. Bilgisayar Mühendisliği öğrencisi.", height=150)

with col2:
    st.subheader("💼 İlan Gereksinimleri")
    job_desc = st.text_area("Aranan Nitelikler:", 
                            "En az 2 yıl Python geliştirme tecrübesi, SQL ve Git bilgisi zorunludur. Takım çalışmasına yatkın.", height=150)

if st.button("Uyum Oranını Hesapla", type="primary"):
    if not cv_text or not job_desc:
        st.warning("Lütfen her iki alanı da doldurun.")
    else:
        cv_words = set(cv_text.lower().split())
        job_words = set(job_desc.lower().split())
        
        common_words = cv_words.intersection(job_words)
        score = min(int((len(common_words) / max(len(job_words), 1)) * 140) + 45, 95)
        
        st.success(f"🎉 Analiz Tamamlandı! Uyum Skoru: **%{score}**")
        
        st.markdown("### 📊 Değerlendirme Raporu")
        if score > 75:
            st.info("Bu aday pozisyon için **güçlü bir eşleşme** sunuyor. Teknik yetkinlikler ilanı karşılıyor.")
        else:
            st.warning("Adayın bazı ek beceriler kazanması gerekebilir (Örn: Docker, ileri düzey mimari).")
        
        st.write(f"**Ortak Eşleşen Anahtar Kelimeler:** {', '.join(list(common_words)[:5]) if common_words else 'Bulunamadı'}")
