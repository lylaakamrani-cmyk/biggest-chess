---

**Developed by AmirAli Kamrani**  
© 2025 AmirAli Kamrani. All rights reserved.
# راهنمای نصب Chess Master Pro

## معرفی

این راهنما مراحل نصب و راه‌اندازی بازی Chess Master Pro را به صورت کامل و گام‌به‌گام توضیح می‌دهد. با دنبال کردن این مراحل، می‌توانید بازی را بر روی سیستم‌عامل‌های مختلف نصب و اجرا کنید.

---

## پیش‌نیازها

قبل از شروع نصب، اطمینان حاصل کنید که سیستم شما دارای موارد زیر است:

### سیستم‌عامل‌های پشتیبانی شده

| سیستم‌عامل | نسخه | توضیح |
|------------|------|-------|
| Android | 7.0 یا بالاتر | با Pydroid 3 |
| Windows | 10 یا بالاتر | 64-bit |
| Linux | Ubuntu 20.04 یا بالاتر | همچنین Fedora, Debian |
| macOS | 11 یا بالاتر | Intel و Apple Silicon |

### پیش‌نیازهای نرم‌افزاری

| نرم‌افزار | نسخه | توضیح |
|-----------|------|-------|
| Python | 3.8 یا بالاتر | زبان برنامه‌نویسی اصلی |
| pip | 21.0 یا بالاتر | مدیریت بسته‌های Python |
| Git | 2.30 یا بالاتر | (اختیاری) برای کلون کردن پروژه |
| Stockfish | اختیاری | موتور شطرنج قدرتمند |

---

## نصب روی Android (Pydroid 3)

### مرحله ۱: نصب Pydroid 3

1. فروشگاه Google Play را باز کنید
2. عبارت Pydroid 3 را جستجو کنید
3. روی دکمه Install کلیک کنید
4. منتظر اتمام دانلود و نصب باشید
5. برنامه Pydroid 3 را باز کنید

### مرحله ۲: ایجاد پوشه پروژه

1. در Pydroid 3، روی دکمه سه خط (☰) در گوشه بالا سمت چپ کلیک کنید
2. گزینه New Folder را انتخاب کنید
3. نام پوشه را Biggest_chess بگذارید
4. وارد پوشه شوید

### مرحله ۳: دانلود پروژه

روش ۱: دانلود از GitHub

در ترمینال Pydroid 3
cd /storage/emulated/0/Biggest_chess
git clone https://github.com/yourusername/chess-master-pro.git .

روش ۲: دانلود مستقیم

1. فایل فشرده پروژه را از منبع مورد نظر دانلود کنید
2. فایل را در پوشه storage/emulated/0/Biggest_chess/ استخراج کنید
3. اطمینان حاصل کنید که فایل‌ها در مسیر صحیح قرار دارند

### مرحله ۴: نصب کتابخانه‌ها

Pydroid 3 را باز کنید و ترمینال را اجرا کنید:

نصب کتابخانه‌های اصلی
pip install kivy==2.1.0
pip install python-chess==1.9.4
pip install pillow==9.4.0
pip install websockets==10.4
pip install requests==2.28.2

نصب کتابخانه‌های اختیاری
pip install numpy==1.24.1
pip install simpleaudio==1.0.4

### مرحله ۵: ساخت دیتابیس

به پوشه پروژه بروید
cd /storage/emulated/0/Biggest_chess

اجرای فایل ساخت دیتابیس
python create_database.py

اجرای فایل پر کردن داده‌ها
python data/init_data.py

### مرحله ۶: اجرای بازی

python ui/app.py

---

## نصب روی Windows

### مرحله ۱: نصب Python

1. به سایت python.org بروید
2. آخرین نسخه Python 3.x را دانلود کنید
3. فایل نصب را اجرا کنید
4. حتماً گزینه Add Python to PATH را تیک بزنید
5. روی Install Now کلیک کنید
6. منتظر اتمام نصب باشید

### مرحله ۲: نصب Git (اختیاری)

1. به سایت git-scm.com بروید
2. فایل نصب را دانلود کنید
3. با تنظیمات پیش‌فرض نصب را ادامه دهید

### مرحله ۳: دانلود پروژه

باز کردن Command Prompt یا PowerShell

رفتن به پوشه مورد نظر
cd C:\Users\YourName\Desktop

کلون کردن پروژه
git clone https://github.com/yourusername/chess-master-pro.git

وارد شدن به پوشه پروژه
cd chess-master-pro

### مرحله ۴: ایجاد محیط مجازی (توصیه شده)

ایجاد محیط مجازی
python -m venv venv

فعال‌سازی محیط مجازی
venv\Scripts\activate

### مرحله ۵: نصب کتابخانه‌ها

نصب همه کتابخانه‌ها از فایل requirements.txt
pip install -r requirements.txt

یا نصب تک‌تک
pip install kivy==2.1.0
pip install python-chess==1.9.4
pip install pillow==9.4.0
pip install websockets==10.4
pip install requests==2.28.2

### مرحله ۶: نصب Stockfish (اختیاری)

1. به stockfishchess.org/download بروید
2. نسخه Windows را دانلود کنید
3. فایل stockfish.exe را در پوشه assets/stockfish/ قرار دهید

### مرحله ۷: ساخت دیتابیس و اجرا

ساخت دیتابیس
python create_database.py

پر کردن داده‌ها
python data/init_data.py

اجرای بازی
python ui/app.py

---

## نصب روی Linux (Ubuntu/Debian)

### مرحله ۱: نصب Python و پیش‌نیازها

به‌روزرسانی سیستم
sudo apt update
sudo apt upgrade -y

نصب Python و pip
sudo apt install python3 python3-pip python3-venv -y

نصب کتابخانه‌های سیستم مورد نیاز Kivy
sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev -y
sudo apt install libgstreamer1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good -y
sudo apt install libpulse-dev libgl1-mesa-dev -y

### مرحله ۲: نصب Git

sudo apt install git -y

### مرحله ۳: دانلود پروژه

کلون کردن پروژه
git clone https://github.com/yourusername/chess-master-pro.git

وارد شدن به پوشه پروژه
cd chess-master-pro

### مرحله ۴: ایجاد محیط مجازی

ایجاد محیط مجازی
python3 -m venv venv

فعال‌سازی محیط مجازی
source venv/bin/activate

### مرحله ۵: نصب کتابخانه‌ها

نصب همه کتابخانه‌ها
pip install -r requirements.txt

یا نصب تک‌تک
pip install kivy==2.1.0
pip install python-chess==1.9.4
pip install pillow==9.4.0
pip install websockets==10.4
pip install requests==2.28.2

### مرحله ۶: نصب Stockfish (اختیاری)

نصب Stockfish
sudo apt install stockfish -y

### مرحله ۷: ساخت دیتابیس و اجرا

ساخت دیتابیس
python create_database.py

پر کردن داده‌ها
python data/init_data.py

اجرای بازی
python ui/app.py

---

## نصب روی macOS

### مرحله ۱: نصب Homebrew

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

### مرحله ۲: نصب Python و پیش‌نیازها

نصب Python
brew install python3

نصب کتابخانه‌های سیستم مورد نیاز Kivy
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf
brew install gstreamer gst-plugins-base gst-plugins-good
brew install libjpeg libpng

### مرحله ۳: نصب Git

brew install git

### مرحله ۴: دانلود پروژه

کلون کردن پروژه
git clone https://github.com/yourusername/chess-master-pro.git

وارد شدن به پوشه پروژه
cd chess-master-pro

### مرحله ۵: ایجاد محیط مجازی

ایجاد محیط مجازی
python3 -m venv venv

فعال‌سازی محیط مجازی
source venv/bin/activate

### مرحله ۶: نصب کتابخانه‌ها

نصب همه کتابخانه‌ها
pip install -r requirements.txt

### مرحله ۷: نصب Stockfish (اختیاری)

brew install stockfish

### مرحله ۸: ساخت دیتابیس و اجرا

ساخت دیتابیس
python create_database.py

پر کردن داده‌ها
python data/init_data.py

اجرای بازی
python ui/app.py

---

## نصب با استفاده از run_all.py (یکجا)

برای نصب خودکار همه موارد، می‌توانید از فایل run_all.py استفاده کنید:

اجرای نصب یکجا
python run_all.py

این فایل به صورت خودکار موارد زیر را انجام می‌دهد:

1. بررسی نسخه Python
2. ایجاد پوشه‌های مورد نیاز
3. نصب کتابخانه‌ها
4. ساخت دیتابیس
5. پر کردن داده‌های اولیه
6. ساخت Assets
7. ساخت فایل تنظیمات
8. بررسی Stockfish

---

## راه‌اندازی سرور (برای بازی آنلاین)

برای بازی آنلاین، نیاز به اجرای سرور WebSocket دارید:

### راه‌اندازی سرور

اجرای سرور
python server/server.py

### تنظیمات سرور

| پارامتر | پیش‌فرض | توضیح |
|---------|---------|-------|
| Host | 0.0.0.0 | آدرس سرور |
| Port | 8765 | پورت سرور |

### اتصال به سرور

در بازی، در بخش Online:

1. نام کاربری خود را وارد کنید
2. روی دکمه Connect کلیک کنید
3. اگر سرور در حال اجرا باشد، اتصال برقرار می‌شود

---

## اجرای تست‌ها

برای اطمینان از عملکرد صحیح تمام بخش‌ها، تست‌ها را اجرا کنید:

### اجرای همه تست‌ها

python -m unittest discover tests

### اجرای تست‌های جداگانه

تست Board
python tests/test_board.py

تست Game
python tests/test_game.py

تست AI
python tests/test_ai.py

تست Database
python tests/test_database.py

---

## ساخت نسخه قابل اجرا

### Windows (با PyInstaller)

نصب PyInstaller
pip install pyinstaller

ساخت فایل exe
pyinstaller --onefile --windowed --name "ChessMasterPro" ui/app.py

### Linux (با PyInstaller)

pip install pyinstaller
pyinstaller --onefile --name "ChessMasterPro" ui/app.py

### Android (با Buildozer)

نصب Buildozer
pip install buildozer

ایجاد فایل buildozer.spec
buildozer init

ساخت APK
buildozer android debug deploy run

### Android (با Pydroid)

در Pydroid 3، می‌توانید به سادگی بازی را اجرا کنید بدون نیاز به ساخت APK.

---

## عیب‌یابی نصب

### خطا: ModuleNotFoundError: No module named 'kivy'

علت: کتابخانه Kivy نصب نشده است

راه حل:

pip install kivy==2.1.0

### خطا: No module named 'chess'

علت: کتابخانه python-chess نصب نشده است

راه حل:

pip install python-chess==1.9.4

### خطا: pip: command not found

علت: pip نصب نشده یا در PATH نیست

راه حل:

نصب pip
python -m ensurepip --upgrade

یا در لینوکس
sudo apt install python3-pip

### خطا: Permission denied

علت: دسترسی کافی برای نصب یا اجرا وجود ندارد

راه حل:

در لینوکس/macOS
sudo python run_all.py

در ویندوز، به عنوان Administrator اجرا کنید

### خطا: Cannot find stockfish

علت: فایل Stockfish در مسیر صحیح قرار ندارد

راه حل:

1. Stockfish را از سایت رسمی دانلود کنید
2. فایل را در پوشه assets/stockfish/ قرار دهید
3. یا از AI داخلی استفاده کنید (بدون Stockfish)

### خطا: sqlite3.OperationalError: no such table: users

علت: دیتابیس ساخته نشده است

راه حل:

python create_database.py

### خطا: ConnectionRefusedError در بازی آنلاین

علت: سرور WebSocket در حال اجرا نیست

راه حل:

python server/server.py

---

## مسیرهای نصب

| سیستم‌عامل | مسیر پیش‌فرض |
|------------|--------------|
| Android | storage/emulated/0/Biggest_chess/ |
| Windows | C:\Users\YourName\chess-master-pro\ |
| Linux | /home/yourname/chess-master-pro/ |
| macOS | /Users/yourname/chess-master-pro/ |

---

## فایل‌های پیکربندی

| فایل | مسیر | توضیح |
|------|------|-------|
| config.json | data/config.json | تنظیمات بازی (تم، صدا، AI و...) |
| chess_data.db | data/chess_data.db | دیتابیس SQLite |
| .secret.key | data/.secret.key | کلید امنیتی برای رمزنگاری |

---

## حذف نصب

### Android

1. پوشه Biggest_chess را حذف کنید
2. برنامه Pydroid 3 را حذف کنید (اختیاری)

### Windows/Linux/macOS

حذف پوشه پروژه
rm -rf chess-master-pro

حذف محیط مجازی (اگر ایجاد شده)
rm -rf venv

---

## نکات اضافی

### به‌روزرسانی بازی

دریافت آخرین تغییرات
git pull

نصب کتابخانه‌های جدید (در صورت وجود)
pip install -r requirements.txt

بازسازی دیتابیس (در صورت نیاز)
python create_database.py

### رفع مشکلات عملکرد

1. بستن برنامه‌های غیرضروری
2. کاهش کیفیت انیمیشن‌ها در تنظیمات
3. استفاده از AI داخلی به جای Stockfish در دستگاه‌های ضعیف

---

## پشتیبانی

در صورت بروز هرگونه مشکل در نصب، با ایمیل زیر تماس بگیرید:

chessmasterpro@email.com

---

## تاریخچه نسخه‌ها

| نسخه | تاریخ | تغییرات |
|------|-------|---------|
| 1.0.0 | 2026-07-17 | انتشار اولیه |

---

**Developed by AmirAli Kamrani**  
© 2025 AmirAli Kamrani. All rights reserved.
