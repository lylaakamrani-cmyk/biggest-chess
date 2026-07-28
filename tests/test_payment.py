# © 2025 AmirAli Kamrani. All rights reserved.

# test_payment.py
from utils.payment import PaymentManager

pm = PaymentManager()
user_id = 'test_user'

# ۱. دریافت اطلاعات کاربر
print(pm.get_statistics(user_id))

# ۲. خرید سکه (لینک پرداخت زرین‌پال)
link = pm.purchase_coins(user_id, 'coins_1000', 'zarinpal')
print(f"🔗 لینک پرداخت: {link}")

# ۳. تایید پرداخت (بعد از بازگشت از زرین‌پال)
success, ref_id = pm.zarinpal_verify('AUTHORITY_CODE', 70000)
print(f"✅ پرداخت: {success}, Ref: {ref_id}")

# ۴. تماشای تبلیغ
reward = pm.watch_ad(user_id)
print(f"📺 سکه: {reward}")

# ۵. هدیه روزانه
reward = pm.daily_reward(user_id)
print(f"🎁 سکه: {reward}")

# ۶. خرید اشتراک
pm.buy_subscription(user_id, 'monthly')
print(f"👑 Premium: {pm.check_subscription(user_id)}")