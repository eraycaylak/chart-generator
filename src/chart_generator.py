#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Grafik Oluşturma Modülü
"""
import os
import tempfile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import numpy as np
import pandas as pd
from utils.logger import setup_logger
import matplotlib.image as mpimg

# Logger kurulumu
logger = setup_logger("chart_generator")

class ChartGenerator:
    """Teknik analiz grafikleri oluşturan sınıf"""
    
    def __init__(self, config):
        """Grafik oluşturma parametrelerini ayarlar"""
        self.config = config
        self.chart_settings = config.CHART_SETTINGS
        logger.info("Grafik oluşturucu başlatıldı")
    
    def generate_chart(self, signal):
        """
        Sinyal için teknik analiz grafiği oluşturur
        
        Args:
            signal (dict): Sinyal bilgileri
            
        Returns:
            str: Oluşturulan grafik dosyasının yolu
        """
        try:
            # Geçici dosya oluştur
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            chart_path = temp_file.name
            temp_file.close()
            
            # Veri çekici oluştur
            from data_fetcher import BinanceDataFetcher
            data_fetcher = BinanceDataFetcher(self.config)
            
            # Sinyal bilgilerini al
            symbol = signal['symbol']
            timeframe = signal['timeframe']
            signal_type = signal['signal_type']
            
            # Veri çek - daha fazla mum için limit artırıldı
            df = data_fetcher.get_klines(symbol, timeframe, limit=400)
            
            if df is None or df.empty:
                logger.error(f"Grafik için veri alınamadı: {symbol} {timeframe}")
                return None
            
            # Teknik indikatörleri hesapla
            from technical_indicators import TechnicalIndicators
            indicators = TechnicalIndicators(self.config)
            df = indicators.add_all_indicators(df)
            
            # Destek ve direnç seviyelerini hesapla
            from support_resistance import SupportResistance
            sr = SupportResistance(self.config)
            levels = sr.find_levels(df)
            
            # Grafik ayarları
            fig_width = self.chart_settings['chart_width']
            fig_height = self.chart_settings['chart_height']
            dpi = self.chart_settings['dpi']
            
            # Gösterilecek mum sayısını ayarla
            display_count = min(self.chart_settings['candle_count'], len(df))
            df_display = df.iloc[-display_count:]
            
            # Açık tema için grafik stilini ayarla
            mc = mpf.make_marketcolors(
                up='black', down='black',  # Yükseliş ve düşüş rengi: Siyah
                wick={'up':'black', 'down':'black'},
                edge={'up':'black', 'down':'black'},
                volume={'up':'#26a69a', 'down':'#ef5350'},
                ohlc='black'
            )
            
            # MPF stil ayarları - alpha parametresi yok, sadece geçerli parametreleri kullan
            s = mpf.make_mpf_style(
                marketcolors=mc,
                gridstyle='-',
                gridcolor='#d1d4dc',  # Klavuz çizgileri rengi
                y_on_right=True,
                facecolor='#d1d4dc',  # Arkaplan rengi: #d1d4dc
                edgecolor='#d1d4dc',
                figcolor='#d1d4dc',
                rc={'axes.labelcolor': 'black', 'axes.edgecolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black'}
            )
            
            # Panel sayısını belirle
            panel_count = 1  # Ana grafik her zaman var
            
            # Sinyal türüne göre ek panelleri belirle
            show_rsi = "RSI" in signal_type or "Oversold" in signal_type or "Overbought" in signal_type or "Divergence" in signal_type
            show_macd = "MACD" in signal_type
            show_adx = "ADX" in signal_type or "Trend" in signal_type
            show_ichimoku = "Ichimoku" in signal_type
            
            # Öncelikli göstergeleri belirle
            is_fibonacci_signal = "Fibonacci" in signal_type
            is_divergence_signal = "Divergence" in signal_type
            is_support_resistance_signal = "Support" in signal_type or "Resistance" in signal_type
            is_trend_signal = "Trend" in signal_type or "ADX" in signal_type
            is_ichimoku_signal = "Ichimoku" in signal_type
            
            # Öncelikli sinyaller için her zaman ilgili göstergeleri göster
            if is_fibonacci_signal or is_divergence_signal:
                show_ema = True
                show_rsi = True
            else:
                show_ema = self.chart_settings.get('show_ema', False)
            
            # Panel oranlarını ayarla - volume=True olduğunda panel sayısı +1 olur
            if show_rsi and show_macd and show_adx:
                panel_ratios = (6, 1, 2, 2, 2)  # Ana grafik, Volume, RSI, MACD, ADX
                panel_count = 5
            elif show_rsi and show_macd:
                panel_ratios = (6, 1, 2, 2)  # Ana grafik, Volume, RSI, MACD
                panel_count = 4
            elif show_rsi and show_adx:
                panel_ratios = (6, 1, 2, 2)  # Ana grafik, Volume, RSI, ADX
                panel_count = 4
            elif show_macd and show_adx:
                panel_ratios = (6, 1, 2, 2)  # Ana grafik, Volume, MACD, ADX
                panel_count = 4
            elif show_rsi:
                panel_ratios = (6, 1, 2)  # Ana grafik, Volume, RSI
                panel_count = 3
            elif show_macd:
                panel_ratios = (6, 1, 2)  # Ana grafik, Volume, MACD
                panel_count = 3
            elif show_adx:
                panel_ratios = (6, 1, 2)  # Ana grafik, Volume, ADX
                panel_count = 3
            else:
                panel_ratios = (6, 1)  # Ana grafik, Volume
                panel_count = 2
            
            # Ek göstergeleri ayarla
            apds = []
            
            # EMA'ları sadece gerektiğinde ekle
            if "EMA" in signal_type or "Moving Average" in signal_type or "Trend" in signal_type or show_ema:
                ema_short = mpf.make_addplot(df_display['ema_short'], color='#4fc3f7', width=1, label=f"EMA{self.config.TA_PARAMS['ema_short']}")
                ema_medium = mpf.make_addplot(df_display['ema_medium'], color='#ffb74d', width=1, label=f"EMA{self.config.TA_PARAMS['ema_medium']}")
                ema_long = mpf.make_addplot(df_display['ema_long'], color='#ce93d8', width=1, label=f"EMA{self.config.TA_PARAMS['ema_long']}")
                apds.extend([ema_short, ema_medium, ema_long])
            
            # Parabolic SAR ekle
            if "Parabolic" in signal_type or "SAR" in signal_type:
                psar = mpf.make_addplot(df_display['psar'], type='scatter', markersize=50, marker='.', color='#757575')
                apds.append(psar)
            
            # Ichimoku Cloud bileşenlerini ekle
            if is_ichimoku_signal or show_ichimoku:
                # Tenkan-sen ve Kijun-sen
                tenkan = mpf.make_addplot(df_display['ichimoku_tenkan'], color='#f44336', width=1, label='Tenkan-sen')
                kijun = mpf.make_addplot(df_display['ichimoku_kijun'], color='#2196f3', width=1, label='Kijun-sen')
                
                # Senkou Span A ve B (Bulut)
                senkou_a = mpf.make_addplot(df_display['ichimoku_senkou_span_a'], color='#4caf50', width=0.8, alpha=0.3)
                senkou_b = mpf.make_addplot(df_display['ichimoku_senkou_span_b'], color='#ff9800', width=0.8, alpha=0.3)
                
                # Chikou Span (Lagging Span)
                chikou = mpf.make_addplot(df_display['ichimoku_chikou'], color='#9c27b0', width=1, alpha=0.5)
                
                apds.extend([tenkan, kijun, senkou_a, senkou_b, chikou])
            
            # RSI paneli
            if show_rsi:
                rsi_panel = 2  # Volume panelinden sonra
                rsi = mpf.make_addplot(df_display['rsi'], panel=rsi_panel, color='#f48fb1', ylabel='RSI')
                rsi_overbought = mpf.make_addplot([self.config.TA_PARAMS['rsi_overbought']] * len(df_display), panel=rsi_panel, color='#757575', linestyle='--')
                rsi_oversold = mpf.make_addplot([self.config.TA_PARAMS['rsi_oversold']] * len(df_display), panel=rsi_panel, color='#757575', linestyle='--')
                apds.extend([rsi, rsi_overbought, rsi_oversold])
                
                # RSI Divergence çizgisi
                if "Divergence" in signal_type:
                    # Son 30 mumu kontrol et
                    lookback = min(30, len(df_display))
                    
                    if "Bearish" in signal_type:
                        # Fiyat yüksek yaparken RSI düşüyor - kırmızı çizgi
                        divergence_line = np.array([np.nan] * len(df_display))
                        divergence_line[-lookback] = df_display['rsi'].iloc[-lookback]
                        divergence_line[-1] = df_display['rsi'].iloc[-1]
                        
                        rsi_div_line = mpf.make_addplot(divergence_line, panel=rsi_panel, color='#ef5350', linestyle='-')
                        apds.append(rsi_div_line)
                    
                    elif "Bullish" in signal_type:
                        # Fiyat düşük yaparken RSI yükseliyor - yeşil çizgi
                        divergence_line = np.array([np.nan] * len(df_display))
                        divergence_line[-lookback] = df_display['rsi'].iloc[-lookback]
                        divergence_line[-1] = df_display['rsi'].iloc[-1]
                        
                        rsi_div_line = mpf.make_addplot(divergence_line, panel=rsi_panel, color='#26a69a', linestyle='-')
                        apds.append(rsi_div_line)
            
            # MACD paneli
            if show_macd:
                macd_panel = 3 if show_rsi else 2  # RSI panelinden sonra veya Volume panelinden sonra
                macd = mpf.make_addplot(df_display['macd'], panel=macd_panel, color='#4fc3f7', ylabel='MACD')
                macd_signal = mpf.make_addplot(df_display['macd_signal'], panel=macd_panel, color='#f48fb1')
                
                # MACD histogramı için pozitif ve negatif değerleri ayır
                macd_hist_pos = df_display['macd_hist'].copy()
                macd_hist_pos[macd_hist_pos <= 0] = np.nan
                macd_hist_neg = df_display['macd_hist'].copy()
                macd_hist_neg[macd_hist_neg > 0] = np.nan
                
                macd_hist_pos_plot = mpf.make_addplot(macd_hist_pos, panel=macd_panel, type='bar', color='#26a69a', alpha=0.6)
                macd_hist_neg_plot = mpf.make_addplot(macd_hist_neg, panel=macd_panel, type='bar', color='#ef5350', alpha=0.6)
                
                apds.extend([macd, macd_signal, macd_hist_pos_plot, macd_hist_neg_plot])
            
            # ADX paneli
            if show_adx:
                adx_panel = panel_count - 1  # Son panel
                adx = mpf.make_addplot(df_display['adx'], panel=adx_panel, color='#9c27b0', ylabel='ADX')
                plus_di = mpf.make_addplot(df_display['plus_di'], panel=adx_panel, color='#26a69a')
                minus_di = mpf.make_addplot(df_display['minus_di'], panel=adx_panel, color='#ef5350')
                
                # ADX eşik çizgileri
                adx_strong = mpf.make_addplot([25] * len(df_display), panel=adx_panel, color='#757575', linestyle='--')
                adx_very_strong = mpf.make_addplot([40] * len(df_display), panel=adx_panel, color='#757575', linestyle=':')
                
                apds.extend([adx, plus_di, minus_di, adx_strong, adx_very_strong])
            
            # Bollinger Bantları
            if "Bollinger" in signal_type:
                # Bollinger Bantları ekle
                bb_upper = mpf.make_addplot(df_display['bb_upper'], color='#ef5350', width=0.8, alpha=0.7)
                bb_middle = mpf.make_addplot(df_display['bb_middle'], color='#757575', width=0.8, alpha=0.7)
                bb_lower = mpf.make_addplot(df_display['bb_lower'], color='#26a69a', width=0.8, alpha=0.7)
                apds.extend([bb_upper, bb_middle, bb_lower])
            
            # Fibonacci seviyeleri hesapla
            fib_levels = {}
            if "Fibonacci" in signal_type or "fib" in signal_type.lower():
                # Son 100 mumda yüksek ve düşük noktaları bul
                high_point = df['high'].iloc[-100:].max()
                low_point = df['low'].iloc[-100:].min()
                
                # Fibonacci seviyeleri - sadece istenen seviyeleri göster
                fib_levels = {
                    0: high_point,
                    0.5: high_point - 0.5 * (high_point - low_point),
                    0.618: high_point - 0.618 * (high_point - low_point),
                    0.786: high_point - 0.786 * (high_point - low_point),
                    1: low_point
                }
                
                # Sinyal türünden Fibonacci seviyesini çıkar
                highlight_level = None
                for level_str in ["0.5", "0.618", "0.786"]:
                    if level_str in signal_type:
                        highlight_level = float(level_str)
                        break
                
                if highlight_level is None:
                    highlight_level = 0.618  # Varsayılan
            
            # Grafik başlığı
            title = f"NAPOLYON CRYPTO SCANNER"
            subtitle = f"{symbol} - {timeframe} - {signal_type}"
            
            # Grafik oluştur - İçi boş mumlar için type='hollow_and_filled'
            fig, axes = mpf.plot(
                df_display,
                type='hollow_and_filled',  # İçi boş mumlar
                style=s,
                figsize=(fig_width, fig_height),
                volume=True,
                panel_ratios=panel_ratios,
                addplot=apds,
                returnfig=True,
                tight_layout=True
            )
            
            # Ana grafik alanını al
            ax1 = axes[0]
            
            # Destek ve direnç seviyelerini ekle - daha temiz görünüm için
            if is_support_resistance_signal or True:  # Her zaman göster, ancak sinyal türüne göre vurgula
                # Mevcut fiyat aralığını belirle
                price_range = df_display['high'].max() - df_display['low'].min()
                current_price = df_display['close'].iloc[-1]
                
                # Destek seviyeleri - yeşil
                # Fiyata yakın olan destek seviyelerini filtrele
                relevant_supports = [level for level in levels['support'] 
                                    if level < current_price and 
                                    current_price - level < price_range * 0.5]
                
                # En yakın 4 destek seviyesini göster
                relevant_supports.sort(reverse=True)  # Fiyata en yakın olanlar önce
                for i, level in enumerate(relevant_supports[:4]):
                    # Destek/Direnç sinyali ise daha kalın çizgi kullan
                    linewidth = 2 if is_support_resistance_signal else 1
                    alpha = 0.9 if is_support_resistance_signal else 0.7
                    
                    ax1.axhline(y=level, color='#26a69a', linestyle='-', alpha=alpha, linewidth=linewidth)
                    ax1.text(0.02, level, f'Support: {level:.8g}', transform=ax1.get_yaxis_transform(), 
                            color='#26a69a', fontsize=8, ha='left', va='center', 
                            bbox=dict(facecolor='#d1d4dc', alpha=0.7, edgecolor='none', pad=1))
                
                # Direnç seviyeleri - kırmızı
                # Fiyata yakın olan direnç seviyelerini filtrele
                relevant_resistances = [level for level in levels['resistance'] 
                                       if level > current_price and 
                                       level - current_price < price_range * 0.5]
                
                # En yakın 4 direnç seviyesini göster
                relevant_resistances.sort()  # Fiyata en yakın olanlar önce
                for i, level in enumerate(relevant_resistances[:4]):
                    # Destek/Direnç sinyali ise daha kalın çizgi kullan
                    linewidth = 2 if is_support_resistance_signal else 1
                    alpha = 0.9 if is_support_resistance_signal else 0.7
                    
                    ax1.axhline(y=level, color='#ef5350', linestyle='-', alpha=alpha, linewidth=linewidth)
                    ax1.text(0.02, level, f'Resistance: {level:.8g}', transform=ax1.get_yaxis_transform(), 
                            color='#ef5350', fontsize=8, ha='left', va='center',
                            bbox=dict(facecolor='#d1d4dc', alpha=0.7, edgecolor='none', pad=1))
            
            # Fibonacci seviyelerini ekle - daha temiz görünüm için
            if fib_levels:
                # Sadece istenen Fibonacci seviyelerini göster
                important_levels = [0, 0.5, 0.618, 0.786, 1]
                for level in important_levels:
                    price = fib_levels.get(level)
                    if price is None:
                        continue
                        
                    if level == 0 or level == 1:
                        color = '#757575'
                        alpha = 0.8
                        linewidth = 1
                    elif level == highlight_level:
                        color = '#ffb74d'  # Vurgulanan seviye - turuncu
                        alpha = 1.0
                        linewidth = 1.5
                    else:
                        color = '#757575'
                        alpha = 0.6
                        linewidth = 1
                    
                    ax1.axhline(y=price, color=color, linestyle='--', alpha=alpha, linewidth=linewidth)
                    # Seviye etiketini ekle - daha temiz görünüm
                    ax1.text(0.98, price, f'Fib {level}', transform=ax1.get_yaxis_transform(), 
                             color=color, fontsize=8, ha='right', va='center',
                             bbox=dict(facecolor='#d1d4dc', alpha=0.7, edgecolor='none', pad=1))
            
            # Grafik açıklamasını ekle
            if show_ema or is_ichimoku_signal:
                ax1.legend(loc='upper left', fontsize=9)
            
            # Başlık ve alt başlık ekle
            plt.suptitle(title, fontsize=16, color='black', y=0.98)
            plt.figtext(0.5, 0.92, subtitle, fontsize=12, color='black', ha='center')
            
            # Grafik alanını optimize et - boşlukları azalt
            plt.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.05, hspace=0.1)
            
            # Logo watermark ekle
            try:
                logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.png')
                if os.path.exists(logo_path):
                    logo = mpimg.imread(logo_path)
                    # Figürün ortasına logoyu yerleştir
                    fig_center = fig.add_axes([0.3, 0.3, 0.4, 0.4], zorder=-1)
                    fig_center.imshow(logo, alpha=self.chart_settings['watermark_alpha'])
                    fig_center.axis('off')  # Eksen çizgilerini gizle
                    logger.info(f"Logo başarıyla eklendi: {logo_path}")
                else:
                    logger.warning(f"Logo dosyası bulunamadı: {logo_path}")
                    # Alternatif watermark ekle
                    fig.text(
                        0.5, 0.5,
                        "NAPOLYON",
                        fontsize=40,
                        color='#757575',
                        alpha=self.chart_settings['watermark_alpha'],
                        ha='center',
                        va='center',
                        rotation=30
                    )
            except Exception as e:
                logger.error(f"Logo eklenirken hata: {str(e)}", exc_info=True)
                # Alternatif watermark ekle
                fig.text(
                    0.5, 0.5,
                    "NAPOLYON",
                    fontsize=40,
                    color='#757575',
                    alpha=self.chart_settings['watermark_alpha'],
                    ha='center',
                    va='center',
                    rotation=30
                )
            
            # Grafiği kaydet
            plt.savefig(chart_path, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Grafik başarıyla oluşturuldu: {chart_path}")
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Grafik oluşturulurken hata: {str(e)}", exc_info=True)
            return None