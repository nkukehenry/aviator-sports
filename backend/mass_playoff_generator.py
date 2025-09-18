#!/usr/bin/env python3
"""
Mass playoff generator - Creates lots of playoffs immediately
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.engine import SimulationEngine
from modules.models import Team
from datetime import datetime
import time

def create_instant_playoffs():
    """Create many playoffs instantly by bypassing daily limits"""
    
    print("🚀 MASS Playoff Generator")
    print("=" * 50)
    
    try:
        # Create engine instance
        engine = SimulationEngine(random_seed=int(time.time()))  # Random seed for variety
        
        # Load client data from database
        from database import get_all_clients
        from flask import Flask
        
        app = Flask(__name__)
        with app.app_context():
            engine.load_client_data_from_db()
            
            print(f"📊 Loaded {len(engine.client_leagues)} clients")
            
            # Override daily limits for mass generation
            original_limit = engine.max_playoffs_per_client_per_day
            engine.max_playoffs_per_client_per_day = 200  # Allow 200 per client!
            engine.last_generation_date = None  # Reset date check
            
            print(f"🔓 Increased limit from {original_limit} to {engine.max_playoffs_per_client_per_day} per client")
            
            # Generate for all clients
            all_clients = list(engine.client_leagues.keys())
            print(f"🎯 Generating playoffs for {len(all_clients)} clients...")
            
            total_generated = 0
            total_started = 0
            
            for client_id in all_clients:
                try:
                    print(f"\n🏆 Processing {client_id}...")
                    
                    # Generate playoffs for this client
                    playoffs = engine.generate_daily_playoffs_for_client(client_id)
                    print(f"   ✅ Generated: {len(playoffs)} playoffs")
                    total_generated += len(playoffs)
                    
                    # Start many of them (first 20 per client)
                    started_count = 0
                    for playoff in playoffs[:20]:
                        try:
                            engine.start_playoff(playoff.id)
                            started_count += 1
                        except Exception as e:
                            print(f"      ⚠️ Failed to start {playoff.id}: {e}")
                    
                    print(f"   🏁 Started: {started_count} playoffs")
                    total_started += started_count
                    
                except Exception as e:
                    print(f"   ❌ Failed for {client_id}: {e}")
            
            print(f"\n🎉 MASS GENERATION COMPLETE!")
            print(f"   📊 Total playoffs generated: {total_generated}")
            print(f"   🏁 Total playoffs started: {total_started}")
            print(f"   🎮 Ready for live action!")
            
            # Show current playoff counts per client
            print(f"\n📋 Current Playoff Counts:")
            for client_id in all_clients:
                client_playoffs = engine.get_playoffs_by_client(client_id)
                live_count = sum(1 for p in client_playoffs if p.status == 'live')
                betting_count = sum(1 for p in client_playoffs if p.status in ['betting_open', 'betting_locked'])
                print(f"   {client_id}: {len(client_playoffs)} total ({live_count} live, {betting_count} betting)")
            
    except Exception as e:
        print(f"❌ Mass generation failed: {e}")
        import traceback
        traceback.print_exc()

def create_extra_demo_playoffs():
    """Create additional demo playoffs with varied timings"""
    
    print("\n🎲 Creating EXTRA Demo Playoffs...")
    print("-" * 30)
    
    try:
        engine = SimulationEngine(random_seed=int(time.time()) + 1000)
        
        from flask import Flask
        app = Flask(__name__)
        with app.app_context():
            engine.load_client_data_from_db()
            
            # Create 10 extra playoffs for client_premier and demo_client
            demo_clients = ['client_premier', 'demo_client']
            
            for client_id in demo_clients:
                print(f"🏆 Creating 10 extra playoffs for {client_id}...")
                
                for i in range(10):
                    try:
                        playoff_name = f"Extra Live Demo {i+1}"
                        playoff = engine.create_playoff(client_id, playoff_name)
                        engine.start_playoff(playoff.id)
                        print(f"   ✅ Created & started: {playoff_name}")
                        
                    except Exception as e:
                        print(f"   ❌ Failed playoff {i+1}: {e}")
                        # Try with daily limit bypass
                        try:
                            engine.max_playoffs_per_client_per_day = 500
                            playoff = engine.create_playoff(client_id, f"Override Demo {i+1}")
                            engine.start_playoff(playoff.id)
                            print(f"   ✅ Override created: Override Demo {i+1}")
                        except:
                            pass
            
            print("🎉 Extra demo playoffs created!")
            
    except Exception as e:
        print(f"❌ Extra demo creation failed: {e}")

if __name__ == '__main__':
    create_instant_playoffs()
    create_extra_demo_playoffs()

