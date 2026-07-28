# © 2025 AmirAli Kamrani. All rights reserved.

# ui/profile.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        header = BoxLayout(size_hint_y=0.06)
        back = Button(text='< Back', font_size=dp(18), size_hint_x=0.2,
                     background_normal='', background_color=(0.2, 0.2, 0.35, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text='👤 Profile', font_size=dp(24), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        layout.add_widget(Widget(size_hint_y=0.02))
        layout.add_widget(Label(text='👤', font_size=dp(60)))
        layout.add_widget(Label(text='Username: Guest', font_size=dp(22), color=(1, 1, 1, 1), bold=True))
        layout.add_widget(Label(text='⭐ Rating: 1200', font_size=dp(18), color=(1, 1, 0.6, 1)))
        layout.add_widget(Label(text='🏅 Rank: Beginner', font_size=dp(16), color=(0.7, 0.7, 0.7, 1)))
        
        stats = GridLayout(cols=4, spacing=dp(10), size_hint_y=0.2)
        for label, value in [('Games', '0'), ('Wins', '0'), ('Losses', '0'), ('Draws', '0')]:
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text=value, font_size=dp(24), color=(1, 1, 0.6, 1)))
            box.add_widget(Label(text=label, font_size=dp(12), color=(0.5, 0.5, 0.5, 1)))
            stats.add_widget(box)
        layout.add_widget(stats)
        
        layout.add_widget(Label(text='💰 Coins: 0', font_size=dp(20), color=(1, 1, 0.6, 1), size_hint_y=0.06))
        layout.add_widget(Widget(size_hint_y=0.02))
        
        logout = Button(text='🚪 Logout', font_size=dp(18), size_hint_y=None, height=dp(45),
                       background_normal='', background_color=(0.6, 0.1, 0.1, 1))
        logout.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(logout)
        
        self.add_widget(layout)