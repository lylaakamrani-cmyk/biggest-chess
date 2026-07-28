💰 چطور پول ها واقعاً به حساب شما واریز میشه؟

برای اینکه پول از فروش بازی واقعاً به حساب شما برسه، باید یک درگاه پرداخت بانکی (مثل زیبال) رو در بازی فعال کنید. کاربر پول میده، پول به حساب شما در درگاه واریز میشه، و درگاه بعداً تسویه میکنه به حساب بانکیتون.

مراحل زیر رو به ترتیب انجام بدید:

---

✅ مرحله 1: ثبت‌نام و دریافت merchant_id از زیبال

شما یک شناسه یا مرچنت کد از درگاه دریافت میکنید. برای زیبال اینطوریه:

· توی سایت zibal.ir ثبت‌نام کنید .
· مدارک هویتی (کارت ملی و شماره موبایل به نام خودتون) رو بارگذاری کنید .
· بعد از تأیید، یک merchant_id مخصوص به شما توی پنل زیبال داده میشه.

برای مرحله تست، میتونید از مرچنت کد پیش‌فرض zibal استفاده کنید تا بدون پول واقعی، فرایند رو تست کنید. 

---

✅ مرحله 2: merchant_id رو در کد بازی قرار بدید

فایل utils/payment.py رو باز کنید و merchant_id واقعی خودتون رو جایگزین کنید:

```python
class PaymentManager:
    def __init__(self):
        # ... کدهای قبلی
        self.zibal_merchant = 'YOUR_REAL_MERCHANT_ID_HERE'  # ← این رو عوض کنید
        self.zibal_sandbox = False  # برای حالت واقعی False کنید
```

---

✅ مرحله 3: فرایند پرداخت (کاربر → درگاه → حساب شما)

وقتی کاربر توی فروشگاه بازی دکمه "خرید" رو بزنه، این اتفاق میافته:

1. درخواست پرداخت به زیبال ارسال میشه: کد شما با merchant_id و مبلغ (به ریال) به سرور زیبال درخواست میده. 

```python
response = client.payment_request(
    amount=10000,  # 10000 ریال = 1000 تومان
    callback_url="https://your-game.com/callback",
    description="خرید ۱۰۰ سکه"
)
track_id = response.get("trackId")
payment_url = client.generate_payment_url(track_id)  # لینک پرداخت ساخته میشه
```

2. کاربر به صفحه پرداخت هدایت میشه: کاربر رو به لینک payment_url میبرید تا اطلاعات کارتش رو وارد کنه. 
3. پول به حساب شما در زیبال واریز میشه: بعد از پرداخت موفق، مبلغ به حساب کیف پول شما در زیبال واریز میشه.
4. تأیید پرداخت: بعد از بازگشت کاربر، کد شما با track_id دوباره به سرور زیبال درخواست میده و تأیید میکنه که پول واقعاً واریز شده. 

```python
verification = client.payment_verify(track_id=track_id)
if verification.get("result") == 100:
    # پول تأیید شد، سکه رو به کاربر بدید
    user['coins'] += package['coins']
```

---

✅ مرحله 4: تسویه به حساب بانکی شما

زیبال هر روز صبح، مبالغ تراکنش‌های روز قبل رو به حساب بانکی شما واریز میکنه. 

· تسویه به صورت اتوماتیک روزانه انجام میشه .
· سقف هر تراکنش تا ۵۰ میلیون تومان .
· کارمزد درگاه حدود ۱٪ (حداقل ۱۰۰۰ تومان، حداکثر ۸۰۰۰ تومان) .

برای واریز پول به حساب شرکا (مثلاً اگر چند نفر هستید)، میتونید از قابلیت تسهیم وجوه زیبال استفاده کنید. 

---

🔧 خلاصه کد نهایی در utils/payment.py

```python
import requests

class PaymentManager:
    def __init__(self):
        self.zibal_merchant = 'YOUR_REAL_MERCHANT_ID'  # از پنل زیبال بگیر
        self.sandbox = False  # برای حالت واقعی False کن
        
    def zibal_payment_request(self, amount_rial, description, callback_url):
        url = 'https://gateway.zibal.ir/v1/request'
        data = {
            'merchant': self.zibal_merchant,
            'amount': amount_rial,
            'description': description,
            'callbackUrl': callback_url,
            'sandbox': self.sandbox
        }
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get('result') == 100:
            track_id = result.get('trackId')
            return f"https://gateway.zibal.ir/start/{track_id}"  # لینک پرداخت
        return None
        
    def zibal_verify(self, track_id, amount_rial):
        url = 'https://gateway.zibal.ir/v1/verify'
        data = {
            'merchant': self.zibal_merchant,
            'trackId': track_id,
            'amount': amount_rial
        }
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        return result.get('result') == 100  # True یعنی پرداخت موفق
```

---

🚀 نتیجه نهایی

· کاربر در بازی پرداخت میکنه
· پول به حساب کیف پول شما در زیبال واریز میشه
· زیبال هر روز به حساب بانکی شما تسویه میکنه
· شما میتونید پول رو از حساب بانکیتون برداشت کنید

⚠️ برای فعال‌سازی نهایی، حتماً sandbox = False کنید و از merchant_id واقعی که از پنل زیبال گرفتید استفاده کنید.