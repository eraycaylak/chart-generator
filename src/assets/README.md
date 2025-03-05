# Logo ve Varlık Dosyaları Hakkında

Bu klasör, bot tarafından kullanılan logo ve diğer varlık dosyalarını içerir.

## Logo Dosyası

Logo dosyası, grafiklerde watermark olarak kullanılır. Kendi logo dosyanızı ekleyebilirsiniz.

### Önerilen Logo Özellikleri

- PNG formatında olmalı
- Şeffaf arka plana sahip olmalı
- Önerilen boyut: 500x500 piksel
- Dosya adı: `logo.png`

Logo dosyasını ekledikten sonra, grafiklerde otomatik olarak kullanılacaktır. Logo dosyası bulunamazsa, alternatif olarak "NAPOLYON" yazısı watermark olarak kullanılacaktır.

## Grafik Ayarları

Grafik görünümünü `config.py` dosyasındaki `CHART_SETTINGS` bölümünden özelleştirebilirsiniz:

```python
self.CHART_SETTINGS = {
    "candle_count": 400,  # Gösterilecek mum adeti
    "chart_width": 14,    # Genişlik
    "chart_height": 10,   # Yükseklik
    "dpi": 150,           # Çözünürlük
    "watermark_alpha": 0.25,  # Filigran opacity
    "background_color": "#d1d4dc", # Grafik arkaplan rengi
    "candle_type": "hollow", # Mumlar: İçi Boş Mumlar
    "up_color": "black",  # Yükseliş Rengi
    "down_color": "black", # Düşüş Rengi
    "grid_opacity": 0.0,  # Klavuz Çizgileri opacity
}
```