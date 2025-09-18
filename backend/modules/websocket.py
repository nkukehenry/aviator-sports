#!/usr/bin/env python3
"""
VFL Virtual Soccer MVP - WebSocket Handler
Real-time communication for client connections and match updates
"""

import logging
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from datetime import datetime
import threading
import time
from typing import Dict, List

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and real-time updates"""
    
    def __init__(self, simulation_engine, socketio):
        self.simulation_engine = simulation_engine
        self.socketio = socketio
        self.connected_clients: Dict[str, str] = {}  # client_id -> session_id
        self.client_rooms: Dict[str, str] = {}  # session_id -> client_id
        self.is_running = False
        self.update_thread = None
        
    def start_real_time_updates(self):
        """Start the real-time update thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info("🔄 Real-time update thread started")
    
    def stop_real_time_updates(self):
        """Stop the real-time update thread"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=1)
        logger.info("🛑 Real-time update thread stopped")
    
    def _update_loop(self):
        """Background loop for sending real-time updates"""
        while self.is_running:
            try:
                # Send updates to all connected clients
                for session_id, client_id in self.client_rooms.items():
                    self._send_client_updates(client_id, session_id)
                
                time.sleep(1)  # Update every second
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                time.sleep(1)
    
    def _send_client_updates(self, client_id: str, session_id: str):
        """Send updates for a specific client"""
        try:
            # Get client's playoffs
            playoffs = self.simulation_engine.get_playoffs_by_client(client_id)
            
            # Get live matches for this client
            live_matches = []
            for playoff in playoffs:
                if playoff.status == 'live':
                    for match in playoff.matches:
                        if match.status == 'live':
                            live_matches.append({
                                'id': match.id,
                                'match_id': match.id,
                                'playoff_id': playoff.id,
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
                                'current_minute': match.current_minute,
                                'status': match.status,
                                'events': [{
                                    'minute': event.minute,
                                    'event_type': event.event_type,
                                    'team': event.team,
                                    'player': event.player,
                                    'description': event.description,
                                    'details': event.details
                                } for event in match.events]  # Send all events
                            })
            
            # Send comprehensive updates including playoff data
            playoff_data = []
            for playoff in playoffs:
                # Calculate real-time totals
                total_goals, total_events = self.simulation_engine.calculate_playoff_totals(playoff)
                
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
            
            # Send updates
            self.socketio.emit('client_updates', {
                'client_id': client_id,
                'timestamp': datetime.now().isoformat(),
                'live_matches': live_matches,
                'playoffs': playoff_data,
                'total_playoffs': len(playoffs),
                'live_playoffs': len([p for p in playoffs if p.status == 'live'])
            }, room=session_id)
            
        except Exception as e:
            logger.error(f"Error sending updates to {client_id}: {e}")
    
    def handle_client_connect(self, client_id: str, session_id: str):
        """Handle client connection"""
        try:
            # Store connection info
            self.connected_clients[client_id] = session_id
            self.client_rooms[session_id] = client_id
            
            # Join client to their room
            join_room(client_id, sid=session_id)
            
            logger.info(f"✅ Client {client_id} connected (session: {session_id})")
            
            # Auto-generate playoffs for this client if they don't have any today
            self._auto_generate_for_client(client_id)
            
            # Send welcome message
            self.socketio.emit('welcome', {
                'client_id': client_id,
                'message': f'Welcome {client_id}! Your playoffs are being prepared.',
                'timestamp': datetime.now().isoformat()
            }, room=session_id)
            
        except Exception as e:
            logger.error(f"Error handling client connection {client_id}: {e}")
    
    def handle_client_disconnect(self, session_id: str):
        """Handle client disconnection"""
        try:
            if session_id in self.client_rooms:
                client_id = self.client_rooms[session_id]
                del self.connected_clients[client_id]
                del self.client_rooms[session_id]
                logger.info(f"❌ Client {client_id} disconnected (session: {session_id})")
        except Exception as e:
            logger.error(f"Error handling client disconnection {session_id}: {e}")
    
    def _auto_generate_for_client(self, client_id: str):
        """Auto-generate playoffs for a client"""
        try:
            # Check if client already has playoffs today
            existing_playoffs = self.simulation_engine.get_playoffs_by_client(client_id)
            if existing_playoffs:
                logger.info(f"Client {client_id} already has {len(existing_playoffs)} playoffs today")
                return
            
            # Generate playoffs for this client
            playoffs = self.simulation_engine.generate_daily_playoffs_for_client(client_id)
            logger.info(f"🎲 Auto-generated {len(playoffs)} playoffs for {client_id}")
            
            # Start some playoffs automatically
            for i, playoff in enumerate(playoffs[:5]):  # Start first 5 playoffs
                try:
                    self.simulation_engine.start_playoff(playoff.id)
                    logger.info(f"🏁 Auto-started playoff {playoff.id} for {client_id}")
                except Exception as e:
                    logger.error(f"Failed to start playoff {playoff.id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error auto-generating for client {client_id}: {e}")
    
    def broadcast_match_update(self, match_id: str, match_data: dict):
        """Broadcast match update to all connected clients"""
        try:
            self.socketio.emit('match_update', {
                'match_id': match_id,
                'data': match_data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error broadcasting match update {match_id}: {e}")
    
    def send_to_client(self, client_id: str, event: str, data: dict):
        """Send data to a specific client"""
        try:
            if client_id in self.connected_clients:
                session_id = self.connected_clients[client_id]
                self.socketio.emit(event, data, room=session_id)
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")

def setup_websocket_handlers(socketio: SocketIO, simulation_engine, websocket_manager: WebSocketManager):
    """Setup WebSocket event handlers"""
    from flask import request
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        logger.info(f"Client connected: {request.sid}")
        emit('connected', {'message': 'Connected to VFL Virtual Soccer', 'session_id': request.sid})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        websocket_manager.handle_client_disconnect(request.sid)
        logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('join_client')
    def handle_join_client(data):
        """Handle client joining with their ID"""
        try:
            client_id = data.get('client_id')
            if not client_id:
                emit('error', {'message': 'client_id is required'})
                return
            
            # Validate client exists
            if client_id not in simulation_engine.client_leagues:
                emit('error', {'message': f'Client {client_id} not found'})
                return
            
            # Handle client connection
            websocket_manager.handle_client_connect(client_id, request.sid)
            
            emit('joined', {
                'client_id': client_id,
                'message': f'Joined as {client_id}',
                'assigned_leagues': simulation_engine.client_leagues[client_id]
            })
            
        except Exception as e:
            logger.error(f"Error handling join_client: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('leave_client')
    def handle_leave_client():
        """Handle client leaving"""
        websocket_manager.handle_client_disconnect(request.sid)
        emit('left', {'message': 'Left client session'})
    
    @socketio.on('get_playoffs')
    def handle_get_playoffs(data):
        """Handle request for client playoffs"""
        try:
            client_id = data.get('client_id')
            if not client_id:
                emit('error', {'message': 'client_id is required'})
                return
            
            playoffs = simulation_engine.get_playoffs_by_client(client_id)
            emit('playoffs_data', {
                'client_id': client_id,
                'playoffs': [{
                    'id': playoff.id,
                    'name': playoff.name,
                    'status': playoff.status,
                    'match_count': len(playoff.matches),
                    'total_goals': playoff.total_goals,
                    'total_events': playoff.total_events
                } for playoff in playoffs]
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
                'message': f'Playoff {playoff_id} started'
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
                'message': f'Playoff {playoff_id} stopped'
            })
            
        except Exception as e:
            logger.error(f"Error handling stop_playoff: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('get_balance')
    def handle_get_balance(data):
        """Handle request for client balance"""
        try:
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
