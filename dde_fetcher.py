# dde_fetcher.py

import pandas as pd
import time
import os
import random

# Eğer ddeclient kurulduysa ve Windows kullanıyorsanız:
# from ddeclient import DDEClient  

DOSYA_ADI = 'Matrix_Analiz_Verileri.csv'

# --- Matrix DDE Bağlantı Ayarları (Gerçek Kod Buraya Gelecek) ---
# DDE_SERVICE = 'MatrixServer'  
# DDE_TOPIC = 'RTD'             

def get_real_time_data_simulated():
    """
    Bu fonksiyon, gerçek DDE bağlantısı kurulana kadar veriyi simüle eder.
    
    Not: Gerçek DDE entegrasyonu için, bu fonksiyonda DDEClient kullanmanız gerekir.
    """
    
    # Simülasyon Verisi:
    hisse_kodlari = ['GARAN', 'THYAO', 'AKBNK', 'EREGL', 'TUPRS', 'SAHOL', 'BIMAS', 'ASELS']
    
    kod = random.choice(hisse_kodlari)
    # Fiyatları gerçekçi dalgalanma için simüle edelim
    fiyat_tabani = random.uniform(10.0, 100.0) 
    acilis = round(fiyat_tabani, 2)
    kapanis = round(random.uniform(acilis - 1, acilis + 1), 2)
    son_fiyat = round(random.uniform(kapanis - 0.5, kapanis + 0.5), 2)
    
    return kod, acilis, kapanis, son_fiyat

def save_data_to_csv(kod, acilis, kapanis, son_fiyat):
    """Çekilen tek bir veri setini CSV dosyasına ekler."""
    
    zaman_damgasi = pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    yeni_satir = pd.DataFrame({
        'Zaman': [zaman_damgasi],
        'Kod': [kod],
        'Acilis': [acilis],
        'Kapanis': [kapanis],
        'Son_Fiyat': [son_fiyat]
    })

    # Dosya yoksa veya boşsa başlıklarla, varsa başlıksız ekle
    if not os.path.exists(DOSYA_ADI) or os.path.getsize(DOSYA_ADI) == 0:
        yeni_satir.to_csv(DOSYA_ADI, index=False, mode='w', encoding='utf-8')
    else:
        yeni_satir.to_csv(DOSYA_ADI, index=False, mode='a', header=False, encoding='utf-8')

def run_analysis_motor(guncelleme_suresi=1): # 1 saniyede bir güncelleme
    print("Matrix Veri Motoru Başlatıldı. Veriler CSV'ye yazılıyor...")
    print(f"Veri dosyası: {DOSYA_ADI}")
    
    while True:
        kod, acilis, kapanis, son_fiyat = get_real_time_data_simulated()
        
        if kod is not None:
            save_data_to_csv(kod, acilis, kapanis, son_fiyat)
        
        time.sleep(guncelleme_suresi)

if __name__ == '__main__':
    run_analysis_motor()