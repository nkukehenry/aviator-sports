#!/usr/bin/env python3
"""
VFL Virtual Soccer MVP - Pure WebSocket Application
WebSocket-only implementation with automatic UI updates
"""

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging
from .engine import SimulationEngine
from .models import match_to_dict, playoff_to_dict
from .event_driven_websocket import EventDrivenWebSocketManager
from database import init_database, seed_database, get_all_clients, get_client_info
import threading
import time
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def create_websocket_app():
    """Create and configure the pure WebSocket Flask application"""
    app = Flask(__name__)
    
    # Add CORS headers for all routes
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Add route for new sports betting UI
    @app.route('/sports')
    def sports_betting_ui():
        try:
            import os
            file_path = os.path.join(os.path.dirname(__file__), '..', 'sports_betting_ui.html')
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            response = app.response_class(content, mimetype='text/html')
            return response
        except FileNotFoundError as e:
            logger.error(f"Sports betting UI file not found: {e}")
            return f"Sports betting UI file not found at {file_path}", 404
    
    @app.route('/')
    def index():
        try:
            import os
            file_path = os.path.join(os.path.dirname(__file__), '..', 'enhanced_events_ui.html')
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            response = app.response_class(content, mimetype='text/html')
            return response
        except FileNotFoundError as e:
            logger.error(f"Enhanced events UI file not found: {e}")
            return f"Enhanced events UI file not found at {file_path}", 404
    
    # Initialize SocketIO with CORS enabled and extended timeouts
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*", 
        async_mode='threading',  # Changed from eventlet to threading
        ping_timeout=300,  # 5 minutes before timeout
        ping_interval=30,  # Ping every 30 seconds
        engineio_logger=True,  # Enable logging to debug
        logger=True  # Enable logging to debug
    )
    
    # Initialize database
    if not init_database(app):
        logger.error("❌ Failed to initialize database. Some features may not work properly.")
    
    # Initialize simulation engine
    simulation_engine = SimulationEngine(random_seed=42)
    
    # Load client data from database when app starts
    with app.app_context():
        simulation_engine.load_client_data_from_db()
    
    # Initialize Event-Driven WebSocket manager (NO POLLING!)
    websocket_manager = EventDrivenWebSocketManager(simulation_engine, socketio)
    
    # Start the event processor to handle simulation events
    websocket_manager.start_event_processor()
    logger.info("Event processor started - ready to handle simulation events")
    
    # Note: Playoff creation is now handled in websocket_main.py for better control
    logger.info("WebSocket app initialized - playoff creation handled by main startup")
    
    # WebSocket event handlers
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        logger.info(f"CONNECT: Client connected with session {request.sid}")
        logger.info(f"CONNECT: Current connected clients: {list(websocket_manager.connected_clients.keys())}")
        logger.info(f"CONNECT: Current session mapping: {dict(websocket_manager.connected_clients)}")
        
        emit('connected', {
            'message': 'Connected to VFL Virtual Soccer WebSocket - Event-Driven Mode',
            'session_id': request.sid,
            'timestamp': datetime.now().isoformat()
        })
        
        # Store the session for potential cleanup
        websocket_manager.temp_sessions[request.sid] = None
        
        # CRITICAL: Check if this is a reconnection for an existing client
        # This handles the case where a client reconnects with a new session
        for client_id, old_session in list(websocket_manager.connected_clients.items()):
            if old_session != request.sid:
                # This is a new session, but we need to check if it's the same client
                # We'll handle this in the join_client event
                logger.info(f"CONNECT: New session {request.sid} - will be handled in join_client")
                break
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info(f"DISCONNECT: Client session {request.sid} disconnecting...")
        websocket_manager.handle_client_disconnect(request.sid)
        
        # Clean up temp session
        if request.sid in websocket_manager.temp_sessions:
            del websocket_manager.temp_sessions[request.sid]
        
        logger.info(f"DISCONNECT: Session {request.sid} cleanup completed")
    
    @socketio.on('join_client')
    def handle_join_client(data):
        """Handle client joining with their ID"""
        try:
            client_id = data.get('client_id')
            if not client_id:
                emit('error', {'message': 'client_id is required'})
                return
            
            logger.info(f"JOIN_CLIENT: Client {client_id} requesting to join with session {request.sid}")
            
            # Validate client exists
            if client_id not in simulation_engine.client_leagues:
                emit('error', {'message': f'Client {client_id} not found'})
                return
            
            # CRITICAL FIX: Always force update session ID FIRST
            logger.info(f"JOIN_CLIENT: Force updating session for {client_id} to {request.sid}")
            logger.info(f"JOIN_CLIENT: Before force_update - Current session mapping: {dict(websocket_manager.connected_clients)}")
            websocket_manager.force_update_session(client_id, request.sid)
            logger.info(f"JOIN_CLIENT: After force_update - Current session mapping: {dict(websocket_manager.connected_clients)}")
            
            # Handle client connection
            logger.info(f"JOIN_CLIENT: Calling handle_client_connect for {client_id} with session {request.sid}")
            websocket_manager.handle_client_connect(client_id, request.sid)
            logger.info(f"JOIN_CLIENT: After handle_client_connect - Current session mapping: {dict(websocket_manager.connected_clients)}")
            
            # CRITICAL: Force update session ID AGAIN after connection to ensure it's current
            logger.info(f"JOIN_CLIENT: Final force update session for {client_id} to {request.sid}")
            websocket_manager.force_update_session(client_id, request.sid)
            logger.info(f"JOIN_CLIENT: Final session mapping: {dict(websocket_manager.connected_clients)}")
            
            # Get client's current playoffs and send them immediately
            playoffs = simulation_engine.get_playoffs_by_client(client_id)
            playoff_data = []
            for playoff in playoffs:
                # Calculate real-time totals
                total_goals, total_events = simulation_engine.calculate_playoff_totals(playoff)
                
                playoff_data.append({
                    'id': playoff.id,
                    'name': playoff.name,
                    'status': playoff.status,
                    'match_count': len(playoff.matches),
                    'total_goals': total_goals,
                    'total_events': total_events,
                    'betting_start_time': playoff.betting_start_time.isoformat() if playoff.betting_start_time else None,
                    'betting_lock_time': playoff.betting_lock_time.isoformat() if playoff.betting_lock_time else None,
                    'scheduled_start_time': playoff.scheduled_start_time.isoformat() if playoff.scheduled_start_time else None,
                    'matches': [{
                        'id': match.id,
                        'home_team': {
                            'name': match.home_team.name,
                            'league': match.home_team.league,
                            'country': match.home_team.country
                        },
                        'away_team': {
                            'name': match.away_team.name,
                            'league': match.away_team.league,
                            'country': match.away_team.country
                        },
                        'home_score': match.home_score,
                        'away_score': match.away_score,
                        'status': match.status,
                        'current_minute': match.current_minute,
                        'events': [{
                            'minute': event.minute,
                            'event_type': event.event_type,
                            'team': event.team,
                            'player': event.player,
                            'description': event.description,
                            'details': event.details
                        } for event in match.events]
                    } for match in playoff.matches]
                })
            
            emit('joined', {
                'client_id': client_id,
                'message': f'Joined as {client_id}',
                'assigned_leagues': simulation_engine.client_leagues[client_id],
                'playoffs': playoff_data,
                'timestamp': datetime.now().isoformat()
            })
            
            # IMMEDIATE TEST: Try emitting test events right after join
            logger.info(f"IMMEDIATE_TEST: About to emit test events to session {request.sid}")
            try:
                # Test 1: Direct emit to current session
                emit('immediate_test', {'message': 'Direct emit test', 'session': request.sid})
                logger.info(f"IMMEDIATE_TEST: Direct emit completed")
                
                # Test 2: SocketIO emit to session
                socketio.emit('socketio_test', {'message': 'SocketIO emit test', 'session': request.sid}, to=request.sid)
                logger.info(f"IMMEDIATE_TEST: SocketIO emit completed")
                
                # Test 3: Global broadcast
                socketio.emit('global_test', {'message': 'Global broadcast test'})
                logger.info(f"IMMEDIATE_TEST: Global broadcast completed")
                
            except Exception as e:
                logger.error(f"IMMEDIATE_TEST: Failed - {e}")
                import traceback
                logger.error(f"IMMEDIATE_TEST: Traceback - {traceback.format_exc()}")
            
            # Send client financial information
            from database import get_client_balance
            balance_info = get_client_balance(client_id)
            if balance_info:
                emit('client_balance', balance_info)
            
        except Exception as e:
            logger.error(f"Error handling join_client: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('leave_client')
    def handle_leave_client():
        """Handle client leaving"""
        websocket_manager.handle_client_disconnect(request.sid)
        emit('left', {'message': 'Left client session'})
    
    @socketio.on('get_playoffs')
    def handle_get_playoffs(data=None):
        """Handle request for client playoffs"""
        try:
            if not data:
                emit('error', {'message': 'No data provided'})
                return
            client_id = data.get('client_id')
            if not client_id:
                emit('error', {'message': 'client_id is required'})
                return
            
            playoffs = simulation_engine.get_playoffs_by_client(client_id)
            playoff_data = []
            for playoff in playoffs:
                # Calculate real-time totals
                total_goals, total_events = simulation_engine.calculate_playoff_totals(playoff)
                
                playoff_data.append({
                    'id': playoff.id,
                    'name': playoff.name,
                    'status': playoff.status,
                    'match_count': len(playoff.matches),
                    'total_goals': total_goals,
                    'total_events': total_events,
                    'matches': [{
                        'id': match.id,
                        'home_team': {
                            'name': match.home_team.name,
                            'league': match.home_team.league,
                            'country': match.home_team.country
                        },
                        'away_team': {
                            'name': match.away_team.name,
                            'league': match.away_team.league,
                            'country': match.away_team.country
                        },
                        'home_score': match.home_score,
                        'away_score': match.away_score,
                        'status': match.status,
                        'current_minute': match.current_minute,
                        'events': [{
                            'minute': event.minute,
                            'event_type': event.event_type,
                            'team': event.team,
                            'player': event.player,
                            'description': event.description,
                            'details': event.details
                        } for event in match.events]
                    } for match in playoff.matches]
                })
            
            emit('playoffs_data', {
                'client_id': client_id,
                'playoffs': playoff_data,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling get_playoffs: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('start_playoff')
    def handle_start_playoff(data):
        """Handle request to start a playoff"""
        try:
            playoff_id = data.get('playoff_id')
            if not playoff_id:
                emit('error', {'message': 'playoff_id is required'})
                return
            
            simulation_engine.start_playoff(playoff_id)
            emit('playoff_started', {
                'playoff_id': playoff_id,
                'message': f'Playoff {playoff_id} started',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling start_playoff: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('stop_playoff')
    def handle_stop_playoff(data):
        """Handle request to stop a playoff"""
        try:
            playoff_id = data.get('playoff_id')
            if not playoff_id:
                emit('error', {'message': 'playoff_id is required'})
                return
            
            simulation_engine.stop_playoff(playoff_id)
            emit('playoff_stopped', {
                'playoff_id': playoff_id,
                'message': f'Playoff {playoff_id} stopped',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling stop_playoff: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('get_balance')
    def handle_get_balance(data=None):
        """Handle request for client balance"""
        try:
            if not data:
                emit('error', {'message': 'No data provided'})
                return
            client_id = data.get('client_id')
            if not client_id:
                emit('error', {'message': 'client_id is required'})
                return
            
            from database import get_client_balance
            balance_info = get_client_balance(client_id)
            if balance_info:
                emit('balance_data', balance_info)
            else:
                emit('error', {'message': 'Client not found'})
                
        except Exception as e:
            logger.error(f"Error handling get_balance: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('get_live_matches')
    def handle_get_live_matches(data=None):
        """Handle request for live matches"""
        try:
            if not data:
                emit('error', {'message': 'No data provided'})
                return
            client_id = data.get('client_id')
            if not client_id:
                emit('error', {'message': 'client_id is required'})
                return
            
            # Get live matches for this client
            live_matches = []
            playoffs = simulation_engine.get_playoffs_by_client(client_id)
            for playoff in playoffs:
                if playoff.status == 'live':
                    for match in playoff.matches:
                        if match.status == 'live':
                            live_matches.append({
                                'match_id': match.id,
                                'playoff_id': playoff.id,
                                'home_team': match.home_team.name,
                                'away_team': match.away_team.name,
                                'home_score': match.home_score,
                                'away_score': match.away_score,
                                'current_minute': match.current_minute,
                                'status': match.status,
                                'events': len(match.events)
                            })
            
            emit('live_matches_data', {
                'client_id': client_id,
                'live_matches': live_matches,
                'count': len(live_matches),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling get_live_matches: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('get_client_info')
    def handle_get_client_info(data):
        """Handle request for client information"""
        try:
            client_id = data.get('client_id')
            if not client_id:
                emit('error', {'message': 'client_id is required'})
                return
            
            # Get client information from database
            client_info = get_client_info(client_id)
            if not client_info:
                emit('error', {'message': 'Client not found'})
                return
            
            # Get client's playoffs
            playoffs = simulation_engine.get_playoffs_by_client(client_id)
            playoff_data = []
            for playoff in playoffs:
                playoff_data.append({
                    'id': playoff.id,
                    'name': playoff.name,
                    'status': playoff.status,
                    'match_count': len(playoff.matches),
                    'total_goals': playoff.total_goals,
                    'total_events': playoff.total_events
                })
            
            # Get client's financial information
            from database import get_client_balance
            balance_info = get_client_balance(client_id)
            
            emit('client_info', {
                'client_id': client_id,
                'client_data': client_info,
                'playoffs': playoff_data,
                'balance': balance_info,
                'assigned_leagues': simulation_engine.client_leagues.get(client_id, []),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling get_client_info: {e}")
            emit('error', {'message': str(e)})
    
    # Store references for external access
    app.socketio = socketio
    app.websocket_manager = websocket_manager
    app.simulation_engine = simulation_engine
    
    return app
