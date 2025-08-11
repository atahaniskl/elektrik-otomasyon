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
    }

    dosya_adi = dosya_map.get(secim)

    if not dosya_adi:
        messagebox.showwarning("Uyarı", "Lütfen bir işlem seçiniz!")
        return

    try:
        subprocess.Popen(["python", dosya_adi])  # ya da ["python3", dosya_adi]
    except Exception as e:
        messagebox.showerror("Hata", f"İşlem çalıştırılamadı:\n{e}")

root = tk.Tk()
root.title("Elektrik Verisi Çekme")
root.geometry("300x180")

dropdown_var = tk.StringVar()
dropdown_var.set("Bir işlem seçiniz")

options = ["Ana Bina - 12001150", "Karpek - 12001257", "TELESET NO:5 - 12001276", "TELESET NO:6/1 - 12001289"]

tk.Label(root, text="Lütfen bir sayaç seçiniz:").pack(pady=10)
dropdown = tk.OptionMenu(root, dropdown_var, *options)
dropdown.pack(pady=5)

tk.Button(root, text="Başlat", command=start_automation).pack(pady=20)

root.mainloop()
