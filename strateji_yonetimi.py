import json
import os

DOSYA_ADI = "kayitli_stratejiler.json"

# Varsayılan (Başlangıç) Stratejisi
VARSAYILAN_KOD = """# 1. Tabloyu Seç
df = veriler.get('MALIYET_ALICI-1')

if df is not None:
    # 2. Temizlik
    df.columns = df.columns.astype(str).str.strip().str.replace(' ', '_').str.upper()
    
    # 3. İşlem
    hedef = 'ALIS_ADET'
    if hedef in df.columns:
        df[hedef] = pd.to_numeric(df[hedef], errors='coerce').fillna(0)
        sonuc = df.sort_values(hedef, ascending=False).head(10)
    else:
        sonuc = pd.DataFrame(["Sütun bulunamadı"])
else:
    sonuc = pd.DataFrame(["Dosya seçilmedi"])
"""

def stratejileri_yukle():
    """Kayıtlı stratejileri dosyadan okur."""
    if not os.path.exists(DOSYA_ADI):
        # Dosya yoksa oluştur ve varsayılanı ekle
        veriler = {"Örnek: Alıcı Sıralama": VARSAYILAN_KOD}
        with open(DOSYA_ADI, "w", encoding="utf-8") as f:
            json.dump(veriler, f, ensure_ascii=False, indent=4)
        return veriler
    
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def strateji_kaydet(isim, kod):
    """Yeni bir strateji kaydeder."""
    mevcutlar = stratejileri_yukle()
    mevcutlar[isim] = kod
    
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(mevcutlar, f, ensure_ascii=False, indent=4)
    return True

def strateji_sil(isim):
    """Stratejiyi siler."""
    mevcutlar = stratejileri_yukle()
    if isim in mevcutlar:
        del mevcutlar[isim]
        with open(DOSYA_ADI, "w", encoding="utf-8") as f:
            json.dump(mevcutlar, f, ensure_ascii=False, indent=4)
        return True
    return False