# modernweb

SQLite tabanlı örnek emitter izleme dashboard'u.

## Çalıştırma

```bash
python app.py
```

Uygulama `http://localhost:3000` adresinde çalışır.

## Özellikler

- SQLite veritabanı (`data/emitters.sqlite`) ve otomatik 10 dummy emitter satırı.
- İki kolonlu tasarım:
  - Sol panel: **Emitter List** (yukarıdan aşağı kart listesi, panelin yarı genişliği).
  - Sağ panel: **Emitter Details** (seçili emitter'ın tüm alanları tabular formatta).
- Kartta özet alanlar: Frequency Values, Frequency Type, PRI Type, PW Type.
- Detay panelinde **PRI Values** ve **PW Values** alanları 3-10 arası çoklu değer listesi olarak tutulur ve 3 farklı yöntemle gösterilir:
  - `yöntem1`: Chip/Pill listesi
  - `yöntem2`: Mikro tablo görünümü
  - `yöntem3`: Mini bar/spark görünümü
- Kullanıcı sağ paneldeki combobox ile yöntem seçince görünüm anlık güncellenir (varsayılan seçim: `yöntem1`).
