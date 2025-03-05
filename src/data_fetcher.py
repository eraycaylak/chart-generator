#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Veri Çekme Modülü
"""
import time
import logging
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("data_fetcher")

class BinanceDataFetcher:
    """Binance API'den veri çeken sınıf"""
    
    def __init__(self, config):
        """Binance API istemcisini başlatır"""
        self.config = config
        self.client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
        self.last_request_time = 0
        logger.info("Binance veri çekici başlatıldı")
    
    def _respect_rate_limit(self):
        """API rate limit aşımını önlemek için bekleme yapar"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.config.API_RATE_LIMIT_WAIT:
            wait_time = self.config.API_RATE_LIMIT_WAIT - elapsed
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def get_klines(self, symbol, timeframe, limit=500):
        """
        Belirtilen sembol ve zaman dilimi için mum verilerini çeker
        
        Args:
            symbol (str): Kripto para sembolü (örn. BTCUSDT)
            timeframe (str): Zaman dilimi (örn. 15m, 1h, 4h, 1d)
            limit (int): Çekilecek mum sayısı
            
        Returns:
            pandas.DataFrame: Mum verileri
        """
        try:
            self._respect_rate_limit()
            
            logger.info(f"{symbol} için {timeframe} zaman diliminde veri çekiliyor")
            
            # Binance API'den veri çek
            klines = self.client.get_klines(
                symbol=symbol,
                interval=timeframe,
                limit=limit
            )
            
            # Veriyi DataFrame'e dönüştür
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Veri tiplerini dönüştür
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            # Timestamp'i index olarak ayarla
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"{symbol} için {len(df)} adet mum verisi alındı")
            
            return df
            
        except BinanceAPIException as e:
            logger.error(f"Binance API hatası: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Veri çekerken beklenmeyen hata: {str(e)}", exc_info=True)
            return None
    
    def get_24h_volume(self, symbol):
        """
        Sembolün 24 saatlik hacmini çeker
        
        Args:
            symbol (str): Kripto para sembolü (örn. BTCUSDT)
            
        Returns:
            float: 24 saatlik hacim (USDT cinsinden)
        """
        try:
            self._respect_rate_limit()
            
            ticker = self.client.get_ticker(symbol=symbol)
            volume = float(ticker['quoteVolume'])
            
            logger.info(f"{symbol} için 24 saatlik hacim: {volume} USDT")
            
            return volume
            
        except BinanceAPIException as e:
            logger.error(f"Binance API hatası: {str(e)}")
            return 0
        except Exception as e:
            logger.error(f"Hacim verisi çekerken beklenmeyen hata: {str(e)}", exc_info=True)
            return 0