#!/usr/bin/env python3
"""
VFL Virtual Soccer MVP - Data Models
Contains all the dataclasses used in the simulation engine
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import uuid

@dataclass
class Team:
    """
    Represents a football team with all necessary statistics for simulation.
    
    Attributes:
        name (str): Team name
        league (str): League the team belongs to
        country (str): Country of the team
        strength (float): Overall team strength (0-100)
        attack (float): Attack rating (0-100)
        defense (float): Defense rating (0-100)
        form (float): Current form (-5 to +5)
        home_advantage (float): Home advantage bonus (0-10)
    """
    name: str
    league: str
    country: str
    strength: float
    attack: float
    defense: float
    form: float = 0.0
    home_advantage: float = 0.0

@dataclass
class MatchEvent:
    """
    Represents an event that occurs during a match.
    
    Attributes:
        minute (float): Match minute when event occurred
        event_type (str): Type of event (goal, card, corner, etc.)
        team (str): Team involved in the event
        player (str): Player involved (optional)
        description (str): Human-readable description
        details (Dict): Additional event details
    """
    minute: float
    event_type: str
    team: str
    player: Optional[str] = None
    description: str = ""
    details: Dict = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}

@dataclass
class Match:
    """
    Represents a football match between two teams.
    
    Attributes:
        id (str): Unique match identifier
        home_team (Team): Home team
        away_team (Team): Away team
        status (str): Match status (betting_open, betting_locked, live, finished)
        home_score (int): Home team score
        away_score (int): Away team score
        current_minute (float): Current match minute
        duration_minutes (float): Total match duration
        events (List[MatchEvent]): List of match events
        playoff_id (Optional[str]): ID of playoff this match belongs to
        match_number (int): Match number within playoff
        created_at (datetime): When match was created
        started_at (Optional[datetime]): When match started
        finished_at (Optional[datetime]): When match finished
    """
    id: str
    home_team: Team
    away_team: Team
    status: str = 'betting_open'
    home_score: int = 0
    away_score: int = 0
    current_minute: float = 0.0
    duration_minutes: float = 90.0  # 45 + 45 seconds
    events: List[MatchEvent] = None
    playoff_id: Optional[str] = None
    match_number: int = 1
    created_at: datetime = None
    betting_start_time: Optional[datetime] = None
    betting_lock_time: Optional[datetime] = None
    scheduled_start_time: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    home_odds: float = 2.0
    away_odds: float = 2.0
    draw_odds: float = 2.1
    over_2_5_odds: float = 1.8
    under_2_5_odds: float = 1.9

    def __post_init__(self):
        if self.events is None:
            self.events = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.betting_start_time is None:
            self.betting_start_time = datetime.now()

@dataclass
class Playoff:
    """
    Represents a playoff containing multiple matches.
    
    Attributes:
        id (str): Unique playoff identifier
        client_id (str): ID of the client this playoff belongs to
        name (str): Playoff name
        matches (List[Match]): List of matches in this playoff
        status (str): Playoff status (scheduled, live, finished)
        created_at (datetime): When playoff was created
        started_at (Optional[datetime]): When playoff started
        finished_at (Optional[datetime]): When playoff finished
        total_goals (int): Total goals across all matches
        total_events (int): Total events across all matches
    """
    id: str
    client_id: str
    name: str
    matches: List[Match] = None
    status: str = 'betting_open'  # betting_open, betting_locked, live, finished
    created_at: datetime = None
    betting_start_time: Optional[datetime] = None
    betting_lock_time: Optional[datetime] = None
    scheduled_start_time: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    total_goals: int = 0
    total_events: int = 0

    def __post_init__(self):
        if self.matches is None:
            self.matches = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.betting_start_time is None:
            self.betting_start_time = datetime.now()

def team_to_dict(team: Team) -> Dict:
    """Convert Team object to dictionary for JSON serialization"""
    return asdict(team)

def match_to_dict(match: Match) -> Dict:
    """Convert Match object to dictionary for JSON serialization"""
    return {
        'id': match.id,
        'home_team': team_to_dict(match.home_team),
        'away_team': team_to_dict(match.away_team),
        'status': match.status,
        'home_score': match.home_score,
        'away_score': match.away_score,
        'current_minute': match.current_minute,
        'duration_minutes': match.duration_minutes,
        'events': [
            {
                'minute': event.minute,
                'event_type': event.event_type,
                'team': event.team,
                'player': event.player,
                'description': event.description,
                'details': event.details
            } for event in match.events
        ],
        'playoff_id': match.playoff_id,
        'match_number': match.match_number,
        'created_at': match.created_at.isoformat() if match.created_at else None,
        'started_at': match.started_at.isoformat() if match.started_at else None,
        'finished_at': match.finished_at.isoformat() if match.finished_at else None
    }

def playoff_to_dict(playoff: Playoff) -> Dict:
    """Convert Playoff object to dictionary for JSON serialization"""
    return {
        'id': playoff.id,
        'client_id': playoff.client_id,
        'name': playoff.name,
        'status': playoff.status,
        'matches': [match_to_dict(match) for match in playoff.matches],
        'created_at': playoff.created_at.isoformat() if playoff.created_at else None,
        'started_at': playoff.started_at.isoformat() if playoff.started_at else None,
        'finished_at': playoff.finished_at.isoformat() if playoff.finished_at else None,
        'total_goals': playoff.total_goals,
        'total_events': playoff.total_events,
        'match_count': len(playoff.matches)
    }
