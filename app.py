import streamlit as st
import pandas as pd
import os
import time
import sys
import importlib

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Berlin Kaplanı v1.2", 
    layout="wide", 
    page_icon="🦁",
    initial_sidebar_state="expanded"
)

# --- SİSTEM KONTROLLERİ ---
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
except:
    script_dir = os.getcwd()
    sys.path.insert(0, script_dir)

try:
    from data_processor import process_files_separately
    import ozel_analiz
    import strateji_yonetimi 
except ImportError as e:
    st.error(f"Sistem Dosyası Eksik: {e}")
    st.stop()

CSV_KLASORU = os.path.join(script_dir, 'CSV_Verileri')

# --- TASARIM MOTORU (SADE & BEYAZ) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Orbitron:wght@900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap');

    .stApp {
        background-color: #F8F9FA;
        color: #2C3E50;
    }

    .header-style {
        font-family: 'Orbitron', sans-serif;
        font-size: 40px;
        color: #E67E22;
        margin-bottom: 5px;
    }
    
    .welcome-style {
        font-family: 'Dancing Script', cursive;
        font-size: 30px;
        color: #34495E;
        border-bottom: 2px solid #E67E22;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        border: 1px solid #E67E22;
        color: #E67E22;
        background-color: white;
    }
    .stButton>button:hover {
        background-color: #E67E22;
        color: white;
    }
    
    .notify-box {
        background-color: #D5F5E3;
        border: 1px solid #2ECC71;
        color: #27AE60;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- RENKLENDİRME ---
def renklendir(val):
    if isinstance(val, str):
        val = val.upper()
        if "AL" in val: return 'color: #27AE60; font-weight: bold' 
        if "SAT" in val: return 'color: #C0392B; font-weight: bold'
        if "YÜKSEK" in val or "FIRSAT" in val: return 'color: #E67E22; font-weight: bold'
    return ''

# --- EVRENSEL DOSYA OKUYUCU ---
def universal_dosya_oku(yol, dosya_adi):
    try:
        df = pd.read_csv(yol, header=None, dtype=str)
        header_idx = -1
        for i in range(min(20, len(df))):
            row = df.iloc[i].astype(str).str.upper().tolist()
            if any(x in row for x in ["SEMBOL", "KOD", "ENIYI"]):
                header_idx = i
                break
        
        if header_idx != -1:
            df.columns = df.iloc[header_idx]
            df = df.iloc[header_idx+1:].reset_index(drop=True)
        else:
            df = pd.read_csv(yol, dtype=str)

        df.columns = df.columns.astype(str).str.strip()
        seen = {}
        new_cols = []
        for col in df.columns:
            c = str(col)
            if c in seen:
                seen[c] += 1
                new_cols.append(f"{c}.{seen[c]}")
            else:
                seen[c] = 0
                new_cols.append(c)
        df.columns = new_cols
        return df
    except Exception as e:
        return pd.DataFrame([f"Hata: {e}"])

# =============================================================================
# 🏠 ANA UYGULAMA
# =============================================================================

# --- SOL MENÜ ---
with st.sidebar:
    st.title("🎛️ KONTROL PANELİ")
    st.caption("Sistem v1.2")
    
    if st.button("🔄 VERİLERİ GÜNCELLE", width="stretch"): 
        with st.spinner("İşleniyor..."):
            if process_files_separately():
                st.success("Veriler Güncel!")
                st.cache_data.clear()
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Bağlantı Hatası")
    
    st.markdown("---")
    st.caption("STRATEJİ YÖNETİMİ")
    
    kayitli = strateji_yonetimi.stratejileri_yukle()
    liste = ["Yeni (Boş Sayfa)"] + list(kayitli.keys())
    
    def kod_guncelle():
        secim = st.session_state.get('secilen_strateji')
        if secim:
            if secim == "Yeni (Boş Sayfa)":
                st.session_state['kod_alani'] = strateji_yonetimi.VARSAYILAN_KOD
            elif secim in kayitli:
                st.session_state['kod_alani'] = kayitli[secim]

    secilen_strateji = st.selectbox("Formüller:", liste, key='secilen_strateji', on_change=kod_guncelle)

# --- ANA EKRAN ---
st.markdown('<div class="header-style">BERLİN KAPLANI</div>', unsafe_allow_html=True)
st.markdown('<div class="welcome-style">Hoşgeldiniz Sayın Emre Bey</div>', unsafe_allow_html=True)

if not os.path.exists(CSV_KLASORU): os.makedirs(CSV_KLASORU)
dosyalar = sorted([f for f in os.listdir(CSV_KLASORU) if f.endswith('.csv')])

if not dosyalar:
    st.warning("Veri yok. Soldan güncelleyin.")
    st.stop()

# --- SEKMELER ---
tab1, tab2 = st.tabs(["📂 DOSYA GEZGİNİ", "⚡ ANALİZ MASASI"])

# 1. DOSYA GEZGİNİ
with tab1:
    c1, c2 = st.columns([1, 4])
    with c1:
        secilen_dosya = st.radio("Listeden Seç:", dosyalar, label_visibility="collapsed")
    with c2:
        if secilen_dosya:
            try:
                path = os.path.join(CSV_KLASORU, secilen_dosya)
                df_view = universal_dosya_oku(path, secilen_dosya)
                if not df_view.empty:
                    st.dataframe(df_view, height=600, use_container_width=True)
                else:
                    st.warning("Dosya Boş.")
            except: st.error("Dosya Okuma Hatası")

# 2. ANALİZ MASASI
with tab2:
    with st.expander("🛠️ Strateji Editörü", expanded=True):
        col_set, col_code = st.columns([1, 2])
        
        with col_set:
            st.caption("1. Veri Kaynakları")
            # DEFAULT BOŞ
            secilenler = st.multiselect("Tabloları Seç:", dosyalar, default=[])
            
            yuklenen_veriler = {}
            if secilenler:
                for f in secilenler:
                    try: yuklenen_veriler[f.replace(".csv", "")] = universal_dosya_oku(os.path.join(CSV_KLASORU, f), f)
                    except: pass
                st.info(f"{len(yuklenen_veriler)} Tablo Hazır.")

        with col_code:
            st.caption("2. Python Formülü")
            if 'kod_alani' not in st.session_state:
                st.session_state['kod_alani'] = strateji_yonetimi.VARSAYILAN_KOD
            
            kod = st.text_area("Kod:", height=200, key="kod_alani", label_visibility="collapsed")
            
            c_run, c_save, c_del = st.columns([3, 2, 1])
            with c_run:
                if st.button("🚀 ANALİZİ BAŞLAT", width="stretch", type="primary"):
                    if not yuklenen_veriler:
                        st.error("Lütfen tablo seçin.")
                    else:
                        importlib.reload(ozel_analiz)
                        basari, df_sonuc, msj = ozel_analiz.calistir(kod, yuklenen_veriler)
                        if basari:
                            st.session_state['sonuc'] = df_sonuc
                            st.success("İşlem Tamamlandı.")
                        else: st.error(f"Hata: {msj}")
            with c_save:
                if st.button("💾 Kaydet", width="stretch"): st.session_state['kaydet_modu'] = True
            with c_del:
                if secilen_strateji != "Yeni (Boş Sayfa)":
                     if st.button("🗑️"):
                        strateji_yonetimi.strateji_sil(secilen_strateji)
                        st.rerun()

            if st.session_state.get('kaydet_modu', False):
                with st.form("kayit_form"):
                    yeni_isim = st.text_input("Strateji Adı:", value=secilen_strateji if "Yeni" not in secilen_strateji else "")
                    c_onay, c_iptal = st.columns(2)
                    with c_onay:
                         if st.form_submit_button("✅ Onayla"):
                            if yeni_isim:
                                strateji_yonetimi.strateji_kaydet(yeni_isim, kod)
                                st.session_state['kaydet_modu'] = False
                                st.rerun()
                    with c_iptal:
                        if st.form_submit_button("❌ İptal"):
                            st.session_state['kaydet_modu'] = False
                            st.rerun()

    # Alt Kısım: SONUÇLAR (SADE)
    st.markdown("### 📊 Piyasa Analiz Sonuçları")
    
    if 'sonuc' in st.session_state:
        res = st.session_state['sonuc']
        
        # --- HAP BİLGİ (HATA DÜZELTİLDİ: str(c) eklendi) ---
        # Artık sütun ismi sayı (0) gelse bile str(0) yapıp string'e çeviriyor, çökme olmuyor.
        score_col = next((c for c in res.columns if any(x in str(c).upper() for x in ["PUAN", "SCORE", "SKOR"])), None)
        alici_col = next((c for c in res.columns if any(x in str(c).upper() for x in ["ALICI", "GUC"])), None)
        gap_col = next((c for c in res.columns if any(x in str(c).upper() for x in ["GAP", "YUZDE"])), None)
        
        if score_col and not res.empty:
            res[score_col] = pd.to_numeric(res[score_col], errors='coerce').fillna(0)
            best_score = res.sort_values(score_col, ascending=False).iloc[0]
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Lider Hisse", best_score['Hisse' if 'Hisse' in res.columns else 'SEMBOL'], f"{best_score[score_col]:.0f} Puan")
            m2.metric("Toplam Hisse", len(res))
            
            if alici_col:
                res[alici_col] = pd.to_numeric(res[alici_col], errors='coerce').fillna(0)
                best_alici = res.sort_values(alici_col, ascending=False).iloc[0]
                m3.metric("En Güçlü Alıcı", best_alici['Hisse' if 'Hisse' in res.columns else 'SEMBOL'], f"{best_alici[alici_col]:.2f}x")
            
            if gap_col:
                res[gap_col] = pd.to_numeric(res[gap_col], errors='coerce').fillna(0)
                neg_gaps = res[res[gap_col] < 0]
                best_gap = neg_gaps.sort_values(score_col, ascending=False).iloc[0] if not neg_gaps.empty else best_score
                m4.metric("Dip Fırsatı", best_gap['Hisse' if 'Hisse' in res.columns else 'SEMBOL'], f"%{best_gap[gap_col]:.2f}")

        st.markdown("---")
        st.dataframe(res.style.map(renklendir), height=600, use_container_width=True)
        
        csv = res.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Excel Olarak İndir", csv, "analiz_sonucu.csv", "text/csv")
        
    else:
        st.info("Lütfen tablolardan seçim yapıp 'ANALİZİ BAŞLAT' butonuna basın.")