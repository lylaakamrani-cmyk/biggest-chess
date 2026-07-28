# © 2025 AmirAli Kamrani. All rights reserved.

# ui/shop.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import sys
import os
import webbrowser
import json
import time
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.payment import PaymentManager

class ShopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment = PaymentManager()
        self.user_id = 'user_001'
        
        # بارگذاری اطلاعات کاربر
        self.user_data = self.payment.get_user_data(self.user_id)
        self.is_premium = self.payment.check_subscription(self.user_id)
        self.coins = self.user_data.get('coins', 0)
        self.owned_items = self.user_data.get('owned_items', [])
        
        # وضعیت تب
        self.current_tab = 'coins'
        
        # آیتم‌های فروشگاه
        self.shop_items = self.get_shop_items()
        
        self.build_ui()
        
    def get_shop_items(self):
        """لیست آیتم‌های فروشگاه"""
        return [
            # ====== تم‌های صفحه (Board Themes) ======
            {'id': 'theme_classic', 'name': 'Classic Theme', 'price': 0, 'rarity': 'common', 'icon': '🎨', 'category': 'theme', 'type': 'board', 'desc': 'Classic wooden board'},
            {'id': 'theme_dark', 'name': 'Dark Theme', 'price': 150, 'rarity': 'common', 'icon': '🌙', 'category': 'theme', 'type': 'board', 'desc': 'Dark elegant board'},
            {'id': 'theme_neon', 'name': 'Neon Theme', 'price': 300, 'rarity': 'rare', 'icon': '💡', 'category': 'theme', 'type': 'board', 'desc': 'Neon glowing board'},
            {'id': 'theme_blue', 'name': 'Blue Theme', 'price': 200, 'rarity': 'uncommon', 'icon': '🔵', 'category': 'theme', 'type': 'board', 'desc': 'Blue ocean board'},
            {'id': 'theme_green', 'name': 'Green Theme', 'price': 200, 'rarity': 'uncommon', 'icon': '🟢', 'category': 'theme', 'type': 'board', 'desc': 'Green nature board'},
            {'id': 'theme_wood', 'name': 'Wood Theme', 'price': 250, 'rarity': 'rare', 'icon': '🪵', 'category': 'theme', 'type': 'board', 'desc': 'Premium wood board'},
            {'id': 'theme_marble', 'name': 'Marble Theme', 'price': 400, 'rarity': 'epic', 'icon': '🏛️', 'category': 'theme', 'type': 'board', 'desc': 'Luxury marble board'},
            
            # ====== مهره‌ها (Pieces) ======
            {'id': 'piece_classic', 'name': 'Classic Pieces', 'price': 0, 'rarity': 'common', 'icon': '♟️', 'category': 'piece', 'type': 'pieces', 'desc': 'Standard chess pieces'},
            {'id': 'piece_modern', 'name': 'Modern Pieces', 'price': 200, 'rarity': 'uncommon', 'icon': '♞', 'category': 'piece', 'type': 'pieces', 'desc': 'Modern design pieces'},
            {'id': 'piece_wood', 'name': 'Wood Pieces', 'price': 300, 'rarity': 'rare', 'icon': '♝', 'category': 'piece', 'type': 'pieces', 'desc': 'Handcrafted wood pieces'},
            {'id': 'piece_marble', 'name': 'Marble Pieces', 'price': 450, 'rarity': 'epic', 'icon': '♛', 'category': 'piece', 'type': 'pieces', 'desc': 'Luxury marble pieces'},
            {'id': 'piece_gold', 'name': 'Gold Pieces', 'price': 600, 'rarity': 'legendary', 'icon': '👑', 'category': 'piece', 'type': 'pieces', 'desc': '24K Gold plated pieces'},
            {'id': 'piece_crystal', 'name': 'Crystal Pieces', 'price': 500, 'rarity': 'epic', 'icon': '💎', 'category': 'piece', 'type': 'pieces', 'desc': 'Crystal clear pieces'},
            
            # ====== صداها (Sounds) ======
            {'id': 'sound_classic', 'name': 'Classic Sounds', 'price': 0, 'rarity': 'common', 'icon': '🔊', 'category': 'sound', 'type': 'audio', 'desc': 'Traditional chess sounds'},
            {'id': 'sound_modern', 'name': 'Modern Sounds', 'price': 150, 'rarity': 'uncommon', 'icon': '🎵', 'category': 'sound', 'type': 'audio', 'desc': 'Modern digital sounds'},
            {'id': 'sound_epic', 'name': 'Epic Sounds', 'price': 300, 'rarity': 'rare', 'icon': '🎼', 'category': 'sound', 'type': 'audio', 'desc': 'Epic cinematic sounds'},
            {'id': 'sound_peaceful', 'name': 'Peaceful Sounds', 'price': 200, 'rarity': 'uncommon', 'icon': '🌿', 'category': 'sound', 'type': 'audio', 'desc': 'Calm and relaxing sounds'},
            
            # ====== پس‌زمینه‌ها (Backgrounds) ======
            {'id': 'bg_wooden', 'name': 'Wooden BG', 'price': 100, 'rarity': 'common', 'icon': '🪵', 'category': 'bg', 'type': 'background', 'desc': 'Warm wood background'},
            {'id': 'bg_dark', 'name': 'Dark BG', 'price': 100, 'rarity': 'common', 'icon': '🌑', 'category': 'bg', 'type': 'background', 'desc': 'Sleek dark background'},
            {'id': 'bg_gradient', 'name': 'Gradient BG', 'price': 150, 'rarity': 'uncommon', 'icon': '🌈', 'category': 'bg', 'type': 'background', 'desc': 'Colorful gradient'},
            {'id': 'bg_stars', 'name': 'Star BG', 'price': 250, 'rarity': 'rare', 'icon': '⭐', 'category': 'bg', 'type': 'background', 'desc': 'Night sky with stars'},
            {'id': 'bg_chess', 'name': 'Chess Pattern', 'price': 120, 'rarity': 'common', 'icon': '♟️', 'category': 'bg', 'type': 'background', 'desc': 'Classic chess pattern'},
            
            # ====== آیکون‌ها (Icons) ======
            {'id': 'icon_classic', 'name': 'Classic Icons', 'price': 0, 'rarity': 'common', 'icon': '🎯', 'category': 'icon', 'type': 'ui', 'desc': 'Standard UI icons'},
            {'id': 'icon_modern', 'name': 'Modern Icons', 'price': 150, 'rarity': 'uncommon', 'icon': '✨', 'category': 'icon', 'type': 'ui', 'desc': 'Modern UI icons'},
            {'id': 'icon_gold', 'name': 'Gold Icons', 'price': 350, 'rarity': 'rare', 'icon': '🌟', 'category': 'icon', 'type': 'ui', 'desc': 'Gold plated icons'},
            
            # ====== موارد ویژه (Special) ======
            {'id': 'unlimited_undo', 'name': 'Unlimited Undo', 'price': 500, 'rarity': 'legendary', 'icon': '♾️', 'category': 'special', 'type': 'feature', 'desc': 'Unlimited undo moves'},
            {'id': 'ai_coach', 'name': 'AI Coach', 'price': 400, 'rarity': 'epic', 'icon': '🧠', 'category': 'special', 'type': 'feature', 'desc': 'AI powered game analysis'},
            {'id': 'premium_stats', 'name': 'Premium Stats', 'price': 300, 'rarity': 'rare', 'icon': '📊', 'category': 'special', 'type': 'feature', 'desc': 'Advanced game statistics'},
        ]
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6))
        
        # ====== HEADER ======
        header = BoxLayout(size_hint_y=0.06)
        back = Button(text='< Back', font_size=dp(18), size_hint_x=0.2,
                     background_normal='', background_color=(0.2, 0.2, 0.35, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text='💰 Shop', font_size=dp(24), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        # ====== USER INFO ======
        info = BoxLayout(size_hint_y=0.06, spacing=dp(10))
        self.coins_label = Label(text=f'🪙 {self.coins} coins', 
                                font_size=dp(18), color=(1, 1, 0.6, 1))
        info.add_widget(self.coins_label)
        
        status_text = '👑 Premium' if self.is_premium else '📄 Free'
        status_color = (1, 1, 0.6, 1) if self.is_premium else (0.7, 0.7, 0.7, 1)
        self.status_label = Label(text=status_text, font_size=dp(14), color=status_color)
        info.add_widget(self.status_label)
        layout.add_widget(info)
        
        # ====== TABS ======
        tabs = BoxLayout(size_hint_y=0.06, spacing=dp(4))
        tab_names = [
            ('🪙 Coins', 'coins'),
            ('🎨 Themes', 'theme'),
            ('♟️ Pieces', 'piece'),
            ('🔊 Sounds', 'sound'),
            ('🎁 Free', 'free')
        ]
        self.tab_buttons = []
        for text, tab_id in tab_names:
            btn = Button(text=text, font_size=dp(12), background_normal='',
                        background_color=(0.97, 0.59, 0.12, 1) if tab_id == 'coins' else (0.2, 0.2, 0.35, 1))
            btn.bind(on_release=lambda x, t=tab_id: self.switch_tab(t))
            tabs.add_widget(btn)
            self.tab_buttons.append({'btn': btn, 'id': tab_id})
        layout.add_widget(tabs)
        
        # ====== SCROLLABLE ITEMS ======
        scroll = ScrollView(size_hint_y=0.75)
        self.items_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
        self.items_grid.bind(minimum_height=self.items_grid.setter('height'))
        scroll.add_widget(self.items_grid)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
        # نمایش تب اول
        self.switch_tab('coins')
        
    def switch_tab(self, tab_id):
        """تغییر تب"""
        self.current_tab = tab_id
        
        # آپدیت دکمه‌ها
        for tab in self.tab_buttons:
            tab['btn'].background_color = (0.97, 0.59, 0.12, 1) if tab['id'] == tab_id else (0.2, 0.2, 0.35, 1)
        
        # نمایش آیتم‌های مربوطه
        if tab_id == 'coins':
            self.show_coins_tab()
        elif tab_id == 'free':
            self.show_free_tab()
        else:
            self.show_items_tab(tab_id)
            
    # ==================== COINS TAB ====================
    
    def show_coins_tab(self):
        """نمایش بسته‌های خرید سکه"""
        self.items_grid.clear_widgets()
        
        packages = [
            {'id': 'coins_100', 'name': '100 Coins', 'price_toman': '10,000', 'coins': 100, 'icon': '🪙', 'color': (0.3, 0.5, 0.8, 1)},
            {'id': 'coins_500', 'name': '500 Coins', 'price_toman': '40,000', 'coins': 500, 'icon': '🪙🪙', 'color': (0.2, 0.6, 0.3, 1)},
            {'id': 'coins_1000', 'name': '1000 Coins', 'price_toman': '70,000', 'coins': 1000, 'icon': '🪙🪙🪙', 'color': (0.8, 0.6, 0.2, 1)},
            {'id': 'coins_5000', 'name': '5000 Coins', 'price_toman': '300,000', 'coins': 5000, 'icon': '💎', 'color': (0.6, 0.2, 0.8, 1)},
            {'id': 'coins_10000', 'name': '10000 Coins', 'price_toman': '500,000', 'coins': 10000, 'icon': '👑', 'color': (1, 0.8, 0, 1)},
        ]
        
        for pkg in packages:
            box = self.create_item_box(pkg['color'])
            
            box.add_widget(Label(text=pkg['icon'], font_size=dp(32), size_hint_y=0.2))
            box.add_widget(Label(text=pkg['name'], font_size=dp(15), color=(1, 1, 1, 1), bold=True, size_hint_y=0.15))
            box.add_widget(Label(text=f'{pkg["coins"]} coins', font_size=dp(13), color=(1, 1, 0.6, 1), size_hint_y=0.12))
            
            price_box = BoxLayout(size_hint_y=0.15, spacing=dp(5))
            price_box.add_widget(Label(text=f'💰 {pkg["price_toman"]} T', font_size=dp(12), color=(0.2, 0.8, 0.2, 1)))
            price_box.add_widget(Label(text='💳 Zibal', font_size=dp(10), color=(0.2, 0.6, 0.9, 1)))
            box.add_widget(price_box)
            
            btn = Button(text='Buy Now', font_size=dp(14), size_hint_y=0.2,
                        background_normal='', background_color=(0.97, 0.59, 0.12, 1))
            btn.bind(on_release=lambda x, p=pkg: self.purchase_coins(p))
            box.add_widget(btn)
            
            self.items_grid.add_widget(box)
            
    # ==================== ITEMS TAB ====================
    
    def show_items_tab(self, category):
        """نمایش آیتم‌های دسته‌بندی شده"""
        self.items_grid.clear_widgets()
        
        # فیلتر آیتم‌ها بر اساس دسته
        filtered = [item for item in self.shop_items if item['category'] == category]
        
        if not filtered:
            label = Label(text='No items in this category', font_size=dp(16), color=(0.5, 0.5, 0.5, 1))
            self.items_grid.add_widget(label)
            return
            
        # مرتب‌سازی بر اساس قیمت
        filtered.sort(key=lambda x: x['price'])
        
        for item in filtered:
            is_owned = item['id'] in self.owned_items
            
            rarity_colors = {
                'common': (0.4, 0.4, 0.4, 1),
                'uncommon': (0.2, 0.6, 0.2, 1),
                'rare': (0.2, 0.4, 0.8, 1),
                'epic': (0.6, 0.2, 0.8, 1),
                'legendary': (1, 0.8, 0, 1)
            }
            
            box = self.create_item_box(rarity_colors.get(item['rarity'], (0.2, 0.2, 0.35, 1)))
            
            # Icon و Rarity
            top = BoxLayout(size_hint_y=0.2)
            top.add_widget(Label(text=item['icon'], font_size=dp(28), size_hint_x=0.6))
            top.add_widget(Label(text=item['rarity'][:3].upper(), font_size=dp(10), 
                                color=rarity_colors.get(item['rarity'], (0.5, 0.5, 0.5, 1)), size_hint_x=0.4))
            box.add_widget(top)
            
            # Name
            box.add_widget(Label(text=item['name'], font_size=dp(14), color=(1, 1, 1, 1), bold=True, size_hint_y=0.15))
            
            # Description
            box.add_widget(Label(text=item['desc'][:20] + '...', font_size=dp(10), color=(0.6, 0.6, 0.6, 1), size_hint_y=0.15))
            
            # Price / Owned
            if is_owned:
                box.add_widget(Label(text='✅ Owned', font_size=dp(12), color=(0.2, 0.8, 0.2, 1), size_hint_y=0.12))
            else:
                price_text = 'Free' if item['price'] == 0 else f'{item["price"]} coins'
                box.add_widget(Label(text=price_text, font_size=dp(12), color=(1, 1, 0.6, 1), size_hint_y=0.12))
            
            # Button
            btn_text = 'Owned' if is_owned else 'Buy'
            btn = Button(text=btn_text, font_size=dp(13), size_hint_y=0.2,
                        background_normal='', background_color=(0.1, 0.6, 0.1, 1) if is_owned else (0.97, 0.59, 0.12, 1))
            if not is_owned:
                btn.bind(on_release=lambda x, i=item: self.buy_item(i))
            box.add_widget(btn)
            
            self.items_grid.add_widget(box)
            
    # ==================== FREE TAB ====================
    
    def show_free_tab(self):
        """نمایش آیتم‌های رایگان"""
        self.items_grid.clear_widgets()
        
        free_items = [
            {'id': 'ad_watch', 'name': 'Watch Ad', 'desc': 'Get 5 free coins', 'icon': '📺', 'color': (0.2, 0.4, 0.8, 1)},
            {'id': 'daily_reward', 'name': 'Daily Reward', 'desc': 'Claim 10 free coins daily', 'icon': '🎁', 'color': (0.97, 0.59, 0.12, 1)},
            {'id': 'invite_friend', 'name': 'Invite Friend', 'desc': 'Get 20 coins per invite', 'icon': '👥', 'color': (0.2, 0.7, 0.2, 1)},
        ]
        
        today = time.strftime('%Y-%m-%d')
        daily_claimed = self.user_data.get('daily_claim') == today
        
        for item in free_items:
            box = self.create_item_box(item['color'])
            
            box.add_widget(Label(text=item['icon'], font_size=dp(30), size_hint_y=0.25))
            box.add_widget(Label(text=item['name'], font_size=dp(15), color=(1, 1, 1, 1), bold=True, size_hint_y=0.15))
            box.add_widget(Label(text=item['desc'], font_size=dp(12), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.15))
            
            if item['id'] == 'daily_reward' and daily_claimed:
                btn = Button(text='✅ Claimed Today', font_size=dp(14), size_hint_y=0.25,
                            background_normal='', background_color=(0.1, 0.4, 0.1, 1))
            else:
                btn = Button(text='Claim', font_size=dp(14), size_hint_y=0.25,
                            background_normal='', background_color=(0.2, 0.7, 0.2, 1))
                btn.bind(on_release=lambda x, i=item: self.do_free_action(i))
            box.add_widget(btn)
            
            self.items_grid.add_widget(box)
            
    # ==================== HELPERS ====================
    
    def create_item_box(self, color):
        box = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4), size_hint_y=None, height=dp(160))
        with box.canvas.before:
            Color(*color)
            rect = RoundedRectangle(size=box.size, pos=box.pos, radius=[dp(10)])
            box.bind(size=lambda i, v: setattr(rect, 'size', v))
            box.bind(pos=lambda i, v: setattr(rect, 'pos', v))
        return box
        
    # ==================== ACTIONS ====================
    
    def purchase_coins(self, package):
        """خرید سکه با زیبال (مناسب زیر ۱۸ سال)"""
        # در نسخه واقعی، اینجا به درگاه زیبال متصل میشه
        # برای تست، شبیه‌سازی میکنیم
        popup = Popup(title='💳 Zibal Payment', 
                    content=Label(text=f'Redirecting to Zibal...\n\n{package["name"]}\nPrice: {package["price_toman"]} Toman\n\n🔒 Secure Payment', 
                                 font_size=dp(14)),
                    size_hint=(0.8, 0.4))
        popup.open()
        
        # شبیه‌سازی پرداخت موفق
        Clock.schedule_once(lambda dt: self.simulate_payment_success(package), 2)
        
    def simulate_payment_success(self, package):
        """شبیه‌سازی پرداخت موفق"""
        # اضافه کردن سکه به کاربر
        self.payment.add_coins(self.user_id, package['coins'])
        self.coins = self.payment.get_coins(self.user_id)
        self.coins_label.text = f'🪙 {self.coins} coins'
        
        popup = Popup(title='✅ Payment Successful!', 
                    content=Label(text=f'You got {package["coins"]} coins!\n\nTransaction ID: ZBL-{random.randint(100000, 999999)}', 
                                 font_size=dp(14)),
                    size_hint=(0.8, 0.35))
        popup.open()
        
    def buy_item(self, item):
        """خرید آیتم با سکه"""
        if item['price'] == 0:
            # آیتم رایگان
            if item['id'] not in self.owned_items:
                self.owned_items.append(item['id'])
                self.user_data['owned_items'] = self.owned_items
                self.payment.save_data()
                self.switch_tab(self.current_tab)
                popup = Popup(title='🎉 Free Item!', 
                            content=Label(text=f'You got {item["name"]} for free!', font_size=dp(16)),
                            size_hint=(0.7, 0.3))
                popup.open()
            return
            
        if self.coins >= item['price']:
            # خرید با سکه
            self.payment.spend_coins(self.user_id, item['price'])
            self.coins = self.payment.get_coins(self.user_id)
            self.coins_label.text = f'🪙 {self.coins} coins'
            
            self.owned_items.append(item['id'])
            self.user_data['owned_items'] = self.owned_items
            self.payment.save_data()
            
            self.switch_tab(self.current_tab)
            
            popup = Popup(title='✅ Purchased!', 
                        content=Label(text=f'You got {item["name"]}!\nRarity: {item["rarity"]}', 
                                     font_size=dp(14)),
                        size_hint=(0.7, 0.35))
            popup.open()
        else:
            popup = Popup(title='❌ Not Enough Coins', 
                        content=Label(text=f'You need {item["price"] - self.coins} more coins!\n\nBuy coins from the shop.', 
                                     font_size=dp(14)),
                        size_hint=(0.8, 0.35))
            popup.open()
            
    def do_free_action(self, item):
        """انجام اقدام رایگان"""
        if item['id'] == 'ad_watch':
            reward = self.payment.watch_ad(self.user_id)
            if reward > 0:
                self.coins = self.payment.get_coins(self.user_id)
                self.coins_label.text = f'🪙 {self.coins} coins'
                popup = Popup(title='📺 Ad Reward', 
                            content=Label(text=f'You got {reward} coins!', font_size=dp(16)),
                            size_hint=(0.7, 0.3))
                popup.open()
            else:
                popup = Popup(title='⏳ Limit Reached', 
                            content=Label(text='You can watch 5 ads per day.\nCome back tomorrow!', font_size=dp(14)),
                            size_hint=(0.8, 0.3))
                popup.open()
                
        elif item['id'] == 'daily_reward':
            reward = self.payment.daily_reward(self.user_id)
            if reward > 0:
                self.coins = self.payment.get_coins(self.user_id)
                self.coins_label.text = f'🪙 {self.coins} coins'
                self.switch_tab('free')
                popup = Popup(title='🎁 Daily Reward', 
                            content=Label(text=f'You got {reward} coins!', font_size=dp(16)),
                            size_hint=(0.7, 0.3))
                popup.open()
            else:
                popup = Popup(title='⏳ Already Claimed', 
                            content=Label(text='You already claimed today\'s reward!', font_size=dp(14)),
                            size_hint=(0.8, 0.3))
                popup.open()
                
        elif item['id'] == 'invite_friend':
            popup = Popup(title='👥 Invite Friend', 
                        content=Label(text='Share this code with friends:\n\nCHESS2024\n\nThey get 50 coins, you get 20!', 
                                     font_size=dp(14)),
                        size_hint=(0.8, 0.4))
            popup.open()