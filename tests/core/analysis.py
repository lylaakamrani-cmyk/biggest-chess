# © 2025 AmirAli Kamrani. All rights reserved.

# core/analysis.py
import chess
import chess.pgn
import json
import time
import math
from typing import Optional, Dict, List, Tuple, Any
from collections import defaultdict
import statistics

from core.board import BoardState
from core.stockfish_engine import StockfishEngine

class GameAnalysis:
    """Advanced game analysis with statistics and insights"""
    
    def __init__(self, stockfish_engine: StockfishEngine = None):
        self.engine = stockfish_engine
        self.analysis_data = {}
        self.moves_analysis = []
        self.position_evaluations = []
        self.game_phases = []
        self.tactical_moves = []
        self.blunders = []
        self.mistakes = []
        self.inaccuracies = []
        self.best_moves = []
        
        # Statistics
        self.stats = {
            'total_moves': 0,
            'average_centipawn_loss': 0,
            'accuracy': 0,
            'white_accuracy': 0,
            'black_accuracy': 0,
            'best_move_percentage': 0,
            'blunders_count': 0,
            'mistakes_count': 0,
            'inaccuracies_count': 0,
            'captures': 0,
            'checks': 0,
            'checkmates': 0,
            'castles': 0,
            'en_passants': 0,
            'promotions': 0
        }
        
    def analyze_game(self, board_state: BoardState, depth: int = 15) -> Dict:
        """Analyze a complete game"""
        self.analysis_data = {}
        self.moves_analysis = []
        self.position_evaluations = []
        self.tactical_moves = []
        self.blunders = []
        self.mistakes = []
        self.inaccuracies = []
        self.best_moves = []
        
        # Reset stats
        for key in self.stats:
            self.stats[key] = 0
            
        # Analyze each position
        board = board_state.board.copy()
        move_history = board_state.move_history
        
        previous_evaluation = None
        white_total_accuracy = 0
        black_total_accuracy = 0
        white_moves = 0
        black_moves = 0
        
        for i, move in enumerate(move_history):
            # Analyze position before move
            evaluation = self._analyze_position(board, depth)
            
            if evaluation:
                self.position_evaluations.append({
                    'move_number': i + 1,
                    'fen': board.fen(),
                    'evaluation': evaluation,
                    'best_move': evaluation.get('best_move'),
                    'score': evaluation.get('score')
                })
                
                # Check if this was a good move
                if previous_evaluation is not None:
                    move_quality = self._analyze_move_quality(previous_evaluation, evaluation, move)
                    self.moves_analysis.append(move_quality)
                    
                    if move_quality['classification'] == 'best':
                        self.best_moves.append(move_quality)
                        
                    if move_quality['classification'] == 'blunder':
                        self.blunders.append(move_quality)
                    elif move_quality['classification'] == 'mistake':
                        self.mistakes.append(move_quality)
                    elif move_quality['classification'] == 'inaccuracy':
                        self.inaccuracies.append(move_quality)
                        
                    # Calculate accuracy
                    accuracy = move_quality['accuracy']
                    if board.turn == chess.WHITE:
                        white_total_accuracy += accuracy
                        white_moves += 1
                    else:
                        black_total_accuracy += accuracy
                        black_moves += 1
                        
                previous_evaluation = evaluation
                
            # Make the move
            board.push(move)
            
            # Track tactical moves
            if self._is_tactical_move(board, move):
                self.tactical_moves.append({
                    'move': move.uci(),
                    'move_number': i + 1,
                    'type': self._get_tactical_type(board, move)
                })
                
            # Update stats
            self._update_stats(move, board)
            
        # Final analysis
        self.stats['total_moves'] = len(move_history)
        self.stats['white_accuracy'] = (white_total_accuracy / white_moves) if white_moves > 0 else 0
        self.stats['black_accuracy'] = (black_total_accuracy / black_moves) if black_moves > 0 else 0
        self.stats['accuracy'] = (self.stats['white_accuracy'] + self.stats['black_accuracy']) / 2
        
        self.stats['best_move_percentage'] = (len(self.best_moves) / len(move_history)) * 100 if move_history else 0
        self.stats['blunders_count'] = len(self.blunders)
        self.stats['mistakes_count'] = len(self.mistakes)
        self.stats['inaccuracies_count'] = len(self.inaccuracies)
        
        # Calculate average centipawn loss
        if self.moves_analysis:
            total_loss = sum(m.get('centipawn_loss', 0) for m in self.moves_analysis)
            self.stats['average_centipawn_loss'] = total_loss / len(self.moves_analysis)
            
        # Compile final analysis
        self.analysis_data = {
            'game_summary': self._get_game_summary(),
            'stats': self.stats,
            'tactical_moves': self.tactical_moves,
            'blunders': self.blunders,
            'mistakes': self.mistakes,
            'inaccuracies': self.inaccuracies,
            'best_moves': self.best_moves,
            'position_evaluations': self.position_evaluations,
            'move_analysis': self.moves_analysis,
            'opening': self._identify_opening(board_state),
            'game_phases': self._analyze_game_phases(board_state)
        }
        
        return self.analysis_data
        
    def _analyze_position(self, board: chess.Board, depth: int) -> Optional[Dict]:
        """Analyze a single position"""
        if not self.engine:
            return None
            
        try:
            result = self.engine.analyze_position(board, depth=depth)
            
            if 'error' not in result:
                return {
                    'fen': board.fen(),
                    'score': result.get('score', 0),
                    'best_move': result.get('best_move'),
                    'pv': result.get('pv', []),
                    'depth': result.get('depth', 0),
                    'nodes': result.get('nodes', 0)
                }
                
        except Exception as e:
            print(f"Analysis error: {e}")
            
        return None
        
    def _analyze_move_quality(self, previous_eval: Dict, current_eval: Dict, move: chess.Move) -> Dict:
        """Analyze the quality of a move"""
        previous_score = previous_eval.get('score', 0)
        current_score = current_eval.get('score', 0)
        best_move = current_eval.get('best_move')
        
        # Calculate centipawn loss
        centipawn_loss = (previous_score - current_score) if previous_score > current_score else 0
        
        # Classify the move
        classification = 'good'
        accuracy = 100
        
        if centipawn_loss > 300:
            classification = 'blunder'
            accuracy = max(0, 100 - centipawn_loss / 10)
        elif centipawn_loss > 150:
            classification = 'mistake'
            accuracy = max(0, 100 - centipawn_loss / 7)
        elif centipawn_loss > 50:
            classification = 'inaccuracy'
            accuracy = max(0, 100 - centipawn_loss / 5)
        elif move.uci() == best_move:
            classification = 'best'
            accuracy = 100
        elif centipawn_loss < 20:
            classification = 'good'
            accuracy = 95
            
        return {
            'move': move.uci(),
            'from': chess.square_name(move.from_square),
            'to': chess.square_name(move.to_square),
            'previous_score': previous_score,
            'current_score': current_score,
            'centipawn_loss': centipawn_loss,
            'classification': classification,
            'accuracy': accuracy,
            'is_best_move': move.uci() == best_move
        }
        
    def _is_tactical_move(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if a move is tactical"""
        # Check if it's a capture
        if board.is_capture(move):
            return True
            
        # Check if it gives check
        board_copy = board.copy()
        board_copy.push(move)
        if board_copy.is_check():
            return True
            
        # Check if it's a promotion
        if move.promotion:
            return True
            
        return False
        
    def _get_tactical_type(self, board: chess.Board, move: chess.Move) -> str:
        """Get tactical type of a move"""
        board_copy = board.copy()
        board_copy.push(move)
        
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                if captured_piece.piece_type == chess.QUEEN:
                    return 'queen_capture'
                elif captured_piece.piece_type == chess.ROOK:
                    return 'rook_capture'
                elif captured_piece.piece_type == chess.BISHOP:
                    return 'bishop_capture'
                elif captured_piece.piece_type == chess.KNIGHT:
                    return 'knight_capture'
                elif captured_piece.piece_type == chess.PAWN:
                    return 'pawn_capture'
                    
        if board_copy.is_checkmate():
            return 'checkmate'
        elif board_copy.is_check():
            return 'check'
            
        if move.promotion:
            return f'promotion_to_{chess.piece_name(move.promotion)}'
            
        return 'tactical'
        
    def _update_stats(self, move: chess.Move, board: chess.Board):
        """Update game statistics"""
        # Captures
        if board.is_capture(move):
            self.stats['captures'] += 1
            
        # Checks
        board_copy = board.copy()
        board_copy.push(move)
        if board_copy.is_check():
            self.stats['checks'] += 1
            
        # Checkmates
        if board_copy.is_checkmate():
            self.stats['checkmates'] += 1
            
        # Castles
        if board.is_castling(move):
            self.stats['castles'] += 1
            
        # En passant
        if board.is_en_passant(move):
            self.stats['en_passants'] += 1
            
        # Promotions
        if move.promotion:
            self.stats['promotions'] += 1
            
    def _get_game_summary(self) -> Dict:
        """Get game summary"""
        return {
            'total_moves': self.stats['total_moves'],
            'accuracy': self.stats['accuracy'],
            'white_accuracy': self.stats['white_accuracy'],
            'black_accuracy': self.stats['black_accuracy'],
            'average_loss': self.stats['average_centipawn_loss'],
            'best_moves': self.stats['best_move_percentage'],
            'blunders': self.stats['blunders_count'],
            'mistakes': self.stats['mistakes_count'],
            'inaccuracies': self.stats['inaccuracies_count']
        }
        
    def _identify_opening(self, board_state: BoardState) -> Dict:
        """Identify the opening used in the game"""
        # Simplified opening identification
        moves = board_state.move_history
        if not moves:
            return {'name': 'Unknown', 'eco': ''}
            
        # Convert moves to SAN
        board = chess.Board()
        san_moves = []
        for move in moves[:10]:  # Check first 10 moves
            san_moves.append(board.san(move))
            board.push(move)
            
        opening_moves = ' '.join(san_moves)
        
        # Check against opening database (simplified)
        openings = {
            'e4 e5 Nf3 Nc6 Bb5': {'name': 'Ruy Lopez', 'eco': 'C60-C99'},
            'd4 d5 c4 e6': {'name': 'Queen\'s Gambit Declined', 'eco': 'D30-D69'},
            'e4 c5 Nf3 d6 d4 cxd4': {'name': 'Sicilian Defense', 'eco': 'B20-B99'},
            'd4 Nf6 c4 g6 Nc3 d5': {'name': 'King\'s Indian Defense', 'eco': 'E60-E99'},
            'd4 d5 c4 c6': {'name': 'Slav Defense', 'eco': 'D10-D19'},
            'e4 e5 Nf3 Nc6 Bc4': {'name': 'Italian Game', 'eco': 'C50-C59'}
        }
        
        # Check if any opening matches
        for pattern, info in openings.items():
            if opening_moves.startswith(pattern):
                return {'name': info['name'], 'eco': info['eco']}
                
        # Check by first few moves
        first_moves = ' '.join(san_moves[:2])
        if first_moves == 'e4 e5':
            return {'name': 'Open Game', 'eco': 'C20-C59'}
        elif first_moves == 'd4 d5':
            return {'name': 'Closed Game', 'eco': 'D00-D69'}
        elif first_moves == 'e4 c5':
            return {'name': 'Sicilian Defense', 'eco': 'B20-B99'}
        elif first_moves == 'd4 Nf6':
            return {'name': 'Indian Defense', 'eco': 'E00-E99'}
            
        return {'name': 'Unknown', 'eco': ''}
        
    def _analyze_game_phases(self, board_state: BoardState) -> List[Dict]:
        """Analyze game phases"""
        phases = []
        move_count = len(board_state.move_history)
        
        if move_count == 0:
            return phases
            
        # Determine phase boundaries
        opening_end = min(10, move_count // 2)
        middlegame_end = max(opening_end, move_count - 10)
        
        # Opening phase
        if opening_end > 0:
            phases.append({
                'phase': 'opening',
                'start': 0,
                'end': opening_end,
                'moves': opening_end
            })
            
        # Middle game
        if middlegame_end > opening_end:
            phases.append({
                'phase': 'middlegame',
                'start': opening_end,
                'end': middlegame_end,
                'moves': middlegame_end - opening_end
            })
            
        # Endgame
        if move_count > middlegame_end:
            phases.append({
                'phase': 'endgame',
                'start': middlegame_end,
                'end': move_count,
                'moves': move_count - middlegame_end
            })
            
        return phases
        
    def get_player_performance(self, color: chess.Color) -> Dict:
        """Get performance analysis for a specific player"""
        if color == chess.WHITE:
            accuracy = self.stats['white_accuracy']
            moves_analyzed = len([m for m in self.moves_analysis if m.get('color') == 'white'])
        else:
            accuracy = self.stats['black_accuracy']
            moves_analyzed = len([m for m in self.moves_analysis if m.get('color') == 'black'])
            
        return {
            'accuracy': accuracy,
            'moves_analyzed': moves_analyzed,
            'best_moves': len([m for m in self.best_moves if m.get('color') == color.name.lower()]),
            'blunders': len([m for m in self.blunders if m.get('color') == color.name.lower()]),
            'mistakes': len([m for m in self.mistakes if m.get('color') == color.name.lower()]),
            'inaccuracies': len([m for m in self.inaccuracies if m.get('color') == color.name.lower()])
        }
        
    def get_tactical_stats(self) -> Dict:
        """Get tactical statistics"""
        tactical_types = defaultdict(int)
        for move in self.tactical_moves:
            tactical_types[move['type']] += 1
            
        return {
            'total_tactical': len(self.tactical_moves),
            'types': dict(tactical_types),
            'captures': self.stats['captures'],
            'checks': self.stats['checks'],
            'checkmates': self.stats['checkmates'],
            'promotions': self.stats['promotions']
        }
        
    def get_positional_evaluation(self, move_number: int) -> Optional[Dict]:
        """Get evaluation for a specific move number"""
        for eval_data in self.position_evaluations:
            if eval_data['move_number'] == move_number:
                return eval_data
        return None
        
    def get_best_moves_list(self) -> List[Dict]:
        """Get list of best moves in the game"""
        return self.best_moves
        
    def get_blunders_list(self) -> List[Dict]:
        """Get list of blunders in the game"""
        return self.blunders
        
    def get_mistakes_list(self) -> List[Dict]:
        """Get list of mistakes in the game"""
        return self.mistakes
        
    def get_inaccuracies_list(self) -> List[Dict]:
        """Get list of inaccuracies in the game"""
        return self.inaccuracies
        
    def export_analysis(self, format: str = 'json') -> str:
        """Export analysis in different formats"""
        if format == 'json':
            return json.dumps(self.analysis_data, indent=2)
        elif format == 'pgn':
            return self._export_as_pgn()
        elif format == 'html':
            return self._export_as_html()
        else:
            return json.dumps(self.analysis_data)
            
    def _export_as_pgn(self) -> str:
        """Export analysis as PGN with annotations"""
        # Simplified PGN export with analysis
        pgn = "[Event \"Analyzed Game\"]\n"
        pgn += f"[Date \"{time.strftime('%Y.%m.%d')}\"]\n"
        pgn += f"[Result \"*\"]\n\n"
        
        # Add moves with analysis
        for i, move_analysis in enumerate(self.moves_analysis):
            move = move_analysis['move']
            classification = move_analysis['classification']
            
            if i % 2 == 0:
                pgn += f"{i//2 + 1}. "
                
            pgn += move
            
            # Add annotation
            if classification == 'best':
                pgn += " !"
            elif classification == 'blunder':
                pgn += " ??"
            elif classification == 'mistake':
                pgn += " ?"
            elif classification == 'inaccuracy':
                pgn += " ?!"
                
            pgn += " "
            
        return pgn
        
    def _export_as_html(self) -> str:
        """Export analysis as HTML report"""
        html = """
        <html>
        <head><title>Game Analysis Report</title>
        <style>
            body { font-family: Arial; margin: 20px; }
            .summary { background: #f0f0f0; padding: 15px; border-radius: 5px; }
            .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
            .stat-card { background: white; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            .blunder { color: red; }
            .mistake { color: orange; }
            .inaccuracy { color: yellow; }
            .best { color: green; }
        </style>
        </head>
        <body>
        """
        
        # Summary
        summary = self._get_game_summary()
        html += f"""
        <h2>Game Analysis Summary</h2>
        <div class="summary">
            <p>Total Moves: {summary['total_moves']}</p>
            <p>Accuracy: {summary['accuracy']:.1f}%</p>
            <p>White Accuracy: {summary['white_accuracy']:.1f}%</p>
            <p>Black Accuracy: {summary['black_accuracy']:.1f}%</p>
            <p>Average Centipawn Loss: {summary['average_loss']:.1f}</p>
            <p>Best Moves: {summary['best_moves']:.1f}%</p>
            <p>Blunders: {summary['blunders']}</p>
            <p>Mistakes: {summary['mistakes']}</p>
            <p>Inaccuracies: {summary['inaccuracies']}</p>
        </div>
        """
        
        # Move list
        html += "<h3>Move Analysis</h3><table border='1'>"
        html += "<tr><th>Move</th><th>Classification</th><th>Loss</th><th>Accuracy</th></tr>"
        
        for move in self.moves_analysis:
            classification = move['classification']
            css_class = classification
            html += f"""
            <tr>
                <td>{move['move']}</td>
                <td class='{css_class}'>{classification}</td>
                <td>{move['centipawn_loss']:.1f}</td>
                <td>{move['accuracy']:.1f}%</td>
            </tr>
            """
            
        html += "</table>"
        
        # Blunders list
        if self.blunders:
            html += "<h3>Blunders</h3><ul>"
            for blunder in self.blunders:
                html += f"<li class='blunder'>{blunder['move']} (Loss: {blunder['centipawn_loss']:.1f})</li>"
            html += "</ul>"
            
        html += "</body></html>"
        
        return html