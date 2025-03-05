#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Mum Formasyonları Sinyalleri Modülü
"""
from signals.base_signal import BaseSignal
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("pattern_signals")

class PatternSignals(BaseSignal):
    """Mum formasyonları tabanlı sinyalleri tespit eden sınıf"""
    
    def __init__(self, config):
        """Mum formasyonları sinyal tespit parametrelerini ayarlar"""
        super().__init__(config)
        self.name = "Candlestick Pattern Signals"
        logger.info("Mum formasyonları sinyal modülü başlatıldı")
    
    def check_signals(self, symbol, timeframe, df):
        """
        Mum formasyonları tabanlı tüm sinyalleri kontrol eder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        signals = []
        
        # Mum Formasyonları
        pattern_signals = self.check_candlestick_patterns(symbol, timeframe, df)
        signals.extend(pattern_signals)
        
        return signals
    
    def check_candlestick_patterns(self, symbol, timeframe, df):
        """Mum Formasyonlarını kontrol eder"""
        signals = []
        
        try:
            # Pattern detector sınıfını oluştur
            from pattern_detector import PatternDetector
            pattern_detector = PatternDetector(self.config)
            
            # Mum formasyonlarını tespit et
            patterns = pattern_detector.detect_patterns(df)
            
            for pattern in patterns:
                pattern_type = pattern['pattern_type']
                is_bullish = pattern['is_bullish']
                
                # Entry, Stop Loss ve Take Profit hesapla
                entry = df['close'].iloc[-1]
                
                if is_bullish:
                    stop_loss = min(df['low'].iloc[-3:]) * 0.99  # Son 3 mumun en düşüğünün %1 altı
                    take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                    quality = self.calculate_signal_quality(df, is_bullish=True)
                else:
                    stop_loss = max(df['high'].iloc[-3:]) * 1.01  # Son 3 mumun en yükseğinin %1 üstü
                    take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                    quality = self.calculate_signal_quality(df, is_bullish=False)
                
                # Mum formasyonu sinyalini oluştur
                # Bu sinyaller artık "Diğer Tespit Edilen Sinyaller" bölümünde gösterilecek
                signals.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': f'Pattern: {pattern_type}',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': df.index[-1],
                    'quality_score': quality,
                    'description': pattern['description'],
                    'is_pattern': True  # Bu bir mum formasyonu sinyali olduğunu belirtmek için
                })
        
        except Exception as e:
            logger.error(f"Mum formasyonları kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals