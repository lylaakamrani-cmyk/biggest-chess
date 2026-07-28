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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.payment import PaymentManager

class ShopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment = PaymentManager()
        self.user_id = 'user_001'  # در نسخه واقعی از دیتابیس میاد
        
        # بارگذاری اطلاعات کاربر
        self.user_data = self.payment.get_user_data(self.user_id)
        self.is_premium = self.payment.check_subscription(self.user_id)
        self.coins = self.user_data.get('coins', 0)
        
        # وضعیت تب‌ها
        self.current_tab = 'coins'
        
        self.build_ui()
        
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
            ('👑 Premium', 'premium'),
            ('🎁 Free', 'free')
        ]
        self.tab_buttons = []
        for text, tab_id in tab_names:
            btn = Button(text=text, font_size=dp(13), background_normal='',
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
        elif tab_id == 'premium':
            self.show_premium_tab()
        else:
            self.show_free_tab()
            
    # ==================== COINS TAB ====================
    
    def show_coins_tab(self):
        """نمایش بسته‌های خرید سکه"""
        self.items_grid.clear_widgets()
        
        packages = [
            {'id': 'coins_100', 'name': '100 Coins', 'price_toman': '10,000', 'price_usd': '0.99$', 'coins': 100, 'icon': '🪙', 'color': (0.3, 0.5, 0.8, 1)},
            {'id': 'coins_500', 'name': '500 Coins', 'price_toman': '40,000', 'price_usd': '3.99$', 'coins': 500, 'icon': '🪙🪙', 'color': (0.2, 0.6, 0.3, 1)},
            {'id': 'coins_1000', 'name': '1000 Coins', 'price_toman': '70,000', 'price_usd': '6.99$', 'coins': 1000, 'icon': '🪙🪙🪙', 'color': (0.8, 0.6, 0.2, 1)},
            {'id': 'coins_5000', 'name': '5000 Coins', 'price_toman': '300,000', 'price_usd': '29.99$', 'coins': 5000, 'icon': '💎', 'color': (0.6, 0.2, 0.8, 1)},
            {'id': 'coins_10000', 'name': '10000 Coins', 'price_toman': '500,000', 'price_usd': '49.99$', 'coins': 10000, 'icon': '👑', 'color': (1, 0.8, 0, 1)},
        ]
        
        for pkg in packages:
            box = self.create_item_box(pkg['color'])
            
            # Icon
            box.add_widget(Label(text=pkg['icon'], font_size=dp(32), size_hint_y=0.2))
            
            # Name
            box.add_widget(Label(text=pkg['name'], font_size=dp(15), color=(1, 1, 1, 1), bold=True, size_hint_y=0.15))
            
            # Coins
            box.add_widget(Label(text=f'{pkg["coins"]} coins', font_size=dp(13), color=(1, 1, 0.6, 1), size_hint_y=0.12))
            
            # Prices
            price_box = BoxLayout(size_hint_y=0.15, spacing=dp(5))
            price_box.add_widget(Label(text=f'💰 {pkg["price_toman"]} T', font_size=dp(12), color=(0.2, 0.8, 0.2, 1)))
            price_box.add_widget(Label(text=f'💵 {pkg["price_usd"]}', font_size=dp(12), color=(0.2, 0.6, 0.9, 1)))
            box.add_widget(price_box)
            
            # Buy button
            btn = Button(text='Buy Now', font_size=dp(14), size_hint_y=0.2,
                        background_normal='', background_color=(0.97, 0.59, 0.12, 1))
            btn.bind(on_release=lambda x, p=pkg: self.purchase_coins(p))
            box.add_widget(btn)
            
            self.items_grid.add_widget(box)
            
    # ==================== PREMIUM TAB ====================
    
    def show_premium_tab(self):
        """نمایش اشتراک‌های Premium"""
        self.items_grid.clear_widgets()
        
        plans = [
            {'id': 'weekly', 'name': 'Weekly', 'price_toman': '20,000', 'price_usd': '1.99$', 'days': 7, 'icon': '📅', 'color': (0.2, 0.4, 0.8, 1)},
            {'id': 'monthly', 'name': 'Monthly', 'price_toman': '60,000', 'price_usd': '5.99$', 'days': 30, 'icon': '📆', 'color': (0.97, 0.59, 0.12, 1)},
            {'id': 'yearly', 'name': 'Yearly', 'price_toman': '500,000', 'price_usd': '49.99$', 'days': 365, 'icon': '🎯', 'color': (0.8, 0.2, 0.6, 1)},
        ]
        
        features = '✅ Unlimited Analysis\n✅ No Ads\n✅ Premium Themes\n✅ Advanced AI\n✅ Tournament Access'
        
        for plan in plans:
            box = self.create_item_box(plan['color'])
            
            # Icon
            box.add_widget(Label(text=plan['icon'], font_size=dp(28), size_hint_y=0.12))
            
            # Name
            box.add_widget(Label(text=plan['name'], font_size=dp(16), color=(1, 1, 0.6, 1), bold=True, size_hint_y=0.12))
            
            # Days
            box.add_widget(Label(text=f'{plan["days"]} days', font_size=dp(12), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.10))
            
            # Features
            box.add_widget(Label(text=features[:35] + '...', font_size=dp(10), color=(0.6, 0.6, 0.6, 1), size_hint_y=0.20, halign='center'))
            
            # Price
            price_box = BoxLayout(size_hint_y=0.12, spacing=dp(5))
            price_box.add_widget(Label(text=f'💰 {plan["price_toman"]} T', font_size=dp(12), color=(0.2, 0.8, 0.2, 1)))
            price_box.add_widget(Label(text=f'💵 {plan["price_usd"]}', font_size=dp(12), color=(0.2, 0.6, 0.9, 1)))
            box.add_widget(price_box)
            
            # Subscribe button
            btn_text = 'Subscribed ✅' if self.is_premium else 'Subscribe'
            btn_color = (0.1, 0.6, 0.1, 1) if self.is_premium else (0.97, 0.59, 0.12, 1)
            btn = Button(text=btn_text, font_size=dp(14), size_hint_y=0.18,
                        background_normal='', background_color=btn_color)
            if not self.is_premium:
                btn.bind(on_release=lambda x, p=plan: self.purchase_subscription(p))
            box.add_widget(btn)
            
            self.items_grid.add_widget(box)
            
    # ==================== FREE TAB ====================
    
    def show_free_tab(self):
        """نمایش آیتم‌های رایگان (تبلیغات، هدیه روزانه)"""
        self.items_grid.clear_widgets()
        
        free_items = [
            {'id': 'ad_watch', 'name': 'Watch Ad', 'desc': 'Get 5 free coins', 'icon': '📺', 'color': (0.2, 0.4, 0.8, 1), 'action': 'watch_ad'},
            {'id': 'daily_reward', 'name': 'Daily Reward', 'desc': 'Claim 10 free coins daily', 'icon': '🎁', 'color': (0.97, 0.59, 0.12, 1), 'action': 'daily_reward'},
            {'id': 'invite_friend', 'name': 'Invite Friend', 'desc': 'Get 20 coins per invite', 'icon': '👥', 'color': (0.2, 0.7, 0.2, 1), 'action': 'invite_friend'},
        ]
        
        # بررسی وضعیت هدیه روزانه
        today = time.strftime('%Y-%m-%d')
        daily_claimed = self.user_data.get('daily_claim') == today
        
        for item in free_items:
            box = self.create_item_box(item['color'])
            
            # Icon
            box.add_widget(Label(text=item['icon'], font_size=dp(30), size_hint_y=0.25))
            
            # Name
            box.add_widget(Label(text=item['name'], font_size=dp(15), color=(1, 1, 1, 1), bold=True, size_hint_y=0.15))
            
            # Description
            box.add_widget(Label(text=item['desc'], font_size=dp(12), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.15))
            
            # Claim button
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
        """ساخت یک باکس آیتم"""
        box = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4), size_hint_y=None, height=dp(180))
        with box.canvas.before:
            Color(*color)
            rect = RoundedRectangle(size=box.size, pos=box.pos, radius=[dp(10)])
            box.bind(size=lambda i, v: setattr(rect, 'size', v))
            box.bind(pos=lambda i, v: setattr(rect, 'pos', v))
        return box
        
    # ==================== ACTIONS ====================
    
    def purchase_coins(self, package):
        """خرید سکه - باز کردن لینک زرین‌پال"""
        # دریافت لینک پرداخت
        payment_url = self.payment.purchase_coins(self.user_id, package['id'], 'zarinpal')
        
        if payment_url and isinstance(payment_url, str) and payment_url.startswith('http'):
            # باز کردن لینک در مرورگر
            webbrowser.open(payment_url)
            
            popup = Popup(title='💰 Payment', 
                        content=Label(text=f'Redirecting to payment page...\n\n{package["name"]}\nPrice: {package["price_toman"]} Toman', 
                                     font_size=dp(14)),
                        size_hint=(0.8, 0.4))
            popup.open()
            
            # شبیه‌سازی تایید پرداخت (در نسخه واقعی بعد از بازگشت از زرین‌پال)
            Clock.schedule_once(lambda dt: self.simulate_payment_confirm(package), 5)
        else:
            popup = Popup(title='❌ Error', 
                        content=Label(text='Payment gateway error!\nPlease try again.', font_size=dp(16)),
                        size_hint=(0.8, 0.3))
            popup.open()
            
    def simulate_payment_confirm(self, package):
        """شبیه‌سازی تایید پرداخت (برای تست)"""
        # در نسخه واقعی، این تابع بعد از بازگشت از زرین‌پال صدا زده میشه
        success = self.payment.confirm_purchase(
            self.user_id, 
            'SIMULATED_AUTHORITY', 
            package['price_toman'].replace(',', '')
        )
        
        if success:
            self.coins = self.payment.get_coins(self.user_id)
            self.coins_label.text = f'🪙 {self.coins} coins'
            
            popup = Popup(title='✅ Success!', 
                        content=Label(text=f'You got {package["coins"]} coins!', font_size=dp(16)),
                        size_hint=(0.7, 0.3))
            popup.open()
        else:
            popup = Popup(title='⚠️ Pending', 
                        content=Label(text='Payment is being processed...\nYou will receive coins soon.', font_size=dp(14)),
                        size_hint=(0.8, 0.3))
            popup.open()
            
    def purchase_subscription(self, plan):
        """خرید اشتراک Premium"""
        success = self.payment.buy_subscription(self.user_id, plan['id'])
        
        if success:
            self.is_premium = True
            self.status_label.text = '👑 Premium'
            self.status_label.color = (1, 1, 0.6, 1)
            
            popup = Popup(title='✅ Subscribed!', 
                        content=Label(text=f'You are now {plan["name"]} Premium!\nEnjoy unlimited features!', font_size=dp(16)),
                        size_hint=(0.8, 0.35))
            popup.open()
            
            # رفرش صفحه
            self.switch_tab(self.current_tab)
        else:
            popup = Popup(title='❌ Error', 
                        content=Label(text='Subscription failed!\nPlease try again.', font_size=dp(16)),
                        size_hint=(0.8, 0.3))
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
                            content=Label(text='You already claimed today\'s reward!\nCome back tomorrow.', font_size=dp(14)),
                            size_hint=(0.8, 0.3))
                popup.open()
                
        elif item['id'] == 'invite_friend':
            popup = Popup(title='👥 Invite Friend', 
                        content=Label(text='Share this code with friends:\n\nCHESS2024\n\nThey get 50 coins, you get 20!', 
                                     font_size=dp(14)),
                        size_hint=(0.8, 0.4))
            popup.open()