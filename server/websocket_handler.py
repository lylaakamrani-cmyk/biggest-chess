# © 2025 AmirAli Kamrani. All rights reserved.

# server/websocket_handler.py
import json
import time
import uuid
from typing import Optional, Dict, List, Any

class WebSocketHandler:
    """مدیریت پیام‌های WebSocket"""
    
    def __init__(self):
        self.handlers = {}
        self.middleware = []
        self._register_default_handlers()
        
    def _register_default_handlers(self):
        """ثبت هندلرهای پیش‌فرض"""
        self.register('auth', self._handle_auth)
        self.register('message', self._handle_message)
        self.register('ping', self._handle_ping)
        self.register('game_action', self._handle_game_action)
        self.register('chat', self._handle_chat)
        
    def register(self, msg_type: str, handler):
        """ثبت هندلر جدید"""
        self.handlers[msg_type] = handler
        print(f"📝 Registered handler: {msg_type}")
        
    def add_middleware(self, middleware):
        """افزودن میان‌افزار"""
        self.middleware.append(middleware)
        
    async def handle(self, client_id: str, message: Dict) -> Dict:
        """پردازش پیام"""
        try:
            # اجرای میان‌افزارها
            for mw in self.middleware:
                result = await mw(client_id, message)
                if result is False:
                    return {'success': False, 'error': 'Middleware blocked'}
                    
            msg_type = message.get('type')
            payload = message.get('payload', {})
            
            handler = self.handlers.get(msg_type)
            if handler:
                result = await handler(client_id, payload)
                return {'success': True, 'data': result}
            else:
                return {'success': False, 'error': f'Unknown type: {msg_type}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    async def _handle_auth(self, client_id: str, payload: Dict) -> Dict:
        """احراز هویت"""
        username = payload.get('username')
        password = payload.get('password')
        
        # بررسی کاربر (ساده)
        if username and password:
            return {
                'authenticated': True,
                'user': {'id': client_id, 'username': username}
            }
            
        return {'authenticated': False, 'error': 'Invalid credentials'}
        
    async def _handle_message(self, client_id: str, payload: Dict) -> Dict:
        """پیام عمومی"""
        text = payload.get('text', '')
        return {'received': text, 'timestamp': time.time()}
        
    async def _handle_ping(self, client_id: str, payload: Dict) -> Dict:
        """پاسخ به پینگ"""
        return {'pong': True, 'timestamp': time.time()}
        
    async def _handle_game_action(self, client_id: str, payload: Dict) -> Dict:
        """عملیات بازی"""
        action = payload.get('action')
        data = payload.get('data', {})
        
        actions = {
            'move': self._handle_move,
            'resign': self._handle_resign,
            'draw': self._handle_draw,
            'ready': self._handle_ready
        }
        
        handler = actions.get(action)
        if handler:
            return await handler(client_id, data)
            
        return {'error': f'Unknown action: {action}'}
        
    async def _handle_move(self, client_id: str, data: Dict) -> Dict:
        """مدیریت حرکت"""
        move = data.get('move')
        game_id = data.get('game_id')
        
        return {
            'action': 'move',
            'move': move,
            'game_id': game_id,
            'status': 'processed'
        }
        
    async def _handle_resign(self, client_id: str, data: Dict) -> Dict:
        """تسلیم شدن"""
        game_id = data.get('game_id')
        
        return {
            'action': 'resign',
            'game_id': game_id,
            'status': 'resigned'
        }
        
    async def _handle_draw(self, client_id: str, data: Dict) -> Dict:
        """پیشنهاد مساوی"""
        game_id = data.get('game_id')
        
        return {
            'action': 'draw',
            'game_id': game_id,
            'status': 'offered'
        }
        
    async def _handle_ready(self, client_id: str, data: Dict) -> Dict:
        """آمادگی بازیکن"""
        game_id = data.get('game_id')
        
        return {
            'action': 'ready',
            'game_id': game_id,
            'status': 'ready'
        }
        
    async def _handle_chat(self, client_id: str, payload: Dict) -> Dict:
        """پیام چت"""
        message = payload.get('message', '')
        target = payload.get('target')
        
        return {
            'from': client_id,
            'to': target,
            'message': message,
            'timestamp': time.time()
        }

class WebSocketMiddleware:
    """کلاس پایه میان‌افزار WebSocket"""
    
    async def process(self, client_id: str, message: Dict) -> bool:
        """پردازش پیام"""
        return True

class AuthMiddleware(WebSocketMiddleware):
    """میان‌افزار احراز هویت"""
    
    def __init__(self, allowed_users: List[str] = None):
        self.allowed_users = allowed_users or []
        
    async def process(self, client_id: str, message: Dict) -> bool:
        # بررسی احراز هویت
        if message.get('type') == 'auth':
            return True
            
        # کاربر باید احراز هویت شده باشد
        # (اینجا باید چک شود)
        return True

class RateLimitMiddleware(WebSocketMiddleware):
    """میان‌افزار محدودیت نرخ"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
        
    async def process(self, client_id: str, message: Dict) -> bool:
        # محدودیت نرخ
        now = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
            
        # پاک کردن درخواست‌های قدیمی
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if now - t < self.time_window
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            return False
            
        self.requests[client_id].append(now)
        return True

def main():
    """تست WebSocketHandler"""
    handler = WebSocketHandler()
    
    # اضافه کردن میان‌افزار
    handler.add_middleware(AuthMiddleware())
    handler.add_middleware(RateLimitMiddleware())
    
    print("✅ WebSocketHandler ready")
    print("📝 Registered handlers:", list(handler.handlers.keys()))
    
if __name__ == "__main__":
    main()