# © 2025 AmirAli Kamrani. All rights reserved.

# utils/payment.py
import json
import os
import time
import uuid
import requests
from typing import Dict, Optional, Tuple

class PaymentManager:
    def __init__(self, db_path="data/payments.json"):
        self.db_path = db_path
        self.data = self.load_data()
        
        # ====== درگاه‌های پرداخت ======
        # زرین‌پال (برای بالای ۱۸ سال)
        self.zarinpal_merchant = 'YOUR_MERCHANT_ID'  # از پنل زرین‌پال بگیر
        
        # زیبال (برای زیر ۱۸ سال)
        self.zibal_merchant = 'zibal'  # برای تست از "zibal" استفاده کن
        self.zibal_sandbox = True
        
        # بسته‌های سکه
        self.coin_packages = {
            'coins_100': {'coins': 100, 'price_toman': 10000, 'price_rial': 100000},
            'coins_500': {'coins': 500, 'price_toman': 40000, 'price_rial': 400000},
            'coins_1000': {'coins': 1000, 'price_toman': 70000, 'price_rial': 700000},
            'coins_5000': {'coins': 5000, 'price_toman': 300000, 'price_rial': 3000000},
            'coins_10000': {'coins': 10000, 'price_toman': 500000, 'price_rial': 5000000},
        }
        
    def load_data(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
        
    def save_data(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
            
    def get_user_data(self, user_id: str) -> Dict:
        if user_id not in self.data:
            self.data[user_id] = {
                'coins': 100,
                'subscription': None,
                'purchases': [],
                'premium': False,
                'owned_items': [],
                'daily_claim': None,
                'ad_watch_count': 0,
                'last_ad_watch': None
            }
            self.save_data()
        return self.data[user_id]
        
    def add_coins(self, user_id: str, amount: int) -> int:
        user = self.get_user_data(user_id)
        user['coins'] += amount
        self.save_data()
        return user['coins']
        
    def spend_coins(self, user_id: str, amount: int) -> bool:
        user = self.get_user_data(user_id)
        if user['coins'] >= amount:
            user['coins'] -= amount
            self.save_data()
            return True
        return False
        
    def get_coins(self, user_id: str) -> int:
        return self.get_user_data(user_id).get('coins', 0)
        
    # ====== ZIBAL GATEWAY (مناسب زیر ۱۸ سال) ======
    
    def zibal_payment(self, amount_toman: int, description: str, callback_url: str) -> Optional[str]:
        """
        پرداخت از طریق زیبال
        مناسب کاربران زیر ۱۸ سال
        """
        amount_rial = amount_toman * 10
        
        url = 'https://gateway.zibal.ir/v1/request'
        data = {
            'merchant': self.zibal_merchant,
            'amount': amount_rial,
            'description': description,
            'callbackUrl': callback_url
        }
        
        if self.zibal_sandbox:
            data['sandbox'] = True
            
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('result') == 100:
                track_id = result.get('trackId')
                payment_url = f"https://gateway.zibal.ir/start/{track_id}"
                return payment_url
            else:
                print(f"❌ Zibal error: {result}")
                return None
                
        except Exception as e:
            print(f"❌ Zibal connection error: {e}")
            return None
            
    def zibal_verify(self, track_id: str, amount_toman: int) -> Tuple[bool, Optional[str]]:
        """تایید پرداخت زیبال"""
        amount_rial = amount_toman * 10
        
        url = 'https://gateway.zibal.ir/v1/verify'
        data = {
            'merchant': self.zibal_merchant,
            'trackId': track_id,
            'amount': amount_rial
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('result') == 100:
                return True, result.get('refNumber')
            else:
                return False, None
                
        except Exception as e:
            print(f"❌ Zibal verify error: {e}")
            return False, None
            
    # ====== ZARINPAL GATEWAY (برای بالای ۱۸ سال) ======
    
    def zarinpal_payment(self, amount_toman: int, description: str, callback_url: str) -> Optional[str]:
        """پرداخت از طریق زرین‌پال"""
        if self.zarinpal_merchant == 'YOUR_MERCHANT_ID':
            print("⚠️ لطفاً MERCHANT_ID زرین‌پال رو تنظیم کن!")
            return None
            
        amount_rial = amount_toman * 10
        
        url = 'https://api.zarinpal.com/pg/v4/payment/request.json'
        data = {
            'merchant_id': self.zarinpal_merchant,
            'amount': amount_rial,
            'description': description,
            'callback_url': callback_url
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('data', {}).get('code') == 100:
                authority = result['data']['authority']
                payment_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
                return payment_url
            else:
                print(f"❌ Zarinpal error: {result}")
                return None
                
        except Exception as e:
            print(f"❌ Zarinpal connection error: {e}")
            return None
            
    def zarinpal_verify(self, authority: str, amount_toman: int) -> Tuple[bool, Optional[str]]:
        """تایید پرداخت زرین‌پال"""
        if self.zarinpal_merchant == 'YOUR_MERCHANT_ID':
            return False, None
            
        amount_rial = amount_toman * 10
        
        url = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
        data = {
            'merchant_id': self.zarinpal_merchant,
            'authority': authority,
            'amount': amount_rial
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('data', {}).get('code') == 100:
                ref_id = result['data']['ref_id']
                return True, ref_id
            else:
                return False, None
                
        except Exception as e:
            print(f"❌ Zarinpal verify error: {e}")
            return False, None
            
    # ====== FREE REWARDS ======
    
    def watch_ad(self, user_id: str) -> int:
        """تماشای تبلیغ برای سکه"""
        user = self.get_user_data(user_id)
        
        today = time.strftime('%Y-%m-%d')
        last_watch = user.get('last_ad_watch', '')
        count = user.get('ad_watch_count', 0)
        
        if last_watch != today:
            count = 0
            
        if count >= 5:
            return -1
            
        reward = 5
        user['coins'] += reward
        user['ad_watch_count'] = count + 1
        user['last_ad_watch'] = today
        self.save_data()
        return reward
        
    def daily_reward(self, user_id: str) -> int:
        """هدیه روزانه"""
        user = self.get_user_data(user_id)
        
        today = time.strftime('%Y-%m-%d')
        last_claim = user.get('daily_claim', '')
        
        if last_claim == today:
            return 0
            
        reward = 10
        user['coins'] += reward
        user['daily_claim'] = today
        self.save_data()
        return reward
        
    # ====== SUBSCRIPTION ======
    
    def check_subscription(self, user_id: str) -> bool:
        user = self.get_user_data(user_id)
        if not user.get('subscription'):
            return False
        if time.time() > user['subscription']['expires']:
            user['premium'] = False
            user['subscription'] = None
            self.save_data()
            return False
        return True
        
    def buy_subscription(self, user_id: str, plan_id: str) -> bool:
        plans = {
            'weekly': {'days': 7, 'price_toman': 20000},
            'monthly': {'days': 30, 'price_toman': 60000},
            'yearly': {'days': 365, 'price_toman': 500000},
        }
        
        if plan_id not in plans:
            return False
            
        plan = plans[plan_id]
        user = self.get_user_data(user_id)
        
        if self.spend_coins(user_id, plan['price_toman']):
            user['subscription'] = {
                'plan': plan_id,
                'start': time.time(),
                'expires': time.time() + (plan['days'] * 86400)
            }
            user['premium'] = True
            self.save_data()
            return True
            
        return False