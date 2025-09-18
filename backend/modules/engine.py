#!/usr/bin/env python3
"""
VFL Virtual Soccer MVP - Simulation Engine
Core simulation logic for virtual football matches
"""

import numpy as np
import time
import threading
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from .models import Team, Match, MatchEvent, Playoff

# Configure logging
logger = logging.getLogger(__name__)

class SimulationEngine:
    """
    Main simulation engine for virtual football matches.
    
    This class handles:
    - Team and league management
    - Match simulation with probabilistic events
    - Playoff generation and management
    - Real-time match updates
    - Client league assignments
    """
    
    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize the simulation engine.
        
        Args:
            random_seed (Optional[int]): Random seed for reproducible results
        """
        # Core simulation data
        self.matches: Dict[str, Match] = {}
        self.playoffs: Dict[str, Playoff] = {}
        self.is_running = False
        self.simulation_thread = None
        
        # Simulation settings - very fast for rapid events
        self.update_interval = 0.1  # 100ms updates - events every 100ms!
        self.time_acceleration = 3.0  # 3x speed for faster gameplay
        
        # Playoff betting timing
        self.playoff_betting_duration = 45.0  # 45 seconds for playoff betting
        self.playoff_betting_lock_duration = 15.0  # 15 seconds locked before start
        
        # Match timing - realistic but compressed for demo
        self.betting_window_duration = 30.0  # 30 seconds for betting
        self.betting_lock_time = 5.0  # Lock betting 5 seconds before match
        self.half_duration = 30.0  # 30 seconds per half (60 seconds total match) - faster!
        self.match_start_interval = 5.0  # 5 seconds between match starts - rapid succession
        
        # Goal frequency control
        self.max_goals_per_period = 2  # Max 2 goals per 5-second period
        self.goal_frequency_window = 5.0  # 5-second window
        self.recent_goals = {}  # Track recent goals per match
        
        # Event observers for real-time notifications
        self.observers: Dict[str, List] = {}
        
        # Connected clients (set by WebSocket manager)
        self.connected_clients: Set[str] = set()
        
        # League and team data
        self.leagues = self._initialize_leagues()
        self.teams = self._initialize_teams()
        
        # Client and daily limits
        self.client_playoffs_today: Dict[str, int] = {}
        self.max_playoffs_per_client_per_day = 50
        self.playoffs_per_playoff = 6  # Each playoff has 6 matches
        
        # Client league assignments and auto-scheduling
        self.client_leagues: Dict[str, List[str]] = {}
        self.auto_generation_enabled = True
        self.last_generation_date = None
        self.scheduler_thread = None
        
        # Set random seed for reproducible results
        if random_seed:
            np.random.seed(random_seed)
            logger.info(f"Random seed set to {random_seed} for reproducible simulations")
    
    def _initialize_leagues(self) -> Dict[str, Dict]:
        """Initialize available football leagues with their characteristics"""
        return {
            "Premier League": {
                "country": "England", "tier": 1, "strength_range": (70, 95),
                "attack_bonus": 5, "defense_bonus": 3, "home_advantage": 8
            },
            "La Liga": {
                "country": "Spain", "tier": 1, "strength_range": (68, 93),
                "attack_bonus": 7, "defense_bonus": 2, "home_advantage": 6
            },
            "Bundesliga": {
                "country": "Germany", "tier": 1, "strength_range": (65, 90),
                "attack_bonus": 6, "defense_bonus": 4, "home_advantage": 7
            },
            "Serie A": {
                "country": "Italy", "tier": 1, "strength_range": (66, 92),
                "attack_bonus": 4, "defense_bonus": 6, "home_advantage": 5
            },
            "Ligue 1": {
                "country": "France", "tier": 1, "strength_range": (60, 88),
                "attack_bonus": 3, "defense_bonus": 3, "home_advantage": 4
            },
            "Championship": {
                "country": "England", "tier": 2, "strength_range": (40, 70),
                "attack_bonus": 2, "defense_bonus": 2, "home_advantage": 3
            },
            "Segunda División": {
                "country": "Spain", "tier": 2, "strength_range": (35, 65),
                "attack_bonus": 1, "defense_bonus": 1, "home_advantage": 2
            },
            "2. Bundesliga": {
                "country": "Germany", "tier": 2, "strength_range": (30, 70),
                "attack_bonus": 1, "defense_bonus": 2, "home_advantage": 3
            }
        }
    
    def _generate_random_team_stats(self) -> Tuple[float, float, float, float, float]:
        """Generate HIGHLY RANDOM team statistics for maximum unpredictability"""
        # WIDER ranges for more variation and unpredictability
        strength = round(np.random.uniform(65, 90), 1)      # 65-90 range (wider spread)
        attack = round(np.random.uniform(60, 95), 1)        # 60-95 range (much wider)  
        defense = round(np.random.uniform(55, 90), 1)       # 55-90 range (much wider)
        form = round(np.random.uniform(-3.0, 3.0), 1)       # -3 to +3 range (wider impact)
        home_advantage = round(np.random.uniform(1, 8), 1)  # 1-8 range (more variation)
        
        # Add some extreme outliers occasionally (5% chance for super stats)
        if np.random.random() < 0.05:
            # Occasionally create a "super team" or "weak team"
            if np.random.random() < 0.5:
                # Super team
                strength = round(np.random.uniform(88, 95), 1)
                attack = round(np.random.uniform(90, 98), 1)
                defense = round(np.random.uniform(85, 95), 1)
            else:
                # Weak team
                strength = round(np.random.uniform(50, 65), 1)
                attack = round(np.random.uniform(45, 70), 1)
                defense = round(np.random.uniform(40, 70), 1)
        
        return strength, attack, defense, form, home_advantage
    
    def _initialize_teams(self) -> Dict[str, Team]:
        """Initialize teams for all leagues with RANDOM stats for unpredictable matches"""
        teams = {}
        
        # Premier League teams - NOW WITH RANDOM STATS!
        premier_league_team_names = [
            "Manchester City", "Arsenal", "Liverpool", "Chelsea", "Manchester United",
            "Tottenham", "Newcastle", "Brighton", "Aston Villa", "West Ham",
            "Crystal Palace", "Fulham", "Brentford", "Wolves", "Everton",
            "Nottingham Forest", "Leeds United", "Leicester City", "Southampton", "Bournemouth"
        ]
        
        for name in premier_league_team_names:
            strength, attack, defense, form, home_adv = self._generate_random_team_stats()
            teams[name] = Team(
                name=name, league="Premier League", country="England",
                strength=strength, attack=attack, defense=defense,
                form=form, home_advantage=home_adv
            )
        
        # La Liga teams - NOW WITH RANDOM STATS!
        la_liga_team_names = [
            "Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla", "Real Sociedad",
            "Villarreal", "Real Betis", "Athletic Bilbao", "Valencia", "Osasuna",
            "Getafe", "Celta Vigo", "Mallorca", "Rayo Vallecano", "Cadiz",
            "Elche", "Almeria", "Valladolid", "Espanyol", "Girona"
        ]
        
        for name in la_liga_team_names:
            strength, attack, defense, form, home_adv = self._generate_random_team_stats()
            teams[name] = Team(
                name=name, league="La Liga", country="Spain",
                strength=strength, attack=attack, defense=defense,
                form=form, home_advantage=home_adv
            )
        
        # Bundesliga teams - NOW WITH RANDOM STATS!
        bundesliga_team_names = [
            "Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen", 
            "Eintracht Frankfurt", "Union Berlin", "Freiburg", "Wolfsburg",
            "Mainz", "Borussia Monchengladbach", "Koln", "Hoffenheim",
            "Werder Bremen", "Augsburg", "Bochum", "Stuttgart", "Hertha Berlin", "Schalke"
        ]
        
        for name in bundesliga_team_names:
            strength, attack, defense, form, home_adv = self._generate_random_team_stats()
            teams[name] = Team(
                name=name, league="Bundesliga", country="Germany",
                strength=strength, attack=attack, defense=defense,
                form=form, home_advantage=home_adv
            )
        
        # Add more leagues (Serie A, Ligue 1, Championship, etc.)
        # ... (similar patterns for other leagues)
        
        logger.info(f"Initialized {len(teams)} teams across {len(self.leagues)} leagues")
        return teams
    
    def load_client_data_from_db(self):
        """Load client league assignments from MySQL database"""
        try:
            from database import get_all_clients
            self.client_leagues = get_all_clients()
            logger.info(f"Loaded {len(self.client_leagues)} clients from database")
            for client_id, leagues in self.client_leagues.items():
                logger.info(f"   {client_id}: {', '.join(leagues)}")
        except Exception as e:
            logger.error(f"❌ Failed to load client data from database: {e}")
            # Fallback to hardcoded data
            self.client_leagues = self._initialize_client_leagues()
            logger.warning("Using fallback hardcoded client data")
    
    def _initialize_client_leagues(self) -> Dict[str, List[str]]:
        """Initialize client league assignments (fallback)"""
        return {
            "client_premier": ["Premier League", "Championship"],
            "client_europe": ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"],
            "client_spain": ["La Liga", "Segunda División"],
            "client_germany": ["Bundesliga", "2. Bundesliga"],
            "client_italy": ["Serie A"],
            "client_france": ["Ligue 1"],
            "client_championship": ["Championship"],
            "client_global": ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1", "Championship", "Segunda División", "2. Bundesliga"]
        }
    
    def create_match(self, home_team: Team, away_team: Team) -> Match:
        """Create a new match between two teams"""
        match_id = f"match_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        # Generate realistic odds based on team strengths (simplified)
        home_odds, away_odds, draw_odds, over_2_5_odds, under_2_5_odds = self._generate_match_odds(home_team, away_team)
        
        match = Match(
            id=match_id,
            home_team=home_team,
            away_team=away_team,
            home_odds=home_odds,
            away_odds=away_odds,
            draw_odds=draw_odds,
            over_2_5_odds=over_2_5_odds,
            under_2_5_odds=under_2_5_odds
        )
        self.matches[match_id] = match
        logger.info(f"Created match {match_id}: {home_team.name} vs {away_team.name} (Odds: {home_odds:.2f}/{draw_odds:.2f}/{away_odds:.2f})")
        return match
    
    def _generate_match_odds(self, home_team: Team, away_team: Team) -> Tuple[float, float, float, float, float]:
        """Generate realistic betting odds for a match"""
        # Create some variation based on team names (simplified odds generation)
        import hashlib
        
        # Use team names to create consistent but varied odds
        team_hash = hashlib.md5(f"{home_team.name}{away_team.name}".encode()).hexdigest()
        seed_value = int(team_hash[:8], 16) % 1000
        
        # Generate odds with some randomness but realistic ranges
        np.random.seed(seed_value)
        
        # Generate odds in range 1.3 to 2.5 as requested
        home_odds = round(1.3 + np.random.random() * 1.2, 1)  # 1.3 to 2.5
        away_odds = round(1.3 + np.random.random() * 1.2, 1)  # 1.3 to 2.5
        draw_odds = round(1.3 + np.random.random() * 1.2, 1)  # 1.3 to 2.5
        
        # Generate Over/Under 2.5 goals odds (typically closer odds)
        over_2_5_odds = round(1.3 + np.random.random() * 1.2, 1)  # 1.3 to 2.5
        under_2_5_odds = round(1.3 + np.random.random() * 1.2, 1)  # 1.3 to 2.5
        
        # Ensure they're not exactly the same (add small variation)
        if home_odds == away_odds:
            away_odds = round(away_odds + 0.1, 1)
        if over_2_5_odds == under_2_5_odds:
            under_2_5_odds = round(under_2_5_odds + 0.1, 1)
            
        # Ensure bounds
        home_odds = max(1.3, min(2.5, home_odds))
        away_odds = max(1.3, min(2.5, away_odds))
        draw_odds = max(1.3, min(2.5, draw_odds))
        over_2_5_odds = max(1.3, min(2.5, over_2_5_odds))
        under_2_5_odds = max(1.3, min(2.5, under_2_5_odds))
        
        return home_odds, away_odds, draw_odds, over_2_5_odds, under_2_5_odds
    
    def start_match(self, match_id: str) -> bool:
        """Start a match simulation"""
        if match_id not in self.matches:
            raise ValueError(f"Match {match_id} not found")
        
        match = self.matches[match_id]
        if match.status not in ['scheduled', 'betting_locked']:
            raise ValueError(f"Match {match_id} is not ready to start (status: {match.status})")
        
        match.status = 'live'
        match.started_at = datetime.now()
        match.current_minute = 0.0
        
        # Add match start event
        start_event = MatchEvent(
            minute=0.0,
            event_type="match_start",
            team="system",
            description=f"Kick-off! {match.home_team.name} vs {match.away_team.name}",
            details={
                "referee": f"Referee {np.random.randint(1, 100)}",
                "stadium": f"Stadium {np.random.randint(1, 50)}",
                "weather": np.random.choice(["Clear", "Cloudy", "Light Rain", "Sunny"])
            }
        )
        match.events.append(start_event)
        
        # Notify observers of match start
        self.notify_observers('match_start', match_id, {
            'match': {
                'home_team': match.home_team.name,
                'away_team': match.away_team.name,
                'home_score': match.home_score,
                'away_score': match.away_score,
                'status': match.status
            }
        })
        
        logger.info(f"Started match {match_id}: {match.home_team.name} vs {match.away_team.name}")
        return True
    
    def stop_match(self, match_id: str) -> bool:
        """Stop a match simulation"""
        if match_id not in self.matches:
            raise ValueError(f"Match {match_id} not found")
        
        match = self.matches[match_id]
        if match.status == 'finished':
            raise ValueError(f"Match {match_id} is already finished")
        
        match.status = 'finished'
        match.finished_at = datetime.now()
        logger.info(f"Finished match {match_id}: {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name}")
        return True
    
    def _can_generate_goal(self, match_id: str) -> bool:
        """Check if a goal can be generated based on frequency limits"""
        current_time = time.time()
        
        if match_id not in self.recent_goals:
            self.recent_goals[match_id] = []
        
        # Remove goals older than the frequency window
        cutoff_time = current_time - self.goal_frequency_window
        self.recent_goals[match_id] = [
            goal_time for goal_time in self.recent_goals[match_id] 
            if goal_time > cutoff_time
        ]
        
        # Check if we're under the limit
        return len(self.recent_goals[match_id]) < self.max_goals_per_period
    
    def _can_generate_goal_with_limits(self, match: Match) -> bool:
        """Enhanced goal generation with match and team limits for more realistic scores"""
        # First check the basic frequency limit
        if not self._can_generate_goal(match.id):
            return False
        
        # Determine if this match should be low-scoring (30% chance)
        match_seed = hash(match.id) % 100
        is_low_scoring_match = match_seed < 30  # 30% of matches are low-scoring
        
        total_goals = match.home_score + match.away_score
        
        # Low-scoring match limits (max 2 total goals)
        if is_low_scoring_match and total_goals >= 2:
            return False
        
        # Regular match limits (max 6 total goals to prevent crazy scores)
        if total_goals >= 6:
            return False
        
        # Individual team goal limits (no team scores more than 2 goals)
        if match.home_score >= 2 or match.away_score >= 2:
            return False
        
        # Add some randomness - occasionally deny goals even when allowed (realistic misses)
        if np.random.random() < 0.3:  # 30% chance to miss even when conditions are met
            return False
        
        return True
    
    def _can_generate_goal_with_limits(self, match: Match) -> bool:
        """Enhanced goal generation with match and team limits for more realistic scores"""
        # First check the basic frequency limit
        if not self._can_generate_goal(match.id):
            return False
        
        # Determine if this match should be low-scoring (30% chance)
        match_seed = hash(match.id) % 100
        is_low_scoring_match = match_seed < 30  # 30% of matches are low-scoring
        
        total_goals = match.home_score + match.away_score
        
        # Low-scoring match limits (max 2 total goals)
        if is_low_scoring_match and total_goals >= 2:
            return False
        
        # Regular match limits (max 6 total goals to prevent crazy scores)
        if total_goals >= 6:
            return False
        
        # Individual team goal limits (no team scores more than 2 goals)
        if match.home_score >= 2 or match.away_score >= 2:
            return False
        
        # Add some randomness - occasionally deny goals even when allowed (realistic misses)
        if np.random.random() < 0.3:  # 30% chance to miss even when conditions are met
            return False
        
        return True
    
    def _track_goal(self, match_id: str):
        """Track a goal for frequency control"""
        current_time = time.time()
        if match_id not in self.recent_goals:
            self.recent_goals[match_id] = []
        self.recent_goals[match_id].append(current_time)
    
    def _calculate_attack_probability(self, attacking_team: Team, defending_team: Team, is_home: bool) -> float:
        """Calculate probability of scoring based on team stats - BALANCED for unpredictable matches"""
        # Base attack probability - increased for 100ms updates
        base_prob = 0.35  # 35% base chance per minute (slightly reduced)
        
        # REDUCED impact of team strength difference (was /100, now /200)
        strength_diff = attacking_team.strength - defending_team.strength
        strength_factor = 1 + (strength_diff / 200)  # Halved impact
        
        # REDUCED impact of attack vs defense ratio
        if defending_team.defense == 0:
            attack_defense_ratio = attacking_team.attack / 1
        else:
            attack_defense_ratio = attacking_team.attack / defending_team.defense
        
        # Reduce the impact by taking square root (makes differences smaller)
        attack_defense_ratio = np.sqrt(attack_defense_ratio)
        
        # REDUCED form factor impact (was /10, now /20)
        form_factor = 1 + (attacking_team.form / 20)  # Halved impact
        
        # REDUCED home advantage impact (was /100, now /200)
        home_factor = 1 + (attacking_team.home_advantage / 200) if is_home else 1  # Halved impact
        
        # ADD RANDOM MATCH MOMENTUM (±20% random variation)
        momentum_factor = 0.8 + (np.random.random() * 0.4)  # Random between 0.8 and 1.2
        
        # ADD UPSET POTENTIAL - occasionally help weaker teams
        # If attacking team is significantly weaker, give them an upset boost
        if strength_diff < -5:  # Attacking team is weaker
            upset_chance = np.random.random()
            if upset_chance < 0.15:  # 15% chance of upset boost
                upset_factor = 1.3 + (np.random.random() * 0.4)  # 1.3x to 1.7x boost
                momentum_factor *= upset_factor
                # Note: This creates David vs Goliath moments!
        
        # Calculate final probability with all factors
        probability = base_prob * strength_factor * attack_defense_ratio * form_factor * home_factor * momentum_factor
        
        # Cap probability between 0.005 and 0.4 (0.5% to 40% per minute for demo)
        # Narrower range makes matches more balanced
        return max(0.005, min(0.4, probability))
    
    def _apply_dynamic_form_changes(self, match: Match):
        """Apply dynamic form changes during matches to increase unpredictability"""
        # Only apply changes occasionally (every ~10 seconds of match time)
        if np.random.random() < 0.01:  # 1% chance per update (every ~10 seconds)
            # Random form boost or penalty for either team
            if np.random.random() < 0.5:
                # Boost home team form (momentum shift)
                old_form = match.home_team.form
                match.home_team.form = min(2.0, match.home_team.form + np.random.uniform(0.1, 0.5))
                if abs(match.home_team.form - old_form) > 0.2:
                    logger.info(f"Match {match.id} - {match.home_team.name} form boost: {old_form:.1f} → {match.home_team.form:.1f}")
            else:
                # Boost away team form (momentum shift)
                old_form = match.away_team.form
                match.away_team.form = min(2.0, match.away_team.form + np.random.uniform(0.1, 0.5))
                if abs(match.away_team.form - old_form) > 0.2:
                    logger.info(f"Match {match.id} - {match.away_team.name} form boost: {old_form:.1f} → {match.away_team.form:.1f}")
        
        # Occasional form penalties (fatigue, pressure)
        if np.random.random() < 0.005:  # 0.5% chance per update
            # Apply fatigue/pressure penalty to a random team
            if np.random.random() < 0.5:
                old_form = match.home_team.form
                match.home_team.form = max(-2.0, match.home_team.form - np.random.uniform(0.1, 0.3))
                if abs(match.home_team.form - old_form) > 0.15:
                    logger.info(f"Match {match.id} - {match.home_team.name} form penalty: {old_form:.1f} → {match.home_team.form:.1f}")
            else:
                old_form = match.away_team.form
                match.away_team.form = max(-2.0, match.away_team.form - np.random.uniform(0.1, 0.3))
                if abs(match.away_team.form - old_form) > 0.15:
                    logger.info(f"Match {match.id} - {match.away_team.name} form penalty: {old_form:.1f} → {match.away_team.form:.1f}")
    
    def _generate_match_event(self, match: Match) -> Optional[MatchEvent]:
        """Generate a random match event"""
        if match.status != 'live':
            return None
        
        # Determine which team is attacking (simplified)
        home_attacking = np.random.random() < 0.5
        
        if home_attacking:
            attacking_team = match.home_team
            defending_team = match.away_team
            team_name = "home"
        else:
            attacking_team = match.away_team
            defending_team = match.home_team
            team_name = "away"
        
        # Calculate attack probability
        attack_prob = self._calculate_attack_probability(
            attacking_team, defending_team, home_attacking
        )
        
        # Check if event occurs
        if np.random.random() < attack_prob:
            # Generate goal with frequency control
            if np.random.random() < 0.5:  # 50% chance of goal when attacking (fast events)
                if self._can_generate_goal_with_limits(match):
                if home_attacking:
                    match.home_score += 1
                else:
                    match.away_score += 1
                
                    # Track this goal for frequency control
                    self._track_goal(match.id)
                    
                return MatchEvent(
                    minute=match.current_minute,
                    event_type="goal",
                    team=team_name,
                        description=f"Goal! {attacking_team.name} scores!",
                        details={"scorer": f"Player {np.random.randint(1, 12)}"}
                )
            else:
                # Generate other events with realistic probabilities
                event_choice = np.random.random()
                if event_choice < 0.4:  # 40% corners
                    event_type = "corner"
                    description = f"Corner kick for {attacking_team.name}"
                elif event_choice < 0.6:  # 20% fouls
                    event_type = "foul"
                    description = f"Foul by {defending_team.name}"
                elif event_choice < 0.75:  # 15% yellow cards
                    event_type = "yellow_card"
                    description = f"Yellow card for {defending_team.name}"
                elif event_choice < 0.85:  # 10% offsides
                    event_type = "offside"
                    description = f"Offside - {attacking_team.name}"
                elif event_choice < 0.95:  # 10% free kicks
                    event_type = "free_kick"
                    description = f"Free kick for {attacking_team.name}"
                else:  # 5% red cards
                    event_type = "red_card"
                    description = f"Red card! {defending_team.name} player sent off!"
                
                return MatchEvent(
                    minute=match.current_minute,
                    event_type=event_type,
                    team=team_name,
                    description=description,
                    details={"player": f"Player {np.random.randint(1, 12)}"}
                )
        
        return None
    
    def _generate_guaranteed_match_events(self, match: Match) -> List[MatchEvent]:
        """Generate guaranteed match events based on current match state"""
        events = []
        current_minute = match.current_minute
        
        # Check if we need to add guaranteed events
        existing_event_types = {event.event_type for event in match.events}
        
        # Match start event (only if we haven't added one yet)
        match_start_exists = any(event.event_type == "match_start" for event in match.events)
        if current_minute > 0 and not match_start_exists:
            events.append(MatchEvent(
                minute=0.0,
                event_type="match_start",
                team="system",
                description=f"Match started: {match.home_team.name} vs {match.away_team.name}",
                details={"referee": f"Referee {np.random.randint(1, 100)}"}
            ))
        
        # First half end (30 seconds)
        if current_minute >= 30.0 and "first_half_end" not in existing_event_types:
            events.append(MatchEvent(
                minute=30.0,
                event_type="first_half_end",
                team="system",
                description="⏰ HALF TIME! First half ends",
                details={"half_time_score": f"{match.home_score}-{match.away_score}"}
            ))
        
        # Second half start (30.1 seconds)
        if current_minute >= 30.1 and "second_half_start" not in existing_event_types:
            events.append(MatchEvent(
                minute=30.1,
                event_type="second_half_start",
                team="system",
                description="🔄 Second half begins!",
                details={"teams_switched_sides": True}
            ))
        
        # Full time whistle (60 seconds or when match ends)
        if current_minute >= 60.0 and "match_end" not in existing_event_types:
            events.append(MatchEvent(
                minute=60.0,
                event_type="match_end",
                team="system",
                description=f"Full time! Final score: {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name}",
                details={
                    "final_score": f"{match.home_score}-{match.away_score}",
                    "total_events": len(match.events) + len(events),
                    "match_duration": current_minute
                }
            ))
        
        return events
    
    def update_match(self, match_id: str) -> bool:
        """Update a single match simulation"""
        if match_id not in self.matches:
            return False
        
        match = self.matches[match_id]
        current_time = datetime.now()
        
        # Debug logging for first few updates
        if hasattr(match, '_debug_count'):
            match._debug_count += 1
        else:
            match._debug_count = 1
            
        if match._debug_count <= 3:
            logger.info(f"DEBUG: Updating match {match_id} #{match._debug_count}: status={match.status}, minute={match.current_minute}")
        
        # Handle betting window phases
        if match.status == 'betting_open':
            if match.betting_lock_time and current_time >= match.betting_lock_time:
                match.status = 'betting_locked'
                self.notify_observers('betting_locked', match_id, {
                    'match': {
                        'home_team': match.home_team.name,
                        'away_team': match.away_team.name,
                        'message': 'Betting is now locked - no more bets accepted'
                    }
                })
                logger.info(f"Match {match_id} - Betting locked")
            return True
        
        if match.status == 'betting_locked':
            if match.scheduled_start_time and current_time >= match.scheduled_start_time:
                return self.start_match(match_id)
            return True
        
        if match.status != 'live':
            return False
        
        # Update match time (60 seconds total = 30 sec first half + 30 sec second half)
        elapsed_seconds = (current_time - match.started_at).total_seconds()
        match.current_minute = elapsed_seconds
        
        # Apply dynamic form changes for unpredictability
        self._apply_dynamic_form_changes(match)
        
        # Generate guaranteed match events first (start, half-time, etc.)
        guaranteed_events = self._generate_guaranteed_match_events(match)
        for guaranteed_event in guaranteed_events:
            match.events.append(guaranteed_event)
            logger.info(f"Match {match_id} - {guaranteed_event.event_type}: {guaranteed_event.description}")
            
            # Notify observers of the event
            self.notify_observers('match_event', match_id, {
                'event': {
                    'minute': guaranteed_event.minute,
                    'event_type': guaranteed_event.event_type,
                    'team': guaranteed_event.team,
                    'player': guaranteed_event.player,
                    'description': guaranteed_event.description,
                    'details': guaranteed_event.details
                },
                'match': {
                    'home_team': match.home_team.name,
                    'away_team': match.away_team.name,
                    'home_score': match.home_score,
                    'away_score': match.away_score,
                    'current_minute': match.current_minute,
                    'status': match.status
                }
            })
            
            # Update playoff data for goals and significant events
            if guaranteed_event.event_type in ['goal', 'match_start', 'first_half_end', 'second_half_start', 'match_end']:
                self._update_playoff_data_for_match(match_id)
        
        # Generate random match events
        random_event = self._generate_match_event(match)
        if random_event:
            match.events.append(random_event)
            logger.info(f"Match {match_id} - {random_event.event_type}: {random_event.description}")
            
            # Notify observers of the event
            self.notify_observers('match_event', match_id, {
                'event': {
                    'minute': random_event.minute,
                    'event_type': random_event.event_type,
                    'team': random_event.team,
                    'player': random_event.player,
                    'description': random_event.description,
                    'details': random_event.details
                },
                'match': {
                    'home_team': match.home_team.name,
                    'away_team': match.away_team.name,
                    'home_score': match.home_score,
                    'away_score': match.away_score,
                    'current_minute': match.current_minute,
                    'status': match.status
                }
            })
            
            # Update playoff data for goals and significant events
            if random_event.event_type in ['goal']:
                self._update_playoff_data_for_match(match_id)
        
        # Check if match should end (60 seconds = 30 + 30 seconds)
        if match.current_minute >= 60.0:
            match.status = 'finished'
            match.finished_at = datetime.now()
            
            # Ensure match end event is added if not already present
            match_end_events = [e for e in match.events if e.event_type == "match_end"]
            if not match_end_events:
                final_event = MatchEvent(
                    minute=match.current_minute,
                    event_type="match_end",
                    team="system",
                    description=f"Full time! Final score: {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name}",
                    details={
                        "final_score": f"{match.home_score}-{match.away_score}",
                        "total_events": len(match.events) + 1,
                        "match_duration": match.current_minute
                    }
                )
                match.events.append(final_event)
            
            # Notify observers of match end
            self.notify_observers('match_end', match_id, {
                'match': {
                    'home_team': match.home_team.name,
                    'away_team': match.away_team.name,
                    'home_score': match.home_score,
                    'away_score': match.away_score,
                    'status': match.status,
                    'final_minute': match.current_minute,
                    'total_events': len(match.events)
                }
            })
            
            logger.info(f"Match {match_id} finished: {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name} (Total events: {len(match.events)})")
            
            # Auto-create fresh playoff when this match finishes to keep content flowing
            self._maybe_create_fresh_playoff_for_client(match)
        
        return True
    
    def _maybe_create_fresh_playoff_for_client(self, finished_match):
        """Maintain exactly 2 active playoffs per client"""
        try:
            # Find which client owns this match through playoff
            client_id = None
            finished_playoff_id = finished_match.playoff_id
            
            if finished_playoff_id and finished_playoff_id in self.playoffs:
                client_id = self.playoffs[finished_playoff_id].client_id
            
            if not client_id:
                return
            
            # Check if client has connected clients (don't create if no one is watching)
            if client_id not in self.connected_clients:
                return
            
            # Check if the playoff this match belongs to is now finished
            self._check_and_finish_playoff(finished_playoff_id)
            
            # Maintain exactly 2 active playoffs per client
            self._maintain_client_playoff_count(client_id)
            
        except Exception as e:
            logger.error(f"Error managing playoff lifecycle for client: {e}")
    
    def _check_and_finish_playoff(self, playoff_id: str):
        """Check if a playoff is finished and mark it as such"""
        if not playoff_id or playoff_id not in self.playoffs:
            return
            
        playoff = self.playoffs[playoff_id]
        
        # Check if all matches in the playoff are finished
        all_finished = all(match.status == 'finished' for match in playoff.matches)
        
        if all_finished and playoff.status != 'finished':
            playoff.status = 'finished'
            playoff.finished_at = datetime.now()
            logger.info(f"Playoff {playoff_id} - '{playoff.name}' finished (all matches completed)")
            
            # Notify observers of playoff completion
            self.notify_observers('playoff_finished', playoff_id, {
                'playoff': {
                    'id': playoff_id,
                    'name': playoff.name,
                    'client_id': playoff.client_id,
                    'total_matches': len(playoff.matches),
                    'total_goals': sum(m.home_score + m.away_score for m in playoff.matches),
                    'total_events': sum(len(m.events) for m in playoff.matches)
                }
            })
            
            # CRITICAL: Immediately create a new playoff for this client
            logger.info(f"Playoff {playoff_id} finished - immediately creating new playoff for {playoff.client_id}")
            self._maintain_client_playoff_count(playoff.client_id)
    
    def _maintain_client_playoff_count(self, client_id: str):
        """Ensure each client has exactly 1 active playoff running"""
        try:
            client_playoffs = self.get_playoffs_by_client(client_id)
            active_playoffs = [p for p in client_playoffs if p.status in ['betting_open', 'betting_locked', 'live']]
            active_count = len(active_playoffs)
            
            logger.info(f"Client {client_id} has {active_count} active playoffs (target: 1)")
            
            # Create playoffs to reach exactly 1 active one
            while active_count < 1:
                logger.info(f"Creating new playoff for {client_id} (currently has {active_count}/1 active)")
                
                # Create new playoff
                fresh_playoff = self.create_playoff(client_id, f"Auto Playoff {int(time.time())}")
                
                # Start betting immediately
                self.start_playoff(fresh_playoff.id)
                
                active_count += 1
                logger.info(f"Created and started playoff {fresh_playoff.id} for {client_id} ({active_count}/1 active)")
            
            if active_count > 1:
                logger.info(f"Client {client_id} has {active_count} active playoffs (more than target of 1)")
            
        except Exception as e:
            logger.error(f"Error maintaining playoff count for {client_id}: {e}")
    
    def start_simulation_loop(self):
        """Start the background simulation loop"""
        if self.is_running:
            logger.warning("Simulation loop is already running")
            return
        
        self.is_running = True
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
        logger.info("Simulation loop started")
    
    def stop_simulation_loop(self):
        """Stop the background simulation loop"""
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1)
        logger.info("Simulation loop stopped")
    
    def _simulation_loop(self):
        """Background simulation loop"""
        loop_count = 0
        while self.is_running:
            try:
                loop_count += 1
                # Only update matches for connected clients
                active_match_ids = self._get_active_match_ids()
                
                # Debug logging every 10 loops (1 second)
                if loop_count % 10 == 0:
                    logger.info(f"Simulation loop #{loop_count}: {len(self.connected_clients)} clients, {len(active_match_ids)} active matches")
                    
                    # Check for finished playoffs and create new ones
                    for client_id in self.connected_clients:
                        client_playoffs = self.get_playoffs_by_client(client_id)
                        for playoff in client_playoffs:
                            if playoff.status != 'finished':
                                self._check_and_finish_playoff(playoff.id)
                    
                    # Show match statuses for debugging
                    for i, match_id in enumerate(active_match_ids[:2]):  # Show first 2 matches
                        if match_id in self.matches:
                            match = self.matches[match_id]
                            logger.info(f"  Match {i+1}: {match.status} - {match.current_minute:.1f}min - {match.home_team.name} vs {match.away_team.name}")
                    
                    # Show playoff statuses
                    for playoff in list(self.playoffs.values())[:1]:  # Show first playoff
                        if playoff.client_id in self.connected_clients:
                            logger.info(f"  Playoff: {playoff.status} - {playoff.name}")
                
                for match_id in active_match_ids:
                    self.update_match(match_id)
                
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
                time.sleep(self.update_interval)
    
    def _get_active_match_ids(self) -> List[str]:
        """Get match IDs for playoffs with connected clients"""
        if not self.connected_clients:
            return []
        
        active_matches = []
        for playoff in self.playoffs.values():
            if playoff.client_id in self.connected_clients:
                # Update playoff phases first
                self._update_playoff_phases(playoff)
                
                # Then get active matches
                for match in playoff.matches:
                    active_matches.append(match.id)
        
        return active_matches
    
    def _update_playoff_phases(self, playoff: Playoff):
        """Update playoff betting phases"""
        current_time = datetime.now()
        
        # Handle playoff betting phase transitions
        if playoff.status == 'betting_open':
            if playoff.betting_lock_time and current_time >= playoff.betting_lock_time:
                playoff.status = 'betting_locked'
                logger.info(f"Playoff {playoff.id} - Betting locked for '{playoff.name}'")
                
                # Notify observers of betting lock
                self.notify_observers('playoff_betting_locked', playoff.id, {
                    'playoff': {
                        'id': playoff.id,
                        'name': playoff.name,
                        'status': playoff.status,
                        'message': f"Betting locked for {playoff.name}! Matches starting soon..."
                    }
                })
                
        elif playoff.status == 'betting_locked':
            if playoff.scheduled_start_time and current_time >= playoff.scheduled_start_time:
                playoff.status = 'live'
                playoff.started_at = current_time
                logger.info(f"Playoff {playoff.id} - Started '{playoff.name}'")
                
                # Transition matches from scheduled to betting_open
                for match in playoff.matches:
                    if match.status == 'scheduled' and match.betting_start_time and current_time >= match.betting_start_time:
                        match.status = 'betting_open'
                        logger.info(f"Match {match.id} - Betting opened")
                        
                        # Notify observers of betting opened
                        self.notify_observers('betting_opened', match.id, {
                            'match': {
                                'home_team': match.home_team.name,
                                'away_team': match.away_team.name,
                                'message': 'Betting is now open - place your bets!'
                            }
                        })
        
        # IMPORTANT: Handle live playoffs - ensure matches transition properly even if playoff was already live
        elif playoff.status == 'live':
            # For live playoffs, continuously check if matches should transition
            for match in playoff.matches:
                # Force immediate transition for live playoffs - matches should start quickly
                if match.status == 'scheduled':
                    if match.betting_start_time and current_time >= match.betting_start_time:
                        match.status = 'betting_open'
                        logger.info(f"Match {match.id} - Betting opened (live playoff)")
                        
                        # Notify observers of betting opened
                        self.notify_observers('betting_opened', match.id, {
                            'match': {
                                'home_team': match.home_team.name,
                                'away_team': match.away_team.name,
                                'message': 'Betting is now open - place your bets!'
                            }
                        })
                    elif not match.betting_start_time:
                        # No betting time set - force immediate betting
                        match.betting_start_time = current_time
                        match.betting_lock_time = current_time + timedelta(seconds=5)
                        match.scheduled_start_time = current_time + timedelta(seconds=10)
                        match.status = 'betting_open'
                        logger.info(f"Match {match.id} - FORCED betting opened (no timing set)")
                        
                        # Notify observers of forced betting opened
                        self.notify_observers('betting_opened', match.id, {
                            'match': {
                                'home_team': match.home_team.name,
                                'away_team': match.away_team.name,
                                'message': 'Betting is now open - place your bets!'
                            }
                        })
                
                # Transition from betting to live
                elif match.status == 'betting_open' and match.scheduled_start_time and current_time >= match.scheduled_start_time:
                    match.status = 'live'
                    match.started_at = current_time
                    match.current_minute = 0.0
                    logger.info(f"Match {match.id} - Started live match: {match.home_team.name} vs {match.away_team.name}")
                
                # Force immediate start for very old scheduled matches
                elif match.status == 'scheduled' and (not match.betting_start_time or (current_time - match.betting_start_time).total_seconds() > 300):
                    # Match has been scheduled for over 5 minutes - force start immediately
                    match.status = 'live'
                    match.started_at = current_time
                    match.current_minute = 0.0
                    logger.info(f"Match {match.id} - FORCE STARTED (was stuck in scheduled): {match.home_team.name} vs {match.away_team.name}")
    
    def set_connected_clients(self, client_ids: Set[str]):
        """Update the set of connected clients"""
        self.connected_clients = client_ids
        logger.info(f"Simulation engine updated: {len(client_ids)} connected clients")
    
    def add_connected_client(self, client_id: str):
        """Add a connected client"""
        self.connected_clients.add(client_id)
        logger.info(f"Client {client_id} connected - simulation engine updated")
    
    def remove_connected_client(self, client_id: str):
        """Remove a connected client"""
        self.connected_clients.discard(client_id)
        logger.info(f"Client {client_id} disconnected - simulation engine updated")
    
    # Playoff management methods
    def create_playoff(self, client_id: str, name: str, same_league: bool = True, league: str = None) -> Playoff:
        """Create a new playoff for a client"""
        # Check daily limits
        if self.get_client_playoff_count_today(client_id) >= self.max_playoffs_per_client_per_day:
            raise ValueError(f"Client {client_id} has reached daily playoff limit")
        
        playoff_id = f"playoff_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        # Generate matches
        matches = []
        for i in range(self.playoffs_per_playoff):
            if same_league and league:
                home_team, away_team = self._get_teams_from_league(league)
            else:
                home_team, away_team = self._get_random_teams()
            
            match = self.create_match(home_team, away_team)
            match.playoff_id = playoff_id
            match.match_number = i + 1
            matches.append(match)
        
        # Create playoff
        playoff = Playoff(
            id=playoff_id,
            client_id=client_id,
            name=name,
            matches=matches
        )
        
        self.playoffs[playoff_id] = playoff
        
        # Update daily count
        today = datetime.now().date().isoformat()
        client_key = f"{client_id}_{today}"
        self.client_playoffs_today[client_key] = self.client_playoffs_today.get(client_key, 0) + 1
        
        logger.info(f"Created playoff {playoff_id} for {client_id} with {len(matches)} matches")
        return playoff
    
    def _get_teams_from_league(self, league: str) -> Tuple[Team, Team]:
        """Get two random teams from the same league"""
        league_teams = [team for team in self.teams.values() if team.league == league]
        
        if len(league_teams) < 2:
            raise ValueError(f"Not enough teams available for playoff: Need 2, have {len(league_teams)}")
        
        selected = np.random.choice(league_teams, 2, replace=False)
        return selected[0], selected[1]
    
    def _get_random_teams(self) -> Tuple[Team, Team]:
        """Get two random teams from any league"""
        teams = list(self.teams.values())
        selected = np.random.choice(teams, 2, replace=False)
        return selected[0], selected[1]
    
    def start_playoff(self, playoff_id: str) -> bool:
        """Start a playoff with betting phase first"""
        if playoff_id not in self.playoffs:
            raise ValueError(f"Playoff {playoff_id} not found")
        
        playoff = self.playoffs[playoff_id]
        if playoff.status not in ['scheduled', 'betting_open']:
            raise ValueError(f"Playoff {playoff_id} is not in scheduled status")
        
        # Set playoff betting timing
        current_time = datetime.now()
        playoff.betting_start_time = current_time
        playoff.betting_lock_time = current_time + timedelta(seconds=self.playoff_betting_duration)
        playoff.scheduled_start_time = current_time + timedelta(seconds=self.playoff_betting_duration + self.playoff_betting_lock_duration)
        
        # Set playoff to betting phase
        playoff.status = 'betting_open'
        
        # Prepare matches but don't start them yet (they start after playoff betting)
        playoff_match_start = playoff.scheduled_start_time
        for i, match in enumerate(playoff.matches):
            # Each match starts after playoff betting ends, with staggered timing
            match_start_offset = i * self.match_start_interval
            
            # Set match betting and start timings (after playoff betting completes)
            match.betting_start_time = playoff_match_start + timedelta(seconds=match_start_offset)
            match.betting_lock_time = match.betting_start_time + timedelta(seconds=self.betting_window_duration - self.betting_lock_time)
            match.scheduled_start_time = match.betting_start_time + timedelta(seconds=self.betting_window_duration)
            
            # Matches start in scheduled state, will transition to betting_open later
            match.status = 'scheduled'
            
            logger.info(f"Scheduled match {match.id}: Betting opens at {match.betting_start_time.strftime('%H:%M:%S')}, "
                       f"locks at {match.betting_lock_time.strftime('%H:%M:%S')}, "
                       f"starts at {match.scheduled_start_time.strftime('%H:%M:%S')}")
        
        playoff.status = 'live'
        playoff.started_at = datetime.now()
        logger.info(f"Started playoff {playoff_id} with {len(playoff.matches)} matches (staggered starts)")
        
        return True
    
    def stop_playoff(self, playoff_id: str) -> bool:
        """Stop all matches in a playoff"""
        if playoff_id not in self.playoffs:
            raise ValueError(f"Playoff {playoff_id} not found")
        
        playoff = self.playoffs[playoff_id]
        playoff.status = 'finished'
        playoff.finished_at = datetime.now()
        
        # Stop all matches and calculate totals
        total_goals = 0
        total_events = 0
        
        for match in playoff.matches:
            if match.status == 'live':
                self.stop_match(match.id)
            total_goals += match.home_score + match.away_score
            total_events += len(match.events)
        
        playoff.total_goals = total_goals
        playoff.total_events = total_events
        
        logger.info(f"Finished playoff {playoff_id}: {total_goals} goals, {total_events} events")
        return True
    
    def get_playoff(self, playoff_id: str) -> Optional[Playoff]:
        """Get a specific playoff"""
        return self.playoffs.get(playoff_id)
    
    def calculate_playoff_totals(self, playoff: Playoff) -> tuple:
        """Calculate real-time totals for a playoff"""
        total_goals = 0
        total_events = 0
        
        for match in playoff.matches:
            total_goals += match.home_score + match.away_score
            total_events += len(match.events)
        
        return total_goals, total_events
    
    def _update_playoff_data_for_match(self, match_id: str):
        """Update playoff data when a match event occurs and notify observers"""
        if match_id not in self.matches:
            return
        
        match = self.matches[match_id]
        if not match.playoff_id or match.playoff_id not in self.playoffs:
            return
        
        playoff = self.playoffs[match.playoff_id]
        
        # Calculate updated playoff totals
        total_goals, total_events = self.calculate_playoff_totals(playoff)
        
        # Create playoff update data
        playoff_data = {
            'playoff_id': playoff.id,
            'name': playoff.name,
            'client_id': playoff.client_id,
            'status': playoff.status,
            'total_goals': total_goals,
            'total_events': total_events,
            'match_count': len(playoff.matches),
            'live_matches': len([m for m in playoff.matches if m.status == 'live']),
            'updated_match_id': match_id,
            'updated_match': {
                'home_team': match.home_team.name,
                'away_team': match.away_team.name,
                'home_score': match.home_score,
                'away_score': match.away_score,
                'status': match.status,
                'current_minute': match.current_minute
            }
        }
        
        # Notify observers of playoff update
        self.notify_observers('playoff_updated', playoff.id, playoff_data)
        
        logger.info(f"Playoff {playoff.id} updated: {total_goals} goals, {total_events} events")
    
    def add_event_observer(self, event_type: str, callback):
        """Add an observer for a specific event type"""
        if event_type not in self.observers:
            self.observers[event_type] = []
        self.observers[event_type].append(callback)
    
    def notify_observers(self, event_type: str, *args, **kwargs):
        """Notify all observers of an event"""
        if event_type in self.observers:
            for callback in self.observers[event_type]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in event observer callback: {e}")
    
    def get_playoffs_by_client(self, client_id: str) -> List[Playoff]:
        """Get all playoffs for a specific client"""
        return [playoff for playoff in self.playoffs.values() if playoff.client_id == client_id]
    
    def get_client_playoff_count_today(self, client_id: str) -> int:
        """Get today's playoff count for a client"""
        today = datetime.now().date().isoformat()
        client_key = f"{client_id}_{today}"
        return self.client_playoffs_today.get(client_key, 0)
    
    def get_remaining_playoffs_today(self, client_id: str) -> int:
        """Get remaining playoffs for a client today"""
        current = self.get_client_playoff_count_today(client_id)
        return max(0, self.max_playoffs_per_client_per_day - current)
    
    def generate_daily_playoffs_for_client(self, client_id: str) -> List[Playoff]:
        """Generate all daily playoffs for a specific client based on their assigned leagues"""
        if client_id not in self.client_leagues:
            logger.warning(f"Client {client_id} not found in league assignments")
            return []
        
        assigned_leagues = self.client_leagues[client_id]
        generated_playoffs = []
        
        # Calculate playoffs per league (distribute 50 playoffs across assigned leagues)
        playoffs_per_league = self.max_playoffs_per_client_per_day // len(assigned_leagues)
        remaining_playoffs = self.max_playoffs_per_client_per_day % len(assigned_leagues)
        
        logger.info(f"Generating {self.max_playoffs_per_client_per_day} playoffs for {client_id} across {len(assigned_leagues)} leagues")
        
        for i, league in enumerate(assigned_leagues):
            # Add one extra playoff to some leagues if there's a remainder
            num_playoffs = playoffs_per_league + (1 if i < remaining_playoffs else 0)
            
            logger.info(f"Generating {num_playoffs} playoffs for {client_id} in {league}")
            
            for j in range(num_playoffs):
                try:
                    playoff = self.create_playoff(
                        client_id=client_id,
                        name=f"{league} Playoff {j+1} - {datetime.now().strftime('%Y-%m-%d')}",
                        same_league=True,
                        league=league
                    )
                    generated_playoffs.append(playoff)
                    
                except ValueError as e:
                    logger.error(f"Failed to create playoff {j+1} for {client_id} in {league}: {e}")
                    break
        
        logger.info(f"Successfully generated {len(generated_playoffs)} playoffs for {client_id}")
        return generated_playoffs
    
    def generate_daily_playoffs_for_all_clients(self) -> Dict[str, List[Playoff]]:
        """Generate daily playoffs for all clients based on their assigned leagues"""
        today = datetime.now().date()
        
        # Check if we've already generated for today
        if self.last_generation_date == today:
            logger.info("Playoffs already generated for today")
            return {}
        
        logger.info(f"Starting daily playoff generation for {len(self.client_leagues)} clients")
        
        all_generated = {}
        
        for client_id in self.client_leagues.keys():
            try:
                playoffs = self.generate_daily_playoffs_for_client(client_id)
                all_generated[client_id] = playoffs
                
                # Auto-start some playoffs (e.g., first 10 per client)
                for playoff in playoffs[:10]:
                    try:
                        self.start_playoff(playoff.id)
                        logger.info(f"Auto-started playoff {playoff.id} for {client_id}")
                    except Exception as e:
                        logger.error(f"Failed to start playoff {playoff.id}: {e}")
                        
            except Exception as e:
                logger.error(f"Failed to generate playoffs for {client_id}: {e}")
        
        self.last_generation_date = today
        logger.info(f"✅ Daily generation completed. Generated playoffs for {len(all_generated)} clients")
        
        return all_generated
    
    def start_auto_scheduler(self):
        """Start the automatic scheduler for daily generation"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.info("Scheduler already running")
            return
        
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("🕐 Auto-scheduler started")
    
    def stop_auto_scheduler(self):
        """Stop the automatic scheduler"""
        self.auto_generation_enabled = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1)
        logger.info("🛑 Auto-scheduler stopped")
    
    def _scheduler_loop(self):
        """Background scheduler loop that runs every minute to check for midnight"""
        while self.auto_generation_enabled:
            try:
                now = datetime.now()
                
                # Check if it's midnight (00:00)
                if now.hour == 0 and now.minute == 0:
                    logger.info("🕛 Midnight detected - starting daily generation")
                    self.generate_daily_playoffs_for_all_clients()
                
                # Sleep for 1 minute
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Continue even if there's an error
