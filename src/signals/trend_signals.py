#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Trend Sinyalleri Modülü
"""
from signals.base_signal import BaseSignal
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("trend_signals")

class TrendSignals(BaseSignal):
    """Trend tabanlı sinyalleri tespit eden sınıf"""
    
    def __init__(self, config):
        """Trend sinyal tespit parametrelerini ayarlar"""
        super().__init__(config)
        self.name = "Trend Signals"
        logger.info("Trend sinyal modülü başlatıldı")
    
    def check_signals(self, symbol, timeframe, df):
        """
        Trend tabanlı tüm sinyalleri kontrol eder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        signals = []
        
        # Trend Değişimi Sinyalleri
        trend_signals = self.check_trend_change(symbol, timeframe, df)
        signals.extend(trend_signals)
        
        # Parabolic SAR Sinyalleri
        psar_signals = self.check_parabolic_sar(symbol, timeframe, df)
        signals.extend(psar_signals)
        
        # ADX Trend Gücü Sinyalleri
        adx_signals = self.check_adx(symbol, timeframe, df)
        signals.extend(adx_signals)
        
        # Yatay Destek/Direnç Sinyalleri
        horizontal_sr_signals = self.check_horizontal_sr(symbol, timeframe, df)
        signals.extend(horizontal_sr_signals)
        
        return signals
    
    def check_trend_change(self, symbol, timeframe, df):
        """Trend Değişimi Sinyallerini kontrol eder"""
        signals = []
        
        try:
            # Son 5 mumu kontrol et
            if len(df) < 50:
                return signals
            
            # Kısa ve uzun dönem EMA'ları kullan
            short_ema = df['ema_short']
            long_ema = df['ema_long']
            
            # Trend yönünü belirle
            prev_trend = short_ema.iloc[-6] > long_ema.iloc[-6]  # 5 mum önceki trend
            current_trend = short_ema.iloc[-1] > long_ema.iloc[-1]  # Şu anki trend
            
            # Trend değişimi kontrolü
            if prev_trend != current_trend:
                # Yükselen trend başlangıcı
                if current_trend:
                    # Entry, Stop Loss ve Take Profit hesapla
                    entry = df['close'].iloc[-1]
                    stop_loss = min(df['low'].iloc[-5:]) * 0.98  # Son 5 mumun en düşüğünün %2 altı
                    take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                    
                    # Sinyal kalitesini hesapla
                    quality = self.calculate_signal_quality(df, is_bullish=True)
                    
                    # Hacim artışı varsa kaliteyi artır
                    if df['volume'].iloc[-1] > df['volume'].iloc[-5:].mean() * 1.5:
                        quality += 10
                    
                    signals.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal_type': 'Yükselen Trend Başlangıcı',
                        'entry': entry,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'timestamp': df.index[-1],
                        'quality_score': quality,
                        'description': 'Yükselen trend başlangıcı tespit edildi. Kısa dönem EMA uzun dönem EMA\'yı yukarı kesti.'
                    })
                # Düşen trend başlangıcı
                else:
                    # Entry, Stop Loss ve Take Profit hesapla
                    entry = df['close'].iloc[-1]
                    stop_loss = max(df['high'].iloc[-5:]) * 1.02  # Son 5 mumun en yükseğinin %2 üstü
                    take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                    
                    # Sinyal kalitesini hesapla
                    quality = self.calculate_signal_quality(df, is_bullish=False)
                    
                    # Hacim artışı varsa kaliteyi artır
                    if df['volume'].iloc[-1] > df['volume'].iloc[-5:].mean() * 1.5:
                        quality += 10
                    
                    signals.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal_type': 'Düşen Trend Başlangıcı',
                        'entry': entry,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'timestamp': df.index[-1],
                        'quality_score': quality,
                        'description': 'Düşen trend başlangıcı tespit edildi. Kısa dönem EMA uzun dönem EMA\'yı aşağı kesti.'
                    })
        
        except Exception as e:
            logger.error(f"Trend değişimi kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals
    
    def check_parabolic_sar(self, symbol, timeframe, df):
        """Parabolic SAR Sinyallerini kontrol eder"""
        signals = []
        
        try:
            # Son 5 mumu kontrol et
            if len(df) < 5 or 'psar' not in df.columns:
                return signals
            
            # Son iki mumun PSAR değerlerini kontrol et
            prev_psar_above = df['psar'].iloc[-2] > df['high'].iloc[-2]  # PSAR mumun üstünde
            current_psar_above = df['psar'].iloc[-1] > df['high'].iloc[-1]  # PSAR mumun üstünde
            
            # PSAR pozisyon değişimi kontrolü
            if prev_psar_above != current_psar_above:
                # Yükselen trend başlangıcı (PSAR mumun altına geçti)
                if not current_psar_above:
                    # Entry, Stop Loss ve Take Profit hesapla
                    entry = df['close'].iloc[-1]
                    stop_loss = df['psar'].iloc[-1] * 0.98  # PSAR'ın %2 altı
                    take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                    
                    # Sinyal kalitesini hesapla
                    quality = self.calculate_signal_quality(df, is_bullish=True)
                    
                    signals.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal_type': 'Parabolic SAR Yükseliş',
                        'entry': entry,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'timestamp': df.index[-1],
                        'quality_score': quality,
                        'description': 'Parabolic SAR mumun altına geçti. Olası bir yükseliş sinyali.'
                    })
                # Düşen trend başlangıcı (PSAR mumun üstüne geçti)
                else:
                    # Entry, Stop Loss ve Take Profit hesapla
                    entry = df['close'].iloc[-1]
                    stop_loss = df['psar'].iloc[-1] * 1.02  # PSAR'ın %2 üstü
                    take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                    
                    # Sinyal kalitesini hesapla
                    quality = self.calculate_signal_quality(df, is_bullish=False)
                    
                    signals.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal_type': 'Parabolic SAR Düşüş',
                        'entry': entry,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'timestamp': df.index[-1],
                        'quality_score': quality,
                        'description': 'Parabolic SAR mumun üstüne geçti. Olası bir düşüş sinyali.'
                    })
        
        except Exception as e:
            logger.error(f"Parabolic SAR kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals
    
    def check_adx(self, symbol, timeframe, df):
        """ADX Trend Gücü Sinyallerini kontrol eder"""
        signals = []
        
        try:
            # ADX değerlerini kontrol et
            if 'adx' not in df.columns or len(df) < 5:
                return signals
            
            # Son ADX değeri
            last_adx = df['adx'].iloc[-1]
            
            # ADX trend gücü eşikleri
            weak_trend = 20
            strong_trend = 25
            very_strong_trend = 40
            
            # Trend yönünü belirle (DI+ ve DI- karşılaştırması)
            if 'plus_di' in df.columns and 'minus_di' in df.columns:
                is_bullish = df['plus_di'].iloc[-1] > df['minus_di'].iloc[-1]
                
                # Güçlü trend başlangıcı (ADX 20'nin üzerine çıktı)
                if last_adx > strong_trend and df['adx'].iloc[-2] <= strong_trend:
                    # Entry, Stop Loss ve Take Profit hesapla
                    entry = df['close'].iloc[-1]
                    
                    if is_bullish:
                        stop_loss = min(df['low'].iloc[-5:]) * 0.98  # Son 5 mumun en düşüğünün %2 altı
                        take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                        
                        # Sinyal kalitesini hesapla
                        quality = self.calculate_signal_quality(df, is_bullish=True)
                        
                        signals.append({
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'signal_type': 'Güçlü Yükselen Trend (ADX)',
                            'entry': entry,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'timestamp': df.index[-1],
                            'quality_score': quality,
                            'description': f'ADX {last_adx:.1f} ile güçlü bir yükselen trend başlangıcı gösteriyor.'
                        })
                    else:
                        stop_loss = max(df['high'].iloc[-5:]) * 1.02  # Son 5 mumun en yükseğinin %2 üstü
                        take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                        
                        # Sinyal kalitesini hesapla
                        quality = self.calculate_signal_quality(df, is_bullish=False)
                        
                        signals.append({
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'signal_type': 'Güçlü Düşen Trend (ADX)',
                            'entry': entry,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'timestamp': df.index[-1],
                            'quality_score': quality,
                            'description': f'ADX {last_adx:.1f} ile güçlü bir düşen trend başlangıcı gösteriyor.'
                        })
                
                # Çok güçlü trend (ADX 40'ın üzerinde)
                elif last_adx > very_strong_trend:
                    # Entry, Stop Loss ve Take Profit hesapla
                    entry = df['close'].iloc[-1]
                    
                    if is_bullish:
                        stop_loss = min(df['low'].iloc[-5:]) * 0.98  # Son 5 mumun en düşüğünün %2 altı
                        take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                        
                        # Sinyal kalitesini hesapla
                        quality = self.calculate_signal_quality(df, is_bullish=True)
                        quality += 15  # Çok güçlü trend için bonus
                        
                        signals.append({
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'signal_type': 'Çok Güçlü Yükselen Trend (ADX)',
                            'entry': entry,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'timestamp': df.index[-1],
                            'quality_score': quality,
                            'description': f'ADX {last_adx:.1f} ile çok güçlü bir yükselen trend gösteriyor. Trend takibi için uygun.'
                        })
                    else:
                        stop_loss = max(df['high'].iloc[-5:]) * 1.02  # Son 5 mumun en yükseğinin %2 üstü
                        take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                        
                        # Sinyal kalitesini hesapla
                        quality = self.calculate_signal_quality(df, is_bullish=False)
                        quality += 15  # Çok güçlü trend için bonus
                        
                        signals.append({
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'signal_type': 'Çok Güçlü Düşen Trend (ADX)',
                            'entry': entry,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'timestamp': df.index[-1],
                            'quality_score': quality,
                            'description': f'ADX {last_adx:.1f} ile çok güçlü bir düşen trend gösteriyor. Trend takibi için uygun.'
                        })
        
        except Exception as e:
            logger.error(f"ADX kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals
    
    def check_horizontal_sr(self, symbol, timeframe, df):
        """Yatay Destek/Direnç Sinyallerini kontrol eder"""
        signals = []
        
        try:
            # Son 50 mumu kontrol et
            if len(df) < 50:
                return signals
            
            # Destek ve direnç seviyelerini hesapla
            from support_resistance import SupportResistance
            sr = SupportResistance(self.config)
            levels = sr.find_levels(df)
            
            # Son kapanış fiyatı
            last_close = df['close'].iloc[-1]
            
            # Yatay destek kontrolü
            for level in levels['support']:
                # Fiyat destek seviyesine %1 yakınsa
                if 0.99 * last_close <= level <= 1.01 * last_close:
                    # Son 20 mumda bu seviyenin test edilip edilmediğini kontrol et
                    test_count = 0
                    for i in range(-20, 0):
                        if 0.99 * level <= df['low'].iloc[i] <= 1.01 * level:
                            test_count += 1
                    
                    # En az 2 kez test edilmişse, yatay destek olarak kabul et
                    if test_count >= 2:
                        # Entry, Stop Loss ve Take Profit hesapla
                        entry = df['close'].iloc[-1]
                        stop_loss = level * 0.98  # Destek seviyesinin %2 altı
                        take_profit = entry + (entry - stop_loss) * 2  # 1:2 risk-ödül oranı
                        
                        # Sinyal kalitesini hesapla
                        quality = self.calculate_signal_quality(df, is_bullish=True)
                        quality += 10  # Yatay destek için bonus
                        
                        signals.append({
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'signal_type': 'Yatay Destek Bölgesi',
                            'entry': entry,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'timestamp': df.index[-1],
                            'quality_score': quality,
                            'description': f'Fiyat {level:.8g} seviyesindeki yatay destek bölgesine yaklaştı. Bu seviye son dönemde birkaç kez test edildi.'
                        })
            
            # Yatay direnç kontrolü
            for level in levels['resistance']:
                # Fiyat direnç seviyesine %1 yakınsa
                if 0.99 * level <= last_close <= 1.01 * level:
                    # Son 20 mumda bu seviyenin test edilip edilmediğini kontrol et
                    test_count = 0
                    for i in range(-20, 0):
                        if 0.99 * level <= df['high'].iloc[i] <= 1.01 * level:
                            test_count += 1
                    
                    # En az 2 kez test edilmişse, yatay direnç olarak kabul et
                    if test_count >= 2:
                        # Entry, Stop Loss ve Take Profit hesapla
                        entry = df['close'].iloc[-1]
                        stop_loss = level * 1.02  # Direnç seviyesinin %2 üstü
                        take_profit = entry - (stop_loss - entry) * 2  # 1:2 risk-ödül oranı
                        
                        # Sinyal kalitesini hesapla
                        quality = self.calculate_signal_quality(df, is_bullish=False)
                        quality += 10  # Yatay direnç için bonus
                        
                        signals.append({
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'signal_type': 'Yatay Direnç Bölgesi',
                            'entry': entry,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'timestamp': df.index[-1],
                            'quality_score': quality,
                            'description': f'Fiyat {level:.8g} seviyesindeki yatay direnç bölgesine yaklaştı. Bu seviye son dönemde birkaç kez test edildi.'
                        })
        
        except Exception as e:
            logger.error(f"Yatay destek/direnç kontrolü sırasında hata: {str(e)}", exc_info=True)
        
        return signals