#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Destek ve Direnç Seviyeleri Modülü
"""
import numpy as np
import pandas as pd
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("support_resistance")

class SupportResistance:
    """Destek ve direnç seviyelerini tespit eden sınıf"""
    
    def __init__(self, config):
        """Destek ve direnç tespit parametrelerini ayarlar"""
        self.config = config
        logger.info("Destek ve direnç modülü başlatıldı")
    
    def find_levels(self, df, window=20, threshold=0.01):
        """
        Destek ve direnç seviyelerini tespit eder
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            window (int): Yerel minimum/maksimum için pencere boyutu
            threshold (float): Seviyeleri birleştirmek için eşik değeri (%)
            
        Returns:
            dict: Destek ve direnç seviyeleri
        """
        try:
            # Son 200 mumu kontrol et (veya mevcut tüm verileri)
            lookback = min(200, len(df))
            df_subset = df.iloc[-lookback:]
            
            # Yerel minimum ve maksimumları bul
            highs = self._find_local_maxima(df_subset, window)
            lows = self._find_local_minima(df_subset, window)
            
            # Yakın seviyeleri birleştir
            support_levels = self._merge_levels(lows, threshold)
            resistance_levels = self._merge_levels(highs, threshold)
            
            # Mevcut fiyata göre seviyeleri filtrele
            current_price = df['close'].iloc[-1]
            
            # Destek seviyeleri - mevcut fiyatın altındakiler
            support_levels = [level for level in support_levels if level < current_price]
            
            # Direnç seviyeleri - mevcut fiyatın üstündekiler
            resistance_levels = [level for level in resistance_levels if level > current_price]
            
            # Seviyeleri önem sırasına göre sırala
            support_levels = sorted(support_levels, reverse=True)  # Fiyata en yakın olanlar önce
            resistance_levels = sorted(resistance_levels)  # Fiyata en yakın olanlar önce
            
            logger.info(f"{len(support_levels)} destek ve {len(resistance_levels)} direnç seviyesi tespit edildi")
            
            return {
                'support': support_levels,
                'resistance': resistance_levels
            }
            
        except Exception as e:
            logger.error(f"Destek ve direnç seviyeleri tespit edilirken hata: {str(e)}", exc_info=True)
            return {'support': [], 'resistance': []}
    
    def _find_local_maxima(self, df, window):
        """
        Yerel maksimumları (tepe noktaları) tespit eder
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            window (int): Pencere boyutu
            
        Returns:
            list: Yerel maksimum fiyatları
        """
        highs = []
        
        try:
            for i in range(window, len(df) - window):
                # Önceki ve sonraki penceredeki en yüksek değerler
                prev_max = df['high'].iloc[i-window:i].max()
                next_max = df['high'].iloc[i+1:i+window+1].max()
                
                # Eğer mevcut mum her iki penceredeki en yüksek değerlerden daha yüksekse
                if df['high'].iloc[i] > prev_max and df['high'].iloc[i] > next_max:
                    highs.append(df['high'].iloc[i])
            
            return highs
            
        except Exception as e:
            logger.error(f"Yerel maksimumlar tespit edilirken hata: {str(e)}", exc_info=True)
            return highs
    
    def _find_local_minima(self, df, window):
        """
        Yerel minimumları (dip noktaları) tespit eder
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            window (int): Pencere boyutu
            
        Returns:
            list: Yerel minimum fiyatları
        """
        lows = []
        
        try:
            for i in range(window, len(df) - window):
                # Önceki ve sonraki penceredeki en düşük değerler
                prev_min = df['low'].iloc[i-window:i].min()
                next_min = df['low'].iloc[i+1:i+window+1].min()
                
                # Eğer mevcut mum her iki penceredeki en düşük değerlerden daha düşükse
                if df['low'].iloc[i] < prev_min and df['low'].iloc[i] < next_min:
                    lows.append(df['low'].iloc[i])
            
            return lows
            
        except Exception as e:
            logger.error(f"Yerel minimumlar tespit edilirken hata: {str(e)}", exc_info=True)
            return lows
    
    def _merge_levels(self, levels, threshold):
        """
        Yakın seviyeleri birleştirir
        
        Args:
            levels (list): Seviyeler listesi
            threshold (float): Birleştirme eşiği (%)
            
        Returns:
            list: Birleştirilmiş seviyeler
        """
        if not levels:
            return []
        
        try:
            # Seviyeleri sırala
            sorted_levels = sorted(levels)
            merged_levels = []
            
            # İlk seviyeyi ekle
            current_level = sorted_levels[0]
            level_count = 1
            
            for level in sorted_levels[1:]:
                # Eğer mevcut seviye ile yeni seviye arasındaki fark eşikten küçükse
                if abs(level - current_level) / current_level <= threshold:
                    # Seviyeleri birleştir (ağırlıklı ortalama)
                    current_level = (current_level * level_count + level) / (level_count + 1)
                    level_count += 1
                else:
                    # Mevcut seviyeyi kaydet ve yeni seviyeye geç
                    merged_levels.append(current_level)
                    current_level = level
                    level_count = 1
            
            # Son seviyeyi ekle
            merged_levels.append(current_level)
            
            return merged_levels
            
        except Exception as e:
            logger.error(f"Seviyeler birleştirilirken hata: {str(e)}", exc_info=True)
            return levels