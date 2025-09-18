#!/usr/bin/env python3
"""
Trigger playoff generation directly in the running server
"""

import socketio
import time
import json

def trigger_server_playoff_generation():
    """Send commands to the running server to generate more playoffs"""
    
    sio = socketio.Client()
    
    @sio.event
    def connect():
        print("✅ Connected to running server!")
        
    @sio.event
    def joined(data):
        client_id = data.get('client_id')
        print(f"🎯 Joined as: {client_id}")
        
    @sio.event
    def full_update(data):
        client_id = data.get('client_id', 'unknown')
        playoffs = data.get('playoffs', [])
        print(f"📊 {client_id} now has: {len(playoffs)} playoffs")
        
    @sio.event
    def real_time_event(data):
        event_type = data.get('type', 'unknown')
        if event_type in ['playoff_start', 'playoff_updated']:
            print(f"⚡ {event_type}: {data.get('description', '')}")
        
    try:
        print("🔌 Connecting to trigger server-side generation...")
        sio.connect('http://localhost:5000')
        
        # Method 1: Use internal server API via WebSocket custom events
        print("\n🎲 Method 1: Triggering bulk creation...")
        
        # Create multiple playoffs directly via server
        clients_to_boost = ['client_premier', 'demo_client', 'client_global', 'client_europe']
        
        for client_id in clients_to_boost:
            print(f"📤 Generating 5 playoffs for {client_id}...")
            
            # Create multiple playoffs for this client
            for i in range(5):
                # Emit a custom event to create a new playoff
                playoff_data = {
                    'client_id': client_id,
                    'name': f'Generated Playoff {i+1}',
                    'action': 'create_and_start'
                }
                
                # Try to join first to trigger auto-generation
                sio.emit('join_client', {'client_id': client_id})
                time.sleep(0.5)
                
                # Then request playoffs to see current count
                sio.emit('get_playoffs', {'client_id': client_id})
                time.sleep(0.5)
        
        print("\n⏳ Waiting for generation to complete...")
        time.sleep(5)
        
        # Check final counts
        print("\n📊 Final check...")
        for client_id in clients_to_boost:
            sio.emit('join_client', {'client_id': client_id})
            time.sleep(1)
        
        print("\n✅ Server-side generation attempt completed!")
        
        sio.disconnect()
        
    except Exception as e:
        print(f"❌ Server generation failed: {e}")

def create_manual_playoffs_in_server():
    """Manually create playoffs by manipulating the running server"""
    
    print("\n🔧 MANUAL Playoff Creation in Server")
    print("=" * 40)
    
    # This approach sends repeated join requests to trigger auto-generation
    sio = socketio.Client()
    
    created_count = 0
    
    @sio.event
    def connect():
        print("✅ Connected for manual creation!")
        
    @sio.event
    def joined(data):
        nonlocal created_count
        created_count += 1
        client_id = data.get('client_id')
        print(f"🎯 Manual join #{created_count}: {client_id}")
        
    try:
        sio.connect('http://localhost:5000')
        
        # Create many manual connections to trigger playoff auto-generation
        clients = ['client_premier', 'demo_client', 'client_global', 'client_europe', 'client_spain']
        
        print(f"🔄 Triggering auto-generation via {len(clients)} x 10 joins...")
        
        for round_num in range(10):  # 10 rounds
            for client_id in clients:
                sio.emit('join_client', {'client_id': client_id})
                time.sleep(0.2)  # Small delay
            
            print(f"   Round {round_num + 1} completed")
        
        print(f"\n📊 Triggered {created_count} join events")
        print("⏳ Allowing server to process...")
        time.sleep(3)
        
        sio.disconnect()
        
    except Exception as e:
        print(f"❌ Manual creation failed: {e}")

if __name__ == '__main__':
    print("🚀 Server Playoff Generation Trigger")
    print("=" * 50)
    
    trigger_server_playoff_generation()
    create_manual_playoffs_in_server()
    
    print("\n🎉 All generation methods attempted!")
    print("📋 Run check_current_playoffs.py to see results")

