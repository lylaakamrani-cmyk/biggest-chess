# © 2025 AmirAli Kamrani. All rights reserved.

# core/database.py
import sqlite3
import json
import hashlib
import time
import uuid
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime
import os
import threading
import queue

class Database:
    """SQLite database manager for chess game data"""
    
    def __init__(self, db_path: str = "chess_data.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._lock = threading.Lock()
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize database with all tables"""
        with self._lock:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            
            # Create tables
            self._create_users_table()
            self._create_games_table()
            self._create_moves_table()
            self._create_stats_table()
            self._create_friends_table()
            self._create_messages_table()
            self._create_tournaments_table()
            self._create_tournament_games_table()
            self._create_shop_table()
            self._create_inventory_table()
            self._create_settings_table()
            self._create_achievements_table()
            self._create_player_achievements_table()
            self._create_analytics_table()
            self._create_replays_table()
            
            # Create indexes
            self._create_indexes()
            
    def _create_users_table(self):
        """Create users table"""
        self.cursor.execute('''
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
        
    def _create_games_table(self):
        """Create games table"""
        self.cursor.execute('''
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
        
    def _create_moves_table(self):
        """Create moves table"""
        self.cursor.execute('''
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
        
    def _create_stats_table(self):
        """Create statistics table"""
        self.cursor.execute('''
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
        
    def _create_friends_table(self):
        """Create friends table"""
        self.cursor.execute('''
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
        
    def _create_messages_table(self):
        """Create messages table"""
        self.cursor.execute('''
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
        
    def _create_tournaments_table(self):
        """Create tournaments table"""
        self.cursor.execute('''
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
        
    def _create_tournament_games_table(self):
        """Create tournament games table"""
        self.cursor.execute('''
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
        
    def _create_shop_table(self):
        """Create shop items table"""
        self.cursor.execute('''
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
        
    def _create_inventory_table(self):
        """Create inventory table"""
        self.cursor.execute('''
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
        
    def _create_settings_table(self):
        """Create user settings table"""
        self.cursor.execute('''
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
        
    def _create_achievements_table(self):
        """Create achievements table"""
        self.cursor.execute('''
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
        
    def _create_player_achievements_table(self):
        """Create player achievements table"""
        self.cursor.execute('''
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
        
    def _create_analytics_table(self):
        """Create analytics table"""
        self.cursor.execute('''
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
        
    def _create_replays_table(self):
        """Create game replays table"""
        self.cursor.execute('''
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
        
    def _create_indexes(self):
        """Create database indexes"""
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_white ON games(white_player_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_black ON games(black_player_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_status ON games(status)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_moves_game ON moves(game_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_user ON stats(user_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_friends_user ON friends(user_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_tournaments_status ON tournaments(status)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_user ON inventory(user_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_settings_user ON settings(user_id)')
        
        self.connection.commit()
        
    def create_user(self, username: str, password: str, email: str = None) -> Optional[int]:
        """Create a new user"""
        with self._lock:
            try:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                created_at = int(time.time())
                
                self.cursor.execute('''
                    INSERT INTO users (username, password_hash, email, created_at, rating)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, password_hash, email, created_at, 1200))
                
                user_id = self.cursor.lastrowid
                
                # Create default settings
                self.cursor.execute('''
                    INSERT INTO settings (user_id) VALUES (?)
                ''', (user_id,))
                
                # Create initial stats
                self.cursor.execute('''
                    INSERT INTO stats (user_id, last_updated) VALUES (?, ?)
                ''', (user_id, created_at))
                
                self.connection.commit()
                return user_id
                
            except sqlite3.IntegrityError:
                return None
                
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user"""
        with self._lock:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            self.cursor.execute('''
                SELECT id, username, rating, games_played, wins, losses, draws, is_banned
                FROM users
                WHERE username = ? AND password_hash = ? AND is_active = 1
            ''', (username, password_hash))
            
            row = self.cursor.fetchone()
            if row:
                # Update last login
                self.cursor.execute('''
                    UPDATE users SET last_login = ? WHERE id = ?
                ''', (int(time.time()), row['id']))
                self.connection.commit()
                
                return dict(row)
                
            return None
            
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        with self._lock:
            self.cursor.execute('''
                SELECT * FROM users WHERE id = ?
            ''', (user_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
            
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        with self._lock:
            self.cursor.execute('''
                SELECT * FROM users WHERE username = ?
            ''', (username,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
            
    def update_user_rating(self, user_id: int, new_rating: int):
        """Update user ELO rating"""
        with self._lock:
            self.cursor.execute('''
                UPDATE users SET rating = ? WHERE id = ?
            ''', (new_rating, user_id))
            self.connection.commit()
            
    def update_user_stats(self, user_id: int, result: str):
        """Update user statistics after game"""
        with self._lock:
            self.cursor.execute('''
                UPDATE users
                SET games_played = games_played + 1
                WHERE id = ?
            ''', (user_id,))
            
            if result == 'win':
                self.cursor.execute('''
                    UPDATE users SET wins = wins + 1 WHERE id = ?
                ''', (user_id,))
            elif result == 'loss':
                self.cursor.execute('''
                    UPDATE users SET losses = losses + 1 WHERE id = ?
                ''', (user_id,))
            elif result == 'draw':
                self.cursor.execute('''
                    UPDATE users SET draws = draws + 1 WHERE id = ?
                ''', (user_id,))
                
            self.connection.commit()
            
    def save_game(self, game_data: Dict) -> str:
        """Save a game to database"""
        with self._lock:
            game_id = game_data.get('id', str(uuid.uuid4()))
            
            self.cursor.execute('''
                INSERT INTO games (
                    id, white_player_id, black_player_id, winner, result, pgn,
                    fen_list, status, time_control, rated, started_at, ended_at,
                    moves_count, white_time_used, black_time_used, analysis_data,
                    game_type, tournament_id, platform
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game_id,
                game_data.get('white_player_id'),
                game_data.get('black_player_id'),
                game_data.get('winner'),
                game_data.get('result'),
                game_data.get('pgn'),
                json.dumps(game_data.get('fen_list', [])),
                game_data.get('status', 'completed'),
                game_data.get('time_control', '10+0'),
                game_data.get('rated', 1),
                game_data.get('started_at', int(time.time())),
                game_data.get('ended_at', int(time.time())),
                game_data.get('moves_count', 0),
                game_data.get('white_time_used', 0),
                game_data.get('black_time_used', 0),
                json.dumps(game_data.get('analysis_data', {})),
                game_data.get('game_type', 'standard'),
                game_data.get('tournament_id'),
                game_data.get('platform', 'desktop')
            ))
            
            # Save moves
            if game_data.get('moves'):
                for i, move in enumerate(game_data['moves']):
                    self.cursor.execute('''
                        INSERT INTO moves (
                            game_id, move_number, from_square, to_square, promotion,
                            san, fen_before, fen_after, move_time, player_color,
                            is_capture, is_check, is_checkmate, is_castle, is_en_passant
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        game_id,
                        i + 1,
                        move.get('from_square'),
                        move.get('to_square'),
                        move.get('promotion'),
                        move.get('san'),
                        move.get('fen_before'),
                        move.get('fen_after'),
                        move.get('move_time', 0),
                        move.get('player_color'),
                        move.get('is_capture', 0),
                        move.get('is_check', 0),
                        move.get('is_checkmate', 0),
                        move.get('is_castle', 0),
                        move.get('is_en_passant', 0)
                    ))
                    
            self.connection.commit()
            return game_id
            
    def get_game(self, game_id: str) -> Optional[Dict]:
        """Get a game by ID"""
        with self._lock:
            self.cursor.execute('''
                SELECT * FROM games WHERE id = ?
            ''', (game_id,))
            
            game = self.cursor.fetchone()
            if not game:
                return None
                
            result = dict(game)
            
            # Get moves
            self.cursor.execute('''
                SELECT * FROM moves WHERE game_id = ? ORDER BY move_number
            ''', (game_id,))
            
            result['moves'] = [dict(row) for row in self.cursor.fetchall()]
            
            return result
            
    def get_user_games(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's games"""
        with self._lock:
            self.cursor.execute('''
                SELECT * FROM games
                WHERE white_player_id = ? OR black_player_id = ?
                ORDER BY started_at DESC LIMIT ?
            ''', (user_id, user_id, limit))
            
            return [dict(row) for row in self.cursor.fetchall()]
            
    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Get user statistics"""
        with self._lock:
            self.cursor.execute('''
                SELECT * FROM stats WHERE user_id = ?
            ''', (user_id,))
            
            row = self.cursor.fetchone()
            if row:
                return dict(row)
                
            # Create stats if not exist
            self.cursor.execute('''
                INSERT INTO stats (user_id, last_updated) VALUES (?, ?)
            ''', (user_id, int(time.time())))
            self.connection.commit()
            
            return self.get_user_stats(user_id)
            
    def update_stats(self, user_id: int, stats_data: Dict):
        """Update user statistics"""
        with self._lock:
            updates = []
            values = []
            
            for key, value in stats_data.items():
                updates.append(f"{key} = ?")
                values.append(value)
                
            values.append(user_id)
            
            query = f'''
                UPDATE stats SET {', '.join(updates)}, last_updated = ?
                WHERE user_id = ?
            '''
            
            self.cursor.execute(query, [*values, int(time.time()), user_id])
            self.connection.commit()
            
    def add_friend(self, user_id: int, friend_id: int) -> bool:
        """Add a friend"""
        with self._lock:
            try:
                self.cursor.execute('''
                    INSERT INTO friends (user_id, friend_id, status, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, friend_id, 'pending', int(time.time())))
                
                self.connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False
                
    def accept_friend(self, user_id: int, friend_id: int) -> bool:
        """Accept a friend request"""
        with self._lock:
            self.cursor.execute('''
                UPDATE friends
                SET status = 'accepted', last_interaction = ?
                WHERE user_id = ? AND friend_id = ?
            ''', (int(time.time()), user_id, friend_id))
            
            if self.cursor.rowcount > 0:
                self.connection.commit()
                return True
                
            return False
            
    def get_friends(self, user_id: int) -> List[Dict]:
        """Get user's friends"""
        with self._lock:
            self.cursor.execute('''
                SELECT u.id, u.username, u.rating, f.status, f.created_at
                FROM friends f
                JOIN users u ON f.friend_id = u.id
                WHERE f.user_id = ? AND f.status = 'accepted'
            ''', (user_id,))
            
            friends = [dict(row) for row in self.cursor.fetchall()]
            
            self.cursor.execute('''
                SELECT u.id, u.username, u.rating, f.status, f.created_at
                FROM friends f
                JOIN users u ON f.user_id = u.id
                WHERE f.friend_id = ? AND f.status = 'accepted'
            ''', (user_id,))
            
            friends.extend([dict(row) for row in self.cursor.fetchall()])
            
            return friends
            
    def save_message(self, sender_id: int, receiver_id: int, message: str, msg_type: str = 'chat') -> int:
        """Save a message"""
        with self._lock:
            self.cursor.execute('''
                INSERT INTO messages (sender_id, receiver_id, message, timestamp, message_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (sender_id, receiver_id, message, int(time.time()), msg_type))
            
            self.connection.commit()
            return self.cursor.lastrowid
            
    def get_messages(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's messages"""
        with self._lock:
            self.cursor.execute('''
                SELECT m.*, u.username as sender_username
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.receiver_id = ? OR m.sender_id = ?
                ORDER BY m.timestamp DESC LIMIT ?
            ''', (user_id, user_id, limit))
            
            return [dict(row) for row in self.cursor.fetchall()]
            
    def mark_messages_read(self, user_id: int):
        """Mark messages as read"""
        with self._lock:
            self.cursor.execute('''
                UPDATE messages SET is_read = 1
                WHERE receiver_id = ? AND is_read = 0
            ''', (user_id,))
            self.connection.commit()
            
    def create_tournament(self, tournament_data: Dict) -> str:
        """Create a tournament"""
        with self._lock:
            tournament_id = tournament_data.get('id', str(uuid.uuid4()))
            
            self.cursor.execute('''
                INSERT INTO tournaments (
                    id, name, type, status, max_players, current_players,
                    created_by, created_at, prize_pool, rules, rounds, current_round
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tournament_id,
                tournament_data.get('name', 'Tournament'),
                tournament_data.get('type', 'swiss'),
                tournament_data.get('status', 'waiting'),
                tournament_data.get('max_players', 16),
                1,
                tournament_data.get('created_by'),
                int(time.time()),
                json.dumps(tournament_data.get('prize_pool', {})),
                json.dumps(tournament_data.get('rules', {})),
                tournament_data.get('rounds', 4),
                0
            ))
            
            self.connection.commit()
            return tournament_id
            
    def join_tournament(self, tournament_id: str, user_id: int) -> bool:
        """Join a tournament"""
        with self._lock:
            self.cursor.execute('''
                UPDATE tournaments
                SET current_players = current_players + 1
                WHERE id = ? AND current_players < max_players
            ''', (tournament_id,))
            
            if self.cursor.rowcount > 0:
                self.connection.commit()
                return True
                
            return False
            
    def get_tournaments(self, status: str = None) -> List[Dict]:
        """Get tournaments"""
        with self._lock:
            if status:
                self.cursor.execute('''
                    SELECT * FROM tournaments WHERE status = ? ORDER BY created_at DESC
                ''', (status,))
            else:
                self.cursor.execute('''
                    SELECT * FROM tournaments ORDER BY created_at DESC
                ''')
                
            return [dict(row) for row in self.cursor.fetchall()]
            
    def add_shop_item(self, item_data: Dict) -> bool:
        """Add an item to shop"""
        with self._lock:
            try:
                self.cursor.execute('''
                    INSERT INTO shop_items (
                        item_id, name, description, price, category,
                        type, image_url, created_at, rarity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_data.get('item_id', str(uuid.uuid4())),
                    item_data.get('name'),
                    item_data.get('description'),
                    item_data.get('price', 100),
                    item_data.get('category'),
                    item_data.get('type'),
                    item_data.get('image_url'),
                    int(time.time()),
                    item_data.get('rarity', 'common')
                ))
                
                self.connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False
                
    def get_shop_items(self, category: str = None) -> List[Dict]:
        """Get shop items"""
        with self._lock:
            if category:
                self.cursor.execute('''
                    SELECT * FROM shop_items WHERE category = ? AND is_active = 1
                ''', (category,))
            else:
                self.cursor.execute('''
                    SELECT * FROM shop_items WHERE is_active = 1
                ''')
                
            return [dict(row) for row in self.cursor.fetchall()]
            
    def purchase_item(self, user_id: int, item_id: str) -> bool:
        """Purchase an item"""
        with self._lock:
            # Check if user has enough coins
            self.cursor.execute('''
                SELECT total_coins FROM users WHERE id = ?
            ''', (user_id,))
            
            user = self.cursor.fetchone()
            if not user:
                return False
                
            self.cursor.execute('''
                SELECT price FROM shop_items WHERE item_id = ?
            ''', (item_id,))
            
            item = self.cursor.fetchone()
            if not item:
                return False
                
            if user['total_coins'] < item['price']:
                return False
                
            # Deduct coins
            self.cursor.execute('''
                UPDATE users SET total_coins = total_coins - ?
                WHERE id = ?
            ''', (item['price'], user_id))
            
            # Add to inventory
            self.cursor.execute('''
                INSERT INTO inventory (user_id, item_id, acquired_at)
                VALUES (?, ?, ?)
            ''', (user_id, item_id, int(time.time())))
            
            self.connection.commit()
            return True
            
    def get_inventory(self, user_id: int) -> List[Dict]:
        """Get user's inventory"""
        with self._lock:
            self.cursor.execute('''
                SELECT i.*, s.name, s.description, s.type
                FROM inventory i
                JOIN shop_items s ON i.item_id = s.item_id
                WHERE i.user_id = ?
            ''', (user_id,))
            
            return [dict(row) for row in self.cursor.fetchall()]
            
    def get_user_settings(self, user_id: int) -> Optional[Dict]:
        """Get user settings"""
        with self._lock:
            self.cursor.execute('''
                SELECT * FROM settings WHERE user_id = ?
            ''', (user_id,))
            
            row = self.cursor.fetchone()
            if row:
                return dict(row)
                
            # Create default settings
            self.cursor.execute('''
                INSERT INTO settings (user_id) VALUES (?)
            ''', (user_id,))
            self.connection.commit()
            
            return self.get_user_settings(user_id)
            
    def update_user_settings(self, user_id: int, settings: Dict):
        """Update user settings"""
        with self._lock:
            updates = []
            values = []
            
            for key, value in settings.items():
                updates.append(f"{key} = ?")
                values.append(value)
                
            values.append(user_id)
            
            query = f'''
                UPDATE settings SET {', '.join(updates)} WHERE user_id = ?
            '''
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
    def add_coins(self, user_id: int, amount: int):
        """Add coins to user"""
        with self._lock:
            self.cursor.execute('''
                UPDATE users SET total_coins = total_coins + ? WHERE id = ?
            ''', (amount, user_id))
            self.connection.commit()
            
    def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        """Get leaderboard by rating"""
        with self._lock:
            self.cursor.execute('''
                SELECT id, username, rating, wins, losses, draws, games_played
                FROM users
                WHERE is_active = 1 AND games_played > 0
                ORDER BY rating DESC LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in self.cursor.fetchall()]
            
    def save_replay(self, replay_data: Dict) -> int:
        """Save a game replay"""
        with self._lock:
            self.cursor.execute('''
                INSERT INTO replays (game_id, user_id, saved_at, title, notes, is_public, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                replay_data.get('game_id'),
                replay_data.get('user_id'),
                int(time.time()),
                replay_data.get('title', ''),
                replay_data.get('notes', ''),
                replay_data.get('is_public', 1),
                json.dumps(replay_data.get('tags', []))
            ))
            
            self.connection.commit()
            return self.cursor.lastrowid
            
    def get_replays(self, user_id: int) -> List[Dict]:
        """Get user's replays"""
        with self._lock:
            self.cursor.execute('''
                SELECT * FROM replays WHERE user_id = ? ORDER BY saved_at DESC
            ''', (user_id,))
            
            return [dict(row) for row in self.cursor.fetchall()]
            
    def log_analytics(self, event_data: Dict):
        """Log analytics event"""
        with self._lock:
            self.cursor.execute('''
                INSERT INTO analytics (event_type, user_id, session_id, timestamp, data, platform, version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_data.get('event_type'),
                event_data.get('user_id'),
                event_data.get('session_id', ''),
                int(time.time()),
                json.dumps(event_data.get('data', {})),
                event_data.get('platform', 'desktop'),
                event_data.get('version', '1.0.0')
            ))
            
            self.connection.commit()
            
    def close(self):
        """Close database connection"""
        with self._lock:
            if self.connection:
                self.connection.close()
                
    def backup(self, backup_path: str = None) -> str:
        """Backup database"""
        if not backup_path:
            backup_path = f"chess_backup_{int(time.time())}.db"
            
        with self._lock:
            source = sqlite3.connect(self.db_path)
            backup = sqlite3.connect(backup_path)
            
            source.backup(backup)
            
            backup.close()
            source.close()
            
            return backup_path
            
    def vacuum(self):
        """Optimize database"""
        with self._lock:
            self.cursor.execute('VACUUM')
            self.connection.commit()