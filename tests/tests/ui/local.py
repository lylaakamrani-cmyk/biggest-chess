# © 2025 AmirAli Kamrani. All rights reserved.

# ui/local.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp

class LocalScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Header
        header = BoxLayout(size_hint_y=0.07)
        back = Button(
            text='< Back',
            font_size=dp(18),
            size_hint_x=0.2,
            background_normal='',
            background_color=(0.2, 0.2, 0.35, 1)
        )
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        
        title = Label(text='🎮 Local Game', font_size=dp(24), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        layout.add_widget(Widget(size_hint_y=0.1))
        
        # Info
        info = Label(
            text='Play against another player on the same device',
            font_size=dp(16),
            color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(info)
        
        layout.add_widget(Widget(size_hint_y=0.05))
        
        # Time control
        time_row = BoxLayout(size_hint_y=None, height=dp(40))
        time_row.add_widget(Label(text='⏱️ Time Control:', font_size=dp(16), color=(0.8, 0.8, 0.8, 1), size_hint_x=0.5))
        time_row.add_widget(Label(text='10+0', font_size=dp(16), color=(1, 1, 0.6, 1), size_hint_x=0.5))
        layout.add_widget(time_row)
        
        layout.add_widget(Widget(size_hint_y=0.05))
        
        # Start button
        start = Button(
            text='▶ Start Game',
            font_size=dp(22),
            size_hint_y=None,
            height=dp(55),
            background_normal='',
            background_color=(0.97, 0.59, 0.12, 1)
        )
        start.bind(on_release=lambda x: setattr(self.manager, 'current', 'board'))
        layout.add_widget(start)
        
        self.add_widget(layout)