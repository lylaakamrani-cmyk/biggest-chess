# © 2025 AmirAli Kamrani. All rights reserved.

# utils/logger.py
import logging
import os
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any, List  # ← مهم

class Logger:
    """سیستم لاگ‌گیری پیشرفته"""
    
    def __init__(self, log_path: str = "logs", name: str = "chess_master"):
        self.log_path = log_path
        self.name = name
        self.logger = None
        self.log_level = logging.INFO
        self._setup_logger()
        
    def _setup_logger(self):
        """راه‌اندازی لاگر"""
        os.makedirs(self.log_path, exist_ok=True)
        
        # نام فایل لاگ بر اساس تاریخ
        log_file = os.path.join(self.log_path, f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log")
        
        # پیکربندی لاگر
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)
        
        # هندلر فایل
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        
        # هندلر کنسول
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # فرمت
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def debug(self, message: str, data: Dict = None):
        """لاگ سطح Debug"""
        self._log(logging.DEBUG, message, data)
        
    def info(self, message: str, data: Dict = None):
        """لاگ سطح Info"""
        self._log(logging.INFO, message, data)
        
    def warning(self, message: str, data: Dict = None):
        """لاگ سطح Warning"""
        self._log(logging.WARNING, message, data)
        
    def error(self, message: str, data: Dict = None):
        """لاگ سطح Error"""
        self._log(logging.ERROR, message, data)
        
    def critical(self, message: str, data: Dict = None):
        """لاگ سطح Critical"""
        self._log(logging.CRITICAL, message, data)
        
    def _log(self, level: int, message: str, data: Dict = None):
        """لاگ کردن با داده‌های اضافی"""
        if data:
            message = f"{message} - {json.dumps(data, ensure_ascii=False)}"
        self.logger.log(level, message)
        
    def log_game_event(self, event_type: str, data: Dict):
        """ثبت رویداد بازی"""
        self.info(f"Game Event: {event_type}", data)
        
    def log_error(self, error: Exception, context: Dict = None):
        """ثبت خطا"""
        self.error(f"Error: {str(error)}", {'type': type(error).__name__, 'context': context})
        
    def log_user_action(self, user_id: int, action: str, details: Dict = None):
        """ثبت اقدام کاربر"""
        self.info(f"User {user_id}: {action}", details)
        
    def get_logs(self, lines: int = 100) -> List[str]:
        """دریافت لاگ‌های اخیر"""
        log_file = os.path.join(self.log_path, f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log")
        
        if not os.path.exists(log_file):
            return []
            
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = f.readlines()
            return logs[-lines:]
            
    def clear_logs(self):
        """پاک کردن لاگ‌ها"""
        log_file = os.path.join(self.log_path, f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log")
        if os.path.exists(log_file):
            os.remove(log_file)
            
    def get_log_stats(self) -> Dict:
        """آمار لاگ‌ها"""
        stats = {
            'total_entries': 0,
            'by_level': {},
            'by_date': {},
            'file_size': 0
        }
        
        log_file = os.path.join(self.log_path, f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log")
        
        if os.path.exists(log_file):
            stats['file_size'] = os.path.getsize(log_file)
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    stats['total_entries'] += 1
                    
                    # استخراج سطح لاگ
                    if ' - DEBUG - ' in line:
                        stats['by_level']['debug'] = stats['by_level'].get('debug', 0) + 1
                    elif ' - INFO - ' in line:
                        stats['by_level']['info'] = stats['by_level'].get('info', 0) + 1
                    elif ' - WARNING - ' in line:
                        stats['by_level']['warning'] = stats['by_level'].get('warning', 0) + 1
                    elif ' - ERROR - ' in line:
                        stats['by_level']['error'] = stats['by_level'].get('error', 0) + 1
                    elif ' - CRITICAL - ' in line:
                        stats['by_level']['critical'] = stats['by_level'].get('critical', 0) + 1
                        
        return stats