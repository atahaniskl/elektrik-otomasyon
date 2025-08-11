import tkinter as tk
from tkinter import messagebox
import importlib

def start_automation():
    secim = dropdown_var.get()
    if secim == "Bir işlem seçiniz":
        messagebox.showwarning("Uyarı", "Lütfen bir işlem seçiniz!")
        return
    
    if secim == "İş Emri Dengeleme":
        try:
            # isemridengeleme.py modülünü import et ve main fonksiyonunu çalıştır
            mod = importlib.import_module("isemridengele")
            mod.main()  # burada isemridengeleme.py'de main() fonksiyonunun olduğundan emin ol
        except Exception as e:
            messagebox.showerror("Hata", f"İşlem çalıştırılamadı:\n{e}")

root = tk.Tk()
root.title("Flicker Arayüz")
root.geometry("300x180")

dropdown_var = tk.StringVar(root)
dropdown_var.set("Bir işlem seçiniz")  # Varsayılan seçim

options = ["Bir işlem seçiniz", "İş Emri Dengeleme", "ornek1"]

tk.Label(root, text="İşlem Seçiniz:").pack(pady=10)

dropdown = tk.OptionMenu(root, dropdown_var, *options)
dropdown.pack(pady=5)

start_button = tk.Button(root, text="Başlat", command=start_automation)
start_button.pack(pady=20)

root.mainloop()
