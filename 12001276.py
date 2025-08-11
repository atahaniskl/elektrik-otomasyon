from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta, timezone
import time
import json
from selenium.webdriver.common.keys import Keys

USERNAME = "x"
PASSWORD = "x"

sayac_no = "12001276"
dosya_adi = f"{sayac_no}_verisi.json"

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

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
        next_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Next page']")))
        
        # Buton devre dışı mı kontrol et
        if not next_button.is_enabled():
            print("Son sayfaya ulaşıldı.")
            return False
        
        # Tıklanabilir olmasını bekle
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next page']")))
        next_button.click()
        time.sleep(1)  # Sayfa yüklenmesi için kısa bekleme
        return True
    except Exception as e:
        print("Sonraki sayfa butonuna tıklanamadı:", e)
        return False

def tum_sayfalari_cek_ve_json_kaydet(driver, wait):
    tum_veriler = []
    sayfa_numarasi = 1

    while True:
        print(f"{sayfa_numarasi}. sayfa verileri çekiliyor...")
        veriler = sayfadan_veri_cek(driver, wait)
        for kayit in veriler:
            kayit["sayac_no"] = sayac_no
        tum_veriler.extend(veriler)

        devam = sonraki_sayfa_butonuna_tikla(driver, wait)
        if not devam:
            break
        sayfa_numarasi += 1

    with open(dosya_adi, "w", encoding="utf-8") as f:
        json.dump(tum_veriler, f, ensure_ascii=False, indent=4)

    print("Tüm veriler veriler.json dosyasına kaydedildi.")

def get_utc_midnight_timestamp(date_obj):
    # date_obj: datetime objesi (timezone yoksa UTC olarak kabul edelim)
    from datetime import datetime, timezone
    
    dt_utc = datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0, tzinfo=timezone.utc)
    return int(dt_utc.timestamp() * 1000)


def onceki_ay_ilk_ve_son_gun():
    today = datetime.today()
    ilk_gun_bu_ay = today.replace(day=1)
    ilk_gun_onceki_ay = (ilk_gun_bu_ay - timedelta(days=1)).replace(day=1)
    son_gun = ilk_gun_bu_ay  # Bu ayın 1'i
    return ilk_gun_onceki_ay, son_gun

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


def onceki_ay_tarihlerini_sec_ve_sorgula(driver, wait):
    baslangic, bitis = onceki_ay_ilk_ve_son_gun()

    tarih_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#deOverview")))
    tarih_input.click()
    time.sleep(1)

    # Sadece bir ay geri git (geçen ay sol tarafa gelsin)
    onceki_ay_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dxbl-calendar-header-previous-month-btn")))
    onceki_ay_btn.click()
    time.sleep(1)
    print("şimdi tarih seçilecek")
    # Sadece sol takvim panelinden tarihleri seç
    tarih_sec_sadece_sol(driver,wait ,baslangic)
    time.sleep(0.5)
    tarih_sec_sadece_sol(driver,wait ,bitis)
    time.sleep(2)

    # Sorgula butonuna tıkla
    sorgula_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Sorgula')]]"
    )))
    sorgula_btn.click()


# --- Program Akışı ---

driver.get("https://osos.mosb.org.tr/")

# Giriş işlemi
username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='login-username']")))
time.sleep(1)
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


driver.get("https://osos.mosb.org.tr/meters/10119791")
time.sleep(5)

driver.get("https://osos.mosb.org.tr/meterQuery")
time.sleep(3)

# Önceki ay tarihlerini seç ve sorgula
onceki_ay_tarihlerini_sec_ve_sorgula(driver, wait)
time.sleep(5)
tum_sayfalari_cek_ve_json_kaydet(driver, wait)

