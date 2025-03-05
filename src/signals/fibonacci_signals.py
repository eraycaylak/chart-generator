#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Fibonacci Sinyalleri Modülü
"""
from signals.base_signal import BaseSignal
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("fibonacci_signals")

class FibonacciSignals(BaseSignal):
    """Fibonacci tabanlı sinyalleri tespit eden sınıf"""
    
    def __init__(self, config):
        """Fibonacci sinyal tespit parametrelerini ayarlar"""
        super().__init__(config)
        self.name = "Fibonacci Signals"
        logger.info("Fibonacci sinyal modülü başlatıldı")
    
    def check_signals(self, symbol, timeframe, df):
        """
        Fibonacci tabanlı tüm sinyalleri kontrol eder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        signals = []
        
        # Fibonacci Geri Çekilme Seviyeleri
        fib_signals = self.check_fibonacci_levels(symbol, timeframe, df)
        signals.extend(fib_signals)
        
        return signals
    
    def check_fibonacci_levels(self, symbol, timeframe, df):
        """Fibonacci Geri Çekilme Seviyelerini kontrol eder"""
        signals = []
        
        try:
            # Son 100 mumu kontrol et
            if len(df) < 100:
                return signals
            
            # Son 100 mumda yüksek ve düşük noktaları bul
            high_point = df['high'].iloc[-100:].max()
            low_point = df['low'].iloc[-100:].min()
            
            # Fibonacci seviyeleri (yüksekten düşüğe)
            fib_levels = {
                0: high_point,
                0.5: high_point - 0.5 * (high_point - low_point),
                0.618: high_point - 0.618 * (high_point - low_point),
                0.705: high_point - 0.705 * (high_point - low_point),
                0.786: high_point - 0.786 * (high_point - low_point),
                1: low_point
            }
            
            # Son kapanış fiyatı
            last_close = df['close'].iloc[-1]
            
            # En iyi Fibonacci seviyesi sinyalini bul
            best_fib_signal = None
            best_fib_quality = 0
            
            # Fiyatın Fibonacci seviyelerine yakınlığını kontrol et
            for level, price in fib_levels.items():
                # Fiyat Fibonacci seviyesine %1 yakınsa
                if 0.99 * price <= last_close <= 1.01 * price:
                    # Trendin yönünü belirle
                    is_uptrend = df['close'].iloc[-20:].mean() > df['close'].iloc[-40:-20].mean()
                    
                    # Entry, Stop Loss ve Take Profit hesapla
                    entry = last_close
                    
                    if is_uptrend:
                        # Yükselen trend - destek olarak kullan
                        stop_loss = price * 0.98  # Fib seviyesinin %2 altı
                        
                        # Bir sonraki Fibonacci seviyesini hedefle
                        next_levels = [l for l, p in fib_levels.items() if l < level]
                        if next_levels:
                            next_level = max(next_levels)
                            take_profit = fib_levels[next_level]
                        else:
                            take_profit = entry + (entry - stop_loss) * 2
                        
                        quality = self.calculate_signal_quality(df, is_bullish=True)
                        signal_type = f'Fibonacci Destek ({level})'
                        description = f'Fiyat {level} Fibonacci destek seviyesine yaklaştı. Olası bir yükseliş sinyali.'
                    else:
                        # Düşen trend - direnç olarak kullan
                        stop_loss = price * 1.02  # Fib seviyesinin %2 üstü
                        
                        # Bir sonraki Fibonacci seviyesini hedefle
                        next_levels = [l for l, p in fib_levels.items() if l > level]
                        if next_levels:
                            next_level = min(next_levels)
                            take_profit = fib_levels[next_level]
                        else:
                            take_profit = entry - (stop_loss - entry) * 2
                        
                        quality = self.calculate_signal_quality(df, is_bullish=False)
                        signal_type = f'Fibonacci Direnç ({level})'
                        description = f'Fiyat {level} Fibonacci direnç seviyesine yaklaştı. Olası bir düşüş sinyali.'
                    
                    # Eğer bu seviye daha iyi bir kaliteye sahipse, en iyi sinyal olarak kaydet
                    if quality > best_fib_quality:
                        best_fib_quality = quality
                        best_fib_signal = {
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'signal_type': signal_type,
                            'entry': entry,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'timestamp': df.index[-1],
                            'quality_score': quality,
                            'description': description
                        }
            
            # Eğer bir Fibonacci sinyali bulunduysa, listeye ekle
            if best_fib_signal:
                signals.append(best_fib_signal)
        
        except Exception as e:
            logger.error(f"Fibonacci seviyeleri kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals