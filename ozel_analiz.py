import pandas as pd
import numpy as np

# =============================================================================
# 🧠 DİNAMİK KOD ÇALIŞTIRICI (DÜZELTİLDİ)
# =============================================================================
def calistir(kod_metni, secilen_tablolar_sozlugu):
    """
    Arayüzden gelen kodu çalıştırır.
    """
    # Kullanıcının kod içinde kullanabileceği hazır değişkenler
    # HATA ÇÖZÜMÜ: pd ve np'yi hem local hem global alana koyuyoruz.
    calisma_ortami = {
        "pd": pd,
        "np": np,
        "veriler": secilen_tablolar_sozlugu,
        "sonuc": None
    }
    
    try:
        # --- DÜZELTME BURADA ---
        # Eskiden: exec(kod_metni, {}, calisma_ortami) -> Hata veriyordu
        # Şimdi: exec(kod_metni, calisma_ortami) -> Fonksiyonlar pd'yi görür
        exec(kod_metni, calisma_ortami)
        
        # Sonuç değişkenini al
        final_df = calisma_ortami.get("sonuc")
        
        if isinstance(final_df, pd.DataFrame):
            return True, final_df, "Başarılı"
        elif isinstance(final_df, (list, dict, str, int, float)):
            return True, pd.DataFrame([{"Sonuç": final_df}]), "Başarılı"
        else:
            return False, None, "Kod çalıştı ama 'sonuc' adında bir tablo üretmedi."
            
    except Exception as e:
        return False, None, str(e)

# =============================================================================
# ⚙️ SİSTEM ALTYAPISI (VERİ BİRLEŞTİRME & TEMİZLEME)
# =============================================================================

def make_unique(columns):
    seen = {}
    new_cols = []
    for col in columns:
        c = str(col).strip()
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}.{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)
    return new_cols

def temizle(df):
    if df.empty: return pd.DataFrame()
    
    # Başlık Bul
    header_idx = -1
    for i in range(min(10, len(df))):
        row = df.iloc[i].astype(str).str.upper().tolist()
        if any(x in row for x in ["SEMBOL", "KOD", "ENIYI", "FIYAT", "ACILIS"]):
            header_idx = i
            break
            
    if header_idx != -1:
        df.columns = make_unique(df.iloc[header_idx].tolist())
        df = df.iloc[header_idx+1:].reset_index(drop=True)
    else:
        df.columns = make_unique(df.columns.tolist())

    # Sütun Temizliği
    new_cols = []
    for col in df.columns:
        c_upper = str(col).upper().strip().replace(" ", "_")
        if c_upper in ["SEMBOL", "KOD"]:
            new_cols.append("SEMBOL")
        else:
            new_cols.append(c_upper)
    df.columns = new_cols

    # Sembol Temizliği
    if "SEMBOL" in df.columns:
        df = df[df["SEMBOL"].notna()]
        df["SEMBOL"] = df["SEMBOL"].astype(str).str.strip()
    
    # Sayısal Dönüşüm
    for col in df.columns:
        if col != "SEMBOL" and "KURUM" not in col:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

def verileri_hazirla(sayfalar):
    """Tabloları birleştirip Ham Veri oluşturur"""
    tum_semboller = set()
    temiz_sayfalar = {}
    
    for name, df in sayfalar.items():
        try:
            cl = temizle(df.copy())
            if not cl.empty and "SEMBOL" in cl.columns:
                tum_semboller.update(cl["SEMBOL"].unique())
                temiz_sayfalar[name] = cl
        except: pass
        
    if not tum_semboller: return pd.DataFrame()
    
    df_master = pd.DataFrame(sorted(list(tum_semboller)), columns=["SEMBOL"])
    
    for name, df in temiz_sayfalar.items():
        # Sütunlara dosya adı ekle (Çakışma önle)
        suffix = "_" + name.upper().replace(" ", "").replace("-", "").replace(".", "")
        rename_map = {c: f"{c}{suffix}" for c in df.columns if c != "SEMBOL"}
        df = df.rename(columns=rename_map)
        
        df_master = pd.merge(df_master, df, on="SEMBOL", how="left")
        
    return df_master.fillna(0)