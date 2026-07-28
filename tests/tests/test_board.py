# © 2025 AmirAli Kamrani. All rights reserved.

# tests/test_board.py
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.board import BoardState
import chess


class TestBoard(unittest.TestCase):
    """Test cases for BoardState class"""
    
    def setUp(self):
        """Setup before each test"""
        self.board = BoardState()
        
    def test_initial_position(self):
        """Test initial board position"""
        fen = self.board.board.fen()
        self.assertEqual(fen, 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        
    def test_make_move(self):
        """Test making a move"""
        move = chess.Move.from_uci('e2e4')
        result = self.board.make_move(move)
        self.assertTrue(result)
        self.assertEqual(len(self.board.move_history), 1)
        
    def test_legal_moves(self):
        """Test getting legal moves"""
        moves = self.board.get_legal_moves()
        self.assertTrue(len(moves) > 0)
        self.assertEqual(len(moves), 20)  # Initial position has 20 legal moves
        
    def test_undo_move(self):
        """Test undoing a move"""
        move = chess.Move.from_uci('e2e4')
        self.board.make_move(move)
        self.assertEqual(len(self.board.move_history), 1)
        
        undone = self.board.undo_last_move()
        self.assertIsNotNone(undone)
        self.assertEqual(len(self.board.move_history), 0)
        
    def test_get_status(self):
        """Test getting game status"""
        status = self.board.get_status()
        self.assertEqual(status['turn'], 'white')
        self.assertFalse(status['in_check'])
        self.assertFalse(status['in_checkmate'])
        self.assertEqual(status['move_count'], 0)
        
    def test_is_checkmate(self):
        """Test checkmate detection"""
        # Fool's mate position
        fen = 'rnb1kbnr/pppp1ppp/8/4p3/5PPq/8/PPPPP2P/RNBQKBNR w KQkq - 1 4'
        self.board = BoardState(fen)
        self.assertTrue(self.board.board.is_check())
        
    def test_get_move_history(self):
        """Test getting move history"""
        self.board.make_move(chess.Move.from_uci('e2e4'))
        self.board.make_move(chess.Move.from_uci('e7e5'))
        history = self.board.get_move_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['from_square'], 'e2')
        self.assertEqual(history[0]['to_square'], 'e4')
        
    def test_get_pgn(self):
        """Test getting PGN"""
        self.board.make_move(chess.Move.from_uci('e2e4'))
        self.board.make_move(chess.Move.from_uci('e7e5'))
        pgn = self.board.get_pgn()
        self.assertIn('e4', pgn)
        self.assertIn('e5', pgn)


def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()