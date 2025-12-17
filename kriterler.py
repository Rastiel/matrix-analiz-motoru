# kriterler.py

import pandas as pd

"""
Bu dosya, abinin gönderdiği görseldeki 'check_criteria' fonksiyonunu 
ve 'formül' olarak bahsettiğin kuralları içerir.
"""

# ---------------------------------------------------------------------
# 1. BÖLÜM: FORMÜLLER (KRİTER FONKSİYONLARI)
# ---------------------------------------------------------------------
# Her "formül" bir fonksiyondur (lambda). 
# Bu fonksiyon, o hisseye ait TÜM veriyi (data) alır ve bir kuralı test eder.
# DİKKAT: data['SütunAdı'].iloc[-1] o hissenin EN SON verisidir.

# FORMÜL 1: Son fiyatı 150'den yüksek olanlar
kural_fiyati_yuksek = lambda data: \
    data['Son_Fiyat'].iloc[-1] > 150

# FORMÜL 2: Son Kapanışı, son Açılışından yüksek olanlar (Pozitif Kapanış)
kural_pozitif_kapanis = lambda data: \
    data['Kapanış'].iloc[-1] > data['Açılış'].iloc[-1]

# FORMÜL 3: Son Fiyatı, o günkü En Yükseğine yakın olanlar (Zirvede Kapatanlar)
kural_en_yuksege_yakin = lambda data: \
    data['Son_Fiyat'].iloc[-1] >= (data['En_Yüksek'].iloc[-1] * 0.99) # %99 ve üzeri

# FORMÜL 4: (Abinin "B'den 4. sütun, 2. satır" örneğini yorumlayalım)
# Bu kural: "AKBNK'nin (TestVerisi'ndeki 2. satır veri) 'Son_Fiyat'ı (4. sütun veri) 90'dan düşük mü?"
# NOT: Bu kural çok spesifiktir, 'Hisse_Kodu' ve 'Son_Fiyat' sütunlarına ihtiyaç duyar
kural_akbank_kontrol = lambda data: \
    'AKBNK' not in data['Hisse_Kodu'].values or \
    data[data['Hisse_Kodu'] == 'AKBNK']['Son_Fiyat'].iloc[-1] < 90


# ---------------------------------------------------------------------
# 2. BÖLÜM: KRİTER LİSTESİ (Sitede görünecek menü)
# ---------------------------------------------------------------------
# Burası, sitedeki 'multiselect' kutusunda görünecek olan menüdür.
# 'name' -> Sitede görünecek ad
# 'func' -> Yukarıda tanımladığımız formülün adı

KRITER_LISTESI = [
    {
        'name': 'Fiyatı 150 den Yüksek Olanlar', 
        'func': kural_fiyati_yuksek
    },
    {
        'name': 'Pozitif Kapanış Yapanlar', 
        'func': kural_pozitif_kapanis
    },
    {
        'name': 'En Yükseğine Yakın Kapatanlar', 
        'func': kural_en_yuksege_yakin
    },
    {
        'name': 'AKBNK Kontrol (Fiyat < 90)', 
        'func': kural_akbank_kontrol
    },
    # Buraya dilediğin kadar yeni formül ve kriter ekleyebilirsin
]


# ---------------------------------------------------------------------
# 3. BÖLÜM: ANALİZ MOTORU (Abinin görseldeki kodu)
# ---------------------------------------------------------------------
# Bu fonksiyon, ham veriyi ve seçilen kriterleri alır, harmanlar.

def check_criteria(df, selected_criteria_names):
    """
    Veritabanını (df) alır ve kullanıcının seçtiği kriterlere (selected_criteria_names) 
    göre tüm hisseleri analiz eder.
    """
    
    # Seçilen kriterlerin fonksiyonlarını 'KRITER_LISTESI' içinden bul
    selected_criteria = [
        crit for crit in KRITER_LISTESI 
        if crit['name'] in selected_criteria_names
    ]
    
    if not selected_criteria:
        return pd.DataFrame(columns=['Hisse_Kodu', 'Kriter', 'Sonuç']) # Seçim yoksa boş döner

    results = []
    
    # Veriyi hisse koduna göre grupla (GARAN, THYAO, vb.)
    grouped = df.groupby('Hisse_Kodu')
    
    # Her bir hisse grubu için...
    for name, data in grouped:
        if data.empty:
            continue
            
        # Seçilen her bir kriter (formül) için...
        for criterion in selected_criteria:
            criterion_name = criterion['name']
            criterion_func = criterion['func']
            
            try:
                # Formülü çalıştır (Test et)
                passed = criterion_func(data)
                
                results.append({
                    'Hisse_Kodu': name,
                    'Kriter': criterion_name,
                    'Sonuç': "BAŞARILI" if passed else "BAŞARISIZ"
                })
            except Exception as e:
                # Formül çalışırken hata olursa (örn: veri eksikse)
                results.append({
                    'Hisse_Kodu': name,
                    'Kriter': criterion_name,
                    'Sonuç': f"HATA: {e}"
                })
                
    return pd.DataFrame(results)