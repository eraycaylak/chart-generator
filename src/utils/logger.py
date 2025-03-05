#!/usr/bin/env python3
"""
Kripto Teknik Analiz Botu - Loglama Modülü
"""
import os
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Belirtilen isimde bir logger oluşturur
    
    Args:
        name (str): Logger adı
        log_file (str, optional): Log dosyası yolu. Belirtilmezse varsayılan dosya kullanılır.
        level (int, optional): Log seviyesi. Varsayılan INFO.
        
    Returns:
        logging.Logger: Oluşturulan logger
    """
    # Log dizinini oluştur
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Log dosyasını belirle
    if log_file is None:
        log_file = os.path.join(log_dir, f"{name}.log")
    else:
        log_file = os.path.join(log_dir, log_file)
    
    # Logger oluştur
    logger = logging.getLogger(name)
    
    # Eğer logger zaten yapılandırılmışsa, mevcut logger'ı döndür
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Dosya handler'ı - UTF-8 encoding ile
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'  # UTF-8 encoding kullan
    )
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Konsol handler'ı - Emoji'leri kaldıran özel formatter ile
    console_handler = logging.StreamHandler(sys.stdout)  # stdout kullan
    console_formatter = EmojiSafeFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Handler'ları logger'a ekle
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class EmojiSafeFormatter(logging.Formatter):
    """Emoji karakterlerini güvenli karakterlerle değiştiren formatter"""
    
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
        # Emoji yerine kullanılacak karakterler
        self.replacements = {
            '✅': '[OK]',
            '❌': '[X]',
            '🔍': '[SCAN]',
            '📊': '[STATS]',
            '⏱️': '[TIME]',
            '🚀': '[START]',
            '⛔': '[STOP]',
            '🔄': '[REFRESH]'
        }
    
    def format(self, record):
        # Önce standart formatlamayı yap
        formatted_message = super().format(record)
        
        # Emoji'leri değiştir
        for emoji, replacement in self.replacements.items():
            formatted_message = formatted_message.replace(emoji, replacement)
        
        return formatted_message