#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Bollinger Bantları Sinyalleri Modülü
"""
from signals.base_signal import BaseSignal
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("bollinger_signals")

class BollingerSignals(BaseSignal):
    """Bollinger Bantları tabanlı sinyalleri tespit eden sınıf"""
    
    def __init__(self, config):
        """Bollinger Bantları sinyal tespit parametrelerini ayarlar"""
        super().__init__(config)
        self.name = "Bollinger Bands Signals"
        logger.info("Bollinger Bantları sinyal modülü başlatıldı")
    
    def check_signals(self, symbol, timeframe, df):
        """
        Bollinger Bantları tabanlı tüm sinyalleri kontrol eder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        signals = []
        
        # Bollinger Bantları Uyarıları
        bb_signals = self.check_bollinger_bands(symbol, timeframe, df)
        signals.extend(bb_signals)
        
        return signals
    
    def check_bollinger_bands(self, symbol, timeframe, df):
        """Bollinger Bantları Sinyallerini kontrol eder"""
        signals = []
        
        try:
            # Son 3 mumu kontrol et
            if len(df) < 4:
                return signals
            
            # Fiyat alt bandın altına indi ve geri döndü (Boğa Sinyali)
            if (df['low'].iloc[-2] < df['bb_lower'].iloc[-2]) and (df['close'].iloc[-1] > df['bb_lower'].iloc[-1]):
                # Entry, Stop Loss ve Take Profit hesapla
                entry = df['close'].iloc[-1]
                stop_loss = min(df['low'].iloc[-3:]) * 0.99  # Son 3 mumun en düşüğünün %1 altı
                take_profit = df['bb_middle'].iloc[-1]  # Orta bant hedef
                
                # Sinyal kalitesini hesapla
                quality = self.calculate_signal_quality(df, is_bullish=True)
                
                # RSI aşırı satım bölgesindeyse kaliteyi artır
                if df['rsi'].iloc[-1] < self.config.TA_PARAMS['rsi_oversold']:
                    quality += 15
                
                signals.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': 'Bollinger Band Bounce (Lower)',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': df.index[-1],
                    'quality_score': quality,
                    'description': 'Fiyat alt Bollinger bandından sekti. Olası bir yükseliş sinyali.'
                })
            
            # Fiyat üst bandın üstüne çıktı ve geri döndü (Ayı Sinyali)
            if (df['high'].iloc[-2] > df['bb_upper'].iloc[-2]) and (df['close'].iloc[-1] < df['bb_upper'].iloc[-1]):
                # Entry, Stop Loss ve Take Profit hesapla
                entry = df['close'].iloc[-1]
                stop_loss = max(df['high'].iloc[-3:]) * 1.01  # Son 3 mumun en yükseğinin %1 üstü
                take_profit = df['bb_middle'].iloc[-1]  # Orta bant hedef
                
                # Sinyal kalitesini hesapla
                quality = self.calculate_signal_quality(df, is_bullish=False)
                
                # RSI aşırı alım bölgesindeyse kaliteyi artır
                if df['rsi'].iloc[-1] > self.config.TA_PARAMS['rsi_overbought']:
                    quality += 15
                
                signals.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': 'Bollinger Band Bounce (Upper)',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': df.index[-1],
                    'quality_score': quality,
                    'description': 'Fiyat üst Bollinger bandından sekti. Olası bir düşüş sinyali.'
                })
        
        except Exception as e:
            logger.error(f"Bollinger Bantları kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals