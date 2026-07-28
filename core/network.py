# © 2025 AmirAli Kamrani. All rights reserved.

# core/network.py
import asyncio
import json
import websockets
import threading
import time
import queue
from typing import Optional, Dict, Any, Callable

class NetworkClient:
    """کلاینت WebSocket برای اتصال به سرور"""
    
    def __init__(self, server_url: str = 'ws://localhost:8765'):
        self.server_url = server_url
        self.websocket = None
        self.connected = False
        self.message_queue = queue.Queue()
        self.receive_thread = None
        self.running = False
        self.client_id = None
        self.callbacks = {}
        self.loop = None
        
    def connect(self) -> bool:
        """اتصال به سرور"""
        try:
            self.running = True
            self.receive_thread = threading.Thread(target=self._run_receiver, daemon=True)
            self.receive_thread.start()
            
            # منتظر اتصال
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
                
            return self.connected
        except Exception as e:
            print(f"Connection error: {e}")
            return False
            
    def _run_receiver(self):
        """اجرای حلقه دریافت پیام"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self._connect_and_receive())
        
    async def _connect_and_receive(self):
        """اتصال و دریافت پیام"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            self._trigger_callback('connected', {})
            
            # دریافت پیام‌ها
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._process_message(data)
                except Exception as e:
                    print(f"Process error: {e}")
                    
        except Exception as e:
            print(f"Connection lost: {e}")
            self.connected = False
            self._trigger_callback('disconnected', {})
            
    async def _process_message(self, data: Dict):
        """پردازش پیام دریافتی"""
        msg_type = data.get('type')
        
        if msg_type == 'welcome':
            self.client_id = data.get('client_id')
            self._trigger_callback('welcome', data)
            
        elif msg_type == 'auth_ok':
            self._trigger_callback('auth_ok', data)
            
        elif msg_type == 'lobby_update':
            self._trigger_callback('lobby_update', data)
            
        elif msg_type == 'games_list':
            self._trigger_callback('games_list', data)
            
        elif msg_type == 'game_created':
            self._trigger_callback('game_created', data)
            
        elif msg_type == 'game_started':
            self._trigger_callback('game_started', data)
            
        elif msg_type == 'opponent_move':
            self._trigger_callback('opponent_move', data)
            
        elif msg_type == 'opponent_resigned':
            self._trigger_callback('opponent_resigned', data)
            
        elif msg_type == 'draw_offered':
            self._trigger_callback('draw_offered', data)
            
        elif msg_type == 'chat_message':
            self._trigger_callback('chat_message', data)
            
        elif msg_type == 'error':
            self._trigger_callback('error', data)
            
    def send_message(self, msg_type: str, payload: Dict = None):
        """ارسال پیام به سرور"""
        if not self.connected or not self.websocket:
            return False
            
        try:
            message = {
                'type': msg_type,
                'payload': payload or {}
            }
            # ارسال غیرهمزمان
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(message)),
                self.loop
            )
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
            
    def authenticate(self, username: str, password: str):
        """احراز هویت در سرور"""
        self.send_message('auth', {'username': username, 'password': password})
        
    def create_game(self, time_control: str = '10+0'):
        """ایجاد بازی جدید"""
        self.send_message('create_game', {'time_control': time_control})
        
    def join_game(self, game_id: str):
        """پیوستن به بازی"""
        self.send_message('join_game', {'game_id': game_id})
        
    def send_move(self, game_id: str, move: str):
        """ارسال حرکت"""
        self.send_message('move', {'game_id': game_id, 'move': move})
        
    def send_chat(self, game_id: str, message: str):
        """ارسال پیام چت"""
        self.send_message('chat', {'game_id': game_id, 'message': message})
        
    def resign(self, game_id: str):
        """تسلیم شدن"""
        self.send_message('resign', {'game_id': game_id})
        
    def offer_draw(self, game_id: str):
        """پیشنهاد مساوی"""
        self.send_message('draw_offer', {'game_id': game_id})
        
    def get_lobby(self):
        """دریافت لیست لابی"""
        self.send_message('get_lobby', {})
        
    def get_games(self):
        """دریافت لیست بازی‌ها"""
        self.send_message('get_games', {})
        
    def disconnect(self):
        """قطع اتصال"""
        self.running = False
        self.connected = False
        if self.websocket:
            try:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.close(),
                    self.loop
                )
            except:
                pass
            
    def is_connected(self) -> bool:
        """بررسی اتصال"""
        return self.connected
        
    def on(self, event: str, callback: Callable):
        """ثبت callback برای رویداد"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
        
    def _trigger_callback(self, event: str, data: Dict):
        """فراخوانی callback ها"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Callback error: {e}")