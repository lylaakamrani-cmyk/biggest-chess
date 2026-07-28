# © 2025 AmirAli Kamrani. All rights reserved.

# tests/test_database.py
import unittest
import sys
import os
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Database


class TestDatabase(unittest.TestCase):
    """Test cases for Database class"""
    
    def setUp(self):
        """Setup before each test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.temp_db.name
        self.db = Database(self.db_path)
        
    def tearDown(self):
        """Cleanup after each test"""
        self.db.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
            
    def test_create_user(self):
        """Test creating a user"""
        user_id = self.db.create_user('testuser', 'password123', 'test@email.com')
        self.assertIsNotNone(user_id)
        
        # Try creating duplicate user
        duplicate = self.db.create_user('testuser', 'password456', 'test2@email.com')
        self.assertIsNone(duplicate)
        
    def test_authenticate_user(self):
        """Test user authentication"""
        self.db.create_user('authuser', 'mypassword', 'auth@email.com')
        user = self.db.authenticate_user('authuser', 'mypassword')
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'authuser')
        
        # Wrong password
        user = self.db.authenticate_user('authuser', 'wrongpassword')
        self.assertIsNone(user)
        
    def test_get_user(self):
        """Test getting user by ID"""
        user_id = self.db.create_user('getuser', 'password', 'get@email.com')
        user = self.db.get_user(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'getuser')
        
    def test_update_user_rating(self):
        """Test updating user rating"""
        user_id = self.db.create_user('ratinguser', 'password', 'rating@email.com')
        self.db.update_user_rating(user_id, 1500)
        user = self.db.get_user(user_id)
        self.assertEqual(user['rating'], 1500)
        
    def test_update_user_stats(self):
        """Test updating user stats"""
        user_id = self.db.create_user('statsuser', 'password', 'stats@email.com')
        
        self.db.update_user_stats(user_id, 'win')
        user = self.db.get_user(user_id)
        self.assertEqual(user['games_played'], 1)
        self.assertEqual(user['wins'], 1)
        
        self.db.update_user_stats(user_id, 'loss')
        user = self.db.get_user(user_id)
        self.assertEqual(user['games_played'], 2)
        self.assertEqual(user['losses'], 1)
        
    def test_save_game(self):
        """Test saving a game"""
        user_id = self.db.create_user('gameuser', 'password', 'game@email.com')
        
        game_data = {
            'white_player_id': user_id,
            'black_player_id': user_id,
            'result': 'white_win',
            'pgn': '1. e4 e5 2. Nf3 Nc6',
            'status': 'completed',
            'moves_count': 2
        }
        
        game_id = self.db.save_game(game_data)
        self.assertIsNotNone(game_id)
        
        saved_game = self.db.get_game(game_id)
        self.assertIsNotNone(saved_game)
        self.assertEqual(saved_game['result'], 'white_win')
        
    def test_get_user_games(self):
        """Test getting user games"""
        user_id = self.db.create_user('gamesuser', 'password', 'games@email.com')
        
        for i in range(3):
            game_data = {
                'white_player_id': user_id,
                'black_player_id': user_id,
                'result': 'draw',
                'pgn': f'Game {i}',
                'status': 'completed',
                'moves_count': i + 1
            }
            self.db.save_game(game_data)
            
        games = self.db.get_user_games(user_id)
        self.assertEqual(len(games), 3)
        
    def test_add_friend(self):
        """Test adding a friend"""
        user1_id = self.db.create_user('friend1', 'pass', 'f1@email.com')
        user2_id = self.db.create_user('friend2', 'pass', 'f2@email.com')
        
        result = self.db.add_friend(user1_id, user2_id)
        self.assertTrue(result)
        
        friends = self.db.get_friends(user1_id)
        self.assertTrue(len(friends) > 0)
        
    def test_shop_items(self):
        """Test shop items"""
        item_data = {
            'item_id': 'test_item_1',
            'name': 'Test Item',
            'description': 'Test Description',
            'price': 100,
            'category': 'theme',
            'type': 'board',
            'rarity': 'common'
        }
        
        result = self.db.add_shop_item(item_data)
        self.assertTrue(result)
        
        items = self.db.get_shop_items()
        self.assertTrue(len(items) > 0)
        
    def test_get_leaderboard(self):
        """Test getting leaderboard"""
        for i in range(3):
            user_id = self.db.create_user(f'player{i}', 'pass', f'p{i}@email.com')
            self.db.update_user_rating(user_id, 1200 + i * 100)
            
        leaderboard = self.db.get_leaderboard(10)
        self.assertTrue(len(leaderboard) > 0)
        # Check sorting by rating
        self.assertTrue(leaderboard[0]['rating'] >= leaderboard[-1]['rating'])


def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()