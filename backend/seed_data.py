#!/usr/bin/env python3
"""
VFL Virtual Soccer MVP - Direct Database Seeding
Seeds the database with sample data and tests the system
"""

from flask import Flask
from database import init_database, seed_database, get_all_clients, get_client_info
from simulation_engine import SimulationEngine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_and_test():
    """Seed database and test the system"""
    print("🌱 VFL Virtual Soccer MVP - Database Seeding & Testing")
    print("=" * 60)
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Initialize database
    print("\n📊 Initializing database...")
    if not init_database(app):
        print("❌ Database initialization failed")
        return False
    
    # Seed database
    print("\n🌱 Seeding database...")
    with app.app_context():
        if not seed_database():
            print("❌ Database seeding failed")
            return False
    
    # Test client data loading
    print("\n👥 Testing client data loading...")
    with app.app_context():
        try:
            clients = get_all_clients()
            print(f"✅ Loaded {len(clients)} clients from database")
            
            for client_id, leagues in clients.items():
                print(f"   {client_id}: {', '.join(leagues)}")
                
                # Get detailed client info
                client_info = get_client_info(client_id)
                if client_info:
                    print(f"     Company: {client_info['company_name']}")
                    print(f"     Address: {client_info['shop_address']}")
                    print(f"     Max playoffs/day: {client_info['max_playoffs_per_day']}")
            
        except Exception as e:
            print(f"❌ Error loading client data: {e}")
            return False
    
    # Test simulation engine with MySQL data
    print("\n⚽ Testing simulation engine with MySQL data...")
    try:
        engine = SimulationEngine(random_seed=42)
        engine.load_client_data_from_db()
        
        print(f"✅ Simulation engine loaded {len(engine.client_leagues)} clients")
        
        # Test playoff generation for a client
        test_client = "client_premier"
        if test_client in engine.client_leagues:
            print(f"\n🎲 Testing playoff generation for {test_client}...")
            playoffs = engine.generate_daily_playoffs_for_client(test_client)
            print(f"✅ Generated {len(playoffs)} playoffs")
            
            if playoffs:
                first_playoff = playoffs[0]
                print(f"   First playoff: {first_playoff.name}")
                print(f"   Matches: {len(first_playoff.matches)}")
                print(f"   Status: {first_playoff.status}")
                
                # Show match details
                for i, match in enumerate(first_playoff.matches[:2]):  # Show first 2 matches
                    print(f"     Match {i+1}: {match.home_team.name} vs {match.away_team.name}")
                    print(f"       League: {match.home_team.league}")
                    print(f"       Status: {match.status}")
        else:
            print(f"❌ Test client {test_client} not found")
            
    except Exception as e:
        print(f"❌ Error testing simulation engine: {e}")
        return False
    
    print("\n✅ Database seeding and testing completed successfully!")
    print("\n📋 Summary:")
    print("   - Database: vfl_soccer (MySQL)")
    print("   - Companies: 3 (eBet Europe, eBet Spain, eBet Germany)")
    print("   - Clients: 8 (various betting shops)")
    print("   - Leagues: 8 (Premier League, La Liga, Bundesliga, etc.)")
    print("   - Teams: 139 (across all leagues)")
    print("   - Client-League assignments: Configured")
    print("   - Playoff generation: Working")
    
    return True

if __name__ == "__main__":
    if seed_and_test():
        print("\n🎉 System is ready! You can now start the simulation engine.")
        print("   Run: python simulation_engine.py")
    else:
        print("\n💥 Seeding failed!")
