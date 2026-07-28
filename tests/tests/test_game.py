# © 2025 AmirAli Kamrani. All rights reserved.

# tests/test_game.py
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game_logic import GameLogic, GameConfig, GameMode
import chess


class TestGame(unittest.TestCase):
    """Test cases for GameLogic class"""
    
    def setUp(self):
        """Setup before each test"""
        self.config = GameConfig()
        self.game = GameLogic(self.config)
        
    def test_game_start(self):
        """Test starting a game"""
        self.game.start_game(GameMode.LOCAL)
        self.assertEqual(self.game.status.value, 'in_progress')
        
    def test_make_move(self):
        """Test making a move in game"""
        self.game.start_game(GameMode.LOCAL)
        move = chess.Move.from_uci('e2e4')
        result = self.game.make_move(move)
        self.assertTrue(result['success'])
        self.assertEqual(self.game.move_count, 1)
        
    def test_illegal_move(self):
        """Test illegal move in game"""
        self.game.start_game(GameMode.LOCAL)
        move = chess.Move.from_uci('e2e5')  # Illegal move
        result = self.game.make_move(move)
        self.assertFalse(result['success'])
        self.assertEqual(self.game.move_count, 0)
        
    def test_game_over_checkmate(self):
        """Test checkmate detection"""
        self.game.start_game(GameMode.LOCAL)
        # Fool's mate
        moves = ['f2f3', 'e7e5', 'g2g4', 'd8h4']
        for move_uci in moves:
            move = chess.Move.from_uci(move_uci)
            self.game.make_move(move)
        status = self.game.get_game_state()
        self.assertEqual(status['status'], 'completed')
        self.assertEqual(status['result'], 'black_win')
        
    def test_takeback(self):
        """Test takeback functionality"""
        self.game.config.allow_takeback = True
        self.game.start_game(GameMode.LOCAL)
        self.game.make_move(chess.Move.from_uci('e2e4'))
        self.game.make_move(chess.Move.from_uci('e7e5'))
        self.assertEqual(self.game.move_count, 2)
        
        result = self.game.takeback(1)
        self.assertTrue(result)
        self.assertEqual(self.game.move_count, 1)
        
    def test_resign(self):
        """Test resign functionality"""
        self.game.start_game(GameMode.LOCAL)
        result = self.game.resign(chess.WHITE)
        self.assertTrue(result)
        self.assertEqual(self.game.status.value, 'completed')
        self.assertEqual(self.game.result.value, 'black_win')
        
    def test_draw_offer(self):
        """Test draw offer functionality"""
        self.game.start_game(GameMode.LOCAL)
        result = self.game.offer_draw(chess.WHITE)
        self.assertTrue(result)
        
    def test_get_legal_moves(self):
        """Test getting legal moves from game"""
        self.game.start_game(GameMode.LOCAL)
        moves = self.game.get_legal_moves()
        self.assertTrue(len(moves) > 0)
        
    def test_get_game_state(self):
        """Test getting game state"""
        self.game.start_game(GameMode.LOCAL)
        state = self.game.get_game_state()
        self.assertIn('board', state)
        self.assertIn('status', state)
        self.assertIn('move_count', state)


def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()