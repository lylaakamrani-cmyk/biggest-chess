# © 2025 AmirAli Kamrani. All rights reserved.

# utils/config.py
import json
import os
import copy
from typing import Dict, Any, Optional
from datetime import datetime

class ConfigManager:
    """مدیریت تنظیمات برنامه"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.default_config = {
            'app': {
                'name': 'Chess Master Pro',
                'version': '1.0.0',
                'language': 'en',
                'dark_mode': False
            },
            'game': {
                'time_control': '10+0',
                'initial_time': 600,
                'increment': 0,
                'rated': True,
                'variant': 'standard',
                'allow_takeback': False,
                'allow_draw_offer': True,
                'allow_resign': True
            },
            'board': {
                'theme': 'classic',
                'piece_theme': 'classic',
                'show_legal_moves': True,
                'highlight_last_move': True,
                'animation_speed': 300,
                'flip_board': False,
                'show_coordinates': True
            },
            'sound': {
                'enabled': True,
                'volume': 70,
                'move_sound': True,
                'check_sound': True,
                'game_ended_sound': True
            },
            'ai': {
                'difficulty': 'medium',
                'depth': 4,
                'time_limit': 2.0,
                'use_stockfish': False
            },
            'network': {
                'server_url': 'ws://localhost:8765',
                'auto_connect': False,
                'reconnect_attempts': 3
            },
            'profile': {
                'username': '',
                'remember_me': False,
                'auto_login': False
            },
            'shop': {
                'show_owned': True,
                'sort_by': 'price'
            },
            'analytics': {
                'enabled': True,
                'send_usage_data': False
            }
        }
        
        self.config = {}
        self._load_config()
        
    def _load_config(self):
        """بارگذاری تنظیمات از فایل"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.config = self._merge_config(self.default_config, loaded)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = copy.deepcopy(self.default_config)
        else:
            self.config = copy.deepcopy(self.default_config)
            self._save_config()
            
    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """ادغام تنظیمات بارگذاری شده با پیش‌فرض"""
        result = copy.deepcopy(default)
        
        for key, value in loaded.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    result[key] = self._merge_config(result[key], value)
                else:
                    result[key] = value
                    
        return result
        
    def _save_config(self):
        """ذخیره تنظیمات در فایل"""
        try:
            # ایجاد پوشه اگر وجود نداشت
            os.makedirs(os.path.dirname(self.config_path) if os.path.dirname(self.config_path) else '.', exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """دریافت مقدار تنظیمات با کلید نقطه‌دار"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any):
        """تنظیم مقدار با کلید نقطه‌دار"""
        keys = key.split('.')
        config = self.config
        
        # رفتن به آخرین سطح
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # تنظیم مقدار
        config[keys[-1]] = value
        self._save_config()
        
    def get_all(self) -> Dict:
        """دریافت همه تنظیمات"""
        return copy.deepcopy(self.config)
        
    def reset_to_default(self):
        """بازنشانی به تنظیمات پیش‌فرض"""
        self.config = copy.deepcopy(self.default_config)
        self._save_config()
        
    def export_config(self, path: str):
        """خروجی گرفتن از تنظیمات"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
            
    def import_config(self, path: str) -> bool:
        """وارد کردن تنظیمات از فایل"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                self.config = self._merge_config(self.config, loaded)
                self._save_config()
                return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False
            
    def get_game_config(self) -> Dict:
        """دریافت تنظیمات بازی"""
        return self.get('game')
        
    def get_board_config(self) -> Dict:
        """دریافت تنظیمات صفحه"""
        return self.get('board')
        
    def get_sound_config(self) -> Dict:
        """دریافت تنظیمات صدا"""
        return self.get('sound')
        
    def get_ai_config(self) -> Dict:
        """دریافت تنظیمات هوش مصنوعی"""
        return self.get('ai')