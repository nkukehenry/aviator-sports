#!/usr/bin/env python3
"""
VFL Virtual Soccer MVP - Pure WebSocket Main Entry Point
WebSocket-only implementation with automatic UI updates
"""

import logging
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.websocket_app import create_websocket_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('vfl_websocket.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point for pure WebSocket implementation"""
    logger.info("Starting VFL Virtual Soccer MVP - Pure WebSocket Implementation")
    
    try:
        # Create WebSocket app
        app = create_websocket_app()
        
        # Auto-generate fresh playoffs for all clients on server startup
        logger.info("Generating fresh playoffs for immediate live action...")
        
        try:
            # Override daily limit to allow fresh generation every startup
            original_limit = app.simulation_engine.max_playoffs_per_client_per_day
            app.simulation_engine.max_playoffs_per_client_per_day = 100  # Allow many playoffs
            app.simulation_engine.last_generation_date = None  # Reset to allow fresh generation
            
            # Define clients to generate playoffs for on startup
            startup_clients = [
                'client_premier', 'demo_client', 'client_global', 'client_europe',
                'client_spain', 'client_italy', 'client_germany', 'client_france',
                'client_championship'
            ]
            
            total_playoffs_created = 0
            total_playoffs_started = 0
            
            logger.info(f"Creating fresh playoffs for {len(startup_clients)} clients...")
            
            for client_id in startup_clients:
                try:
                    logger.info(f"Generating playoffs for {client_id}...")
                    
                    # Generate playoffs for this client (will create up to 50)
                    playoffs = app.simulation_engine.generate_daily_playoffs_for_client(client_id)
                    total_playoffs_created += len(playoffs)
                    
                    logger.info(f"Generated {len(playoffs)} playoffs for {client_id}")
                    
                    # Start first 10 playoffs for immediate action
                    started_count = 0
                    for playoff in playoffs[:10]:
                        try:
                            app.simulation_engine.start_playoff(playoff.id)
                            started_count += 1
                        except Exception as e:
                            logger.error(f"Failed to start playoff {playoff.id}: {e}")
                    
                    total_playoffs_started += started_count
                    logger.info(f"Auto-started {started_count} playoffs for {client_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to generate playoffs for {client_id}: {e}")
            
            # Restore original limit
            app.simulation_engine.max_playoffs_per_client_per_day = original_limit
            
            logger.info(f"STARTUP GENERATION COMPLETE!")
            logger.info(f"  Total playoffs created: {total_playoffs_created}")
            logger.info(f"  Total playoffs started: {total_playoffs_started}")
            logger.info(f"  Ready for immediate live action!")
            
            # Verify a few key clients
            premier_playoffs = app.simulation_engine.get_playoffs_by_client("client_premier")
            demo_playoffs = app.simulation_engine.get_playoffs_by_client("demo_client")
            global_playoffs = app.simulation_engine.get_playoffs_by_client("client_global")
            
            logger.info(f"Verification:")
            logger.info(f"  client_premier: {len(premier_playoffs)} playoffs")
            logger.info(f"  demo_client: {len(demo_playoffs)} playoffs")  
            logger.info(f"  client_global: {len(global_playoffs)} playoffs")
            
        except Exception as e:
            logger.error(f"Error during startup playoff generation: {e}")
            import traceback
            traceback.print_exc()
        
        # Start event-driven processor (NO POLLING!)
        app.websocket_manager.start_event_processor()
        
        # Start the simulation loop to update matches continuously
        app.simulation_engine.start_simulation_loop()
        logger.info("Simulation loop started - matches will now progress automatically")
        
        # Log WebSocket events
        logger.info("WebSocket Events Available:")
        logger.info("  - connect: Client connects to server")
        logger.info("  - disconnect: Client disconnects from server")
        logger.info("  - join_client: Client joins with their ID")
        logger.info("  - leave_client: Client leaves their session")
        logger.info("  - get_playoffs: Get client's playoffs")
        logger.info("  - start_playoff: Start a specific playoff")
        logger.info("  - stop_playoff: Stop a specific playoff")
        logger.info("  - get_balance: Get client's financial information")
        logger.info("  - get_live_matches: Get live matches for client")
        logger.info("  - get_client_info: Get complete client information")
        
        logger.info("Event-Driven Updates (NO POLLING!):")
        logger.info("  - real_time_event: Instant event notifications (< 10ms)")
        logger.info("  - full_update: Complete data on connect only")
        logger.info("  - match_event: Individual match events (goals, cards)")
        logger.info("  - playoff_status: Playoff status changes")
        logger.info("  - client_balance: Financial updates")
        
        logger.info("Server starting on http://0.0.0.0:5000")
        logger.info("WebSocket endpoint: ws://0.0.0.0:5000/socket.io/")
        logger.info("Test client: Open websocket_client.html in browser")
        
        # Start the SocketIO server
        app.socketio.run(app, host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        logger.info("Shutting down WebSocket server...")
        if 'app' in locals():
            app.websocket_manager.stop_event_processor()
            app.simulation_engine.stop_simulation_loop()
        logger.info("WebSocket server stopped")
    except Exception as e:
        logger.error(f"Error starting WebSocket server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
