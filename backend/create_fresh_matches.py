#!/usr/bin/env python3
"""
Create fresh matches that are just starting for immediate events
"""

import socketio
import time

def create_fresh_playoffs():
    """Connect and trigger creation of fresh playoffs with new matches"""
    
    sio = socketio.Client()
    
    @sio.event
    def connect():
        print("✅ Connected to create fresh matches!")
        
    @sio.event
    def joined(data):
        client_id = data.get('client_id')
        print(f"🎯 Joined as: {client_id}")
        
    @sio.event
    def full_update(data):
        playoffs = data.get('playoffs', [])
        active_matches = 0
        live_matches = 0
        
        for playoff in playoffs:
            for match in playoff.get('matches', []):
                if match.get('status') in ['betting_open', 'live']:
                    active_matches += 1
                if match.get('status') == 'live' and match.get('current_minute', 90) < 80:
                    live_matches += 1
        
        print(f"📊 {data.get('client_id', 'unknown')}: {len(playoffs)} playoffs, {active_matches} active, {live_matches} fresh matches")
        
    @sio.event
    def real_time_event(data):
        event_type = data.get('type', 'unknown')
        if event_type in ['match_event', 'match_start']:
            description = data.get('description', data.get('event_data', {}).get('description', ''))[:50]
            print(f"⚡ LIVE EVENT: {event_type} - {description}")
        
    try:
        print("🚀 Creating Fresh Matches for Immediate Events")
        print("=" * 50)
        
        sio.connect('http://localhost:5000')
        
        # Connect as multiple clients to trigger fresh playoff generation
        fresh_clients = [
            'client_premier_fresh', 'demo_client_fresh', 'client_global_fresh',
            'client_europe_fresh', 'client_spain_fresh'
        ]
        
        print("🎲 Triggering fresh playoff generation...")
        for client_id in fresh_clients:
            print(f"📤 Creating fresh playoffs for {client_id}...")
            sio.emit('join_client', {'client_id': client_id})
            time.sleep(2)  # Give time for auto-generation
        
        # Now connect as regular clients to check status
        regular_clients = ['client_premier', 'demo_client']
        
        print(f"\n📊 Checking status of regular clients...")
        for client_id in regular_clients:
            print(f"📤 Checking {client_id}...")
            sio.emit('join_client', {'client_id': client_id})
            time.sleep(1)
        
        print(f"\n⏳ Monitoring for live events for 15 seconds...")
        start_time = time.time()
        event_count = 0
        
        @sio.event
        def real_time_event(data):
            nonlocal event_count
            event_count += 1
            event_type = data.get('type', 'unknown')
            elapsed = int(time.time() - start_time)
            print(f"  {elapsed:2d}s: ⚡ Event #{event_count}: {event_type}")
        
        time.sleep(15)
        
        print(f"\n📊 Results:")
        print(f"   ⚡ Total events received: {event_count}")
        
        if event_count > 0:
            print(f"   ✅ SUCCESS: Events are flowing to the client!")
            print(f"   🎮 UI should be updating with live data")
        else:
            print(f"   ⚠️  No events received - matches may all be finished")
            print(f"   🔄 Need to create new matches or restart playoffs")
        
        sio.disconnect()
        
    except Exception as e:
        print(f"❌ Fresh match creation failed: {e}")

if __name__ == '__main__':
    create_fresh_playoffs()

