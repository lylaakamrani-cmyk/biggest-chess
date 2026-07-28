# © 2025 AmirAli Kamrani. All rights reserved.

# ui/shop.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

class ShopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coins = 1000
        self.owned_items = []
        self.items = [
            {'id': 'theme_classic', 'name': 'Classic Theme', 'price': 0, 'rarity': 'common', 'icon': '🎨'},
            {'id': 'theme_dark', 'name': 'Dark Theme', 'price': 100, 'rarity': 'common', 'icon': '🌙'},
            {'id': 'theme_neon', 'name': 'Neon Theme', 'price': 200, 'rarity': 'rare', 'icon': '💡'},
            {'id': 'theme_blue', 'name': 'Blue Theme', 'price': 150, 'rarity': 'uncommon', 'icon': '🔵'},
            {'id': 'theme_green', 'name': 'Green Theme', 'price': 150, 'rarity': 'uncommon', 'icon': '🟢'},
            {'id': 'piece_modern', 'name': 'Modern Pieces', 'price': 150, 'rarity': 'uncommon', 'icon': '♞'},
            {'id': 'piece_wood', 'name': 'Wood Pieces', 'price': 200, 'rarity': 'rare', 'icon': '♝'},
            {'id': 'piece_gold', 'name': 'Gold Pieces', 'price': 500, 'rarity': 'legendary', 'icon': '✨'},
            {'id': 'piece_marble', 'name': 'Marble Pieces', 'price': 300, 'rarity': 'epic', 'icon': '💎'},
            {'id': 'sound_epic', 'name': 'Epic Sounds', 'price': 150, 'rarity': 'rare', 'icon': '🔊'},
            {'id': 'bg_gradient', 'name': 'Gradient BG', 'price': 75, 'rarity': 'uncommon', 'icon': '🌈'},
            {'id': 'bg_wooden', 'name': 'Wooden BG', 'price': 50, 'rarity': 'common', 'icon': '🪵'},
        ]
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        
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
        
        title = Label(text='🛒 Shop', font_size=dp(24), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Coins
        self.coins_label = Label(
            text=f'💰 Coins: {self.coins}',
            font_size=dp(18),
            color=(1, 1, 0.6, 1),
            size_hint_y=0.05
        )
        layout.add_widget(self.coins_label)
        
        # Items
        scroll = ScrollView(size_hint_y=0.8)
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for item in self.items:
            widget = self.create_item_widget(item)
            grid.add_widget(widget)
            
        scroll.add_widget(grid)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
    def create_item_widget(self, item):
        is_owned = item['id'] in self.owned_items
        
        rarity_colors = {
            'common': (0.5, 0.5, 0.5, 1),
            'uncommon': (0.2, 0.7, 0.2, 1),
            'rare': (0.2, 0.4, 0.8, 1),
            'epic': (0.6, 0.2, 0.8, 1),
            'legendary': (1, 0.8, 0, 1)
        }
        
        box = BoxLayout(
            orientation='vertical',
            padding=dp(8),
            spacing=dp(4),
            size_hint_y=None,
            height=dp(130)
        )
        
        with box.canvas.before:
            Color(*rarity_colors.get(item['rarity'], (0.2, 0.2, 0.35, 1)))
            rect = RoundedRectangle(size=box.size, pos=box.pos, radius=[dp(8)])
            box.bind(size=lambda i, v: setattr(rect, 'size', v))
            box.bind(pos=lambda i, v: setattr(rect, 'pos', v))
        
        # Icon
        box.add_widget(Label(text=item['icon'], font_size=dp(28), size_hint_y=0.3))
        
        # Name
        box.add_widget(Label(text=item['name'], font_size=dp(14), color=(1, 1, 1, 1), size_hint_y=0.25))
        
        # Price
        price_text = 'Free' if item['price'] == 0 else f'{item["price"]}💰'
        box.add_widget(Label(text=price_text, font_size=dp(12), color=(1, 1, 0.6, 1), size_hint_y=0.2))
        
        # Button
        btn_text = '✅ Owned' if is_owned else '🛒 Buy'
        btn = Button(
            text=btn_text,
            font_size=dp(12),
            size_hint_y=0.25,
            background_normal='',
            background_color=(0.1, 0.6, 0.1, 1) if is_owned else (0.97, 0.59, 0.12, 1)
        )
        if not is_owned:
            btn.bind(on_release=lambda x, i=item: self.buy_item(i))
        box.add_widget(btn)
        
        return box
        
    def buy_item(self, item):
        if self.coins >= item['price']:
            self.coins -= item['price']
            self.owned_items.append(item['id'])
            self.coins_label.text = f'💰 Coins: {self.coins}'
            
            content = Label(text=f'✅ Purchased {item["name"]}!', font_size=dp(16))
            popup = Popup(title='Success', content=content, size_hint=(0.7, 0.3))
            popup.open()
            
            self.build_ui()
        else:
            content = Label(text='❌ Not enough coins!', font_size=dp(16))
            popup = Popup(title='Error', content=content, size_hint=(0.7, 0.3))
            popup.open()