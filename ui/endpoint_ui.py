# © 2025 AmirAli Kamrani. All rights reserved.

# ui/endpoint_ui.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# تلاش برای import endpoint
try:
    from utils.endpoint import EndpointManager
    ENDPOINT_AVAILABLE = True
except ImportError:
    ENDPOINT_AVAILABLE = False
    print("⚠️ EndpointManager not available")

class EndpointScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_connected = False
        self.endpoint = None
        
        if ENDPOINT_AVAILABLE:
            try:
                self.endpoint = EndpointManager()
            except Exception as e:
                print(f"⚠️ Endpoint init error: {e}")
                self.endpoint = None
        
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Header
        header = BoxLayout(size_hint_y=0.08)
        back = Button(text='< Back', font_size=dp(20), size_hint_x=0.18,
                     background_normal='', background_color=(0.2, 0.2, 0.35, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text='Endpoint Connection', font_size=dp(24), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        layout.add_widget(Widget(size_hint_y=0.02))
        
        # Status
        self.status = Label(text='Status: Disconnected', font_size=dp(18), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.06)
        layout.add_widget(self.status)
        
        # Mode info
        if not ENDPOINT_AVAILABLE:
            info_label = Label(text='⚠️ Endpoint module not available\nRunning in offline mode', 
                              font_size=dp(14), color=(1, 0.8, 0, 1), size_hint_y=0.06)
            layout.add_widget(info_label)
        
        # Connection buttons
        btn_row = BoxLayout(size_hint_y=0.10, spacing=dp(10))
        
        self.connect_btn = Button(text='Connect', font_size=dp(20), 
                                 background_normal='', background_color=(0.2, 0.7, 0.2, 1))
        self.connect_btn.bind(on_release=self.toggle_connect)
        btn_row.add_widget(self.connect_btn)
        
        test_btn = Button(text='Test', font_size=dp(20), 
                         background_normal='', background_color=(0.2, 0.4, 0.8, 1))
        test_btn.bind(on_release=self.test_connection)
        btn_row.add_widget(test_btn)
        
        layout.add_widget(btn_row)
        
        layout.add_widget(Widget(size_hint_y=0.02))
        
        # Login section
        login_box = BoxLayout(orientation='vertical', size_hint_y=0.32, spacing=dp(8))
        login_box.add_widget(Label(text='Login to Server', font_size=dp(18), color=(1, 1, 0.6, 1), size_hint_y=0.15))
        
        self.username_input = TextInput(hint_text='Username', font_size=dp(18), multiline=False,
                                       background_color=(0.15, 0.15, 0.25, 1), foreground_color=(1, 1, 1, 1),
                                       size_hint_y=0.25)
        login_box.add_widget(self.username_input)
        
        self.password_input = TextInput(hint_text='Password', font_size=dp(18), multiline=False, password=True,
                                       background_color=(0.15, 0.15, 0.25, 1), foreground_color=(1, 1, 1, 1),
                                       size_hint_y=0.25)
        login_box.add_widget(self.password_input)
        
        login_btn = Button(text='Login', font_size=dp(20), size_hint_y=0.30,
                          background_normal='', background_color=(0.97, 0.59, 0.12, 1))
        login_btn.bind(on_release=self.do_login)
        login_box.add_widget(login_btn)
        
        layout.add_widget(login_box)
        
        layout.add_widget(Widget(size_hint_y=0.02))
        
        # Info
        info = Label(text='Sync your game data with cloud server', 
                    font_size=dp(14), color=(0.5, 0.5, 0.5, 1), halign='center', size_hint_y=0.06)
        layout.add_widget(info)
        
        self.add_widget(layout)
        
    def toggle_connect(self, instance):
        if self.is_connected:
            self.is_connected = False
            if self.endpoint:
                try:
                    self.endpoint.stop_ping()
                except:
                    pass
            self.status.text = 'Status: Disconnected'
            self.status.color = (0.7, 0.7, 0.7, 1)
            self.connect_btn.text = 'Connect'
            self.connect_btn.background_color = (0.2, 0.7, 0.2, 1)
        else:
            self.do_connect()
            
    def do_connect(self):
        if not self.endpoint:
            self.status.text = 'Status: Offline Mode'
            self.status.color = (1, 0.8, 0, 1)
            self.connect_btn.text = 'Disconnect'
            self.connect_btn.background_color = (0.8, 0.2, 0.2, 1)
            self.is_connected = True
            
            popup = Popup(title='Offline Mode', 
                        content=Label(text='Running in offline mode\nData will be stored locally', font_size=dp(16)),
                        size_hint=(0.75, 0.3))
            popup.open()
            return
            
        try:
            success = self.endpoint.connect()
            if success:
                self.is_connected = True
                self.status.text = 'Status: Connected'
                self.status.color = (0.2, 0.8, 0.2, 1)
                self.connect_btn.text = 'Disconnect'
                self.connect_btn.background_color = (0.8, 0.2, 0.2, 1)
                self.endpoint.start_ping()
                
                popup = Popup(title='Connected', 
                            content=Label(text='Successfully connected to endpoint server!', font_size=dp(16)),
                            size_hint=(0.75, 0.3))
                popup.open()
            else:
                self.status.text = 'Connection failed - Using offline mode'
                self.status.color = (1, 0.8, 0, 1)
                self.is_connected = True
                self.connect_btn.text = 'Disconnect'
                self.connect_btn.background_color = (0.8, 0.2, 0.2, 1)
        except Exception as e:
            self.status.text = f'Error: {str(e)[:30]}'
            self.status.color = (0.8, 0.2, 0.2, 1)
            
    def test_connection(self, instance):
        if not self.is_connected:
            popup = Popup(title='Not Connected', 
                        content=Label(text='Please connect first!', font_size=dp(16)),
                        size_hint=(0.7, 0.3))
            popup.open()
            return
            
        if self.endpoint:
            try:
                items = self.endpoint.get_shop_items(force_refresh=True)
                popup = Popup(title='Test Result', 
                            content=Label(text=f'Items loaded: {len(items)}', font_size=dp(16)),
                            size_hint=(0.7, 0.3))
                popup.open()
            except Exception as e:
                popup = Popup(title='Test Error', 
                            content=Label(text=f'Error: {str(e)[:40]}', font_size=dp(14)),
                            size_hint=(0.7, 0.3))
                popup.open()
        else:
            popup = Popup(title='Test Result', 
                        content=Label(text='Items loaded: 10 (offline mode)', font_size=dp(16)),
                        size_hint=(0.7, 0.3))
            popup.open()
            
    def do_login(self, instance):
        if not self.endpoint:
            # حالت آفلاین
            username = self.username_input.text.strip()
            if username:
                popup = Popup(title='Login Successful (Offline)', 
                            content=Label(text=f'Welcome {username}!', font_size=dp(16)),
                            size_hint=(0.7, 0.3))
                popup.open()
            else:
                popup = Popup(title='Error', 
                            content=Label(text='Please enter username!', font_size=dp(16)),
                            size_hint=(0.7, 0.3))
                popup.open()
            return
            
        if not self.is_connected:
            popup = Popup(title='Not Connected', 
                        content=Label(text='Please connect first!', font_size=dp(16)),
                        size_hint=(0.7, 0.3))
            popup.open()
            return
            
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            popup = Popup(title='Error', 
                        content=Label(text='Please enter username and password!', font_size=dp(16)),
                        size_hint=(0.7, 0.3))
            popup.open()
            return
            
        try:
            result = self.endpoint.login(username, password)
            if result:
                popup = Popup(title='Login Successful', 
                            content=Label(text=f'Welcome {username}!', font_size=dp(16)),
                            size_hint=(0.7, 0.3))
                popup.open()
            else:
                popup = Popup(title='Login Failed', 
                            content=Label(text='Invalid username or password', font_size=dp(16)),
                            size_hint=(0.7, 0.3))
                popup.open()
        except Exception as e:
            popup = Popup(title='Login Error', 
                        content=Label(text=f'Error: {str(e)[:40]}', font_size=dp(14)),
                        size_hint=(0.7, 0.3))
            popup.open()