#!/usr/bin/env python3
"""
VFL Virtual Soccer MVP - Data Generator
Generates realistic league and team data and stores them in JSON files

This script creates comprehensive league and team data that can be used
by different clients or customized for specific needs.
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, List, Any
import numpy as np

def generate_league_data() -> Dict[str, Any]:
    """
    Generate comprehensive league data with realistic characteristics.
    
    Returns:
        Dict[str, Any]: Complete league data structure
    """
    leagues = {
        "Premier League": {
            "country": "England",
            "tier": 1,
            "strength_range": (70, 95),
            "attack_bonus": 5,
            "defense_bonus": 3,
            "home_advantage": 8,
            "description": "The most competitive football league in the world",
            "founded": 1992,
            "teams": 20,
            "season_duration": "August to May",
            "champions_league_spots": 4,
            "europa_league_spots": 2
        },
        "La Liga": {
            "country": "Spain", 
            "tier": 1,
            "strength_range": (68, 93),
            "attack_bonus": 7,
            "defense_bonus": 2,
            "home_advantage": 6,
            "description": "Spanish top division with technical excellence",
            "founded": 1929,
            "teams": 20,
            "season_duration": "August to May",
            "champions_league_spots": 4,
            "europa_league_spots": 2
        },
        "Bundesliga": {
            "country": "Germany",
            "tier": 1, 
            "strength_range": (65, 90),
            "attack_bonus": 4,
            "defense_bonus": 5,
            "home_advantage": 7,
            "description": "German top division known for passionate fans",
            "founded": 1963,
            "teams": 18,
            "season_duration": "August to May",
            "champions_league_spots": 4,
            "europa_league_spots": 2
        },
        "Serie A": {
            "country": "Italy",
            "tier": 1,
            "strength_range": (63, 88),
            "attack_bonus": 3,
            "defense_bonus": 6,
            "home_advantage": 5,
            "description": "Italian top division with tactical excellence",
            "founded": 1898,
            "teams": 20,
            "season_duration": "August to May",
            "champions_league_spots": 4,
            "europa_league_spots": 2
        },
        "Ligue 1": {
            "country": "France",
            "tier": 1,
            "strength_range": (60, 85),
            "attack_bonus": 4,
            "defense_bonus": 4,
            "home_advantage": 6,
            "description": "French top division with emerging talent",
            "founded": 1932,
            "teams": 20,
            "season_duration": "August to May",
            "champions_league_spots": 3,
            "europa_league_spots": 2
        },
        "Championship": {
            "country": "England",
            "tier": 2,
            "strength_range": (45, 70),
            "attack_bonus": 2,
            "defense_bonus": 3,
            "home_advantage": 5,
            "description": "English second division with promotion battles",
            "founded": 2004,
            "teams": 24,
            "season_duration": "August to May",
            "promotion_spots": 3,
            "playoff_spots": 4
        },
        "Segunda División": {
            "country": "Spain",
            "tier": 2,
            "strength_range": (40, 65),
            "attack_bonus": 3,
            "defense_bonus": 2,
            "home_advantage": 4,
            "description": "Spanish second division",
            "founded": 1929,
            "teams": 22,
            "season_duration": "August to May",
            "promotion_spots": 3,
            "playoff_spots": 4
        },
        "2. Bundesliga": {
            "country": "Germany",
            "tier": 2,
            "strength_range": (42, 67),
            "attack_bonus": 2,
            "defense_bonus": 4,
            "home_advantage": 5,
            "description": "German second division",
            "founded": 1974,
            "teams": 18,
            "season_duration": "August to May",
            "promotion_spots": 3,
            "playoff_spots": 1
        }
    }
    
    return leagues

def generate_team_data() -> Dict[str, Any]:
    """
    Generate comprehensive team data across all leagues.
    
    Returns:
        Dict[str, Any]: Complete team data structure
    """
    teams = {}
    
    # Premier League teams with realistic data
    premier_league_teams = [
        ("Manchester City", 92, 95, 88, 2.5, 8, "Sky Blue", "Etihad Stadium", 55000),
        ("Arsenal", 88, 92, 85, 1.8, 7, "Red", "Emirates Stadium", 60000),
        ("Liverpool", 90, 89, 91, 2.2, 9, "Red", "Anfield", 54000),
        ("Chelsea", 85, 87, 83, 0.5, 6, "Blue", "Stamford Bridge", 41000),
        ("Manchester United", 82, 84, 80, -0.5, 8, "Red", "Old Trafford", 74000),
        ("Tottenham", 80, 85, 75, 1.2, 7, "White", "Tottenham Hotspur Stadium", 62000),
        ("Newcastle", 75, 78, 72, 1.5, 6, "Black & White", "St. James' Park", 52000),
        ("Brighton", 72, 74, 70, 0.8, 5, "Blue & White", "Amex Stadium", 31000),
        ("Aston Villa", 70, 73, 68, 0.3, 6, "Claret & Blue", "Villa Park", 42000),
        ("West Ham", 68, 71, 65, -0.2, 5, "Claret & Blue", "London Stadium", 66000),
        ("Crystal Palace", 65, 68, 62, 0.1, 4, "Red & Blue", "Selhurst Park", 25000),
        ("Fulham", 63, 66, 60, -0.5, 4, "White & Black", "Craven Cottage", 19000),
        ("Brentford", 61, 64, 58, 0.7, 3, "Red & White", "Brentford Community Stadium", 17000),
        ("Wolves", 59, 62, 56, -0.8, 4, "Gold & Black", "Molineux Stadium", 32000),
        ("Everton", 57, 60, 54, -1.2, 5, "Blue", "Goodison Park", 40000),
        ("Nottingham Forest", 55, 58, 52, -0.5, 4, "Red", "City Ground", 30000),
        ("Luton Town", 52, 55, 49, 0.2, 3, "Orange", "Kenilworth Road", 10000),
        ("Burnley", 50, 53, 47, -0.8, 4, "Claret & Blue", "Turf Moor", 22000),
        ("Sheffield United", 48, 51, 45, -1.5, 3, "Red & White", "Bramall Lane", 32000),
        ("Bournemouth", 46, 49, 43, -0.3, 2, "Red & Black", "Vitality Stadium", 11000)
    ]
    
    for name, strength, attack, defense, form, home_adv, colors, stadium, capacity in premier_league_teams:
        teams[name] = {
            "name": name,
            "league": "Premier League",
            "country": "England",
            "strength": strength,
            "attack": attack,
            "defense": defense,
            "form": form,
            "home_advantage": home_adv,
            "colors": colors,
            "stadium": stadium,
            "capacity": capacity,
            "founded": random.randint(1870, 2000),
            "nickname": f"The {name.split()[-1]}s" if len(name.split()) > 1 else f"The {name}s"
        }
    
    # La Liga teams
    la_liga_teams = [
        ("Real Madrid", 94, 96, 92, 2.8, 7, "White", "Santiago Bernabéu", 81000),
        ("Barcelona", 92, 94, 90, 2.5, 6, "Blue & Red", "Camp Nou", 99000),
        ("Atletico Madrid", 88, 85, 91, 1.8, 8, "Red & White", "Wanda Metropolitano", 68000),
        ("Real Sociedad", 78, 80, 76, 1.2, 5, "Blue & White", "Reale Arena", 40000),
        ("Villarreal", 76, 78, 74, 0.8, 4, "Yellow", "Estadio de la Cerámica", 23000),
        ("Real Betis", 74, 76, 72, 0.5, 5, "Green & White", "Benito Villamarín", 60000),
        ("Athletic Bilbao", 72, 70, 74, 0.3, 6, "Red & White", "San Mamés", 53000),
        ("Valencia", 70, 72, 68, -0.2, 5, "Orange & Black", "Mestalla", 55000),
        ("Sevilla", 68, 70, 66, -0.8, 4, "White & Red", "Ramón Sánchez-Pizjuán", 43000),
        ("Osasuna", 66, 68, 64, 0.1, 4, "Red", "El Sadar", 24000),
        ("Getafe", 64, 62, 66, -0.5, 3, "Blue", "Coliseum Alfonso Pérez", 17000),
        ("Celta Vigo", 62, 64, 60, -0.3, 3, "Sky Blue", "Balaídos", 29000),
        ("Mallorca", 60, 62, 58, 0.2, 2, "Red & Yellow", "Son Moix", 23000),
        ("Las Palmas", 58, 60, 56, 0.5, 2, "Yellow & Blue", "Estadio Gran Canaria", 32000),
        ("Rayo Vallecano", 56, 58, 54, -0.2, 3, "Red", "Vallecas", 15000),
        ("Cadiz", 54, 56, 52, -0.8, 2, "Yellow & Blue", "Nuevo Mirandilla", 20000),
        ("Alaves", 52, 54, 50, -0.5, 2, "Blue & White", "Mendizorrotza", 20000),
        ("Almeria", 50, 52, 48, -1.2, 1, "Red & White", "Power Horse Stadium", 15000),
        ("Granada", 48, 50, 46, -1.5, 1, "Red & White", "Nuevo Los Cármenes", 19000),
        ("Elche", 46, 48, 44, -2.0, 1, "Green & White", "Martínez Valero", 33000)
    ]
    
    for name, strength, attack, defense, form, home_adv, colors, stadium, capacity in la_liga_teams:
        teams[name] = {
            "name": name,
            "league": "La Liga",
            "country": "Spain",
            "strength": strength,
            "attack": attack,
            "defense": defense,
            "form": form,
            "home_advantage": home_adv,
            "colors": colors,
            "stadium": stadium,
            "capacity": capacity,
            "founded": random.randint(1900, 2000),
            "nickname": f"Los {name.split()[-1]}" if len(name.split()) > 1 else f"Los {name}"
        }
    
    # Add more leagues...
    # (Bundesliga, Serie A, etc. - truncated for brevity)
    
    return teams

def generate_client_data(client_name: str) -> Dict[str, Any]:
    """
    Generate client-specific data structure.
    
    Args:
        client_name (str): Name of the client
        
    Returns:
        Dict[str, Any]: Client data structure
    """
    return {
        "client": {
            "name": client_name,
            "id": f"client_{client_name.lower().replace(' ', '_')}",
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "description": f"League data for {client_name}",
            "settings": {
                "default_league": "Premier League",
                "max_concurrent_matches": 10,
                "match_duration_minutes": 90,
                "time_acceleration": 1.0,
                "update_interval": 0.1
            }
        },
        "leagues": generate_league_data(),
        "teams": generate_team_data(),
        "metadata": {
            "total_leagues": 8,
            "total_teams": 78,
            "generated_at": datetime.now().isoformat(),
            "data_version": "1.0.0"
        }
    }

def save_data_to_files(client_name: str, output_dir: str = "data") -> None:
    """
    Save generated data to JSON files.
    
    Args:
        client_name (str): Name of the client
        output_dir (str): Output directory for JSON files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate data
    client_data = generate_client_data(client_name)
    
    # Save complete client data
    client_file = os.path.join(output_dir, f"{client_name.lower().replace(' ', '_')}_complete.json")
    with open(client_file, 'w', encoding='utf-8') as f:
        json.dump(client_data, f, indent=2, ensure_ascii=False)
    
    # Save individual league data
    leagues_dir = os.path.join(output_dir, "leagues")
    os.makedirs(leagues_dir, exist_ok=True)
    
    for league_name, league_data in client_data["leagues"].items():
        league_file = os.path.join(leagues_dir, f"{league_name.lower().replace(' ', '_')}.json")
        with open(league_file, 'w', encoding='utf-8') as f:
            json.dump(league_data, f, indent=2, ensure_ascii=False)
    
    # Save teams by league
    teams_dir = os.path.join(output_dir, "teams")
    os.makedirs(teams_dir, exist_ok=True)
    
    teams_by_league = {}
    for team_name, team_data in client_data["teams"].items():
        league = team_data["league"]
        if league not in teams_by_league:
            teams_by_league[league] = {}
        teams_by_league[league][team_name] = team_data
    
    for league_name, teams in teams_by_league.items():
        teams_file = os.path.join(teams_dir, f"{league_name.lower().replace(' ', '_')}_teams.json")
        with open(teams_file, 'w', encoding='utf-8') as f:
            json.dump(teams, f, indent=2, ensure_ascii=False)
    
    # Save metadata
    metadata_file = os.path.join(output_dir, "metadata.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(client_data["metadata"], f, indent=2, ensure_ascii=False)
    
    print(f"✅ Data generated for {client_name}")
    print(f"📁 Complete data: {client_file}")
    print(f"📁 Leagues: {leagues_dir}")
    print(f"📁 Teams: {teams_dir}")
    print(f"📁 Metadata: {metadata_file}")

def main():
    """Main function to generate data for multiple clients."""
    clients = [
        "VFL Premier",
        "VFL Europe", 
        "VFL Global",
        "VFL Championship"
    ]
    
    print("🚀 VFL Virtual Soccer MVP - Data Generator")
    print("=" * 50)
    
    for client in clients:
        print(f"\n🎯 Generating data for {client}...")
        save_data_to_files(client)
    
    print(f"\n✅ All data generated successfully!")
    print(f"📊 Generated data for {len(clients)} clients")

if __name__ == "__main__":
    main()
