# modernweb

SQLite tabanlı örnek emitter izleme dashboard'u.

## Çalıştırma Prosedürü

1. Proje klasörüne gir:
```bash
cd /Users/doruk.bozagac/Documents/modernweb
```
2. Python sürümünü doğrula (3.10+ önerilir):
```bash
python3 --version
```
3. Uygulamayı başlat:
```bash
python3 app.py
```
4. Tarayıcıdan aç:
```text
http://localhost:4000
```

## Durdurma

- Terminalde çalışan süreç için `Ctrl + C` kullan.

## Notlar

- Uygulama ilk açılışta SQLite dosyasını (`data/emitters.sqlite`) ve örnek emitter verilerini otomatik oluşturur.
- Frontend React CDN kullandığı için internet erişimi yoksa arayüz render edilmeyebilir.

## Özellikler

- SQLite veritabanı (`data/emitters.sqlite`) ve otomatik 10 dummy emitter satırı.
- Dummy verilerde PRI/PW listelerine ek 5'er örnek değer daha eklenmiştir (liste boyutları önceki sürüme göre +5 artar).
- Frontend React 18 ile yazıldı (CDN: React + ReactDOM + Babel Standalone), backend Python'da kalır.
- Üç kolonlu tasarım:
  - Sol panel: **Emitter List** (yukarıdan aşağı kart listesi, kartta sağ kolonda emitter görseli).
  - Orta panel: **Emitter Details** (üstte `ID/Emitter` + görsel, altta grup detayları).
  - Sağ panel: **View Settings** (tüm görünüm ayarları).
- Veritabanına `emitter_image` alanı eklendi ve örnek veriler Wikimedia kaynaklı radar/emitter görselleriyle dolduruldu.
- Kartta özet alanlar: Frequency Values, Frequency Type, PRI Type, PW Type.
- Kartta ek özet alanlar: Country, Classification, Antenna Type.
- Veritabanında eklenen idari alanlar: `country`, `classification`, `operatorUnit`, `platform`, `missionArea`.
- Veritabanında eklenen teknik alanlar: `antennaType`, `antennaHeightM`, `antennaGainDbi`, `antennaPolarization`, `antennaAzimuthDeg`, `antennaElevationDeg`, `beamwidthDeg`, `bandwidthMHz`, `txPowerWatts`, `receiverSensitivityDbm`.
- Detay panelinde **PRI Values** ve **PW Values** alanları 3-10 arası çoklu değer listesi olarak tutulur ve 9 farklı yöntemle gösterilir:
  - `Chip/Pill Listesi`
  - `Mikro Tablo`
  - `Mini Bar/Spark`
  - `Adım Grafiği (SVG)`
  - `Isı Haritası Hücreleri`
  - `Delta Akış Listesi`
  - `Radial Rozetler`
  - `Merdiven Skala`
  - `Mini Histogram`
- Kullanıcı sağ paneldeki combobox ile yöntem seçince görünüm anlık güncellenir (varsayılan seçim: `Chip/Pill Listesi`).
- Yoğun değer listelerinde taşma/okunabilirlik için `Micro Table` ve `Mini Bar/Spark` görünümleri yatay kaydırma ve sıklaştırılmış çizim desteğiyle güncellenmiştir.
- Emitter details ekranında ilk 2 alan (`ID`, `Name`) her zaman görünür.
- Sonraki 5 alan `Administrative`, kalan tüm alanlar `Technical` grubunda gösterilir.
- `Grouping` combobox ile 5 farklı grup aç/kapa stili seçilebilir:
  - `Klasik Accordion`
  - `Kart Bölümleri`
  - `Ağaç Görünümü`
  - `Sekme Panelleri`
  - `Kompakt Katlanır`
- `Expanded/Collapsed/Tabbed` radio seçimi grupların varsayılan davranışını tüm grouping yöntemleri için belirler:
  - `Expanded`: Her iki grup açık başlar.
  - `Collapsed`: Her iki grup kapalı başlar.
  - `Tabbed`: Aynı anda tek grup açık kalır (tab davranışı).
