# © 2025 AmirAli Kamrani. All rights reserved.

# ui/home.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.app import App

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        # Layout اصلی
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        
        # Title
        title = Label(text='♟ Chess Master Pro', font_size=dp(32), color=(1, 1, 0.6, 1), bold=True)
        main_layout.add_widget(title)
        
        subtitle = Label(text='Professional Chess Game', font_size=dp(16), color=(0.7, 0.7, 0.7, 1))
        main_layout.add_widget(subtitle)
        
        main_layout.add_widget(Widget(size_hint_y=0.05))
        
        # Menu
        menu = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.55)
        
# اضافه کردن دکمه Tutorial به منو
menu_items = [
    ('Local Game', 'local'),
    ('VS AI', 'ai'),
    ('Online Game', 'online'),
    ('Tournament', 'tournament'),
    ('Analysis', 'analysis'),
    ('Tutorial', 'tutorial'),  # <-- اضافه شد
    ('Profile', 'profile'),
    ('Shop', 'shop'),
    ('Settings', 'settings')
]
        
        for text, screen in menu_items:
            btn = Button(
                text=text,
                font_size=dp(18),
                size_hint_y=None,
                height=dp(55),
                background_normal='',
                background_color=(0.2, 0.2, 0.35, 1)
            )
            btn.bind(on_release=lambda x, s=screen: setattr(self.manager, 'current', s))
            menu.add_widget(btn)
            
        main_layout.add_widget(menu)
        
        # فضای کشسان برای هل دادن به پایین
        main_layout.add_widget(Widget(size_hint_y=1))
        
        # باکس مخصوص دکمه Exit و Status (برای چسباندن به پایین)
        bottom_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70), spacing=dp(5))
        
        # Status - بالای دکمه Exit
        status = Label(text='Status: Ready', font_size=dp(12), color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(20))
        bottom_box.add_widget(status)
        
        # Exit - در پایین‌ترین نقطه
        exit_btn = Button(
            text='🚪 Exit',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_color=(0.6, 0.1, 0.1, 1)
        )
        exit_btn.bind(on_release=lambda x: App.get_running_app().stop())
        bottom_box.add_widget(exit_btn)
        
        main_layout.add_widget(bottom_box)
        
        self.add_widget(main_layout)
