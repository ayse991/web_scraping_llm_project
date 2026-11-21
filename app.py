import pandas as pd
import streamlit as st

import core

st.set_page_config(page_title="Akıllı CV Analiz Asistanı", page_icon="🎯", layout="wide")

DEFAULT_CV = "3 yıl Python ve Django deneyimi. SQL veritabanları, Git ve temel düzeyde Docker bilgisi var."
DEFAULT_JOB = "En az 2 yıl Python geliştirme tecrübesi, SQL ve Git bilgisi zorunludur. Tercihen Docker bilgisi."
st.session_state.setdefault("job_text", DEFAULT_JOB)

with st.sidebar:
    st.header("⚙️ Ayarlar")
    engine = st.radio("Scraping yöntemi", ["BeautifulSoup", "Selenium"], horizontal=True)
    api_key = st.text_input("Gemini API Anahtarı (opsiyonel)", type="password")
    st.caption("Anahtar yoksa sistem tamamen yerel çalışır.")
    st.caption("⚖️ Scraping yapmadan önce sitenin kullanım şartlarına ve robots.txt kurallarına uyun.")

st.title("🎯 Akıllı CV ve Pozisyon Eşleştirme Aracı")
st.caption("URL → Scraping → Temizleme → Ağırlıklı skor → LLM yorumu")

tab1, tab2, tab3, tab4 = st.tabs(["1️⃣ Tek İlan Analizi", "2️⃣ Çoklu İlan Sıralama",
                                   "3️⃣ BS vs Selenium", "4️⃣ Test Seti"])

# ---------------------------------------------------------------- TAB 1
with tab1:
    url = st.text_input("İlan URL'si (opsiyonel)", placeholder="https://...")
    if st.button("İlanı URL'den çek"):
        if not url.strip():
            st.warning("Bir URL girin.")
        else:
            ok = core.robots_allowed(url.strip())
            if ok is False:
                st.error("robots.txt bu sayfanın otomatik çekilmesine izin vermiyor.")
            else:
                if ok is None:
                    st.info("robots.txt kontrol edilemedi, dikkatli devam ediliyor.")
                with st.spinner(f"{engine} ile çekiliyor..."):
                    r = core.scrape(url.strip(), engine)
                if r["ok"]:
                    st.session_state["job_text"] = r["text"]
                    core.save_jobs([r])
                    st.success(f"{r['chars']} karakter çekildi ({r['seconds']} sn) ve veri setine kaydedildi.")
                else:
                    st.error(r["error"])

    c1, c2 = st.columns(2)
    cv_text = c1.text_area("📄 Aday özeti", DEFAULT_CV, height=180)
    job_text = c2.text_area("💼 İlan gereksinimleri", st.session_state["job_text"], height=180)
    use_llm_extract = st.checkbox("LLM ile ilandan beceri çıkar (sözlükte olmayanları da yakalar)",
                                  disabled=not api_key.strip())

    if st.button("Uyum oranını hesapla", type="primary"):
        extra = None
        if use_llm_extract and api_key.strip():
            try:
                data = core.llm_extract_requirements(api_key.strip(), job_text)
                extra = core.llm_terms(data)
                st.caption(f"LLM çıktısı: {data}")
            except Exception as e:
                st.warning(f"LLM çıkarımı başarısız, yerel sözlük kullanılıyor: {e}")
        res = core.score_match(cv_text, job_text, extra)
        if res["empty"]:
            st.warning("İlanda analiz edilecek yeterli kelime yok.")
        else:
            st.subheader(f"📊 Uyum skoru: %{res['score']}")
            st.progress(res["score"] / 100)
            if res["score"] >= 70:
                st.success("Güçlü eşleşme")
            elif res["score"] >= 40:
                st.info("Orta düzey eşleşme")
            else:
                st.error("Düşük eşleşme")
            if res["job_years"]:
                msg = f"Deneyim: ilan {res['job_years']} yıl, aday {res['cv_years']} yıl"
                (st.success if res["exp_ok"] else st.warning)(
                    msg + ("" if res["exp_ok"] else f" → -{core.EXP_PENALTY} puan"))
            a, b = st.columns(2)
            a.markdown("**✅ Eşleşenler**\n\n" + ("\n".join(f"- `{w}`" for w in res["common"]) or "—"))
            b.markdown("**❌ Eksikler**\n\n" + ("\n".join(f"- `{w}`" for w in res["missing"]) or "—"))
            if api_key.strip():
                with st.spinner("LLM yorumluyor..."):
                    try:
                        st.markdown("---")
                        st.markdown(core.llm_review(api_key.strip(), cv_text, job_text, res["score"]))
                    except Exception as e:
                        st.error(f"LLM hatası: {e}")

# ---------------------------------------------------------------- TAB 2
with tab2:
    st.write("Her satıra bir ilan URL'si yazın. Hepsi çekilir, veri setine kaydedilir ve aday için sıralanır.")
    urls_raw = st.text_area("İlan URL'leri", height=120, placeholder="https://...\nhttps://...")
    cv_multi = st.text_area("Aday özeti", DEFAULT_CV, height=100, key="cv_multi")
    if st.button("Çek ve sırala", type="primary"):
        urls = [u.strip() for u in urls_raw.splitlines() if u.strip()]
        if not urls:
            st.warning("En az bir URL girin.")
        else:
            results, bar = [], st.progress(0.0)
            for i, u in enumerate(urls):
                if core.robots_allowed(u) is False:
                    results.append({"url": u, "title": "", "method": engine, "ok": False, "text": "",
                                    "chars": 0, "seconds": 0, "error": "robots.txt izin vermiyor"})
                else:
                    results.append(core.scrape(u, engine))
                bar.progress((i + 1) / len(urls))
            core.save_jobs(results)
            rows = []
            for r in results:
                if r["ok"]:
                    m = core.score_match(cv_multi, r["text"])
                    rows.append({"Skor": m["score"], "Başlık": r["title"][:60], "URL": r["url"],
                                 "Eksikler": ", ".join(m["missing"][:6])})
                else:
                    rows.append({"Skor": None, "Başlık": "⚠️ " + r["error"], "URL": r["url"], "Eksikler": ""})
            st.dataframe(pd.DataFrame(rows).sort_values("Skor", ascending=False, na_position="last"),
                         use_container_width=True, hide_index=True)
    jobs = core.load_jobs()
    st.markdown(f"**📁 Veri seti:** {len(jobs)} kayıt (jobs.db)")
    if len(jobs):
        st.dataframe(jobs.drop(columns=["text"]), use_container_width=True, hide_index=True)
        st.download_button("CSV olarak indir", jobs.to_csv(index=False).encode("utf-8-sig"),
                           "ilanlar.csv", "text/csv")

# ---------------------------------------------------------------- TAB 3
with tab3:
    st.write("Aynı URL'yi iki yöntemle çekip süre, karakter sayısı ve başarıyı karşılaştırın.")
    cmp_url = st.text_input("Karşılaştırılacak URL", placeholder="https://...", key="cmp_url")
    if st.button("Karşılaştır"):
        if not cmp_url.strip():
            st.warning("Bir URL girin.")
        else:
            rows = []
            for m in ("BeautifulSoup", "Selenium"):
                with st.spinner(f"{m}..."):
                    r = core.scrape(cmp_url.strip(), m)
                rows.append({"Yöntem": m, "Başarılı": "✅" if r["ok"] else "❌",
                             "Süre (sn)": r["seconds"], "Karakter": r["chars"], "Not": r["error"]})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.caption("Statik sayfada BeautifulSoup genelde çok daha hızlıdır; "
                       "JavaScript ile yüklenen sayfada Selenium daha fazla metin getirir.")

# ---------------------------------------------------------------- TAB 4
with tab4:
    st.write("Sistemin beklenen aralıkta skor üretip üretmediğini 8 örnek çiftle test eder.")
    if st.button("Testleri çalıştır"):
        df = core.run_tests()
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.metric("Geçen test", f"{(df['Sonuç'] == '✅').sum()} / {len(df)}")

