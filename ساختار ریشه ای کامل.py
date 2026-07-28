# © 2025 AmirAli Kamrani. All rights reserved.
/storage/emulated/0/Biggest_chess/
│
├── main.py                          (ورودی اصلی برنامه)
├── create_database.py               (ساخت دیتابیس)
├── run_all.py                       (نصب و راه‌اندازی یکجا)
├── requirements.txt                 (کتابخانه‌های مورد نیاز)
├── README.md                        (مستندات اصلی)
│
├── core/                            (هسته اصلی - ۱۲ فایل)
│   ├── __init__.py                  
│   ├── board.py                     (مدیریت صفحه شطرنج)
│   ├── game_logic.py                (منطق اصلی بازی)
│   ├── ai_engine.py                 (موتور هوش مصنوعی)
│   ├── stockfish_engine.py          (موتور Stockfish)
│   ├── network.py                   (ارتباط شبکه)
│   ├── database.py                  (مدیریت دیتابیس)
│   ├── profile.py                   (پروفایل کاربر)
│   ├── elo.py                       (سیستم رتبه‌بندی ELO)
│   ├── cloud.py                     (همگام‌سازی ابری)
│   ├── tournament.py                (سیستم تورنمنت)
│   ├── analysis.py                  (تحلیل بازی)
│   └── replay.py                    (پخش مجدد بازی)
│
├── ui/                              (رابط کاربری - ۱۳ فایل)
│   ├── __init__.py                  
│   ├── app.py                       (برنامه اصلی Kivy)
│   ├── home.py                      (صفحه اصلی)
│   ├── board.py                     (صفحه شطرنج)
│   ├── login.py                     (صفحه ورود)
│   ├── profile.py                   (پروفایل کاربر)
│   ├── shop.py                      (فروشگاه)
│   ├── settings.py                  (تنظیمات)
│   ├── online.py                    (بازی آنلاین)
│   ├── local.py                     (بازی محلی)
│   ├── tournament.py                (تورنمنت)
│   ├── analysis.py                  (تحلیل)
│   ├── widgets.py                   (ویجت‌های سفارشی)
│   └── dialogs.py                   (دیالوگ‌ها)
│
├── utils/                           (ابزارها - ۶ فایل)
│   ├── __init__.py                  
│   ├── config.py                    (مدیریت تنظیمات)
│   ├── assets.py                    (مدیریت Assets)
│   ├── sounds.py                    (مدیریت صداها)
│   ├── logger.py                    (مدیریت لاگ‌ها)
│   └── security.py                  (مدیریت امنیت)
│
├── assets/                          (Assets)
│   ├── build_assets.py              (ساخت Assets)
│   ├── images/
│   │   ├── pieces/
│   │   │   ├── white/
│   │   │   │   ├── king.png
│   │   │   │   ├── queen.png
│   │   │   │   ├── rook.png
│   │   │   │   ├── bishop.png
│   │   │   │   ├── knight.png
│   │   │   │   └── pawn.png
│   │   │   └── black/
│   │   │       ├── king.png
│   │   │       ├── queen.png
│   │   │       ├── rook.png
│   │   │       ├── bishop.png
│   │   │       ├── knight.png
│   │   │       └── pawn.png
│   │   ├── backgrounds/
│   │   │   ├── wooden.jpg
│   │   │   ├── dark.jpg
│   │   │   ├── gradient.jpg
│   │   │   └── chess_pattern.jpg
│   │   └── icons/
│   │       ├── settings.png
│   │       ├── profile.png
│   │       ├── friends.png
│   │       ├── shop.png
│   │       ├── home.png
│   │       ├── chess_icon.png
│   │       ├── notification.png
│   │       ├── trophy.png
│   │       └── logo.png
│   ├── sounds/
│   │   ├── move.wav
│   │   ├── check.wav
│   │   ├── win.wav
│   │   ├── lose.wav
│   │   ├── draw.wav
│   │   ├── start.wav
│   │   ├── notification.wav
│   │   ├── click.wav
│   │   └── capture.wav
│   ├── themes/
│   │   ├── classic.json
│   │   ├── dark.json
│   │   ├── neon.json
│   │   ├── blue.json
│   │   ├── green.json
│   │   ├── wood.json
│   │   └── marble.json
│   ├── fonts/
│   │   ├── chess.ttf
│   │   ├── custom.ttf
│   │   └── noto_sans.ttf
│   └── stockfish/
│       ├── stockfish.exe
│       ├── stockfish
│       └── stockfish_android
│
├── server/                          (سرور - ۲ فایل)
│   ├── __init__.py                  
│   ├── server.py                    (سرور اصلی WebSocket)
│   └── websocket_handler.py         (مدیریت پیام‌ها)
│
├── web/                             (نسخه وب - ۳ فایل)
│   ├── index.html                   (صفحه اصلی)
│   ├── styles.css                   (استایل‌ها)
│   └── script.js                    (منطق وب)
│
├── data/                            (داده‌ها)
│   ├── chess_data.db                (دیتابیس اصلی)
│   ├── config.json                  (تنظیمات)
│   ├── .secret.key                  (کلید امنیتی)
│   ├── init_data.py                 (پر کردن دیتابیس)
│   ├── backup.py                    (پشتیبان‌گیری)
│   └── backups/                     (پشتیبان‌ها)
│
├── logs/                            (لاگ‌ها)
│   └── chess_master_YYYYMMDD.log
│
├── tests/                           (تست‌ها - ۵ فایل)
│   ├── __init__.py                  
│   ├── test_board.py                (تست Board)
│   ├── test_game.py                 (تست Game)
│   ├── test_ai.py                   (تست AI)
│   └── test_database.py             (تست Database)
│
└── docs/                            (مستندات - ۴ فایل)
    ├── README.md                    
    ├── API.md                       
    ├── USER_GUIDE.md                
    └── INSTALL.md                   