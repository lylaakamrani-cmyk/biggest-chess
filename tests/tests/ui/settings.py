# © 2025 AmirAli Kamrani. All rights reserved.

# ui/settings.py
import os
import json
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.metrics import dp

CONFIG_PATH = '/storage/emulated/0/Biggest_chess/data/config.json'

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.load_settings()
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
            'animations': 'On'
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
            data = {'settings': self.settings}
            with open(CONFIG_PATH, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        
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
        
        title = Label(text='⚙️ Settings', font_size=dp(24), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        layout.add_widget(Widget(size_hint_y=0.02))
        
        # Settings groups
        groups = [
            ('🎨 Appearance', [
                ('Board Theme', 'board_theme'),
                ('Piece Theme', 'piece_theme'),
                ('Dark Mode', 'dark_mode')
            ]),
            ('🔊 Sound', [
                ('Sound', 'sound'),
                ('Volume', 'volume')
            ]),
            ('🎮 Game', [
                ('AI Level', 'ai_level'),
                ('Time Control', 'time_control'),
                ('Animations', 'animations')
            ])
        ]
        
        scroll = ScrollView(size_hint_y=0.75)
        grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for group_name, items in groups:
            # Group header
            header_label = Label(
                text=group_name,
                font_size=dp(18),
                color=(1, 1, 0.6, 1),
                bold=True,
                size_hint_y=None,
                height=dp(30)
            )
            grid.add_widget(header_label)
            
            for label_text, key in items:
                row = BoxLayout(size_hint_y=None, height=dp(40))
                row.add_widget(Label(
                    text=label_text,
                    font_size=dp(15),
                    color=(0.8, 0.8, 0.8, 1),
                    size_hint_x=0.5
                ))
                
                # Value with left/right buttons
                btn_box = BoxLayout(size_hint_x=0.5, spacing=dp(2))
                
                left = Button(text='◀', font_size=dp(14), size_hint_x=0.2,
                             background_normal='', background_color=(0.3, 0.3, 0.5, 1))
                left.bind(on_release=lambda x, k=key: self.change_value(k, -1))
                
                value = Label(
                    text=self.settings.get(key, ''),
                    font_size=dp(15),
                    color=(1, 1, 0.6, 1),
                    size_hint_x=0.6
                )
                
                right = Button(text='▶', font_size=dp(14), size_hint_x=0.2,
                              background_normal='', background_color=(0.3, 0.3, 0.5, 1))
                right.bind(on_release=lambda x, k=key: self.change_value(k, 1))
                
                btn_box.add_widget(left)
                btn_box.add_widget(value)
                btn_box.add_widget(right)
                
                row.add_widget(btn_box)
                grid.add_widget(row)
                
            grid.add_widget(Widget(size_hint_y=None, height=dp(5)))
            
        scroll.add_widget(grid)
        layout.add_widget(scroll)
        
        # Save button
        save = Button(
            text='💾 Save Settings',
            font_size=dp(20),
            size_hint_y=0.07,
            background_normal='',
            background_color=(0.97, 0.59, 0.12, 1)
        )
        save.bind(on_release=self.save_and_confirm)
        layout.add_widget(save)
        
        self.add_widget(layout)
        
    def change_value(self, key, direction):
        options = {
            'board_theme': ['Classic', 'Dark', 'Neon', 'Blue', 'Green', 'Wood'],
            'piece_theme': ['Classic', 'Modern', 'Wood', 'Gold', 'Marble'],
            'sound': ['On', 'Off'],
            'volume': ['0%', '25%', '50%', '70%', '100%'],
            'ai_level': ['Beginner', 'Easy', 'Medium', 'Hard', 'Expert', 'Master'],
            'time_control': ['1+0', '3+0', '5+0', '10+0', '15+10', '30+0'],
            'dark_mode': ['Off', 'On'],
            'animations': ['On', 'Off']
        }
        
        opts = options.get(key, [])
        if not opts:
            return
            
        current = self.settings.get(key, opts[0])
        try:
            idx = opts.index(current)
            new_idx = (idx + direction) % len(opts)
            self.settings[key] = opts[new_idx]
            self.build_ui()
        except ValueError:
            self.settings[key] = opts[0]
            self.build_ui()
        
    def save_and_confirm(self, instance):
        if self.save_settings():
            content = Label(text='✅ Settings saved successfully!', font_size=dp(18))
            popup = Popup(title='Success', content=content, size_hint=(0.7, 0.3))
            popup.open()
        else:
            content = Label(text='❌ Failed to save settings!', font_size=dp(18))
            popup = Popup(title='Error', content=content, size_hint=(0.7, 0.3))
            popup.open()