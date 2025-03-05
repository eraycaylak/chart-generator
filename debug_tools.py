#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Debug Araçları Modülü
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("debug_tools")

class DebugTools:
    """Debug ve analiz araçları sınıfı"""
    
    def __init__(self, config):
        """Debug araçlarını başlatır"""
        self.config = config
        self.debug_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug')
        os.makedirs(self.debug_dir, exist_ok=True)
        logger.info("Debug araçları başlatıldı")
    
    def save_rsi_analysis(self, symbol, timeframe, df):
        """
        RSI analizi için debug grafiği oluşturur ve kaydeder
        
        Args:
            symbol (str): Kripto para sembolü
            timeframe (str): Zaman dilimi
            df (pandas.DataFrame): Fiyat ve RSI verileri
        """
        try:
            if 'rsi' not in df.columns or df['rsi'].isnull().all():
                logger.warning(f"{symbol} {timeframe} için RSI değerleri bulunamadı")
                return
            
            # Son 100 mumu al
            lookback = min(100, len(df))
            df_subset = df.iloc[-lookback:]
            
            # Grafik oluştur
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
            
            # Fiyat grafiği
            ax1.plot(df_subset.index, df_subset['close'], label='Kapanış Fiyatı')
            ax1.set_title(f"{symbol} - {timeframe} - Fiyat ve RSI Analizi")
            ax1.set_ylabel('Fiyat')
            ax1.grid(True)
            ax1.legend()
            
            # RSI grafiği
            ax2.plot(df_subset.index, df_subset['rsi'], color='purple', label='RSI')
            ax2.axhline(y=self.config.TA_PARAMS['rsi_overbought'], color='r', linestyle='--', label=f"Aşırı Alım ({self.config.TA_PARAMS['rsi_overbought']})")
            ax2.axhline(y=self.config.TA_PARAMS['rsi_oversold'], color='g', linestyle='--', label=f"Aşırı Satım ({self.config.TA_PARAMS['rsi_oversold']})")
            ax2.set_ylabel('RSI')
            ax2.set_ylim(0, 100)
            ax2.grid(True)
            ax2.legend()
            
            # Yerel minimum ve maksimumları bul
            price_lows = []
            price_highs = []
            rsi_lows = []
            rsi_highs = []
            
            for i in range(5, lookback - 5):
                # Yerel minimum (dip) kontrolü
                if (df_subset['low'].iloc[i-5:i].min() > df_subset['low'].iloc[i]) and (df_subset['low'].iloc[i+1:i+6].min() > df_subset['low'].iloc[i]):
                    price_lows.append((i, df_subset['low'].iloc[i]))
                    ax1.scatter(df_subset.index[i], df_subset['low'].iloc[i], color='green', marker='^', s=100)
                
                # Yerel maksimum (tepe) kontrolü
                if (df_subset['high'].iloc[i-5:i].max() < df_subset['high'].iloc[i]) and (df_subset['high'].iloc[i+1:i+6].max() < df_subset['high'].iloc[i]):
                    price_highs.append((i, df_subset['high'].iloc[i]))
                    ax1.scatter(df_subset.index[i], df_subset['high'].iloc[i], color='red', marker='v', s=100)
                
                # RSI yerel minimum kontrolü
                if (df_subset['rsi'].iloc[i-5:i].min() > df_subset['rsi'].iloc[i]) and (df_subset['rsi'].iloc[i+1:i+6].min() > df_subset['rsi'].iloc[i]):
                    rsi_lows.append((i, df_subset['rsi'].iloc[i]))
                    ax2.scatter(df_subset.index[i], df_subset['rsi'].iloc[i], color='green', marker='^', s=100)
                
                # RSI yerel maksimum kontrolü
                if (df_subset['rsi'].iloc[i-5:i].max() < df_subset['rsi'].iloc[i]) and (df_subset['rsi'].iloc[i+1:i+6].max() < df_subset['rsi'].iloc[i]):
                    rsi_highs.append((i, df_subset['rsi'].iloc[i]))
                    ax2.scatter(df_subset.index[i], df_subset['rsi'].iloc[i], color='red', marker='v', s=100)
            
            # Uyumsuzlukları kontrol et ve çiz
            if len(price_lows) >= 2 and len(rsi_lows) >= 2:
                # Son iki fiyat dibi
                last_price_lows = sorted(price_lows, key=lambda x: x[0], reverse=True)[:2]
                last_price_lows.sort(key=lambda x: x[0])  # Zaman sırasına göre sırala
                
                # Son iki RSI dibi
                last_rsi_lows = sorted(rsi_lows, key=lambda x: x[0], reverse=True)[:2]
                last_rsi_lows.sort(key=lambda x: x[0])  # Zaman sırasına göre sırala
                
                # Boğa uyumsuzluğu (Bullish Divergence) kontrolü
                # Fiyat düşük yaparken RSI yükseliyor
                if (last_price_lows[1][1] < last_price_lows[0][1]) and (last_rsi_lows[1][1] > last_rsi_lows[0][1]):
                    # Fiyat diplerini birleştir
                    ax1.plot([df_subset.index[last_price_lows[0][0]], df_subset.index[last_price_lows[1][0]]],
                             [last_price_lows[0][1], last_price_lows[1][1]], 'g--', linewidth=2)
                    
                    # RSI diplerini birleştir
                    ax2.plot([df_subset.index[last_rsi_lows[0][0]], df_subset.index[last_rsi_lows[1][0]]],
                             [last_rsi_lows[0][1], last_rsi_lows[1][1]], 'g--', linewidth=2)
                    
                    # Grafiğe not ekle
                    ax1.annotate('Bullish Divergence', 
                                xy=(df_subset.index[last_price_lows[1][0]], last_price_lows[1][1]),
                                xytext=(df_subset.index[last_price_lows[1][0]], last_price_lows[1][1]*1.05),
                                arrowprops=dict(facecolor='green', shrink=0.05),
                                color='green', fontsize=12)
            
            if len(price_highs) >= 2 and len(rsi_highs) >= 2:
                # Son iki fiyat tepesi
                last_price_highs = sorted(price_highs, key=lambda x: x[0], reverse=True)[:2]
                last_price_highs.sort(key=lambda x: x[0])  # Zaman sırasına göre sırala
                
                # Son iki RSI tepesi
                last_rsi_highs = sorted(rsi_highs, key=lambda x: x[0], reverse=True)[:2]
                last_rsi_highs.sort(key=lambda x: x[0])  # Zaman sırasına göre sırala
                
                # Ayı uyumsuzluğu (Bearish Divergence) kontrolü
                # Fiyat yüksek yaparken RSI düşüyor
                if (last_price_highs[1][1] > last_price_highs[0][1]) and (last_rsi_highs[1][1] < last_rsi_highs[0][1]):
                    # Fiyat tepelerini birleştir
                    ax1.plot([df_subset.index[last_price_highs[0][0]], df_subset.index[last_price_highs[1][0]]],
                             [last_price_highs[0][1], last_price_highs[1][1]], 'r--', linewidth=2)
                    
                    # RSI tepelerini birleştir
                    ax2.plot([df_subset.index[last_rsi_highs[0][0]], df_subset.index[last_rsi_highs[1][0]]],
                             [last_rsi_highs[0][1], last_rsi_highs[1][1]], 'r--', linewidth=2)
                    
                    # Grafiğe not ekle
                    ax1.annotate('Bearish Divergence', 
                                xy=(df_subset.index[last_price_highs[1][0]], last_price_highs[1][1]),
                                xytext=(df_subset.index[last_price_highs[1][0]], last_price_highs[1][1]*0.95),
                                arrowprops=dict(facecolor='red', shrink=0.05),
                                color='red', fontsize=12)
            
            # Grafiği kaydet
            plt.tight_layout()
            debug_file = os.path.join(self.debug_dir, f"{symbol}_{timeframe}_rsi_analysis.png")
            plt.savefig(debug_file, dpi=150)
            plt.close(fig)
            
            logger.info(f"RSI analiz grafiği kaydedildi: {debug_file}")
            
        except Exception as e:
            logger.error(f"RSI analiz grafiği oluşturulurken hata: {str(e)}", exc_info=True)
    
    def save_signal_summary(self, all_signals):
        """
        Tespit edilen tüm sinyallerin özetini kaydeder
        
        Args:
            all_signals (list): Tespit edilen tüm sinyaller listesi
        """
        try:
            if not all_signals:
                logger.warning("Kaydedilecek sinyal bulunamadı")
                return
            
            # Sinyalleri kalite puanına göre sırala
            all_signals.sort(key=lambda x: x['quality_score'], reverse=True)
            
            # Özet dosyası oluştur
            summary_file = os.path.join(self.debug_dir, "signal_summary.txt")
            
            with open(summary_file, 'w') as f:
                f.write("=== NAPOLYON CRYPTO SCANNER - SİNYAL ÖZETİ ===\n\n")
                f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Toplam Sinyal Sayısı: {len(all_signals)}\n\n")
                
                # Sinyal türlerine göre grupla
                signal_types = {}
                for signal in all_signals:
                    signal_type = signal['signal_type']
                    if signal_type not in signal_types:
                        signal_types[signal_type] = []
                    signal_types[signal_type].append(signal)
                
                # Her sinyal türü için özet
                f.write("=== SİNYAL TÜRLERİNE GÖRE DAĞILIM ===\n\n")
                for signal_type, signals in signal_types.items():
                    f.write(f"{signal_type}: {len(signals)} adet\n")
                
                # En iyi 20 sinyali listele
                f.write("\n=== EN İYİ 20 SİNYAL ===\n\n")
                for i, signal in enumerate(all_signals[:20]):
                    f.write(f"{i+1}. {signal['symbol']} - {signal['timeframe']} - {signal['signal_type']} - Kalite: {signal['quality_score']}/100\n")
                    f.write(f"   Açıklama: {signal['description']}\n")
                    f.write(f"   Giriş: {signal['entry']:.8g}, Stop Loss: {signal.get('stop_loss', 'N/A')}, Take Profit: {signal.get('take_profit', 'N/A')}\n\n")
            
            logger.info(f"Sinyal özeti kaydedildi: {summary_file}")
            
        except Exception as e:
            logger.error(f"Sinyal özeti kaydedilirken hata: {str(e)}", exc_info=True)