#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Ichimoku Bulutu Sinyalleri Modülü
"""
from signals.base_signal import BaseSignal
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("ichimoku_signals")

class IchimokuSignals(BaseSignal):
    """Ichimoku Bulutu tabanlı sinyalleri tespit eden sınıf"""
    
    def __init__(self, config):
        """Ichimoku Bulutu sinyal tespit parametrelerini ayarlar"""
        super().__init__(config)
        self.name = "Ichimoku Cloud Signals"
        logger.info("Ichimoku Bulutu sinyal modülü başlatıldı")
    
    def check_signals(self, symbol, timeframe, df):
        """
        Ichimoku Bulutu tabanlı tüm sinyalleri kontrol eder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        signals = []
        
        # Ichimoku Bulutu Uyarıları
        ichimoku_signals = self.check_ichimoku_cloud(symbol, timeframe, df)
        signals.extend(ichimoku_signals)
        
        return signals
    
    def check_ichimoku_cloud(self, symbol, timeframe, df):
        """Ichimoku Bulutu Sinyallerini kontrol eder"""
        signals = []
        
        try:
            # Son 2 mumu kontrol et
            if len(df) < 3:
                return signals
            
            # Tenkan-sen Kijun-sen'i yukarı kesiyor (Boğa Sinyali)
            if (df['ichimoku_tenkan'].iloc[-2] <= df['ichimoku_kijun'].iloc[-2]) and (df['ichimoku_tenkan'].iloc[-1] > df['ichimoku_kijun'].iloc[-1]):
                # Entry, Stop Loss ve Take Profit hesapla
                entry = df['close'].iloc[-1]
                stop_loss = min(df['low'].iloc[-5:]) * 0.99  # Son 5 mumun en düşüğünün %1 altı
                take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                
                # Sinyal kalitesini hesapla
                quality = self.calculate_signal_quality(df, is_bullish=True)
                
                # Fiyat bulutun üstündeyse kaliteyi artır
                if df['close'].iloc[-1] > max(df['ichimoku_senkou_span_a'].iloc[-1], df['ichimoku_senkou_span_b'].iloc[-1]):
                    quality += 15
                
                signals.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': 'Ichimoku TK Cross (Bullish)',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': df.index[-1],
                    'quality_score': quality,
                    'description': 'Tenkan-sen Kijun-sen\'i yukarı kesti. Olası bir yükseliş sinyali.'
                })
            
            # Tenkan-sen Kijun-sen'i aşağı kesiyor (Ayı Sinyali)
            if (df['ichimoku_tenkan'].iloc[-2] >= df['ichimoku_kijun'].iloc[-2]) and (df['ichimoku_tenkan'].iloc[-1] < df['ichimoku_kijun'].iloc[-1]):
                # Entry, Stop Loss ve Take Profit hesapla
                entry = df['close'].iloc[-1]
                stop_loss = max(df['high'].iloc[-5:]) * 1.01  # Son 5 mumun en yükseğinin %1 üstü
                take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                
                # Sinyal kalitesini hesapla
                quality = self.calculate_signal_quality(df, is_bullish=False)
                
                # Fiyat bulutun altındaysa kaliteyi artır
                if df['close'].iloc[-1] < min(df['ichimoku_senkou_span_a'].iloc[-1], df['ichimoku_senkou_span_b'].iloc[-1]):
                    quality += 15
                
                signals.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': 'Ichimoku TK Cross (Bearish)',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': df.index[-1],
                    'quality_score': quality,
                    'description': 'Tenkan-sen Kijun-sen\'i aşağı kesti. Olası bir düşüş sinyali.'
                })
        
        except Exception as e:
            logger.error(f"Ichimoku sinyali kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals