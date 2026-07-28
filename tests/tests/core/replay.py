# © 2025 AmirAli Kamrani. All rights reserved.

# core/replay.py
import chess
import chess.pgn
import json
import time
import threading
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import queue

from core.board import BoardState
from core.game_logic import GameLogic, GameResult

class ReplaySpeed(Enum):
    SLOW = 0.5
    NORMAL = 1.0
    FAST = 2.0
    VERY_FAST = 4.0

class ReplayMode(Enum):
    AUTO = "auto"
    MANUAL = "manual"
    STEP = "step"

@dataclass
class ReplayAnnotation:
    """Annotation for replay positions"""
    move_number: int
    fen: str
    comment: str
    evaluation: float
    best_move: str
    classification: str  # best, good, inaccuracy, mistake, blunder

class GameReplay:
    """Game replay system with full control and analysis"""
    
    def __init__(self):
        self.board_state = None
        self.game_logic = None
        self.move_history = []
        self.current_position = 0
        self.total_moves = 0
        self.is_playing = False
        self.is_paused = False
        self.speed = ReplaySpeed.NORMAL
        self.mode = ReplayMode.MANUAL
        
        # Analysis data
        self.analysis_data = None
        self.annotations = []
        self.comments = {}
        
        # Threading
        self.replay_thread = None
        self.replay_queue = queue.Queue()
        self.is_running = False
        
        # Callbacks
        self.event_listeners = []
        
        # Bookmark system
        self.bookmarks = {}
        self.bookmark_counter = 0
        
    def load_game(self, board_state: BoardState, analysis_data: Dict = None):
        """Load a game for replay"""
        self.board_state = board_state
        self.move_history = board_state.move_history.copy()
        self.total_moves = len(self.move_history)
        self.current_position = 0
        self.analysis_data = analysis_data
        
        # Create game logic for replay
        self.game_logic = GameLogic()
        self.game_logic.board = board_state
        self.game_logic.move_history = board_state.move_history.copy()
        
        # Reset board to start
        self.board_state.board.reset()
        self.board_state.move_history = []
        self.current_position = 0
        
        # Process analysis data
        if analysis_data:
            self._process_analysis_data(analysis_data)
            
        # Notify listeners
        self._notify_listeners('game_loaded', {
            'total_moves': self.total_moves,
            'analysis': bool(analysis_data)
        })
        
    def load_from_pgn(self, pgn_data: str) -> bool:
        """Load game from PGN"""
        try:
            game = chess.pgn.read_game(pgn_data)
            if not game:
                return False
                
            board = chess.Board()
            moves = []
            
            for move in game.mainline_moves():
                moves.append(move)
                board.push(move)
                
            board_state = BoardState()
            board_state.board = board
            board_state.move_history = moves
            
            self.load_game(board_state)
            return True
            
        except Exception as e:
            print(f"Error loading PGN: {e}")
            return False
            
    def _process_analysis_data(self, analysis_data: Dict):
        """Process analysis data for annotations"""
        self.annotations = []
        
        # Process move analysis
        if 'move_analysis' in analysis_data:
            for move_analysis in analysis_data['move_analysis']:
                annotation = ReplayAnnotation(
                    move_number=move_analysis.get('move_number', 0),
                    fen=move_analysis.get('fen', ''),
                    comment=self._generate_comment(move_analysis),
                    evaluation=move_analysis.get('centipawn_loss', 0),
                    best_move=move_analysis.get('best_move', ''),
                    classification=move_analysis.get('classification', '')
                )
                self.annotations.append(annotation)
                
        # Process blunders, mistakes, inaccuracies
        if 'blunders' in analysis_data:
            for blunder in analysis_data['blunders']:
                self._add_annotation(blunder, 'blunder')
                
        if 'mistakes' in analysis_data:
            for mistake in analysis_data['mistakes']:
                self._add_annotation(mistake, 'mistake')
                
        if 'inaccuracies' in analysis_data:
            for inaccuracy in analysis_data['inaccuracies']:
                self._add_annotation(inaccuracy, 'inaccuracy')
                
    def _add_annotation(self, move_data: Dict, classification: str):
        """Add annotation for a move"""
        annotation = ReplayAnnotation(
            move_number=move_data.get('move_number', 0),
            fen=move_data.get('fen', ''),
            comment=move_data.get('comment', ''),
            evaluation=move_data.get('centipawn_loss', 0),
            best_move=move_data.get('best_move', ''),
            classification=classification
        )
        self.annotations.append(annotation)
        
    def _generate_comment(self, move_analysis: Dict) -> str:
        """Generate comment for a move"""
        classification = move_analysis.get('classification', '')
        loss = move_analysis.get('centipawn_loss', 0)
        
        comments = {
            'best': 'Excellent move!',
            'good': 'Good move.',
            'inaccuracy': f'Inaccuracy ({loss:.1f}cp loss)',
            'mistake': f'Mistake ({loss:.1f}cp loss)',
            'blunder': f'Blunder! ({loss:.1f}cp loss)'
        }
        
        return comments.get(classification, '')
        
    def play(self):
        """Start auto replay"""
        if self.is_playing:
            return
            
        if self.current_position >= self.total_moves:
            self.current_position = 0
            self._reset_board()
            
        self.is_playing = True
        self.is_paused = False
        self.is_running = True
        
        self.replay_thread = threading.Thread(target=self._replay_worker, daemon=True)
        self.replay_thread.start()
        
        self._notify_listeners('replay_started', {})
        
    def pause(self):
        """Pause replay"""
        self.is_paused = True
        self._notify_listeners('replay_paused', {})
        
    def resume(self):
        """Resume replay"""
        self.is_paused = False
        self._notify_listeners('replay_resumed', {})
        
    def stop(self):
        """Stop replay"""
        self.is_playing = False
        self.is_running = False
        if self.replay_thread:
            self.replay_thread.join(timeout=1)
        self._notify_listeners('replay_stopped', {})
        
    def step_forward(self):
        """Step one move forward"""
        if self.current_position < self.total_moves:
            self.current_position += 1
            self._apply_move(self.move_history[self.current_position - 1])
            self._notify_listeners('step_forward', {
                'position': self.current_position,
                'total': self.total_moves
            })
            
    def step_backward(self):
        """Step one move backward"""
        if self.current_position > 0:
            self.current_position -= 1
            self._reset_board()
            for i in range(self.current_position):
                self._apply_move(self.move_history[i])
            self._notify_listeners('step_backward', {
                'position': self.current_position,
                'total': self.total_moves
            })
            
    def go_to_position(self, position: int):
        """Go to a specific position"""
        if 0 <= position <= self.total_moves:
            self.current_position = position
            self._reset_board()
            for i in range(position):
                self._apply_move(self.move_history[i])
            self._notify_listeners('position_changed', {
                'position': self.current_position,
                'total': self.total_moves
            })
            
    def _replay_worker(self):
        """Worker thread for auto replay"""
        while self.is_running and self.is_playing:
            if self.is_paused:
                time.sleep(0.1)
                continue
                
            if self.current_position < self.total_moves:
                # Move forward
                self.step_forward()
                
                # Wait based on speed
                speed_multiplier = self.speed.value
                time.sleep(1.0 / speed_multiplier)
                
                # Check for annotations at this position
                self._check_annotations()
            else:
                # Reached end
                self.is_playing = False
                self._notify_listeners('replay_finished', {})
                break
                
    def _apply_move(self, move: chess.Move):
        """Apply a move to the board"""
        if self.board_state:
            self.board_state.make_move(move)
            
    def _reset_board(self):
        """Reset board to initial position"""
        if self.board_state:
            self.board_state.board.reset()
            self.board_state.move_history = []
            
    def _check_annotations(self):
        """Check for annotations at current position"""
        for annotation in self.annotations:
            if annotation.move_number == self.current_position:
                self._notify_listeners('annotation_reached', {
                    'move_number': annotation.move_number,
                    'comment': annotation.comment,
                    'classification': annotation.classification,
                    'evaluation': annotation.evaluation
                })
                
    def set_speed(self, speed: ReplaySpeed):
        """Set replay speed"""
        self.speed = speed
        self._notify_listeners('speed_changed', {'speed': speed.value})
        
    def set_mode(self, mode: ReplayMode):
        """Set replay mode"""
        self.mode = mode
        if mode == ReplayMode.MANUAL:
            self.pause()
        elif mode == ReplayMode.AUTO:
            self.resume()
            
    def add_bookmark(self, comment: str = '') -> int:
        """Add a bookmark at current position"""
        self.bookmark_counter += 1
        bookmark_id = self.bookmark_counter
        
        self.bookmarks[bookmark_id] = {
            'position': self.current_position,
            'comment': comment,
            'fen': self.board_state.board.fen() if self.board_state else '',
            'created_at': time.time()
        }
        
        self._notify_listeners('bookmark_added', {
            'id': bookmark_id,
            'position': self.current_position
        })
        
        return bookmark_id
        
    def go_to_bookmark(self, bookmark_id: int) -> bool:
        """Go to a bookmark position"""
        if bookmark_id in self.bookmarks:
            bookmark = self.bookmarks[bookmark_id]
            self.go_to_position(bookmark['position'])
            return True
        return False
        
    def remove_bookmark(self, bookmark_id: int):
        """Remove a bookmark"""
        if bookmark_id in self.bookmarks:
            del self.bookmarks[bookmark_id]
            self._notify_listeners('bookmark_removed', {'id': bookmark_id})
            
    def get_bookmarks(self) -> Dict:
        """Get all bookmarks"""
        return self.bookmarks
        
    def add_comment(self, move_number: int, comment: str):
        """Add comment for a specific move"""
        self.comments[move_number] = comment
        self._notify_listeners('comment_added', {
            'move_number': move_number,
            'comment': comment
        })
        
    def get_comment(self, move_number: int) -> Optional[str]:
        """Get comment for a move"""
        return self.comments.get(move_number)
        
    def get_current_position_info(self) -> Dict:
        """Get information about current position"""
        info = {
            'position': self.current_position,
            'total_moves': self.total_moves,
            'progress': (self.current_position / self.total_moves * 100) if self.total_moves > 0 else 0,
            'fen': self.board_state.board.fen() if self.board_state else '',
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'speed': self.speed.value,
            'mode': self.mode.value
        }
        
        # Get annotation at current position
        for annotation in self.annotations:
            if annotation.move_number == self.current_position:
                info['annotation'] = {
                    'comment': annotation.comment,
                    'classification': annotation.classification,
                    'evaluation': annotation.evaluation
                }
                break
                
        return info
        
    def get_game_statistics(self) -> Dict:
        """Get statistics about the game"""
        if not self.move_history:
            return {}
            
        # Calculate basic statistics
        white_moves = len([m for m in self.move_history[::2]])
        black_moves = len([m for m in self.move_history[1::2]])
        
        return {
            'total_moves': len(self.move_history),
            'white_moves': white_moves,
            'black_moves': black_moves,
            'annotations': len(self.annotations),
            'bookmarks': len(self.bookmarks),
            'comments': len(self.comments),
            'position_history': len(self.move_history)
        }
        
    def export_replay(self, format: str = 'pgn') -> str:
        """Export replay in different formats"""
        if format == 'pgn':
            return self._export_pgn()
        elif format == 'json':
            return self._export_json()
        elif format == 'html':
            return self._export_html()
        else:
            return ''
            
    def _export_pgn(self) -> str:
        """Export as PGN with annotations"""
        if not self.move_history:
            return ''
            
        pgn = chess.pgn.Game()
        node = pgn
        
        board = chess.Board()
        for i, move in enumerate(self.move_history):
            node = node.add_variation(move)
            
            # Add comment if available
            comment = self.comments.get(i + 1)
            if comment:
                node.comment = comment
                
            # Add NAG if annotation available
            for annotation in self.annotations:
                if annotation.move_number == i + 1:
                    if annotation.classification == 'best':
                        node.nags.add(chess.pgn.NAG_GOOD_MOVE)
                    elif annotation.classification == 'blunder':
                        node.nags.add(chess.pgn.NAG_BLUNDER)
                    elif annotation.classification == 'mistake':
                        node.nags.add(chess.pgn.NAG_MISTAKE)
                    break
                    
        return str(pgn)
        
    def _export_json(self) -> str:
        """Export as JSON"""
        data = {
            'moves': [move.uci() for move in self.move_history],
            'current_position': self.current_position,
            'total_moves': self.total_moves,
            'annotations': [
                {
                    'move_number': a.move_number,
                    'comment': a.comment,
                    'classification': a.classification,
                    'evaluation': a.evaluation
                }
                for a in self.annotations
            ],
            'bookmarks': self.bookmarks,
            'comments': self.comments
        }
        return json.dumps(data, indent=2)
        
    def _export_html(self) -> str:
        """Export as HTML"""
        html = """
        <html>
        <head><title>Game Replay</title>
        <style>
            body { font-family: Arial; margin: 20px; }
            .board { display: grid; grid-template-columns: repeat(8, 60px); grid-template-rows: repeat(8, 60px); }
            .square { width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; font-size: 30px; }
            .white { background: #f0d9b5; }
            .black { background: #b58863; }
            .controls { margin: 20px 0; }
            .moves { column-count: 2; }
            .move { padding: 3px; }
            .best { color: green; }
            .blunder { color: red; }
            .mistake { color: orange; }
            .inaccuracy { color: yellow; }
        </style>
        </head>
        <body>
        <h2>Game Replay</h2>
        <div id="board-container"></div>
        <div class="controls">
            <button onclick="play()">▶ Play</button>
            <button onclick="pause()">⏸ Pause</button>
            <button onclick="stop()">⏹ Stop</button>
            <button onclick="stepForward()">⏭ Forward</button>
            <button onclick="stepBackward()">⏮ Backward</button>
        </div>
        <div class="moves">
        """
        
        # Add moves
        board = chess.Board()
        for i, move in enumerate(self.move_history):
            move_san = board.san(move)
            board.push(move)
            
            classification = ''
            for annotation in self.annotations:
                if annotation.move_number == i + 1:
                    classification = annotation.classification
                    break
                    
            html += f"<div class='move {classification}'>{i+1}. {move_san}</div>"
            
        html += "</div></body></html>"
        return html
        
    def add_event_listener(self, listener: callable):
        """Add event listener"""
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: callable):
        """Remove event listener"""
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            
    def _notify_listeners(self, event: str, data: Dict):
        """Notify all event listeners"""
        for listener in self.event_listeners:
            try:
                listener(event, data)
            except Exception as e:
                print(f"Error in event listener: {e}")
                
    def get_status(self) -> Dict:
        """Get replay status"""
        return {
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_position': self.current_position,
            'total_moves': self.total_moves,
            'speed': self.speed.value,
            'mode': self.mode.value,
            'progress': (self.current_position / self.total_moves * 100) if self.total_moves > 0 else 0
        }
        
    def get_position_fen(self) -> str:
        """Get FEN of current position"""
        if self.board_state:
            return self.board_state.board.fen()
        return chess.Board().fen()
        
    def get_position_svg(self) -> str:
        """Get SVG of current position"""
        if self.board_state:
            return chess.svg.board(self.board_state.board)
        return chess.svg.board()
        
    def get_move_pgn(self) -> List[str]:
        """Get moves in PGN format"""
        if not self.move_history:
            return []
            
        board = chess.Board()
        pgn_moves = []
        for i, move in enumerate(self.move_history):
            san = board.san(move)
            if i % 2 == 0:
                pgn_moves.append(f"{i//2 + 1}. {san}")
            else:
                pgn_moves.append(san)
            board.push(move)
            
        return pgn_moves