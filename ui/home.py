# © 2025 AmirAli Kamrani. All rights reserved.

# ui/home.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(4))
        
        # Title (کوچک‌تر)
        title = Label(text='Chess Master Pro', font_size=dp(24), color=(1, 1, 0.6, 1), bold=True, size_hint_y=0.06)
        layout.add_widget(title)
        
        subtitle = Label(text='Professional Chess Game', font_size=dp(12), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.04)
        layout.add_widget(subtitle)
        
        # فاصله کمتر
        layout.add_widget(Widget(size_hint_y=0.01))
        
        # منو (بزرگتر و بالاتر)
        menu = GridLayout(cols=2, spacing=dp(8), size_hint_y=0.72)
        
        items = [
            ('Local', 'local'),
            ('VS AI', 'ai'),
            ('Online', 'online'),
            ('Tournament', 'tournament'),
            ('Analysis', 'analysis'),
            ('Profile', 'profile'),
            ('Shop', 'shop'),
            ('Settings', 'settings'),
            ('Endpoint', 'endpoint'),
        ]
        
        for text, screen in items:
            btn = Button(text=text, font_size=dp(18), size_hint_y=None, height=dp(52),
                        background_normal='', background_color=(0.2, 0.2, 0.35, 1))
            btn.bind(on_release=lambda x, s=screen: setattr(self.manager, 'current', s))
            menu.add_widget(btn)
            
        layout.add_widget(menu)
        
        # فاصله کمتر تا Exit
        layout.add_widget(Widget(size_hint_y=0.03))
        
        exit_btn = Button(text='Exit', font_size=dp(18), size_hint_y=None, height=dp(38),
                         background_normal='', background_color=(0.6, 0.1, 0.1, 1))
        exit_btn.bind(on_release=lambda x: App.get_running_app().stop())
        layout.add_widget(exit_btn)
        
        self.add_widget(layout)