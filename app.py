import streamlit as st
import re

# Sayfa Yapılandırması
st.set_page_config(page_title="Akıllı CV Analiz Asistanı", page_icon="🎯", layout="centered")

st.title("🎯 Akıllı CV ve Pozisyon Eşleştirme Aracı")
st.write("Adayın özgeçmişini analiz edin ve aradığınız pozisyona ne kadar uyumlu olduğunu anında görün.")

# İki sütunlu veri giriş arayüzü
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Aday Özeti")
    cv_text = st.text_area(
        "Adayın Yetkinlikleri ve Deneyimleri:", 
        "3 yıl Python ve Django deneyimi. SQL veritabanları, Git ve temel düzeyde Docker bilgisi var.", 
        height=150
    )

with col2:
    st.subheader("💼 İlan Gereksinimleri")
    job_desc = st.text_area(
        "Aranan Nitelikler:", 
        "En az 2 yıl Python geliştirme tecrübesi, SQL ve Git bilgisi zorunludur.", 
        height=150
    )

def clean_and_tokenize(text):
    """Metni Türkçe karakterlere duyarlı şekilde temizler ve anlamlı kelimeleri ayıklar."""
    # Türkçe büyük harf dönüşüm hatalarını önlemek için güvenli düzeltme
    text_tr = text.replace('İ', 'i').replace('I', 'ı').lower()
    
    # Sadece kelime köklerini/harfleri seç
    words = re.findall(r'\b\w+\b', text_tr)
    
    # Analizi kirletecek anlamsız dolgu kelimeleri ve bağlaçlar
    stop_words = {
        "ve", "ile", "bir", "bu", "şu", "o", "için", "olan", "en", "az", 
        "var", "yok", "gibi", "kadar", "da", "de", "ki", "hem", "ya", 
        "ama", "ancak", "lakin", "fakat", "göre", "birlikte", "olarak",
        "bilgi", "bilgisi", "deneyim", "deneyimi", "yıl", "sene"
    }
    
    # 2 karakterden uzun ve stop words listesinde olmayan kelimeleri döndür
    return set(w for w in words if w not in stop_words and len(w) > 2)

# Hesaplama Butonu
if st.button("Uyum Oranını Hesapla", type="primary"):
    if not cv_text.strip() or not job_desc.strip():
        st.warning("Lütfen her iki metin alanını da eksiksiz doldurun.")
    else:
        # Kelimeleri temizle ve set haline getir
        cv_words = clean_and_tokenize(cv_text)
        job_words = clean_and_tokenize(job_desc)
        
        if not job_words:
            st.warning("İlan gereksinimlerinde analiz edilecek yeterli anahtar kelime bulunamadı.")
        else:
            # Küme kesişim ve fark hesaplamaları
            common_words = cv_words.intersection(job_words)
            missing_words = job_words - cv_words
            
            # Gerçek matematiksel oran (0 ile 100 arasında sınırlandırılmış)
            score = int((len(common_words) / len(job_words)) * 100)
            score = min(max(score, 0), 100)
            
            st.markdown("---")
            st.subheader(f"📊 Analiz Sonucu & Uyum Skoru: **%{score}**")
            st.progress(score / 100)
            
            # Skora göre durum değerlendirmesi
            if score >= 70:
                st.success("✨ **Güçlü Eşleşme:** Aday aranan niteliklerin büyük çoğunluğunu karşılıyor.")
            elif score >= 40:
                st.info("⚠️ **Orta Düzey Eşleşme:** Adayın temel yetkinlikleri var ancak bazı kritik kriterler eksik.")
            else:
                st.error("❌ **Düşük Eşleşme:** Aday ilandaki temel gereksinimleri karşılamıyor.")
            
            # Detaylı Eşleşme ve Eksik Raporu (Yan yana iki sütun)
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.markdown("**✅ Eşleşen Kriterler:**")
                if common_words:
                    for word in sorted(common_words):
                        st.markdown(f"- `{word}`")
                else:
                    st.write("*(Eşleşen kelime bulunamadı)*")
                    
            with col_res2:
                st.markdown("**❌ Eksik Kriterler:**")
                if missing_words:
                    for word in sorted(missing_words):
                        st.markdown(f"- `{word}`")
                else:
                    st.write("*(Eksik kriter yok, tam uyum!)*")
