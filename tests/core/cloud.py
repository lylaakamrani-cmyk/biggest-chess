# © 2025 AmirAli Kamrani. All rights reserved.

# core/cloud.py
import json
import time
import hashlib
import uuid
import threading
import queue
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime, timedelta
import requests
import os
import base64
import zlib

class CloudSync:
    """Cloud synchronization manager for game data"""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or "https://api.chesscloud.com/v1"
        self.api_key = api_key
        self.session_token = None
        self.user_id = None
        self.sync_queue = queue.Queue()
        self.sync_thread = None
        self.is_syncing = False
        self.last_sync = None
        self.sync_interval = 300  # 5 minutes
        self.max_retry = 3
        self.offline_data = {}
        
        # Cache
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        
        # Headers
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'ChessMasterPro/1.0'
        }
        
        if self.api_key:
            self.headers['X-API-Key'] = self.api_key
            
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with cloud service"""
        try:
            data = {
                'username': username,
                'password': password,
                'device_id': self._get_device_id()
            }
            
            response = self._make_request('POST', '/auth/login', data)
            
            if response and response.get('success'):
                self.session_token = response.get('token')
                self.user_id = response.get('user_id')
                self.headers['Authorization'] = f'Bearer {self.session_token}'
                return True
                
        except Exception as e:
            print(f"Authentication error: {e}")
            
        return False
        
    def register(self, username: str, password: str, email: str) -> bool:
        """Register with cloud service"""
        try:
            data = {
                'username': username,
                'password': password,
                'email': email
            }
            
            response = self._make_request('POST', '/auth/register', data)
            
            if response and response.get('success'):
                return True
                
        except Exception as e:
            print(f"Registration error: {e}")
            
        return False
        
    def sync_profile(self, profile_data: Dict) -> bool:
        """Sync user profile to cloud"""
        try:
            data = {
                'user_id': self.user_id,
                'profile': profile_data,
                'timestamp': int(time.time())
            }
            
            response = self._make_request('POST', '/profile/sync', data)
            
            if response and response.get('success'):
                return True
                
        except Exception as e:
            print(f"Profile sync error: {e}")
            # Store for later sync
            self._store_offline('profile', data)
            
        return False
        
    def sync_game(self, game_data: Dict) -> bool:
        """Sync game data to cloud"""
        try:
            data = {
                'user_id': self.user_id,
                'game': game_data,
                'timestamp': int(time.time())
            }
            
            response = self._make_request('POST', '/games/sync', data)
            
            if response and response.get('success'):
                return True
                
        except Exception as e:
            print(f"Game sync error: {e}")
            self._store_offline('game', data)
            
        return False
        
    def get_profile(self, user_id: str = None) -> Optional[Dict]:
        """Get user profile from cloud"""
        user_id = user_id or self.user_id
        
        cache_key = f'profile_{user_id}'
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_timeout:
                return cached_data
                
        try:
            response = self._make_request('GET', f'/profile/{user_id}')
            
            if response and response.get('success'):
                data = response.get('data')
                self.cache[cache_key] = (data, time.time())
                return data
                
        except Exception as e:
            print(f"Get profile error: {e}")
            
        return None
        
    def get_games(self, user_id: str = None, limit: int = 50) -> List[Dict]:
        """Get user games from cloud"""
        user_id = user_id or self.user_id
        
        cache_key = f'games_{user_id}'
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_timeout:
                return cached_data
                
        try:
            response = self._make_request('GET', f'/games/{user_id}?limit={limit}')
            
            if response and response.get('success'):
                data = response.get('data', [])
                self.cache[cache_key] = (data, time.time())
                return data
                
        except Exception as e:
            print(f"Get games error: {e}")
            
        return []
        
    def get_rating_history(self, user_id: str = None) -> List[Dict]:
        """Get rating history from cloud"""
        user_id = user_id or self.user_id
        
        cache_key = f'rating_{user_id}'
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_timeout:
                return cached_data
                
        try:
            response = self._make_request('GET', f'/rating/{user_id}')
            
            if response and response.get('success'):
                data = response.get('data', [])
                self.cache[cache_key] = (data, time.time())
                return data
                
        except Exception as e:
            print(f"Get rating history error: {e}")
            
        return []
        
    def sync_achievements(self, achievements: List[Dict]) -> bool:
        """Sync achievements to cloud"""
        try:
            data = {
                'user_id': self.user_id,
                'achievements': achievements,
                'timestamp': int(time.time())
            }
            
            response = self._make_request('POST', '/achievements/sync', data)
            
            if response and response.get('success'):
                return True
                
        except Exception as e:
            print(f"Achievements sync error: {e}")
            
        return False
        
    def get_friends(self) -> List[Dict]:
        """Get friends list from cloud"""
        try:
            response = self._make_request('GET', f'/friends/{self.user_id}')
            
            if response and response.get('success'):
                return response.get('data', [])
                
        except Exception as e:
            print(f"Get friends error: {e}")
            
        return []
        
    def add_friend(self, friend_username: str) -> bool:
        """Add friend via cloud"""
        try:
            data = {
                'user_id': self.user_id,
                'friend_username': friend_username
            }
            
            response = self._make_request('POST', '/friends/add', data)
            
            if response and response.get('success'):
                return True
                
        except Exception as e:
            print(f"Add friend error: {e}")
            
        return False
        
    def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        """Get global leaderboard"""
        try:
            response = self._make_request('GET', f'/leaderboard?limit={limit}')
            
            if response and response.get('success'):
                return response.get('data', [])
                
        except Exception as e:
            print(f"Get leaderboard error: {e}")
            
        return []
        
    def get_active_players(self) -> List[Dict]:
        """Get active online players"""
        try:
            response = self._make_request('GET', '/players/active')
            
            if response and response.get('success'):
                return response.get('data', [])
                
        except Exception as e:
            print(f"Get active players error: {e}")
            
        return []
        
    def send_challenge(self, opponent_id: str, challenge_data: Dict) -> bool:
        """Send game challenge via cloud"""
        try:
            data = {
                'user_id': self.user_id,
                'opponent_id': opponent_id,
                'challenge': challenge_data,
                'timestamp': int(time.time())
            }
            
            response = self._make_request('POST', '/challenges/send', data)
            
            if response and response.get('success'):
                return True
                
        except Exception as e:
            print(f"Send challenge error: {e}")
            
        return False
        
    def get_challenges(self) -> List[Dict]:
        """Get pending challenges"""
        try:
            response = self._make_request('GET', f'/challenges/{self.user_id}')
            
            if response and response.get('success'):
                return response.get('data', [])
                
        except Exception as e:
            print(f"Get challenges error: {e}")
            
        return []
        
    def accept_challenge(self, challenge_id: str) -> bool:
        """Accept a game challenge"""
        try:
            data = {'challenge_id': challenge_id}
            
            response = self._make_request('POST', '/challenges/accept', data)
            
            if response and response.get('success'):
                return True
                
        except Exception as e:
            print(f"Accept challenge error: {e}")
            
        return False
        
    def start_sync(self):
        """Start automatic sync thread"""
        if self.sync_thread and self.sync_thread.is_alive():
            return
            
        self.is_syncing = True
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
        
    def stop_sync(self):
        """Stop sync thread"""
        self.is_syncing = False
        if self.sync_thread:
            self.sync_thread.join(timeout=2)
            
    def _sync_worker(self):
        """Background sync worker"""
        while self.is_syncing:
            try:
                # Process sync queue
                while not self.sync_queue.empty():
                    item = self.sync_queue.get()
                    self._process_sync_item(item)
                    
                # Sync offline data
                self._sync_offline_data()
                
                # Update last sync time
                self.last_sync = time.time()
                
                # Wait for next sync
                time.sleep(self.sync_interval)
                
            except Exception as e:
                print(f"Sync worker error: {e}")
                time.sleep(10)
                
    def _process_sync_item(self, item: Dict):
        """Process a sync queue item"""
        sync_type = item.get('type')
        data = item.get('data')
        
        if sync_type == 'profile':
            self.sync_profile(data)
        elif sync_type == 'game':
            self.sync_game(data)
        elif sync_type == 'achievement':
            self.sync_achievements(data)
        elif sync_type == 'settings':
            self.sync_settings(data)
            
    def _store_offline(self, data_type: str, data: Dict):
        """Store data for offline sync"""
        if data_type not in self.offline_data:
            self.offline_data[data_type] = []
            
        self.offline_data[data_type].append({
            'data': data,
            'timestamp': int(time.time()),
            'retries': 0
        })
        
    def _sync_offline_data(self):
        """Sync offline stored data"""
        for data_type, items in list(self.offline_data.items()):
            for item in items:
                if item['retries'] >= self.max_retry:
                    self.offline_data[data_type].remove(item)
                    continue
                    
                try:
                    if data_type == 'profile':
                        success = self.sync_profile(item['data'])
                    elif data_type == 'game':
                        success = self.sync_game(item['data'])
                    else:
                        success = False
                        
                    if success:
                        self.offline_data[data_type].remove(item)
                    else:
                        item['retries'] += 1
                        
                except Exception as e:
                    print(f"Offline sync error: {e}")
                    item['retries'] += 1
                    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make API request"""
        url = self.api_url + endpoint
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=self.headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=self.headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=10)
            else:
                return None
                
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Token expired, try refresh
                if self._refresh_token():
                    return self._make_request(method, endpoint, data)
                    
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            
        return None
        
    def _refresh_token(self) -> bool:
        """Refresh authentication token"""
        try:
            data = {'token': self.session_token}
            response = self._make_request('POST', '/auth/refresh', data)
            
            if response and response.get('success'):
                self.session_token = response.get('token')
                self.headers['Authorization'] = f'Bearer {self.session_token}'
                return True
                
        except Exception as e:
            print(f"Token refresh error: {e}")
            
        return False
        
    def _get_device_id(self) -> str:
        """Get unique device ID"""
        # Try to get from file
        device_file = '.device_id'
        if os.path.exists(device_file):
            with open(device_file, 'r') as f:
                device_id = f.read().strip()
                if device_id:
                    return device_id
                    
        # Generate new device ID
        device_id = str(uuid.uuid4())
        try:
            with open(device_file, 'w') as f:
                f.write(device_id)
        except:
            pass
            
        return device_id
        
    def clear_cache(self):
        """Clear cache"""
        self.cache.clear()
        
    def get_sync_status(self) -> Dict:
        """Get sync status"""
        return {
            'is_syncing': self.is_syncing,
            'last_sync': self.last_sync,
            'last_sync_formatted': datetime.fromtimestamp(self.last_sync).strftime('%Y-%m-%d %H:%M:%S') if self.last_sync else 'Never',
            'offline_items': sum(len(items) for items in self.offline_data.values()),
            'queue_size': self.sync_queue.qsize(),
            'user_id': self.user_id,
            'authenticated': bool(self.session_token)
        }
        
    def sync_now(self) -> bool:
        """Force immediate sync"""
        try:
            # Sync profile
            if self.user_id:
                profile = self.get_profile()
                if profile:
                    self.sync_profile(profile)
                    
                # Sync games
                games = self.get_games()
                if games:
                    for game in games:
                        self.sync_game(game)
                        
                return True
                
        except Exception as e:
            print(f"Force sync error: {e}")
            
        return False
        
    def upload_analysis(self, analysis_data: Dict) -> bool:
        """Upload game analysis to cloud"""
        try:
            data = {
                'user_id': self.user_id,
                'analysis': analysis_data,
                'timestamp': int(time.time())
            }
            
            response = self._make_request('POST', '/analysis/upload', data)
            
            if response and response.get('success'):
                return True
                
        except Exception as e:
            print(f"Upload analysis error: {e}")
            
        return False
        
    def download_analysis(self, game_id: str) -> Optional[Dict]:
        """Download game analysis from cloud"""
        try:
            response = self._make_request('GET', f'/analysis/{self.user_id}/{game_id}')
            
            if response and response.get('success'):
                return response.get('data')
                
        except Exception as e:
            print(f"Download analysis error: {e}")
            
        return None
        
    def share_game(self, game_id: str, public: bool = True) -> Optional[str]:
        """Share game publicly"""
        try:
            data = {
                'game_id': game_id,
                'public': public,
                'user_id': self.user_id
            }
            
            response = self._make_request('POST', '/games/share', data)
            
            if response and response.get('success'):
                return response.get('share_url')
                
        except Exception as e:
            print(f"Share game error: {e}")
            
        return None
        
    def get_shared_game(self, share_url: str) -> Optional[Dict]:
        """Get shared game by URL"""
        try:
            response = self._make_request('GET', f'/games/shared/{share_url}')
            
            if response and response.get('success'):
                return response.get('data')
                
        except Exception as e:
            print(f"Get shared game error: {e}")
            
        return None
        
    def get_tournaments(self) -> List[Dict]:
        """Get upcoming tournaments from cloud"""
        try:
            response = self._make_request('GET', '/tournaments/upcoming')
            
            if response and response.get('success'):
                return response.get('data', [])
                
        except Exception as e:
            print(f"Get tournaments error: {e}")
            
        return []
        
    def register_tournament(self, tournament_id: str) -> bool:
        """Register for tournament"""
        try:
            data = {
                'user_id': self.user_id,
                'tournament_id': tournament_id
            }
            
            response = self._make_request('POST', '/tournaments/register', data)
            
            if response and response.get('success'):
                return True
                
        except Exception as e:
            print(f"Register tournament error: {e}")
            
        return False