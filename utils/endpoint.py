# © 2025 AmirAli Kamrani. All rights reserved.

# utils/endpoint.py
import json
import time
import threading
import requests
from typing import Dict, Optional, Any, List

class EndpointManager:
    """
    مدیریت نقطه اتصال REST به سرور مرکزی
    برای همگام‌سازی داده‌ها (فروشگاه، پروفایل، تورنمنت و...)
    """
    
    def __init__(self, server_url: str = "https://your-server.com/api"):
        self.server_url = server_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ChessMasterPro/1.0'
        })
        self.is_connected = False
        self.cache = {}
        self.cache_timeout = 60  # ثانیه
        self.token = None
        
    def connect(self) -> bool:
        """بررسی اتصال به سرور"""
        try:
            response = self.session.get(f"{self.server_url}/ping", timeout=5)
            if response.status_code == 200:
                self.is_connected = True
                print("✅ Endpoint connected")
                return True
        except Exception as e:
            print(f"⚠️ Endpoint connection failed: {e}")
        
        self.is_connected = False
        return False
        
    def is_online(self) -> bool:
        return self.is_connected
        
    # ==================== AUTH ====================
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        try:
            response = self.session.post(f"{self.server_url}/auth/login", json={
                'username': username,
                'password': password
            }, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.session.headers.update({
                    'Authorization': f"Bearer {self.token}"
                })
                return data
        except Exception as e:
            print(f"Login error: {e}")
        return None
        
    def register(self, username: str, password: str, email: str) -> Optional[Dict]:
        try:
            response = self.session.post(f"{self.server_url}/auth/register", json={
                'username': username,
                'password': password,
                'email': email
            }, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Register error: {e}")
        return None
        
    # ==================== SHOP ====================
    
    def get_shop_items(self, force_refresh: bool = False) -> List[Dict]:
        cache_key = 'shop_items'
        if not force_refresh and cache_key in self.cache:
            if time.time() - self.cache[cache_key]['time'] < self.cache_timeout:
                return self.cache[cache_key]['data']
                
        # اگر آفلاین هستیم، داده محلی برگردون
        if not self.is_connected:
            return self._get_local_shop_items()
            
        try:
            response = self.session.get(f"{self.server_url}/shop/items", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.cache[cache_key] = {'data': data, 'time': time.time()}
                return data
        except Exception as e:
            print(f"Get shop items error: {e}")
            
        return self._get_local_shop_items()
        
    def _get_local_shop_items(self) -> List[Dict]:
        return [
            {'id': 'theme_classic', 'name': 'Classic Theme', 'price': 0, 'rarity': 'common', 'icon': '🎨', 'category': 'theme'},
            {'id': 'theme_dark', 'name': 'Dark Theme', 'price': 150, 'rarity': 'common', 'icon': '🌙', 'category': 'theme'},
            {'id': 'theme_neon', 'name': 'Neon Theme', 'price': 300, 'rarity': 'rare', 'icon': '💡', 'category': 'theme'},
            {'id': 'theme_blue', 'name': 'Blue Theme', 'price': 200, 'rarity': 'uncommon', 'icon': '🔵', 'category': 'theme'},
            {'id': 'piece_classic', 'name': 'Classic Pieces', 'price': 0, 'rarity': 'common', 'icon': '♟️', 'category': 'piece'},
            {'id': 'piece_modern', 'name': 'Modern Pieces', 'price': 200, 'rarity': 'uncommon', 'icon': '♞', 'category': 'piece'},
            {'id': 'piece_gold', 'name': 'Gold Pieces', 'price': 600, 'rarity': 'legendary', 'icon': '👑', 'category': 'piece'},
        ]
        
    # ==================== PROFILE ====================
    
    def get_profile(self, user_id: str) -> Optional[Dict]:
        if not self.is_connected:
            return None
        try:
            response = self.session.get(f"{self.server_url}/profile/{user_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Get profile error: {e}")
        return None
        
    def update_profile(self, user_id: str, data: Dict) -> bool:
        if not self.is_connected:
            return False
        try:
            response = self.session.put(f"{self.server_url}/profile/{user_id}", json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Update profile error: {e}")
            return False
            
    # ==================== PURCHASE ====================
    
    def send_purchase(self, user_id: str, package_id: str, amount_toman: int, ref_id: str) -> bool:
        if not self.is_connected:
            return False
        try:
            response = self.session.post(f"{self.server_url}/purchase/record", json={
                'user_id': user_id,
                'package_id': package_id,
                'amount_toman': amount_toman,
                'ref_id': ref_id,
                'time': time.time()
            }, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Send purchase error: {e}")
            return False
            
    # ==================== LEADERBOARD ====================
    
    def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        if not self.is_connected:
            return []
        try:
            response = self.session.get(f"{self.server_url}/leaderboard?limit={limit}", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Get leaderboard error: {e}")
        return []
        
    # ==================== TOURNAMENT ====================
    
    def get_tournaments(self) -> List[Dict]:
        if not self.is_connected:
            return []
        try:
            response = self.session.get(f"{self.server_url}/tournaments", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Get tournaments error: {e}")
        return []
        
    def register_tournament(self, user_id: str, tournament_id: str) -> bool:
        if not self.is_connected:
            return False
        try:
            response = self.session.post(f"{self.server_url}/tournaments/register", json={
                'user_id': user_id,
                'tournament_id': tournament_id
            }, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Register tournament error: {e}")
            return False