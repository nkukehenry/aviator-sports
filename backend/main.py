#!/usr/bin/env python3
"""
VFL Virtual Soccer MVP - Main Application
Entry point for the modular simulation engine
"""

import logging
from modules import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    logger.info("🚀 Starting VFL Virtual Soccer MVP - Modular Python Simulation Engine with WebSocket")
    
    # Create Flask app
    app = create_app()
    
    # Start real-time updates
    app.websocket_manager.start_real_time_updates()
    
    # Log API endpoints
    logger.info("📊 Health check: http://localhost:5000/api/health")
    logger.info("⚽ Matches API: http://localhost:5000/api/matches")
    logger.info("🏆 Leagues API: http://localhost:5000/api/leagues")
    logger.info("👥 Teams API: http://localhost:5000/api/teams")
    logger.info("🏁 Playoffs API: http://localhost:5000/api/playoffs")
    logger.info("🏢 Companies API: http://localhost:5000/api/companies")
    logger.info("🕐 Scheduler API: http://localhost:5000/api/scheduler")
    logger.info("🔌 WebSocket: ws://localhost:5000/socket.io/")
    
    try:
        # Start the SocketIO server
        app.socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("Shutting down simulation engine...")
        app.websocket_manager.stop_real_time_updates()
        logger.info("Simulation engine stopped")

if __name__ == '__main__':
    main()
