# © 2025 AmirAli Kamrani. All rights reserved.

# ui/analysis.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
import chess
import chess.pgn
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.board import BoardState
from core.analysis import GameAnalysis
from core.stockfish_engine import StockfishEngine


class AnalysisScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = chess.Board()
        self.move_history = []
        self.selected_square = None
        self.legal_moves = []
        self.flipped = False
        self.board_grid = None
        self.status_label = None
        self.move_count_label = None
        self.analysis = None
        self.stockfish = None
        self.is_analyzing = False
        self.build_ui()
        self.update_board()
        self.init_analysis()
        
    def init_analysis(self):
        try:
            self.stockfish = StockfishEngine()
            self.analysis = GameAnalysis(self.stockfish)
        except:
            self.analysis = None
            
    def get_piece_symbol(self, piece):
        if not piece:
            return ''
        symbols = {
            'r': 'r', 'n': 'n', 'b': 'b', 'q': 'q', 'k': 'k', 'p': 'p',
            'R': 'R', 'N': 'N', 'B': 'B', 'Q': 'Q', 'K': 'K', 'P': 'P'
        }
        return symbols.get(piece.symbol(), '')
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
        
        # Header
        header = BoxLayout(size_hint_y=0.06)
        back = Button(text='< Back', font_size=dp(18), size_hint_x=0.18,
                     background_normal='', background_color=(0.2, 0.2, 0.35, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text='Game Analysis', font_size=dp(22), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Board
        self.board_grid = GridLayout(cols=8, rows=8, size_hint=(1, 0.5))
        layout.add_widget(self.board_grid)
        
        # Status
        info = BoxLayout(size_hint_y=0.04, spacing=dp(10))
        self.status_label = Label(text='Position: Start', font_size=dp(14), color=(0.7, 0.7, 0.7, 1))
        self.move_count_label = Label(text='Moves: 0', font_size=dp(14), color=(0.7, 0.7, 0.7, 1))
        info.add_widget(self.status_label)
        info.add_widget(self.move_count_label)
        layout.add_widget(info)
        
        # Controls
        controls = BoxLayout(size_hint_y=0.06, spacing=dp(5))
        
        reset_btn = Button(text='New Game', font_size=dp(13), background_normal='', background_color=(0.2, 0.2, 0.35, 1))
        reset_btn.bind(on_release=self.do_reset)
        controls.add_widget(reset_btn)
        
        flip_btn = Button(text='Flip', font_size=dp(13), background_normal='', background_color=(0.2, 0.2, 0.35, 1))
        flip_btn.bind(on_release=self.do_flip)
        controls.add_widget(flip_btn)
        
        analyze_btn = Button(text='Analyze', font_size=dp(13), background_normal='', background_color=(0.97, 0.59, 0.12, 1))
        analyze_btn.bind(on_release=self.do_analyze)
        controls.add_widget(analyze_btn)
        
        layout.add_widget(controls)
        
        # Analysis results
        scroll = ScrollView(size_hint_y=0.30)
        self.result_grid = GridLayout(cols=1, spacing=dp(3), size_hint_y=None)
        self.result_grid.bind(minimum_height=self.result_grid.setter('height'))
        scroll.add_widget(self.result_grid)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
    def update_board(self):
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
                bg = (0.94, 0.85, 0.71, 1) if is_light else (0.71, 0.53, 0.39, 1)
                if self.selected_square == square:
                    bg = (0.5, 0.8, 0.5, 0.8)
                if square in self.legal_moves:
                    bg = (0.3, 0.8, 0.3, 0.5)
                btn = Button(text=self.get_piece_symbol(piece), font_size=dp(30),
                            background_normal='', background_color=bg,
                            color=(1, 1, 1, 1) if piece and piece.color == chess.WHITE else (0, 0, 0, 1),
                            bold=True)
                btn.bind(on_release=lambda x, sq=square: self.on_square_click(sq))
                self.board_grid.add_widget(btn)
        
        if self.status_label:
            self.status_label.text = f'Position: {len(self.move_history)} moves'
        if self.move_count_label:
            self.move_count_label.text = f'Moves: {len(self.move_history)}'
            
    def on_square_click(self, square):
        piece = self.board.piece_at(square)
        if self.selected_square is not None:
            if square == self.selected_square:
                self.selected_square = None
                self.legal_moves = []
                self.update_board()
                return
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                self.selected_square = None
                self.legal_moves = []
                self.update_board()
                return
            else:
                if piece and piece.color == self.board.turn:
                    self.selected_square = square
                    self.legal_moves = [m.to_square for m in self.board.legal_moves if m.from_square == square]
                    self.update_board()
                else:
                    self.selected_square = None
                    self.legal_moves = []
                    self.update_board()
                return
        if piece and piece.color == self.board.turn:
            self.selected_square = square
            self.legal_moves = [m.to_square for m in self.board.legal_moves if m.from_square == square]
            self.update_board()
        else:
            self.selected_square = None
            self.legal_moves = []
            self.update_board()
            
    def do_reset(self, instance):
        self.board = chess.Board()
        self.move_history = []
        self.selected_square = None
        self.legal_moves = []
        self.flipped = False
        self.result_grid.clear_widgets()
        self.update_board()
        
    def do_flip(self, instance):
        self.flipped = not self.flipped
        self.update_board()
        
    def do_analyze(self, instance):
        if self.is_analyzing:
            return
            
        if len(self.move_history) == 0:
            popup = Popup(title='Info', content=Label(text='Please make some moves first!', font_size=dp(16)),
                         size_hint=(0.7, 0.3))
            popup.open()
            return
            
        self.is_analyzing = True
        self.status_label.text = 'Analyzing...'
        Clock.schedule_once(self.run_analysis, 0.5)
        
    def run_analysis(self, dt):
        self.result_grid.clear_widgets()
        
        try:
            # Create board state from history
            board_state = BoardState()
            for move in self.move_history:
                board_state.make_move(move)
                
            if self.analysis:
                # Run full analysis
                result = self.analysis.analyze_game(board_state)
                
                if result:
                    stats = result.get('stats', {})
                    accuracy = stats.get('accuracy', 0)
                    white_acc = stats.get('white_accuracy', 0)
                    black_acc = stats.get('black_accuracy', 0)
                    blunders = stats.get('blunders_count', 0)
                    mistakes = stats.get('mistakes_count', 0)
                    inaccuracies = stats.get('inaccuracies_count', 0)
                    best_moves = stats.get('best_move_percentage', 0)
                    
                    # Display results
                    results = [
                        ('Accuracy', f'{accuracy:.1f}%'),
                        ('White Accuracy', f'{white_acc:.1f}%'),
                        ('Black Accuracy', f'{black_acc:.1f}%'),
                        ('Best Moves', f'{best_moves:.1f}%'),
                        ('Blunders', str(blunders)),
                        ('Mistakes', str(mistakes)),
                        ('Inaccuracies', str(inaccuracies)),
                        ('Total Moves', str(len(self.move_history)))
                    ]
                    
                    for label, value in results:
                        row = BoxLayout(size_hint_y=None, height=dp(25))
                        row.add_widget(Label(text=label, font_size=dp(13), color=(0.8, 0.8, 0.8, 1), size_hint_x=0.5))
                        row.add_widget(Label(text=value, font_size=dp(13), color=(1, 1, 0.6, 1), size_hint_x=0.5))
                        self.result_grid.add_widget(row)
                        
                    # Show move analysis
                    if 'move_analysis' in result:
                        self.result_grid.add_widget(Widget(size_hint_y=None, height=dp(5)))
                        self.result_grid.add_widget(Label(text='Move Analysis:', font_size=dp(14), 
                                                         color=(1, 1, 0.6, 1), size_hint_y=None, height=dp(20)))
                        
                        for ma in result['move_analysis'][-10:]:  # Last 10 moves
                            row = BoxLayout(size_hint_y=None, height=dp(20))
                            move_text = ma.get('move', '')
                            classification = ma.get('classification', '')
                            color_map = {
                                'best': (0.2, 0.8, 0.2, 1),
                                'good': (0.2, 0.6, 0.2, 1),
                                'inaccuracy': (1, 0.8, 0, 1),
                                'mistake': (1, 0.6, 0, 1),
                                'blunder': (1, 0.2, 0.2, 1)
                            }
                            color = color_map.get(classification, (0.7, 0.7, 0.7, 1))
                            row.add_widget(Label(text=move_text, font_size=dp(12), color=color, size_hint_x=0.4))
                            row.add_widget(Label(text=classification, font_size=dp(12), color=color, size_hint_x=0.3))
                            loss = ma.get('centipawn_loss', 0)
                            row.add_widget(Label(text=f'{loss:.1f}cp', font_size=dp(12), color=color, size_hint_x=0.3))
                            self.result_grid.add_widget(row)
                            
                else:
                    self.result_grid.add_widget(Label(text='Analysis failed', font_size=dp(14), color=(1, 0.2, 0.2, 1)))
            else:
                # Simple analysis without Stockfish
                self.result_grid.add_widget(Label(text='Simple Analysis:', font_size=dp(16), color=(1, 1, 0.6, 1)))
                row = BoxLayout(size_hint_y=None, height=dp(25))
                row.add_widget(Label(text='Moves', font_size=dp(14), color=(0.8, 0.8, 0.8, 1), size_hint_x=0.5))
                row.add_widget(Label(text=str(len(self.move_history)), font_size=dp(14), color=(1, 1, 0.6, 1), size_hint_x=0.5))
                self.result_grid.add_widget(row)
                
                # Count captures
                captures = sum(1 for move in self.move_history if self.board.is_capture(move) or 
                              any(self.board.is_capture(m) for m in self.move_history[:self.move_history.index(move)+1]))
                
                # Check if checkmate
                if self.board.is_checkmate():
                    self.result_grid.add_widget(Label(text='Checkmate!', font_size=dp(14), color=(1, 0.8, 0, 1)))
                elif self.board.is_check():
                    self.result_grid.add_widget(Label(text='Check!', font_size=dp(14), color=(1, 0.8, 0, 1)))
                    
        except Exception as e:
            self.result_grid.add_widget(Label(text=f'Analysis error: {str(e)}', font_size=dp(14), color=(1, 0.2, 0.2, 1)))
            
        self.is_analyzing = False
        self.status_label.text = 'Analysis complete'