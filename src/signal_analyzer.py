#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Sinyal Analiz Modülü
"""
import numpy as np
import pandas as pd
from technical_indicators import TechnicalIndicators
from support_resistance import SupportResistance
from utils.logger import setup_logger

# Sinyal modüllerini içe aktar
from signals.rsi_signals import RSISignals
from signals.moving_average_signals import MovingAverageSignals
from signals.macd_signals import MACDSignals
from signals.bollinger_signals import BollingerSignals
from signals.pattern_signals import PatternSignals
from signals.ichimoku_signals import IchimokuSignals
from signals.support_resistance_signals import SupportResistanceSignals
from signals.fibonacci_signals import FibonacciSignals
from signals.volatility_signals import VolatilitySignals
from signals.trend_signals import TrendSignals

# Logger kurulumu
logger = setup_logger("signal_analyzer")

class SignalAnalyzer:
    """Teknik analiz sinyallerini tespit eden sınıf"""
    
    def __init__(self, config):
        """Sinyal analizörünü başlatır"""
        self.config = config
        self.indicators = TechnicalIndicators(config)
        self.support_resistance = SupportResistance(config)
        
        # Sinyal modüllerini başlat
        self.signal_modules = [
            RSISignals(config),
            MovingAverageSignals(config),
            MACDSignals(config),
            BollingerSignals(config),
            PatternSignals(config),
            IchimokuSignals(config),
            SupportResistanceSignals(config),
            FibonacciSignals(config),
            VolatilitySignals(config),
            TrendSignals(config)
        ]
        
        logger.info("Sinyal analizörü başlatıldı")
    
    def analyze(self, symbol, timeframe, df):
        """
        Verilen veri için tüm sinyal türlerini analiz eder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat verileri
            
        Returns:
            list: Tespit edilen sinyaller listesi
        """
        try:
            logger.info(f"{symbol} için {timeframe} zaman diliminde sinyal analizi başlatılıyor")
            
            # Teknik indikatörleri hesapla
            df = self.indicators.add_all_indicators(df)
            
            # Tüm sinyal modüllerini çalıştır ve sinyalleri topla
            all_signals = []
            pattern_signals = []
            
            for module in self.signal_modules:
                signals = module.check_signals(symbol, timeframe, df)
                
                # Mum formasyonu sinyallerini ayır
                for signal in signals:
                    if "Pattern:" in signal['signal_type'] or signal.get('is_pattern', False):
                        pattern_signals.append(signal)
                    else:
                        all_signals.append(signal)
            
            # Eğer hiç normal sinyal yoksa ve sadece mum formasyonu sinyalleri varsa
            if not all_signals and pattern_signals:
                # En iyi mum formasyonu sinyalini seç
                pattern_signals.sort(key=lambda x: x['quality_score'], reverse=True)
                best_pattern = pattern_signals[0]
                
                # Yeni bir sinyal oluştur (mum formasyonu değil)
                fallback_signal = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': 'Technical Analysis Alert',
                    'entry': best_pattern.get('entry'),
                    'stop_loss': best_pattern.get('stop_loss'),
                    'take_profit': best_pattern.get('take_profit'),
                    'timestamp': df.index[-1],
                    'quality_score': best_pattern['quality_score'],
                    'description': f"Teknik analiz uyarısı: {best_pattern['description']}"
                }
                all_signals.append(fallback_signal)
            
            # Sinyalleri kalite puanına göre sırala
            all_signals.sort(key=lambda x: x['quality_score'], reverse=True)
            
            # Her sembol ve zaman dilimi için sadece en iyi sinyali seç
            best_signals = self.filter_best_signals(all_signals)
            
            # En iyi sinyale diğer sinyalleri ve mum formasyonlarını ekle
            for signal in best_signals:
                # Aynı sembol ve timeframe için diğer sinyalleri bul
                other_signals = [s for s in all_signals if s['symbol'] == signal['symbol'] and 
                                s['timeframe'] == signal['timeframe'] and 
                                s['signal_type'] != signal['signal_type']]
                
                # Mum formasyonu sinyallerini ekle
                matching_patterns = [p for p in pattern_signals if p['symbol'] == signal['symbol'] and 
                                    p['timeframe'] == signal['timeframe']]
                
                # Diğer sinyalleri kalite puanına göre sırala
                other_signals.sort(key=lambda x: x['quality_score'], reverse=True)
                matching_patterns.sort(key=lambda x: x['quality_score'], reverse=True)
                
                # En iyi 3 alternatif sinyali ekle
                signal['alternative_signals'] = other_signals[:3]
                
                # Mum formasyonu sinyallerini alternative_signals'a ekle
                for pattern in matching_patterns[:2]:  # En iyi 2 mum formasyonu
                    if pattern not in signal['alternative_signals']:
                        signal['alternative_signals'].append(pattern)
                
                # Destek ve direnç seviyelerini ekle
                levels = self.support_resistance.find_levels(df)
                signal['support_levels'] = levels['support']
                signal['resistance_levels'] = levels['resistance']
                
                # ADX trend bilgisini ekle
                if 'adx' in df.columns and not pd.isna(df['adx'].iloc[-1]):
                    adx_value = df['adx'].iloc[-1]
                    plus_di = df['plus_di'].iloc[-1] if 'plus_di' in df.columns else 0
                    minus_di = df['minus_di'].iloc[-1] if 'minus_di' in df.columns else 0
                    
                    # Trend yönü ve gücü
                    trend_direction = "Bullish" if plus_di > minus_di else "Bearish"
                    
                    if adx_value < 20:
                        trend_strength = "Weak"
                    elif adx_value < 25:
                        trend_strength = "Moderate"
                    elif adx_value < 40:
                        trend_strength = "Strong"
                    else:
                        trend_strength = "Very Strong"
                    
                    # ADX trend bilgisini ekle
                    signal['adx_trend'] = {
                        'value': adx_value,
                        'direction': trend_direction,
                        'strength': trend_strength
                    }
                    
                    # ADX trend sinyalini alternative_signals'a ekle
                    adx_signal = {
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal_type': f"{trend_strength} {trend_direction} Trend (ADX: {adx_value:.1f})",
                        'quality_score': min(80, int(adx_value)),
                        'description': f"ADX {adx_value:.1f} değeri ile {trend_strength.lower()} bir {trend_direction.lower()} trend gösteriyor."
                    }
                    
                    # ADX sinyalini alternative_signals'ın başına ekle
                    if adx_signal not in signal['alternative_signals']:
                        signal['alternative_signals'] = [adx_signal] + signal['alternative_signals']
            
            logger.info(f"{symbol} için {timeframe} zaman diliminde {len(all_signals)} sinyal tespit edildi, en iyi {len(best_signals)} sinyal seçildi")
            
            return best_signals
            
        except Exception as e:
            logger.error(f"Sinyal analizi sırasında hata: {str(e)}", exc_info=True)
            return []
    
    def filter_best_signals(self, signals):
        """
        Her sembol için en iyi sinyali filtreler
        
        Args:
            signals (list): Tüm sinyaller listesi
            
        Returns:
            list: Filtrelenmiş en iyi sinyaller listesi
        """
        if not signals:
            return []
        
        # Sembol bazında grupla
        symbol_groups = {}
        for signal in signals:
            symbol = signal['symbol']
            if symbol not in symbol_groups:
                symbol_groups[symbol] = []
            symbol_groups[symbol].append(signal)
        
        # Her sembol için en iyi sinyali seç
        best_signals = []
        for symbol, symbol_signals in symbol_groups.items():
            # Kalite puanına göre sırala
            symbol_signals.sort(key=lambda x: x['quality_score'], reverse=True)
            
            # Mum formasyonu sinyallerini filtrele
            non_pattern_signals = [s for s in symbol_signals if "Pattern:" not in s['signal_type'] and not s.get('is_pattern', False)]
            
            # Eğer mum formasyonu olmayan sinyal varsa, onu seç
            if non_pattern_signals:
                best_signals.append(non_pattern_signals[0])
            else:
                # Yoksa en iyi sinyali seç
                best_signals.append(symbol_signals[0])
        
        return best_signals