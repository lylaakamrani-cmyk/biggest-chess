# © 2025 AmirAli Kamrani. All rights reserved.
# create_database.py
import os
import sqlite3
import time

def create_database():
    """ساخت دیتابیس و تمام جداول"""
    
    # ایجاد پوشه data
    os.makedirs("data", exist_ok=True)
    
    # اتصال به دیتابیس
    db_path = "data/chess_data.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📊 Creating tables...")
    
    # 1. جدول users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at INTEGER NOT NULL,
            last_login INTEGER,
            rating INTEGER DEFAULT 1200,
            games_played INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            avatar TEXT,
            is_active BOOLEAN DEFAULT 1,
            is_banned BOOLEAN DEFAULT 0,
            country TEXT,
            bio TEXT,
            total_coins INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0
        )
    ''')
    print("  ✅ users")
    
    # 2. جدول games
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            white_player_id INTEGER,
            black_player_id INTEGER,
            winner TEXT,
            result TEXT,
            pgn TEXT,
            fen_list TEXT,
            status TEXT,
            time_control TEXT,
            rated BOOLEAN,
            started_at INTEGER,
            ended_at INTEGER,
            moves_count INTEGER,
            white_time_used INTEGER,
            black_time_used INTEGER,
            analysis_data TEXT,
            game_type TEXT,
            tournament_id TEXT,
            platform TEXT
        )
    ''')
    print("  ✅ games")
    
    # 3. جدول moves
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT,
            move_number INTEGER,
            from_square TEXT,
            to_square TEXT,
            promotion TEXT,
            san TEXT,
            fen_before TEXT,
            fen_after TEXT,
            move_time INTEGER,
            player_color TEXT,
            is_capture BOOLEAN,
            is_check BOOLEAN,
            is_checkmate BOOLEAN,
            is_castle BOOLEAN,
            is_en_passant BOOLEAN,
            FOREIGN KEY (game_id) REFERENCES games (id)
        )
    ''')
    print("  ✅ moves")
    
    # 4. جدول stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total_games INTEGER DEFAULT 0,
            total_wins INTEGER DEFAULT 0,
            total_losses INTEGER DEFAULT 0,
            total_draws INTEGER DEFAULT 0,
            total_moves INTEGER DEFAULT 0,
            avg_time_per_move INTEGER DEFAULT 0,
            longest_win_streak INTEGER DEFAULT 0,
            current_win_streak INTEGER DEFAULT 0,
            best_rating INTEGER DEFAULT 1200,
            worst_rating INTEGER DEFAULT 1200,
            last_updated INTEGER,
            openings_played TEXT,
            favorite_opening TEXT,
            total_captures INTEGER DEFAULT 0,
            total_checks INTEGER DEFAULT 0,
            total_checkmates INTEGER DEFAULT 0,
            total_castles INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    print("  ✅ stats")
    
    # 5. جدول friends
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            friend_id INTEGER,
            status TEXT,
            created_at INTEGER,
            last_interaction INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id)
        )
    ''')
    print("  ✅ friends")
    
    # 6. جدول messages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            message TEXT,
            timestamp INTEGER,
            is_read BOOLEAN DEFAULT 0,
            message_type TEXT,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')
    print("  ✅ messages")
    
    # 7. جدول tournaments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tournaments (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT,
            status TEXT,
            max_players INTEGER,
            current_players INTEGER,
            created_by INTEGER,
            created_at INTEGER,
            started_at INTEGER,
            ended_at INTEGER,
            prize_pool TEXT,
            rules TEXT,
            rounds INTEGER,
            current_round INTEGER,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    print("  ✅ tournaments")
    
    # 8. جدول tournament_games
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tournament_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id TEXT,
            game_id TEXT,
            round_number INTEGER,
            player1_id INTEGER,
            player2_id INTEGER,
            winner_id INTEGER,
            status TEXT,
            FOREIGN KEY (tournament_id) REFERENCES tournaments (id),
            FOREIGN KEY (game_id) REFERENCES games (id)
        )
    ''')
    print("  ✅ tournament_games")
    
    # 9. جدول shop_items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            category TEXT,
            type TEXT,
            image_url TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at INTEGER,
            discount INTEGER DEFAULT 0,
            rarity TEXT
        )
    ''')
    print("  ✅ shop_items")
    
    # 10. جدول inventory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id TEXT,
            quantity INTEGER DEFAULT 1,
            acquired_at INTEGER,
            equipped BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (item_id) REFERENCES shop_items (item_id)
        )
    ''')
    print("  ✅ inventory")
    
    # 11. جدول settings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            board_theme TEXT DEFAULT 'classic',
            piece_theme TEXT DEFAULT 'classic',
            sound_enabled BOOLEAN DEFAULT 1,
            animations_enabled BOOLEAN DEFAULT 1,
            show_timer BOOLEAN DEFAULT 1,
            show_move_history BOOLEAN DEFAULT 1,
            language TEXT DEFAULT 'en',
            auto_promote BOOLEAN DEFAULT 1,
            move_animation_speed INTEGER DEFAULT 300,
            volume INTEGER DEFAULT 70,
            notifications_enabled BOOLEAN DEFAULT 1,
            dark_mode BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    print("  ✅ settings")
    
    # 12. جدول achievements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            achievement_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            points INTEGER DEFAULT 10,
            category TEXT,
            requirement TEXT
        )
    ''')
    print("  ✅ achievements")
    
    # 13. جدول player_achievements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            achievement_id TEXT,
            unlocked_at INTEGER,
            progress REAL DEFAULT 0.0,
            is_completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (achievement_id) REFERENCES achievements (achievement_id)
        )
    ''')
    print("  ✅ player_achievements")
    
    # 14. جدول analytics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            user_id INTEGER,
            session_id TEXT,
            timestamp INTEGER,
            data TEXT,
            platform TEXT,
            version TEXT
        )
    ''')
    print("  ✅ analytics")
    
    # 15. جدول replays
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS replays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT,
            user_id INTEGER,
            saved_at INTEGER,
            title TEXT,
            notes TEXT,
            is_public BOOLEAN DEFAULT 1,
            tags TEXT,
            FOREIGN KEY (game_id) REFERENCES games (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    print("  ✅ replays")
    
    # ایجاد ایندکس‌ها
    print("📊 Creating indexes...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_white ON games(white_player_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_black ON games(black_player_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_status ON games(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_moves_game ON moves(game_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_user ON stats(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_friends_user ON friends(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tournaments_status ON tournaments(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_user ON inventory(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_settings_user ON settings(user_id)')
    
    # ذخیره تغییرات
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ Database created successfully!")
    print("=" * 50)
    print(f"   📁 Path: {db_path}")
    print("   📊 Tables: 15")
    print("   🔍 Indexes: 11")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("📊 Creating Chess Database...")
    print("=" * 50)
    create_database()