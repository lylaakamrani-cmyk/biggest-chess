# © 2025 AmirAli Kamrani. All rights reserved.

# core/ai_engine.py
import chess
import chess.pgn
import json
import random
import math
import time
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum
import threading
import queue
import subprocess
import os

class AIDifficulty(Enum):
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"
    MASTER = "master"

class AIEngine:
    """AI Engine with multiple difficulty levels"""
    
    def __init__(self):
        self.difficulty = AIDifficulty.MEDIUM
        self.depth = 3
        self.time_limit = 2.0  # seconds
        self.nodes_searched = 0
        self.best_move = None
        self.evaluation = 0.0
        self.thinking = False
        self.stop_thinking = False
        
        # Opening book
        self.opening_book = self._load_opening_book()
        
        # Transposition table
        self.transposition_table = {}
        self.tt_size = 1000000
        
        # Search statistics
        self.search_stats = {
            'nodes': 0,
            'captures': 0,
            'checks': 0,
            'mate_found': False
        }
        
        # Stockfish path (optional)
        self.stockfish_path = None
        self.stockfish_process = None
        self.use_stockfish = False
        
    def set_difficulty(self, difficulty: AIDifficulty):
        """Set AI difficulty level"""
        self.difficulty = difficulty
        difficulty_settings = {
            AIDifficulty.BEGINNER: {'depth': 2, 'time': 1.0},
            AIDifficulty.EASY: {'depth': 3, 'time': 1.5},
            AIDifficulty.MEDIUM: {'depth': 4, 'time': 2.0},
            AIDifficulty.HARD: {'depth': 6, 'time': 3.0},
            AIDifficulty.EXPERT: {'depth': 8, 'time': 5.0},
            AIDifficulty.MASTER: {'depth': 12, 'time': 10.0}
        }
        settings = difficulty_settings.get(difficulty, difficulty_settings[AIDifficulty.MEDIUM])
        self.depth = settings['depth']
        self.time_limit = settings['time']
        
    def get_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Get best move for current position"""
        if self.use_stockfish and self.stockfish_path:
            return self._get_stockfish_move(board)
        return self._get_alpha_beta_move(board)
        
    def _get_alpha_beta_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Get best move using alpha-beta pruning"""
        self.thinking = True
        self.stop_thinking = False
        self.nodes_searched = 0
        self.search_stats = {'nodes': 0, 'captures': 0, 'checks': 0, 'mate_found': False}
        
        # Check opening book first
        move = self._check_opening_book(board)
        if move:
            self.best_move = move
            self.thinking = False
            return move
            
        # Initialize best move
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        # Get legal moves and order them
        moves = list(board.legal_moves)
        moves = self._order_moves(board, moves)
        
        # Start search
        start_time = time.time()
        max_depth = self.depth
        
        # Iterative deepening
        for depth in range(1, max_depth + 1):
            if self.stop_thinking or (time.time() - start_time) > self.time_limit:
                break
                
            for move in moves:
                if self.stop_thinking:
                    break
                    
                # Make move
                board.push(move)
                value = -self._alphabeta(board, depth - 1, -beta, -alpha, False)
                board.pop()
                
                # Update best move
                if value > best_value:
                    best_value = value
                    best_move = move
                    
                alpha = max(alpha, value)
                
            # Store best move for this depth
            self.best_move = best_move
            self.evaluation = best_value
            
        self.thinking = False
        return best_move
        
    def _alphabeta(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Alpha-beta search algorithm"""
        self.nodes_searched += 1
        self.search_stats['nodes'] += 1
        
        # Check transposition table
        board_hash = board._transposition_key()
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                if entry['flag'] == 'exact':
                    return entry['value']
                elif entry['flag'] == 'lowerbound':
                    alpha = max(alpha, entry['value'])
                elif entry['flag'] == 'upperbound':
                    beta = min(beta, entry['value'])
                if alpha >= beta:
                    return entry['value']
                    
        # Check terminal positions
        if depth == 0 or board.is_checkmate() or board.is_stalemate():
            return self._evaluate_position(board)
            
        # Get legal moves
        moves = list(board.legal_moves)
        if not moves:
            return self._evaluate_position(board)
            
        # Order moves
        moves = self._order_moves(board, moves)
        
        # Search
        best_value = -float('inf') if maximizing else float('inf')
        best_move = None
        alpha_original = alpha
        beta_original = beta
        
        for move in moves:
            if self.stop_thinking:
                break
                
            board.push(move)
            
            # Track captures and checks for statistics
            captured = board.piece_at(move.to_square)
            if captured:
                self.search_stats['captures'] += 1
            if board.is_check():
                self.search_stats['checks'] += 1
                
            value = -self._alphabeta(board, depth - 1, -beta, -alpha, not maximizing)
            board.pop()
            
            if maximizing:
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, value)
            else:
                if value < best_value:
                    best_value = value
                    best_move = move
                beta = min(beta, value)
                
            if alpha >= beta:
                break
                
        # Store in transposition table
        if len(self.transposition_table) < self.tt_size:
            flag = 'exact'
            if best_value <= alpha_original:
                flag = 'upperbound'
            elif best_value >= beta_original:
                flag = 'lowerbound'
                
            self.transposition_table[board_hash] = {
                'value': best_value,
                'depth': depth,
                'flag': flag,
                'move': best_move
            }
            
        return best_value
        
    def _evaluate_position(self, board: chess.Board) -> float:
        """Evaluate position from white's perspective"""
        if board.is_checkmate():
            return -10000 if board.turn == chess.WHITE else 10000
        if board.is_stalemate():
            return 0
            
        # Piece values
        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Piece square tables (simplified)
        pawn_table = [
            0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5,-10,  0,  0,-10, -5,  5,
            5, 10, 10,-20,-20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0
        ]
        
        knight_table = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50
        ]
        
        bishop_table = [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20
        ]
        
        rook_table = [
            0,  0,  0,  0,  0,  0,  0,  0,
            5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            0,  0,  0,  5,  5,  0,  0,  0
        ]
        
        queen_table = [
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
            -5,  0,  5,  5,  5,  5,  0, -5,
            0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20
        ]
        
        # Material and positional evaluation
        score = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece:
                continue
                
            # Material value
            value = piece_values.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
                
            # Positional value
            square_index = square if piece.color == chess.WHITE else 63 - square
            if piece.piece_type == chess.PAWN:
                score += pawn_table[square_index] if piece.color == chess.WHITE else -pawn_table[square_index]
            elif piece.piece_type == chess.KNIGHT:
                score += knight_table[square_index] if piece.color == chess.WHITE else -knight_table[square_index]
            elif piece.piece_type == chess.BISHOP:
                score += bishop_table[square_index] if piece.color == chess.WHITE else -bishop_table[square_index]
            elif piece.piece_type == chess.ROOK:
                score += rook_table[square_index] if piece.color == chess.WHITE else -rook_table[square_index]
            elif piece.piece_type == chess.QUEEN:
                score += queen_table[square_index] if piece.color == chess.WHITE else -queen_table[square_index]
                
        # Mobility bonus (simplified)
        white_mobility = len(board.attacks(chess.WHITE))
        black_mobility = len(board.attacks(chess.BLACK))
        score += (white_mobility - black_mobility) * 0.5
        
        # Center control bonus
        center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
        for square in center_squares:
            if board.piece_at(square):
                piece = board.piece_at(square)
                if piece.color == chess.WHITE:
                    score += 5
                else:
                    score -= 5
                    
        # Pawn structure evaluation
        score += self._evaluate_pawn_structure(board)
        
        # King safety
        score += self._evaluate_king_safety(board)
        
        # Tempo bonus
        if board.turn == chess.WHITE:
            score += 10
        else:
            score -= 10
            
        return score
        
    def _evaluate_pawn_structure(self, board: chess.Board) -> float:
        """Evaluate pawn structure"""
        score = 0
        
        # White pawns
        for square in board.pieces(chess.PAWN, chess.WHITE):
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            
            # Doubled pawns penalty
            for s in board.pieces(chess.PAWN, chess.WHITE):
                if s != square and chess.square_file(s) == file:
                    score -= 10
                    break
                    
            # Isolated pawn penalty
            has_neighbor = False
            for f in [file - 1, file + 1]:
                if 0 <= f <= 7:
                    for s in board.pieces(chess.PAWN, chess.WHITE):
                        if chess.square_file(s) == f:
                            has_neighbor = True
                            break
                if has_neighbor:
                    break
            if not has_neighbor:
                score -= 15
                
            # Passed pawn bonus
            is_passed = True
            for r in range(rank + 1, 8):
                for f in [file - 1, file, file + 1]:
                    if 0 <= f <= 7:
                        s = chess.square(f, r)
                        piece = board.piece_at(s)
                        if piece and piece.color == chess.BLACK and piece.piece_type == chess.PAWN:
                            is_passed = False
                            break
                if not is_passed:
                    break
            if is_passed:
                score += 20
                
        # Black pawns (mirror)
        for square in board.pieces(chess.PAWN, chess.BLACK):
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            
            for s in board.pieces(chess.PAWN, chess.BLACK):
                if s != square and chess.square_file(s) == file:
                    score += 10
                    break
                    
            has_neighbor = False
            for f in [file - 1, file + 1]:
                if 0 <= f <= 7:
                    for s in board.pieces(chess.PAWN, chess.BLACK):
                        if chess.square_file(s) == f:
                            has_neighbor = True
                            break
                if has_neighbor:
                    break
            if not has_neighbor:
                score += 15
                
            is_passed = True
            for r in range(rank - 1, -1, -1):
                for f in [file - 1, file, file + 1]:
                    if 0 <= f <= 7:
                        s = chess.square(f, r)
                        piece = board.piece_at(s)
                        if piece and piece.color == chess.WHITE and piece.piece_type == chess.PAWN:
                            is_passed = False
                            break
                if not is_passed:
                    break
            if is_passed:
                score -= 20
                
        return score
        
    def _evaluate_king_safety(self, board: chess.Board) -> float:
        """Evaluate king safety"""
        score = 0
        
        # White king
        white_king = board.king(chess.WHITE)
        if white_king:
            # Castled bonus
            if white_king == chess.G1:
                score += 30
            elif white_king == chess.C1:
                score += 20
            else:
                # Pawn shield
                shield = self._count_pawn_shield(board, white_king, chess.WHITE)
                score += shield * 2
                
        # Black king
        black_king = board.king(chess.BLACK)
        if black_king:
            if black_king == chess.G8:
                score -= 30
            elif black_king == chess.C8:
                score -= 20
            else:
                shield = self._count_pawn_shield(board, black_king, chess.BLACK)
                score -= shield * 2
                
        return score
        
    def _count_pawn_shield(self, board: chess.Board, king_square: int, color: chess.Color) -> int:
        """Count pawns protecting the king"""
        rank = chess.square_rank(king_square)
        file = chess.square_file(king_square)
        count = 0
        
        for df in [-1, 0, 1]:
            for dr in [-1, 0, 1]:
                if df == 0 and dr == 0:
                    continue
                new_file = file + df
                new_rank = rank + dr
                if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                    square = chess.square(new_file, new_rank)
                    piece = board.piece_at(square)
                    if piece and piece.color == color and piece.piece_type == chess.PAWN:
                        count += 1
                        
        return count
        
    def _order_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        """Order moves for better search efficiency"""
        move_scores = []
        
        for move in moves:
            score = 0
            
            # Captures
            captured = board.piece_at(move.to_square)
            if captured:
                piece = board.piece_at(move.from_square)
                if piece:
                    # MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
                    victim_value = {
                        chess.PAWN: 100,
                        chess.KNIGHT: 320,
                        chess.BISHOP: 330,
                        chess.ROOK: 500,
                        chess.QUEEN: 900,
                        chess.KING: 20000
                    }
                    attacker_value = {
                        chess.PAWN: 100,
                        chess.KNIGHT: 320,
                        chess.BISHOP: 330,
                        chess.ROOK: 500,
                        chess.QUEEN: 900,
                        chess.KING: 20000
                    }
                    score += victim_value.get(captured.piece_type, 0) * 10
                    score -= attacker_value.get(piece.piece_type, 0)
                    
            # Check
            board.push(move)
            if board.is_check():
                score += 100
            board.pop()
            
            # Promotion
            if move.promotion:
                score += 800
                
            # Center control
            if move.to_square in [chess.E4, chess.D4, chess.E5, chess.D5]:
                score += 20
                
            move_scores.append((move, score))
            
        # Sort by score descending
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, score in move_scores]
        
    def _check_opening_book(self, board: chess.Board) -> Optional[chess.Move]:
        """Check if position is in opening book"""
        fen = board.fen()
        
        # Simplified opening book
        opening_moves = {
            # King's Pawn Opening
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": ["e2e4", "d2d4", "g1f3"],
            # Sicilian Defense
            "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2": ["g1f3", "b1c3", "f1c4"],
            # King's Indian Defense
            "rnbqkb1r/pppppp1p/5np1/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3": ["b1c3", "g1f3", "f1e2"],
            # Queen's Gambit
            "rnbqkb1r/ppp1pppp/5n2/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq d6 0 3": ["c2c3", "b1c3", "c4d5"],
            # Ruy Lopez
            "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4": ["0-0", "f1e1", "d2d3"],
            # Italian Game
            "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4": ["0-0", "d2d3", "b1c3"],
            # French Defense
            "rnbqkbnr/pppp1ppp/8/4p3/3P4/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 2": ["e4e5", "g1f3", "b1c3"],
            # Caro-Kann
            "rnbqkbnr/pp1ppppp/8/2p5/3PP3/8/PPP2PPP/RNBQKBNR b KQkq - 0 2": ["d7d5", "g8f6", "c7c5"]
        }
        
        # Check if position is in book
        if fen in opening_moves:
            moves = opening_moves[fen]
            move = chess.Move.from_uci(random.choice(moves))
            if move in board.legal_moves:
                return move
                
        # Check for transpositions
        for book_fen, moves in opening_moves.items():
            if fen.startswith(book_fen.split(' ')[0]):
                move = chess.Move.from_uci(random.choice(moves))
                if move in board.legal_moves:
                    return move
                    
        return None
        
    def _load_opening_book(self) -> Dict:
        """Load opening book from file"""
        # In production, this would load from a database or file
        return {}
        
    def _get_stockfish_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Get move using Stockfish engine"""
        if not self.stockfish_path:
            return None
            
        try:
            # Start Stockfish if not running
            if not self.stockfish_process:
                self.stockfish_process = subprocess.Popen(
                    [self.stockfish_path, '--quiet'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
            # Send position
            self._stockfish_command(f"position fen {board.fen()}")
            
            # Get best move
            self._stockfish_command(f"go depth {self.depth}")
            
            # Read output
            output = []
            while True:
                line = self.stockfish_process.stdout.readline()
                if not line:
                    break
                output.append(line.strip())
                if line.startswith('bestmove'):
                    break
                    
            # Parse best move
            for line in output:
                if line.startswith('bestmove'):
                    parts = line.split()
                    if len(parts) >= 2:
                        move_uci = parts[1]
                        if move_uci != '(none)':
                            move = chess.Move.from_uci(move_uci)
                            if move in board.legal_moves:
                                return move
                                
        except Exception as e:
            print(f"Stockfish error: {e}")
            
        return None
        
    def _stockfish_command(self, command: str):
        """Send command to Stockfish"""
        if self.stockfish_process:
            self.stockfish_process.stdin.write(command + '\n')
            self.stockfish_process.stdin.flush()
            
    def set_stockfish_path(self, path: str):
        """Set Stockfish executable path"""
        self.stockfish_path = path
        self.use_stockfish = True if path and os.path.exists(path) else False
        
    def stop_search(self):
        """Stop current search"""
        self.stop_thinking = True
        
    def get_search_stats(self) -> Dict:
        """Get search statistics"""
        return self.search_stats
        
    def clear_transposition_table(self):
        """Clear transposition table"""
        self.transposition_table.clear()
        
    def get_evaluation(self) -> float:
        """Get current evaluation"""
        return self.evaluation
        
    def get_best_move_uci(self) -> Optional[str]:
        """Get best move in UCI format"""
        if self.best_move:
            return self.best_move.uci()
        return None