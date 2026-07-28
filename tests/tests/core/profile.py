# © 2025 AmirAli Kamrani. All rights reserved.

# core/profile.py
import time
import json
import hashlib
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
import math

from core.database import Database

class UserRank(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    LEGENDARY = "legendary"

class UserProfile:
    """User profile manager with stats, achievements, and progression"""
    
    def __init__(self, db: Database):
        self.db = db
        self.user_data = None
        self.stats = None
        self.settings = None
        self.inventory = []
        self.friends = []
        self.achievements = []
        self.current_user_id = None
        self._cache = {}
        self._cache_time = {}
        self._cache_duration = 60  # seconds
        
    def load_profile(self, user_id: int) -> bool:
        """Load user profile data"""
        self.current_user_id = user_id
        
        # Load user data
        self.user_data = self.db.get_user(user_id)
        if not self.user_data:
            return False
            
        # Load stats
        self.stats = self.db.get_user_stats(user_id)
        
        # Load settings
        self.settings = self.db.get_user_settings(user_id)
        
        # Load inventory
        self.inventory = self.db.get_inventory(user_id)
        
        # Load friends
        self.friends = self.db.get_friends(user_id)
        
        # Load achievements
        self.achievements = self._load_achievements(user_id)
        
        return True
        
    def create_profile(self, username: str, password: str, email: str = None) -> Optional[int]:
        """Create new user profile"""
        user_id = self.db.create_user(username, password, email)
        if user_id:
            self.load_profile(user_id)
            return user_id
        return None
        
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and load profile"""
        user = self.db.authenticate_user(username, password)
        if user:
            self.load_profile(user['id'])
            return user
        return None
        
    def get_profile_data(self) -> Dict:
        """Get complete profile data"""
        return {
            'user': self.user_data,
            'stats': self.stats,
            'settings': self.settings,
            'inventory': self.inventory,
            'friends': self.friends,
            'achievements': self.achievements,
            'rank': self.get_rank(),
            'level': self.get_level(),
            'progress_to_next_level': self.get_level_progress(),
            'total_games': self.get_total_games(),
            'win_rate': self.get_win_rate(),
            'streak': self.get_current_streak()
        }
        
    def get_rank(self) -> Dict:
        """Get user rank based on rating"""
        rating = self.user_data.get('rating', 1200)
        
        rank_info = {
            'name': 'Bronze',
            'tier': UserRank.BRONZE,
            'color': '#CD7F32',
            'icon': '🥉',
            'min_rating': 0,
            'max_rating': 1399
        }
        
        if rating >= 2800:
            rank_info = {'name': 'Legendary', 'tier': UserRank.LEGENDARY, 'color': '#FFD700', 'icon': '👑', 'min_rating': 2800, 'max_rating': float('inf')}
        elif rating >= 2600:
            rank_info = {'name': 'Grandmaster', 'tier': UserRank.GRANDMASTER, 'color': '#FF6B00', 'icon': '⭐', 'min_rating': 2600, 'max_rating': 2799}
        elif rating >= 2400:
            rank_info = {'name': 'Master', 'tier': UserRank.MASTER, 'color': '#FF4500', 'icon': '🏆', 'min_rating': 2400, 'max_rating': 2599}
        elif rating >= 2200:
            rank_info = {'name': 'Diamond', 'tier': UserRank.DIAMOND, 'color': '#00BFFF', 'icon': '💎', 'min_rating': 2200, 'max_rating': 2399}
        elif rating >= 2000:
            rank_info = {'name': 'Platinum', 'tier': UserRank.PLATINUM, 'color': '#E5E4E2', 'icon': '🔷', 'min_rating': 2000, 'max_rating': 2199}
        elif rating >= 1800:
            rank_info = {'name': 'Gold', 'tier': UserRank.GOLD, 'color': '#FFD700', 'icon': '🥇', 'min_rating': 1800, 'max_rating': 1999}
        elif rating >= 1600:
            rank_info = {'name': 'Silver', 'tier': UserRank.SILVER, 'color': '#C0C0C0', 'icon': '🥈', 'min_rating': 1600, 'max_rating': 1799}
        elif rating >= 1400:
            rank_info = {'name': 'Bronze', 'tier': UserRank.BRONZE, 'color': '#CD7F32', 'icon': '🥉', 'min_rating': 1400, 'max_rating': 1599}
        else:
            rank_info = {'name': 'Beginner', 'tier': UserRank.BRONZE, 'color': '#808080', 'icon': '🎯', 'min_rating': 0, 'max_rating': 1399}
            
        rank_info['rating'] = rating
        rank_info['next_rank_rating'] = rank_info['max_rating'] + 1 if rank_info['max_rating'] != float('inf') else None
        rank_info['progress_to_next'] = (rating - rank_info['min_rating']) / (rank_info['max_rating'] - rank_info['min_rating']) * 100 if rank_info['max_rating'] != float('inf') else 100
        
        return rank_info
        
    def get_level(self) -> Dict:
        """Get user level and progression"""
        exp = self.user_data.get('experience', 0)
        
        # Level formula: level = floor(sqrt(exp/100)) + 1
        level = int(math.sqrt(exp / 100)) + 1
        exp_for_level = level * 100 * level  # exp needed for current level
        exp_next_level = (level + 1) * 100 * (level + 1)
        
        return {
            'level': level,
            'experience': exp,
            'exp_for_level': exp_for_level,
            'exp_for_next_level': exp_next_level,
            'progress': (exp - exp_for_level) / (exp_next_level - exp_for_level) * 100 if exp_next_level > exp_for_level else 100,
            'title': self._get_level_title(level)
        }
        
    def _get_level_title(self, level: int) -> str:
        """Get title for level"""
        titles = {
            1: 'Beginner',
            5: 'Novice',
            10: 'Amateur',
            20: 'Apprentice',
            30: 'Adept',
            40: 'Expert',
            50: 'Master',
            75: 'Grandmaster',
            100: 'Legendary'
        }
        
        for lvl, title in sorted(titles.items(), reverse=True):
            if level >= lvl:
                return title
        return 'Beginner'
        
    def get_level_progress(self) -> float:
        """Get progress to next level as percentage"""
        level_info = self.get_level()
        return level_info.get('progress', 0)
        
    def get_total_games(self) -> int:
        """Get total games played"""
        return self.user_data.get('games_played', 0)
        
    def get_win_rate(self) -> float:
        """Get win rate percentage"""
        wins = self.user_data.get('wins', 0)
        total = self.get_total_games()
        if total == 0:
            return 0
        return (wins / total) * 100
        
    def get_current_streak(self) -> Dict:
        """Get current win streak"""
        # This would need to be calculated from game history
        # For now, return data from stats
        return {
            'current': self.stats.get('current_win_streak', 0),
            'best': self.stats.get('longest_win_streak', 0)
        }
        
    def update_rating(self, new_rating: int):
        """Update user rating"""
        self.db.update_user_rating(self.current_user_id, new_rating)
        self.user_data['rating'] = new_rating
        
    def update_stats(self, result: str, game_data: Dict = None):
        """Update user statistics after game"""
        self.db.update_user_stats(self.current_user_id, result)
        
        # Update stats table
        stats_update = {}
        
        if result == 'win':
            stats_update['total_wins'] = self.stats.get('total_wins', 0) + 1
            stats_update['current_win_streak'] = self.stats.get('current_win_streak', 0) + 1
            if stats_update['current_win_streak'] > self.stats.get('longest_win_streak', 0):
                stats_update['longest_win_streak'] = stats_update['current_win_streak']
        elif result == 'loss':
            stats_update['total_losses'] = self.stats.get('total_losses', 0) + 1
            stats_update['current_win_streak'] = 0
        elif result == 'draw':
            stats_update['total_draws'] = self.stats.get('total_draws', 0) + 1
            stats_update['current_win_streak'] = 0
            
        stats_update['total_games'] = self.stats.get('total_games', 0) + 1
        
        # Update game-specific stats
        if game_data:
            stats_update['total_moves'] = self.stats.get('total_moves', 0) + game_data.get('moves_count', 0)
            stats_update['total_captures'] = self.stats.get('total_captures', 0) + game_data.get('captures', 0)
            stats_update['total_checks'] = self.stats.get('total_checks', 0) + game_data.get('checks', 0)
            stats_update['total_checkmates'] = self.stats.get('total_checkmates', 0) + game_data.get('checkmates', 0)
            
        self.db.update_stats(self.current_user_id, stats_update)
        
        # Update user table
        self.user_data['games_played'] = self.user_data.get('games_played', 0) + 1
        if result == 'win':
            self.user_data['wins'] = self.user_data.get('wins', 0) + 1
        elif result == 'loss':
            self.user_data['losses'] = self.user_data.get('losses', 0) + 1
        elif result == 'draw':
            self.user_data['draws'] = self.user_data.get('draws', 0) + 1
            
        # Add experience
        exp_gain = self._calculate_exp_gain(result)
        self.user_data['experience'] = self.user_data.get('experience', 0) + exp_gain
        
        # Reload stats
        self.stats = self.db.get_user_stats(self.current_user_id)
        
    def _calculate_exp_gain(self, result: str) -> int:
        """Calculate experience gain from game"""
        base_exp = 10
        rating_bonus = max(0, self.user_data.get('rating', 1200) - 1200) // 100
        
        if result == 'win':
            return base_exp + rating_bonus + 5
        elif result == 'draw':
            return base_exp // 2 + rating_bonus // 2
        else:  # loss
            return max(1, base_exp // 3)
            
    def add_experience(self, amount: int):
        """Add experience directly"""
        self.user_data['experience'] = self.user_data.get('experience', 0) + amount
        self.db.cursor.execute('''
            UPDATE users SET experience = ? WHERE id = ?
        ''', (self.user_data['experience'], self.current_user_id))
        self.db.connection.commit()
        
    def add_coins(self, amount: int):
        """Add coins to user"""
        self.db.add_coins(self.current_user_id, amount)
        self.user_data['total_coins'] = self.user_data.get('total_coins', 0) + amount
        
    def spend_coins(self, amount: int) -> bool:
        """Spend coins"""
        if self.user_data.get('total_coins', 0) >= amount:
            self.user_data['total_coins'] -= amount
            self.db.cursor.execute('''
                UPDATE users SET total_coins = ? WHERE id = ?
            ''', (self.user_data['total_coins'], self.current_user_id))
            self.db.connection.commit()
            return True
        return False
        
    def get_user_statistics(self) -> Dict:
        """Get comprehensive user statistics"""
        return {
            'overall': {
                'games_played': self.user_data.get('games_played', 0),
                'wins': self.user_data.get('wins', 0),
                'losses': self.user_data.get('losses', 0),
                'draws': self.user_data.get('draws', 0),
                'win_rate': self.get_win_rate()
            },
            'rating': {
                'current': self.user_data.get('rating', 1200),
                'best': self.stats.get('best_rating', 1200),
                'worst': self.stats.get('worst_rating', 1200)
            },
            'streaks': {
                'current': self.stats.get('current_win_streak', 0),
                'best': self.stats.get('longest_win_streak', 0)
            },
            'game_stats': {
                'total_moves': self.stats.get('total_moves', 0),
                'avg_time_per_move': self.stats.get('avg_time_per_move', 0),
                'total_captures': self.stats.get('total_captures', 0),
                'total_checks': self.stats.get('total_checks', 0),
                'total_checkmates': self.stats.get('total_checkmates', 0),
                'total_castles': self.stats.get('total_castles', 0)
            },
            'openings': {
                'favorite': self.stats.get('favorite_opening', 'Unknown'),
                'played': json.loads(self.stats.get('openings_played', '{}')) if self.stats else {}
            },
            'level': self.get_level(),
            'rank': self.get_rank()
        }
        
    def _load_achievements(self, user_id: int) -> List[Dict]:
        """Load user achievements"""
        self.db.cursor.execute('''
            SELECT pa.*, a.name, a.description, a.icon, a.points, a.category
            FROM player_achievements pa
            JOIN achievements a ON pa.achievement_id = a.achievement_id
            WHERE pa.user_id = ?
        ''', (user_id,))
        
        return [dict(row) for row in self.db.cursor.fetchall()]
        
    def check_achievements(self):
        """Check and unlock achievements"""
        achievements_to_check = [
            {'id': 'first_game', 'name': 'First Move', 'desc': 'Play your first game', 'points': 10},
            {'id': 'first_win', 'name': 'First Victory', 'desc': 'Win your first game', 'points': 20},
            {'id': 'win_streak_3', 'name': 'On Fire', 'desc': 'Win 3 games in a row', 'points': 30},
            {'id': 'win_streak_5', 'name': 'Unstoppable', 'desc': 'Win 5 games in a row', 'points': 50},
            {'id': 'win_streak_10', 'name': 'Legendary', 'desc': 'Win 10 games in a row', 'points': 100},
            {'id': 'games_10', 'name': 'Active Player', 'desc': 'Play 10 games', 'points': 15},
            {'id': 'games_50', 'name': 'Dedicated', 'desc': 'Play 50 games', 'points': 30},
            {'id': 'games_100', 'name': 'Chess Enthusiast', 'desc': 'Play 100 games', 'points': 50},
            {'id': 'games_500', 'name': 'Chess Master', 'desc': 'Play 500 games', 'points': 100},
            {'id': 'rating_1400', 'name': 'Bronze Level', 'desc': 'Reach 1400 rating', 'points': 25},
            {'id': 'rating_1600', 'name': 'Silver Level', 'desc': 'Reach 1600 rating', 'points': 50},
            {'id': 'rating_1800', 'name': 'Gold Level', 'desc': 'Reach 1800 rating', 'points': 75},
            {'id': 'rating_2000', 'name': 'Platinum Level', 'desc': 'Reach 2000 rating', 'points': 100},
            {'id': 'rating_2200', 'name': 'Diamond Level', 'desc': 'Reach 2200 rating', 'points': 150},
            {'id': 'rating_2400', 'name': 'Master Level', 'desc': 'Reach 2400 rating', 'points': 200},
            {'id': 'checkmate_10', 'name': 'Checkmate Artist', 'desc': 'Deliver 10 checkmates', 'points': 25},
            {'id': 'checkmate_100', 'name': 'Checkmate Expert', 'desc': 'Deliver 100 checkmates', 'points': 75},
            {'id': 'capture_100', 'name': 'Piece Collector', 'desc': 'Capture 100 pieces', 'points': 30},
            {'id': 'capture_500', 'name': 'Grand Collector', 'desc': 'Capture 500 pieces', 'points': 60}
        ]
        
        # Check each achievement
        for achievement in achievements_to_check:
            self._unlock_achievement(achievement['id'])
            
    def _unlock_achievement(self, achievement_id: str):
        """Unlock an achievement"""
        # Check if already unlocked
        for ach in self.achievements:
            if ach['achievement_id'] == achievement_id and ach['is_completed']:
                return
                
        # Check requirements
        if self._check_achievement_requirements(achievement_id):
            self.db.cursor.execute('''
                INSERT OR REPLACE INTO player_achievements (user_id, achievement_id, unlocked_at, is_completed)
                VALUES (?, ?, ?, ?)
            ''', (self.current_user_id, achievement_id, int(time.time()), 1))
            self.db.connection.commit()
            
            # Add achievement points as coins
            self.db.cursor.execute('''
                SELECT points FROM achievements WHERE achievement_id = ?
            ''', (achievement_id,))
            row = self.db.cursor.fetchone()
            if row:
                self.add_coins(row['points'])
                
            self.achievements = self._load_achievements(self.current_user_id)
            
    def _check_achievement_requirements(self, achievement_id: str) -> bool:
        """Check if achievement requirements are met"""
        stats = self.get_user_statistics()
        
        requirements = {
            'first_game': lambda: stats['overall']['games_played'] >= 1,
            'first_win': lambda: stats['overall']['wins'] >= 1,
            'win_streak_3': lambda: stats['streaks']['best'] >= 3,
            'win_streak_5': lambda: stats['streaks']['best'] >= 5,
            'win_streak_10': lambda: stats['streaks']['best'] >= 10,
            'games_10': lambda: stats['overall']['games_played'] >= 10,
            'games_50': lambda: stats['overall']['games_played'] >= 50,
            'games_100': lambda: stats['overall']['games_played'] >= 100,
            'games_500': lambda: stats['overall']['games_played'] >= 500,
            'rating_1400': lambda: stats['rating']['current'] >= 1400,
            'rating_1600': lambda: stats['rating']['current'] >= 1600,
            'rating_1800': lambda: stats['rating']['current'] >= 1800,
            'rating_2000': lambda: stats['rating']['current'] >= 2000,
            'rating_2200': lambda: stats['rating']['current'] >= 2200,
            'rating_2400': lambda: stats['rating']['current'] >= 2400,
            'checkmate_10': lambda: stats['game_stats']['total_checkmates'] >= 10,
            'checkmate_100': lambda: stats['game_stats']['total_checkmates'] >= 100,
            'capture_100': lambda: stats['game_stats']['total_captures'] >= 100,
            'capture_500': lambda: stats['game_stats']['total_captures'] >= 500
        }
        
        if achievement_id in requirements:
            return requirements[achievement_id]()
        return False
        
    def add_friend(self, username: str) -> bool:
        """Add a friend by username"""
        friend = self.db.get_user_by_username(username)
        if not friend or friend['id'] == self.current_user_id:
            return False
            
        return self.db.add_friend(self.current_user_id, friend['id'])
        
    def get_friend_requests(self) -> List[Dict]:
        """Get pending friend requests"""
        self.db.cursor.execute('''
            SELECT u.id, u.username, u.rating, f.created_at
            FROM friends f
            JOIN users u ON f.user_id = u.id
            WHERE f.friend_id = ? AND f.status = 'pending'
        ''', (self.current_user_id,))
        
        return [dict(row) for row in self.db.cursor.fetchall()]
        
    def accept_friend(self, friend_id: int) -> bool:
        """Accept a friend request"""
        return self.db.accept_friend(self.current_user_id, friend_id)
        
    def update_settings(self, settings: Dict) -> bool:
        """Update user settings"""
        self.db.update_user_settings(self.current_user_id, settings)
        self.settings = self.db.get_user_settings(self.current_user_id)
        return True
        
    def get_daily_reward(self) -> Dict:
        """Get daily reward status"""
        today = int(time.time()) // 86400  # day number
        
        # Check if already claimed today
        self.db.cursor.execute('''
            SELECT * FROM analytics
            WHERE user_id = ? AND event_type = 'daily_reward' AND timestamp > ?
            ORDER BY timestamp DESC LIMIT 1
        ''', (self.current_user_id, int(time.time()) - 86400))
        
        if self.db.cursor.fetchone():
            return {'claimed': True, 'message': 'Already claimed today'}
            
        # Calculate streak
        self.db.cursor.execute('''
            SELECT timestamp FROM analytics
            WHERE user_id = ? AND event_type = 'daily_reward'
            ORDER BY timestamp DESC
        ''', (self.current_user_id,))
        
        rows = self.db.cursor.fetchall()
        streak = 0
        
        if rows:
            last_claim = rows[0]['timestamp']
            days_ago = (int(time.time()) - last_claim) // 86400
            
            if days_ago == 1:
                streak = 1  # Continue streak (would need to count previous days)
                
        # Reward amount increases with streak
        base_reward = 50
        streak_bonus = min(streak * 10, 100)
        reward = base_reward + streak_bonus
        
        # Claim reward
        self.add_coins(reward)
        
        # Log claim
        self.db.log_analytics({
            'event_type': 'daily_reward',
            'user_id': self.current_user_id,
            'data': {'reward': reward, 'streak': streak}
        })
        
        return {
            'claimed': True,
            'reward': reward,
            'streak': streak,
            'message': f'Claimed {reward} coins!'
        }
        
    def get_avatar_url(self) -> str:
        """Get user avatar URL"""
        if self.user_data and self.user_data.get('avatar'):
            return self.user_data['avatar']
        return f"https://ui-avatars.com/api/?name={self.user_data.get('username', 'U')}&size=128&background=random"
        
    def update_avatar(self, avatar_url: str):
        """Update user avatar"""
        self.db.cursor.execute('''
            UPDATE users SET avatar = ? WHERE id = ?
        ''', (avatar_url, self.current_user_id))
        self.db.connection.commit()
        self.user_data['avatar'] = avatar_url
        
    def get_game_history(self, limit: int = 20) -> List[Dict]:
        """Get user's game history"""
        return self.db.get_user_games(self.current_user_id, limit)
        
    def get_rating_history(self) -> List[Dict]:
        """Get rating history over time"""
        self.db.cursor.execute('''
            SELECT timestamp, data FROM analytics
            WHERE user_id = ? AND event_type = 'rating_change'
            ORDER BY timestamp ASC
        ''', (self.current_user_id,))
        
        history = []
        for row in self.db.cursor.fetchall():
            data = json.loads(row['data'])
            history.append({
                'timestamp': row['timestamp'],
                'rating': data.get('new_rating'),
                'change': data.get('change')
            })
            
        return history
        
    def get_opponent_stats(self, opponent_id: int) -> Dict:
        """Get stats against specific opponent"""
        # Get games against opponent
        self.db.cursor.execute('''
            SELECT * FROM games
            WHERE (white_player_id = ? AND black_player_id = ?)
            OR (white_player_id = ? AND black_player_id = ?)
            ORDER BY started_at DESC
        ''', (self.current_user_id, opponent_id, opponent_id, self.current_user_id))
        
        games = self.db.cursor.fetchall()
        
        wins = 0
        losses = 0
        draws = 0
        
        for game in games:
            if game['winner'] == 'white' and game['white_player_id'] == self.current_user_id:
                wins += 1
            elif game['winner'] == 'black' and game['black_player_id'] == self.current_user_id:
                wins += 1
            elif game['result'] == 'draw':
                draws += 1
            else:
                losses += 1
                
        return {
            'games_played': len(games),
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': (wins / len(games) * 100) if len(games) > 0 else 0
        }