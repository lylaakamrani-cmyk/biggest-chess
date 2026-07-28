# © 2025 AmirAli Kamrani. All rights reserved.

# ui/login.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))
        
        # Back button
        back = Button(
            text='< Back',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_color=(0.2, 0.2, 0.35, 1)
        )
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back)
        
        layout.add_widget(Widget(size_hint_y=0.1))
        
        # Title
        title = Label(text='🔐 Login', font_size=dp(32), color=(1, 1, 1, 1), bold=True)
        layout.add_widget(title)
        
        subtitle = Label(text='Sign in to your account', font_size=dp(16), color=(0.7, 0.7, 0.7, 1))
        layout.add_widget(subtitle)
        
        layout.add_widget(Widget(size_hint_y=0.05))
        
        # Username
        self.username = TextInput(
            hint_text='Username',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(50),
            background_color=(0.15, 0.15, 0.25, 1),
            foreground_color=(1, 1, 1, 1)
        )
        layout.add_widget(self.username)
        
        # Password
        self.password = TextInput(
            hint_text='Password',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(50),
            password=True,
            background_color=(0.15, 0.15, 0.25, 1),
            foreground_color=(1, 1, 1, 1)
        )
        layout.add_widget(self.password)
        
        layout.add_widget(Widget(size_hint_y=0.05))
        
        # Login button
        login_btn = Button(
            text='Login',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.97, 0.59, 0.12, 1)
        )
        login_btn.bind(on_release=self.do_login)
        layout.add_widget(login_btn)
        
        # Register button
        register_btn = Button(
            text='Create Account',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_color=(0.2, 0.2, 0.35, 1)
        )
        register_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'register'))
        layout.add_widget(register_btn)
        
        # Status
        self.status = Label(text='', font_size=dp(14), color=(0.8, 0.2, 0.2, 1))
        layout.add_widget(self.status)
        
        self.add_widget(layout)
        
    def do_login(self, instance):
        username = self.username.text
        password = self.password.text
        
        if not username or not password:
            self.status.text = 'Please enter username and password'
            return
            
        # بررسی ساده (در نسخه واقعی از دیتابیس استفاده می‌شود)
        if username == 'admin' and password == 'admin':
            self.status.text = '✅ Login successful!'
            self.status.color = (0.2, 0.8, 0.2, 1)
            # ذخیره کاربر
            self.manager.app.current_user = {'username': username, 'rating': 1500}
            setattr(self.manager, 'current', 'home')
        else:
            self.status.text = '❌ Invalid username or password'
            self.status.color = (0.8, 0.2, 0.2, 1)