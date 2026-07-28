# © 2025 AmirAli Kamrani. All rights reserved.

# core/tutorial.py
import json
import os
from typing import List, Dict, Optional

class TutorialStep:
    def __init__(self, step_id: int, title: str, description: str, 
                 board_state: Optional[Dict] = None, 
                 highlight_squares: Optional[List[str]] = None,
                 move_hint: Optional[str] = None):
        self.step_id = step_id
        self.title = title
        self.description = description
        self.board_state = board_state or {}
        self.highlight_squares = highlight_squares or []
        self.move_hint = move_hint

class TutorialManager:
    def __init__(self):
        self.steps: List[TutorialStep] = []
        self.current_step_index = 0
        self.is_completed = False
        self._load_tutorial_data()
    
    def _load_tutorial_data(self):
        """Load tutorial steps from JSON or use default data"""
        tutorial_file = os.path.join(os.path.dirname(__file__), 'tutorial_data.json')
        
        if os.path.exists(tutorial_file):
            with open(tutorial_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    self.steps.append(TutorialStep(
                        step_id=item['id'],
                        title=item['title'],
                        description=item['description'],
                        board_state=item.get('board_state', {}),
                        highlight_squares=item.get('highlight_squares', []),
                        move_hint=item.get('move_hint')
                    ))
        else:
            # Default tutorial data
            self._create_default_tutorial()
    
    def _create_default_tutorial(self):
        """Create default tutorial steps"""
        default_steps = [
            {
                'id': 1,
                'title': 'Welcome to Chess',
                'description': 'Chess is a two-player strategy game played on an 8x8 board. Each player starts with 16 pieces: 1 King, 1 Queen, 2 Rooks, 2 Bishops, 2 Knights, and 8 Pawns.',
                'board_state': {},
                'highlight_squares': [],
                'move_hint': None
            },
            {
                'id': 2,
                'title': 'The Board',
                'description': 'The board consists of 64 squares arranged in an 8x8 grid. The columns are labeled a-h and rows are labeled 1-8. White pieces start on rows 1-2, Black pieces start on rows 7-8.',
                'board_state': {},
                'highlight_squares': ['a1', 'h1', 'a8', 'h8'],
                'move_hint': None
            },
            {
                'id': 3,
                'title': 'Pawn Movement',
                'description': 'Pawns move forward one square, but capture diagonally. On their first move, they can move two squares forward. Pawns can be promoted when reaching the opposite end of the board.',
                'board_state': {},
                'highlight_squares': ['e2', 'e3', 'e4'],
                'move_hint': 'e2-e4'
            },
            {
                'id': 4,
                'title': 'Knight Movement',
                'description': 'Knights move in an L-shape: two squares in one direction and then one square perpendicular. Knights are the only pieces that can jump over other pieces.',
                'board_state': {},
                'highlight_squares': ['g1', 'f3', 'h3', 'e2', 'e4'],
                'move_hint': 'g1-f3'
            },
            {
                'id': 5,
                'title': 'Bishop Movement',
                'description': 'Bishops move diagonally any number of squares. Each bishop stays on one color (light or dark) for the entire game.',
                'board_state': {},
                'highlight_squares': ['c1', 'd2', 'e3', 'f4', 'g5', 'h6'],
                'move_hint': 'c1-g5'
            },
            {
                'id': 6,
                'title': 'Rook Movement',
                'description': 'Rooks move horizontally or vertically any number of squares. Rooks are powerful pieces that work best in open files.',
                'board_state': {},
                'highlight_squares': ['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1'],
                'move_hint': 'a1-a8'
            },
            {
                'id': 7,
                'title': 'Queen Movement',
                'description': 'The Queen is the most powerful piece. She can move in any direction: horizontally, vertically, or diagonally, any number of squares.',
                'board_state': {},
                'highlight_squares': ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8'],
                'move_hint': 'd1-d8'
            },
            {
                'id': 8,
                'title': 'King Movement',
                'description': 'The King moves one square in any direction. The King is the most important piece - if the King is in check, you must respond to it immediately.',
                'board_state': {},
                'highlight_squares': ['e1', 'e2', 'd1', 'd2', 'f1', 'f2'],
                'move_hint': 'e1-e2'
            },
            {
                'id': 9,
                'title': 'Special Moves: Castling',
                'description': 'Castling is a special move that moves the King and Rook simultaneously. The King moves two squares towards the Rook, and the Rook jumps over the King.',
                'board_state': {},
                'highlight_squares': ['e1', 'g1', 'h1'],
                'move_hint': 'O-O (Kingside) or O-O-O (Queenside)'
            },
            {
                'id': 10,
                'title': 'Special Moves: En Passant',
                'description': 'En passant is a special pawn capture. If a pawn moves two squares from its starting position, the opponent can capture it as if it had moved only one square.',
                'board_state': {},
                'highlight_squares': [],
                'move_hint': None
            },
            {
                'id': 11,
                'title': 'Check and Checkmate',
                'description': 'When the King is under attack, it is in "check". You must get out of check immediately. If you cannot escape check, it is "checkmate" and you lose the game.',
                'board_state': {},
                'highlight_squares': [],
                'move_hint': None
            },
            {
                'id': 12,
                'title': 'Basic Strategy',
                'description': 'Control the center of the board, develop your pieces early, protect your King, and look for tactical opportunities. Practice regularly to improve your chess skills!',
                'board_state': {},
                'highlight_squares': ['d4', 'e4', 'd5', 'e5'],
                'move_hint': None
            }
        ]
        
        for item in default_steps:
            self.steps.append(TutorialStep(
                step_id=item['id'],
                title=item['title'],
                description=item['description'],
                board_state=item.get('board_state', {}),
                highlight_squares=item.get('highlight_squares', []),
                move_hint=item.get('move_hint')
            ))
    
    def get_current_step(self) -> Optional[TutorialStep]:
        """Get current tutorial step"""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def next_step(self) -> bool:
        """Move to next step, returns True if successful"""
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            return True
        self.is_completed = True
        return False
    
    def previous_step(self) -> bool:
        """Move to previous step, returns True if successful"""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.is_completed = False
            return True
        return False
    
    def reset_tutorial(self):
        """Reset tutorial to beginning"""
        self.current_step_index = 0
        self.is_completed = False
    
    def get_progress(self) -> float:
        """Get tutorial progress as percentage"""
        if not self.steps:
            return 0
        return (self.current_step_index + 1) / len(self.steps) * 100
    
    def get_total_steps(self) -> int:
        """Get total number of steps"""
        return len(self.steps)
    
    def get_current_step_number(self) -> int:
        """Get current step number (1-based)"""
        return self.current_step_index + 1