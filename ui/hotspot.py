# © 2025 AmirAli Kamrani. All rights reserved.

# ui/hotspot.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
import socket
import threading
import time
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.network import NetworkServer, NetworkClient

class HotspotScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server = None
        self.client = None
        self.is_host = False
        self.is_connected = False
        self.players = []
        self.hotspot_ip = self.get_hotspot_ip()
        self.build_ui()
        
    def get_hotspot_ip(self):
        """دریافت IP هات‌اسپات (معمولاً 192.168.43.1)"""
        try:
            # دریافت IP دستگاه
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            # اگر IP با 192.168.43 شروع شد، یعنی هات‌اسپات فعال است
            if ip.startswith('192.168.43'):
                return ip
            return ip
        except:
            return '192.168.43.1'
            
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Header
        header = BoxLayout(size_hint_y=0.06)
        back = Button(text='< Back', font_size=dp(18), size_hint_x=0.2,
                     background_normal='', background_color=(0.2, 0.2, 0.35, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text='Hotspot Game', font_size=dp(22), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Status
        self.status = Label(text='Status: Disconnected', font_size=dp(14), color=(0.7, 0.7, 0.7, 1))
        layout.add_widget(self.status)
        
        # IP Info
        ip_row = BoxLayout(size_hint_y=0.06, spacing=dp(5))
        ip_row.add_widget(Label(text='Hotspot IP:', font_size=dp(14), color=(0.8, 0.8, 0.8, 1), size_hint_x=0.25))
        self.ip_label = Label(text=self.hotspot_ip, font_size=dp(14), color=(1, 1, 0.6, 1), size_hint_x=0.5)
        ip_row.add_widget(self.ip_label)
        
        refresh_btn = Button(text='Refresh', font_size=dp(12), size_hint_x=0.25,
                            background_normal='', background_color=(0.2, 0.4, 0.8, 1))
        refresh_btn.bind(on_release=self.refresh_ip)
        ip_row.add_widget(refresh_btn)
        layout.add_widget(ip_row)
        
        # Buttons
        btn_row = BoxLayout(size_hint_y=0.07, spacing=dp(8))
        
        self.host_btn = Button(text='Start Host', font_size=dp(16), background_normal='', background_color=(0.97, 0.59, 0.12, 1))
        self.host_btn.bind(on_release=self.start_host)
        btn_row.add_widget(self.host_btn)
        
        self.join_btn = Button(text='Join Game', font_size=dp(16), background_normal='', background_color=(0.2, 0.7, 0.2, 1))
        self.join_btn.bind(on_release=self.join_game)
        btn_row.add_widget(self.join_btn)
        layout.add_widget(btn_row)
        
        # Join input
        join_row = BoxLayout(size_hint_y=0.06, spacing=dp(5))
        self.ip_input = TextInput(hint_text='Enter Host IP', font_size=dp(14), multiline=False,
                                 background_color=(0.15, 0.15, 0.25, 1), foreground_color=(1, 1, 1, 1), size_hint_x=0.6)
        join_row.add_widget(self.ip_input)
        
        connect_btn = Button(text='Connect', font_size=dp(14), size_hint_x=0.4,
                            background_normal='', background_color=(0.2, 0.4, 0.8, 1))
        connect_btn.bind(on_release=self.connect_to_host)
        join_row.add_widget(connect_btn)
        layout.add_widget(join_row)
        
        # Players
        layout.add_widget(Label(text='Players:', font_size=dp(14), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.04))
        self.players_list = Label(text='No players', font_size=dp(13), color=(0.8, 0.8, 0.8, 1), size_hint_y=0.08)
        layout.add_widget(self.players_list)
        
        # Game code (for host)
        code_row = BoxLayout(size_hint_y=0.06, spacing=dp(5))
        code_row.add_widget(Label(text='Game Code:', font_size=dp(14), color=(0.8, 0.8, 0.8, 1), size_hint_x=0.25))
        self.code_display = Label(text='------', font_size=dp(16), color=(1, 1, 0.6, 1), size_hint_x=0.5)
        code_row.add_widget(self.code_display)
        layout.add_widget(code_row)
        
        # Start game button
        start_btn = Button(text='Start Game', font_size=dp(18), size_hint_y=None, height=dp(45),
                          background_normal='', background_color=(0.97, 0.59, 0.12, 1))
        start_btn.bind(on_release=self.start_game)
        layout.add_widget(start_btn)
        
        self.add_widget(layout)
        
    def refresh_ip(self, instance):
        self.hotspot_ip = self.get_hotspot_ip()
        self.ip_label.text = self.hotspot_ip
        
    def start_host(self, instance):
        """راه‌اندازی سرور روی هات‌اسپات"""
        try:
            # راه‌اندازی سرور
            self.server = NetworkServer(self.hotspot_ip, 8765)
            threading.Thread(target=self.server.start, daemon=True).start()
            
            self.is_host = True
            self.is_connected = True
            self.status.text = f'Status: Hosting on {self.hotspot_ip}:8765'
            self.status.color = (0.2, 0.8, 0.2, 1)
            self.host_btn.text = 'Stop Host'
            self.host_btn.background_color = (0.8, 0.2, 0.2, 1)
            
            # تولید کد بازی
            import random, string
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.code_display.text = code
            
            # شروع ترد دریافت پیام‌ها
            threading.Thread(target=self.host_receive, daemon=True).start()
            
            popup = Popup(title='✅ Host Started', 
                        content=Label(text=f'Game Code: {code}\nIP: {self.hotspot_ip}\nPort: 8765', font_size=dp(14)),
                        size_hint=(0.8, 0.35))
            popup.open()
            
        except Exception as e:
            popup = Popup(title='❌ Error', 
                        content=Label(text=f'Failed to start host: {e}', font_size=dp(14)),
                        size_hint=(0.8, 0.3))
            popup.open()
            
    def host_receive(self):
        """دریافت پیام‌ها در حالت هاست"""
        # در اینجا می‌توانید پیام‌های دریافتی از کلاینت‌ها را پردازش کنید
        pass
        
    def join_game(self, instance):
        """اتصال به عنوان کلاینت"""
        if self.is_connected:
            self.is_connected = False
            self.is_host = False
            if self.client:
                self.client.disconnect()
                self.client = None
            self.status.text = 'Status: Disconnected'
            self.status.color = (0.7, 0.7, 0.7, 1)
            self.join_btn.text = 'Join Game'
            self.join_btn.background_color = (0.2, 0.7, 0.2, 1)
            self.players_list.text = 'No players'
            return
            
        # وارد کردن IP
        popup = Popup(title='Join Game', 
                    content=Label(text='Enter Host IP:', font_size=dp(14)),
                    size_hint=(0.7, 0.2))
        popup.open()
        
    def connect_to_host(self, instance):
        """اتصال به هاست با IP وارد شده"""
        host_ip = self.ip_input.text.strip()
        if not host_ip:
            host_ip = self.hotspot_ip
            
        try:
            self.client = NetworkClient(f'ws://{host_ip}:8765')
            if self.client.connect():
                self.is_connected = True
                self.status.text = f'Status: Connected to {host_ip}'
                self.status.color = (0.2, 0.8, 0.2, 1)
                self.join_btn.text = 'Disconnect'
                self.join_btn.background_color = (0.8, 0.2, 0.2, 1)
                
                # احراز هویت
                self.client.authenticate('Player', 'password')
                
                popup = Popup(title='✅ Connected', 
                            content=Label(text=f'Connected to {host_ip}', font_size=dp(14)),
                            size_hint=(0.7, 0.3))
                popup.open()
            else:
                popup = Popup(title='❌ Connection Failed', 
                            content=Label(text=f'Could not connect to {host_ip}', font_size=dp(14)),
                            size_hint=(0.7, 0.3))
                popup.open()
        except Exception as e:
            popup = Popup(title='❌ Error', 
                        content=Label(text=f'Connection error: {e}', font_size=dp(14)),
                        size_hint=(0.8, 0.3))
            popup.open()
            
    def start_game(self, instance):
        """شروع بازی"""
        if self.is_connected:
            self.manager.current = 'board'
        else:
            popup = Popup(title='⚠️ Not Connected', 
                        content=Label(text='Please connect first!', font_size=dp(14)),
                        size_hint=(0.7, 0.3))
            popup.open()