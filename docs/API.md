---

**Developed by AmirAli Kamrani**  
© 2025 AmirAli Kamrani. All rights reserved.
# مستندات API

## معرفی

این مستندات شامل توضیحات کامل APIهای پیاده‌سازی شده در بازی Chess Master Pro می‌باشد. APIها به سه دسته Core، Utils و Network تقسیم می‌شوند.

---

## بخش Core

### 1. BoardState (core/board.py)

مدیریت صفحه شطرنج و قوانین بازی

#### متدها

**`__init__(fen: Optional[str] = None)`**
- مقداردهی اولیه صفحه شطرنج
- دریافت FEN اختیاری برای تنظیم موقعیت دلخواه

**`make_move(move: chess.Move, time_elapsed: float = 0.0) -> bool`**
- اجرای حرکت روی صفحه
- بازگشت True در صورت موفقیت

**`undo_last_move() -> Optional[chess.Move]`**
- برگشت آخرین حرکت
- بازگشت حرکت برگشتی یا None

**`get_legal_moves() -> List[chess.Move]`**
- دریافت لیست حرکت‌های قانونی
- خروجی: لیستی از حرکت‌های مجاز

**`get_status() -> Dict[str, Any]`**
- دریافت وضعیت فعلی بازی
- خروجی شامل: turn, in_check, in_checkmate, in_stalemate, move_count

**`get_move_history() -> List[Dict]`**
- دریافت تاریخچه حرکت‌ها
- خروجی: لیستی از دیکشنری‌های شامل move_number, from_square, to_square, san

**`get_pgn() -> str`**
- دریافت بازی در فرمت PGN

**`get_move_analysis() -> Dict[str, Any]`**
- تحلیل موقعیت فعلی
- خروجی شامل: material_balance, piece_activity, king_safety, pawn_structure

---

### 2. GameLogic (core/game_logic.py)

منطق اصلی بازی و مدیریت جریان بازی

#### کلاس GameConfig

تنظیمات بازی

| پارامتر | نوع | پیش‌فرض | توضیح |
|---------|-----|---------|-------|
| time_control | str | "10+0" | کنترل زمان بازی |
| initial_time | int | 600 | زمان اولیه بر حسب ثانیه |
| increment | int | 0 | افزایش زمان در هر حرکت |
| allow_takeback | bool | False | اجازه برگشت حرکت |
| allow_draw_offer | bool | True | اجازه پیشنهاد مساوی |
| allow_resign | bool | True | اجازه تسلیم |
| rated | bool | True | بازی رتبه‌بندی شده |
| variant | str | "standard" | نوع بازی |

#### متدها

**`start_game(mode: GameMode)`**
- شروع بازی در حالت مشخص
- حالت‌ها: LOCAL, AI, ONLINE, TOURNAMENT

**`make_move(move: chess.Move) -> Dict[str, Any]`**
- اجرای حرکت در بازی
- خروجی شامل: success, move, status, result

**`get_legal_moves(square: int = None) -> List[chess.Move]`**
- دریافت حرکت‌های قانونی
- دریافت شماره مربع اختیاری

**`get_move_suggestions(count: int = 3) -> List[Dict]`**
- دریافت پیشنهاد حرکت از AI
- تعداد پیشنهادات قابل تنظیم

**`offer_draw(player: chess.Color) -> bool`**
- پیشنهاد مساوی
- بازگشت True در صورت موفقیت

**`resign(player: chess.Color) -> bool`**
- تسلیم بازی
- بازگشت True در صورت موفقیت

**`takeback(moves: int = 1) -> bool`**
- برگشت حرکت‌های قبلی
- تعداد حرکت‌های برگشتی قابل تنظیم

**`get_game_state() -> Dict[str, Any]`**
- دریافت وضعیت کامل بازی
- خروجی شامل: board, status, result, mode, white_time, black_time

**`to_pgn() -> str`**
- تبدیل بازی به فرمت PGN

**`from_pgn(pgn: str)`**
- بارگذاری بازی از فرمت PGN

---

### 3. AIEngine (core/ai_engine.py)

موتور هوش مصنوعی بازی

#### کلاس AIDifficulty

سطوح دشواری AI

| سطح | depth | زمان (ثانیه) |
|-----|-------|--------------|
| BEGINNER | 2 | 1.0 |
| EASY | 3 | 1.5 |
| MEDIUM | 4 | 2.0 |
| HARD | 6 | 3.0 |
| EXPERT | 8 | 5.0 |
| MASTER | 12 | 10.0 |

#### متدها

**`set_difficulty(difficulty: AIDifficulty)`**
- تنظیم سطح دشواری AI

**`get_best_move(board: chess.Board) -> Optional[chess.Move]`**
- دریافت بهترین حرکت برای موقعیت فعلی

**`set_stockfish_path(path: str)`**
- تنظیم مسیر Stockfish

**`get_search_stats() -> Dict`**
- دریافت آمار جستجو
- خروجی شامل: nodes, captures, checks, mate_found

**`clear_transposition_table()`**
- پاک کردن جدول انتقال

**`get_evaluation() -> float`**
- دریافت امتیاز موقعیت فعلی

---

### 4. StockfishEngine (core/stockfish_engine.py)

موتور Stockfish برای تحلیل حرفه‌ای

#### متدها

**`set_config(**kwargs)`**
- تنظیمات موتور
- پارامترها: Threads, Hash, Skill_Level, Contempt

**`set_search_config(**kwargs)`**
- تنظیمات جستجو
- پارامترها: depth, time, nodes, mate, movetime

**`get_best_move(board: chess.Board, **kwargs) -> Optional[chess.Move]`**
- دریافت بهترین حرکت با تنظیمات جستجو

**`analyze_position(board: chess.Board, **kwargs) -> Dict`**
- تحلیل عمیق موقعیت
- خروجی شامل: best_move, score, pv, depth, nodes

**`get_evaluation(board: chess.Board, depth: int = 12) -> float`**
- دریافت امتیاز موقعیت در عمق مشخص

**`get_pv(board: chess.Board, depth: int = 15) -> List[chess.Move]`**
- دریافت تغییرات اصلی (Principal Variation)

---

### 5. Database (core/database.py)

مدیریت دیتابیس SQLite

#### متدهای کاربر

**`create_user(username: str, password: str, email: str = None) -> Optional[int]`**
- ایجاد کاربر جدید
- بازگشت ID کاربر یا None

**`authenticate_user(username: str, password: str) -> Optional[Dict]`**
- احراز هویت کاربر
- خروجی: اطلاعات کاربر یا None

**`get_user(user_id: int) -> Optional[Dict]`**
- دریافت اطلاعات کاربر با ID

**`get_user_by_username(username: str) -> Optional[Dict]`**
- دریافت اطلاعات کاربر با نام کاربری

**`update_user_rating(user_id: int, new_rating: int)`**
- به‌روزرسانی رتبه کاربر

**`update_user_stats(user_id: int, result: str)`**
- به‌روزرسانی آمار کاربر (win/loss/draw)

**`get_user_stats(user_id: int) -> Optional[Dict]`**
- دریافت آمار کاربر

**`get_leaderboard(limit: int = 100) -> List[Dict]`**
- دریافت جدول رتبه‌بندی

#### متدهای بازی

**`save_game(game_data: Dict) -> str`**
- ذخیره بازی در دیتابیس
- بازگشت ID بازی

**`get_game(game_id: str) -> Optional[Dict]`**
- دریافت بازی با ID

**`get_user_games(user_id: int, limit: int = 50) -> List[Dict]`**
- دریافت بازی‌های کاربر

#### متدهای دوستان

**`add_friend(user_id: int, friend_id: int) -> bool`**
- اضافه کردن دوست

**`accept_friend(user_id: int, friend_id: int) -> bool`**
- پذیرش درخواست دوستی

**`get_friends(user_id: int) -> List[Dict]`**
- دریافت لیست دوستان

#### متدهای فروشگاه

**`add_shop_item(item_data: Dict) -> bool`**
- اضافه کردن آیتم به فروشگاه

**`get_shop_items(category: str = None) -> List[Dict]`**
- دریافت آیتم‌های فروشگاه

**`purchase_item(user_id: int, item_id: str) -> bool`**
- خرید آیتم توسط کاربر

**`get_inventory(user_id: int) -> List[Dict]`**
- دریافت موجودی کاربر

#### متدهای تنظیمات

**`get_user_settings(user_id: int) -> Optional[Dict]`**
- دریافت تنظیمات کاربر

**`update_user_settings(user_id: int, settings: Dict)`**
- به‌روزرسانی تنظیمات کاربر

---

## بخش Utils

### 6. ConfigManager (utils/config.py)

مدیریت تنظیمات برنامه

#### متدها

**`get(key: str, default: Any = None) -> Any`**
- دریافت مقدار تنظیمات با کلید نقطه‌دار
- مثال: `config.get('game.time_control')`

**`set(key: str, value: Any)`**
- تنظیم مقدار با کلید نقطه‌دار
- مثال: `config.set('board.theme', 'dark')`

**`get_all() -> Dict`**
- دریافت همه تنظیمات

**`reset_to_default()`**
- بازنشانی به تنظیمات پیش‌فرض

**`export_config(path: str)`**
- خروجی گرفتن از تنظیمات به فایل

**`import_config(path: str) -> bool`**
- وارد کردن تنظیمات از فایل

---

### 7. AssetManager (utils/assets.py)

مدیریت Assets

#### متدها

**`get_piece_path(piece_type: str, color: str, format: str = 'png') -> str`**
- دریافت مسیر مهره

**`load_theme(theme_name: str) -> Dict`**
- بارگذاری تم

**`load_font(font_name: str, size: int) -> Optional[object]`**
- بارگذاری فونت

**`create_default_assets()`**
- ایجاد Assets پیش‌فرض

**`verify_assets() -> Dict[str, bool]`**
- بررسی وجود Assets

**`get_asset_info() -> Dict`**
- دریافت اطلاعات Assets

---

### 8. SoundManager (utils/sounds.py)

مدیریت صداهای بازی

#### کلاس SoundType

انواع صداها: MOVE, CHECK, WIN, LOSE, DRAW, START, NOTIFICATION, CLICK, TIMER

#### متدها

**`play(sound_type: SoundType, volume: float = None)`**
- پخش صدا

**`play_move_sound()`**
- صدای حرکت

**`play_check_sound()`**
- صدای کیش

**`play_win_sound()`**
- صدای برد

**`play_lose_sound()`**
- صدای باخت

**`play_draw_sound()`**
- صدای مساوی

**`set_volume(volume: float)`**
- تنظیم بلندی صدا

**`set_enabled(enabled: bool)`**
- فعال/غیرفعال کردن صدا

**`stop_all()`**
- توقف همه صداها

---

### 9. Logger (utils/logger.py)

سیستم لاگ‌گیری

#### متدها

**`debug(message: str, data: Dict = None)`**
- لاگ سطح Debug

**`info(message: str, data: Dict = None)`**
- لاگ سطح Info

**`warning(message: str, data: Dict = None)`**
- لاگ سطح Warning

**`error(message: str, data: Dict = None)`**
- لاگ سطح Error

**`critical(message: str, data: Dict = None)`**
- لاگ سطح Critical

**`log_game_event(event_type: str, data: Dict)`**
- ثبت رویداد بازی

**`get_logs(lines: int = 100) -> List[str]`**
- دریافت لاگ‌های اخیر

**`get_log_stats() -> Dict`**
- آمار لاگ‌ها

---

### 10. SecurityManager (utils/security.py)

مدیریت امنیت و رمزنگاری

#### متدها

**`encrypt(data: Any) -> str`**
- رمزنگاری داده

**`decrypt(encrypted_data: str) -> Any`**
- رمزگشایی داده

**`hash_password(password: str, salt: str = None) -> tuple`**
- هش کردن رمز عبور

**`verify_password(password: str, password_hash: str, salt: str) -> bool`**
- تایید رمز عبور

**`generate_token(length: int = 32) -> str`**
- تولید توکن امن

**`generate_otp(length: int = 6) -> str`**
- تولید کد یکبار مصرف

**`validate_input(data: str, max_length: int = 1000) -> bool`**
- اعتبارسنجی ورودی

**`sanitize_filename(filename: str) -> str`**
- پاکسازی نام فایل

**`encrypt_file(input_path: str, output_path: str = None)`**
- رمزنگاری فایل

**`decrypt_file(input_path: str, output_path: str = None)`**
- رمزگشایی فایل

---

## بخش Network

### 11. NetworkServer (core/network.py)

سرور WebSocket

#### متدها

**`start()`**
- راه‌اندازی سرور

**`stop()`**
- توقف سرور

**`register_user(username: str, password: str)`**
- ثبت کاربر جدید

**`add_connection_callback(callback: Callable)`**
- اضافه کردن callback اتصال

**`add_message_handler(message_type: MessageType, handler: Callable)`**
- اضافه کردن handler پیام

**`get_stats() -> Dict`**
- دریافت آمار سرور

---

### 12. NetworkClient (core/network.py)

کلاینت WebSocket

#### متدها

**`connect() -> bool`**
- اتصال به سرور

**`disconnect()`**
- قطع اتصال

**`authenticate(username: str, password: str) -> bool`**
- احراز هویت

**`create_game(config: Dict = None) -> bool`**
- ایجاد بازی جدید

**`join_game(game_id: str) -> bool`**
- پیوستن به بازی

**`send_move(game_id: str, move: str) -> bool`**
- ارسال حرکت

**`send_chat(message: str, target: str = None) -> bool`**
- ارسال پیام چت

**`get_profile(username: str = None) -> bool`**
- دریافت پروفایل

**`is_connected() -> bool`**
- بررسی اتصال

**`is_authenticated() -> bool`**
- بررسی احراز هویت

---

## کدهای وضعیت

| کد | توضیح |
|----------|-----|
| 200 | موفقیت |
| 400 | خطای کلاینت |
| 401 | احراز هویت نشده |
| 403 | دسترسی غیرمجاز |
| 404 | پیدا نشد |
| 500 | خطای سرور |

---

## پیام‌های WebSocket

| نوع پیام | توضیح |
|----------|-------|
| auth | احراز هویت |
| join_lobby | پیوستن به لابی |
| create_game | ایجاد بازی |
| join_game | پیوستن به بازی |
| move | حرکت |
| chat | چت |
| resign | تسلیم |
| draw_offer | پیشنهاد مساوی |
| get_lobby | دریافت لیست لابی |
| get_games | دریافت لیست بازی‌ها |
| ping | پینگ |
| pong | پونگ |

---

## تاریخچه نسخه‌ها

| نسخه | تاریخ | تغییرات |
|----------|--------|---------|
| 1.0.0 | 2026-7-14 | انتشار اولیه |


---

**Developed by AmirAli Kamrani**  
© 2025 AmirAli Kamrani. All rights reserved.
