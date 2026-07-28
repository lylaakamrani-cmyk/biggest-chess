# © 2025 AmirAli Kamrani. All rights reserved.

# utils/assets.py
import os
import json
import shutil
import base64
from typing import Dict, List, Optional, Any
from PIL import Image, ImageDraw, ImageFont
import hashlib

class AssetManager:
    """مدیریت Assets بازی"""
    
    def __init__(self, assets_path: str = "assets"):
        self.assets_path = assets_path
        self.cache = {}
        self.loaded_assets = {}
        
        # مسیرهای زیرپوشه‌ها
        self.paths = {
            'images': os.path.join(assets_path, 'images'),
            'sounds': os.path.join(assets_path, 'sounds'),
            'themes': os.path.join(assets_path, 'themes'),
            'fonts': os.path.join(assets_path, 'fonts'),
            'stockfish': os.path.join(assets_path, 'stockfish')
        }
        
        # ایجاد پوشه‌ها
        self._create_directories()
        
    def _create_directories(self):
        """ایجاد پوشه‌های مورد نیاز"""
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)
            
        # پوشه‌های فرعی تصاویر
        image_subdirs = ['pieces/white', 'pieces/black', 'backgrounds', 'icons']
        for subdir in image_subdirs:
            os.makedirs(os.path.join(self.paths['images'], subdir), exist_ok=True)
            
    def get_piece_path(self, piece_type: str, color: str, format: str = 'png') -> str:
        """دریافت مسیر مهره"""
        filename = f"{piece_type}.{format}"
        return os.path.join(self.paths['images'], 'pieces', color, filename)
        
    def get_theme_path(self, theme_name: str) -> str:
        """دریافت مسیر تم"""
        return os.path.join(self.paths['themes'], f"{theme_name}.json")
        
    def get_sound_path(self, sound_name: str) -> str:
        """دریافت مسیر صدا"""
        return os.path.join(self.paths['sounds'], f"{sound_name}.wav")
        
    def get_font_path(self, font_name: str) -> str:
        """دریافت مسیر فونت"""
        return os.path.join(self.paths['fonts'], font_name)
        
    def load_theme(self, theme_name: str) -> Dict:
        """بارگذاری تم"""
        theme_path = self.get_theme_path(theme_name)
        
        if theme_name in self.cache:
            return self.cache[theme_name]
            
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                theme = json.load(f)
                self.cache[theme_name] = theme
                return theme
        except Exception as e:
            print(f"Error loading theme {theme_name}: {e}")
            return self._get_default_theme()
            
    def _get_default_theme(self) -> Dict:
        """تم پیش‌فرض"""
        return {
            'name': 'Classic',
            'colors': {
                'light': '#F0D9B5',
                'dark': '#B58863',
                'highlight': '#FFFF00',
                'last_move': '#CDD26A',
                'legal_move': '#7B8B3E',
                'check': '#FF0000'
            },
            'pieces': {
                'style': 'classic',
                'size': 60
            },
            'background': {
                'color': '#000000',
                'image': None
            }
        }
        
    def load_font(self, font_name: str, size: int) -> Optional[object]:
        """بارگذاری فونت"""
        font_path = self.get_font_path(font_name)
        
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
            else:
                # فونت پیش‌فرض
                return ImageFont.load_default()
        except Exception as e:
            print(f"Error loading font: {e}")
            return ImageFont.load_default()
            
    def create_default_assets(self):
        """ایجاد Assets پیش‌فرض"""
        self._create_default_pieces()
        self._create_default_themes()
        self._create_default_icons()
        self._create_default_sounds()
        
    def _create_default_pieces(self):
        """ایجاد مهره‌های پیش‌فرض (با PIL)"""
        pieces = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']
        colors = ['white', 'black']
        
        for color in colors:
            for piece in pieces:
                path = self.get_piece_path(piece, color)
                if not os.path.exists(path):
                    self._create_piece_image(piece, color, path)
                    
    def _create_piece_image(self, piece: str, color: str, path: str):
        """ساخت تصویر مهره (ساده)"""
        size = 60
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # رنگ مهره
        fill_color = (255, 255, 255, 255) if color == 'white' else (0, 0, 0, 255)
        
        # رسم مهره (ساده)
        center = size // 2
        radius = size // 3
        
        # دایره
        draw.ellipse([center - radius, center - radius, center + radius, center + radius], 
                     outline=fill_color, width=2)
        
        # حرف مهره
        symbols = {
            'king': '♔',
            'queen': '♕',
            'rook': '♖',
            'bishop': '♗',
            'knight': '♘',
            'pawn': '♙'
        }
        
        try:
            font = ImageFont.truetype("/system/fonts/NotoSansSymbols-Regular.ttf", 30)
        except:
            font = ImageFont.load_default()
            
        draw.text((center - 15, center - 15), symbols.get(piece, '?'), 
                  fill=fill_color, font=font)
                  
        img.save(path)
        
    def _create_default_themes(self):
        """ایجاد تم‌های پیش‌فرض"""
        themes = {
            'classic': {
                'name': 'Classic',
                'colors': {
                    'light': '#F0D9B5',
                    'dark': '#B58863',
                    'highlight': '#FFFF00',
                    'last_move': '#CDD26A',
                    'legal_move': '#7B8B3E',
                    'check': '#FF0000'
                }
            },
            'dark': {
                'name': 'Dark',
                'colors': {
                    'light': '#779952',
                    'dark': '#446633',
                    'highlight': '#FFD700',
                    'last_move': '#88AA55',
                    'legal_move': '#55AA88',
                    'check': '#FF3333'
                }
            },
            'neon': {
                'name': 'Neon',
                'colors': {
                    'light': '#00FFAA',
                    'dark': '#003322',
                    'highlight': '#FF00FF',
                    'last_move': '#00FFFF',
                    'legal_move': '#FFFF00',
                    'check': '#FF0000'
                }
            },
            'blue': {
                'name': 'Blue',
                'colors': {
                    'light': '#4A90D9',
                    'dark': '#2C5F8A',
                    'highlight': '#FFD700',
                    'last_move': '#6BA3E0',
                    'legal_move': '#3A7BD5',
                    'check': '#FF0000'
                }
            },
            'green': {
                'name': 'Green',
                'colors': {
                    'light': '#90EE90',
                    'dark': '#228B22',
                    'highlight': '#FFD700',
                    'last_move': '#7CCD7C',
                    'legal_move': '#32CD32',
                    'check': '#FF0000'
                }
            }
        }
        
        for name, theme in themes.items():
            path = self.get_theme_path(name)
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(theme, f, indent=2, ensure_ascii=False)
                    
    def _create_default_icons(self):
        """ایجاد آیکون‌های پیش‌فرض"""
        icons = ['settings', 'profile', 'friends', 'shop', 'logo', 'home']
        for icon in icons:
            path = os.path.join(self.paths['images'], 'icons', f"{icon}.png")
            if not os.path.exists(path):
                self._create_icon(icon, path)
                
    def _create_icon(self, name: str, path: str):
        """ساخت آیکون ساده"""
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # مربع با گوشه‌های گرد
        draw.rounded_rectangle([5, 5, size-5, size-5], radius=10, 
                              fill=(100, 100, 100, 200))
        
        # متن
        try:
            font = ImageFont.truetype("/system/fonts/NotoSans-Regular.ttf", 20)
        except:
            font = ImageFont.load_default()
            
        draw.text((size//2 - 15, size//2 - 10), name[:2].upper(), 
                  fill=(255, 255, 255, 255), font=font)
                  
        img.save(path)
        
    def _create_default_sounds(self):
        """ایجاد فایل‌های صوتی پیش‌فرض (فایل‌های خالی)"""
        sounds = ['move', 'check', 'win', 'lose', 'draw', 'start', 'notification']
        for sound in sounds:
            path = self.get_sound_path(sound)
            if not os.path.exists(path):
                # ایجاد فایل خالی WAV (ساده)
                with open(path, 'wb') as f:
                    # هدر WAV ساده
                    f.write(b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
                    
    def get_asset_hash(self, asset_path: str) -> str:
        """محاسبه هش یک Asset"""
        if os.path.exists(asset_path):
            with open(asset_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        return ''
        
    def verify_assets(self) -> Dict[str, bool]:
        """بررسی وجود Assets"""
        results = {}
        
        # بررسی تم‌ها
        themes = ['classic', 'dark', 'neon', 'blue', 'green']
        for theme in themes:
            path = self.get_theme_path(theme)
            results[f'theme_{theme}'] = os.path.exists(path)
            
        # بررسی صداها
        sounds = ['move', 'check', 'win', 'lose', 'draw', 'start', 'notification']
        for sound in sounds:
            path = self.get_sound_path(sound)
            results[f'sound_{sound}'] = os.path.exists(path)
            
        return results
        
    def get_asset_info(self) -> Dict:
        """دریافت اطلاعات Assets"""
        info = {
            'total_size': 0,
            'files': 0,
            'directories': {},
            'missing': []
        }
        
        for name, path in self.paths.items():
            if os.path.exists(path):
                size, count = self._get_dir_info(path)
                info['directories'][name] = {'size': size, 'files': count}
                info['total_size'] += size
                info['files'] += count
            else:
                info['missing'].append(name)
                
        return info
        
    def _get_dir_info(self, path: str) -> tuple:
        """دریافت اطلاعات یک پوشه"""
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1
                
        return total_size, file_count