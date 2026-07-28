# © 2025 AmirAli Kamrani. All rights reserved.

# data/init_data.py
import sqlite3
import time
import os

class DataInitializer:
    def __init__(self, db_path="data/chess_data.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        if self.conn:
            self.conn.close()
            
    def init_all(self):
        self.connect()
        
        # بررسی وجود جدول users
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not self.cursor.fetchone():
            print("❌ Database not initialized! Please run create_database.py first.")
            self.close()
            return
            
        self.init_users()
        self.init_shop()
        self.init_achievements()
        self.init_settings()
        self.close()
        print("\n✅ All data initialized!")
        
    def init_users(self):
        print("📊 Creating users...")
        users = [
            ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin@chess.com', int(time.time()), 1500, 0, 0, 0, 0, 1, 0, 'IR', 'Chess Master', 1000, 5, 500),
            ('guest', 'guest_hash', 'guest@chess.com', int(time.time()), 1200, 0, 0, 0, 0, 1, 0, 'US', 'Guest Player', 0, 1, 0),
            ('player1', 'player1_hash', 'p1@chess.com', int(time.time()), 1300, 0, 0, 0, 0, 1, 0, 'UK', 'Player One', 100, 2, 50),
            ('player2', 'player2_hash', 'p2@chess.com', int(time.time()), 1400, 0, 0, 0, 0, 1, 0, 'DE', 'Player Two', 150, 3, 100)
        ]
        
        for user in users:
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO users (
                        username, password_hash, email, created_at, rating,
                        games_played, wins, losses, draws,
                        is_active, is_banned, country, bio,
                        total_coins, level, experience
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', user)
            except Exception as e:
                print(f"Error: {e}")
            
        self.conn.commit()
        print(f"  ✅ {len(users)} users created")
        
    def init_shop(self):
        print("📊 Creating shop items...")
        items = [
            ('theme_classic', 'Classic Theme', 'Classic chess board theme', 0, 'theme', 'board', 'classic', 1, int(time.time()), 0, 'common'),
            ('theme_dark', 'Dark Theme', 'Dark chess board theme', 100, 'theme', 'board', 'dark', 1, int(time.time()), 0, 'common'),
            ('theme_neon', 'Neon Theme', 'Neon chess board theme', 200, 'theme', 'board', 'neon', 1, int(time.time()), 0, 'rare'),
            ('piece_classic', 'Classic Pieces', 'Classic chess pieces', 0, 'piece', 'pieces', 'classic', 1, int(time.time()), 0, 'common'),
            ('piece_modern', 'Modern Pieces', 'Modern chess pieces', 150, 'piece', 'pieces', 'modern', 1, int(time.time()), 0, 'uncommon'),
            ('piece_gold', 'Gold Pieces', 'Gold chess pieces', 500, 'piece', 'pieces', 'gold', 1, int(time.time()), 0, 'legendary')
        ]
        
        for item in items:
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO shop_items (
                        item_id, name, description, price, category,
                        type, image_url, is_active, created_at, discount, rarity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', item)
            except Exception as e:
                print(f"Error: {e}")
            
        self.conn.commit()
        print(f"  ✅ {len(items)} shop items created")
        
    def init_achievements(self):
        print("📊 Creating achievements...")
        achievements = [
            ('first_game', 'First Move', 'Play your first game', '🎯', 10, 'progress', 'games_played>=1'),
            ('first_win', 'First Victory', 'Win your first game', '🏆', 20, 'progress', 'wins>=1'),
            ('games_10', 'Active Player', 'Play 10 games', '🎮', 15, 'progress', 'games_played>=10'),
            ('rating_1400', 'Bronze Level', 'Reach 1400 rating', '🥉', 25, 'rating', 'rating>=1400'),
            ('rating_1600', 'Silver Level', 'Reach 1600 rating', '🥈', 50, 'rating', 'rating>=1600')
        ]
        
        for ach in achievements:
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO achievements (
                        achievement_id, name, description, icon,
                        points, category, requirement
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', ach)
            except Exception as e:
                print(f"Error: {e}")
            
        self.conn.commit()
        print(f"  ✅ {len(achievements)} achievements created")
        
    def init_settings(self):
        print("📊 Creating settings...")
        self.cursor.execute('SELECT id FROM users')
        users = self.cursor.fetchall()
        
        for user in users:
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO settings (user_id) VALUES (?)
                ''', (user[0],))
            except Exception as e:
                print(f"Error: {e}")
            
        self.conn.commit()
        print(f"  ✅ Settings created for {len(users)} users")

def main():
    print("=" * 50)
    print("📊 Data Initializer")
    print("=" * 50)
    
    init = DataInitializer()
    init.init_all()

if __name__ == "__main__":
    main()