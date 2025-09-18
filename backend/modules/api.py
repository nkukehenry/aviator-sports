#!/usr/bin/env python3
"""
VFL Virtual Soccer MVP - Flask API
REST API endpoints for the simulation engine
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
import logging
from .engine import SimulationEngine
from .models import match_to_dict, playoff_to_dict
from .websocket import WebSocketManager, setup_websocket_handlers
from database import init_database, seed_database, get_all_clients, get_client_info

# Configure logging
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
    
    # Initialize database
    if not init_database(app):
        logger.error("❌ Failed to initialize database. Some features may not work properly.")
    
    # Initialize simulation engine
    simulation_engine = SimulationEngine(random_seed=42)
    
    # Load client data from database when app starts
    with app.app_context():
        simulation_engine.load_client_data_from_db()
    
    # Initialize WebSocket manager
    websocket_manager = WebSocketManager(simulation_engine, socketio)
    
    # Setup WebSocket handlers
    setup_websocket_handlers(socketio, simulation_engine, websocket_manager)
    
    # Auto-generate data for all clients on startup
    with app.app_context():
        logger.info("🎲 Auto-generating data for all clients on startup...")
        try:
            generated = simulation_engine.generate_daily_playoffs_for_all_clients()
            total_playoffs = sum(len(playoffs) for playoffs in generated.values())
            logger.info(f"✅ Generated {total_playoffs} playoffs for {len(generated)} clients")
            
            # Start some playoffs automatically
            for client_id, playoffs in generated.items():
                for i, playoff in enumerate(playoffs[:3]):  # Start first 3 playoffs per client
                    try:
                        simulation_engine.start_playoff(playoff.id)
                        logger.info(f"🏁 Auto-started playoff {playoff.id} for {client_id}")
                    except Exception as e:
                        logger.error(f"Failed to start playoff {playoff.id}: {e}")
        except Exception as e:
            logger.error(f"❌ Error auto-generating data: {e}")
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'message': 'VFL Virtual Soccer MVP is running',
            'timestamp': simulation_engine.matches,
            'total_matches': len(simulation_engine.matches),
            'total_playoffs': len(simulation_engine.playoffs),
            'total_teams': len(simulation_engine.teams),
            'leagues': list(simulation_engine.leagues.keys()),
            'playoff_settings': {
                'max_playoffs_per_client_per_day': simulation_engine.max_playoffs_per_client_per_day,
                'matches_per_playoff': simulation_engine.playoffs_per_playoff
            }
        })
    
    # Match endpoints
    @app.route('/api/matches', methods=['GET'])
    def get_matches():
        """Get all matches"""
        return jsonify({
            'success': True,
            'data': [match_to_dict(match) for match in simulation_engine.matches.values()]
        })
    
    @app.route('/api/matches/live', methods=['GET'])
    def get_live_matches():
        """Get all live matches"""
        live_matches = [match for match in simulation_engine.matches.values() if match.status == 'live']
        return jsonify({
            'success': True,
            'data': [match_to_dict(match) for match in live_matches]
        })
    
    @app.route('/api/matches/<match_id>', methods=['GET'])
    def get_match(match_id: str):
        """Get a specific match"""
        if match_id not in simulation_engine.matches:
            return jsonify({'success': False, 'error': 'Match not found'}), 404
        
        return jsonify({
            'success': True,
            'data': match_to_dict(simulation_engine.matches[match_id])
        })
    
    @app.route('/api/matches/<match_id>/start', methods=['POST'])
    def start_match(match_id: str):
        """Start a match"""
        try:
            simulation_engine.start_match(match_id)
            return jsonify({
                'success': True,
                'message': f'Match {match_id} started'
            })
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/matches/<match_id>/stop', methods=['POST'])
    def stop_match(match_id: str):
        """Stop a match"""
        try:
            simulation_engine.stop_match(match_id)
            return jsonify({
                'success': True,
                'message': f'Match {match_id} stopped'
            })
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # League and team endpoints
    @app.route('/api/leagues', methods=['GET'])
    def get_leagues():
        """Get all available leagues"""
        return jsonify({
            'success': True,
            'data': simulation_engine.leagues
        })
    
    @app.route('/api/teams', methods=['GET'])
    def get_teams():
        """Get all teams"""
        return jsonify({
            'success': True,
            'data': {name: {
                'name': team.name,
                'league': team.league,
                'country': team.country,
                'strength': team.strength,
                'attack': team.attack,
                'defense': team.defense,
                'form': team.form,
                'home_advantage': team.home_advantage
            } for name, team in simulation_engine.teams.items()}
        })
    
    @app.route('/api/teams/<league>', methods=['GET'])
    def get_teams_by_league(league: str):
        """Get teams by league"""
        league_teams = [team for team in simulation_engine.teams.values() if team.league == league]
        return jsonify({
            'success': True,
            'data': [{
                'name': team.name,
                'league': team.league,
                'country': team.country,
                'strength': team.strength,
                'attack': team.attack,
                'defense': team.defense,
                'form': team.form,
                'home_advantage': team.home_advantage
            } for team in league_teams]
        })
    
    # Playoff endpoints
    @app.route('/api/playoffs', methods=['GET'])
    def get_playoffs():
        """Get all playoffs"""
        return jsonify({
            'success': True,
            'data': [playoff_to_dict(playoff) for playoff in simulation_engine.playoffs.values()]
        })
    
    @app.route('/api/playoffs/client/<client_id>', methods=['GET'])
    def get_playoffs_by_client(client_id: str):
        """Get playoffs for a specific client"""
        playoffs = simulation_engine.get_playoffs_by_client(client_id)
        return jsonify({
            'success': True,
            'data': [playoff_to_dict(playoff) for playoff in playoffs],
            'client_id': client_id,
            'count': len(playoffs)
        })
    
    @app.route('/api/playoffs/generate', methods=['POST'])
    def generate_playoffs():
        """Generate daily playoffs for all clients (admin only)"""
        try:
            generated = simulation_engine.generate_daily_playoffs_for_all_clients()
            
            total_playoffs = sum(len(playoffs) for playoffs in generated.values())
            
            return jsonify({
                'success': True,
                'message': f'Generated {total_playoffs} playoffs for {len(generated)} clients',
                'data': {
                    'clients': list(generated.keys()),
                    'total_playoffs': total_playoffs,
                    'playoffs_per_client': {client: len(playoffs) for client, playoffs in generated.items()}
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/playoffs/generate/<client_id>', methods=['POST'])
    def generate_playoffs_for_client(client_id: str):
        """Generate daily playoffs for a specific client"""
        try:
            playoffs = simulation_engine.generate_daily_playoffs_for_client(client_id)
            
            return jsonify({
                'success': True,
                'message': f'Generated {len(playoffs)} playoffs for {client_id}',
                'data': [playoff_to_dict(playoff) for playoff in playoffs]
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/playoffs/<playoff_id>/start', methods=['POST'])
    def start_playoff(playoff_id: str):
        """Start a playoff"""
        try:
            simulation_engine.start_playoff(playoff_id)
            return jsonify({
                'success': True,
                'message': f'Playoff {playoff_id} started'
            })
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/playoffs/<playoff_id>/stop', methods=['POST'])
    def stop_playoff(playoff_id: str):
        """Stop a playoff"""
        try:
            simulation_engine.stop_playoff(playoff_id)
            return jsonify({
                'success': True,
                'message': f'Playoff {playoff_id} stopped'
            })
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/playoffs/<playoff_id>', methods=['GET'])
    def get_playoff(playoff_id: str):
        """Get a specific playoff"""
        playoff = simulation_engine.get_playoff(playoff_id)
        if not playoff:
            return jsonify({'success': False, 'error': 'Playoff not found'}), 404
        
        return jsonify({
            'success': True,
            'data': playoff_to_dict(playoff)
        })
    
    # Client endpoints
    @app.route('/api/clients', methods=['GET'])
    def get_clients():
        """Get all clients and their league assignments"""
        return jsonify({
            'success': True,
            'data': {
                'clients': list(simulation_engine.client_leagues.keys()),
                'client_leagues': simulation_engine.client_leagues,
                'total_clients': len(simulation_engine.client_leagues)
            }
        })
    
    @app.route('/api/clients/<client_id>/limits', methods=['GET'])
    def get_client_limits(client_id: str):
        """Get client daily limits and usage"""
        current = simulation_engine.get_client_playoff_count_today(client_id)
        remaining = simulation_engine.get_remaining_playoffs_today(client_id)
        max_limit = simulation_engine.max_playoffs_per_client_per_day
        
        return jsonify({
            'success': True,
            'data': {
                'client_id': client_id,
                'current_playoffs_today': current,
                'remaining_playoffs_today': remaining,
                'max_playoffs_per_day': max_limit,
                'matches_per_playoff': simulation_engine.playoffs_per_playoff
            }
        })
    
    # Scheduler endpoints
    @app.route('/api/scheduler/status', methods=['GET'])
    def get_scheduler_status():
        """Get auto-scheduler status"""
        return jsonify({
            'success': True,
            'data': {
                'enabled': simulation_engine.auto_generation_enabled,
                'running': simulation_engine.scheduler_thread and simulation_engine.scheduler_thread.is_alive(),
                'last_generation_date': simulation_engine.last_generation_date.isoformat() if simulation_engine.last_generation_date else None,
                'next_generation': 'Midnight (00:00)' if simulation_engine.auto_generation_enabled else 'Disabled'
            }
        })
    
    @app.route('/api/scheduler/start', methods=['POST'])
    def start_scheduler():
        """Start the auto-scheduler"""
        try:
            simulation_engine.start_auto_scheduler()
            return jsonify({
                'success': True,
                'message': 'Auto-scheduler started'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/scheduler/stop', methods=['POST'])
    def stop_scheduler():
        """Stop the auto-scheduler"""
        try:
            simulation_engine.stop_auto_scheduler()
            return jsonify({
                'success': True,
                'message': 'Auto-scheduler stopped'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Database endpoints
    @app.route('/api/database/seed', methods=['POST'])
    def seed_database_endpoint():
        """Seed the database with initial data"""
        try:
            if seed_database():
                # Reload client data after seeding
                simulation_engine.load_client_data_from_db()
                return jsonify({
                    'success': True,
                    'message': 'Database seeded successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to seed database'
                }), 500
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/database/reload', methods=['POST'])
    def reload_client_data():
        """Reload client data from database"""
        try:
            simulation_engine.load_client_data_from_db()
            return jsonify({
                'success': True,
                'message': 'Client data reloaded successfully',
                'data': {
                    'clients': list(simulation_engine.client_leagues.keys()),
                    'total_clients': len(simulation_engine.client_leagues)
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Company endpoints
    @app.route('/api/companies', methods=['GET'])
    def get_companies():
        """Get all companies"""
        try:
            from database import Company
            companies = Company.query.filter_by(is_active=True).all()
            return jsonify({
                'success': True,
                'data': [company.to_dict() for company in companies]
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/companies/<company_id>/clients', methods=['GET'])
    def get_company_clients(company_id: str):
        """Get all clients for a specific company"""
        try:
            from database import Company
            company = Company.query.filter_by(id=company_id).first()
            if not company:
                return jsonify({'success': False, 'error': 'Company not found'}), 404
            
            return jsonify({
                'success': True,
                'data': {
                    'company': company.to_dict(),
                    'clients': [client.to_dict() for client in company.clients if client.is_active]
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Client financial endpoints
    @app.route('/api/clients/<client_id>/balance', methods=['GET'])
    def get_client_balance(client_id: str):
        """Get client balance and financial information"""
        try:
            from database import get_client_balance
            balance_info = get_client_balance(client_id)
            if not balance_info:
                return jsonify({'success': False, 'error': 'Client not found'}), 404
            
            return jsonify({
                'success': True,
                'data': balance_info
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/clients/<client_id>/balance', methods=['POST'])
    def update_client_balance(client_id: str):
        """Update client balance"""
        try:
            from database import update_client_balance
            data = request.get_json() or {}
            
            amount = data.get('amount')
            transaction_type = data.get('type', 'adjustment')
            
            if amount is None:
                return jsonify({'success': False, 'error': 'Amount is required'}), 400
            
            success, message = update_client_balance(client_id, amount, transaction_type)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message
                })
            else:
                return jsonify({'success': False, 'error': message}), 400
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/clients/<client_id>/daily-limit', methods=['POST'])
    def check_daily_limit(client_id: str):
        """Check if transaction exceeds daily limit"""
        try:
            from database import check_daily_limit
            data = request.get_json() or {}
            
            amount = data.get('amount')
            if amount is None:
                return jsonify({'success': False, 'error': 'Amount is required'}), 400
            
            success, message = check_daily_limit(client_id, amount)
            
            return jsonify({
                'success': success,
                'message': message,
                'data': {
                    'client_id': client_id,
                    'amount': amount,
                    'within_limit': success
                }
            })
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Store references for external access
    app.socketio = socketio
    app.websocket_manager = websocket_manager
    app.simulation_engine = simulation_engine
    
    return app
