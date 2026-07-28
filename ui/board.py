# © 2025 AmirAli Kamrani. All rights reserved.

# ui/board.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.metrics import dp
import chess
import os

# ============================================
# مسیر Assets (دقیقاً مطابق ساختار شما)
# ============================================
ASSETS_PATH = '/storage/emulated/0/Biggest_chess/assets/'
PIECES_PATH = os.path.join(ASSETS_PATH, 'images/pieces/')

class BoardScreen(Screen):
    def __init__(self, mode='local', **kwargs):
        super().__init__(**kwargs)
        self.mode = mode
        self.board = chess.Board()
        self.selected = None
        self.legal_moves = []
        self.flipped = False
        self.move_history = []
        self.build_ui()
        self.update_board()
        
    def get_piece_image(self, piece):
        """
        دریافت مسیر تصویر مهره از Assets
        """
        if not piece:
            return None
            
        # تعیین رنگ
        color = 'white' if piece.color == chess.WHITE else 'black'
        
        # تعیین نام فایل
        names = {
            chess.PAWN: 'pawn',
            chess.KNIGHT: 'knight',
            chess.BISHOP: 'bishop',
            chess.ROOK: 'rook',
            chess.QUEEN: 'queen',
            chess.KING: 'king'
        }
        
        piece_name = names.get(piece.piece_type)
        if not piece_name:
            return None
            
        # ساخت مسیر کامل
        path = os.path.join(PIECES_PATH, color, f'{piece_name}.png')
        
        # بررسی وجود فایل
        if os.path.exists(path):
            return path
        else:
            print(f"⚠️ File not found: {path}")
            return None
            
    def get_piece_symbol(self, piece):
        """یونیکد برای Fallback (اگر تصویر نبود)"""
        if not piece:
            return ''
        symbols = {
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
        }
        return symbols.get(piece.symbol(), '')
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
        
        # Header
        header = BoxLayout(size_hint_y=0.06)
        back = Button(text='< Back', font_size=dp(18), size_hint_x=0.18,
                     background_normal='', background_color=(0.2, 0.2, 0.35, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        
        mode_text = 'Local' if self.mode == 'local' else 'VS AI'
        title = Label(text=f'Chess {mode_text}', font_size=dp(22), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Board
        self.board_grid = GridLayout(cols=8, rows=8, size_hint=(1, 0.65))
        layout.add_widget(self.board_grid)
        
        # Status
        info = BoxLayout(size_hint_y=0.05, spacing=dp(10))
        self.status_label = Label(text='Turn: White', font_size=dp(15), color=(0.7, 0.7, 0.7, 1))
        self.move_count_label = Label(text='Moves: 0', font_size=dp(15), color=(0.7, 0.7, 0.7, 1))
        info.add_widget(self.status_label)
        info.add_widget(self.move_count_label)
        layout.add_widget(info)
        
        # Controls
        controls = BoxLayout(size_hint_y=0.07, spacing=dp(6))
        for text, action in [('Undo', self.do_undo), ('Reset', self.do_reset), ('Flip', self.do_flip)]:
            btn = Button(text=text, font_size=dp(14), background_normal='', background_color=(0.2, 0.2, 0.35, 1))
            btn.bind(on_release=action)
            controls.add_widget(btn)
        layout.add_widget(controls)
        
        self.add_widget(layout)
        
    def update_board(self):
        """به‌روزرسانی صفحه با مهره‌ها (تصویر یا یونیکد)"""
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
                
                # رنگ مربع
                bg = (0.94, 0.85, 0.71, 1) if is_light else (0.71, 0.53, 0.39, 1)
                
                # هایلایت‌ها
                if self.selected == square:
                    bg = (0.5, 0.8, 0.5, 0.8)
                if square in self.legal_moves:
                    bg = (0.3, 0.8, 0.3, 0.5)
                if self.board.is_check() and piece and piece.piece_type == chess.KING:
                    bg = (1, 0.2, 0.2, 0.8)
                
                # دریافت تصویر مهره
                img_path = self.get_piece_image(piece)
                
                if img_path and os.path.exists(img_path):
                    # استفاده از تصویر
                    btn = Button(
                        background_normal=img_path,
                        background_color=(1, 1, 1, 1),
                        background_down=''
                    )
                else:
                    # Fallback به یونیکد
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
        
        # به‌روزرسانی وضعیت
        if self.status_label:
            if self.board.is_checkmate():
                winner = 'Black' if self.board.turn == chess.WHITE else 'White'
                self.status_label.text = f'Checkmate! {winner} wins!'
            elif self.board.is_stalemate():
                self.status_label.text = 'Stalemate! Draw.'
            elif self.board.is_check():
                turn = 'White' if self.board.turn == chess.WHITE else 'Black'
                self.status_label.text = f'Check! ({turn})'
            else:
                turn = 'White' if self.board.turn == chess.WHITE else 'Black'
                self.status_label.text = f'Turn: {turn}'
        if self.move_count_label:
            self.move_count_label.text = f'Moves: {len(self.move_history)}'
            
    def on_square_click(self, square):
        piece = self.board.piece_at(square)
        if self.selected is not None:
            if square == self.selected:
                self.selected = None
                self.legal_moves = []
                self.update_board()
                return
            move = chess.Move(self.selected, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                self.selected = None
                self.legal_moves = []
                self.update_board()
                return
            else:
                if piece and piece.color == self.board.turn:
                    self.selected = square
                    self.legal_moves = [m.to_square for m in self.board.legal_moves if m.from_square == square]
                    self.update_board()
                else:
                    self.selected = None
                    self.legal_moves = []
                    self.update_board()
                return
        if piece and piece.color == self.board.turn:
            self.selected = square
            self.legal_moves = [m.to_square for m in self.board.legal_moves if m.from_square == square]
            self.update_board()
        else:
            self.selected = None
            self.legal_moves = []
            self.update_board()
            
    def do_undo(self, instance):
        if self.move_history:
            self.board.pop()
            self.move_history.pop()
            self.selected = None
            self.legal_moves = []
            self.update_board()
            
    def do_reset(self, instance):
        self.board = chess.Board()
        self.move_history = []
        self.selected = None
        self.legal_moves = []
        self.flipped = False
        self.update_board()
        
    def do_flip(self, instance):
        self.flipped = not self.flipped
        self.update_board()