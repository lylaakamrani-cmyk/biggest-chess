# © 2025 AmirAli Kamrani. All rights reserved.

# ui/settings.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.core.window import Window
import json
import os

CONFIG_PATH = '/storage/emulated/0/Biggest_chess/data/config.json'

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.load_settings()
        self.options = {
            'board_theme': ['Classic', 'Dark', 'Neon', 'Blue', 'Green', 'Wood', 'Marble'],
            'piece_theme': ['Classic', 'Modern', 'Wood', 'Gold', 'Marble', 'Crystal'],
            'sound': ['On', 'Off'],
            'volume': ['0%', '25%', '50%', '70%', '100%'],
            'ai_level': ['Beginner', 'Easy', 'Medium', 'Hard', 'Expert', 'Master'],
            'time_control': ['1+0', '3+0', '5+0', '10+0', '15+10', '30+0'],
            'dark_mode': ['Off', 'On'],  # حالت شب
            'animations': ['On', 'Off'],
            'language': ['English', 'Persian', 'Turkish', 'Arabic', 'Russian'],
            'show_timer': ['On', 'Off'],
            'auto_promote': ['On', 'Off'],
            'sound_effects': ['On', 'Off']
        }
        self.value_widgets = {}
        self.build_ui()
        
    def load_settings(self):
        default = {
            'board_theme': 'Classic',
            'piece_theme': 'Classic',
            'sound': 'On',
            'volume': '70%',
            'ai_level': 'Medium',
            'time_control': '10+0',
            'dark_mode': 'Off',
            'animations': 'On',
            'language': 'English',
            'show_timer': 'On',
            'auto_promote': 'On',
            'sound_effects': 'On'
        }
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    data = json.load(f)
                    if 'settings' in data:
                        return {**default, **data['settings']}
            except:
                pass
        return default
        
    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump({'settings': self.settings}, f, indent=2)
            
            # اعمال حالت شب
            self.apply_dark_mode()
            return True
        except:
            return False

    def apply_dark_mode(self):
        """اعمال حالت شب به کل برنامه"""
        is_dark = self.settings.get('dark_mode', 'Off') == 'On'
        if is_dark:
            Window.clearcolor = (0.05, 0.05, 0.1, 1)
            # تنظیمات بیشتر برای حالت شب
        else:
            Window.clearcolor = (0.08, 0.08, 0.15, 1)

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        
        # Header
        header = BoxLayout(size_hint_y=0.06)
        back = Button(text='< Back', font_size=dp(18), size_hint_x=0.15,
                     background_normal='', background_color=(0.2, 0.2, 0.35, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text='Settings', font_size=dp(24), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Scrollable settings
        scroll = ScrollView(size_hint_y=0.82)
        self.grid = GridLayout(cols=1, spacing=dp(3), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.value_widgets = {}
        
        groups = [
            ('Appearance', ['board_theme', 'piece_theme', 'dark_mode']),
            ('Sound', ['sound', 'sound_effects', 'volume']),
            ('Game', ['ai_level', 'time_control', 'auto_promote', 'show_timer']),
            ('Language', ['language']),
            ('Other', ['animations'])
        ]
        
        for group_name, keys in groups:
            self.grid.add_widget(Label(text=group_name, font_size=dp(16), color=(1, 1, 0.6, 1),
                                      bold=True, size_hint_y=None, height=dp(28)))
            
            for key in keys:
                row = BoxLayout(size_hint_y=None, height=dp(38))
                label = key.replace('_', ' ').title()
                row.add_widget(Label(text=label, font_size=dp(14), color=(0.8, 0.8, 0.8, 1), size_hint_x=0.4))
                
                btn_box = BoxLayout(size_hint_x=0.6, spacing=dp(2))
                
                left = Button(text='<', font_size=dp(16), size_hint_x=0.15,
                             background_normal='', background_color=(0.3, 0.3, 0.5, 1))
                left.bind(on_release=lambda x, k=key: self.change_value(k, -1))
                
                val = Label(text=self.settings.get(key, ''), font_size=dp(14), 
                           color=(1, 1, 0.6, 1), size_hint_x=0.7)
                self.value_widgets[key] = val
                
                right = Button(text='>', font_size=dp(16), size_hint_x=0.15,
                              background_normal='', background_color=(0.3, 0.3, 0.5, 1))
                right.bind(on_release=lambda x, k=key: self.change_value(k, 1))
                
                btn_box.add_widget(left)
                btn_box.add_widget(val)
                btn_box.add_widget(right)
                
                row.add_widget(btn_box)
                self.grid.add_widget(row)
                
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        
        save = Button(text='Save Settings', font_size=dp(18), size_hint_y=0.07,
                     background_normal='', background_color=(0.97, 0.59, 0.12, 1))
        save.bind(on_release=self.save_and_confirm)
        layout.add_widget(save)
        
        self.add_widget(layout)
        # اعمال حالت شب هنگام باز شدن
        self.apply_dark_mode()

    def change_value(self, key, direction):
        opts = self.options.get(key, [])
        if not opts:
            return
        current = self.settings.get(key, opts[0])
        try:
            idx = opts.index(current)
            new_idx = (idx + direction) % len(opts)
            new_value = opts[new_idx]
            self.settings[key] = new_value
            
            if key in self.value_widgets:
                self.value_widgets[key].text = new_value
                
            # اگر dark_mode تغییر کرد، سریع اعمال کن
            if key == 'dark_mode':
                self.apply_dark_mode()
        except ValueError:
            self.settings[key] = opts[0]
            if key in self.value_widgets:
                self.value_widgets[key].text = opts[0]

    def save_and_confirm(self, instance):
        if self.save_settings():
            popup = Popup(title='Success', 
                        content=Label(text='Settings saved!', font_size=dp(16)),
                        size_hint=(0.6, 0.25))
            popup.open()
        else:
            popup = Popup(title='Error', 
                        content=Label(text='Failed to save!', font_size=dp(16)),
                        size_hint=(0.6, 0.25))
            popup.open()