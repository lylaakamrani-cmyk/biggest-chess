# © 2025 AmirAli Kamrani. All rights reserved.

# core/game_logic.py
import chess
import chess.pgn
import json
import time
from typing import Optional, Dict, List, Tuple, Any, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import threading
import queue

# ✅ تغییر: import مطلق به جای نسبی
from core.board import BoardState

class GamePhase(Enum):
    OPENING = "opening"
    MIDDLEGAME = "middlegame"
    ENDGAME = "endgame"

class GameMode(Enum):
    LOCAL = "local"
    AI = "ai"
    ONLINE = "online"
    SPECTATOR = "spectator"
    TOURNAMENT = "tournament"

class GameResult(Enum):
    WHITE_WIN = "white_win"
    BLACK_WIN = "black_win"
    DRAW = "draw"
    IN_PROGRESS = "in_progress"
    ABANDONED = "abandoned"

class GameStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

@dataclass
class GameConfig:
    """Game configuration settings"""
    time_control: str = "10+0"
    initial_time: int = 600
    increment: int = 0
    max_moves: int = 0
    allow_takeback: bool = False
    allow_draw_offer: bool = True
    allow_resign: bool = True
    allow_undo: bool = False
    rated: bool = True
    variant: str = "standard"
    board_theme: str = "classic"
    piece_theme: str = "classic"
    animation_speed: float = 1.0

class GameLogic:
    """Core game logic manager"""
    
    def __init__(self, config: GameConfig = None):
        self.board = BoardState()
        self.config = config or GameConfig()
        self.mode = GameMode.LOCAL
        self.status = GameStatus.NOT_STARTED
        self.result = GameResult.IN_PROGRESS
        
        # Players
        self.white_player = None
        self.black_player = None
        self.current_player = None
        
        # Timer
        self.white_time = self.config.initial_time
        self.black_time = self.config.initial_time
        self.time_start = None
        self.last_move_time = None
        self.timer_active = False
        
        # Move tracking
        self.move_count = 0
        self.half_move_count = 0
        self.moves_since_capture = 0
        self.moves_since_pawn = 0
        
        # Draw offers
        self.draw_offered_by = None
        self.draw_offered_time = None
        
        # State
        self.analysis = None
        self.move_analysis_history = []
        self.game_events = []
        self.event_listeners = []
        
        # Threading
        self.analysis_queue = queue.Queue()
        self.analysis_thread = None
        self.running = False
        
    def start_game(self, mode: GameMode = GameMode.LOCAL):
        """Start the game"""
        self.mode = mode
        self.status = GameStatus.IN_PROGRESS
        self.result = GameResult.IN_PROGRESS
        self.board = BoardState()
        self.white_time = self.config.initial_time
        self.black_time = self.config.initial_time
        self.move_count = 0
        self.half_move_count = 0
        self.moves_since_capture = 0
        self.moves_since_pawn = 0
        self.timer_active = True
        self.time_start = time.time()
        self.current_player = chess.WHITE
        self._notify_listeners('game_started', {'mode': mode.value})
        
        # Start analysis thread
        self._start_analysis_thread()
        
    def make_move(self, move: chess.Move) -> Dict[str, Any]:
        """Execute a move"""
        if self.status != GameStatus.IN_PROGRESS:
            return {'success': False, 'error': 'Game not in progress'}
            
        if not self.board.is_move_legal(move):
            return {'success': False, 'error': 'Illegal move'}
            
        # Check time
        time_elapsed = self._get_time_elapsed()
        if time_elapsed > self._get_current_time():
            return {'success': False, 'error': 'Time out'}
            
        # Store state
        old_board = self.board.board.fen()
        old_move_count = self.move_count
        
        # Execute move
        success = self.board.make_move(move, time_elapsed)
        if not success:
            return {'success': False, 'error': 'Failed to make move'}
            
        # Update counts
        self.move_count += 1
        self.half_move_count += 1
        
        # Check if capture or pawn move
        captured = self.board.board.piece_at(move.to_square)
        if captured or self.board.board.piece_at(move.from_square).piece_type == chess.PAWN:
            self.moves_since_capture = 0
            self.moves_since_pawn = 0
        else:
            self.moves_since_capture += 1
            self.moves_since_pawn += 1
            
        # Update timer
        self._update_timer(time_elapsed)
        self.last_move_time = time.time()
        
        # Check game end
        game_end = self._check_game_end()
        if game_end:
            self.status = GameStatus.COMPLETED
            self.result = game_end['result']
            self.timer_active = False
            self._notify_listeners('game_ended', game_end)
            
        # Analysis
        self.analysis = self.board.get_move_analysis()
        self.move_analysis_history.append({
            'move': move.uci(),
            'position': old_board,
            'analysis': self.analysis,
            'time': time_elapsed
        })
        
        self._notify_listeners('move_made', {
            'move': move.uci(),
            'from': chess.square_name(move.from_square),
            'to': chess.square_name(move.to_square),
            'status': game_end
        })
        
        return {
            'success': True,
            'move': move.uci(),
            'status': self.status.value,
            'result': self.result.value if self.result != GameResult.IN_PROGRESS else None,
            'analysis': self.analysis
        }
        
    def get_legal_moves(self, square: int = None) -> List[chess.Move]:
        """Get legal moves for a square or all legal moves"""
        if square is None:
            return self.board.get_legal_moves()
        return [move for move in self.board.get_legal_moves() if move.from_square == square]
        
    def get_move_suggestions(self, count: int = 3) -> List[Dict]:
        """Get suggested moves"""
        moves = self.board.get_legal_moves()
        scored_moves = []
        for move in moves[:10]:
            board_copy = self.board.board.copy()
            board_copy.push(move)
            score = self._evaluate_position(board_copy)
            scored_moves.append({
                'move': move.uci(),
                'from': chess.square_name(move.from_square),
                'to': chess.square_name(move.to_square),
                'promotion': move.promotion,
                'score': score
            })
        scored_moves.sort(key=lambda x: x['score'], reverse=True)
        return scored_moves[:count]
        
    def offer_draw(self, player: chess.Color) -> bool:
        """Offer a draw"""
        if not self.config.allow_draw_offer:
            return False
        if self.draw_offered_by is not None:
            if self.draw_offered_by != player:
                self.status = GameStatus.COMPLETED
                self.result = GameResult.DRAW
                self.timer_active = False
                self._notify_listeners('game_ended', {'result': 'draw', 'reason': 'draw_agreement'})
                return True
            return False
            
        self.draw_offered_by = player
        self.draw_offered_time = time.time()
        self._notify_listeners('draw_offered', {'player': 'white' if player == chess.WHITE else 'black'})
        return True
        
    def resign(self, player: chess.Color) -> bool:
        """Resign the game"""
        if not self.config.allow_resign:
            return False
            
        self.status = GameStatus.COMPLETED
        self.result = GameResult.BLACK_WIN if player == chess.WHITE else GameResult.WHITE_WIN
        self.timer_active = False
        self._notify_listeners('game_ended', {
            'result': self.result.value,
            'reason': 'resignation',
            'resigned': 'white' if player == chess.WHITE else 'black'
        })
        return True
        
    def takeback(self, moves: int = 1) -> bool:
        """Takeback moves"""
        if not self.config.allow_takeback:
            return False
            
        for _ in range(min(moves, len(self.board.move_history))):
            if not self.board.undo_last_move():
                return False
                
        self._notify_listeners('takeback', {'moves': moves})
        return True
        
    def _check_game_end(self) -> Optional[Dict]:
        """Check if game has ended"""
        board = self.board.board
        
        if board.is_checkmate():
            winner = 'black' if board.turn == chess.WHITE else 'white'
            return {
                'result': GameResult.WHITE_WIN if winner == 'white' else GameResult.BLACK_WIN,
                'reason': 'checkmate',
                'winner': winner
            }
            
        if board.is_stalemate():
            return {'result': GameResult.DRAW, 'reason': 'stalemate'}
            
        if board.is_insufficient_material():
            return {'result': GameResult.DRAW, 'reason': 'insufficient_material'}
            
        if board.is_fivefold_repetition():
            return {'result': GameResult.DRAW, 'reason': 'fivefold_repetition'}
            
        if board.is_seventyfive_moves():
            return {'result': GameResult.DRAW, 'reason': 'seventyfive_moves'}
            
        if self._get_current_time() <= 0:
            player = 'white' if self.current_player == chess.WHITE else 'black'
            winner = 'black' if player == 'white' else 'white'
            return {
                'result': GameResult.WHITE_WIN if winner == 'white' else GameResult.BLACK_WIN,
                'reason': 'timeout',
                'winner': winner,
                'loser': player
            }
            
        if self.config.max_moves > 0 and self.move_count >= self.config.max_moves:
            return {'result': GameResult.DRAW, 'reason': 'maximum_moves'}
            
        return None
        
    def _evaluate_position(self, board: chess.Board) -> float:
        """Basic position evaluation"""
        if board.is_checkmate():
            return -1000 if board.turn == chess.WHITE else 1000
            
        piece_values = {
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
            piece = board.piece_at(square)
            if piece:
                value = piece_values.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    white_material += value
                else:
                    black_material += value
                    
        return white_material - black_material
        
    def _get_time_elapsed(self) -> float:
        """Get time elapsed since last move"""
        if self.time_start is None:
            return 0
        return time.time() - self.time_start
        
    def _get_current_time(self) -> float:
        """Get current time remaining for current player"""
        if self.current_player == chess.WHITE:
            return self.white_time - self._get_time_elapsed()
        else:
            return self.black_time - self._get_time_elapsed()
            
    def _update_timer(self, elapsed: float):
        """Update timer after move"""
        if self.current_player == chess.WHITE:
            self.white_time -= elapsed
            self.white_time += self.config.increment
        else:
            self.black_time -= elapsed
            self.black_time += self.config.increment
            
        self.current_player = chess.BLACK if self.current_player == chess.WHITE else chess.WHITE
        self.time_start = time.time()
        
    def _start_analysis_thread(self):
        """Start background analysis thread"""
        self.running = True
        self.analysis_thread = threading.Thread(target=self._analysis_worker, daemon=True)
        self.analysis_thread.start()
        
    def _analysis_worker(self):
        """Background analysis worker"""
        while self.running and self.status == GameStatus.IN_PROGRESS:
            try:
                if not self.analysis_queue.empty():
                    analysis_request = self.analysis_queue.get()
                    if analysis_request['type'] == 'position':
                        result = self.board.get_move_analysis()
                        self._notify_listeners('analysis_updated', result)
                time.sleep(0.1)
            except Exception as e:
                print(f"Analysis error: {e}")
                
    def add_event_listener(self, listener: Callable):
        """Add event listener"""
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable):
        """Remove event listener"""
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            
    def _notify_listeners(self, event_type: str, data: Dict):
        """Notify all event listeners"""
        for listener in self.event_listeners:
            try:
                listener(event_type, data)
            except Exception as e:
                print(f"Error in event listener: {e}")
                
    def get_game_state(self) -> Dict[str, Any]:
        """Get complete game state"""
        return {
            'board': self.board.to_dict(),
            'status': self.status.value,
            'result': self.result.value,
            'mode': self.mode.value,
            'white_time': self.white_time,
            'black_time': self.black_time,
            'current_player': 'white' if self.current_player == chess.WHITE else 'black',
            'move_count': self.move_count,
            'half_move_count': self.half_move_count,
            'moves_since_capture': self.moves_since_capture,
            'moves_since_pawn': self.moves_since_pawn,
            'draw_offered_by': self.draw_offered_by,
            'analysis': self.analysis,
            'history': self.move_analysis_history[-10:] if self.move_analysis_history else [],
            'config': {
                'time_control': self.config.time_control,
                'rated': self.config.rated,
                'variant': self.config.variant
            }
        }
        
    def to_pgn(self) -> str:
        """Convert game to PGN format"""
        game = chess.pgn.Game()
        game.headers["Event"] = "Chess Game"
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        game.headers["White"] = "White"
        game.headers["Black"] = "Black"
        game.headers["Result"] = self.result.value.replace('_', '-')
        game.headers["TimeControl"] = self.config.time_control
        
        node = game
        for move in self.board.move_history:
            node = node.add_variation(move)
            
        return str(game)
        
    def from_pgn(self, pgn: str):
        """Load game from PGN"""
        game = chess.pgn.read_game(pgn)
        if game:
            self.board = BoardState()
            for move in game.main_line():
                self.board.make_move(move)
                
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=1)