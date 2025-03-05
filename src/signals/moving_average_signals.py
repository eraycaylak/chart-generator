#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Hareketli Ortalama Sinyalleri Modülü
"""
from signals.base_signal import BaseSignal
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("ma_signals")

class MovingAverageSignals(BaseSignal):
    """Hareketli ortalama tabanlı sinyalleri tespit eden sınıf"""
    
    def __init__(self, config):
        """Hareketli ortalama sinyal tespit parametrelerini ayarlar"""
        super().__init__(config)
        self.name = "Moving Average Signals"
        logger.info("Hareketli ortalama sinyal modülü başlatıldı")
    
    def check_signals(self, symbol, timeframe, df):
        """
        Hareketli ortalama tabanlı tüm sinyalleri kontrol eder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        signals = []
        
        # EMA Kesişimleri
        ema_signals = self.check_ema_crossovers(symbol, timeframe, df)
        signals.extend(ema_signals)
        
        return signals
    
    def check_ema_crossovers(self, symbol, timeframe, df):
        """EMA Kesişimlerini kontrol eder"""
        signals = []
        
        try:
            # Son 2 mumu kontrol et
            if len(df) < 3:
                return signals
            
            # Kısa EMA uzun EMA'yı yukarı kesiyor (Golden Cross - Boğa Sinyali)
            if (df['ema_short'].iloc[-2] <= df['ema_long'].iloc[-2]) and (df['ema_short'].iloc[-1] > df['ema_long'].iloc[-1]):
                # Entry, Stop Loss ve Take Profit hesapla
                entry = df['close'].iloc[-1]
                stop_loss = min(df['low'].iloc[-5:]) * 0.99  # Son 5 mumun en düşüğünün %1 altı
                take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                
                # Sinyal kalitesini hesapla
                quality = self.calculate_signal_quality(df, is_bullish=True)
                
                signals.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': 'EMA Golden Cross',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': df.index[-1],
                    'quality_score': quality,
                    'description': f'Kısa EMA ({self.config.TA_PARAMS["ema_short"]}) uzun EMA\'yı ({self.config.TA_PARAMS["ema_long"]}) yukarı kesti. Olası bir yükseliş sinyali.'
                })
            
            # Kısa EMA uzun EMA'yı aşağı kesiyor (Death Cross - Ayı Sinyali)
            if (df['ema_short'].iloc[-2] >= df['ema_long'].iloc[-2]) and (df['ema_short'].iloc[-1] < df['ema_long'].iloc[-1]):
                # Entry, Stop Loss ve Take Profit hesapla
                entry = df['close'].iloc[-1]
                stop_loss = max(df['high'].iloc[-5:]) * 1.01  # Son 5 mumun en yükseğinin %1 üstü
                take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                
                # Sinyal kalitesini hesapla
                quality = self.calculate_signal_quality(df, is_bullish=False)
                
                signals.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': 'EMA Death Cross',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': df.index[-1],
                    'quality_score': quality,
                    'description': f'Kısa EMA ({self.config.TA_PARAMS["ema_short"]}) uzun EMA\'yı ({self.config.TA_PARAMS["ema_long"]}) aşağı kesti. Olası bir düşüş sinyali.'
                })
        
        except Exception as e:
            logger.error(f"EMA kesişimi kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals