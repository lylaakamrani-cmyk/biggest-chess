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
from kivy.metrics import dp
from kivy.clock import Clock
import json
import threading
import random
import string
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.network import NetworkClient

class OnlineScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # حالت: واقعی (WebSocket) یا ساده (محلی)
        self.use_real_server = False
        self.network = None
        
        # متغیرهای ساده
        self.games = []
        self.players = ['Player1', 'Player2', 'Player3']
        self.game_codes = {}
        
        # متغیرهای واقعی
        self.ws = None
        self.is_connected = False
        self.username = ''
        self.client_id = ''
        self.current_game_id = None
        self.is_host = False
        self.real_games = []
        self.real_players = []
        
        self.build_ui()
        
    def generate_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6))
        
        # Header
        header = BoxLayout(size_hint_y=0.06)
        back = Button(text='< Back', font_size=dp(18), size_hint_x=0.2,
                     background_normal='', background_color=(0.2, 0.2, 0.35, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text='Online Game', font_size=dp(24), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Username
        user_row = BoxLayout(size_hint_y=0.07, spacing=dp(5))
        self.username_input = TextInput(hint_text='Username', font_size=dp(16), multiline=False,
                                       background_color=(0.15, 0.15, 0.25, 1), foreground_color=(1, 1, 1, 1), size_hint_x=0.5)
        user_row.add_widget(self.username_input)
        
        self.connect_btn = Button(text='Connect', font_size=dp(14), size_hint_x=0.25,
                                 background_normal='', background_color=(0.2, 0.7, 0.2, 1))
        self.connect_btn.bind(on_release=self.toggle_connect)
        user_row.add_widget(self.connect_btn)
        
        self.mode_btn = Button(text='Simple Mode', font_size=dp(12), size_hint_x=0.25,
                              background_normal='', background_color=(0.2, 0.4, 0.8, 1))
        self.mode_btn.bind(on_release=self.toggle_mode)
        user_row.add_widget(self.mode_btn)
        layout.add_widget(user_row)
        
        # Status
        self.status = Label(text='Status: Disconnected (Simple Mode)', font_size=dp(13), 
                           color=(0.7, 0.7, 0.7, 1), size_hint_y=0.04)
        layout.add_widget(self.status)
        
        # Game Code
        code_row = BoxLayout(size_hint_y=0.07, spacing=dp(5))
        code_row.add_widget(Label(text='Game Code:', font_size=dp(15), color=(0.8, 0.8, 0.8, 1), size_hint_x=0.2))
        self.code_display = Label(text='------', font_size=dp(18), color=(1, 1, 0.6, 1), size_hint_x=0.35)
        code_row.add_widget(self.code_display)
        
        gen_btn = Button(text='New Code', font_size=dp(13), size_hint_x=0.2,
                        background_normal='', background_color=(0.2, 0.4, 0.8, 1))
        gen_btn.bind(on_release=self.generate_new_code)
        code_row.add_widget(gen_btn)
        
        refresh_btn = Button(text='Refresh', font_size=dp(13), size_hint_x=0.25,
                            background_normal='', background_color=(0.3, 0.3, 0.5, 1))
        refresh_btn.bind(on_release=self.refresh)
        code_row.add_widget(refresh_btn)
        layout.add_widget(code_row)
        
        # Create/Join buttons
        btn_row = BoxLayout(size_hint_y=0.07, spacing=dp(5))
        create_btn = Button(text='Create Game', font_size=dp(16), background_normal='', background_color=(0.97, 0.59, 0.12, 1))
        create_btn.bind(on_release=self.create_game)
        btn_row.add_widget(create_btn)
        
        join_btn = Button(text='Join Game', font_size=dp(16), background_normal='', background_color=(0.2, 0.7, 0.2, 1))
        join_btn.bind(on_release=self.join_game)
        btn_row.add_widget(join_btn)
        layout.add_widget(btn_row)
        
        # Join input
        join_row = BoxLayout(size_hint_y=0.06, spacing=dp(5))
        self.join_input = TextInput(hint_text='Enter game code', font_size=dp(14), multiline=False,
                                   background_color=(0.15, 0.15, 0.25, 1), foreground_color=(1, 1, 1, 1), size_hint_x=0.6)
        join_row.add_widget(self.join_input)
        
        go_btn = Button(text='Go', font_size=dp(14), size_hint_x=0.4,
                       background_normal='', background_color=(0.2, 0.4, 0.8, 1))
        go_btn.bind(on_release=self.join_game_by_code_input)
        join_row.add_widget(go_btn)
        layout.add_widget(join_row)
        
        # Players online
        layout.add_widget(Label(text='Players Online:', font_size=dp(13), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.04))
        self.players_list = Label(text='No players', font_size=dp(13), color=(0.8, 0.8, 0.8, 1), size_hint_y=0.06)
        layout.add_widget(self.players_list)
        
        # Active games
        layout.add_widget(Label(text='Active Games:', font_size=dp(13), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.04))
        scroll = ScrollView(size_hint_y=0.30)
        self.games_grid = GridLayout(cols=1, spacing=dp(3), size_hint_y=None)
        self.games_grid.bind(minimum_height=self.games_grid.setter('height'))
        scroll.add_widget(self.games_grid)
        layout.add_widget(scroll)
        
        # Chat
        layout.add_widget(Label(text='Chat:', font_size=dp(13), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.03))
        chat_row = BoxLayout(size_hint_y=0.06, spacing=dp(5))
        self.chat_input = TextInput(hint_text='Message...', font_size=dp(13), multiline=False,
                                   background_color=(0.15, 0.15, 0.25, 1), foreground_color=(1, 1, 1, 1), size_hint_x=0.8)
        chat_row.add_widget(self.chat_input)
        
        send_btn = Button(text='Send', font_size=dp(13), size_hint_x=0.2,
                         background_normal='', background_color=(0.97, 0.59, 0.12, 1))
        send_btn.bind(on_release=self.send_chat)
        chat_row.add_widget(send_btn)
        layout.add_widget(chat_row)
        
        self.chat_history = Label(text='Chat: Welcome!', font_size=dp(11),
                                  color=(0.6, 0.6, 0.6, 1), size_hint_y=0.05, halign='left', valign='top')
        layout.add_widget(self.chat_history)
        
        self.add_widget(layout)
        self.update_games_list()
        
    def toggle_mode(self, instance):
        """تغییر بین حالت ساده و واقعی"""
        self.use_real_server = not self.use_real_server
        mode_text = 'Real Mode' if self.use_real_server else 'Simple Mode'
        self.mode_btn.text = mode_text
        self.status.text = f'Status: {mode_text}'
        if self.use_real_server:
            self.status.color = (0.2, 0.8, 0.2, 1)
            self.start_real_connection()
        else:
            self.status.color = (0.7, 0.7, 0.7, 1)
            self.is_connected = False
            self.connect_btn.text = 'Connect'
            self.connect_btn.background_color = (0.2, 0.7, 0.2, 1)
            if self.network:
                self.network.disconnect()
                self.network = None
            self.players_list.text = 'Player1, Player2, Player3'
            self.update_games_list_simple()
            
    def generate_new_code(self, instance):
        code = self.generate_code()
        self.code_display.text = code
        
    # ================ SIMPLE MODE ================
    
    def create_game_simple(self):
        code = self.code_display.text
        if code == '------':
            code = self.generate_code()
            self.code_display.text = code
            
        self.games.append({
            'code': code,
            'host': 'You',
            'status': 'waiting',
            'players': 1
        })
        self.game_codes[code] = {'host': 'You', 'joined': False}
        self.update_games_list_simple()
        
        popup = Popup(title='Game Created!', 
                    content=Label(text=f'Game Code: {code}\nShare with opponent!', font_size=dp(16)),
                    size_hint=(0.7, 0.35))
        popup.open()
        
    def join_game_simple(self):
        code = self.join_input.text.strip().upper()
        if code in self.game_codes:
            if not self.game_codes[code]['joined']:
                self.game_codes[code]['joined'] = True
                popup = Popup(title='Joined!', 
                            content=Label(text=f'You joined game {code}!', font_size=dp(16)),
                            size_hint=(0.7, 0.3))
                popup.open()
                self.manager.current = 'board'
            else:
                popup = Popup(title='Error', 
                            content=Label(text='Game is full!', font_size=dp(16)),
                            size_hint=(0.7, 0.3))
                popup.open()
        else:
            popup = Popup(title='Error', 
                        content=Label(text='Invalid game code!', font_size=dp(16)),
                        size_hint=(0.7, 0.3))
            popup.open()
            
    def update_games_list_simple(self):
        self.games_grid.clear_widgets()
        if not self.games:
            label = Label(text='No active games', font_size=dp(13), color=(0.5, 0.5, 0.5, 1))
            self.games_grid.add_widget(label)
            return
            
        for game in self.games:
            row = BoxLayout(size_hint_y=None, height=dp(30))
            status_icon = '🟢' if game['status'] == 'waiting' else '🔴'
            row.add_widget(Label(text=f'{status_icon} {game["code"]} - {game["host"]} ({game["players"]}/2)',
                                font_size=dp(13), color=(0.8, 0.8, 0.8, 1), size_hint_x=0.7))
            
            if game['status'] == 'waiting' and game['players'] < 2:
                join_btn = Button(text='Join', font_size=dp(12), size_hint_x=0.3,
                                 background_normal='', background_color=(0.2, 0.4, 0.8, 1))
                join_btn.bind(on_release=lambda x, c=game['code']: self.join_game_by_code(c))
                row.add_widget(join_btn)
            else:
                row.add_widget(Label(text='Full', font_size=dp(12), color=(0.5, 0.5, 0.5, 1), size_hint_x=0.3))
            self.games_grid.add_widget(row)
            
    def join_game_by_code(self, code):
        self.join_input.text = code
        self.join_game(None)
        
    def join_game_by_code_input(self, instance):
        code = self.join_input.text.strip().upper()
        if code:
            if self.use_real_server:
                self.join_game_real(code)
            else:
                self.join_input.text = code
                self.join_game(None)
                
    # ================ REAL MODE (WebSocket) ================
    
    def start_real_connection(self):
        """اتصال به سرور واقعی با WebSocket"""
        if self.network is None:
            self.network = NetworkClient('ws://localhost:8765')
        
        username = self.username_input.text.strip() or 'Guest'
        self.username = username
        
        if self.network.connect():
            self.is_connected = True
            self.status.text = f'Status: Connected (Real Mode)'
            self.status.color = (0.2, 0.8, 0.2, 1)
            self.connect_btn.text = 'Disconnect'
            self.connect_btn.background_color = (0.8, 0.2, 0.2, 1)
            
            # Authenticate
            self.network.authenticate(username, 'password123')
            
            # Start receiving messages
            threading.Thread(target=self.receive_messages_real, daemon=True).start()
            
            # Get lobby and games
            self.network.send_message('get_lobby', {})
            self.network.send_message('get_games', {})
        else:
            self.status.text = 'Connection failed!'
            self.status.color = (0.8, 0.2, 0.2, 1)
            
    def receive_messages_real(self):
        """دریافت پیام‌های سرور"""
        while self.is_connected and self.network and self.network.is_connected():
            try:
                # Read messages from queue
                import time
                time.sleep(0.1)
                # Messages are handled by NetworkClient callbacks
            except Exception as e:
                print(f"Receive error: {e}")
                break
                
    def toggle_connect(self, instance):
        if self.use_real_server:
            if self.is_connected:
                self.is_connected = False
                if self.network:
                    self.network.disconnect()
                    self.network = None
                self.status.text = 'Status: Disconnected (Real Mode)'
                self.status.color = (0.7, 0.7, 0.7, 1)
                self.connect_btn.text = 'Connect'
                self.connect_btn.background_color = (0.2, 0.7, 0.2, 1)
                self.players_list.text = ''
                self.games_grid.clear_widgets()
            else:
                if self.username_input.text.strip():
                    self.start_real_connection()
                else:
                    self.status.text = 'Enter username first!'
                    self.status.color = (0.8, 0.6, 0, 1)
                    
    def join_game_real(self, game_id):
        if not self.is_connected or not self.network:
            self.status.text = 'Connect first!'
            return
        self.is_host = False
        self.network.send_message('join_game', {'game_id': game_id})
            
    # ================ MAIN FUNCTIONS ================
    
    def create_game(self, instance):
        if self.use_real_server:
            if not self.is_connected or not self.network:
                self.status.text = 'Connect first!'
                return
            self.is_host = True
            self.network.send_message('create_game', {'time_control': '10+0'})
            self.status.text = 'Creating game...'
        else:
            self.create_game_simple()
            
    def join_game(self, instance):
        if self.use_real_server:
            self.join_game_by_code_input(instance)
        else:
            self.join_game_simple()
            
    def refresh(self, instance):
        if self.use_real_server:
            if self.is_connected and self.network:
                self.network.send_message('get_games', {})
                self.network.send_message('get_lobby', {})
        else:
            self.update_games_list_simple()
            
    def send_chat(self, instance):
        msg = self.chat_input.text.strip()
        if msg:
            if self.use_real_server and self.is_connected and self.network:
                self.network.send_message('chat', {'message': msg, 'game_id': self.current_game_id})
                self.chat_history.text = f'You: {msg}'
            else:
                self.chat_history.text = f'You: {msg}'
            self.chat_input.text = ''
            
    def update_games_list(self):
        if self.use_real_server:
            # Real mode - will be updated by server messages
            pass
        else:
            self.update_games_list_simple()