import subprocess

# Çalıştırılacak sayaç dosyaları (sırasıyla)
dosyalar = [
    "12001150.py",
    "12001257.py",
    "12001276.py",
    "12001289.py"
]

for dosya in dosyalar:
    print(f"{dosya} çalıştırılıyor...")
    result = subprocess.run(["python", dosya])

    if result.returncode != 0:
        print(f"HATA: {dosya} çalıştırılırken hata oluştu! Çıkış kodu: {result.returncode}")
        break  # İstersen burada durabilir veya devam edebilirsin
    else:
        print(f"{dosya} başarıyla tamamlandı.\n")
