import pandas as pd
import os
import win32com.client as win32
import time 
import pythoncom 

ANA_KLASOR = os.path.dirname(os.path.abspath(__file__)) 
EXCEL_KLASORU = os.path.join(ANA_KLASOR, 'Excel_Verileri')
CSV_KLASORU = os.path.join(ANA_KLASOR, 'CSV_Verileri') 

def process_files_separately():
    try: pythoncom.CoInitialize()
    except: pass 
    
    if not os.path.exists(EXCEL_KLASORU): os.makedirs(EXCEL_KLASORU)
    if not os.path.exists(CSV_KLASORU): os.makedirs(CSV_KLASORU)
        
    print(f"\n--- EXCEL TARANIYOR ---")

    # 1. EXCEL KAYDET
    try:
        excel = win32.GetActiveObject('Excel.Application')
        excel.DisplayAlerts = False 
        for wb in excel.Workbooks: wb.Save()
        excel.DisplayAlerts = True
    except: pass
    
    time.sleep(0.5)

    # 2. DOSYALARI AYRI AYRI KAYDET
    files = [f for f in os.listdir(EXCEL_KLASORU) if f.endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
    
    processed = 0
    for filename in files:
        try:
            path = os.path.join(EXCEL_KLASORU, filename)
            # Header=None ile ham okuyoruz
            xls = pd.read_excel(path, sheet_name=None, header=None, engine='openpyxl')
            
            for sheet_name, df in xls.items():
                if df.empty: continue
                
                # --- AKILLI BAŞLIK BULUCU ---
                # İçinde "SEMBOL" geçen satırı bul, başlık yap
                header_idx = -1
                for i in range(min(15, len(df))):
                    row_str = df.iloc[i].astype(str).str.upper().tolist()
                    if any("SEMBOL" in s for s in row_str):
                        header_idx = i
                        break
                
                if header_idx != -1:
                    df.columns = df.iloc[header_idx]
                    df = df.iloc[header_idx+1:].reset_index(drop=True)
                else:
                    # Sembol bulamazsa ilk satırı al
                    df.columns = df.iloc[0]
                    df = df.iloc[1:].reset_index(drop=True)

                # Sütun isimlerini temizle (boşlukları sil)
                df.columns = df.columns.astype(str).str.strip()
                
                # Dosya adını temizle
                safe_name = sheet_name.strip().replace(" ", "_")
                
                # OLDUĞU GİBİ KAYDET (Müdahale yok!)
                df.to_csv(os.path.join(CSV_KLASORU, f"{safe_name}.csv"), index=False, encoding='utf-8-sig')
                print(f"✅ {safe_name}.csv oluşturuldu.")
                processed += 1
                
        except Exception as e:
            print(f"Hata ({filename}): {e}")

    pythoncom.CoUninitialize() 
    return processed > 0

if __name__ == '__main__':
    process_files_separately()