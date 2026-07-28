# © 2025 AmirAli Kamrani. All rights reserved.

# ui/board.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.clock import Clock
import chess
import random
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Assets Paths
ASSETS_PATH = '/storage/emulated/0/Biggest_chess/assets'
IMAGES_PATH = os.path.join(ASSETS_PATH, 'images')
PIECES_PATH = os.path.join(IMAGES_PATH, 'pieces')


class BoardScreen(Screen):
    def __init__(self, mode='local', **kwargs):
        super().__init__(**kwargs)
        
        # Game mode: local, ai, online
        self.mode = mode
        
        # Chess board
        self.board = chess.Board()
        self.selected = None
        self.legal_moves = []
        self.flipped = False
        self.move_history = []
        
        # Online mode variables
        self.is_online = False
        self.ws = None
        self.game_id = None
        self.online_username = ''
        
        # Timers
        self.white_time = 600
        self.black_time = 600
        self.timer_running = False
        self.timer_event = None
        
        # UI elements
        self.board_grid = None
        self.status_label = None
        self.move_count_label = None
        self.white_timer_label = None
        self.black_timer_label = None
        
        self.build_ui()
        self.update_board()
        self.start_timer()
        
    def get_piece_image(self, piece):
        """Get piece image path from assets"""
        if not piece:
            return None
        color = 'white' if piece.color == chess.WHITE else 'black'
        names = {
            chess.PAWN: 'pawn',
            chess.KNIGHT: 'knight',
            chess.BISHOP: 'bishop',
            chess.ROOK: 'rook',
            chess.QUEEN: 'queen',
            chess.KING: 'king'
        }
        name = names.get(piece.piece_type, '')
        if name:
            path = os.path.join(PIECES_PATH, color, f'{name}.png')
            if os.path.exists(path):
                return path
        return None
        
    def get_piece_symbol(self, piece):
        """Get unicode symbol for piece"""
        if not piece:
            return ''
        symbols = {
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
        }
        return symbols.get(piece.symbol(), '')
        
    def build_ui(self):
        """Build the board UI"""
        layout = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
        
        # Header
        header = BoxLayout(size_hint_y=0.06)
        back = Button(
            text='< Back',
            font_size=dp(18),
            size_hint_x=0.18,
            background_normal='',
            background_color=(0.2, 0.2, 0.35, 1)
        )
        back.bind(on_release=self.go_home)
        
        mode_text = 'Local' if self.mode == 'local' else 'VS AI' if self.mode == 'ai' else 'Online'
        title = Label(
            text=f'♟ {mode_text} Game',
            font_size=dp(22),
            color=(1, 1, 1, 1),
            bold=True
        )
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Board (8x8 grid)
        self.board_grid = GridLayout(cols=8, rows=8, size_hint=(1, 0.62))
        layout.add_widget(self.board_grid)
        
        # Status bar
        info = BoxLayout(size_hint_y=0.05, spacing=dp(10))
        self.status_label = Label(
            text='Turn: White',
            font_size=dp(15),
            color=(0.7, 0.7, 0.7, 1)
        )
        self.move_count_label = Label(
            text='Moves: 0',
            font_size=dp(15),
            color=(0.7, 0.7, 0.7, 1)
        )
        info.add_widget(self.status_label)
        info.add_widget(self.move_count_label)
        layout.add_widget(info)
        
        # Timer
        timer_box = BoxLayout(size_hint_y=0.05, spacing=dp(10))
        self.white_timer_label = Label(
            text='⏱️ White: 10:00',
            font_size=dp(14),
            color=(1, 1, 1, 1)
        )
        self.black_timer_label = Label(
            text='Black: 10:00',
            font_size=dp(14),
            color=(1, 1, 1, 1)
        )
        timer_box.add_widget(self.white_timer_label)
        timer_box.add_widget(self.black_timer_label)
        layout.add_widget(timer_box)
        
        # Control buttons
        controls = BoxLayout(size_hint_y=0.07, spacing=dp(6))
        
        # Undo button
        undo_btn = Button(
            text='↩ Undo',
            font_size=dp(14),
            background_normal='',
            background_color=(0.2, 0.2, 0.35, 1)
        )
        undo_btn.bind(on_release=self.do_undo)
        controls.add_widget(undo_btn)
        
        # Reset button
        reset_btn = Button(
            text='🔄 Reset',
            font_size=dp(14),
            background_normal='',
            background_color=(0.2, 0.2, 0.35, 1)
        )
        reset_btn.bind(on_release=self.do_reset)
        controls.add_widget(reset_btn)
        
        # Flip button
        flip_btn = Button(
            text='🔃 Flip',
            font_size=dp(14),
            background_normal='',
            background_color=(0.2, 0.2, 0.35, 1)
        )
        flip_btn.bind(on_release=self.do_flip)
        controls.add_widget(flip_btn)
        
        # AI Move button (only in AI mode)
        if self.mode == 'ai':
            ai_btn = Button(
                text='🤖 AI Move',
                font_size=dp(14),
                background_normal='',
                background_color=(0.97, 0.59, 0.12, 1)
            )
            ai_btn.bind(on_release=self.do_ai_move)
            controls.add_widget(ai_btn)
            
        # Resign button (only in online mode)
        if self.mode == 'online':
            resign_btn = Button(
                text='🏳️ Resign',
                font_size=dp(14),
                background_normal='',
                background_color=(0.6, 0.1, 0.1, 1)
            )
            resign_btn.bind(on_release=self.do_resign)
            controls.add_widget(resign_btn)
            
        layout.add_widget(controls)
        
        self.add_widget(layout)
        
    def update_board(self):
        """Update the board display"""
        if not self.board_grid:
            return
            
        self.board_grid.clear_widgets()
        
        for row in range(8):
            for col in range(8):
                r = row if not self.flipped else 7 - row
                c = col if not self.flipped else 7 - col
                square = r * 8 + c
                is_light = (r + c) % 2 == 0
                piece = self.board.piece_at(square)
                
                # Square colors
                bg = (0.94, 0.85, 0.71, 1) if is_light else (0.71, 0.53, 0.39, 1)
                
                # Selected square highlight
                if self.selected == square:
                    bg = (0.5, 0.8, 0.5, 0.8)
                    
                # Legal moves highlight
                if square in self.legal_moves:
                    bg = (0.3, 0.8, 0.3, 0.5)
                    
                # Check highlight
                if self.board.is_check() and piece and piece.piece_type == chess.KING:
                    bg = (1, 0.2, 0.2, 0.8)
                    
                # Try to load image
                img_path = self.get_piece_image(piece)
                
                if img_path and os.path.exists(img_path):
                    btn = Button(
                        background_normal=img_path,
                        background_color=(1, 1, 1, 1),
                        background_down=''
                    )
                else:
                    # Fallback to unicode
                    btn = Button(
                        text=self.get_piece_symbol(piece),
                        font_size=dp(36),
                        background_normal='',
                        background_color=bg,
                        color=(1, 1, 1, 1) if piece and piece.color == chess.WHITE else (0, 0, 0, 1),
                        bold=True
                    )
                
                btn.bind(on_release=lambda x, sq=square: self.on_square_click(sq))
                self.board_grid.add_widget(btn)
        
        # Update status
        if self.status_label:
            if self.board.is_checkmate():
                winner = 'Black' if self.board.turn == chess.WHITE else 'White'
                self.status_label.text = f'🏆 Checkmate! {winner} wins!'
            elif self.board.is_stalemate():
                self.status_label.text = '🤝 Stalemate! Draw.'
            elif self.board.is_insufficient_material():
                self.status_label.text = 'Draw - Insufficient material.'
            elif self.board.is_check():
                turn = 'White' if self.board.turn == chess.WHITE else 'Black'
                self.status_label.text = f'⚡ Check! ({turn})'
            else:
                turn = 'White' if self.board.turn == chess.WHITE else 'Black'
                self.status_label.text = f'Turn: {turn}'
                
        if self.move_count_label:
            self.move_count_label.text = f'Moves: {len(self.move_history)}'
            
    def on_square_click(self, square):
        """Handle square click"""
        if self.mode == 'online' and self.board.turn != chess.WHITE:
            # In online mode, you play as White
            self.status_label.text = '⏳ Waiting for opponent...'
            return
            
        piece = self.board.piece_at(square)
        
        # If a square is already selected
        if self.selected is not None:
            if square == self.selected:
                # Deselect
                self.selected = None
                self.legal_moves = []
                self.update_board()
                return
                
            # Try to make a move
            move = chess.Move(self.selected, square)
            
            # Check for pawn promotion
            if self.board.piece_at(self.selected) and \
               self.board.piece_at(self.selected).piece_type == chess.PAWN:
                if (self.board.turn == chess.WHITE and square // 8 == 7) or \
                   (self.board.turn == chess.BLACK and square // 8 == 0):
                    move = chess.Move(self.selected, square, promotion=chess.QUEEN)
            
            # Make the move
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                self.selected = None
                self.legal_moves = []
                self.update_board()
                
                # Send move if online
                if self.mode == 'online' and self.is_online:
                    self.send_online_move(move.uci())
                
                # AI move if AI mode
                if self.mode == 'ai' and not self.board.is_game_over() and self.board.turn == chess.BLACK:
                    Clock.schedule_once(lambda dt: self.do_ai_move(None), 0.5)
                return
            else:
                # Try to select a new piece
                if piece and piece.color == self.board.turn:
                    self.selected = square
                    self.legal_moves = [m.to_square for m in self.board.legal_moves if m.from_square == square]
                    self.update_board()
                else:
                    self.selected = None
                    self.legal_moves = []
                    self.update_board()
                return
                
        # Select a piece
        if piece and piece.color == self.board.turn:
            self.selected = square
            self.legal_moves = [m.to_square for m in self.board.legal_moves if m.from_square == square]
            self.update_board()
        else:
            self.selected = None
            self.legal_moves = []
            self.update_board()
            
    def send_online_move(self, move_uci):
        """Send move to online opponent"""
        if self.ws and self.game_id:
            try:
                message = {
                    'type': 'move',
                    'payload': {
                        'game_id': self.game_id,
                        'move': move_uci
                    }
                }
                self.ws.send(json.dumps(message))
            except Exception as e:
                print(f"Send move error: {e}")
                
    def do_ai_move(self, instance):
        """Make AI move (random for now)"""
        if self.board.turn == chess.BLACK and not self.board.is_game_over():
            moves = list(self.board.legal_moves)
            if moves:
                move = random.choice(moves)
                self.board.push(move)
                self.move_history.append(move)
                self.selected = None
                self.legal_moves = []
                self.update_board()
                
    def do_resign(self, instance):
        """Resign game"""
        if self.mode == 'online' and self.is_online:
            try:
                message = {
                    'type': 'resign',
                    'payload': {'game_id': self.game_id}
                }
                self.ws.send(json.dumps(message))
                self.status_label.text = '🏳️ You resigned'
            except:
                pass
        else:
            self.status_label.text = '🏳️ You resigned'
            self.board = chess.Board()
            self.move_history = []
            self.selected = None
            self.legal_moves = []
            self.update_board()
            
    def do_undo(self, instance):
        """Undo last move(s)"""
        if self.mode == 'ai' and len(self.move_history) >= 2:
            # Undo 2 moves (player + AI)
            for _ in range(2):
                if self.move_history:
                    self.board.pop()
                    self.move_history.pop()
        elif self.move_history:
            self.board.pop()
            self.move_history.pop()
            
        self.selected = None
        self.legal_moves = []
        self.update_board()
        
    def do_reset(self, instance):
        """Reset the game"""
        self.board = chess.Board()
        self.move_history = []
        self.selected = None
        self.legal_moves = []
        self.flipped = False
        self.white_time = 600
        self.black_time = 600
        self.update_board()
        
    def do_flip(self, instance):
        """Flip the board"""
        self.flipped = not self.flipped
        self.update_board()
        
    def start_timer(self):
        """Start the chess clock"""
        if self.timer_event:
            return
        self.timer_running = True
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        
    def update_timer(self, dt):
        """Update timer every second"""
        if self.board.turn == chess.WHITE:
            self.white_time -= 1
            if self.white_time <= 0:
                self.white_time = 0
                self.status_label.text = '⏰ Black wins on time!'
                self.timer_running = False
                if self.timer_event:
                    self.timer_event.cancel()
                    self.timer_event = None
        else:
            self.black_time -= 1
            if self.black_time <= 0:
                self.black_time = 0
                self.status_label.text = '⏰ White wins on time!'
                self.timer_running = False
                if self.timer_event:
                    self.timer_event.cancel()
                    self.timer_event = None
                    
        # Update display
        self.white_timer_label.text = f'⏱️ White: {self.format_time(self.white_time)}'
        self.black_timer_label.text = f'Black: {self.format_time(self.black_time)}'
        
    def format_time(self, seconds):
        """Format seconds to MM:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f'{mins:02d}:{secs:02d}'
        
    def go_home(self, instance):
        """Go back to home screen"""
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        self.manager.current = 'home'