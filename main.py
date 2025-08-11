import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
import os

LOGO_PATH = "tds_logo.png"
KULLANICI_DOSYA = "kullanicilar.json"
OPERATOR_DOSYA = "operatorler.json"
HATAKOD_DOSYA = "hatakodlari.json"
ISKOD_DOSYA = "iskodlari.json"

VARSAYILAN_KULLANICILAR = {
    "admin": "1234",
    "Arda Ertan": "1234",
    "Emrah Karaman": "1234",
    "Elif Kaya": "abc1",
    "Berk Aslan": "berk42",
    "Zeynep Gül": "zeynep!"
}
VARSAYILAN_OPERATORLER = [
    "Sercan Gür", "Salim Tanrıkulu", "Ali Sucu", "İsa Akça", "Mürsel Gümüşsoy",
    "Yunus Kılıç", "Ş Muratoğlu", "Arda Ertan", "Furkan Ekin", "Burak Polat",
    "Canan Gül", "Elif Yüce", "Derya Aksu", "Ece Baran", "Berk Aslan",
    "Hüseyin Sevim", "Yusuf Uzun", "Emre Sarı", "Seda Öztürk", "Zeynep Yıldız"
]
VARSAYILAN_HATAKODLARI = [
    "HT01", "HT02", "HT03", "HT04", "HT05", "HT06", "HT07", "HT08", "HT09", "HT10"
]
VARSAYILAN_ISKODLARI = [f"{i:03}" for i in range(1, 301)]
ADMINS = ["admin"]

def load_or_init(filename, default):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default.copy() if isinstance(default, list) else dict(default)
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

st.markdown("""
<style>
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(90deg, #2572f7 0%, #8fd3fe 100%);
    color: #fff !important;
    font-weight: 500;
    border: none;
    border-radius: 10px;
    padding: 7px 24px;
    box-shadow: 0 1px 8px #b1cffc33;
    transition: background 0.2s;
    margin-bottom: 8px;
    font-size: 1rem;
}
.stButton>button:hover, .stDownloadButton>button:hover {
    background: linear-gradient(90deg, #195ec2 0%, #61a1f8 100%);
    color: #fff !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg,#f1f9ff 0%,#d6edff 100%) !important;
    color: #195ec2 !important;
}
.stTabs [aria-selected="false"] {
    color: #2572f7 !important;
}
</style>
""", unsafe_allow_html=True)

def get_image_base64(img_path):
    import base64
    try:
        with open(img_path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    except Exception as e:
        st.error(f"Logo okunamadı: {e}")
        return ""

def logo_header():
    st.markdown(
        f"""
        <style>
        .custom-logo-header {{
            position: absolute;
            top: 28px;
            right: 38px;
            z-index: 100;
            background: white;
            padding: 4px 18px 4px 6px;
            border-radius: 12px;
            box-shadow: 0 2px 6px #00000011;
        }}
        </style>
        <div class="custom-logo-header">
            <img src="data:image/png;base64,{get_image_base64(LOGO_PATH)}" width="165"/>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h3 style='margin-bottom:0px; margin-top:10px; font-size:2.1rem;'>İşleme  Üretim Takibi</h3>",
        unsafe_allow_html=True
    )
    st.write("---")

def main_app():
    st.set_page_config(layout="wide")
    logo_header()

    kullanicilar = load_or_init(KULLANICI_DOSYA, VARSAYILAN_KULLANICILAR)
    operatorler = load_or_init(OPERATOR_DOSYA, VARSAYILAN_OPERATORLER)
    hatakodlari = load_or_init(HATAKOD_DOSYA, VARSAYILAN_HATAKODLARI)
    iskodlari = load_or_init(ISKOD_DOSYA, VARSAYILAN_ISKODLARI)

    def load_data():
        if os.path.exists("raporlar.json"):
            with open("raporlar.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_data(data):
        with open("raporlar.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def delete_all_data():
        if os.path.exists("raporlar.json"):
            os.remove("raporlar.json")

    sekme_ikon = [
        "📝 Veri Girişi",
        "📋 Kayıtlar",
        "🔍 Raporlar & Filtreleme",
        "📊 Grafikler"
    ]
    if st.session_state.get("giris") and st.session_state.get("kullanici") in ADMINS:
        sekme_ikon.append("🔑 Admin Paneli")
    tab1, tabKayitlar, tab2, tab3, *admin_tab = st.tabs(sekme_ikon)

    # --- 1. SEKME: VERİ GİRİŞİ ---
    with tab1:
        col1, col2 = st.columns([2,1])
        with col1:
            tarih = st.date_input("Tarih (GG-AA-YYYY)", value=datetime.today()).strftime("%d-%m-%Y")
        with col2:
            vardiya = st.selectbox("Vardiya", ["Gündüz", "Gece"])

        st.markdown("<div style='margin-bottom: -18px;'></div>", unsafe_allow_html=True)
        st.markdown("<h5 style='margin-bottom: 4px; margin-top: 6px;'>Üretim Tablosu</h5>", unsafe_allow_html=True)

        satir_sayisi = 13
        default_rows = [{
            "Makine": f"T{i:02}",
            "İş Kodu": "",
            "Operatör": "",
            "Üretim": 0,
            "Hurda": 0,
            "Kod": "",
            "Açıklama": "",
            "Hedef": 0
        } for i in range(1, satir_sayisi+1)]

        df = pd.DataFrame(default_rows)

        df_edit = st.data_editor(
            df,
            column_config={
                "Makine": st.column_config.TextColumn(width="small"),
                "İş Kodu": st.column_config.SelectboxColumn(options=[""] + iskodlari, width="small"),
                "Operatör": st.column_config.SelectboxColumn(options=[""] + operatorler, width="medium"),
                "Üretim": st.column_config.NumberColumn(width="small", step=1, min_value=0),
                "Hurda": st.column_config.NumberColumn(width="small", step=1, min_value=0),
                "Kod": st.column_config.SelectboxColumn(options=[""] + hatakodlari, width="small"),
                "Açıklama": st.column_config.TextColumn(width="large"),
                "Hedef": st.column_config.NumberColumn(width="small", step=1, min_value=0),
            },
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
            key="uretim_tablosu"
        )

        if st.button("KAYDET", type="primary"):
            kayitlar = [
                row for row in df_edit.to_dict("records")
                if any([row["İş Kodu"], row["Operatör"], row["Üretim"], row["Hurda"], row["Kod"], row["Açıklama"], row["Hedef"]])
            ]
            if kayitlar:
                data = load_data()
                data.append({
                    "tarih": tarih,
                    "vardiya": vardiya,
                    "zaman": datetime.now().strftime("%d-%m-%Y %H:%M"),
                    "satirlar": kayitlar
                })
                save_data(data)
                st.success("Tablo kaydedildi!")
            else:
                st.warning("Hiçbir satırda veri yok.")

    # --- 2. SEKME: KAYITLAR ---
    with tabKayitlar:
        st.subheader("Kayıtlar", divider=True)
        data = load_data()
        if data:
            if "tum_sil_onay" not in st.session_state:
                st.session_state.tum_sil_onay = False

            if st.button("Tüm Kayıtları Kalıcı Olarak Sil", type="secondary"):
                st.session_state.tum_sil_onay = True

            if st.session_state.tum_sil_onay:
                st.warning("Bu işlem tüm kayıtları GERİ DÖNÜŞÜMSÜZ siler. Emin misiniz?")
                col_yes, col_no = st.columns([1,1])
                if col_yes.button("Evet, hepsini sil!", type="primary"):
                    delete_all_data()
                    st.success("Tüm kayıtlar silindi! Sayfayı yenileyin.")
                    st.session_state.tum_sil_onay = False
                    st.rerun()
                if col_no.button("İptal", type="secondary"):
                    st.session_state.tum_sil_onay = False

        if not data:
            st.info("Henüz kayıt yok.")
        else:
            tum_gunler = sorted(list({r.get("tarih", "") for r in data if r.get("tarih", "")}))
            sec_gun = st.selectbox("Günü Seç", ["Tümü"] + tum_gunler, key="gun_kayitlar")

            for i, rapor in reversed(list(enumerate(data))):
                if sec_gun != "Tümü" and rapor.get("tarih", "") != sec_gun:
                    continue
                zaman = rapor.get('zaman', '')
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:18px;font-size:1.1rem;margin-top:8px;'>"
                    f"<span style='font-size:1.2rem;'>&#128197;</span>"
                    f"<b>{rapor.get('tarih','?')} / {rapor.get('vardiya','?')}</b>"
                    f"<span style='color:#555; font-size:1rem;'>— {zaman}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                df_rapor = pd.DataFrame(rapor.get("satirlar", []))
                if not df_rapor.empty:
                    st.dataframe(df_rapor, use_container_width=True)
                else:
                    st.info("Bu raporda kayıtlı satır yok.")
                if st.button("Günü Sil", key=f"gun_sil_{i}", help="Bu günün tüm kayıtlarını siler!"):
                    st.session_state.gun_sil_idx = i
                if st.session_state.get("gun_sil_idx") == i:
                    col_gun1, col_gun2 = st.columns([1,2])
                    with col_gun1:
                        if st.button("Eminim, silinsin!", key=f"gun_sil_em_{i}", type="primary"):
                            data.pop(i)
                            save_data(data)
                            st.session_state.gun_sil_idx = None
                            st.rerun()
                    with col_gun2:
                        if st.button("İptal", key=f"gun_iptal_{i}", type="secondary"):
                            st.session_state.gun_sil_idx = None

    # --- 3. SEKME: RAPORLAR & FİLTRELEME ---
    with tab2:
        st.subheader("Raporlar ve Filtreleme", divider=True)
        data = load_data()
        if not data:
            st.info("Henüz kayıt yok.")
        else:
            all_rows = []
            for rapor in data:
                for satir in rapor.get("satirlar", []):
                    all_rows.append({
                        "Tarih": rapor.get("tarih", ""),
                        "Vardiya": rapor.get("vardiya", ""),
                        "Makine": satir.get("Makine", ""),
                        "İş Kodu": satir.get("İş Kodu", ""),
                        "Operatör": satir.get("Operatör", ""),
                        "Üretim": satir.get("Üretim", 0),
                        "Hurda": satir.get("Hurda", 0),
                        "Kod": satir.get("Kod", ""),
                        "Açıklama": satir.get("Açıklama", ""),
                        "Hedef": satir.get("Hedef", 0)
                    })
            df_all = pd.DataFrame(all_rows)

            min_date = max_date = None
            if not df_all.empty:
                df_all["Tarih_dt"] = pd.to_datetime(df_all["Tarih"], format="%d-%m-%Y", errors='coerce')
                min_date = df_all["Tarih_dt"].min()
                max_date = df_all["Tarih_dt"].max()
            else:
                min_date = max_date = datetime.today()

            col1, col2 = st.columns(2)
            with col1:
                tarih_bas = st.date_input("Başlangıç Tarihi", value=min_date if min_date is not None else datetime.today())
            with col2:
                tarih_bit = st.date_input("Bitiş Tarihi", value=max_date if max_date is not None else datetime.today())

            col3, col4, col5, col6 = st.columns(4)
            vardiya_f = col3.selectbox("Vardiya", ["Tümü"] + sorted(df_all["Vardiya"].unique()), index=0)
            makine_f = col4.selectbox("Makine", ["Tümü"] + sorted(df_all["Makine"].unique()), index=0)
            op_f = col5.selectbox("Operatör", ["Tümü"] + sorted(df_all["Operatör"].unique()), index=0)
            is_kodu_f = col6.selectbox("İş Kodu", ["Tümü"] + sorted(df_all["İş Kodu"].unique()), index=0)

            filtre = df_all.copy()
            if not filtre.empty:
                filtre["Tarih_dt"] = pd.to_datetime(filtre["Tarih"], format="%d-%m-%Y", errors='coerce')
                filtre = filtre[(filtre["Tarih_dt"] >= pd.to_datetime(tarih_bas)) & (filtre["Tarih_dt"] <= pd.to_datetime(tarih_bit))]

            if vardiya_f != "Tümü":
                filtre = filtre[filtre["Vardiya"] == vardiya_f]
            if makine_f != "Tümü":
                filtre = filtre[filtre["Makine"] == makine_f]
            if op_f != "Tümü":
                filtre = filtre[filtre["Operatör"] == op_f]
            if is_kodu_f != "Tümü":
                filtre = filtre[filtre["İş Kodu"] == is_kodu_f]

            toplam_uretim = filtre["Üretim"].sum()
            toplam_hurda = filtre["Hurda"].sum()
            gunduz_uretim = filtre[filtre["Vardiya"] == "Gündüz"]["Üretim"].sum()
            gece_uretim = filtre[filtre["Vardiya"] == "Gece"]["Üretim"].sum()

            st.dataframe(filtre.drop(columns=["Tarih_dt"]), use_container_width=True)
            st.markdown(
                f"""
                <div class="custom-summary-bar" style='
                    margin-top: 0.5em;
                    margin-bottom: 1.2em;
                    background: #f4f7fa;
                    border-top: 1.5px solid #c5def6;
                    padding: 6px 18px;
                    font-size: 0.95rem;
                    color: #222;
                    display: flex;
                    gap: 32px;
                    justify-content: flex-start;
                '>
                    <span><b>Toplam Üretim:</b> {toplam_uretim}</span>
                    <span><b>Toplam Hurda:</b> {toplam_hurda}</span>
                    <span><b>Gündüz Üretim:</b> {gunduz_uretim}</span>
                    <span><b>Gece Üretim:</b> {gece_uretim}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    # --- 4. SEKME: GRAFİKLER ---
    with tab3:
        st.subheader("Grafik Analizler", divider=True)
        data = load_data()
        if not data:
            st.info("Henüz kayıt yok.")
        else:
            all_rows = []
            for rapor in data:
                for satir in rapor.get("satirlar", []):
                    all_rows.append({
                        "Tarih": rapor.get("tarih", ""),
                        "Vardiya": rapor.get("vardiya", ""),
                        "Makine": satir.get("Makine", ""),
                        "Operatör": satir.get("Operatör", ""),
                        "İş Kodu": satir.get("İş Kodu", ""),
                        "Üretim": satir.get("Üretim", 0),
                        "Hurda": satir.get("Hurda", 0),
                        "Kod": satir.get("Kod", ""),
                        "Hedef": satir.get("Hedef", 0)
                    })
            df_all = pd.DataFrame(all_rows)
            grafik_sekmeleri = st.tabs([
                "Makine Bazında Üretim/Hurda",
                "Operatör Bazında Üretim",
                "İş Kodu Bazında Üretim",
                "Verim (Makine)",
                "Verim (Operatör)",
                "Günlük Toplamlar",
            ])
            with grafik_sekmeleri[0]:
                df_group = df_all.groupby("Makine")[["Üretim", "Hurda"]].sum().reset_index()
                st.plotly_chart(
                    px.bar(df_group, x="Makine", y=["Üretim", "Hurda"], barmode="group", title="Makine Bazında Üretim ve Hurda"),
                    use_container_width=True
                )
            with grafik_sekmeleri[1]:
                df_op = df_all.groupby("Operatör")[["Üretim", "Hurda"]].sum().reset_index()
                st.plotly_chart(
                    px.bar(df_op, x="Operatör", y=["Üretim", "Hurda"], barmode="group", title="Operatör Bazında Üretim ve Hurda"),
                    use_container_width=True
                )
            with grafik_sekmeleri[2]:
                df_kod = df_all.groupby("İş Kodu")[["Üretim", "Hurda"]].sum().reset_index()
                st.plotly_chart(
                    px.bar(df_kod, x="İş Kodu", y=["Üretim", "Hurda"], barmode="group", title="İş Kodu Bazında Üretim ve Hurda"),
                    use_container_width=True
                )
            with grafik_sekmeleri[3]:
                df_verim = df_all.groupby("Makine").apply(
                    lambda x: 100 * x["Üretim"].sum() / x["Hedef"].sum() if x["Hedef"].sum() else 0
                ).reset_index(name="Verim (%)")
                st.plotly_chart(
                    px.bar(df_verim, x="Makine", y="Verim (%)", title="Makine Bazında Verim (%)"),
                    use_container_width=True
                )
            with grafik_sekmeleri[4]:
                df_opverim = df_all.groupby("Operatör").apply(
                    lambda x: 100 * x["Üretim"].sum() / x["Hedef"].sum() if x["Hedef"].sum() else 0
                ).reset_index(name="Verim (%)")
                st.plotly_chart(
                    px.bar(df_opverim, x="Operatör", y="Verim (%)", title="Operatör Bazında Verim (%)"),
                    use_container_width=True
                )
            with grafik_sekmeleri[5]:
                df_tarih = df_all.groupby("Tarih")[["Üretim", "Hurda"]].sum().reset_index()
                st.plotly_chart(
                    px.line(df_tarih, x="Tarih", y=["Üretim", "Hurda"], markers=True, title="Günlük Toplam Üretim ve Hurda"),
                    use_container_width=True
                )

    # --- 5. SEKME: ADMIN PANELİ (Eğer admin ise) ---
    if admin_tab:
        with admin_tab[0]:
            st.header("🔑 Admin Paneli")
            st.info("Bu panel yalnızca admin tarafından görülebilir.")

            st.subheader("Kullanıcılar")
            with st.expander("Kullanıcıları Görüntüle / Ekle / Sil / Şifre Değiştir"):
                users = list(kullanicilar.keys())
                st.write("Kullanıcılar:", users)
                yeni_user = st.text_input("Yeni Kullanıcı Adı Ekle", "")
                yeni_pass = st.text_input("Yeni Kullanıcı Şifresi", "", type="password")
                if st.button("Kullanıcı Ekle"):
                    if yeni_user and yeni_pass:
                        if yeni_user not in kullanicilar:
                            kullanicilar[yeni_user] = yeni_pass
                            save_json(KULLANICI_DOSYA, kullanicilar)
                            st.success(f"{yeni_user} eklendi.")
                        else:
                            st.warning("Bu kullanıcı zaten var.")
                silinecek_user = st.selectbox("Silinecek Kullanıcı", [u for u in users if u not in ADMINS], key="kullanici_sil")
                if st.button("Kullanıcıyı Sil"):
                    if silinecek_user in kullanicilar:
                        del kullanicilar[silinecek_user]
                        save_json(KULLANICI_DOSYA, kullanicilar)
                        st.success(f"{silinecek_user} silindi.")
                sec_user = st.selectbox("Şifresini Değiştir", users, key="sifre_degistir")
                degis_pass = st.text_input("Yeni Şifre", "", type="password", key="degis_pass")
                if st.button("Şifreyi Güncelle"):
                    if degis_pass:
                        kullanicilar[sec_user] = degis_pass
                        save_json(KULLANICI_DOSYA, kullanicilar)
                        st.success(f"{sec_user} şifresi güncellendi.")

            st.subheader("Operatörler")
            with st.expander("Operatörleri Görüntüle / Ekle / Sil"):
                st.write("Operatörler:", operatorler)
                yeni_op = st.text_input("Yeni Operatör Ekle", "")
                if st.button("Operatör Ekle"):
                    if yeni_op and yeni_op not in operatorler:
                        operatorler.append(yeni_op)
                        save_json(OPERATOR_DOSYA, operatorler)
                        st.success(f"{yeni_op} eklendi.")
                sil_op = st.selectbox("Silinecek Operatör", operatorler, key="op_sil")
                if st.button("Operatörü Sil"):
                    if sil_op in operatorler:
                        operatorler.remove(sil_op)
                        save_json(OPERATOR_DOSYA, operatorler)
                        st.success(f"{sil_op} silindi.")

            st.subheader("Hata Kodları")
            with st.expander("Hata Kodlarını Görüntüle / Ekle / Sil"):
                st.write("Hata Kodları:", hatakodlari)
                yeni_hata = st.text_input("Yeni Hata Kodu Ekle", "")
                if st.button("Hata Kodu Ekle"):
                    if yeni_hata and yeni_hata not in hatakodlari:
                        hatakodlari.append(yeni_hata)
                        save_json(HATAKOD_DOSYA, hatakodlari)
                        st.success(f"{yeni_hata} eklendi.")
                sil_hata = st.selectbox("Silinecek Hata Kodu", hatakodlari, key="hata_sil")
                if st.button("Hata Kodunu Sil"):
                    if sil_hata in hatakodlari:
                        hatakodlari.remove(sil_hata)
                        save_json(HATAKOD_DOSYA, hatakodlari)
                        st.success(f"{sil_hata} silindi.")

            st.subheader("İş Kodları")
            with st.expander("İş Kodlarını Görüntüle / Ekle / Sil"):
                st.write("İş Kodları:", iskodlari)
                yeni_iskod = st.text_input("Yeni İş Kodu Ekle", "")
                if st.button("İş Kodu Ekle"):
                    if yeni_iskod and yeni_iskod not in iskodlari:
                        iskodlari.append(yeni_iskod)
                        save_json(ISKOD_DOSYA, iskodlari)
                        st.success(f"{yeni_iskod} eklendi.")
                sil_iskod = st.selectbox("Silinecek İş Kodu", iskodlari, key="iskod_sil")
                if st.button("İş Kodunu Sil"):
                    if sil_iskod in iskodlari:
                        iskodlari.remove(sil_iskod)
                        save_json(ISKOD_DOSYA, iskodlari)
                        st.success(f"{sil_iskod} silindi.")

def login_page():
    kullanicilar = load_or_init(KULLANICI_DOSYA, VARSAYILAN_KULLANICILAR)
    logo_header()
    user = st.selectbox("Kullanıcı Adı", list(kullanicilar.keys()))
    pwd = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", use_container_width=True):
        if kullanicilar.get(user) == pwd:
            st.session_state["giris"] = True
            st.session_state["kullanici"] = user
            st.success(f"Hoşgeldin, {user}!")
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre hatalı.")

if "giris" not in st.session_state or not st.session_state["giris"]:
    login_page()
else:
    main_app()


