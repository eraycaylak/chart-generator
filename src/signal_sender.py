#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Sinyal Gönderme Modülü
"""
import os
import time
import requests
from chart_generator import ChartGenerator
from utils.logger import setup_logger

# Logger kurulumu
logger = setup_logger("signal_sender")

class TelegramSender:
    """Telegram üzerinden sinyal gönderen sınıf"""
    
    def __init__(self, config):
        """Telegram API ayarlarını başlatır"""
        self.config = config
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chart_chat_id = config.TELEGRAM_CHAT_ID  # Grafik ve teknik analiz için kanal
        self.signals_chat_id = config.TELEGRAM_SIGNALS_CHAT_ID  # Sadece işlem sinyalleri için kanal
        self.chart_generator = ChartGenerator(config)
        
        # API anahtarlarını kontrol et
        if not self.bot_token or not self.chart_chat_id:
            logger.warning("Telegram API anahtarları eksik! .env dosyasını kontrol edin.")
            logger.warning("Bot token: " + ("Ayarlanmış" if self.bot_token else "Eksik"))
            logger.warning("Chart Chat ID: " + ("Ayarlanmış" if self.chart_chat_id else "Eksik"))
            logger.warning("Signals Chat ID: " + ("Ayarlanmış" if self.signals_chat_id else "Eksik"))
            
            # Örnek değerler göster
            logger.warning("Örnek .env dosyası:")
            logger.warning("TELEGRAM_BOT_TOKEN=123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ")
            logger.warning("TELEGRAM_CHAT_ID=-1002113698544")
            logger.warning("TELEGRAM_SIGNALS_CHAT_ID=-1002443145235")
        else:
            logger.info("Telegram sinyal gönderici başlatıldı")
            # API bağlantısını test et
            self._test_connection()
    
    def _test_connection(self):
        """Telegram API bağlantısını test eder"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get("ok"):
                    bot_name = bot_info["result"].get("first_name")
                    bot_username = bot_info["result"].get("username")
                    logger.info(f"Telegram bot bağlantısı başarılı: {bot_name} (@{bot_username})")
                    
                    # Chat ID'leri test et
                    self._test_chat_id(self.chart_chat_id, "Grafik kanalı")
                    if self.signals_chat_id:
                        self._test_chat_id(self.signals_chat_id, "Sinyal kanalı")
                else:
                    logger.error(f"Bot bilgileri alınamadı: {bot_info}")
            else:
                logger.error(f"Telegram API bağlantı hatası: {response.text}")
        except Exception as e:
            logger.error(f"Telegram bağlantı testi sırasında hata: {str(e)}", exc_info=True)
    
    def _test_chat_id(self, chat_id, chat_name):
        """Chat ID'nin geçerliliğini test eder"""
        try:
            if not chat_id:
                logger.warning(f"{chat_name} ID'si tanımlanmamış, atlanıyor.")
                return
                
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": f"🔄 NAPOLYON CRYPTO SCANNER {chat_name} bağlantı testi başarılı! Bot aktif ve çalışıyor.",
                "parse_mode": "HTML",
                "disable_notification": True
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logger.info(f"{chat_name} bağlantısı başarılı: {chat_id}")
            else:
                error_data = response.json()
                logger.error(f"{chat_name} ID hatası: {error_data.get('description', 'Bilinmeyen hata')}")
                
                if "chat not found" in response.text.lower():
                    logger.error(f"{chat_name} ID bulunamadı. Lütfen şunları kontrol edin:")
                    logger.error("1. Bot, hedef kanala/gruba eklenmiş mi?")
                    logger.error("2. Kanal/grup için doğru ID kullanılıyor mu?")
                    logger.error("3. Kanal ID'si için @ işareti kullanılıyor mu? (örn: @kanal_adi)")
                    logger.error("4. Grup ID'si için - işareti ile başlıyor mu? (örn: -1001234567890)")
        except Exception as e:
            logger.error(f"{chat_name} ID testi sırasında hata: {str(e)}", exc_info=True)
    
    def send_signal(self, signal):
        """
        Sinyali Telegram kanallarına gönderir
        
        Args:
            signal (dict): Gönderilecek sinyal bilgileri
            
        Returns:
            bool: Gönderim başarılı mı?
        """
        try:
            # API anahtarlarını kontrol et
            if not self.bot_token or not self.chart_chat_id:
                logger.error("Telegram API anahtarları eksik! Sinyal gönderilemiyor.")
                return False
                
            symbol = signal['symbol']
            timeframe = signal['timeframe']
            signal_type = signal['signal_type']
            
            logger.info(f"{symbol} için {signal_type} sinyali gönderiliyor")
            
            # Grafik oluştur
            chart_path = self.chart_generator.generate_chart(signal)
            
            if not chart_path or not os.path.exists(chart_path):
                logger.error(f"Grafik oluşturulamadı: {chart_path}")
                # Grafik olmadan mesajı gönder
                chart_message = self._format_chart_message(signal)
                signals_message = self._format_signals_message(signal)
                
                chart_success = self._send_text_message(chart_message, self.chart_chat_id)
                signals_success = True
                
                if self.signals_chat_id:
                    signals_success = self._send_text_message(signals_message, self.signals_chat_id)
                
                return chart_success and signals_success
            
            # Mesajları hazırla
            chart_message = self._format_chart_message(signal)
            signals_message = self._format_signals_message(signal)
            
            # Fotoğraf ve mesajı birlikte gönder
            chart_success = self._send_photo_with_caption(chart_path, chart_message, self.chart_chat_id)
            
            # Sinyal kanalına işlem detaylarını gönder (eğer ikinci kanal tanımlanmışsa)
            signals_success = True
            if self.signals_chat_id:
                signals_success = self._send_text_message(signals_message, self.signals_chat_id)
            
            # Geçici grafik dosyasını temizle
            try:
                os.remove(chart_path)
            except Exception as e:
                logger.warning(f"Geçici grafik dosyası temizlenirken hata: {str(e)}")
            
            return chart_success and signals_success
            
        except Exception as e:
            logger.error(f"Sinyal gönderilirken hata: {str(e)}", exc_info=True)
            return False
    
    def _format_chart_message(self, signal):
        """
        Grafik kanalı için sinyal mesajını formatlar (teknik analiz bilgileri)
        
        Args:
            signal (dict): Sinyal bilgileri
            
        Returns:
            str: Formatlanmış mesaj
        """
        try:
            symbol = signal['symbol']
            timeframe = signal['timeframe']
            signal_type = signal['signal_type']
            quality_score = signal.get('quality_score', 0)
            description = signal.get('description', '')
            
            # Destek ve direnç seviyelerini al
            support_levels = signal.get('support_levels', [])
            resistance_levels = signal.get('resistance_levels', [])
            
            # Alternatif sinyalleri al
            alternative_signals = signal.get('alternative_signals', [])
            
            # Ana sinyal başlığı
            message = f"⚠️ <b>[{symbol}] {signal_type} ({timeframe})</b>\n"
            
            # Kalite puanı
            if quality_score > 0:
                message += f"⭐️ Kalite: {quality_score}/100\n"
            
            # Açıklama - ADX ve Trend bilgilerini içermiyorsa ekle
            if description and not any(keyword in description for keyword in ["ADX", "trend gösteriyor", "Trend takibi"]):
                message += f"\n<b>📝 {description}</b>\n"
            
            # Alternatif sinyalleri öncelik sırasına göre sırala
            if alternative_signals:
                # Öncelikli sinyal türleri
                priority_signals = []
                secondary_signals = []
                other_signals = []
                pattern_signals = []
                adx_signals = []
                
                for alt_signal in alternative_signals:
                    signal_name = alt_signal['signal_type']
                    
                    # ADX ve Trend sinyallerini her zaman adx_signals'a ekle
                    if "ADX" in signal_name or "Trend" in signal_name or "Güçlü" in signal_name:
                        # İngilizce ADX sinyallerini Türkçe'ye çevir
                        if "Strong Bullish Trend" in signal_name:
                            alt_signal['signal_type'] = signal_name.replace("Strong Bullish Trend", "Güçlü Yükselen Trend")
                        elif "Strong Bearish Trend" in signal_name:
                            alt_signal['signal_type'] = signal_name.replace("Strong Bearish Trend", "Güçlü Düşen Trend")
                        elif "Very Strong Bullish Trend" in signal_name:
                            alt_signal['signal_type'] = signal_name.replace("Very Strong Bullish Trend", "Çok Güçlü Yükselen Trend")
                        elif "Very Strong Bearish Trend" in signal_name:
                            alt_signal['signal_type'] = signal_name.replace("Very Strong Bearish Trend", "Çok Güçlü Düşen Trend")
                        elif "Weak Bullish Trend" in signal_name:
                            alt_signal['signal_type'] = signal_name.replace("Weak Bullish Trend", "Zayıf Yükselen Trend")
                        elif "Weak Bearish Trend" in signal_name:
                            alt_signal['signal_type'] = signal_name.replace("Weak Bearish Trend", "Zayıf Düşen Trend")
                        elif "Moderate Bullish Trend" in signal_name:
                            alt_signal['signal_type'] = signal_name.replace("Moderate Bullish Trend", "Orta Yükselen Trend")
                        elif "Moderate Bearish Trend" in signal_name:
                            alt_signal['signal_type'] = signal_name.replace("Moderate Bearish Trend", "Orta Düşen Trend")
                            
                        adx_signals.append(alt_signal)
                    # Mum formasyonlarını pattern_signals'a ekle
                    elif "Pattern:" in signal_name or alt_signal.get('is_pattern', False):
                        pattern_signals.append(alt_signal)
                    # Fibonacci, Divergence sinyallerini önceliklendir
                    elif any(keyword in signal_name for keyword in ["Fibonacci", "Divergence"]):
                        priority_signals.append(alt_signal)
                    # Support/Resistance sinyallerini ikincil önceliklendir
                    elif any(keyword in signal_name for keyword in ["Support", "Resistance", "Destek", "Direnç"]):
                        secondary_signals.append(alt_signal)
                    # Diğer sinyaller
                    else:
                        other_signals.append(alt_signal)
                
                # Öncelikli sinyalleri kalite puanına göre sırala
                priority_signals.sort(key=lambda x: x['quality_score'], reverse=True)
                secondary_signals.sort(key=lambda x: x['quality_score'], reverse=True)
                other_signals.sort(key=lambda x: x['quality_score'], reverse=True)
                pattern_signals.sort(key=lambda x: x['quality_score'], reverse=True)
                adx_signals.sort(key=lambda x: x['quality_score'], reverse=True)
                
                # Tüm sinyalleri birleştir (öncelikli olanlar önce)
                sorted_signals = priority_signals + secondary_signals + other_signals
                
                # ADX sinyallerini her zaman en üstte göster
                if adx_signals:
                    message += "\n🔍 <b>Trend Bilgisi:</b>\n"
                    for adx_signal in adx_signals[:1]:  # Sadece en iyi ADX sinyalini göster
                        message += f"• {adx_signal['signal_type']}\n"
                
                # Diğer sinyalleri göster
                if sorted_signals or pattern_signals:
                    message += "\n🔍 <b>Diğer Tespit Edilen Sinyaller:</b>\n"
                    
                    # Önce normal sinyalleri göster
                    for alt_signal in sorted_signals[:3]:  # En iyi 3 sinyali göster
                        message += f"• {alt_signal['signal_type']}\n"
                    
                    # Sonra mum formasyonlarını göster
                    for pattern_signal in pattern_signals[:2]:  # En iyi 2 mum formasyonunu göster
                        message += f"• {pattern_signal['signal_type']}\n"
            
            # Destek ve direnç seviyeleri - yan yana formatla
            if support_levels:
                support_text = "🟢 <b>Destek Seviyeleri:</b> "
                for i, level in enumerate(support_levels[:3]):  # En fazla 3 seviye göster
                    if i > 0:
                        support_text += " • "
                    support_text += f"{level:.8g}"
                message += f"\n{support_text}\n"
            
            if resistance_levels:
                resistance_text = "🔴 <b>Direnç Seviyeleri:</b> "
                for i, level in enumerate(resistance_levels[:3]):  # En fazla 3 seviye göster
                    if i > 0:
                        resistance_text += " • "
                    resistance_text += f"{level:.8g}"
                message += f"{resistance_text}\n"
            
            # Not
            message += "\n⚠️ Bu bir sinyal botu tarafından otomatik olarak oluşturulan sinyaldir. Kendi araştırmanızı yapın ve riski yönetin."
            
            return message
            
        except Exception as e:
            logger.error(f"Grafik mesajı formatlanırken hata: {str(e)}", exc_info=True)
            return f"NAPOLYON CRYPTO SCANNER: {signal['symbol']} - {signal['signal_type']}"
    
    def _format_signals_message(self, signal):
        """
        Sinyal kanalı için mesajı formatlar (işlem detayları)
        
        Args:
            signal (dict): Sinyal bilgileri
            
        Returns:
            str: Formatlanmış mesaj
        """
        try:
            symbol = signal['symbol']
            timeframe = signal['timeframe']
            signal_type = signal['signal_type']
            entry = signal.get('entry')
            stop_loss = signal.get('stop_loss')
            take_profit = signal.get('take_profit')
            quality_score = signal.get('quality_score', 0)
            
            # İşlem kanalı için daha basit format
            message = f"⚠️ {symbol} - {signal_type} ({timeframe})\n"
            
            # Entry, Stop Loss ve Take Profit bilgileri
            if entry is not None:
                message += f"🎯 Entry: {entry:.8g}\n"
            
            if stop_loss is not None:
                message += f"🛑 Stop Loss: {stop_loss:.8g}\n"
            
            if take_profit is not None:
                # Take Profit değerini hesapla - Entry'den %1.5 uzaklıkta
                if "Bullish" in signal_type or not any(keyword in signal_type for keyword in ["Bearish", "Resistance", "Overbought"]):
                    # Alış sinyali - TP yukarıda
                    take_profit = entry * 1.015  # %1.5 yukarıda
                else:
                    # Satış sinyali - TP aşağıda
                    take_profit = entry * 0.985  # %1.5 aşağıda
                
                message += f"💰 Take Profit: {take_profit:.8g}\n"
            
            # Risk/Ödül oranını hesapla
            if entry is not None and stop_loss is not None and take_profit is not None:
                risk = abs(entry - stop_loss)
                reward = abs(take_profit - entry)
                if risk > 0:
                    rr_ratio = reward / risk
                    message += f"📊 Risk/Ödül: 1:{rr_ratio:.2f}\n"
            
            # Kalite puanı
            if quality_score > 0:
                message += f"⭐️ Kalite: {quality_score}/100\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Sinyal mesajı formatlanırken hata: {str(e)}", exc_info=True)
            return f"NAPOLYON CRYPTO SCANNER: {signal['symbol']} - {signal['signal_type']}"
    
    def _send_text_message(self, message, chat_id):
        """
        Metin mesajı gönderir
        
        Args:
            message (str): Gönderilecek mesaj
            chat_id (str): Hedef chat ID
            
        Returns:
            bool: Gönderim başarılı mı?
        """
        try:
            if not chat_id:
                logger.warning("Chat ID tanımlanmamış, mesaj gönderilemiyor.")
                return False
                
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"  # Markdown yerine HTML kullan
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logger.info(f"Metin mesajı başarıyla gönderildi: {chat_id}")
                return True
            else:
                logger.error(f"Metin mesajı gönderilirken hata: { response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Metin mesajı gönderilirken hata: {str(e)}", exc_info=True)
            return False
    
    def _send_photo_with_caption(self, photo_path, caption, chat_id):
        """
        Fotoğraf ve açıklamayı birlikte gönderir
        
        Args:
            photo_path (str): Fotoğraf dosyasının yolu
            caption (str): Fotoğraf açıklaması
            chat_id (str): Hedef chat ID
            
        Returns:
            bool: Gönderim başarılı mı?
        """
        try:
            if not chat_id:
                logger.warning("Chat ID tanımlanmamış, fotoğraf gönderilemiyor.")
                return False
            
            # Telegram API'nin caption uzunluk sınırı (1024 karakter)
            max_caption_length = 1024
            
            # HTML etiketlerini temizle
            clean_caption = caption
            
            # Eğer açıklama çok uzunsa, kısalt
            if len(clean_caption) > max_caption_length:
                # Kısaltılmış açıklama
                short_caption = clean_caption[:max_caption_length-50] + "...\n(Devamı için bir sonraki mesaja bakın)"
                
                # Fotoğrafı kısaltılmış açıklamayla gönder
                url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
                
                with open(photo_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {
                        "chat_id": chat_id,
                        "caption": short_caption,
                        "parse_mode": "HTML"
                    }
                    
                    response = requests.post(url, data=data, files=files)
                
                if response.status_code == 200:
                    logger.info(f"Fotoğraf mesajı başarıyla gönderildi: {chat_id}")
                    
                    # Kalan açıklamayı ayrı bir metin mesajı olarak gönder
                    remaining_text = clean_caption[max_caption_length-50:]
                    self._send_text_message(remaining_text, chat_id)
                    
                    return True
                else:
                    logger.error(f"Fotoğraf mesajı gönderilirken hata: {response.text}")
                    return False
            else:
                # Açıklama kısa ise, doğrudan gönder
                url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
                
                with open(photo_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {
                        "chat_id": chat_id,
                        "caption": clean_caption,
                        "parse_mode": "HTML"
                    }
                    
                    response = requests.post(url, data=data, files=files)
                
                if response.status_code == 200:
                    logger.info(f"Fotoğraf ve açıklama başarıyla gönderildi: {chat_id}")
                    return True
                else:
                    logger.error(f"Fotoğraf ve açıklama gönderilirken hata: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Fotoğraf ve açıklama gönderilirken hata: {str(e)}", exc_info=True)
            return False