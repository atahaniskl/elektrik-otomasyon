import tkinter as tk
from tkinter import messagebox
import subprocess

def start_automation():
    secim = dropdown_var.get()
    dosya_map = {
        "Ana Bina - 12001150": "12001150.py",
        "Karpek - 12001257": "12001257.py",
        "TELESET NO:5 - 12001276": "12001276.py",
        "TELESET NO:6/1 - 12001289": "12001289.py",
        "Hepsi": "ALL"
    }

    dosya_adi = dosya_map.get(secim)

    baslangic_tarih = baslangic_entry.get().strip()
    bitis_tarih = bitis_entry.get().strip()

    if not dosya_adi:
        messagebox.showwarning("Uyarı", "Lütfen bir işlem seçiniz!")
        return

    try:
        if dosya_adi == "ALL":
            tum_dosyalar = [
                "12001150.py",
                "12001257.py",
                "12001276.py",
                "12001289.py"
            ]
            for dosya in tum_dosyalar:
                komut = ["python", dosya]
                if baslangic_tarih and bitis_tarih:
                    komut += [baslangic_tarih, bitis_tarih]
                print(f"{dosya} çalıştırılıyor...")
                # Burada run kullanıyoruz, bitmesini bekler
                result = subprocess.run(komut)
                if result.returncode != 0:
                    messagebox.showerror("Hata", f"{dosya} çalıştırılırken hata oluştu!")
                    break  # Hata olursa döngüyü kırabiliriz
        else:
            komut = ["python", dosya_adi]
            if baslangic_tarih and bitis_tarih:
                komut += [baslangic_tarih, bitis_tarih]
            result = subprocess.run(komut)
            if result.returncode != 0:
                messagebox.showerror("Hata", f"{dosya_adi} çalıştırılırken hata oluştu!")

    except Exception as e:
        messagebox.showerror("Hata", f"İşlem çalıştırılamadı:\n{e}")


root = tk.Tk()
root.title("Elektrik Verisi Çekme")
root.geometry("350x300")

dropdown_var = tk.StringVar()
dropdown_var.set("Bir işlem seçiniz")

options = ["Ana Bina - 12001150", "Karpek - 12001257", "TELESET NO:5 - 12001276", "TELESET NO:6/1 - 12001289", "Hepsi"]

tk.Label(root, text="Lütfen bir sayaç seçiniz:").pack(pady=10)
dropdown = tk.OptionMenu(root, dropdown_var, *options)
dropdown.pack(pady=5)

# Başlangıç Tarihi
tk.Label(root, text="Başlangıç Tarihi (GG/AA/YYYY):").pack(pady=5)
baslangic_entry = tk.Entry(root)
baslangic_entry.pack(pady=5)

# Bitiş Tarihi
tk.Label(root, text="Bitiş Tarihi (GG/AA/YYYY):").pack(pady=5)
bitis_entry = tk.Entry(root)
bitis_entry.pack(pady=5)

tk.Button(root, text="Başlat", command=start_automation).pack(pady=20)

root.mainloop()
