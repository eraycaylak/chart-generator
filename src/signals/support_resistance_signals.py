#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Destek ve Direnç Sinyalleri Modülü
"""
from signals.base_signal import BaseSignal
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("sr_signals")

class SupportResistanceSignals(BaseSignal):
    """Destek ve direnç tabanlı sinyalleri tespit eden sınıf"""
    
    def __init__(self, config):
        """Destek ve direnç sinyal tespit parametrelerini ayarlar"""
        super().__init__(config)
        self.name = "Support & Resistance Signals"
        logger.info("Destek ve direnç sinyal modülü başlatıldı")
    
    def check_signals(self, symbol, timeframe, df):
        """
        Destek ve direnç tabanlı tüm sinyalleri kontrol eder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        signals = []
        
        # Destek & Direnç Bölgeleri
        sr_signals = self.check_support_resistance(symbol, timeframe, df)
        signals.extend(sr_signals)
        
        return signals
    
    def check_support_resistance(self, symbol, timeframe, df):
        """Destek ve Direnç Bölgelerini kontrol eder"""
        signals = []
        
        try:
            # Support Resistance sınıfını oluştur
            from support_resistance import SupportResistance
            sr = SupportResistance(self.config)
            
            # Destek ve direnç seviyelerini hesapla
            levels = sr.find_levels(df)
            
            # Son kapanış fiyatı
            last_close = df['close'].iloc[-1]
            
            # Destek seviyelerine yakınlık kontrolü
            for level in levels['support']:
                # Fiyat destek seviyesine %2 yakınsa
                if 0.98 * last_close <= level <= 1.02 * last_close:
                    # Entry, Stop Loss ve Take Profit hesapla
                    entry = last_close
                    stop_loss = level * 0.98  # Destek seviyesinin %2 altı
                    
                    # En yakın direnç seviyesini bul
                    resistance_levels = [r for r in levels['resistance'] if r > last_close]
                    if resistance_levels:
                        take_profit = min(resistance_levels)  # En yakın direnç
                    else:
                        take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                    
                    # Sinyal kalitesini hesapla
                    quality = self.calculate_signal_quality(df, is_bullish=True)
                    
                    # Hacim artıyorsa kaliteyi artır
                    if df['volume'].iloc[-1] > df['volume'].iloc[-2]:
                        quality += 10
                    
                    signals.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal_type': 'Support Level Test',
                        'entry': entry,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'timestamp': df.index[-1],
                        'quality_score': quality,
                        'description': f'Fiyat {level:.2f} destek seviyesine yaklaştı. Olası bir yükseliş sinyali.'
                    })
            
            # Direnç seviyelerine yakınlık kontrolü
            for level in levels['resistance']:
                # Fiyat direnç seviyesine %2 yakınsa
                if 0.98 * level <= last_close <= 1.02 * level:
                    # Entry, Stop Loss ve Take Profit hesapla
                    entry = last_close
                    stop_loss = level * 1.02  # Direnç seviyesinin %2 üstü
                    
                    # En yakın destek seviyesini bul
                    support_levels = [s for s in levels['support'] if s < last_close]
                    if support_levels:
                        take_profit = max(support_levels)  # En yakın destek
                    else:
                        take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                    
                    # Sinyal kalitesini hesapla
                    quality = self.calculate_signal_quality(df, is_bullish=False)
                    
                    # Hacim artıyorsa kaliteyi artır
                    if df['volume'].iloc[-1] > df['volume'].iloc[-2]:
                        quality += 10
                    
                    signals.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal_type': 'Resistance Level Test',
                        'entry': entry,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'timestamp': df.index[-1],
                        'quality_score': quality,
                        'description': f'Fiyat {level:.2f} direnç seviyesine yaklaştı. Olası bir düşüş sinyali.'
                    })
        
        except Exception as e:
            logger.error(f"Destek/direnç kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals