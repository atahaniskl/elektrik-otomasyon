from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta, timezone
import time
import json
from selenium.webdriver.common.keys import Keys
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
#options.add_argument("--headless")  # Tarayıcıyı görünmeden açar
#options.add_argument("--disable-gpu")  # GPU kullanımını devre dışı bırakır
#options.add_argument("--window-size=1920,1080") 

driver = webdriver.Chrome(options=options)

print("sys.argv:", sys.argv)

USERNAME = "x"
PASSWORD = "x"

sayac_no = "12001257"
dosya_adi = f"veriler.json"


wait = WebDriverWait(driver, 15)

def get_tarih_araligi():
    if len(sys.argv) >= 3:
        try:
            baslangic_str = sys.argv[1]
            bitis_str = sys.argv[2]
            baslangic = datetime.strptime(baslangic_str, "%d/%m/%Y")
            bitis = datetime.strptime(bitis_str, "%d/%m/%Y")
            print(f"Kullanıcıdan alınan tarih aralığı: {baslangic} - {bitis}")
            return baslangic, bitis
        except Exception as e:
            print("Geçersiz tarih formatı. '%d/%m/%Y' bekleniyor. Hata:", e)

    # Eğer argüman yoksa veya hata varsa otomatik olarak geçen ay
    print("Tarih girilmedi, önceki haftanın verileri alınacak.")
    return onceki_hafta_pazartesi_ve_bu_hafta_pazartesi()

def toplam_sayfayi_bul(driver, wait):
    # Sayfa sayısını belirten div'i bul
    # Örnek: " of 13" yazıyor, buradaki 13 sayısını alacağız
    div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.dxbl-text.dxbl-pager-page-edit-text")))
    text = div.text.strip()  # Örn: "of 13"
    toplam = int(text.split()[-1])  # Son kelimeyi al -> 13
    print(f"Toplam sayfa sayısı: {toplam}")
    return toplam

def sayfadan_veri_cek(driver, wait):
    
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody")))
    tbody = driver.find_element(By.CSS_SELECTOR, "table tbody")
    satirlar = tbody.find_elements(By.TAG_NAME, "tr")
    
    sayfa_verileri = []
    for satir in satirlar:
        hucreler = satir.find_elements(By.TAG_NAME, "td")
        if len(hucreler) < 5:  # başlık sayısına göre kontrol et
            continue
        veri = {
            "Tarih": hucreler[0].text.strip(),
            "Endeks Kodu": hucreler[1].text.strip(),
            "Endeks Açıklama": hucreler[2].text.strip(),
            "Okunan Değer": hucreler[3].text.strip(),
            "Çarpan": hucreler[4].text.strip(),
            "Endeks Değeri": hucreler[5].text.strip() if len(hucreler) > 5 else ""
        }
        sayfa_verileri.append(veri)
    return sayfa_verileri

def sonraki_sayfa_butonuna_tikla(driver, wait):
    try:
        # Önce klasik "Next page" butonunu dene
        next_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Next page']")
        if next_buttons:
            next_button = next_buttons[0]
            if next_button.is_enabled():
                print("Next page butonuna tıklanıyor...")
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next page']")))
                next_button.click()
                time.sleep(1.5)
                return True
            else:
                print("Son sayfaya ulaşıldı (Next butonu devre dışı).")
                return False

        print("Next page butonu bulunamadı, sayfa numaraları üzerinden geçiş deneniyor...")

        # Aktif sayfa butonunu bul (dxbl-pager-active-page-btn class'lı)
        aktif_buton = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.dxbl-pager-active-page-btn"))
        )
        aktif_sayi = int(aktif_buton.text.strip())
        print(f"Aktif sayfa: {aktif_sayi}")

        # Tüm sayfa butonlarını al
        sayfa_butonlari = driver.find_elements(By.CSS_SELECTOR, "button.dxbl-pager-page-btn")

        for buton in sayfa_butonlari:
            try:
                sayi = int(buton.text.strip())
                if sayi == aktif_sayi + 1:
                    print(f"{sayi}. sayfa butonuna tıklanıyor (numara üzerinden)...")
                    driver.execute_script("arguments[0].click();", buton)
                    time.sleep(1.5)
                    return True
            except ValueError:
                continue  # '...' gibi geçersiz karakterli butonlar olabilir

        print("Son sayfaya ulaşıldı (sayfa numaraları üzerinden).")
        return False

    except Exception as e:
        print("Sayfa geçişinde hata oluştu:", e)
        return False



def tum_sayfalari_cek_ve_json_kaydet(driver, wait):
    tum_veriler = []
    sayfa_numarasi = 1

    # Mevcut veriyi yükle (dosya varsa)
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            mevcut_veriler = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        mevcut_veriler = []

    # Var olan sayaç + tarih kombinasyonlarını set olarak tut
    mevcut_kombinasyonlar = set()
    for veri in mevcut_veriler:
        try:
            key = (veri["sayac_no"], veri["Tarih"])
            mevcut_kombinasyonlar.add(key)
        except:
            continue

    while True:
        print(f"{sayfa_numarasi}. sayfa verileri çekiliyor...")
        veriler = sayfadan_veri_cek(driver, wait)

        for kayit in veriler:
            kayit["sayac_no"] = sayac_no
            key = (kayit["sayac_no"], kayit["Tarih"])

            if key in mevcut_kombinasyonlar:
                continue  # Bu kayıt zaten mevcut

            tum_veriler.append(kayit)

        devam = sonraki_sayfa_butonuna_tikla(driver, wait)
        if not devam:
            break
        sayfa_numarasi += 1

    # Yeni verilerle eskileri birleştir
    tum_veriler.extend(mevcut_veriler)
    print("Yeni verilerle eskiler birleştiriliyor")
    # Tarihe göre sıralayıp kaydet
    tum_veriler = sorted(tum_veriler, key=lambda x: x["Tarih"], reverse=True)
    print("Tarihe göre sıralayıp kaydediliyor")
    with open(dosya_adi, "w", encoding="utf-8") as f:
        json.dump(tum_veriler, f, ensure_ascii=False, indent=4)

    print(f"Yeni veriler {dosya_adi} dosyasına kaydedildi.")



def get_utc_midnight_timestamp(date_obj):
    # date_obj: datetime objesi (timezone yoksa UTC olarak kabul edelim)
    from datetime import datetime, timezone
    
    dt_utc = datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0, tzinfo=timezone.utc)
    return int(dt_utc.timestamp() * 1000)

def onceki_hafta_pazartesi_ve_bu_hafta_pazartesi():
    today = datetime.today()
    # Bugün haftanın kaçıncı günü? (Pazartesi=0, Pazar=6)
    hafta_gunu = today.weekday()

    # Bu haftanın pazartesi günü
    bu_hafta_pazartesi = today - timedelta(days=hafta_gunu)

    # Geçen haftanın pazartesi günü
    gecen_hafta_pazartesi = bu_hafta_pazartesi - timedelta(days=7)

    return gecen_hafta_pazartesi, bu_hafta_pazartesi

def tarih_sec_sadece_sol(driver, wait, timestamp_date):
    timestamp_ms = get_utc_midnight_timestamp(timestamp_date)
    xpath = (
        "//dxbl-calendar-table-container[@period-index='0']"
        f"//td[@data-date='{timestamp_ms}']/a"
    )
    print(f"Aranıyor: {xpath}")
    day_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    day_element.click()
    print("tarih secildi")


def tarih_sec_ve_sorgula(driver, wait):
    baslangic, bitis = get_tarih_araligi()

    tarih_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#deOverview")))
    time.sleep(0.5)
    tarih_input.click()
    time.sleep(2)

    # Takvimi istenen aya getirene kadar geri git
    ay_farki = (datetime.today().year - baslangic.year) * 12 + (datetime.today().month - baslangic.month)
    for _ in range(ay_farki):
        time.sleep(0.5)
        onceki_ay_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dxbl-calendar-header-previous-month-btn")))
        time.sleep(0.5)
        onceki_ay_btn.click()
        time.sleep(0.5)
    time.sleep(1)
    tarih_sec_sadece_sol(driver, wait, baslangic)
    time.sleep(0.5)
    tarih_sec_sadece_sol(driver, wait, bitis)
    time.sleep(1.5)

    sorgula_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Sorgula')]]")))
    sorgula_btn.click()




# --- Program Akışı ---

driver.get("https://osos.mosb.org.tr/")

# Giriş işlemi
username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='login-username']")))
time.sleep(3)
username_input.clear()
username_input.send_keys(USERNAME)

password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='login-password']")))
password_input.clear()
password_input.send_keys(PASSWORD)

checkbox = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox']")))
if not checkbox.is_selected():
    checkbox.click()

giris_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Giriş Yap']]")))
giris_btn.click()

time.sleep(5)  # Giriş sonrası bekle


driver.get("https://osos.mosb.org.tr/meters/10186932")
time.sleep(5)

driver.get("https://osos.mosb.org.tr/meterQuery")
time.sleep(3)

# Önceki ay tarihlerini seç ve sorgula
tarih_sec_ve_sorgula(driver, wait)
time.sleep(5)
tum_sayfalari_cek_ve_json_kaydet(driver, wait)

