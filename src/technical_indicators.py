#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Teknik İndikatörler Modülü
"""
import numpy as np
import pandas as pd
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("technical_indicators")

class TechnicalIndicators:
    """Teknik indikatörleri hesaplayan sınıf"""
    
    def __init__(self, config):
        """Teknik indikatör parametrelerini ayarlar"""
        self.config = config
        self.params = config.TA_PARAMS
        logger.info("Teknik indikatörler modülü başlatıldı")
    
    def add_all_indicators(self, df):
        """
        Tüm teknik indikatörleri hesaplar ve DataFrame'e ekler
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            pandas.DataFrame: İndikatörler eklenmiş DataFrame
        """
        try:
            # RSI
            df = self.add_rsi(df, self.params['rsi_period'])
            
            # EMA'lar
            df = self.add_ema(df, self.params['ema_short'], 'ema_short')
            df = self.add_ema(df, self.params['ema_medium'], 'ema_medium')
            df = self.add_ema(df, self.params['ema_long'], 'ema_long')
            
            # MACD
            df = self.add_macd(df, self.params['macd_fast'], self.params['macd_slow'], self.params['macd_signal'])
            
            # Bollinger Bantları
            df = self.add_bollinger_bands(df, self.params['bb_period'], self.params['bb_std'])
            
            # Ichimoku Bulutu
            df = self.add_ichimoku(df, self.params['ichimoku_tenkan'], self.params['ichimoku_kijun'], self.params['ichimoku_senkou_span_b'])
            
            # Parabolic SAR
            df = self.add_parabolic_sar(df)
            
            # ADX (Average Directional Index)
            df = self.add_adx(df)
            
            # OBV (On-Balance Volume)
            df = self.add_obv(df)
            
            logger.info("Tüm teknik indikatörler hesaplandı")
            
            return df
            
        except Exception as e:
            logger.error(f"İndikatörler hesaplanırken hata: {str(e)}", exc_info=True)
            return df
    
    def add_rsi(self, df, period=14):
        """
        Relative Strength Index (RSI) hesaplar
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            period (int): RSI periyodu
            
        Returns:
            pandas.DataFrame: RSI eklenmiş DataFrame
        """
        try:
            logger.info(f"RSI hesaplanıyor (periyot: {period})...")
            
            # Fiyat değişimlerini hesapla
            delta = df['close'].diff()
            
            # Pozitif ve negatif değişimleri ayır
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # İlk değerleri hesapla
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # Sonraki değerleri hesapla (Wilder's smoothing method)
            for i in range(period, len(df)):
                avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period-1) + gain.iloc[i]) / period
                avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period-1) + loss.iloc[i]) / period
            
            # RS ve RSI hesapla
            rs = avg_gain / avg_loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # RSI değerlerini kontrol et
            if df['rsi'].isnull().all():
                logger.warning("RSI değerleri hesaplanamadı, tüm değerler NaN")
            else:
                # Son RSI değerini logla
                last_rsi = df['rsi'].iloc[-1]
                logger.info(f"RSI hesaplandı. Son değer: {last_rsi:.2f}")
                
                # NaN değerleri kontrol et
                nan_count = df['rsi'].isnull().sum()
                if nan_count > 0:
                    logger.warning(f"RSI'da {nan_count} adet NaN değer var")
                
                # Aşırı alım/satım bölgelerini kontrol et
                if last_rsi < self.params['rsi_oversold']:
                    logger.info(f"RSI aşırı satım bölgesinde: {last_rsi:.2f} < {self.params['rsi_oversold']}")
                elif last_rsi > self.params['rsi_overbought']:
                    logger.info(f"RSI aşırı alım bölgesinde: {last_rsi:.2f} > {self.params['rsi_overbought']}")
            
            return df
            
        except Exception as e:
            logger.error(f"RSI hesaplanırken hata: {str(e)}", exc_info=True)
            df['rsi'] = np.nan
            return df
    
    def add_ema(self, df, period, column_name):
        """
        Exponential Moving Average (EMA) hesaplar
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            period (int): EMA periyodu
            column_name (str): Eklenecek sütun adı
            
        Returns:
            pandas.DataFrame: EMA eklenmiş DataFrame
        """
        try:
            df[column_name] = df['close'].ewm(span=period, adjust=False).mean()
            return df
            
        except Exception as e:
            logger.error(f"{column_name} hesaplanırken hata: {str(e)}", exc_info=True)
            df[column_name] = np.nan
            return df
    
    def add_macd(self, df, fast_period=12, slow_period=26, signal_period=9):
        """
        Moving Average Convergence Divergence (MACD) hesaplar
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            fast_period (int): Hızlı EMA periyodu
            slow_period (int): Yavaş EMA periyodu
            signal_period (int): Sinyal çizgisi periyodu
            
        Returns:
            pandas.DataFrame: MACD eklenmiş DataFrame
        """
        try:
            # Hızlı ve yavaş EMA'ları hesapla
            fast_ema = df['close'].ewm(span=fast_period, adjust=False).mean()
            slow_ema = df['close'].ewm(span=slow_period, adjust=False).mean()
            
            # MACD çizgisi
            df['macd'] = fast_ema - slow_ema
            
            # Sinyal çizgisi
            df['macd_signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
            
            # Histogram
            df['macd_hist'] = df['macd'] - df['macd_signal']
            
            return df
            
        except Exception as e:
            logger.error(f"MACD hesaplanırken hata: {str(e)}", exc_info=True)
            df['macd'] = np.nan
            df['macd_signal'] = np.nan
            df['macd_hist'] = np.nan
            return df
    
    def add_bollinger_bands(self, df, period=20, std_dev=2):
        """
        Bollinger Bantlarını hesaplar
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            period (int): Periyot
            std_dev (float): Standart sapma çarpanı
            
        Returns:
            pandas.DataFrame: Bollinger Bantları eklenmiş DataFrame
        """
        try:
            # Orta bant (SMA)
            df['bb_middle'] = df['close'].rolling(window=period).mean()
            
            # Standart sapma
            df['bb_std'] = df['close'].rolling(window=period).std()
            
            # Üst ve alt bantlar
            df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * std_dev)
            df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * std_dev)
            
            return df
            
        except Exception as e:
            logger.error(f"Bollinger Bantları hesaplanırken hata: {str(e)}", exc_info=True)
            df['bb_middle'] = np.nan
            df['bb_upper'] = np.nan
            df['bb_lower'] = np.nan
            return df
    
    def add_ichimoku(self, df, tenkan_period=9, kijun_period=26, senkou_span_b_period=52):
        """
        Ichimoku Bulutunu hesaplar
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            tenkan_period (int): Tenkan-sen periyodu
            kijun_period (int): Kijun-sen periyodu
            senkou_span_b_period (int): Senkou Span B periyodu
            
        Returns:
            pandas.DataFrame: Ichimoku Bulutu eklenmiş DataFrame
        """
        try:
            # Tenkan-sen (Conversion Line)
            tenkan_high = df['high'].rolling(window=tenkan_period).max()
            tenkan_low = df['low'].rolling(window=tenkan_period).min()
            df['ichimoku_tenkan'] = (tenkan_high + tenkan_low) / 2
            
            # Kijun-sen (Base Line)
            kijun_high = df['high'].rolling(window=kijun_period).max()
            kijun_low = df['low'].rolling(window=kijun_period).min()
            df['ichimoku_kijun'] = (kijun_high + kijun_low) / 2
            
            # Senkou Span A (Leading Span A)
            df['ichimoku_senkou_span_a'] = ((df['ichimoku_tenkan'] + df['ichimoku_kijun']) / 2).shift(kijun_period)
            
            # Senkou Span B (Leading Span B)
            senkou_high = df['high'].rolling(window=senkou_span_b_period).max()
            senkou_low = df['low'].rolling(window=senkou_span_b_period).min()
            df['ichimoku_senkou_span_b'] = ((senkou_high + senkou_low) / 2).shift(kijun_period)
            
            # Chikou Span (Lagging Span)
            df['ichimoku_chikou'] = df['close'].shift(-kijun_period)
            
            return df
            
        except Exception as e:
            logger.error(f"Ichimoku Bulutu hesaplanırken hata: {str(e)}", exc_info=True)
            df['ichimoku_tenkan'] = np.nan
            df['ichimoku_kijun'] = np.nan
            df['ichimoku_senkou_span_a'] = np.nan
            df['ichimoku_senkou_span_b'] = np.nan
            df['ichimoku_chikou'] = np.nan
            return df
    
    def add_parabolic_sar(self, df, af_start=0.02, af_increment=0.02, af_max=0.2):
        """
        Parabolic SAR hesaplar
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            af_start (float): Başlangıç hızlanma faktörü
            af_increment (float): Hızlanma faktörü artış miktarı
            af_max (float): Maksimum hızlanma faktörü
            
        Returns:
            pandas.DataFrame: Parabolic SAR eklenmiş DataFrame
        """
        try:
            # Kopya DataFrame oluştur
            df_copy = df.copy()
            
            # PSAR sütunu oluştur
            df_copy['psar'] = np.nan
            
            # İlk değerleri ayarla
            df_copy.loc[df_copy.index[1], 'psar'] = df_copy['low'].iloc[0]  # İlk PSAR değeri
            trend_up = True  # Başlangıç trendi (yukarı)
            ep = df_copy['high'].iloc[1]  # Extreme Point
            af = af_start  # Acceleration Factor
            
            # PSAR değerlerini hesapla
            for i in range(2, len(df_copy)):
                # Önceki PSAR değeri
                prev_psar = df_copy['psar'].iloc[i-1]
                
                # Trend yukarı ise
                if trend_up:
                    # PSAR hesapla
                    df_copy.loc[df_copy.index[i], 'psar'] = prev_psar + af * (ep - prev_psar)
                    
                    # PSAR değerini son iki mumun en düşük değerinden daha aşağıda tut
                    df_copy.loc[df_copy.index[i], 'psar'] = min(df_copy['psar'].iloc[i], df_copy['low'].iloc[i-1], df_copy['low'].iloc[i-2])
                    
                    # Yeni yüksek nokta kontrolü
                    if df_copy['high'].iloc[i] > ep:
                        ep = df_copy['high'].iloc[i]
                        af = min(af + af_increment, af_max)
                    
                    # Trend değişimi kontrolü
                    if df_copy['low'].iloc[i] < df_copy['psar'].iloc[i]:
                        trend_up = False
                        df_copy.loc[df_copy.index[i], 'psar'] = ep
                        ep = df_copy['low'].iloc[i]
                        af = af_start
                
                # Trend aşağı ise
                else:
                    # PSAR hesapla
                    df_copy.loc[df_copy.index[i], 'psar'] = prev_psar + af * (ep - prev_psar)
                    
                    # PSAR değerini son iki mumun en yüksek değerinden daha yukarıda tut
                    df_copy.loc[df_copy.index[i], 'psar'] = max(df_copy['psar'].iloc[i], df_copy['high'].iloc[i-1], df_copy['high'].iloc[i-2])
                    
                    # Yeni düşük nokta kontrolü
                    if df_copy['low'].iloc[i] < ep:
                        ep = df_copy['low'].iloc[i]
                        af = min(af + af_increment, af_max)
                    
                    # Trend değişimi kontrolü
                    if df_copy['high'].iloc[i] > df_copy['psar'].iloc[i]:
                        trend_up = True
                        df_copy.loc[df_copy.index[i], 'psar'] = ep
                        ep = df_copy['high'].iloc[i]
                        af = af_start
            
            # Hesaplanan PSAR değerlerini orijinal DataFrame'e ekle
            df['psar'] = df_copy['psar']
            
            return df
            
        except Exception as e:
            logger.error(f"Parabolic SAR hesaplanırken hata: {str(e)}", exc_info=True)
            df['psar'] = np.nan
            return df
    
    def add_adx(self, df, period=14):
        """
        Average Directional Index (ADX) hesaplar
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            period (int): ADX periyodu
            
        Returns:
            pandas.DataFrame: ADX eklenmiş DataFrame
        """
        try:
            # True Range hesapla
            df['tr1'] = abs(df['high'] - df['low'])
            df['tr2'] = abs(df['high'] - df['close'].shift(1))
            df['tr3'] = abs(df['low'] - df['close'].shift(1))
            df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
            
            # Directional Movement hesapla
            df['up_move'] = df['high'] - df['high'].shift(1)
            df['down_move'] = df['low'].shift(1) - df['low']
            
            # Positive Directional Movement (+DM)
            df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
            
            # Negative Directional Movement (-DM)
            df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)
            
            # Smoothed True Range, +DM, -DM
            df['atr'] = df['tr'].rolling(window=period).mean()
            df['plus_di'] = 100 * (df['plus_dm'].rolling(window=period).mean() / df['atr'])
            df['minus_di'] = 100 * (df['minus_dm'].rolling(window=period).mean() / df['atr'])
            
            # Directional Index (DX)
            df['dx'] = 100 * (abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']))
            
            # Average Directional Index (ADX)
            df['adx'] = df['dx'].rolling(window=period).mean()
            
            # Temizlik
            df.drop(['tr1', 'tr2', 'tr3', 'up_move', 'down_move'], axis=1, inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"ADX hesaplanırken hata: {str(e)}", exc_info=True)
            df['adx'] = np.nan
            df['plus_di'] = np.nan
            df['minus_di'] = np.nan
            return df
    
    def add_obv(self, df):
        """
        On-Balance Volume (OBV) hesaplar
        
        Args:
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            pandas.DataFrame: OBV eklenmiş DataFrame
        """
        try:
            # Yeni bir DataFrame oluştur
            result_df = df.copy()
            
            # OBV sütunu oluştur ve ilk değeri ayarla
            result_df['obv'] = pd.Series(dtype='float64')
            result_df.loc[result_df.index[0], 'obv'] = float(result_df['volume'].iloc[0])
            
            # OBV değerlerini hesapla
            for i in range(1, len(result_df)):
                if result_df['close'].iloc[i] > result_df['close'].iloc[i-1]:
                    # Fiyat yükseldi, hacmi ekle
                    result_df.loc[result_df.index[i], 'obv'] = result_df['obv'].iloc[i-1] + result_df['volume'].iloc[i]
                elif result_df['close'].iloc[i] < result_df['close'].iloc[i-1]:
                    # Fiyat düştü, hacmi çıkar
                    result_df.loc[result_df.index[i], 'obv'] = result_df['obv'].iloc[i-1] - result_df['volume'].iloc[i]
                else:
                    # Fiyat değişmedi, OBV aynı kalır
                    result_df.loc[result_df.index[i], 'obv'] = result_df['obv'].iloc[i-1]
            
            # Hesaplanan OBV değerlerini orijinal DataFrame'e ekle
            df['obv'] = result_df['obv']
            
            return df
            
        except Exception as e:
            logger.error(f"OBV hesaplanırken hata: {str(e)}", exc_info=True)
            df['obv'] = np.nan
            return df