# © 2025 AmirAli Kamrani. All rights reserved.

# core/tournament.py
import time
import uuid
import json
import random
import threading
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum
from dataclasses import dataclass, asdict
import math

# ✅ تغییر: import مطلق به جای نسبی
from core.database import Database
from core.elo import EloCalculator
from core.game_logic import GameLogic, GameResult

class TournamentType(Enum):
    SWISS = "swiss"
    ROUND_ROBIN = "round_robin"
    KNOCKOUT = "knockout"
    DOUBLE_ELIMINATION = "double_elimination"
    RAPID = "rapid"
    BLITZ = "blitz"

class TournamentStatus(Enum):
    WAITING = "waiting"
    REGISTRATION = "registration"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class TournamentPlayer:
    user_id: int
    username: str
    rating: int
    score: float
    games_played: int
    wins: int
    losses: int
    draws: int
    tiebreak: float
    eliminated: bool
    seed: int

class Tournament:
    def __init__(self, db: Database, elo: EloCalculator):
        self.db = db
        self.elo = elo
        self.tournament_id = None
        self.tournament_data = None
        self.players = {}
        self.games = []
        self.rounds = []
        self.current_round = 0
        self.status = TournamentStatus.WAITING
        
        self.config = {
            'type': TournamentType.SWISS,
            'max_players': 16,
            'min_players': 4,
            'rounds': 5,
            'time_control': '10+0',
            'rated': True,
            'prize_pool': {},
            'rules': {},
            'start_date': None,
            'registration_deadline': None
        }
        
        self.matchmaking_thread = None
        self.is_running = False
        
    def create_tournament(self, name: str, config: Dict) -> str:
        self.tournament_id = str(uuid.uuid4())
        self.tournament_data = {
            'id': self.tournament_id,
            'name': name,
            'type': config.get('type', TournamentType.SWISS).value,
            'status': TournamentStatus.WAITING.value,
            'max_players': config.get('max_players', 16),
            'current_players': 0,
            'created_by': config.get('created_by'),
            'created_at': int(time.time()),
            'prize_pool': json.dumps(config.get('prize_pool', {})),
            'rules': json.dumps(config.get('rules', {})),
            'rounds': config.get('rounds', 5),
            'current_round': 0,
            'time_control': config.get('time_control', '10+0')
        }
        
        tournament_id = self.db.create_tournament(self.tournament_data)
        self.status = TournamentStatus.REGISTRATION
        return tournament_id
        
    def register_player(self, user_id: int, username: str, rating: int) -> bool:
        if self.status not in [TournamentStatus.WAITING, TournamentStatus.REGISTRATION]:
            return False
        if len(self.players) >= self.config['max_players']:
            return False
        if user_id in self.players:
            return False
            
        self.players[user_id] = TournamentPlayer(
            user_id=user_id,
            username=username,
            rating=rating,
            score=0,
            games_played=0,
            wins=0,
            losses=0,
            draws=0,
            tiebreak=0,
            eliminated=False,
            seed=len(self.players) + 1
        )
        
        self.db.join_tournament(self.tournament_id, user_id)
        return True
        
    def unregister_player(self, user_id: int) -> bool:
        if user_id in self.players:
            del self.players[user_id]
            return True
        return False
        
    def start_tournament(self) -> bool:
        if self.status != TournamentStatus.REGISTRATION:
            return False
        if len(self.players) < self.config['min_players']:
            return False
            
        self.status = TournamentStatus.IN_PROGRESS
        self.current_round = 0
        self._generate_round()
        return True
        
    def _generate_round(self):
        if self.current_round >= self.config['rounds']:
            self.finish_tournament()
            return
            
        self.current_round += 1
        active_players = [p for p in self.players.values() if not p.eliminated]
        
        if len(active_players) < 2:
            self.finish_tournament()
            return
            
        if self.config['type'] == TournamentType.SWISS:
            pairings = self._generate_swiss_pairings(active_players)
        elif self.config['type'] == TournamentType.ROUND_ROBIN:
            pairings = self._generate_round_robin_pairings(active_players)
        elif self.config['type'] == TournamentType.KNOCKOUT:
            pairings = self._generate_knockout_pairings(active_players)
        else:
            pairings = self._generate_swiss_pairings(active_players)
            
        round_games = []
        for pairing in pairings:
            if pairing:
                game_id = str(uuid.uuid4())
                round_games.append({
                    'game_id': game_id,
                    'round': self.current_round,
                    'player1': pairing[0].user_id,
                    'player2': pairing[1].user_id,
                    'status': 'pending',
                    'result': None
                })
                
        self.rounds.append(round_games)
        self.games.extend(round_games)
        self._save_round_games(round_games)
        
    def _generate_swiss_pairings(self, players: List[TournamentPlayer]) -> List[Tuple]:
        sorted_players = sorted(players, key=lambda p: (p.score, p.rating), reverse=True)
        pairings = []
        used = set()
        
        for i, player in enumerate(sorted_players):
            if player.user_id in used:
                continue
                
            opponent = None
            for j in range(i + 1, len(sorted_players)):
                candidate = sorted_players[j]
                if candidate.user_id in used:
                    continue
                if not self._have_played_before(player.user_id, candidate.user_id):
                    opponent = candidate
                    break
                    
            if opponent:
                pairings.append((player, opponent))
                used.add(player.user_id)
                used.add(opponent.user_id)
            else:
                pairings.append((player, None))
                used.add(player.user_id)
                
        return pairings
        
    def _generate_round_robin_pairings(self, players: List[TournamentPlayer]) -> List[Tuple]:
        n = len(players)
        if n % 2 == 1:
            players.append(None)
            
        pairings = []
        for i in range(n // 2):
            if players[i] and players[n - 1 - i]:
                pairings.append((players[i], players[n - 1 - i]))
            elif players[i]:
                pairings.append((players[i], None))
            elif players[n - 1 - i]:
                pairings.append((players[n - 1 - i], None))
                
        return pairings
        
    def _generate_knockout_pairings(self, players: List[TournamentPlayer]) -> List[Tuple]:
        sorted_players = sorted(players, key=lambda p: p.seed)
        pairings = []
        for i in range(0, len(sorted_players), 2):
            if i + 1 < len(sorted_players):
                pairings.append((sorted_players[i], sorted_players[i + 1]))
            else:
                pairings.append((sorted_players[i], None))
        return pairings
        
    def _have_played_before(self, player1_id: int, player2_id: int) -> bool:
        for game in self.games:
            if (game['player1'] == player1_id and game['player2'] == player2_id) or \
               (game['player1'] == player2_id and game['player2'] == player1_id):
                return True
        return False
        
    def submit_game_result(self, game_id: str, result: str) -> bool:
        game = None
        for g in self.games:
            if g['game_id'] == game_id:
                game = g
                break
                
        if not game:
            return False
            
        game['status'] = 'completed'
        game['result'] = result
        
        player1 = self.players.get(game['player1'])
        player2 = self.players.get(game['player2'])
        
        if not player1 or not player2:
            return False
            
        player1.games_played += 1
        player2.games_played += 1
        
        if result == 'white_win':
            player1.wins += 1
            player1.score += 1
            player2.losses += 1
            if self.config['rated']:
                self._update_elo(player1, player2, 1)
        elif result == 'black_win':
            player2.wins += 1
            player2.score += 1
            player1.losses += 1
            if self.config['rated']:
                self._update_elo(player1, player2, 0)
        elif result == 'draw':
            player1.draws += 1
            player2.draws += 1
            player1.score += 0.5
            player2.score += 0.5
            if self.config['rated']:
                self._update_elo(player1, player2, 0.5)
                
        self._check_round_completion()
        self._update_game_result(game_id, result)
        return True
        
    def _update_elo(self, player1: TournamentPlayer, player2: TournamentPlayer, result: float):
        rating1 = player1.rating
        rating2 = player2.rating
        elo_change = self.elo.calculate_elo_change(rating1, rating2, result)
        new_rating1 = elo_change['new_rating']
        new_rating2 = rating2 - (new_rating1 - rating1)
        player1.rating = new_rating1
        player2.rating = new_rating2
        self.db.update_user_rating(player1.user_id, int(new_rating1))
        self.db.update_user_rating(player2.user_id, int(new_rating2))
        
    def _check_round_completion(self):
        if self.current_round <= len(self.rounds):
            round_games = self.rounds[self.current_round - 1]
            all_completed = all(g['status'] == 'completed' for g in round_games)
            if all_completed:
                self._generate_round()
                
    def _save_round_games(self, games: List[Dict]):
        for game in games:
            self.db.cursor.execute('''
                INSERT INTO tournament_games (
                    tournament_id, game_id, round_number,
                    player1_id, player2_id, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.tournament_id, game['game_id'], game['round'],
                  game['player1'], game['player2'], game['status']))
        self.db.connection.commit()
        
    def _update_game_result(self, game_id: str, result: str):
        self.db.cursor.execute('''
            UPDATE tournament_games
            SET result = ?, status = 'completed'
            WHERE game_id = ?
        ''', (result, game_id))
        self.db.connection.commit()
        
    def finish_tournament(self):
        self.status = TournamentStatus.COMPLETED
        standings = self.get_standings()
        self._award_prizes(standings)
        self._save_final_results(standings)
        
    def _award_prizes(self, standings: List[Dict]):
        prize_pool = json.loads(self.config.get('prize_pool', '{}'))
        if not prize_pool:
            return
            
        for i, player in enumerate(standings[:3]):
            prize = prize_pool.get(str(i + 1), 0)
            if prize:
                self.db.add_coins(player['user_id'], prize)
                
        for player in standings:
            exp = max(10, 100 - player['rank'] * 5)
            self.db.cursor.execute('''
                UPDATE users SET experience = experience + ?
                WHERE id = ?
            ''', (exp, player['user_id']))
        self.db.connection.commit()
        
    def _save_final_results(self, standings: List[Dict]):
        self.db.cursor.execute('''
            UPDATE tournaments
            SET status = ?, ended_at = ?
            WHERE id = ?
        ''', (TournamentStatus.COMPLETED.value, int(time.time()), self.tournament_id))
        
        self.db.cursor.execute('''
            UPDATE tournaments
            SET prize_pool = ?
            WHERE id = ?
        ''', (json.dumps({'standings': standings}), self.tournament_id))
        self.db.connection.commit()
        
    def get_standings(self) -> List[Dict]:
        standings = []
        for player in self.players.values():
            standings.append({
                'rank': 0,
                'user_id': player.user_id,
                'username': player.username,
                'rating': player.rating,
                'score': player.score,
                'games_played': player.games_played,
                'wins': player.wins,
                'losses': player.losses,
                'draws': player.draws,
                'tiebreak': player.tiebreak,
                'eliminated': player.eliminated
            })
        standings.sort(key=lambda p: (p['score'], p['tiebreak'], p['rating']), reverse=True)
        for i, player in enumerate(standings):
            player['rank'] = i + 1
        return standings
        
    def get_current_round(self) -> int:
        return self.current_round
        
    def get_total_rounds(self) -> int:
        return self.config['rounds']
        
    def get_games_for_round(self, round_num: int) -> List[Dict]:
        if round_num <= len(self.rounds):
            return self.rounds[round_num - 1]
        return []
        
    def get_player_games(self, user_id: int) -> List[Dict]:
        player_games = []
        for game in self.games:
            if game['player1'] == user_id or game['player2'] == user_id:
                player_games.append(game)
        return player_games
        
    def get_tournament_stats(self) -> Dict:
        total_games = len(self.games)
        completed_games = len([g for g in self.games if g['status'] == 'completed'])
        return {
            'tournament_id': self.tournament_id,
            'status': self.status.value,
            'current_round': self.current_round,
            'total_rounds': self.config['rounds'],
            'total_players': len(self.players),
            'total_games': total_games,
            'completed_games': completed_games,
            'progress': (completed_games / total_games * 100) if total_games > 0 else 0,
            'type': self.config['type'].value
        }
        
    def is_player_eligible(self, user_id: int) -> bool:
        if user_id not in self.players:
            return False
        player = self.players[user_id]
        if player.eliminated:
            return False
        player_games = self.get_player_games(user_id)
        if len(player_games) >= self.current_round:
            return False
        return True
        
    def get_pairings(self) -> List[Dict]:
        if self.current_round <= len(self.rounds):
            round_games = self.rounds[self.current_round - 1]
            pairings = []
            for game in round_games:
                pairings.append({
                    'game_id': game['game_id'],
                    'white': self.players.get(game['player1']).username if game['player1'] else None,
                    'black': self.players.get(game['player2']).username if game['player2'] else None,
                    'white_id': game['player1'],
                    'black_id': game['player2'],
                    'status': game['status']
                })
            return pairings
        return []
        
    def get_remaining_games(self) -> int:
        if self.status == TournamentStatus.COMPLETED:
            return 0
        total_needed = self.config['rounds'] * (len(self.players) // 2)
        completed = len([g for g in self.games if g['status'] == 'completed'])
        return total_needed - completed
        
    def cancel_tournament(self):
        self.status = TournamentStatus.CANCELLED
        self.db.cursor.execute('''
            UPDATE tournaments
            SET status = ? WHERE id = ?
        ''', (TournamentStatus.CANCELLED.value, self.tournament_id))
        self.db.connection.commit()
        
    def get_winner(self) -> Optional[Dict]:
        if self.status != TournamentStatus.COMPLETED:
            return None
        standings = self.get_standings()
        return standings[0] if standings else None
        
    def get_top_players(self, n: int = 3) -> List[Dict]:
        standings = self.get_standings()
        return standings[:n]
        
    def export_results(self) -> Dict:
        return {
            'tournament_id': self.tournament_id,
            'name': self.tournament_data['name'],
            'type': self.config['type'].value,
            'status': self.status.value,
            'rounds_played': self.current_round,
            'total_rounds': self.config['rounds'],
            'players': [asdict(p) for p in self.players.values()],
            'games': self.games,
            'standings': self.get_standings(),
            'winner': self.get_winner()
        }