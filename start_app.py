import subprocess
import sys
import time
import os
import math
import shutil

# --- SİSTEM AYARLARI ---
VERSION = "v1.2"
SYSTEM_NAME = "BERLİN KAPLANI"

# --- RENK VE ANİMASYON MOTORU ---
class RenkMotoru:
    RESET = '\033[0m'
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'
    MOVE_TO_TOP = '\033[H'
    
    @staticmethod
    def rgb(r, g, b, text):
        return f'\033[38;2;{r};{g};{b}m{text}{RenkMotoru.RESET}'

    @staticmethod
    def temizle():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def rgb_dalgasi_oynat(yazi, sure=2):
        """
        RGB Wave Efekti - HIZLANDIRILMIŞ VERSİYON
        """
        start_time = time.time()
        offset = 0
        
        sys.stdout.write(RenkMotoru.HIDE_CURSOR)
        lines = yazi.strip().split('\n')
        
        try:
            while time.time() - start_time < sure:
                sys.stdout.write(RenkMotoru.MOVE_TO_TOP)
                output = ""
                for i, line in enumerate(lines):
                    colored_line = ""
                    for j, char in enumerate(line):
                        if char == " ":
                            colored_line += " "
                            continue
                        
                        # Daha hızlı renk değişimi için frekansı artırdık
                        freq = 0.3
                        r = int(math.sin(freq * j + i + offset) * 127 + 128)
                        g = int(math.sin(freq * j + i + offset + 2) * 127 + 128)
                        b = int(math.sin(freq * j + i + offset + 4) * 127 + 128)
                        
                        colored_line += f'\033[38;2;{r};{g};{b}m{char}'
                    output += colored_line + "\033[0m\n"
                
                # --- İSİM YERİNE VERSİYON BİLGİSİ ---
                info_text = f"\n   >>>> {SYSTEM_NAME} <<<<   "
                ver_text  = f"   VERSION: {VERSION}   " # İsim kalktı, sürüm geldi
                
                # Info text RGB
                r_info = int(math.sin(offset) * 127 + 128)
                g_info = int(math.sin(offset + 2) * 127 + 128)
                b_info = int(math.sin(offset + 4) * 127 + 128)
                
                output += f"\n   \033[38;2;{r_info};{g_info};{b_info}m{info_text}\033[0m"
                output += f"\n   \033[38;2;150;150;150m{ver_text}\033[0m\n"
                
                sys.stdout.write(output)
                sys.stdout.flush()
                
                offset += 0.4 # Animasyon hızı artırıldı
                time.sleep(0.03) # Bekleme süresi azaltıldı
                
        except KeyboardInterrupt:
            pass
        finally:
            sys.stdout.write(RenkMotoru.SHOW_CURSOR)

    @staticmethod
    def yukleme_cubugu(mesaj):
        print(f"\n{mesaj}")
        genislik = 40
        # HIZLANDIRILMIŞ YÜKLEME (0.01s bekleme)
        for i in range(genislik + 1):
            time.sleep(0.01) 
            r = 0
            g = int(255 - (i * 4))
            if g < 0: g = 0
            b = int(i * 6)
            if b > 255: b = 255
            
            bar = '█' * i + '░' * (genislik - i)
            yuzde = int((i / genislik) * 100)
            sys.stdout.write(f'\r\033[38;2;{r};{g};{b}m[{bar}] {yuzde}%{RenkMotoru.RESET}')
            sys.stdout.flush()
        print("\n")

# --- YOL AYARLARI ---
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
except:
    script_dir = os.getcwd()
    sys.path.insert(0, script_dir)

# --- LOGO ---
logo = r"""
  ____  _____ ____  _     ___ _   _ 
 | __ )| ____|  _ \| |   |_ _| \ | |
 |  _ \|  _| | |_) | |    | ||  \| |
 | |_) | |___|  _ <| |___ | || |\  |
 |____/|_____|_| \_\_____|___|_| \_|
                                    
  _  __    _    ____  _        _    _   _ ___ 
 | |/ /   / \  |  _ \| |      / \  | \ | |_ _|
 | ' /   / _ \ | |_) | |     / _ \ |  \| || | 
 | . \  / ___ \|  __/| |___ / ___ \| |\  || | 
 |_|\_\/_/   \_\_|   |_____/_/   \_\_| \_|___|
"""

# --- GÖSTERİ BAŞLIYOR ---
RenkMotoru.temizle()

# 1. SADECE 2 SANİYE RGB ANİMASYON
RenkMotoru.rgb_dalgasi_oynat(logo, sure=2.0)

# --- MOTOR KONTROLÜ ---
try:
    RenkMotoru.yukleme_cubugu("⚙️  SİSTEM BAŞLATILIYOR...")
    from data_processor import process_files_separately
except ImportError as e:
    print(RenkMotoru.rgb(255, 0, 0, f"KRİTİK HATA: Motor bulunamadı! ({e})"))
    time.sleep(5)
    sys.exit(1)

def main():
    # 1. ADIM: VERİ ÇEKME
    print(RenkMotoru.rgb(0, 255, 255, ">>> 📊 Excel Veri Bağlantısı Kuruluyor..."))
    
    try:
        basari = process_files_separately()
        if basari:
            print(RenkMotoru.rgb(0, 255, 0, ">>> ✅ BAŞARILI: Veriler güncel."))
            if os.name == 'nt': 
                import winsound
                try: winsound.Beep(1000, 100) # Kısa Bip
                except: pass
        else:
            print(RenkMotoru.rgb(255, 165, 0, ">>> ⚠️ UYARI: Veri alınamadı (Eski verilerle devam)."))
                
    except Exception as e:
        print(RenkMotoru.rgb(255, 0, 0, f">>> ❌ HATA: {e}"))

    # 2. ADIM: ARAYÜZ
    print("-" * 60)
    print(RenkMotoru.rgb(255, 0, 255, ">>> 🚀 Arayüz Açılıyor..."))
    time.sleep(0.5) # Bekleme süresi kısaltıldı
    
    try:
        app_path = os.path.join(script_dir, "app.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    except KeyboardInterrupt:
        print(RenkMotoru.rgb(255, 255, 0, "\n>>> Sistem kapatıldı."))
    except Exception as e:
        print(RenkMotoru.rgb(255, 0, 0, f"\n>>> Arayüz Hatası: {e}"))
        time.sleep(3)

if __name__ == "__main__":
    main()