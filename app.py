# ================================================================
# ARSEN PROCESS - CINEMA STUDIO v8.0 (CLEAN & ERROR-FREE)
# AI Yönetmen + 3D Reaktör + CRM + Otonom Film + Canlı Sunum + Avatar + Fabrika + Dijital İkiz
# Komut: streamlit run app.py
# ================================================================

import streamlit as st
import os, time, asyncio, json, cv2, random
import urllib.parse, urllib.request
import numpy as np
from PIL import Image as PILImage
import plotly.graph_objects as go

from arsen_engine import (
    AudioEngine, VisualEngine, ContentEngine,
    AdvancedAIEngine, DistributionEngine,
    VOICES, PHOTOS, VIDEOS, LOGOS, MUSIC,
    OUTPUT, AI_OUT, AUDIO, SUBS
)
from director_engine import (
    AIDirector, Reactor3D, CloudRender,
    ClientPortal, AutoPipeline, AIAvatar
)

# ================================================================
# SAYFA AYARLARI
# ================================================================
st.set_page_config(
    page_title="Arşen Process - Cinema Studio v8.0",
    page_icon="🎬", layout="wide", initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1A0F00 0%, #0A1628 40%, #0A1A0F 70%, #0D0D1A 100%);
        padding: 2rem; border-radius: 15px; text-align: center;
        border: 2px solid #D4AF37; margin-bottom: 1.5rem;
        box-shadow: 0 0 30px rgba(212,175,55,0.15);
    }
    .main-header h1 { color: #D4AF37; margin: 0; font-size: 2rem; font-family: 'Arial'; }
    .main-header p { color: #00D2BA; margin: 0.5rem 0 0 0; }
</style>
""", unsafe_allow_html=True)

for d in [PHOTOS, VIDEOS, LOGOS, MUSIC, OUTPUT, AI_OUT, AUDIO, SUBS, "projects", "exports", "ai_generated/slides"]:
    os.makedirs(d, exist_ok=True)

# ================================================================
# VARSAYILAN VERİLER
# ================================================================
if "scenes" not in st.session_state:
    st.session_state.scenes = [
        {"id":"S01","title":"SÜPERKRİTİK DÖNÜŞÜM","type":"manim","vo":"Bazı dönüşümler gözle görülmez."},
        {"id":"S02","title":"ARŞEN PROCESS","type":"manim","vo":"Arşen Proses. Bilimi endüstriyel çözümlere dönüştürür."},
        {"id":"S03","title":"2007 KURULUŞ","type":"photo","photo":"factory.jpg","vo":"İki bin yedi yılında kuruldu."},
        {"id":"S04","title":"MÜHENDİSLİK","type":"photo","photo":"founder.jpg","vo":"Petrokimya deneyimi."},
        {"id":"S05","title":"2012 KEŞİF","type":"photo","photo":"founder.jpg","vo":"İki bin on ikide Ar-Ge başladı."},
        {"id":"S06","title":"KRİTİK NOKTA","type":"manim","vo":"Karbondioksit yeni davranış kazanır."},
        {"id":"S07","title":"PROTOTİP","type":"photo","photo":"prototype.jpg","vo":"İlk prototip hayata geçti."},
        {"id":"S08","title":"FUWELL","type":"photo","photo":"products.jpg","vo":"Fuvell wellness markası."},
        {"id":"S09","title":"SYNTEGRA","type":"manim","vo":"Sintegra imalat gücü."},
        {"id":"S10","title":"KAPANIŞ","type":"manim","vo":"Arşen Proses. Geleceği bugün tasarlıyoruz."},
    ]

if "film_plan" not in st.session_state:
    st.session_state.film_plan = None

if "crm_clients" not in st.session_state:
    st.session_state.crm_clients = [
        {"name": "Mr. Giorgi", "company": "Giorgi Industries", "project": "2x1000L SC-CO2 Şerbetçiotu", "investment": "4.25M USD", "status": "Aktif", "film": ""},
        {"name": "Mertoğlu Grup", "company": "Mertoğlu Holding", "project": "2x2500L Şerbetçiotu + Protein", "investment": "8.5M USD", "status": "Planlama", "film": ""},
        {"name": "Ordu Büyükşehir", "company": "Ordu Belediyesi", "project": "R&D 2x50L + 4x250L Süper Gıda", "investment": "2.1M USD", "status": "Aktif", "film": ""},
        {"name": "Irak Zeytin A.Ş.", "company": "Iraq Olive Corp", "project": "2x2000L Polifenol + Zeytinyağı", "investment": "6.0M USD", "status": "Teklif", "film": ""},
        {"name": "Sakarya Teverler", "company": "Teverler Grup", "project": "500L Evrensel Ekstraksiyon", "investment": "1.8M USD", "status": "Aktif", "film": ""},
    ]

# ================================================================
# HEADER
# ================================================================
st.markdown("""
<div class="main-header">
    <h1>🎬 ARŞEN PROCESS — CINEMA STUDIO v8.0</h1>
    <p>AI Yönetmen | 3D Reaktör | CRM | Otonom Film | Canlı Sunum | Avatar | 3D Fabrika | Dijital İkiz</p>
</div>
""", unsafe_allow_html=True)

# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.header("⚙️ Ayarlar")
    voice_lang = st.selectbox("Dil", list(VOICES.keys()), key="sb_lang_key")
    voice_gender = st.selectbox("Ses", ["male", "female"], key="sb_gender_key")
    color_style = st.selectbox("Renk", ["teal_orange","bleach_bypass","vintage_amber","cold_tech","noir"], key="sb_color_key")

    st.divider()
    st.subheader("📊 Durum")
    total = len(st.session_state.scenes)
    ready = sum(1 for s in st.session_state.scenes if os.path.exists(f"output_clips/{s['id']}.mp4"))
    st.metric("Klipler", f"{ready}/{total}")
    st.progress(ready / max(total, 1))
    st.metric("CRM Müşteri", len(st.session_state.crm_clients))

# ================================================================
# SEKMELER (12 MODÜL)
# ================================================================
t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12 = st.tabs([
    "🎬 AI Yönetmen",
    "🏗️ 3D Reaktör",
    "📊 CRM",
    "🚀 Otonom",
    "📋 Sahneler",
    "🎨 Görsel",
    "🎤 Ses",
    "📤 Dağıtım",
    "🎥 Sunum",
    "🧑‍💼 AI Avatar",
    "🏭 3D Fabrika",
    "📈 Dijital İkiz"
])

# ================================================================
# T1: AI YÖNETMEN
# ================================================================
with t1:
    st.header("🎬 AI Film Yönetmeni")
    brief = st.text_area("Film Brief'i:",
        "Create a 3-minute corporate documentary for Arşen Process about supercritical CO2 extraction technology, SYNTEGRA manufacturing, FUWELL products, and global projects.",
        height=100, key="t1_brief_key")

    if st.button("🎬 FİLMİ PLANLA", type="primary", key="t1_plan_key"):
        with st.spinner("AI Yönetmen senaryo ve plan hazırlıyor..."):
            plan = AIDirector.plan_film(brief)
            st.session_state.film_plan = plan

    if st.session_state.film_plan:
        plan = st.session_state.film_plan
        if "error" in plan:
            st.error(f"Hata: {plan['error']}")
        else:
            st.success(f"✅ {plan.get('film_title','')} — {len(plan.get('scenes',[]))} sahne")
            for sc in plan.get("scenes", []):
                with st.expander(f"🎬 {sc.get('id','')} — {sc.get('title','')}"):
                    st.write(f"**Kamera:** {sc.get('camera','-')} | **Süre:** {sc.get('duration','-')}sn")
                    st.write(f"**Seslendirme:** {sc.get('narration','-')}")

            if st.button("🖼️ GÖRSELLERİ ÜRET", type="primary", key="t1_img_key"):
                with st.spinner("Görseller üretiliyor..."):
                    results = AIDirector.generate_all_images(plan)
                    for r in results:
                        if r["status"] == "ok" and r["path"]:
                            st.image(r["path"], caption=r["id"], width=300)

# ================================================================
# T2: 3D REAKTÖR
# ================================================================
with t2:
    st.header("🏗️ 3D SC-CO₂ Reaktör Simülasyonu")
    c1, c2, c3 = st.columns(3)
    with c1: pressure = st.slider("Basınç (Bar)", 50, 600, 500, 10, key="t2_p_key")
    with c2: temperature = st.slider("Sıcaklık (°C)", 20, 100, 60, 5, key="t2_t_key")
    with c3: volume = st.select_slider("Hacim (L)", [50,250,500,1000,2000,2500,5000], 1000, key="t2_v_key")

    fig = Reactor3D.build_reactor(pressure, temperature, volume)
    st.plotly_chart(fig, use_container_width=True, key="plot_t2_reactor")

    st.divider()
    fig2 = Reactor3D.build_process_flow()
    st.plotly_chart(fig2, use_container_width=True, key="plot_t2_flow")

    phase = "**SÜPERKRİTİK** ✅" if pressure >= 73.8 and temperature >= 31.1 else "**GAZ** ⚠️"
    st.info(f"💡 Faz Durumu: {pressure} bar / {temperature}°C → CO₂ {phase} fazda")

# ================================================================
# T3: CRM
# ================================================================
with t3:
    st.header("📊 CRM & Müşteri Yönetim Paneli")

    with st.expander("➕ Yeni Müşteri Ekle"):
        nc1, nc2, nc3 = st.columns(3)
        with nc1:
            new_name = st.text_input("Müşteri Adı", key="crm_name_key")
            new_company = st.text_input("Şirket", key="crm_comp_key")
        with nc2:
            new_project = st.text_input("Proje", key="crm_proj_key")
            new_invest = st.text_input("Yatırım", key="crm_inv_key")
        with nc3:
            new_status = st.selectbox("Durum", ["Teklif","Planlama","Aktif","Tamamlandı"], key="crm_stat_key")

        if st.button("Müşteri Ekle", key="crm_add_btn"):
            if new_name:
                st.session_state.crm_clients.append({
                    "name": new_name, "company": new_company,
                    "project": new_project, "investment": new_invest,
                    "status": new_status, "film": ""
                })
                st.success(f"✅ {new_name} eklendi!")
                st.rerun()

    st.divider()
    st.subheader(f"Aktif Müşteriler ({len(st.session_state.crm_clients)})")

    for idx, client in enumerate(st.session_state.crm_clients):
        status_color = {"Aktif":"🟢","Planlama":"🟡","Teklif":"🔵","Tamamlandı":"✅"}.get(client["status"], "⚪")

        with st.expander(f"{status_color} {client['name']} — {client['company']} | {client['project']}"):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.write(f"**Proje:** {client['project']}")
                st.write(f"**Yatırım:** {client['investment']}")
                st.write(f"**Durum:** {client['status']}")
                if client.get("film") and os.path.exists(client["film"]):
                    st.video(client["film"])
            with c2:
                client["status"] = st.selectbox("Durum Güncelle",
                    ["Teklif","Planlama","Aktif","Tamamlandı"],
                    index=["Teklif","Planlama","Aktif","Tamamlandı"].index(client["status"]),
                    key=f"crm_st_{idx}")
            with c3:
                if st.button(f"🎬 Film Üret", key=f"crm_film_{idx}"):
                    with st.spinner(f"{client['name']} için film üretiliyor..."):
                        brief = f"{client['name']} ({client['company']}). Project: {client['project']}. Investment: {client['investment']}."
                        result = AutoPipeline.run(brief, output_name=f"CRM_{client['name'].replace(' ','_')}", lang="Türkçe")
                        if result["status"] == "success":
                            client["film"] = result["output"]
                            st.success(f"✅ Film hazır: {result['output']}")
                            st.video(result["output"])
                        else:
                            st.error(f"Hata: {result.get('error','')}")

                if st.button(f"🗑️ Sil", key=f"crm_del_{idx}"):
                    st.session_state.crm_clients.pop(idx)
                    st.rerun()

# ================================================================
# T4: OTONOM FİLM
# ================================================================
with t4:
    st.header("🚀 Tam Otonom Film Üretim Hattı")
    st.write("Tek brief → Final MP4. Sıfır insan müdahalesi.")

    c1, c2 = st.columns([2, 1])
    with c1:
        auto_brief = st.text_area("Brief:",
            "Create a 2-minute documentary for Mr. Giorgi about 2x1000L SC-CO2 hop extraction at 500 bar.",
            height=100, key="t4_brief_key")
    with c2:
        auto_lang = st.selectbox("Dil", ["Türkçe","English","العربية"], key="t4_lang_key")
        auto_name = st.text_input("Proje Adı", "OTONOM_FILM", key="t4_name_key")

    if st.button("🚀 FİLMİ ÜRET", type="primary", use_container_width=True, key="t4_run_key"):
        progress_bar = st.progress(0, text="Başlatılıyor...")

        def update(pct, msg):
            progress_bar.progress(pct / 100, text=f"{pct}% — {msg}")

        with st.spinner("Otonom üretim çalışıyor..."):
            result = AutoPipeline.run(auto_brief, auto_name, auto_lang, update)

        if result["status"] == "success":
            st.balloons()
            st.success(f"🎉 Film hazır! ({result['duration']:.0f}sn, {result['scenes']} sahne)")
            st.video(result["output"])
            with open(result["output"], "rb") as f:
                st.download_button("📥 İndir", f.read(), result["output"], "video/mp4", key="t4_dl_key")
        else:
            st.error(f"Hata: {result.get('error','')}")

# ================================================================
# T5: SAHNELER
# ================================================================
with t5:
    st.header("📋 Sahne Listesi")
    for sc in st.session_state.scenes:
        sid = sc["id"]
        exists = os.path.exists(f"output_clips/{sid}.mp4")
        with st.expander(f"{'✅' if exists else '⏳'} {sid} — {sc['title']}"):
            c1, c2 = st.columns([2, 1])
            with c1:
                sc["title"] = st.text_input("Başlık", sc["title"], key=f"t5_t_{sid}")
                sc["vo"] = st.text_area("Ses", sc["vo"], key=f"t5_v_{sid}")
            with c2:
                if exists:
                    st.video(f"output_clips/{sid}.mp4")

# ================================================================
# T6: GÖRSEL STÜDYO
# ================================================================
with t6:
    st.header("🎨 Görsel Kalite Stüdyosu")
    up = st.file_uploader("Fotoğraf Yükle", type=["jpg","jpeg","png"], key="t6_up_key")
    if up:
        img = PILImage.open(up)
        st.image(img, width=400)
        eff = st.selectbox("Efekt", ["zoom_in","zoom_out","pan_right","pan_left","slow_zoom"], key="t6_eff_key")
        if st.button("📸 Üret", type="primary", key="t6_run_key"):
            temp = f"{PHOTOS}/_upload.jpg"
            img.save(temp)
            out_v = f"{OUTPUT}/cinematic_{int(time.time())}.mp4"
            img_cv = cv2.imread(temp)
            h, w = img_cv.shape[:2]
            writer = cv2.VideoWriter(out_v, cv2.VideoWriter_fourcc(*'mp4v'), 30, (1920,1080))
            effs = {"zoom_in":(1.0,1.3),"zoom_out":(1.3,1.0),"pan_right":(1.2,1.2),"pan_left":(1.2,1.2),"slow_zoom":(1.0,1.15)}
            ss, es = effs.get(eff, (1.0,1.2))
            for fi in range(240):
                t = fi/239; ts = t*t*(3-2*t)
                scale = ss+(es-ss)*ts
                cw, ch = int(w/scale), int(h/scale)
                x1, y1 = max(0,(w-cw)//2), max(0,(h-ch)//2)
                crop = cv2.resize(img_cv[y1:y1+ch, x1:x1+cw], (1920,1080))
                crop = VisualEngine.apply_color_grade(crop, color_style)
                crop = VisualEngine.add_vignette(crop)
                writer.write(crop)
            writer.release()
            st.success("✅ Hazır!")
            st.video(out_v)

    st.divider()
    v_files = [f for f in os.listdir(OUTPUT) if f.endswith(".mp4")]
    if v_files:
        sel = st.selectbox("Video", v_files, key="t6_vid_key")
        grade = st.selectbox("Renk", ["teal_orange","bleach_bypass","vintage_amber","cold_tech","noir"], key="t6_grade_key")
        if st.button("🎨 Uygula", type="primary", key="t6_apply_key"):
            out = os.path.join(OUTPUT, f"graded_{sel}")
            VisualEngine.process_video(os.path.join(OUTPUT, sel), out, color_grade=grade)
            st.success("✅ Hazır!")
            st.video(out)

# ================================================================
# T7: SES STÜDYO
# ================================================================
with t7:
    st.header("🎤 Ses Stüdyosu")
    text = st.text_area("Metin:", st.session_state.scenes[0]["vo"], key="t7_text_key")
    c1, c2 = st.columns(2)
    with c1: lang = st.selectbox("Dil", list(VOICES.keys()), key="t7_lang_key")
    with c2: gender = st.selectbox("Cinsiyet", ["male","female"], key="t7_gen_key")
    if st.button("🎤 Seslendir", type="primary", key="t7_run_key"):
        out = f"{AUDIO}/preview.mp3"
        result = asyncio.run(AudioEngine.generate_voice(text, lang, gender, output_path=out))
        if result:
            st.success("✅ Hazır!")
            st.audio(result)

    st.divider()
    sfx_type = st.selectbox("SFX", ["factory_hum","pressure_valve","liquid_flow","welding","whoosh"], key="t7_sfx_key")
    if st.button("🔊 SFX Üret", key="t7_sfx_run_key"):
        out = AudioEngine.generate_sfx(sfx_type, 3.0)
        st.audio(out)

    st.divider()
    if st.button("🎵 Ambient Müzik Bestele", key="t7_music_key"):
        out = AudioEngine.generate_ambient_music(60, "epic")
        st.success("✅ Müzik hazır!")
        st.audio(out)

# ================================================================
# T8: DAĞITIM
# ================================================================
with t8:
    st.header("📤 Dağıtım ve Export")
    v_files_dist = [f for f in os.listdir(OUTPUT) if f.endswith(".mp4")]
    if v_files_dist:
        sel_dist = st.selectbox("Kaynak Video", v_files_dist, key="t8_dist_vid_key")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("📺 Tüm Formatlarda Export (4K/1080p/720p/Dikey/Kare)", type="primary", key="t8_export_key"):
                with st.spinner("Formatlar üretiliyor..."):
                    results = DistributionEngine.export_formats(os.path.join(OUTPUT, sel_dist), "exports")
                    st.success(f"✅ {len(results)} format!")
                    for r in results:
                        st.write(f"📁 {r}")
        with c2:
            if st.button("📱 Sosyal Medya Kesitleri (Reel/Story)", type="primary", key="t8_social_key"):
                with st.spinner("Kesitler hazırlanıyor..."):
                    results = ContentEngine.generate_social_cuts(os.path.join(OUTPUT, sel_dist), "exports/social")
                    st.success(f"✅ {len(results)} klip!")
                    for r in results:
                        st.write(f"📁 {r}")
    else:
        st.warning("Henüz video yok. Önce sahne üretin.")

# ================================================================
# T9: CANLI SUNUM MODU (DÜZELTİLDİ: TÜM GRAFİKLERDE BENZERSİZ KEY)
# ================================================================
with t9:
    st.header("🎥 Canlı Sunum Modu")
    c1, c2, c3 = st.columns(3)
    with c1: pres_client = st.selectbox("Müşteri", ["Genel"] + [c["name"] for c in st.session_state.crm_clients], key="t9_client_key")
    with c2: pres_lang = st.selectbox("Dil", ["Türkçe","English"], key="t9_lang_key")
    with c3: pres_duration = st.slider("Süre (dk)", 1, 10, 3, key="t9_dur_key")

    st.divider()

    if st.button("▶️ SUNUMU BAŞLAT (Tam Ekran)", type="primary", use_container_width=True, key="t9_start_key"):
        st.balloons()

        st.markdown("## 🎬 Arşen Process — Kurumsal Tanıtım")
        v_files_pres = [f for f in os.listdir(OUTPUT) if f.endswith(".mp4")]
        if v_files_pres:
            st.video(os.path.join(OUTPUT, v_files_pres[0]))

        st.divider()

        # 3D Reaktör (Benzersiz Key)
        st.markdown("## 🏗️ 500 Bar SC-CO₂ Reaktör — Canlı Simülasyon")
        fig_pres = Reactor3D.build_reactor(500, 60, 2500)
        st.plotly_chart(fig_pres, use_container_width=True, key="plot_t9_pres_reactor")

        st.divider()

        # Proses Akışı (Benzersiz Key)
        st.markdown("## 📊 Kapalı Devre Proses Akışı")
        fig_flow = Reactor3D.build_process_flow()
        st.plotly_chart(fig_flow, use_container_width=True, key="plot_t9_pres_flow")

        st.divider()

        if pres_client != "Genel":
            client_data = next((c for c in st.session_state.crm_clients if c["name"] == pres_client), None)
            if client_data:
                st.markdown(f"## 🤝 {client_data['name']} — Özel Teklif")
                st.markdown(f"""
                | Kalem | Detay |
                |---|---|
                | **Müşteri** | {client_data['name']} ({client_data['company']}) |
                | **Proje** | {client_data['project']} |
                | **Yatırım** | {client_data['investment']} |
                | **Durum** | {client_data['status']} |
                | **Geri Ödeme** | 36 ay eşit taksit |
                | **İşletme** | Arşen Process (sıfır müşteri maliyeti) |
                """)
                if client_data.get("film") and os.path.exists(client_data["film"]):
                    st.video(client_data["film"])

# ================================================================
# T10: AI DİJİTAL SUNUCU (AVATAR)
# ================================================================
with t10:
    st.header("🧑‍💼 AI Dijital Sunucu (Avatar)")
    c1, c2 = st.columns(2)
    with c1:
        avatar_client = st.selectbox("Müşteri", ["Mr. Giorgi","Mertoğlu Grup","Ordu Büyükşehir","Irak Zeytin A.Ş."], key="t10_client_key")
        avatar_project = st.text_input("Proje Detayı", "2x1000L SC-CO2 Şerbetçiotu, 500 Bar, 4.25M USD", key="t10_proj_key")
        avatar_setting = st.selectbox("Ortam", ["confident_factory","confident_lab","confident_office","presentation"], key="t10_set_key")

    with c2:
        if st.button("🧑‍💼 Avatar Görseli Üret", type="primary", key="t10_avatar_key"):
            with st.spinner("AI avatar oluşturuluyor..."):
                path = AIAvatar.generate_avatar_image(None, setting=avatar_setting.split("_")[1] if "_" in avatar_setting else "factory")
                st.success("✅ Avatar hazır!")
                st.image(path, width=400)

    st.divider()

    if st.button("📊 Sunum Slaytları Oluştur", type="primary", key="t10_slides_key"):
        with st.spinner("5 slaytlık sunum hazırlanıyor..."):
            slides = AIAvatar.create_presentation_slides(avatar_client, avatar_project)
            st.success(f"✅ {len(slides)} slayt hazır!")
            for s in slides:
                st.image(s, use_container_width=True)

    if st.button("🎬 Avatar Sunum Videosu Üret", type="primary", key="t10_video_key"):
        with st.spinner("Sunum videosu oluşturuluyor..."):
            slides = AIAvatar.create_presentation_slides(avatar_client, avatar_project)
            video_path = AIAvatar.generate_avatar_video(slides)
            if video_path:
                st.success("✅ Sunum videosu hazır!")
                st.video(video_path)

# ================================================================
# T11: 3D İNTERAKTİF FABRİKA TURU
# ================================================================
with t11:
    st.header("🏭 3D İnteraktif Fabrika Turu")
    c1, c2, c3, c4 = st.columns(4)
    with c1: f_extractors = st.selectbox("Ekstraktör Sayısı", [2, 4, 6, 8], key="t11_ext_key")
    with c2: f_volume = st.selectbox("Hacim (L)", [500, 1000, 2000, 2500, 5000], key="t11_vol_key")
    with c3: f_pressure = st.slider("Basınç (Bar)", 100, 600, 500, key="t11_pres_key")
    with c4: f_temp = st.slider("Sıcaklık (°C)", 25, 90, 60, key="t11_temp_key")

    st.divider()

    fig_factory = go.Figure()
    for i in range(f_extractors):
        x_offset = (i - f_extractors/2 + 0.5) * 3
        theta = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(-2, 2, 15)
        tg, zg = np.meshgrid(theta, z)
        r = 0.6 + f_volume / 10000

        fig_factory.add_trace(go.Surface(
            x=r*np.cos(tg) + x_offset, y=r*np.sin(tg), z=zg,
            colorscale=[[0,'#3a3a4a'],[0.5,'#8E9AAF'],[1,'#5a5a6a']],
            opacity=0.8, showscale=False
        ))

    fig_factory.update_layout(
        title=dict(text=f"SYNTEGRA Tesis Planı | {f_extractors}x{f_volume}L | {f_pressure} Bar | {f_temp}°C",
                   font=dict(color="#D4AF37", size=16)),
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                   bgcolor='#0B0F19', camera=dict(eye=dict(x=0, y=-2.5, z=2))),
        paper_bgcolor='#0B0F19', height=500, showlegend=False, margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig_factory, use_container_width=True, key="plot_t11_factory")

# ================================================================
# T12: CANLI DİJİTAL İKİZ DASHBOARD
# ================================================================
with t12:
    st.header("📈 Canlı Dijital İkiz Dashboard")
    st.info("💡 Simülasyon Modu: Gerçek zamanlı sensör verileri canlandırılmaktadır.")

    live_c1, live_c2, live_c3, live_c4 = st.columns(4)
    sim_pressure = 487 + random.randint(-15, 15)
    sim_temp = 58 + random.randint(-3, 3)
    sim_flow = 85 + random.randint(-5, 5)
    sim_yield = 94 + random.randint(-2, 2)

    live_c1.metric("Basınç", f"{sim_pressure} Bar", delta=f"{random.randint(-3,3)} Bar")
    live_c2.metric("Sıcaklık", f"{sim_temp}°C", delta=f"{random.randint(-1,1)}°C")
    live_c3.metric("Akış Hızı", f"{sim_flow} L/dk")
    live_c4.metric("Verim", f"{sim_yield}%")

    st.divider()

    hours = list(range(24))
    pressure_data = [490 + random.randint(-20, 20) for _ in hours]
    temp_data = [58 + random.randint(-5, 5) for _ in hours]

    fig_twin = go.Figure()
    fig_twin.add_trace(go.Scatter(x=hours, y=pressure_data, mode="lines+markers", name="Basınç (Bar)", line=dict(color="#00D2BA", width=2)))
    fig_twin.add_trace(go.Scatter(x=hours, y=temp_data, mode="lines+markers", name="Sıcaklık (°C)", line=dict(color="#FF8C00", width=2), yaxis="y2"))

    fig_twin.update_layout(
        plot_bgcolor='#0B0F19', paper_bgcolor='#0B0F19',
        font=dict(color="white"),
        xaxis=dict(title="Saat", gridcolor="#1a1a2e"),
        yaxis=dict(title="Basınç (Bar)", gridcolor="#1a1a2e"),
        yaxis2=dict(title="Sıcaklık (°C)", overlaying="y", side="right", gridcolor="#1a1a2e"),
        legend=dict(x=0.01, y=0.99), height=400
    )
    st.plotly_chart(fig_twin, use_container_width=True, key="plot_t12_twin")
# ================================================================
# T13: GERÇEK AI VİDEO ÜRETİMİ (Hugging Face CogVideoX)
# ================================================================
with st.tabs(["🎬 Gerçek AI"])[0]:
    st.header("🎬 Gerçek AI Video Üretimi (CogVideoX-5B)")
    st.write("OpenCV çizimi DEĞİL — Hugging Face'in CogVideoX modeli ile gerçek fotogerçekçi sinematik videolar üretin.")

    hf_key = st.text_input("Hugging Face API Key (hf_xxxxx):",
        type="password", key="t13_key",
        help="huggingface.co → Settings → Access Tokens → New Token (Read)")

    st.divider()

    mode = st.radio("Üretim Modu:", [
        "🎯 Tek Sahne Videosu",
        "🎬 Tam Film (Tüm Sahneler)"
    ], key="t13_mode")

    if mode == "🎯 Tek Sahne Videosu":
        prompt = st.text_area("Video Prompt (İngilizce, detaylı):",
            "Cinematic aerial drone shot of a massive petrochemical refinery at golden hour, "
            "steam rising from distillation columns, steel pipelines stretching to horizon, "
            "warm amber lighting, 4K documentary style",
            height=100, key="t13_prompt")

        if st.button("🎬 Gerçek AI Video Üret", type="primary", key="t13_single"):
            if not hf_key:
                st.error("⚠️ Hugging Face API key gerekli!")
            else:
                from director_engine import RealAIVideo
                with st.spinner("CogVideoX-5B ile gerçek video üretiliyor... (2-5 dakika)"):
                    result = RealAIVideo.generate_video(prompt, hf_key)

                if result["status"] == "ok":
                    st.success("✅ Gerçek AI videosu hazır!")
                    st.video(result["path"])
                    with open(result["path"], "rb") as f:
                        st.download_button("📥 İndir", f.read(), result["path"], "video/mp4", key="t13_dl")
                elif result["status"] == "loading":
                    st.warning(f"⏳ {result['msg']}")
                elif result["status"] == "rate_limit":
                    st.warning(f"⚠️ {result['msg']}")
                else:
                    st.error(f"❌ {result.get('msg','Hata')}")

    else:
        st.info("Mevcut film planındaki tüm sahneler için gerçek AI videoları üretilecek. "
                "Bu işlem 20-60 dakika sürebilir (ücretsiz tier'da model yükleme bekleme süresi dahil).")

        if st.button("🎬 TÜM FİLMİ GERÇEK AI İLE ÜRET", type="primary", key="t13_full"):
            if not hf_key:
                st.error("⚠️ Hugging Face API key gerekli!")
            elif not st.session_state.film_plan:
                st.warning("⚠️ Önce 'AI Yönetmen' sekmesinden film planı oluşturun!")
            else:
                from director_engine import RealAIVideo
                progress = st.progress(0, text="Başlatılıyor...")

                def update(pct, msg):
                    progress.progress(pct / 100, text=f"{pct}% — {msg}")

                with st.spinner("Tam film gerçek AI ile üretiliyor..."):
                    result = RealAIVideo.generate_full_film(
                        st.session_state.film_plan, hf_key,
                        output_name="REAL_AI_FILM",
                        progress_callback=update
                    )

                if result["status"] == "success":
                    st.balloons()
                    st.success(f"🎉 Gerçek AI filmi hazır! ({result['duration']:.0f}sn)")
                    st.video(result["output"])
                else:
                    st.error(f"❌ {result.get('error','Hata')}")
                    with st.expander("📋 Log"):
                        for line in result.get("log", []):
                            st.text(line)

# ================================================================
# FOOTER
# ================================================================
st.divider()
st.caption("Arşen Process Cinema Studio v8.0 — Full Enterprise Edition")