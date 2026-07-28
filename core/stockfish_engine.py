# © 2025 AmirAli Kamrani. All rights reserved.

# core/stockfish_engine.py
import chess
import chess.engine
import chess.polyglot  # ✅ اضافه شد
import json
import subprocess
import threading
import queue
import time
import os
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum
import tempfile
import shutil

class EngineMode(Enum):
    ANALYSIS = "analysis"
    PLAY = "play"
    TRAINING = "training"
    PUZZLE = "puzzle"

class EngineLevel(Enum):
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    LEVEL_8 = 8

class StockfishEngine:
    """Advanced Stockfish engine wrapper with full control"""
    
    def __init__(self, stockfish_path: str = None, book_path: str = None):
        self.stockfish_path = stockfish_path or self._find_stockfish()
        self.book_path = book_path or "book.bin"
        self.engine = None
        self.engine_process = None
        self.is_ready = False
        self.is_thinking = False
        self.current_position = None
        
        # Engine configuration
        self.config = {
            'Threads': 4,
            'Hash': 256,
            'UCI_Chess960': False,
            'UCI_ShowWDL': True,
            'Move_Overhead': 10,
            'Skill_Level': 20,
            'Contempt': 0,
            'SyzygyPath': '',
            'SyzygyProbeDepth': 1
        }
        
        # Search configuration
        self.search_config = {
            'depth': 18,
            'time': 2000,
            'nodes': 1000000,
            'mate': 0,
            'movetime': 0
        }
        
        # Analysis data
        self.analysis_data = []
        self.best_move = None
        self.score = 0
        self.mate_found = False
        self.pv = []
        self.depth_reached = 0
        self.nodes_searched = 0
        self.time_used = 0
        
        # Evaluation cache
        self.eval_cache = {}
        self.cache_size = 10000
        
        # Threading
        self.analysis_queue = queue.Queue()
        self.analysis_thread = None
        self.stop_analysis = False
        self.analysis_result = None
        
        # Temporary directory for tablebases
        self.temp_dir = None
        
        self._initialize_engine()
        
    def _find_stockfish(self) -> Optional[str]:
        """Find Stockfish executable in common locations"""
        paths = [
            'stockfish',
            'stockfish.exe',
            '/usr/bin/stockfish',
            '/usr/local/bin/stockfish',
            '/opt/homebrew/bin/stockfish',
            'C:/Program Files/Stockfish/stockfish.exe',
            'C:/Stockfish/stockfish.exe',
            './stockfish',
            './stockfish.exe',
            '../stockfish',
            '../stockfish.exe'
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
                
        android_paths = [
            '/storage/emulated/0/stockfish',
            '/data/data/com.termux/files/usr/bin/stockfish'
        ]
        for path in android_paths:
            if os.path.exists(path):
                return path
                
        return None
        
    def _initialize_engine(self):
        """Initialize the Stockfish engine"""
        if not self.stockfish_path or not os.path.exists(self.stockfish_path):
            print(f"Stockfish not found at {self.stockfish_path}")
            return
            
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            self.engine_process = self.engine
            
            for key, value in self.config.items():
                try:
                    self.engine.configure({key: value})
                except Exception as e:
                    print(f"Failed to configure {key}: {e}")
                    
            self.is_ready = True
            print(f"Stockfish engine initialized at {self.stockfish_path}")
            
        except Exception as e:
            print(f"Failed to initialize Stockfish: {e}")
            self.is_ready = False
            
    def set_config(self, **kwargs):
        """Set engine configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                if self.is_ready:
                    try:
                        self.engine.configure({key: value})
                    except Exception as e:
                        print(f"Failed to set {key}: {e}")
                        
    def set_search_config(self, **kwargs):
        """Set search configuration"""
        for key, value in kwargs.items():
            if key in self.search_config:
                self.search_config[key] = value
                
    def get_best_move(self, board: chess.Board, **kwargs) -> Optional[chess.Move]:
        """Get best move with current configuration"""
        if not self.is_ready:
            return None
            
        try:
            for key, value in kwargs.items():
                if key in self.search_config:
                    self.search_config[key] = value
                    
            self.is_thinking = True
            self.current_position = board
            
            limit = chess.engine.Limit(
                depth=self.search_config['depth'],
                time=self.search_config['time'] / 1000,
                nodes=self.search_config['nodes'],
                mate=self.search_config['mate'],
                movetime=self.search_config['movetime'] / 1000
            )
            
            with self.engine.analysis(board, limit) as analysis:
                for info in analysis:
                    if self.stop_analysis:
                        break
                    self._process_analysis_info(info)
                    
            self.is_thinking = False
            return self.best_move
            
        except Exception as e:
            print(f"Engine error: {e}")
            self.is_thinking = False
            return None
            
    def analyze_position(self, board: chess.Board, **kwargs) -> Dict:
        """Analyze position in depth"""
        if not self.is_ready:
            return {'error': 'Engine not ready'}
            
        try:
            self.analysis_data = []
            self.best_move = None
            self.score = 0
            self.pv = []
            
            for key, value in kwargs.items():
                if key in self.search_config:
                    self.search_config[key] = value
                    
            limit = chess.engine.Limit(
                depth=self.search_config['depth'],
                time=self.search_config['time'] / 1000
            )
            
            with self.engine.analysis(board, limit) as analysis:
                for info in analysis:
                    if self.stop_analysis:
                        break
                    self._process_analysis_info(info)
                    
            return {
                'best_move': self.best_move.uci() if self.best_move else None,
                'score': self.score,
                'mate_found': self.mate_found,
                'pv': [move.uci() for move in self.pv] if self.pv else [],
                'depth': self.depth_reached,
                'nodes': self.nodes_searched,
                'time': self.time_used,
                'analysis': self.analysis_data[-10:] if self.analysis_data else []
            }
            
        except Exception as e:
            return {'error': str(e)}
            
    def _process_analysis_info(self, info: chess.engine.InfoDict):
        """Process analysis information"""
        self.analysis_data.append(info)
        
        if 'depth' in info:
            self.depth_reached = info['depth']
            
        if 'nodes' in info:
            self.nodes_searched = info['nodes']
            
        if 'time' in info:
            self.time_used = info['time']
            
        if 'score' in info:
            self.score = info['score'].relative.score(mate_score=10000)
            self.mate_found = info['score'].mate is not None
            
        if 'pv' in info and info['pv']:
            self.pv = info['pv']
            self.best_move = self.pv[0] if self.pv else None
            
    def get_evaluation(self, board: chess.Board, depth: int = 12) -> float:
        """Get evaluation score for position"""
        board_hash = self._get_board_hash(board)
        
        if board_hash in self.eval_cache:
            cached = self.eval_cache[board_hash]
            if cached['depth'] >= depth:
                return cached['score']
                
        config = self.search_config.copy()
        config['depth'] = depth
        
        result = self.analyze_position(board, **config)
        
        if 'error' not in result:
            score = result['score'] / 100
            
            if len(self.eval_cache) < self.cache_size:
                self.eval_cache[board_hash] = {
                    'score': score,
                    'depth': depth,
                    'time': time.time()
                }
                
            return score
            
        return 0.0
        
    def _get_board_hash(self, board: chess.Board) -> str:
        """Get unique hash for board position"""
        return board._transposition_key()
        
    def get_pv(self, board: chess.Board, depth: int = 15) -> List[chess.Move]:
        """Get principal variation for position"""
        config = self.search_config.copy()
        config['depth'] = depth
        
        result = self.analyze_position(board, **config)
        
        if 'error' not in result and result['pv']:
            return [chess.Move.from_uci(move) for move in result['pv']]
            
        return []
        
    def get_best_move_uci(self, board: chess.Board, **kwargs) -> Optional[str]:
        """Get best move in UCI format"""
        move = self.get_best_move(board, **kwargs)
        return move.uci() if move else None
        
    def play_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Play a move with the engine"""
        return self.get_best_move(board)
        
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'is_ready': self.is_ready,
            'is_thinking': self.is_thinking,
            'depth_reached': self.depth_reached,
            'nodes_searched': self.nodes_searched,
            'time_used': self.time_used,
            'best_move': self.best_move.uci() if self.best_move else None,
            'score': self.score,
            'mate_found': self.mate_found,
            'pv': [move.uci() for move in self.pv] if self.pv else [],
            'config': self.config,
            'search_config': self.search_config
        }
        
    def set_skill_level(self, level: int):
        """Set engine skill level (1-20)"""
        if 1 <= level <= 20:
            self.set_config(Skill_Level=level)
            
    def set_time_control(self, moves: int, time_remaining: float, increment: float = 0):
        """Set time control for game"""
        time_per_move = time_remaining / max(1, moves)
        if increment > 0:
            time_per_move = min(time_per_move + increment, time_remaining)
        self.set_search_config(time=int(time_per_move * 1000))
        
    def set_pos(self, fen: str):
        """Set position for analysis"""
        board = chess.Board(fen)
        self.current_position = board
        
    def start_analysis(self, board: chess.Board, callback: callable = None):
        """Start background analysis"""
        self.stop_analysis = False
        
        def analysis_worker():
            while not self.stop_analysis:
                result = self.analyze_position(board)
                if callback:
                    callback(result)
                time.sleep(0.5)
                
        self.analysis_thread = threading.Thread(target=analysis_worker)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
    def stop_analysis_thread(self):
        """Stop background analysis"""
        self.stop_analysis = True
        if self.analysis_thread:
            self.analysis_thread.join(timeout=1)
            
    def clear_cache(self):
        """Clear evaluation cache"""
        self.eval_cache.clear()
        
    def set_tablebase_path(self, path: str):
        """Set path to Syzygy tablebases"""
        if os.path.exists(path):
            self.set_config(SyzygyPath=path)
            
    def get_tablebase_hit(self, board: chess.Board) -> Optional[str]:
        """Check if position is in tablebase"""
        if not self.is_ready:
            return None
            
        try:
            limit = chess.engine.Limit(time=0.1)
            with self.engine.analysis(board, limit) as analysis:
                for info in analysis:
                    if 'tbhits' in info and info['tbhits'] > 0:
                        return f"Tablebase hit: {info['tbhits']} positions"
        except Exception as e:
            pass
        return None
        
    def save_position_to_pgn(self, board: chess.Board, filename: str = None):
        """Save current position to PGN"""
        if not filename:
            filename = f"analysis_{int(time.time())}.pgn"
            
        try:
            game = chess.pgn.Game()
            game.setup(board)
            
            with open(filename, 'w') as f:
                exporter = chess.pgn.FileExporter(f)
                game.accept(exporter)
                
            return filename
        except Exception as e:
            print(f"Failed to save PGN: {e}")
            return None
            
    def load_position_from_pgn(self, pgn_data: str) -> Optional[chess.Board]:
        """Load position from PGN"""
        try:
            game = chess.pgn.read_game(pgn_data)
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
            return board
        except Exception as e:
            print(f"Failed to load PGN: {e}")
            return None
            
    def get_opening_book_moves(self, board: chess.Board) -> List[chess.Move]:
        """
        Get moves from opening book for the given board position.
        Uses polyglot book format (.bin files).
        """
        if not self.is_ready:
            return []
            
        try:
            if not os.path.exists(self.book_path):
                return []
                
            with chess.polyglot.open_reader(self.book_path) as reader:
                moves = []
                for entry in reader.find_all(board):
                    if entry.move in board.legal_moves:
                        moves.append(entry.move)
                return moves
                
        except FileNotFoundError:
            print(f"Opening book not found at: {self.book_path}")
            return []
        except Exception as e:
            print(f"Error reading opening book: {e}")
            return []
            
    def get_opening_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Get a single opening move from the book"""
        moves = self.get_opening_book_moves(board)
        return moves[0] if moves else None
        
    def analyze_tactical_moves(self, board: chess.Board, depth: int = 8) -> Dict:
        """Analyze position for tactical moves"""
        result = {
            'tactical_moves': [],
            'best_tactical': None,
            'captures': [],
            'checks': [],
            'threats': []
        }
        
        for move in board.legal_moves:
            if board.is_capture(move):
                result['captures'].append(move.uci())
                
            board_copy = board.copy()
            board_copy.push(move)
            if board_copy.is_check():
                result['checks'].append(move.uci())
                
            if self._is_tactical_threat(board, move):
                result['threats'].append(move.uci())
                
        if result['checks'] or result['captures']:
            tactical_moves = result['checks'] + result['captures']
            for move_uci in tactical_moves[:5]:
                move = chess.Move.from_uci(move_uci)
                if move in board.legal_moves:
                    board_copy = board.copy()
                    board_copy.push(move)
                    score = self.get_evaluation(board_copy, depth)
                    result['tactical_moves'].append({
                        'move': move_uci,
                        'score': score
                    })
                    
        if result['tactical_moves']:
            result['best_tactical'] = max(result['tactical_moves'], key=lambda x: x['score'])
            
        return result
        
    def _is_tactical_threat(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move creates a tactical threat"""
        board_copy = board.copy()
        board_copy.push(move)
        
        for next_move in board_copy.legal_moves:
            if board_copy.is_capture(next_move):
                return True
                
        return False
        
    def close(self):
        """Close engine and clean up"""
        self.stop_analysis_thread()
        if self.engine:
            try:
                self.engine.close()
            except Exception as e:
                pass
        self.is_ready = False
        
    def __del__(self):
        """Destructor"""
        self.close()