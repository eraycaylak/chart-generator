#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - RSI Sinyalleri Modülü
"""
import numpy as np
import pandas as pd
from signals.base_signal import BaseSignal
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("rsi_signals")

class RSISignals(BaseSignal):
    """RSI tabanlı sinyalleri tespit eden sınıf"""
    
    def __init__(self, config):
        """RSI sinyal tespit parametrelerini ayarlar"""
        super().__init__(config)
        self.name = "RSI Signals"
        logger.info("RSI sinyal modülü başlatıldı")
    
    def check_signals(self, symbol, timeframe, df):
        """
        RSI tabanlı tüm sinyalleri kontrol eder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        signals = []
        
        # RSI değerlerini kontrol et
        if 'rsi' not in df.columns:
            logger.warning(f"[X] {symbol} {timeframe} için RSI sütunu bulunamadı!")
            return signals
            
        if df['rsi'].isnull().all():
            logger.warning(f"[X] {symbol} {timeframe} için RSI değerleri hesaplanmamış veya hepsi NaN")
            return signals
        
        # Son RSI değerini logla
        last_rsi = df['rsi'].iloc[-1]
        logger.info(f"[SCAN] {symbol} {timeframe} için son RSI değeri: {last_rsi:.2f}")
        
        # RSI Aşırı Alım/Satım Bölgeleri
        logger.info(f"[SCAN] {symbol} {timeframe} için RSI aşırı alım/satım kontrolü yapılıyor...")
        extreme_signals = self.check_rsi_extreme(symbol, timeframe, df)
        signals.extend(extreme_signals)
        
        # RSI Uyumsuzlukları
        logger.info(f"[SCAN] {symbol} {timeframe} için RSI uyumsuzluk (Divergence) kontrolü yapılıyor...")
        divergence_signals = self.check_rsi_divergence(symbol, timeframe, df)
        signals.extend(divergence_signals)
        
        # Sonuçları logla
        if extreme_signals:
            logger.info(f"[OK] {symbol} {timeframe} için {len(extreme_signals)} adet RSI aşırı alım/satım sinyali bulundu")
        else:
            logger.info(f"[X] {symbol} {timeframe} için RSI aşırı alım/satım sinyali bulunamadı")
            
        if divergence_signals:
            logger.info(f"[OK] {symbol} {timeframe} için {len(divergence_signals)} adet RSI uyumsuzluk sinyali bulundu")
        else:
            logger.info(f"[X] {symbol} {timeframe} için RSI uyumsuzluk sinyali bulunamadı")
        
        return signals
    
    def check_rsi_divergence(self, symbol, timeframe, df):
        """RSI Uyumsuzluklarını kontrol eder"""
        signals = []
        
        try:
            # Son 50 mumu kontrol et
            lookback = min(50, len(df) - 1)
            
            if lookback < 10:
                logger.warning(f"[X] {symbol} {timeframe} için yeterli veri yok (en az 10 mum gerekli)")
                return signals
            
            # Fiyat ve RSI için yerel minimum ve maksimumları bul
            price_lows = []
            price_highs = []
            rsi_lows = []
            rsi_highs = []
            
            # Son 50 mumda yerel minimum ve maksimumları bul
            for i in range(5, lookback - 5):
                # Yerel minimum (dip) kontrolü
                if (df['low'].iloc[i-5:i].min() > df['low'].iloc[i]) and (df['low'].iloc[i+1:i+6].min() > df['low'].iloc[i]):
                    price_lows.append((i, df['low'].iloc[i]))
                
                # Yerel maksimum (tepe) kontrolü
                if (df['high'].iloc[i-5:i].max() < df['high'].iloc[i]) and (df['high'].iloc[i+1:i+6].max() < df['high'].iloc[i]):
                    price_highs.append((i, df['high'].iloc[i]))
                
                # RSI yerel minimum kontrolü
                if (df['rsi'].iloc[i-5:i].min() > df['rsi'].iloc[i]) and (df['rsi'].iloc[i+1:i+6].min() > df['rsi'].iloc[i]):
                    rsi_lows.append((i, df['rsi'].iloc[i]))
                
                # RSI yerel maksimum kontrolü
                if (df['rsi'].iloc[i-5:i].max() < df['rsi'].iloc[i]) and (df['rsi'].iloc[i+1:i+6].max() < df['rsi'].iloc[i]):
                    rsi_highs.append((i, df['rsi'].iloc[i]))
            
            # Bulunan dip ve tepe noktalarını logla
            logger.info(f"[SCAN] {symbol} {timeframe} için {len(price_lows)} fiyat dibi, {len(price_highs)} fiyat tepesi bulundu")
            logger.info(f"[SCAN] {symbol} {timeframe} için {len(rsi_lows)} RSI dibi, {len(rsi_highs)} RSI tepesi bulundu")
            
            # En son 2 dip ve tepe noktasını al
            if len(price_lows) >= 2 and len(rsi_lows) >= 2:
                # Son iki fiyat dibi
                last_price_lows = sorted(price_lows, key=lambda x: x[0], reverse=True)[:2]
                last_price_lows.sort(key=lambda x: x[0])  # Zaman sırasına göre sırala
                
                # Son iki RSI dibi
                last_rsi_lows = sorted(rsi_lows, key=lambda x: x[0], reverse=True)[:2]
                last_rsi_lows.sort(key=lambda x: x[0])  # Zaman sırasına göre sırala
                
                # Boğa uyumsuzluğu (Bullish Divergence) kontrolü
                # Fiyat düşük yaparken RSI yükseliyor
                price_trend = "düşüyor" if last_price_lows[1][1] < last_price_lows[0][1] else "yükseliyor"
                rsi_trend = "yükseliyor" if last_rsi_lows[1][1] > last_rsi_lows[0][1] else "düşüyor"
                
                logger.info(f"[SCAN] {symbol} {timeframe} için fiyat {price_trend}, RSI {rsi_trend}")
                
                if (last_price_lows[1][1] < last_price_lows[0][1]) and (last_rsi_lows[1][1] > last_rsi_lows[0][1]):
                    logger.info(f"[OK] {symbol} {timeframe} için Bullish Divergence tespit edildi!")
                    logger.info(f"   Fiyat dipleri: {last_price_lows[0][1]:.8g} -> {last_price_lows[1][1]:.8g}")
                    logger.info(f"   RSI dipleri: {last_rsi_lows[0][1]:.2f} -> {last_rsi_lows[1][1]:.2f}")
                    
                    # Entry, Stop Loss ve Take Profit hesapla
                    entry = df['close'].iloc[-1]
                    stop_loss = min(df['low'].iloc[-5:]) * 0.99  # Son 5 mumun en düşüğünün %1 altı
                    take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                    
                    # Sinyal kalitesini hesapla
                    quality = self.calculate_signal_quality(df, is_bullish=True)
                    
                    signals.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal_type': 'RSI Bullish Divergence',
                        'entry': entry,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'timestamp': df.index[-1],
                        'quality_score': quality,
                        'description': 'Fiyat düşük yaparken RSI yükseliyor. Olası bir yükseliş sinyali.'
                    })
                else:
                    logger.info(f"[X] {symbol} {timeframe} için Bullish Divergence tespit edilemedi")
            
            # En son 2 tepe noktasını kontrol et
            if len(price_highs) >= 2 and len(rsi_highs) >= 2:
                # Son iki fiyat tepesi
                last_price_highs = sorted(price_highs, key=lambda x: x[0], reverse=True)[:2]
                last_price_highs.sort(key=lambda x: x[0])  # Zaman sırasına göre sırala
                
                # Son iki RSI tepesi
                last_rsi_highs = sorted(rsi_highs, key=lambda x: x[0], reverse=True)[:2]
                last_rsi_highs.sort(key=lambda x: x[0])  # Zaman sırasına göre sırala
                
                # Ayı uyumsuzluğu (Bearish Divergence) kontrolü
                # Fiyat yüksek yaparken RSI düşüyor
                price_trend = "yükseliyor" if last_price_highs[1][1] > last_price_highs[0][1] else "düşüyor"
                rsi_trend = "düşüyor" if last_rsi_highs[1][1] < last_rsi_highs[0][1] else "yükseliyor"
                
                logger.info(f"[SCAN] {symbol} {timeframe} için fiyat {price_trend}, RSI {rsi_trend}")
                
                if (last_price_highs[1][1] > last_price_highs[0][1]) and (last_rsi_highs[1][1] < last_rsi_highs[0][1]):
                    logger.info(f"[OK] {symbol} {timeframe} için Bearish Divergence tespit edildi!")
                    logger.info(f"   Fiyat tepeleri: {last_price_highs[0][1]:.8g} -> {last_price_highs[1][1]:.8g}")
                    logger.info(f"   RSI tepeleri: {last_rsi_highs[0][1]:.2f} -> {last_rsi_highs[1][1]:.2f}")
                    
                    # Entry, Stop Loss ve Take Profit hesapla
                    entry = df['close'].iloc[-1]
                    stop_loss = max(df['high'].iloc[-5:]) * 1.01  # Son 5 mumun en yükseğinin %1 üstü
                    take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                    
                    # Sinyal kalitesini hesapla
                    quality = self.calculate_signal_quality(df, is_bullish=False)
                    
                    signals.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal_type': 'RSI Bearish Divergence',
                        'entry': entry,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'timestamp': df.index[-1],
                        'quality_score': quality,
                        'description': 'Fiyat yüksek yaparken RSI düşüyor. Olası bir düşüş sinyali.'
                    })
                else:
                    logger.info(f"[X] {symbol} {timeframe} için Bearish Divergence tespit edilemedi")
        
        except Exception as e:
            logger.error(f"RSI uyumsuzluğu kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals
    
    def check_rsi_extreme(self, symbol, timeframe, df):
        """RSI Aşırı Alım/Satım durumlarını kontrol eder"""
        signals = []
        
        try:
            # Son 5 mumu kontrol et
            if len(df) < 5:
                logger.warning(f"[X] {symbol} {timeframe} için yeterli veri yok (en az 5 mum gerekli)")
                return signals
            
            # Son RSI değeri
            last_rsi = df['rsi'].iloc[-1]
            
            # RSI değerini logla
            logger.info(f"[SCAN] {symbol} {timeframe} için son RSI değeri: {last_rsi:.2f}")
            logger.info(f"[SCAN] Aşırı satım eşiği: {self.config.TA_PARAMS['rsi_oversold']}, Aşırı alım eşiği: {self.config.TA_PARAMS['rsi_overbought']}")
            
            # Aşırı satım bölgesi (RSI < 30)
            if last_rsi < self.config.TA_PARAMS['rsi_oversold']:
                logger.info(f"[OK] {symbol} {timeframe} için RSI aşırı satım bölgesinde: {last_rsi:.2f} < {self.config.TA_PARAMS['rsi_oversold']}")
                
                # Entry, Stop Loss ve Take Profit hesapla
                entry = df['close'].iloc[-1]
                stop_loss = min(df['low'].iloc[-5:]) * 0.98  # Son 5 mumun en düşüğünün %2 altı
                take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                
                # Sinyal kalitesini hesapla
                quality = self.calculate_signal_quality(df, is_bullish=True)
                
                # RSI değeri çok düşükse kaliteyi artır
                if last_rsi < 20:
                    quality += 15
                    signal_type = "RSI Extremely Oversold"
                    description = f'RSI aşırı satım bölgesinde ({last_rsi:.1f} < 20). Güçlü bir yükseliş sinyali olabilir.'
                else:
                    signal_type = "RSI Oversold"
                    description = f'RSI aşırı satım bölgesinde ({last_rsi:.1f} < 30). Olası bir yükseliş sinyali.'
                
                signals.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': signal_type,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': df.index[-1],
                    'quality_score': quality,
                    'description': description
                })
            else:
                logger.info(f"[X] {symbol} {timeframe} için RSI aşırı satım bölgesinde değil: {last_rsi:.2f} >= {self.config.TA_PARAMS['rsi_oversold']}")
            
            # Aşırı alım bölgesi (RSI > 70)
            if last_rsi > self.config.TA_PARAMS['rsi_overbought']:
                logger.info(f"[OK] {symbol} {timeframe} için RSI aşırı alım bölgesinde: {last_rsi:.2f} > {self.config.TA_PARAMS['rsi_overbought']}")
                
                # Entry, Stop Loss ve Take Profit hesapla
                entry = df['close'].iloc[-1]
                stop_loss = max(df['high'].iloc[-5:]) * 1.02  # Son 5 mumun en yükseğinin %2 üstü
                take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                
                # Sinyal kalitesini hesapla
                quality = self.calculate_signal_quality(df, is_bullish=False)
                
                # RSI değeri çok yüksekse kaliteyi artır
                if last_rsi > 80:
                    quality += 15
                    signal_type = "RSI Extremely Overbought"
                    description = f'RSI aşırı alım bölgesinde ({last_rsi:.1f} > 80). Güçlü bir düşüş sinyali olabilir.'
                else:
                    signal_type = "RSI Overbought"
                    description = f'RSI aşırı alım bölgesinde ({last_rsi:.1f} > 70). Olası bir düşüş sinyali.'
                
                signals.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': signal_type,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': df.index[-1],
                    'quality_score': quality,
                    'description': description
                })
            else:
                logger.info(f"[X] {symbol} {timeframe} için RSI aşırı alım bölgesinde değil: {last_rsi:.2f} <= {self.config.TA_PARAMS['rsi_overbought']}")
        
        except Exception as e:
            logger.error(f"RSI aşırı alım/satım kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals