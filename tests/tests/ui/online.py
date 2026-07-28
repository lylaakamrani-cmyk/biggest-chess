# © 2025 AmirAli Kamrani. All rights reserved.

# ui/online.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
import json
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class OnlineScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ws = None
        self.is_connected = False
        self.username = ''
        self.client_id = ''
        self.games = []
        self.players = []
        self.current_game_id = None
        self.chat_messages = []
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6))
        
        # Header
        header = BoxLayout(size_hint_y=0.06)
        back = Button(
            text='< Back',
            font_size=dp(18),
            size_hint_x=0.2,
            background_normal='',
            background_color=(0.2, 0.2, 0.35, 1)
        )
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        
        title = Label(
            text='🌐 Online Game',
            font_size=dp(24),
            color=(1, 1, 1, 1),
            bold=True
        )
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Username input
        username_row = BoxLayout(size_hint_y=0.07, spacing=dp(5))
        self.username_input = TextInput(
            hint_text='Enter username',
            font_size=dp(16),
            multiline=False,
            background_color=(0.15, 0.15, 0.25, 1),
            foreground_color=(1, 1, 1, 1),
            size_hint_x=0.7
        )
        username_row.add_widget(self.username_input)
        
        self.connect_btn = Button(
            text='🔗 Connect',
            font_size=dp(16),
            background_normal='',
            background_color=(0.2, 0.7, 0.2, 1),
            size_hint_x=0.3
        )
        self.connect_btn.bind(on_release=self.toggle_connect)
        username_row.add_widget(self.connect_btn)
        layout.add_widget(username_row)
        
        # Status
        self.status = Label(
            text='📡 Status: Disconnected',
            font_size=dp(14),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.04
        )
        layout.add_widget(self.status)
        
        # Create game
        create_btn = Button(
            text='➕ Create Game',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_color=(0.97, 0.59, 0.12, 1)
        )
        create_btn.bind(on_release=self.create_game)
        layout.add_widget(create_btn)
        
        # Game code input
        join_row = BoxLayout(size_hint_y=0.07, spacing=dp(5))
        self.game_code_input = TextInput(
            hint_text='Enter game code',
            font_size=dp(16),
            multiline=False,
            background_color=(0.15, 0.15, 0.25, 1),
            foreground_color=(1, 1, 1, 1),
            size_hint_x=0.7
        )
        join_row.add_widget(self.game_code_input)
        
        join_btn = Button(
            text='🔗 Join',
            font_size=dp(16),
            background_normal='',
            background_color=(0.2, 0.4, 0.8, 1),
            size_hint_x=0.3
        )
        join_btn.bind(on_release=self.join_game_code)
        join_row.add_widget(join_btn)
        layout.add_widget(join_row)
        
        # Lobby players
        layout.add_widget(Label(
            text='👥 Players Online:',
            font_size=dp(14),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.04
        ))
        self.players_list = Label(
            text='',
            font_size=dp(13),
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=0.10
        )
        layout.add_widget(self.players_list)
        
        # Active games
        layout.add_widget(Label(
            text='🎮 Active Games:',
            font_size=dp(14),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.04
        ))
        
        scroll = ScrollView(size_hint_y=0.30)
        self.games_grid = GridLayout(cols=1, spacing=dp(3), size_hint_y=None)
        self.games_grid.bind(minimum_height=self.games_grid.setter('height'))
        scroll.add_widget(self.games_grid)
        layout.add_widget(scroll)
        
        # Chat
        layout.add_widget(Label(
            text='💬 Chat:',
            font_size=dp(14),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.03
        ))
        
        chat_row = BoxLayout(size_hint_y=0.06, spacing=dp(5))
        self.chat_input = TextInput(
            hint_text='Type message...',
            font_size=dp(14),
            multiline=False,
            background_color=(0.15, 0.15, 0.25, 1),
            foreground_color=(1, 1, 1, 1),
            size_hint_x=0.8
        )
        chat_row.add_widget(self.chat_input)
        
        send_btn = Button(
            text='📤',
            font_size=dp(16),
            size_hint_x=0.2,
            background_normal='',
            background_color=(0.97, 0.59, 0.12, 1)
        )
        send_btn.bind(on_release=self.send_chat)
        chat_row.add_widget(send_btn)
        layout.add_widget(chat_row)
        
        self.chat_history = Label(
            text='Chat: Welcome!',
            font_size=dp(12),
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=0.06,
            halign='left',
            valign='top'
        )
        layout.add_widget(self.chat_history)
        
        self.add_widget(layout)
        
    def start_connection_thread(self):
        """Start WebSocket connection in background"""
        def connect():
            try:
                import websocket
                self.ws = websocket.WebSocket()
                self.ws.connect("ws://localhost:8765", timeout=3)
                # Use Clock to schedule on main thread
                Clock.schedule_once(lambda dt: self.on_connect(), 0)
            except Exception as err:
                # Store error message and schedule on main thread
                error_msg = str(err)
                Clock.schedule_once(lambda dt, msg=error_msg: self.on_connect_error(msg), 0)
                
        thread = threading.Thread(target=connect, daemon=True)
        thread.start()
        
    def on_connect(self):
        self.is_connected = True
        self.status.text = '✅ Status: Connected'
        self.status.color = (0.2, 0.8, 0.2, 1)
        self.connect_btn.text = '🔌 Disconnect'
        self.connect_btn.background_color = (0.8, 0.2, 0.2, 1)
        
        # Authenticate
        username = self.username_input.text.strip()
        if username:
            self.username = username
            self.send_message('auth', {'username': username})
        
        # Start receiving messages
        threading.Thread(target=self.receive_messages, daemon=True).start()
        
    def on_connect_error(self, error):
        self.status.text = f'❌ Connection error: {error}'
        self.status.color = (0.8, 0.2, 0.2, 1)
        self.is_connected = False
        
    def toggle_connect(self, instance):
        if self.is_connected:
            self.is_connected = False
            if self.ws:
                try:
                    self.ws.close()
                except:
                    pass
            self.status.text = '📡 Status: Disconnected'
            self.status.color = (0.7, 0.7, 0.7, 1)
            self.connect_btn.text = '🔗 Connect'
            self.connect_btn.background_color = (0.2, 0.7, 0.2, 1)
            self.players_list.text = ''
            self.games_grid.clear_widgets()
        else:
            username = self.username_input.text.strip()
            if username:
                self.username = username
                self.start_connection_thread()
            else:
                self.status.text = '⚠️ Please enter username'
                self.status.color = (0.8, 0.6, 0, 1)
                
    def receive_messages(self):
        while self.is_connected and self.ws:
            try:
                message = self.ws.recv()
                if message:
                    Clock.schedule_once(lambda dt, msg=message: self.handle_message(msg), 0)
            except Exception as e:
                print(f"Receive error: {e}")
                break
                
    def handle_message(self, message):
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'welcome':
                self.client_id = data.get('client_id')
                self.status.text = f'✅ Connected! ID: {self.client_id[:8]}'
                
            elif msg_type == 'auth_result':
                if data.get('success'):
                    self.status.text = f'✅ Authenticated as {data.get("username")}'
                    self.status.color = (0.2, 0.8, 0.2, 1)
                    # Join lobby automatically
                    self.send_message('join_lobby', {})
                else:
                    self.status.text = f'❌ {data.get("message")}'
                    self.status.color = (0.8, 0.2, 0.2, 1)
                    
            elif msg_type == 'lobby_update':
                self.players = data.get('players', [])
                self.players_list.text = ', '.join(self.players) if self.players else 'No players online'
                
            elif msg_type == 'games_list':
                self.games = data.get('games', [])
                self.update_games_list()
                
            elif msg_type == 'game_created':
                game_id = data.get('game_id')
                self.status.text = f'✅ Game created! Code: {game_id}'
                self.status.color = (0.2, 0.8, 0.2, 1)
                self.game_code_input.text = game_id
                
            elif msg_type == 'game_started':
                self.status.text = f'🎮 Game started!'
                self.status.color = (0.2, 0.8, 0.2, 1)
                self.current_game_id = data.get('game_id')
                self.go_to_board(data)
                
            elif msg_type == 'opponent_move':
                if self.current_game_id == data.get('game_id'):
                    self.status.text = f'⚡ Opponent moved'
                    
            elif msg_type == 'opponent_resigned':
                self.status.text = '🏳️ Opponent resigned! You win!'
                
            elif msg_type == 'draw_offered':
                self.status.text = f'🤝 {data.get("from")} offered a draw'
                
            elif msg_type == 'chat_message':
                from_name = data.get('from', 'Unknown')
                msg = data.get('message', '')
                self.chat_history.text = f'💬 {from_name}: {msg}'
                
            elif msg_type == 'error':
                self.status.text = f'❌ {data.get("message")}'
                self.status.color = (0.8, 0.2, 0.2, 1)
                
        except Exception as e:
            print(f"Error handling message: {e}")
            
    def send_message(self, msg_type, payload=None):
        if not self.is_connected or not self.ws:
            return
            
        try:
            message = {
                'type': msg_type,
                'payload': payload or {}
            }
            self.ws.send(json.dumps(message))
        except Exception as e:
            print(f"Send error: {e}")
            
    def update_games_list(self):
        self.games_grid.clear_widgets()
        if not self.games:
            label = Label(text='No games available', font_size=dp(13), color=(0.5, 0.5, 0.5, 1))
            self.games_grid.add_widget(label)
            return
            
        for game in self.games:
            row = BoxLayout(size_hint_y=None, height=dp(30))
            row.add_widget(Label(
                text=f'🎯 {game.get("white", "Unknown")} - {game.get("time_control", "10+0")}',
                font_size=dp(13),
                color=(0.8, 0.8, 0.8, 1),
                size_hint_x=0.7
            ))
            
            join_btn = Button(
                text='🔗 Join',
                font_size=dp(12),
                size_hint_x=0.3,
                background_normal='',
                background_color=(0.2, 0.4, 0.8, 1)
            )
            join_btn.bind(on_release=lambda x, gid=game.get('id'): self.join_game_id(gid))
            row.add_widget(join_btn)
            self.games_grid.add_widget(row)
            
    def create_game(self, instance):
        if not self.is_connected:
            self.status.text = '⚠️ Connect first!'
            self.status.color = (0.8, 0.6, 0, 1)
            return
            
        self.send_message('create_game', {'time_control': '10+0'})
        
    def join_game_code(self, instance):
        game_code = self.game_code_input.text.strip()
        if game_code:
            self.join_game_id(game_code)
            
    def join_game_id(self, game_id):
        if not self.is_connected:
            self.status.text = '⚠️ Connect first!'
            self.status.color = (0.8, 0.6, 0, 1)
            return
            
        self.send_message('join_game', {'game_id': game_id})
        
    def send_chat(self, instance):
        msg = self.chat_input.text.strip()
        if msg:
            self.send_message('chat', {'message': msg, 'game_id': self.current_game_id})
            self.chat_input.text = ''
            
    def go_to_board(self, data):
        """Go to board screen with game data"""
        from ui.board import BoardScreen
        board = BoardScreen(mode='online', name='board_online')
        board.is_online = True
        board.ws = self.ws
        board.game_id = self.current_game_id
        board.online_username = self.username
        self.manager.add_widget(board)
        self.manager.current = 'board_online'