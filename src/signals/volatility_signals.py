#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Volatilite Sinyalleri Modülü
"""
import numpy as np
import pandas as pd
from signals.base_signal import BaseSignal
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("volatility_signals")

class VolatilitySignals(BaseSignal):
    """Volatilite tabanlı sinyalleri tespit eden sınıf"""
    
    def __init__(self, config):
        """Volatilite sinyal tespit parametrelerini ayarlar"""
        super().__init__(config)
        self.name = "Volatility Signals"
        logger.info("Volatilite sinyal modülü başlatıldı")
    
    def check_signals(self, symbol, timeframe, df):
        """
        Volatilite tabanlı tüm sinyalleri kontrol eder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        signals = []
        
        # BTC için Anormal Volatilite Uyarısı
        if symbol == "BTCUSDT":
            volatility_signals = self.check_btc_volatility(timeframe, df)
            signals.extend(volatility_signals)
        
        return signals
    
    def check_btc_volatility(self, timeframe, df):
        """BTC için Anormal Volatilite Uyarısı kontrol eder"""
        signals = []
        
        try:
            # Son 20 mumun volatilitesini hesapla
            if len(df) < 21:
                return signals
            
            # True Range hesapla
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift(1))
            low_close = np.abs(df['low'] - df['close'].shift(1))
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr_20 = true_range.rolling(20).mean()
            
            # Son ATR değeri
            last_atr = atr_20.iloc[-1]
            
            # Son 100 mumun ortalama ATR'sini hesapla
            if len(df) >= 100:
                avg_atr_100 = atr_20.iloc[-100:].mean()
                
                # Son ATR, ortalama ATR'nin 2 katından fazlaysa
                if last_atr > 2 * avg_atr_100:
                    # Entry, Stop Loss ve Take Profit hesapla (bu bir uyarı sinyali olduğu için boş bırakılabilir)
                    entry = df['close'].iloc[-1]
                    stop_loss = None
                    take_profit = None
                    
                    signals.append({
                        'symbol': 'BTCUSDT',
                        'timeframe': timeframe,
                        'signal_type': 'BTC Volatility Alert',
                        'entry': entry,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'timestamp': df.index[-1],
                        'quality_score': 90,  # Yüksek öncelikli bir uyarı
                        'description': f'BTC\'de anormal volatilite tespit edildi. ATR: {last_atr:.2f}, Ortalama ATR: {avg_atr_100:.2f}. Dikkatli olun!'
                    })
        
        except Exception as e:
            logger.error(f"BTC volatilite kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals