#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Ana Modül
"""
import time
import logging
import schedule
import json
import os
from datetime import datetime
from config import Config
from data_fetcher import BinanceDataFetcher
from signal_analyzer import SignalAnalyzer
from signal_sender import TelegramSender
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("main")

class KriptoMotoru:
    """Ana bot sınıfı - tüm işlemleri koordine eder"""
    
    def __init__(self):
        """Bot bileşenlerini başlatır"""
        self.config = Config()
        self.data_fetcher = BinanceDataFetcher(self.config)
        self.signal_analyzer = SignalAnalyzer(self.config)
        self.signal_sender = TelegramSender(self.config)
        
        # Gönderilen sinyalleri takip etmek için
        self.sent_signals_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sent_signals.json')
        self.sent_signals = self.load_sent_signals()
        
        # Veri dizinini oluştur
        os.makedirs(os.path.dirname(self.sent_signals_file), exist_ok=True)
        
        # Log dizinini oluştur
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logger.info("Kripto Motoru başlatıldı")
        logger.info(f"Takip edilen semboller: {', '.join(self.config.SYMBOLS)}")
        logger.info(f"Takip edilen zaman dilimleri: {', '.join(self.config.TIMEFRAMES)}")
        logger.info(f"Minimum sinyal kalitesi: {self.config.MIN_SIGNAL_QUALITY}")
        logger.info(f"Minimum hacim eşiği: {self.config.MIN_VOLUME_THRESHOLD} USDT")
    
    def load_sent_signals(self):
        """Gönderilen sinyalleri dosyadan yükler"""
        try:
            if os.path.exists(self.sent_signals_file):
                with open(self.sent_signals_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Gönderilen sinyaller yüklenirken hata: {str(e)}", exc_info=True)
            return {}
    
    def save_sent_signals(self):
        """Gönderilen sinyalleri dosyaya kaydeder"""
        try:
            with open(self.sent_signals_file, 'w') as f:
                json.dump(self.sent_signals, f)
            logger.info("Gönderilen sinyaller başarıyla kaydedildi")
        except Exception as e:
            logger.error(f"Gönderilen sinyaller kaydedilirken hata: {str(e)}", exc_info=True)
    
    def run_scan(self):
        """Tüm sembolleri tarar ve sinyalleri analiz eder"""
        try:
            logger.info("[SCAN] Tarama başlatılıyor...")
            
            all_signals = []  # Tüm zaman dilimleri için sinyalleri topla
            
            # Desteklenen tüm zaman dilimleri için tarama yap
            for timeframe in self.config.TIMEFRAMES:
                logger.info(f"[SCAN] {timeframe} zaman dilimi için tarama başlatılıyor")
                
                # Tüm sembolleri tara
                for symbol in self.config.SYMBOLS:
                    # Hacim kontrolü
                    if not self.check_volume_threshold(symbol):
                        logger.info(f"[X] {symbol} hacim eşiğinin altında, atlanıyor")
                        continue
                    
                    # Veri çek
                    df = self.data_fetcher.get_klines(symbol, timeframe)
                    if df is None or df.empty:
                        logger.warning(f"[X] {symbol} için veri alınamadı, atlanıyor")
                        continue
                    
                    # Sinyalleri analiz et
                    logger.info(f"[SCAN] {symbol} {timeframe} için sinyal analizi yapılıyor...")
                    signals = self.signal_analyzer.analyze(symbol, timeframe, df)
                    
                    if signals:
                        logger.info(f"[OK] {symbol} {timeframe} için {len(signals)} sinyal tespit edildi")
                        all_signals.extend(signals)
                    else:
                        logger.info(f"[X] {symbol} {timeframe} için sinyal tespit edilemedi")
                
                # API rate limit aşımını önlemek için kısa bir bekleme
                time.sleep(1)
            
            # Tüm sinyalleri kalite puanına göre sırala
            all_signals.sort(key=lambda x: x['quality_score'], reverse=True)
            
            logger.info(f"[OK] Toplam {len(all_signals)} sinyal tespit edildi")
            
            # Her sembol için en iyi sinyali seç
            best_signals_by_symbol = {}
            for signal in all_signals:
                symbol = signal['symbol']
                if symbol not in best_signals_by_symbol:
                    best_signals_by_symbol[symbol] = signal
            
            logger.info(f"[OK] {len(best_signals_by_symbol)} sembol için en iyi sinyaller seçildi")
            
            # Gönderilecek sinyalleri filtrele
            signals_to_send = []
            for symbol, signal in best_signals_by_symbol.items():
                # Sinyal kalitesini ve cooldown süresini kontrol et
                if self.should_send_signal(symbol, signal):
                    signals_to_send.append(signal)
            
            logger.info(f"[OK] Toplam {len(signals_to_send)} sinyal gönderilecek")
            
            # Sinyal türlerine göre dağılımı logla
            self.log_signal_distribution(signals_to_send)
            
            # Diğer tespit edilen sinyalleri de logla
            self.log_other_signals(all_signals, signals_to_send)
            
            # Sinyalleri 2 dakika arayla gönder
            self.send_signals_with_delay(signals_to_send, delay_seconds=120)
            
            # Gönderilen sinyalleri kaydet
            self.save_sent_signals()
            
            logger.info("[OK] Tarama tamamlandı")
            
        except Exception as e:
            logger.error(f"Tarama sırasında hata: {str(e)}", exc_info=True)
    
    def log_signal_distribution(self, signals):
        """Sinyal türlerine göre dağılımı loglar"""
        try:
            if not signals:
                return
                
            # Sinyal türlerine göre grupla
            signal_types = {}
            for signal in signals:
                signal_type = signal['signal_type']
                if signal_type not in signal_types:
                    signal_types[signal_type] = 0
                signal_types[signal_type] += 1
            
            # Sinyal türlerini logla
            logger.info("[STATS] Sinyal Türlerine Göre Dağılım:")
            for signal_type, count in signal_types.items():
                logger.info(f"   {signal_type}: {count} adet")
        
        except Exception as e:
            logger.error(f"Sinyal dağılımı loglanırken hata: {str(e)}", exc_info=True)
    
    def log_other_signals(self, all_signals, signals_to_send):
        """Gönderilmeyen diğer sinyalleri loglar"""
        try:
            # Gönderilecek sinyallerin sembol ve zaman dilimlerini al
            sent_symbol_timeframes = [(s['symbol'], s['timeframe']) for s in signals_to_send]
            
            # Gönderilmeyen sinyalleri filtrele
            other_signals = [s for s in all_signals if (s['symbol'], s['timeframe']) not in sent_symbol_timeframes]
            
            # Kalite puanına göre sırala
            other_signals.sort(key=lambda x: x['quality_score'], reverse=True)
            
            # En iyi 10 sinyali logla
            if other_signals:
                logger.info("[SCAN] Diğer Tespit Edilen Sinyaller:")
                for i, signal in enumerate(other_signals[:10]):
                    logger.info(f"   [{signal['symbol']}] {signal['signal_type']} ({signal['timeframe']}) - Kalite: {signal['quality_score']}/100")
        
        except Exception as e:
            logger.error(f"Diğer sinyaller loglanırken hata: {str(e)}", exc_info=True)
    
    def send_signals_with_delay(self, signals, delay_seconds=120):
        """Sinyalleri belirli bir gecikmeyle gönderir"""
        signals_sent = 0
        
        for signal in signals:
            symbol = signal['symbol']
            signal_type = signal['signal_type']
            
            # Sinyali gönder
            success = self.signal_sender.send_signal(signal)
            
            if success:
                signals_sent += 1
                self.update_sent_signals(symbol, signal)
                logger.info(f"[OK] {symbol} için {signal_type} sinyali başarıyla gönderildi")
            else:
                logger.error(f"[X] {symbol} için {signal_type} sinyali gönderilirken hata oluştu")
            
            # Son sinyal değilse bekle
            if signals_sent < len(signals):
                logger.info(f"[TIME] Bir sonraki sinyal için {delay_seconds} saniye bekleniyor...")
                time.sleep(delay_seconds)
        
        logger.info(f"[OK] Toplam {signals_sent} sinyal Telegram'a gönderildi")
    
    def check_volume_threshold(self, symbol):
        """Sembolün yeterli hacme sahip olup olmadığını kontrol eder"""
        try:
            volume_data = self.data_fetcher.get_24h_volume(symbol)
            is_above_threshold = volume_data >= self.config.MIN_VOLUME_THRESHOLD
            
            if is_above_threshold:
                logger.info(f"[OK] {symbol} hacim kontrolü başarılı: {volume_data:.2f} USDT")
            else:
                logger.info(f"[X] {symbol} hacim kontrolü başarısız: {volume_data:.2f} USDT < {self.config.MIN_VOLUME_THRESHOLD} USDT")
                
            return is_above_threshold
        except Exception as e:
            logger.error(f"[X] {symbol} için hacim kontrolü sırasında hata: {str(e)}")
            return False
    
    def should_send_signal(self, symbol, signal):
        """Sinyalin gönderilip gönderilmeyeceğini belirler (spam önleme)"""
        signal_type = signal['signal_type']
        current_time = time.time()
        
        # Sembol ve sinyal türü için son gönderim zamanını kontrol et
        key = f"{symbol}_{signal_type}"
        if key in self.sent_signals:
            last_sent_time = self.sent_signals[key]
            # Belirli süre içinde (config'de tanımlı) aynı sinyali tekrar gönderme
            if current_time - last_sent_time < self.config.SIGNAL_COOLDOWN:
                logger.info(f"[X] {symbol} için {signal_type} sinyali yakın zamanda gönderildi, atlanıyor")
                return False
        
        # Sinyal kalitesini kontrol et
        if signal['quality_score'] < self.config.MIN_SIGNAL_QUALITY:
            logger.info(f"[X] {symbol} için {signal_type} sinyali kalite eşiğinin altında ({signal['quality_score']}), atlanıyor")
            return False
            
        return True
    
    def update_sent_signals(self, symbol, signal):
        """Gönderilen sinyalleri günceller"""
        key = f"{symbol}_{signal['signal_type']}"
        self.sent_signals[key] = time.time()
    
    def schedule_tasks(self):
        """Zamanlanmış görevleri ayarlar"""
        # Her 90 dakikada bir tarama yap
        schedule.every(90).minutes.do(self.run_scan)
        
        logger.info("[TIME] Zamanlanmış görevler ayarlandı")
        
        # Zamanlanmış görevleri çalıştır
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("[STOP] Bot kullanıcı tarafından durduruldu")
                break
            except Exception as e:
                logger.error(f"[X] Beklenmeyen hata: {str(e)}", exc_info=True)
                time.sleep(60)  # Hata durumunda 1 dakika bekle ve tekrar dene

def main():
    """Ana fonksiyon"""
    try:
        logger.info("[START] Kripto Teknik Analiz Botu başlatılıyor...")
        bot = KriptoMotoru()
        # İlk taramayı hemen yap
        bot.run_scan()
        # Zamanlanmış görevleri başlat
        bot.schedule_tasks()
    except Exception as e:
        logger.critical(f"[X] Kritik hata: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()