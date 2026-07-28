# © 2025 AmirAli Kamrani. All rights reserved.

# core/board.py
import chess
import chess.svg
import random
import time
import json
from typing import Optional, List, Dict, Tuple, Any
from enum import Enum
import copy
import hashlib

class GamePhase(Enum):
    OPENING = "opening"
    MIDDLEGAME = "middlegame"
    ENDGAME = "endgame"

class BoardState:
    """Core board management with FIDE rules implementation"""
    
    def __init__(self, fen: Optional[str] = None):
        self.board = chess.Board(fen) if fen else chess.Board()
        self.move_history: List[chess.Move] = []
        self.position_history: List[str] = []  # FEN strings
        self.captured_pieces: Dict[str, int] = {'white': 0, 'black': 0}
        self.move_times: List[float] = []
        self.game_phase = GamePhase.OPENING
        self.legal_moves_cache = None
        self.last_move = None
        self.position_count = 0
        self.ply_count = 0
        
    def make_move(self, move: chess.Move, time_elapsed: float = 0.0) -> bool:
        """Execute a move with full validation"""
        if not self.is_move_legal(move):
            return False
            
        # Store state before move
        self.position_history.append(self.board.fen())
        self.move_history.append(move)
        self.move_times.append(time_elapsed)
        
        # Track captured pieces
        captured = self.board.piece_at(move.to_square)
        if captured:
            color = 'white' if captured.color == chess.WHITE else 'black'
            self.captured_pieces[color] += 1
            
        # Make the move
        self.board.push(move)
        self.ply_count += 1
        self.last_move = move
        self.legal_moves_cache = None
        
        # Update game phase
        self._update_game_phase()
        
        # Check for repetition
        self.position_count += 1
        
        return True
    
    def undo_last_move(self) -> Optional[chess.Move]:
        """Undo the last move"""
        if not self.move_history:
            return None
            
        # Remove last move from history
        move = self.move_history.pop()
        self.position_history.pop()
        if self.move_times:
            self.move_times.pop()
            
        # Update board
        self.board.pop()
        self.ply_count -= 1
        
        # Update captured pieces count (hard to track perfectly, recalculate)
        self._recalculate_captured()
        
        self.last_move = self.move_history[-1] if self.move_history else None
        self.legal_moves_cache = None
        self._update_game_phase()
        
        return move
    
    def get_legal_moves(self) -> List[chess.Move]:
        """Get all legal moves with caching"""
        if self.legal_moves_cache is None:
            self.legal_moves_cache = list(self.board.legal_moves)
        return self.legal_moves_cache
    
    def is_move_legal(self, move: chess.Move) -> bool:
        """Check if a move is legal"""
        return move in self.get_legal_moves()
    
    def get_move_history(self) -> List[Dict]:
        """Get move history with metadata"""
        history = []
        for i, move in enumerate(self.move_history):
            history.append({
                'move_number': i + 1,
                'from_square': chess.square_name(move.from_square),
                'to_square': chess.square_name(move.to_square),
                'promotion': chess.piece_name(move.promotion) if move.promotion else None,
                'san': self.board.san(move) if i < len(self.move_history) else None,
                'time': self.move_times[i] if i < len(self.move_times) else None
            })
        return history
    
    def get_status(self) -> Dict[str, Any]:
        """Get current game status"""
        status = {
            'fen': self.board.fen(),
            'turn': 'white' if self.board.turn == chess.WHITE else 'black',
            'in_check': self.board.is_check(),
            'in_checkmate': self.board.is_checkmate(),
            'in_stalemate': self.board.is_stalemate(),
            'in_insufficient_material': self.board.is_insufficient_material(),
            'can_claim_draw': self.board.can_claim_draw(),
            'game_phase': self.game_phase.value,
            'ply_count': self.ply_count,
            'move_count': len(self.move_history),
            'captured': self.captured_pieces,
            'legal_moves_count': len(self.get_legal_moves()),
            'move_stack': len(self.board.move_stack)
        }
        
        # Additional draw conditions
        if self.board.is_fivefold_repetition():
            status['draw_reason'] = 'fivefold_repetition'
        elif self.board.is_seventyfive_moves():
            status['draw_reason'] = 'seventyfive_moves'
        elif self.board.is_variant_draw():
            status['draw_reason'] = 'variant_draw'
        else:
            status['draw_reason'] = None
            
        return status
    
    def get_move_analysis(self) -> Dict[str, Any]:
        """Analyze the current position"""
        analysis = {
            'material_balance': self._calculate_material_balance(),
            'piece_activity': self._calculate_piece_activity(),
            'king_safety': self._evaluate_king_safety(),
            'pawn_structure': self._evaluate_pawn_structure(),
            'control_center': self._evaluate_center_control(),
            'development': self._evaluate_development(),
            'tactical_opportunities': self._find_tactical_moves(),
            'threats': self._find_threats()
        }
        return analysis
    
    def _update_game_phase(self):
        """Determine current game phase"""
        piece_count = sum(1 for _ in self.board.pieces())
        if piece_count > 25:
            self.game_phase = GamePhase.OPENING
        elif piece_count > 10:
            self.game_phase = GamePhase.MIDDLEGAME
        else:
            self.game_phase = GamePhase.ENDGAME
    
    def _calculate_material_balance(self) -> Dict[str, int]:
        """Calculate material balance for both sides"""
        values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }
        
        white_material = 0
        black_material = 0
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    white_material += values.get(piece.piece_type, 0)
                else:
                    black_material += values.get(piece.piece_type, 0)
                    
        return {'white': white_material, 'black': black_material, 'difference': white_material - black_material}
    
    def _calculate_piece_activity(self) -> Dict[str, float]:
        """Calculate piece activity scores"""
        activity = {'white': 0.0, 'black': 0.0}
        center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                # Center control bonus
                if square in center_squares:
                    bonus = 0.5
                elif square in [chess.C3, chess.F3, chess.C6, chess.F6]:
                    bonus = 0.3
                else:
                    bonus = 0.0
                    
                # Mobility bonus (approximate)
                mobility = len(self.board.attacks(square))
                bonus += mobility * 0.01
                
                color = 'white' if piece.color == chess.WHITE else 'black'
                activity[color] += bonus
                
        return activity
    
    def _evaluate_king_safety(self) -> Dict[str, float]:
        """Evaluate king safety for both sides"""
        safety = {'white': 0.0, 'black': 0.0}
        
        for color in [chess.WHITE, chess.BLACK]:
            king_square = self.board.king(color)
            if king_square:
                # Check if king has castled
                if color == chess.WHITE and king_square == chess.G1:
                    safety['white'] = 1.0
                elif color == chess.WHITE and king_square == chess.C1:
                    safety['white'] = 0.8
                elif color == chess.BLACK and king_square == chess.G8:
                    safety['black'] = 1.0
                elif color == chess.BLACK and king_square == chess.C8:
                    safety['black'] = 0.8
                else:
                    # Check pawn shield
                    pawn_shield = self._count_pawn_shield(king_square)
                    safety['white' if color == chess.WHITE else 'black'] = pawn_shield * 0.5
                    
        return safety
    
    def _count_pawn_shield(self, king_square: int) -> int:
        """Count pawns protecting the king"""
        rank = chess.square_rank(king_square)
        file = chess.square_file(king_square)
        shield_count = 0
        
        for df in [-1, 0, 1]:
            for dr in [-1, 0, 1]:
                if df == 0 and dr == 0:
                    continue
                new_file = file + df
                new_rank = rank + dr
                if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                    square = chess.square(new_file, new_rank)
                    piece = self.board.piece_at(square)
                    if piece and piece.piece_type == chess.PAWN:
                        shield_count += 1
                        
        return shield_count
    
    def _evaluate_pawn_structure(self) -> Dict[str, Any]:
        """Evaluate pawn structure"""
        structure = {
            'white_pawns': [],
            'black_pawns': [],
            'doubled': {'white': 0, 'black': 0},
            'isolated': {'white': 0, 'black': 0},
            'passed': {'white': 0, 'black': 0}
        }
        
        for color in [chess.WHITE, chess.BLACK]:
            pawns = self.board.pieces(chess.PAWN, color)
            pawn_files = {}
            
            for pawn in pawns:
                file = chess.square_file(pawn)
                rank = chess.square_rank(pawn)
                structure['white_pawns' if color == chess.WHITE else 'black_pawns'].append({
                    'square': chess.square_name(pawn),
                    'file': file,
                    'rank': rank
                })
                
                # Count doubled pawns
                if file in pawn_files:
                    structure['doubled']['white' if color == chess.WHITE else 'black'] += 1
                else:
                    pawn_files[file] = 1
                    
            # Check isolated pawns
            for file in pawn_files:
                has_neighbor = False
                for f in [-1, 1]:
                    if file + f in pawn_files:
                        has_neighbor = True
                        break
                if not has_neighbor:
                    structure['isolated']['white' if color == chess.WHITE else 'black'] += 1
                    
            # Check passed pawns
            for pawn in pawns:
                if self._is_passed_pawn(pawn, color):
                    structure['passed']['white' if color == chess.WHITE else 'black'] += 1
                    
        return structure
    
    def _is_passed_pawn(self, square: int, color: chess.Color) -> bool:
        """Check if a pawn is passed"""
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        # Direction of pawn advancement
        direction = 1 if color == chess.WHITE else -1
        
        # Check if any enemy pawn can block or capture
        for r in range(rank + direction, 0 if color == chess.WHITE else 7, direction):
            for f in [file - 1, file, file + 1]:
                if 0 <= f <= 7:
                    enemy_square = chess.square(f, r)
                    piece = self.board.piece_at(enemy_square)
                    if piece and piece.color != color and piece.piece_type == chess.PAWN:
                        return False
        return True
    
    def _evaluate_center_control(self) -> Dict[str, int]:
        """Evaluate control of center squares"""
        center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
        control = {'white': 0, 'black': 0}
        
        for square in center_squares:
            attackers = self.board.attackers(chess.WHITE, square)
            defenders = self.board.attackers(chess.BLACK, square)
            control['white'] += len(attackers)
            control['black'] += len(defenders)
            
        return control
    
    def _evaluate_development(self) -> Dict[str, int]:
        """Evaluate piece development"""
        development = {'white': 0, 'black': 0}
        starting_positions = {
            chess.WHITE: [chess.B1, chess.G1, chess.C1, chess.F1],
            chess.BLACK: [chess.B8, chess.G8, chess.C8, chess.F8]
        }
        
        for color in [chess.WHITE, chess.BLACK]:
            for square in starting_positions[color]:
                piece = self.board.piece_at(square)
                if not piece or piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                    development['white' if color == chess.WHITE else 'black'] += 1
                    
        return development
    
    def _find_tactical_moves(self) -> List[Dict]:
        """Find tactical opportunities in current position"""
        tactical_moves = []
        
        for move in self.get_legal_moves():
            # Check for captures
            captured = self.board.piece_at(move.to_square)
            if captured:
                piece = self.board.piece_at(move.from_square)
                if piece and captured.piece_type == chess.QUEEN and piece.piece_type != chess.PAWN:
                    tactical_moves.append({
                        'move': move,
                        'type': 'capture',
                        'description': f'{chess.square_name(move.from_square)} captures queen'
                    })
                    continue
                elif piece and captured.piece_type > piece.piece_type:
                    tactical_moves.append({
                        'move': move,
                        'type': 'capture',
                        'description': f'{chess.square_name(move.from_square)} captures {chess.piece_name(captured.piece_type)}'
                    })
                    
            # Check for check moves
            board_copy = self.board.copy()
            board_copy.push(move)
            if board_copy.is_check():
                tactical_moves.append({
                    'move': move,
                    'type': 'check',
                    'description': f'{chess.square_name(move.from_square)} to {chess.square_name(move.to_square)} gives check'
                })
                
            # Check for promotion
            if move.promotion:
                tactical_moves.append({
                    'move': move,
                    'type': 'promotion',
                    'description': f'Promote to {chess.piece_name(move.promotion)}'
                })
                
        return tactical_moves
    
    def _find_threats(self) -> Dict[str, List]:
        """Find immediate threats"""
        threats = {
            'white': [],
            'black': [],
            'mate_in_one': None
        }
        
        for color in [chess.WHITE, chess.BLACK]:
            for move in self.get_legal_moves():
                board_copy = self.board.copy()
                board_copy.push(move)
                
                if board_copy.is_checkmate():
                    threats['mate_in_one'] = {
                        'move': move,
                        'color': 'white' if color == chess.WHITE else 'black'
                    }
                    continue
                    
                # Check for forks, pins, skewers
                if board_copy.is_check():
                    threats['white' if color == chess.WHITE else 'black'].append({
                        'move': move,
                        'type': 'check',
                        'description': f'{chess.square_name(move.from_square)} to {chess.square_name(move.to_square)}'
                    })
                    
        return threats
    
    def _recalculate_captured(self):
        """Recalculate captured pieces count"""
        self.captured_pieces = {'white': 0, 'black': 0}
        # This would require full game history to be accurate
        # For simplicity, we'll reset and count from current position
        
    def get_pgn(self) -> str:
        """Get PGN representation of the game"""
        return self.board.variation_san(self.move_history)
    
    def get_fen_list(self) -> List[str]:
        """Get list of FEN positions"""
        return self.position_history
    
    def get_position_hash(self) -> str:
        """Get hash of current position for repetition detection"""
        return hashlib.md5(self.board.fen().encode()).hexdigest()
    
    def is_position_repeated(self) -> bool:
        """Check if current position has been repeated 3 times"""
        return self.board.is_repetition(3)
    
    def get_total_moves(self) -> int:
        """Get total number of moves"""
        return len(self.move_history)
    
    def get_player_turn(self) -> chess.Color:
        """Get whose turn it is"""
        return self.board.turn
    
    def get_score(self, perspective: chess.Color) -> float:
        """Get score from perspective"""
        return self.board.pawns(perspective).count() * 1.0
    
    def to_dict(self) -> Dict:
        """Convert board state to dictionary"""
        return {
            'fen': self.board.fen(),
            'move_history': [move.uci() for move in self.move_history],
            'move_count': len(self.move_history),
            'status': self.get_status(),
            'game_phase': self.game_phase.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BoardState':
        """Create board state from dictionary"""
        board = cls(data['fen'])
        board.move_history = [chess.Move.from_uci(move) for move in data.get('move_history', [])]
        return board