# © 2025 AmirAli Kamrani. All rights reserved.

# tests/test_ai.py
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_engine import AIEngine, AIDifficulty
import chess


class TestAI(unittest.TestCase):
    """Test cases for AIEngine class"""
    
    def setUp(self):
        """Setup before each test"""
        self.ai = AIEngine()
        
    def test_difficulty_setting(self):
        """Test setting difficulty levels"""
        self.ai.set_difficulty(AIDifficulty.BEGINNER)
        self.assertEqual(self.ai.difficulty, AIDifficulty.BEGINNER)
        self.assertEqual(self.ai.depth, 2)
        
        self.ai.set_difficulty(AIDifficulty.MASTER)
        self.assertEqual(self.ai.difficulty, AIDifficulty.MASTER)
        self.assertEqual(self.ai.depth, 12)
        
    def test_get_best_move(self):
        """Test getting best move"""
        board = chess.Board()
        self.ai.set_difficulty(AIDifficulty.BEGINNER)
        move = self.ai.get_best_move(board)
        self.assertIsNotNone(move)
        self.assertTrue(move in board.legal_moves)
        
    def test_evaluate_position(self):
        """Test position evaluation"""
        board = chess.Board()
        score = self.ai._evaluate_position(board)
        self.assertEqual(score, 0)  # Starting position is equal
        
    def test_checkmate_evaluation(self):
        """Test checkmate evaluation"""
        board = chess.Board('rnb1kbnr/pppp1ppp/8/4p3/5PPq/8/PPPPP2P/RNBQKBNR w KQkq - 1 4')
        score = self.ai._evaluate_position(board)
        self.assertTrue(score < 0 or score > 0)  # Not equal
        
    def test_order_moves(self):
        """Test move ordering"""
        board = chess.Board()
        moves = list(board.legal_moves)
        ordered = self.ai._order_moves(board, moves)
        self.assertEqual(len(ordered), len(moves))
        
    def test_clear_transposition_table(self):
        """Test clearing transposition table"""
        board = chess.Board()
        self.ai.get_best_move(board)
        self.assertTrue(len(self.ai.transposition_table) > 0)
        self.ai.clear_transposition_table()
        self.assertEqual(len(self.ai.transposition_table), 0)
        
    def test_search_stats(self):
        """Test search statistics"""
        board = chess.Board()
        self.ai.get_best_move(board)
        stats = self.ai.get_search_stats()
        self.assertIn('nodes', stats)
        self.assertIn('captures', stats)
        self.assertIn('checks', stats)


def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()''