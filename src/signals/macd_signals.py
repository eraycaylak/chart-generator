#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - MACD Sinyalleri Modülü
"""
from signals.base_signal import BaseSignal
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("macd_signals")

class MACDSignals(BaseSignal):
    """MACD tabanlı sinyalleri tespit eden sınıf"""
    
    def __init__(self, config):
        """MACD sinyal tespit parametrelerini ayarlar"""
        super().__init__(config)
        self.name = "MACD Signals"
        logger.info("MACD sinyal modülü başlatıldı")
    
    def check_signals(self, symbol, timeframe, df):
        """
        MACD tabanlı tüm sinyalleri kontrol eder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        signals = []
        
        # MACD Kesişimleri
        macd_signals = self.check_macd_crossovers(symbol, timeframe, df)
        signals.extend(macd_signals)
        
        return signals
    
    def check_macd_crossovers(self, symbol, timeframe, df):
        """MACD Sinyallerini kontrol eder"""
        signals = []
        
        try:
            # Son 2 mumu kontrol et
            if len(df) < 3:
                return signals
            
            # MACD çizgisi sinyal çizgisini yukarı kesiyor (Boğa Sinyali)
            if (df['macd'].iloc[-2] <= df['macd_signal'].iloc[-2]) and (df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]):
                # Entry, Stop Loss ve Take Profit hesapla
                entry = df['close'].iloc[-1]
                stop_loss = min(df['low'].iloc[-5:]) * 0.99  # Son 5 mumun en düşüğünün %1 altı
                take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                
                # Sinyal kalitesini hesapla
                quality = self.calculate_signal_quality(df, is_bullish=True)
                
                # MACD histogramı negatiften pozitife geçiyorsa kaliteyi artır
                if df['macd_hist'].iloc[-2] < 0 and df['macd_hist'].iloc[-1] > 0:
                    quality += 10
                
                signals.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': 'MACD Bullish Crossover',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': df.index[-1],
                    'quality_score': quality,
                    'description': 'MACD çizgisi sinyal çizgisini yukarı kesti. Olası bir yükseliş sinyali.'
                })
            
            # MACD çizgisi sinyal çizgisini aşağı kesiyor (Ayı Sinyali)
            if (df['macd'].iloc[-2] >= df['macd_signal'].iloc[-2]) and (df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]):
                # Entry, Stop Loss ve Take Profit hesapla
                entry = df['close'].iloc[-1]
                stop_loss = max(df['high'].iloc[-5:]) * 1.01  # Son 5 mumun en yükseğinin %1 üstü
                take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                
                # Sinyal kalitesini hesapla
                quality = self.calculate_signal_quality(df, is_bullish=False)
                
                # MACD histogramı pozitiften negatife geçiyorsa kaliteyi artır
                if df['macd_hist'].iloc[-2] > 0 and df['macd_hist'].iloc[-1] < 0:
                    quality += 10
                
                signals.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': 'MACD Bearish Crossover',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': df.index[-1],
                    'quality_score': quality,
                    'description': 'MACD çizgisi sinyal çizgisini aşağı kesti. Olası bir düşüş sinyali.'
                })
        
        except Exception as e:
            logger.error(f"MACD sinyali kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals