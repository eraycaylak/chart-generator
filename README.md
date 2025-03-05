# Kripto Teknik Analiz Botu

Bu bot, kripto para piyasalarını analiz eder ve Telegram üzerinden sinyal gönderir. Binance API'den veri çeker, çeşitli teknik analiz yöntemleriyle sinyaller üretir ve kaliteli sinyalleri Telegram kanalına gönderir.

## Özellikler

- **Veri Toplama**: Binance API üzerinden mum verileri çekilir.
- **Çoklu Zaman Dilimleri**: 15dk, 1saat, 4saat, 1gün zaman dilimleri desteklenir.
- **Teknik Analiz**: Çeşitli teknik indikatörler ve formasyonlar analiz edilir.
- **Sinyal Kalite Analizi**: Sinyaller kalitelerine göre puanlanır ve filtrelenir.
- **Telegram Entegrasyonu**: Sinyaller otomatik olarak Telegram kanalına gönderilir.
- **Profesyonel Grafikler**: Her sinyal için detaylı teknik analiz grafiği oluşturulur.

## Algılanabilen Sinyaller

- Destek & Direnç Bölgeleri
- RSI Uyumsuzlukları (Divergence)
- Fibonacci Geri Çekilme Seviyeleri
- EMA / SMA Kesişimleri
- MACD Kesişimleri
- Bollinger Bantları Uyarıları
- BTC için Anormal Volatilite Uyarısı
- Mum Formasyonları (Pin Bar, Engulfing vb.)
- Ichimoku Bulutu Uyarıları

## Kurulum

1. Gerekli Python paketlerini yükleyin:
   ```
   pip install python-binance python-telegram-bot matplotlib numpy pandas requests mplfinance python-dotenv schedule
   ```

2. `.env.example` dosyasını `.env` olarak kopyalayın ve API anahtarlarınızı girin:
   ```
   cp .env.example .env
   ```

3. `.env` dosyasını düzenleyin ve API anahtarlarınızı ekleyin:
   ```
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_API_SECRET=your_binance_api_secret
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   ```

## Kullanım

Botu başlatmak için:

```
python src/main.py
```

## Modüler Yapı

Bot, aşağıdaki modüllerden oluşur:

- **main.py**: Ana bot sınıfı ve koordinasyon
- **config.py**: Konfigürasyon ayarları
- **data_fetcher.py**: Binance API'den veri çekme
- **technical_indicators.py**: Teknik indikatörleri hesaplama
- **signal_analyzer.py**: Sinyal analizi ve tespit
- **pattern_detector.py**: Mum formasyonlarını tespit etme
- **support_resistance.py**: Destek ve direnç seviyelerini tespit etme
- **chart_generator.py**: Teknik analiz grafikleri oluşturma
- **signal_sender.py**: Telegram üzerinden sinyal gönderme
- **utils/logger.py**: Loglama sistemi

## Özelleştirme

`config.py` dosyasını düzenleyerek botun davranışını özelleştirebilirsiniz:

- İzlenecek kripto para sembolleri
- Taranacak zaman dilimleri
- Teknik indikatör parametreleri
- Sinyal kalite eşikleri
- Grafik ayarları

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.