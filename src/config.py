#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Konfigürasyon Modülü
"""
import os
from dotenv import load_dotenv

# .env dosyasını yükle (eğer varsa)
load_dotenv()

class Config:
    """Bot konfigürasyonunu içeren sınıf"""
    
    def __init__(self):
        # API Anahtarları
        self.BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
        self.BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
        self.TELEGRAM_SIGNALS_CHAT_ID = os.getenv("TELEGRAM_SIGNALS_CHAT_ID", "")
        
        # Tarama Ayarları
        self.SYMBOLS = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", 
            "XRPUSDT", "DOTUSDT", "DOGEUSDT", "AVAXUSDT", "MATICUSDT",
            "LINKUSDT", "LTCUSDT", "UNIUSDT", "ATOMUSDT", "ETCUSDT"
        ]
        
        self.TIMEFRAMES = ["4h"]
        
        # Sinyal Ayarları
        self.SIGNAL_COOLDOWN = 4 * 3600  # 4 saat (saniye cinsinden)
        self.MIN_SIGNAL_QUALITY = 50  # 0-100 arası kalite puanı (daha düşük eşik değeri)
        self.MIN_VOLUME_THRESHOLD = 1000000  # 1 milyon USDT (daha düşük hacim eşiği)
        
        # Teknik Analiz Parametreleri
        self.TA_PARAMS = {
            "rsi_period": 14,
            "rsi_overbought": 70,
            "rsi_oversold": 30,
            "ema_short": 9,
            "ema_medium": 21,
            "ema_long": 50,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "bb_period": 20,
            "bb_std": 2,
            "ichimoku_tenkan": 9,
            "ichimoku_kijun": 26,
            "ichimoku_senkou_span_b": 52,
        }
        
        # Grafik Ayarları - Daha temiz ve estetik görünüm için güncellendi
        self.CHART_SETTINGS = {
            "candle_count": 300,  # Grafikte gösterilecek mum sayısı
            "chart_width": 14,    # Genişlik
            "chart_height": 10,   # Yükseklik
            "dpi": 150,           # Yüksek çözünürlük
            "watermark_text": "NAPOLYON CRYPTO SCANNER",
            "watermark_alpha": 0.15,  # Daha belirgin watermark
            "show_ema": False,    # EMA'ları sadece gerektiğinde göster
            "clean_design": True, # Daha temiz tasarım
            "show_all_signals": True, # Tüm sinyalleri göster
            "background_color": "#d1d4dc", # Grafik arkaplan rengi
            "candle_type": "hollow", # Mumlar: İçi Boş Mumlar
            "up_color": "black",  # Yükseliş Rengi: Siyah
            "down_color": "black", # Düşüş Rengi: Siyah
            "grid_alpha": 0.0,  # Klavuz Çizgileri opacity
        }
        
        # API Rate Limiting
        self.API_RATE_LIMIT_WAIT = 1  # saniye
        
        # Loglama Ayarları
        self.LOG_LEVEL = "INFO"
        self.LOG_FILE = "kripto_motoru.log"
        
        # Debug Modu - RSI ve Divergence sinyallerini daha detaylı loglamak için
        self.DEBUG_MODE = True