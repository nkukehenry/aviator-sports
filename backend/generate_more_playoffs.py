#!/usr/bin/env python3
"""
Generate more playoffs for all clients
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.engine import SimulationEngine
from datetime import datetime
import socketio
import time

def generate_playoffs_via_api():
    """Generate playoffs by connecting to the running server and triggering generation"""
    
    sio = socketio.Client()
    
    @sio.event
    def connect():
        print("✅ Connected to server!")
        
    @sio.event
    def joined(data):
        print(f"🎯 Joined as: {data.get('client_id')}")
        
    try:
        print("🔌 Connecting to server to trigger playoff generation...")
        sio.connect('http://localhost:5000')
        
        # We'll use the WebSocket to trigger generation for multiple clients
        clients = ['client_premier', 'demo_client', 'client_global', 'client_europe', 'client_spain', 'client_italy', 'client_germany', 'client_france']
        
        for client_id in clients:
            print(f"📤 Generating playoffs for {client_id}...")
            sio.emit('join_client', {'client_id': client_id})
            time.sleep(1)
            
        print("⏳ Waiting for server to process playoff generation...")
        time.sleep(5)
        
        sio.disconnect()
        print("✅ Playoff generation requests sent!")
        
    except Exception as e:
        print(f"❌ Failed to trigger via server: {e}")
        print("🔄 Trying direct engine approach...")
        generate_playoffs_directly()

def generate_playoffs_directly():
    """Generate playoffs directly using engine instance"""
    
    try:
        print("🏗️ Creating engine instance...")
        engine = SimulationEngine(random_seed=42)
        
        # Load client data
        from database import get_all_clients
        from flask import Flask
        
        app = Flask(__name__)
        with app.app_context():
            engine.load_client_data_from_db()
            
            print(f"📊 Loaded {len(engine.client_leagues)} clients")
            
            # Force reset the generation date to allow new generation
            engine.last_generation_date = None
            
            print("🚀 Generating daily playoffs for all clients...")
            generated = engine.generate_daily_playoffs_for_all_clients()
            
            total_playoffs = sum(len(playoffs) for playoffs in generated.values())
            print(f"✅ Generated {total_playoffs} playoffs across {len(generated)} clients")
            
            # Show breakdown
            for client_id, playoffs in generated.items():
                if playoffs:
                    print(f"   {client_id}: {len(playoffs)} playoffs")
                    
                    # Auto-start first few playoffs for immediate action
                    started_count = 0
                    for playoff in playoffs[:5]:  # Start first 5 per client
                        try:
                            engine.start_playoff(playoff.id)
                            started_count += 1
                        except Exception as e:
                            print(f"      ❌ Failed to start {playoff.id}: {e}")
                    
                    if started_count > 0:
                        print(f"      🏁 Auto-started {started_count} playoffs")
            
            print(f"\n🎉 SUCCESS: {total_playoffs} new playoffs generated and ready!")
            
    except Exception as e:
        print(f"❌ Direct generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🎲 VFL Playoff Generation Tool")
    print("=" * 40)
    
    # Try server approach first, fallback to direct
    generate_playoffs_via_api()

