# © 2025 AmirAli Kamrani. All rights reserved.

# core/elo.py
import math
import time
import json
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum
from dataclasses import dataclass

class EloSystem(Enum):
    STANDARD = "standard"
    FIDE = "fide"
    USCF = "uscf"
    GLICKO = "glicko"
    GLICKO2 = "glicko2"

@dataclass
class EloRating:
    """ELO rating with metadata"""
    rating: float
    deviation: float  # For Glicko systems
    volatility: float  # For Glicko-2
    games_played: int
    last_update: int
    provisional: bool

class EloCalculator:
    """Advanced ELO rating calculator with multiple systems"""
    
    def __init__(self, system: EloSystem = EloSystem.STANDARD):
        self.system = system
        self.k_factor = 32  # Standard K-factor
        self.initial_rating = 1200
        self.initial_deviation = 350  # For Glicko
        self.initial_volatility = 0.06  # For Glicko-2
        
        # FIDE specific
        self.fide_k_factors = {
            'u18': 40,
            'u30': 20,
            'above30': 10,
            'above40': 5
        }
        
        # USCF specific
        self.uscf_k_factors = {
            'u18': 32,
            'above18': 24
        }
        
        # Rating categories
        self.rating_categories = {
            'beginner': (0, 1199),
            'intermediate': (1200, 1599),
            'advanced': (1600, 1999),
            'expert': (2000, 2399),
            'master': (2400, 2599),
            'grandmaster': (2600, 2799),
            'legendary': (2800, float('inf'))
        }
        
        # Cache
        self._cache = {}
        
    def calculate_elo_change(
        self,
        rating: float,
        opponent_rating: float,
        result: float,  # 1 = win, 0.5 = draw, 0 = loss
        games_played: int = 0,
        age: int = 25,
        k_factor: float = None
    ) -> Dict:
        """Calculate ELO change with multiple factors"""
        
        if self.system == EloSystem.STANDARD:
            return self._calculate_standard(rating, opponent_rating, result, k_factor)
        elif self.system == EloSystem.FIDE:
            return self._calculate_fide(rating, opponent_rating, result, age, k_factor)
        elif self.system == EloSystem.USCF:
            return self._calculate_uscf(rating, opponent_rating, result, age, k_factor)
        elif self.system == EloSystem.GLICKO:
            return self._calculate_glicko(rating, opponent_rating, result, games_played)
        elif self.system == EloSystem.GLICKO2:
            return self._calculate_glicko2(rating, opponent_rating, result)
        else:
            return self._calculate_standard(rating, opponent_rating, result, k_factor)
            
    def _calculate_standard(
        self,
        rating: float,
        opponent_rating: float,
        result: float,
        k_factor: float = None
    ) -> Dict:
        """Standard ELO calculation"""
        
        k = k_factor or self.k_factor
        
        # Expected score
        expected = 1 / (1 + 10 ** ((opponent_rating - rating) / 400))
        
        # Rating change
        change = k * (result - expected)
        
        # Apply provisional rating adjustment for new players
        is_provisional = False
        if rating == self.initial_rating:
            is_provisional = True
            change = change * 1.5  # Higher volatility for new players
            
        new_rating = rating + change
        
        return {
            'old_rating': rating,
            'new_rating': new_rating,
            'change': change,
            'expected': expected,
            'k_factor': k,
            'provisional': is_provisional
        }
        
    def _calculate_fide(
        self,
        rating: float,
        opponent_rating: float,
        result: float,
        age: int = 25,
        k_factor: float = None
    ) -> Dict:
        """FIDE ELO calculation"""
        
        # Determine K-factor based on age and rating
        if k_factor:
            k = k_factor
        else:
            if age < 18:
                k = self.fide_k_factors['u18']
            elif age < 30:
                if rating < 2400:
                    k = self.fide_k_factors['u30']
                else:
                    k = 10
            else:
                if age < 40 and rating < 2400:
                    k = self.fide_k_factors['above30']
                else:
                    k = self.fide_k_factors['above40']
                    
        # Expected score with FIDE formula (same as standard)
        expected = 1 / (1 + 10 ** ((opponent_rating - rating) / 400))
        
        # Rating change
        change = k * (result - expected)
        
        # Rating floor (FIDE minimum)
        new_rating = max(1000, rating + change)
        
        return {
            'old_rating': rating,
            'new_rating': new_rating,
            'change': change,
            'expected': expected,
            'k_factor': k,
            'age_bracket': self._get_fide_age_bracket(age)
        }
        
    def _get_fide_age_bracket(self, age: int) -> str:
        """Get FIDE age bracket"""
        if age < 18:
            return 'u18'
        elif age < 30:
            return 'u30'
        elif age < 40:
            return 'u30'
        else:
            return 'above40'
            
    def _calculate_uscf(
        self,
        rating: float,
        opponent_rating: float,
        result: float,
        age: int = 25,
        k_factor: float = None
    ) -> Dict:
        """USCF ELO calculation"""
        
        # USCF K-factor
        if k_factor:
            k = k_factor
        else:
            if age < 18:
                k = self.uscf_k_factors['u18']
            else:
                k = self.uscf_k_factors['above18']
                
        # USCF uses 400-point system with modifications
        rating_diff = opponent_rating - rating
        
        # USCF expected score (slightly different formula)
        if rating_diff > 400:
            rating_diff = 400
        elif rating_diff < -400:
            rating_diff = -400
            
        expected = 1 / (1 + 10 ** (rating_diff / 400))
        
        # Rating change
        change = k * (result - expected)
        
        # USCF bonus for players below 2000
        if rating < 2000 and result == 1:
            bonus = max(0, (2000 - rating) / 100)
            change += bonus
            
        # USCF floor
        new_rating = max(100, rating + change)
        
        return {
            'old_rating': rating,
            'new_rating': new_rating,
            'change': change,
            'expected': expected,
            'k_factor': k,
            'bonus_applied': rating < 2000 and result == 1
        }
        
    def _calculate_glicko(
        self,
        rating: float,
        opponent_rating: float,
        result: float,
        games_played: int
    ) -> Dict:
        """Glicko rating system"""
        
        # Glicko constants
        c = math.sqrt(0.3 * 350**2)  # Rating volatility
        tau = 0.5  # System constant
        
        # Rating deviation
        rd = self.initial_deviation / math.sqrt(1 + (games_played * 0.06))
        if rd < 30:
            rd = 30
            
        opponent_rd = self.initial_deviation / math.sqrt(1 + (games_played * 0.06))
        
        # Glicko formula
        g = 1 / math.sqrt(1 + 3 * opponent_rd**2 / math.pi**2)
        expected = 1 / (1 + 10 ** (-g * (rating - opponent_rating) / 400))
        
        # Calculate new rating
        d2 = 1 / (g**2 * expected * (1 - expected))
        
        if result == 1:
            rating_change = 1 / (1 / rd**2 + 1 / d2) * g * (1 - expected)
        elif result == 0:
            rating_change = 1 / (1 / rd**2 + 1 / d2) * g * (0 - expected)
        else:  # draw
            rating_change = 1 / (1 / rd**2 + 1 / d2) * g * (0.5 - expected)
            
        new_rating = rating + rating_change
        
        # New rating deviation
        new_rd = math.sqrt(1 / (1 / rd**2 + 1 / d2))
        new_rd = min(new_rd, self.initial_deviation)
        
        return {
            'old_rating': rating,
            'new_rating': new_rating,
            'change': rating_change,
            'expected': expected,
            'rating_deviation': rd,
            'new_deviation': new_rd,
            'system': 'glicko'
        }
        
    def _calculate_glicko2(
        self,
        rating: float,
        opponent_rating: float,
        result: float
    ) -> Dict:
        """Glicko-2 rating system (simplified)"""
        
        # Glicko-2 constants
        tau = 0.5
        epsilon = 0.000001
        
        # Rating deviation and volatility
        rd = 350
        volatility = self.initial_volatility
        
        # Glicko-2 conversion
        mu = (rating - 1500) / 173.7178
        phi = rd / 173.7178
        sigma = volatility
        
        # Opponent parameters
        mu_j = (opponent_rating - 1500) / 173.7178
        phi_j = 350 / 173.7178
        
        # Glicko-2 calculation
        g = 1 / math.sqrt(1 + 3 * phi_j**2 / math.pi**2)
        e = 1 / (1 + math.exp(-g * (mu - mu_j)))
        
        v = 1 / (g**2 * e * (1 - e))
        
        # Rating update
        if result == 1:
            delta = v * g * (1 - e)
        elif result == 0:
            delta = v * g * (0 - e)
        else:  # draw
            delta = v * g * (0.5 - e)
            
        # Update rating
        new_mu = mu + delta
        
        # Update rating deviation
        phi_star = math.sqrt(phi**2 + sigma**2)
        new_phi = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
        
        # Update volatility (simplified)
        new_sigma = sigma * 0.9
        
        # Convert back to standard scale
        new_rating = new_mu * 173.7178 + 1500
        new_deviation = new_phi * 173.7178
        
        return {
            'old_rating': rating,
            'new_rating': new_rating,
            'change': new_rating - rating,
            'expected': e,
            'rating_deviation': rd,
            'new_deviation': new_deviation,
            'volatility': sigma,
            'new_volatility': new_sigma,
            'system': 'glicko2'
        }
        
    def get_rating_category(self, rating: float) -> Dict:
        """Get rating category and title"""
        for category, (min_rating, max_rating) in self.rating_categories.items():
            if min_rating <= rating <= max_rating:
                titles = {
                    'beginner': 'Beginner',
                    'intermediate': 'Intermediate',
                    'advanced': 'Advanced',
                    'expert': 'Expert',
                    'master': 'Master',
                    'grandmaster': 'Grandmaster',
                    'legendary': 'Legendary'
                }
                return {
                    'category': category,
                    'title': titles.get(category, 'Unknown'),
                    'min_rating': min_rating,
                    'max_rating': max_rating,
                    'rating': rating,
                    'progress': (rating - min_rating) / (max_rating - min_rating) * 100 if max_rating != float('inf') else 100
                }
        return {'category': 'unknown', 'title': 'Unknown', 'rating': rating}
        
    def get_expected_score(self, rating: float, opponent_rating: float) -> float:
        """Calculate expected score against opponent"""
        return 1 / (1 + 10 ** ((opponent_rating - rating) / 400))
        
    def get_rating_confidence(self, rating: float, games: int) -> float:
        """Calculate rating confidence based on games played"""
        # More games = higher confidence
        if games < 10:
            return 0.3 + (games / 10) * 0.7
        elif games < 50:
            return 0.7 + ((games - 10) / 40) * 0.25
        else:
            return 0.95 + min((games - 50) / 50, 1) * 0.05
            
    def predict_rating_change(
        self,
        current_rating: float,
        target_rating: float,
        games_needed: int = None
    ) -> Dict:
        """Predict rating changes needed to reach target"""
        
        diff = target_rating - current_rating
        
        if games_needed:
            # Calculate required change per game
            change_per_game = diff / games_needed
            expected_score = change_per_game / self.k_factor + 0.5
            
            # Adjust for 400-point rule
            expected_score = max(0.1, min(0.9, expected_score))
            opponent_rating = current_rating - 400 * math.log10(1 / expected_score - 1)
            
            return {
                'games_needed': games_needed,
                'change_per_game': change_per_game,
                'required_score': expected_score,
                'required_opponent_rating': opponent_rating,
                'current_rating': current_rating,
                'target_rating': target_rating
            }
        else:
            # Calculate games needed with 50% win rate
            change_per_game = self.k_factor * 0.5
            games_needed = abs(diff) / change_per_game
            
            return {
                'games_needed': math.ceil(games_needed),
                'change_per_game': change_per_game,
                'current_rating': current_rating,
                'target_rating': target_rating
            }
            
    def calculate_rating_distribution(self, ratings: List[float]) -> Dict:
        """Calculate statistics for a list of ratings"""
        if not ratings:
            return {}
            
        sorted_ratings = sorted(ratings)
        n = len(sorted_ratings)
        
        return {
            'count': n,
            'mean': sum(sorted_ratings) / n,
            'median': sorted_ratings[n // 2] if n % 2 else (sorted_ratings[n // 2 - 1] + sorted_ratings[n // 2]) / 2,
            'min': sorted_ratings[0],
            'max': sorted_ratings[-1],
            'std_dev': self._calculate_std_dev(sorted_ratings),
            'quartiles': {
                'q1': sorted_ratings[n // 4],
                'q2': sorted_ratings[n // 2] if n % 2 else (sorted_ratings[n // 2 - 1] + sorted_ratings[n // 2]) / 2,
                'q3': sorted_ratings[3 * n // 4]
            },
            'distribution': self._get_rating_distribution(sorted_ratings)
        }
        
    def _calculate_std_dev(self, ratings: List[float]) -> float:
        """Calculate standard deviation"""
        mean = sum(ratings) / len(ratings)
        variance = sum((x - mean) ** 2 for x in ratings) / len(ratings)
        return math.sqrt(variance)
        
    def _get_rating_distribution(self, ratings: List[float]) -> Dict:
        """Get distribution across rating categories"""
        distribution = {}
        for category, (min_rating, max_rating) in self.rating_categories.items():
            count = sum(1 for r in ratings if min_rating <= r <= max_rating)
            distribution[category] = {
                'count': count,
                'percentage': (count / len(ratings)) * 100 if ratings else 0
            }
        return distribution
        
    def get_elo_rating(self, rating_data: Dict) -> EloRating:
        """Get EloRating object from data"""
        return EloRating(
            rating=rating_data.get('rating', self.initial_rating),
            deviation=rating_data.get('deviation', self.initial_deviation),
            volatility=rating_data.get('volatility', self.initial_volatility),
            games_played=rating_data.get('games_played', 0),
            last_update=rating_data.get('last_update', int(time.time())),
            provisional=rating_data.get('provisional', False)
        )
        
    def format_rating(self, rating: float) -> str:
        """Format rating for display"""
        return f"{rating:.0f}"
        
    def get_rating_stats(self, rating: float, games: int) -> Dict:
        """Get comprehensive rating statistics"""
        confidence = self.get_rating_confidence(rating, games)
        category = self.get_rating_category(rating)
        
        return {
            'rating': rating,
            'formatted': self.format_rating(rating),
            'games': games,
            'confidence': confidence,
            'category': category,
            'is_provisional': games < 20,
            'percentile': self._calculate_percentile(rating)
        }
        
    def _calculate_percentile(self, rating: float) -> float:
        """Calculate approximate percentile"""
        # This is a rough estimate based on typical rating distributions
        if rating < 1000:
            return 10 + (rating - 400) / 600 * 30
        elif rating < 1200:
            return 40 + (rating - 1000) / 200 * 25
        elif rating < 1400:
            return 65 + (rating - 1200) / 200 * 20
        elif rating < 1600:
            return 85 + (rating - 1400) / 200 * 10
        elif rating < 1800:
            return 95 + (rating - 1600) / 200 * 4
        elif rating < 2000:
            return 99 + (rating - 1800) / 200 * 0.9
        else:
            return 99.9 + (rating - 2000) / 800 * 0.09
            
    def get_rating_history_stats(self, history: List[Dict]) -> Dict:
        """Analyze rating history"""
        if not history:
            return {}
            
        ratings = [h.get('rating', 0) for h in history]
        
        return {
            'current': ratings[-1] if ratings else 0,
            'highest': max(ratings) if ratings else 0,
            'lowest': min(ratings) if ratings else 0,
            'average': sum(ratings) / len(ratings) if ratings else 0,
            'change': ratings[-1] - ratings[0] if len(ratings) > 1 else 0,
            'best_gain': self._find_best_gain(ratings),
            'worst_loss': self._find_worst_loss(ratings),
            'periods': self._analyze_periods(ratings)
        }
        
    def _find_best_gain(self, ratings: List[float]) -> Dict:
        """Find best rating gain period"""
        if len(ratings) < 2:
            return {'gain': 0, 'start': 0, 'end': 0}
            
        max_gain = 0
        start_idx = 0
        end_idx = 0
        
        for i in range(len(ratings) - 1):
            for j in range(i + 1, min(i + 20, len(ratings))):
                gain = ratings[j] - ratings[i]
                if gain > max_gain:
                    max_gain = gain
                    start_idx = i
                    end_idx = j
                    
        return {
            'gain': max_gain,
            'start_index': start_idx,
            'end_index': end_idx,
            'games': end_idx - start_idx + 1
        }
        
    def _find_worst_loss(self, ratings: List[float]) -> Dict:
        """Find worst rating loss period"""
        if len(ratings) < 2:
            return {'loss': 0, 'start': 0, 'end': 0}
            
        max_loss = 0
        start_idx = 0
        end_idx = 0
        
        for i in range(len(ratings) - 1):
            for j in range(i + 1, min(i + 20, len(ratings))):
                loss = ratings[i] - ratings[j]
                if loss > max_loss:
                    max_loss = loss
                    start_idx = i
                    end_idx = j
                    
        return {
            'loss': max_loss,
            'start_index': start_idx,
            'end_index': end_idx,
            'games': end_idx - start_idx + 1
        }
        
    def _analyze_periods(self, ratings: List[float]) -> Dict:
        """Analyze rating periods"""
        if len(ratings) < 2:
            return {}
            
        # Split into periods of 10 games
        periods = []
        for i in range(0, len(ratings), 10):
            period_ratings = ratings[i:i+10]
            if len(period_ratings) >= 2:
                periods.append({
                    'start': period_ratings[0],
                    'end': period_ratings[-1],
                    'change': period_ratings[-1] - period_ratings[0],
                    'games': len(period_ratings),
                    'average': sum(period_ratings) / len(period_ratings)
                })
                
        # Find best period
        best_period = max(periods, key=lambda p: p['change']) if periods else None
        worst_period = min(periods, key=lambda p: p['change']) if periods else None
        
        return {
            'periods': periods,
            'best_period': best_period,
            'worst_period': worst_period
        }