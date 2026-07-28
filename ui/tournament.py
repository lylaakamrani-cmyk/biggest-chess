# © 2025 AmirAli Kamrani. All rights reserved.

# ui/tournament.py
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
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tournament import Tournament, TournamentType
from core.database import Database
from core.elo import EloCalculator


class TournamentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tournament = None
        self.players = []
        self.matches = []
        self.current_round = 0
        self.total_rounds = 0
        self.standings = []
        self.is_started = False
        self.db = None
        self.elo = None
        self.init_tournament()
        self.build_ui()
        
    def init_tournament(self):
        try:
            self.db = Database('data/chess_data.db')
            self.elo = EloCalculator()
            self.tournament = Tournament(self.db, self.elo)
        except:
            self.tournament = None
            
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
        
        # Header
        header = BoxLayout(size_hint_y=0.06)
        back = Button(text='< Back', font_size=dp(18), size_hint_x=0.18,
                     background_normal='', background_color=(0.2, 0.2, 0.35, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text='Tournament', font_size=dp(22), color=(1, 1, 1, 1), bold=True)
        header.add_widget(back)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Info bar
        info = BoxLayout(size_hint_y=0.05, spacing=dp(8))
        self.round_label = Label(text='Round: 0/0', font_size=dp(14), color=(0.7, 0.7, 0.7, 1))
        self.players_label = Label(text='Players: 0', font_size=dp(14), color=(0.7, 0.7, 0.7, 1))
        info.add_widget(self.round_label)
        info.add_widget(self.players_label)
        layout.add_widget(info)
        
        # Controls
        controls = BoxLayout(size_hint_y=0.06, spacing=dp(5))
        
        add_btn = Button(text='Add Player', font_size=dp(13), background_normal='', background_color=(0.2, 0.7, 0.2, 1))
        add_btn.bind(on_release=self.add_player)
        controls.add_widget(add_btn)
        
        start_btn = Button(text='Start', font_size=dp(13), background_normal='', background_color=(0.97, 0.59, 0.12, 1))
        start_btn.bind(on_release=self.start_tournament)
        controls.add_widget(start_btn)
        
        next_btn = Button(text='Next Round', font_size=dp(13), background_normal='', background_color=(0.2, 0.4, 0.8, 1))
        next_btn.bind(on_release=self.next_round)
        controls.add_widget(next_btn)
        
        reset_btn = Button(text='Reset', font_size=dp(13), background_normal='', background_color=(0.6, 0.1, 0.1, 1))
        reset_btn.bind(on_release=self.reset_tournament)
        controls.add_widget(reset_btn)
        
        layout.add_widget(controls)
        
        # Players list
        players_label = Label(text='Players:', font_size=dp(14), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.04)
        layout.add_widget(players_label)
        
        scroll_players = ScrollView(size_hint_y=0.15)
        self.players_grid = GridLayout(cols=4, spacing=dp(4), size_hint_y=None)
        self.players_grid.bind(minimum_height=self.players_grid.setter('height'))
        scroll_players.add_widget(self.players_grid)
        layout.add_widget(scroll_players)
        
        # Bracket
        bracket_label = Label(text='Bracket:', font_size=dp(14), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.04)
        layout.add_widget(bracket_label)
        
        scroll_bracket = ScrollView(size_hint_y=0.45)
        self.bracket_grid = GridLayout(cols=1, spacing=dp(3), size_hint_y=None)
        self.bracket_grid.bind(minimum_height=self.bracket_grid.setter('height'))
        scroll_bracket.add_widget(self.bracket_grid)
        layout.add_widget(scroll_bracket)
        
        # Standings
        standings_label = Label(text='Standings:', font_size=dp(14), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.04)
        layout.add_widget(standings_label)
        
        scroll_standings = ScrollView(size_hint_y=0.15)
        self.standings_grid = GridLayout(cols=4, spacing=dp(4), size_hint_y=None)
        self.standings_grid.bind(minimum_height=self.standings_grid.setter('height'))
        scroll_standings.add_widget(self.standings_grid)
        layout.add_widget(scroll_standings)
        
        self.add_widget(layout)
        self.update_ui()
        
    def add_player(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        text_input = TextInput(hint_text='Player name', multiline=False, font_size=dp(16),
                              background_color=(0.15, 0.15, 0.25, 1), foreground_color=(1, 1, 1, 1))
        content.add_widget(text_input)
        
        buttons = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        ok_btn = Button(text='Add', background_normal='', background_color=(0.97, 0.59, 0.12, 1))
        cancel_btn = Button(text='Cancel', background_normal='', background_color=(0.6, 0.1, 0.1, 1))
        buttons.add_widget(ok_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        
        popup = Popup(title='Add Player', content=content, size_hint=(0.8, 0.35))
        
        def add_action(instance):
            name = text_input.text.strip()
            if name and name not in self.players:
                self.players.append(name)
                self.update_ui()
            popup.dismiss()
            
        ok_btn.bind(on_release=add_action)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
        
    def start_tournament(self, instance):
        if len(self.players) < 3:
            popup = Popup(title='Error', content=Label(text='Need at least 3 players!', font_size=dp(16)),
                         size_hint=(0.7, 0.3))
            popup.open()
            return
            
        self.is_started = True
        self.matches = []
        self.current_round = 1
        self.total_rounds = len(self.players) - 1
        self.generate_matches()
        self.update_ui()
        
    def generate_matches(self):
        """Generate Swiss system matches"""
        shuffled = self.players.copy()
        random.shuffle(shuffled)
        
        self.matches = []
        pairings = []
        
        # Simple round-robin
        n = len(shuffled)
        for i in range(n):
            for j in range(i + 1, n):
                pairings.append((shuffled[i], shuffled[j]))
        
        # Assign rounds
        round_size = n // 2
        for round_num in range(self.total_rounds):
            round_matches = []
            for k in range(round_size):
                idx = round_num * round_size + k
                if idx < len(pairings):
                    p1, p2 = pairings[idx]
                    round_matches.append({
                        'player1': p1,
                        'player2': p2,
                        'winner': None,
                        'round': round_num + 1
                    })
            self.matches.extend(round_matches)
            
    def next_round(self, instance):
        if not self.is_started:
            popup = Popup(title='Error', content=Label(text='Start tournament first!', font_size=dp(16)),
                         size_hint=(0.7, 0.3))
            popup.open()
            return
            
        if self.current_round >= self.total_rounds:
            popup = Popup(title='Done', content=Label(text='Tournament complete!', font_size=dp(16)),
                         size_hint=(0.7, 0.3))
            popup.open()
            return
            
        # Determine winners randomly for demo
        for match in self.matches:
            if match['round'] == self.current_round and match['winner'] is None:
                match['winner'] = random.choice([match['player1'], match['player2']])
                
        self.current_round += 1
        self.update_ui()
        
        if self.current_round > self.total_rounds:
            popup = Popup(title='🏆 Tournament Complete!', 
                        content=Label(text=self.get_winner_message(), font_size=dp(16)),
                        size_hint=(0.8, 0.35))
            popup.open()
            
    def get_winner_message(self):
        scores = {}
        for match in self.matches:
            if match['winner']:
                scores[match['winner']] = scores.get(match['winner'], 0) + 1
                
        if scores:
            winner = max(scores, key=scores.get)
            return f'Winner: {winner} with {scores[winner]} points!'
        return 'No winner yet.'
        
    def reset_tournament(self, instance):
        self.players = []
        self.matches = []
        self.current_round = 0
        self.total_rounds = 0
        self.is_started = False
        self.update_ui()
        
    def update_ui(self):
        # Update info
        self.round_label.text = f'Round: {self.current_round}/{self.total_rounds}'
        self.players_label.text = f'Players: {len(self.players)}'
        
        # Update players list
        self.players_grid.clear_widgets()
        for i, player in enumerate(self.players):
            self.players_grid.add_widget(Label(text=f'{i+1}. {player}', font_size=dp(12), color=(0.8, 0.8, 0.8, 1)))
            
        # Update bracket
        self.bracket_grid.clear_widgets()
        if self.matches:
            # Group by round
            rounds = {}
            for match in self.matches:
                r = match['round']
                if r not in rounds:
                    rounds[r] = []
                rounds[r].append(match)
                
            for round_num in sorted(rounds.keys()):
                round_label = Label(text=f'Round {round_num}', font_size=dp(14), 
                                   color=(1, 1, 0.6, 1), bold=True, size_hint_y=None, height=dp(22))
                self.bracket_grid.add_widget(round_label)
                
                for match in rounds[round_num]:
                    if match['round'] == round_num:
                        winner_text = f' ✅ {match["winner"]}' if match['winner'] else ''
                        match_text = f'  {match["player1"]} vs {match["player2"]}{winner_text}'
                        color = (0.2, 0.8, 0.2, 1) if match['winner'] else (0.8, 0.8, 0.8, 1)
                        self.bracket_grid.add_widget(Label(text=match_text, font_size=dp(12), color=color,
                                                          size_hint_y=None, height=dp(18)))
        else:
            self.bracket_grid.add_widget(Label(text='No matches yet', font_size=dp(13), color=(0.5, 0.5, 0.5, 1)))
            
        # Update standings
        self.standings_grid.clear_widgets()
        if self.matches:
            scores = {}
            for match in self.matches:
                if match['winner']:
                    scores[match['winner']] = scores.get(match['winner'], 0) + 1
                    
            # Header
            self.standings_grid.add_widget(Label(text='Rank', font_size=dp(11), color=(1, 1, 0.6, 1), bold=True))
            self.standings_grid.add_widget(Label(text='Player', font_size=dp(11), color=(1, 1, 0.6, 1), bold=True))
            self.standings_grid.add_widget(Label(text='Points', font_size=dp(11), color=(1, 1, 0.6, 1), bold=True))
            self.standings_grid.add_widget(Label(text='Status', font_size=dp(11), color=(1, 1, 0.6, 1), bold=True))
            
            sorted_players = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for i, (player, points) in enumerate(sorted_players):
                self.standings_grid.add_widget(Label(text=str(i+1), font_size=dp(11), color=(0.8, 0.8, 0.8, 1)))
                self.standings_grid.add_widget(Label(text=player, font_size=dp(11), color=(0.8, 0.8, 0.8, 1)))
                self.standings_grid.add_widget(Label(text=str(points), font_size=dp(11), color=(1, 1, 0.6, 1)))
                status = 'Active' if i == 0 else 'Playing'
                self.standings_grid.add_widget(Label(text=status, font_size=dp(11), 
                                                    color=(0.2, 0.8, 0.2, 1) if i == 0 else (0.7, 0.7, 0.7, 1)))
        else:
            self.standings_grid.add_widget(Label(text='No data', font_size=dp(13), color=(0.5, 0.5, 0.5, 1)))