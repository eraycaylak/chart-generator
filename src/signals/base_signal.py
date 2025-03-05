#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Temel Sinyal Sınıfı
"""
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("base_signal")

class BaseSignal:
    """Tüm sinyal türleri için temel sınıf"""
    
    def __init__(self, config):
        """Sinyal tespit parametrelerini ayarlar"""
        self.config = config
        self.name = "Base Signal"
        logger.info(f"{self.name} sinyal modülü başlatıldı")
    
    def check_signals(self, symbol, timeframe, df):
        """
        Sinyalleri kontrol eder - alt sınıflar tarafından uygulanmalıdır
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        return []
    
    def calculate_signal_quality(self, df, is_bullish):
        """
        Sinyal kalitesini hesaplar (0-100 arası)
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            is_bullish (bool): Sinyal boğa sinyali mi?
            
        Returns:
            int: Kalite puanı (0-100)
        """
        quality = 50  # Başlangıç puanı
        
        try:
            # Trend gücü
            ema_short = df['ema_short'].iloc[-1]
            ema_long = df['ema_long'].iloc[-1]
            
            if is_bullish:
                # Boğa sinyali için trend kontrolü
                if ema_short > ema_long:
                    quality += 10  # Yükselen trend
                else:
                    quality -= 10  # Düşen trend
                
                # RSI kontrolü
                if df['rsi'].iloc[-1] < 30:
                    quality += 15  # Aşırı satım bölgesi
                elif df['rsi'].iloc[-1] < 50:
                    quality += 5  # Nötr bölge
                
                # MACD kontrolü
                if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
                    quality += 10  # MACD pozitif
                
                # Bollinger Bantları kontrolü
                if df['close'].iloc[-1] < df['bb_lower'].iloc[-1]:
                    quality += 10  # Fiyat alt bandın altında
            else:
                # Ayı sinyali için trend kontrolü
                if ema_short < ema_long:
                    quality += 10  # Düşen trend
                else:
                    quality -= 10  # Yükselen trend
                
                # RSI kontrolü
                if df['rsi'].iloc[-1] > 70:
                    quality += 15  # Aşırı alım bölgesi
                elif df['rsi'].iloc[-1] > 50:
                    quality += 5  # Nötr bölge
                
                # MACD kontrolü
                if df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]:
                    quality += 10  # MACD negatif
                
                # Bollinger Bantları kontrolü
                if df['close'].iloc[-1] > df['bb_upper'].iloc[-1]:
                    quality += 10  # Fiyat üst bandın üstünde
            
            # Hacim kontrolü
            avg_volume = df['volume'].iloc[-5:].mean()
            if df['volume'].iloc[-1] > 1.5 * avg_volume:
                quality += 10  # Hacim artışı
            
            # Kaliteyi 0-100 arasında sınırla
            quality = max(0, min(100, quality))
            
        except Exception as e:
            logger.error(f"Sinyal kalitesi hesaplanırken hata: {str(e)}", exc_info=True)
            quality = 50  # Hata durumunda orta kalite
        
        return quality