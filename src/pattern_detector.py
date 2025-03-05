#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Mum Formasyonları Tespit Modülü
"""
import numpy as np
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("pattern_detector")

class PatternDetector:
    """Mum formasyonlarını tespit eden sınıf"""
    
    def __init__(self, config):
        """Mum formasyonu tespit parametrelerini ayarlar"""
        self.config = config
        logger.info("Mum formasyonu tespit modülü başlatıldı")
    
    def detect_patterns(self, df):
        """
        Tüm mum formasyonlarını tespit eder
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen formasyonlar listesi
        """
        patterns = []
        
        try:
            # Son 5 mumu kontrol et
            if len(df) < 5:
                return patterns
            
            # Pin Bar (Hammer/Shooting Star)
            pin_bar = self.detect_pin_bar(df)
            if pin_bar:
                patterns.append(pin_bar)
            
            # Engulfing Pattern
            engulfing = self.detect_engulfing(df)
            if engulfing:
                patterns.append(engulfing)
            
            # Doji
            doji = self.detect_doji(df)
            if doji:
                patterns.append(doji)
            
            # Morning/Evening Star
            star = self.detect_star(df)
            if star:
                patterns.append(star)
            
            # Three White Soldiers / Three Black Crows
            three_candles = self.detect_three_candles(df)
            if three_candles:
                patterns.append(three_candles)
            
            logger.info(f"{len(patterns)} adet mum formasyonu tespit edildi")
            
            return patterns
            
        except Exception as e:
            logger.error(f"Mum formasyonları tespit edilirken hata: {str(e)}", exc_info=True)
            return patterns
    
    def detect_pin_bar(self, df):
        """
        Pin Bar (Hammer/Shooting Star) formasyonunu tespit eder
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            dict: Tespit edilen formasyon bilgileri
        """
        try:
            # Son mumu kontrol et
            last_candle = df.iloc[-1]
            
            # Gövde ve gölge uzunluklarını hesapla
            body = abs(last_candle['close'] - last_candle['open'])
            upper_wick = last_candle['high'] - max(last_candle['open'], last_candle['close'])
            lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']
            
            # Pin Bar kriterleri
            is_hammer = (lower_wick > body * 2) and (upper_wick < body * 0.5)
            is_shooting_star = (upper_wick > body * 2) and (lower_wick < body * 0.5)
            
            if is_hammer:
                # Trend kontrolü
                is_bullish = df['close'].iloc[-5:-1].mean() < df['close'].iloc[-1]
                
                return {
                    'pattern_type': 'Hammer',
                    'is_bullish': True,
                    'description': 'Hammer formasyonu tespit edildi. Bu genellikle bir dip oluşumu ve olası bir yükseliş sinyalidir.'
                }
            
            if is_shooting_star:
                # Trend kontrolü
                is_bullish = df['close'].iloc[-5:-1].mean() > df['close'].iloc[-1]
                
                return {
                    'pattern_type': 'Shooting Star',
                    'is_bullish': False,
                    'description': 'Shooting Star formasyonu tespit edildi. Bu genellikle bir tepe oluşumu ve olası bir düşüş sinyalidir.'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Pin Bar tespiti sırasında hata: {str(e)}", exc_info=True)
            return None
    
    def detect_engulfing(self, df):
        """
        Engulfing (Yutan) formasyonunu tespit eder
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            dict: Tespit edilen formasyon bilgileri
        """
        try:
            # Son iki mumu kontrol et
            if len(df) < 2:
                return None
            
            current_candle = df.iloc[-1]
            prev_candle = df.iloc[-2]
            
            current_body = abs(current_candle['close'] - current_candle['open'])
            prev_body = abs(prev_candle['close'] - prev_candle['open'])
            
            # Bullish Engulfing
            is_bullish_engulfing = (
                current_candle['close'] > current_candle['open'] and  # Yükselen mum
                prev_candle['close'] < prev_candle['open'] and  # Düşen mum
                current_candle['open'] < prev_candle['close'] and  # Açılış önceki kapanışın altında
                current_candle['close'] > prev_candle['open'] and  # Kapanış önceki açılışın üstünde
                current_body > prev_body  # Gövde daha büyük
            )
            
            # Bearish Engulfing
            is_bearish_engulfing = (
                current_candle['close'] < current_candle['open'] and  # Düşen mum
                prev_candle['close'] > prev_candle['open'] and  # Yükselen mum
                current_candle['open'] > prev_candle['close'] and  # Açılış önceki kapanışın üstünde
                current_candle['close'] < prev_candle['open'] and  # Kapanış önceki açılışın altında
                current_body > prev_body  # Gövde daha büyük
            )
            
            if is_bullish_engulfing:
                return {
                    'pattern_type': 'Bullish Engulfing',
                    'is_bullish': True,
                    'description': 'Bullish Engulfing formasyonu tespit edildi. Bu genellikle bir dip oluşumu ve olası bir yükseliş sinyalidir.'
                }
            
            if is_bearish_engulfing:
                return {
                    'pattern_type': 'Bearish Engulfing',
                    'is_bullish': False,
                    'description': 'Bearish Engulfing formasyonu tespit edildi. Bu genellikle bir tepe oluşumu ve olası bir düşüş sinyalidir.'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Engulfing tespiti sırasında hata: {str(e)}", exc_info=True)
            return None
    
    def detect_doji(self, df):
        """
        Doji formasyonunu tespit eder
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            dict: Tespit edilen formasyon bilgileri
        """
        try:
            # Son mumu kontrol et
            last_candle = df.iloc[-1]
            
            # Gövde ve toplam mum uzunluğunu hesapla
            body = abs(last_candle['close'] - last_candle['open'])
            candle_range = last_candle['high'] - last_candle['low']
            
            # Doji kriteri: Gövde, toplam mumun %5'inden küçük
            is_doji = body <= (candle_range * 0.05) and candle_range > 0
            
            if is_doji:
                # Trend kontrolü
                prev_trend = df['close'].iloc[-5:-1].mean() > df['close'].iloc[-10:-5].mean()
                
                if prev_trend:  # Yükselen trend
                    return {
                        'pattern_type': 'Doji (Bearish)',
                        'is_bullish': False,
                        'description': 'Yükselen trend içinde Doji formasyonu tespit edildi. Bu genellikle bir kararsızlık ve olası bir trend değişimi sinyalidir.'
                    }
                else:  # Düşen trend
                    return {
                        'pattern_type': 'Doji (Bullish)',
                        'is_bullish': True,
                        'description': 'Düşen trend içinde Doji formasyonu tespit edildi. Bu genellikle bir kararsızlık ve olası bir trend değişimi sinyalidir.'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Doji tespiti sırasında hata: {str(e)}", exc_info=True)
            return None
    
    def detect_star(self, df):
        """
        Morning Star / Evening Star formasyonunu tespit eder
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            dict: Tespit edilen formasyon bilgileri
        """
        try:
            # Son üç mumu kontrol et
            if len(df) < 3:
                return None
            
            candle1 = df.iloc[-3]
            candle2 = df.iloc[-2]
            candle3 = df.iloc[-1]
            
            # Gövdeleri hesapla
            body1 = abs(candle1['close'] - candle1['open'])
            body2 = abs(candle2['close'] - candle2['open'])
            body3 = abs(candle3['close'] - candle3['open'])
            
            # Morning Star kriterleri
            is_morning_star = (
                candle1['close'] < candle1['open'] and  # İlk mum düşen
                body2 < body1 * 0.5 and  # İkinci mum küçük gövdeli
                candle3['close'] > candle3['open'] and  # Üçüncü mum yükselen
                candle3['close'] > (candle1['open'] + candle1['close']) / 2  # Üçüncü mum ilk mumun ortasının üzerinde
            )
            
            # Evening Star kriterleri
            is_evening_star = (
                candle1['close'] > candle1['open'] and  # İlk mum yükselen
                body2 < body1 * 0.5 and  # İkinci mum küçük gövdeli
                candle3['close'] < candle3['open'] and  # Üçüncü mum düşen
                candle3['close'] < (candle1['open'] + candle1['close']) / 2  # Üçüncü mum ilk mumun ortasının altında
            )
            
            if is_morning_star:
                return {
                    'pattern_type': 'Morning Star',
                    'is_bullish': True,
                    'description': 'Morning Star formasyonu tespit edildi. Bu genellikle bir dip oluşumu ve güçlü bir yükseliş sinyalidir.'
                }
            
            if is_evening_star:
                return {
                    'pattern_type': 'Evening Star',
                    'is_bullish': False,
                    'description': 'Evening Star formasyonu tespit edildi. Bu genellikle bir tepe oluşumu ve güçlü bir düşüş sinyalidir.'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Star formasyonu tespiti sırasında hata: {str(e)}", exc_info=True)
            return None
    
    def detect_three_candles(self, df):
        """
        Three White Soldiers / Three Black Crows formasyonunu tespit eder
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            dict: Tespit edilen formasyon bilgileri
        """
        try:
            # Son üç mumu kontrol et
            if len(df) < 3:
                return None
            
            candle1 = df.iloc[-3]
            candle2 = df.iloc[-2]
            candle3 = df.iloc[-1]
            
            # Three White Soldiers kriterleri
            is_three_white_soldiers = (
                candle1['close'] > candle1['open'] and  # İlk mum yükselen
                candle2['close'] > candle2['open'] and  # İkinci mum yükselen
                candle3['close'] > candle3['open'] and  # Üçüncü mum yükselen
                candle2['close'] > candle1['close'] and  # Her mum bir öncekinden daha yüksek kapanıyor
                candle3['close'] > candle2['close'] and
                candle2['open'] > candle1['open'] and  # Her mum bir öncekinden daha yüksek açılıyor
                candle3['open'] > candle2['open']
            )
            
            # Three Black Crows kriterleri
            is_three_black_crows = (
                candle1['close'] < candle1['open'] and  # İlk mum düşen
                candle2['close'] < candle2['open'] and  # İkinci mum düşen
                candle3['close'] < candle3['open'] and  # Üçüncü mum düşen
                candle2['close'] < candle1['close'] and  # Her mum bir öncekinden daha düşük kapanıyor
                candle3['close'] < candle2['close'] and
                candle2['open'] < candle1['open'] and  # Her mum bir öncekinden daha düşük açılıyor
                candle3['open'] < candle2['open']
            )
            
            if is_three_white_soldiers:
                return {
                    'pattern_type': 'Three White Soldiers',
                    'is_bullish': True,
                    'description': 'Three White Soldiers formasyonu tespit edildi. Bu güçlü bir yükseliş trendinin başlangıcını gösterebilir.'
                }
            
            if is_three_black_crows:
                return {
                    'pattern_type': 'Three Black Crows',
                    'is_bullish': False,
                    'description': 'Three Black Crows formasyonu tespit edildi. Bu güçlü bir düşüş trendinin başlangıcını gösterebilir.'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Three Candles formasyonu tespiti sırasında hata: {str(e)}", exc_info=True)
            return None