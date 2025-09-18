#!/usr/bin/env python3
"""
VFL Virtual Soccer MVP - Database Configuration
MySQL database setup and models for clients, companies, and league assignments
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import logging

# Initialize SQLAlchemy
db = SQLAlchemy()

# Configure logging
logger = logging.getLogger(__name__)

# Association table for many-to-many relationship between clients and leagues
client_leagues = Table(
    'client_leagues',
    db.Model.metadata,
    Column('client_id', String(50), ForeignKey('clients.id'), primary_key=True),
    Column('league_name', String(100), ForeignKey('leagues.name'), primary_key=True)
)

class Company(db.Model):
    """Company model for eBet companies"""
    __tablename__ = 'companies'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    country = Column(String(100))
    contact_email = Column(String(200))
    contact_phone = Column(String(50))
    max_playoffs_per_day = Column(Integer, default=50)
    is_active = Column(db.Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    clients = relationship("Client", back_populates="company")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'max_playoffs_per_day': self.max_playoffs_per_day,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'client_count': len(self.clients)
        }

class Client(db.Model):
    """Client model for betting shops"""
    __tablename__ = 'clients'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    company_id = Column(String(50), ForeignKey('companies.id'), nullable=False)
    shop_address = Column(Text)
    contact_email = Column(String(200))
    contact_phone = Column(String(50))
    max_playoffs_per_day = Column(Integer, default=50)
    
    # Financial fields
    balance = Column(db.Float, default=0.0)  # Current float balance
    credit_limit = Column(db.Float, default=10000.0)  # Maximum credit limit
    daily_limit = Column(db.Float, default=5000.0)  # Daily betting limit
    currency = Column(String(3), default='USD')  # Currency code
    
    # Status and timestamps
    is_active = Column(db.Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="clients")
    leagues = relationship("League", secondary=client_leagues, back_populates="clients")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'shop_address': self.shop_address,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'max_playoffs_per_day': self.max_playoffs_per_day,
            'balance': self.balance,
            'credit_limit': self.credit_limit,
            'daily_limit': self.daily_limit,
            'currency': self.currency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'assigned_leagues': [league.name for league in self.leagues]
        }

class League(db.Model):
    """League model for football leagues"""
    __tablename__ = 'leagues'
    
    name = Column(String(100), primary_key=True)
    country = Column(String(100), nullable=False)
    tier = Column(Integer, default=1)
    strength_range_min = Column(Integer, default=50)
    strength_range_max = Column(Integer, default=100)
    attack_bonus = Column(Integer, default=0)
    defense_bonus = Column(Integer, default=0)
    home_advantage = Column(Integer, default=5)
    is_active = Column(db.Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    clients = relationship("Client", secondary=client_leagues, back_populates="leagues")
    
    def to_dict(self):
        return {
            'name': self.name,
            'country': self.country,
            'tier': self.tier,
            'strength_range': (self.strength_range_min, self.strength_range_max),
            'attack_bonus': self.attack_bonus,
            'defense_bonus': self.defense_bonus,
            'home_advantage': self.home_advantage,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'client_count': len(self.clients)
        }

def init_database(app):
    """Initialize the database with Flask app"""
    try:
        # Configure MySQL connection
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Admin!2025@localhost/vfl_soccer'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database with app
        db.init_app(app)
        
        # Create all tables
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        return False

def seed_database():
    """Seed the database with initial data"""
    try:
        with db.session.begin():
            # Create sample companies
            companies_data = [
                {
                    'id': 'company_1',
                    'name': 'eBet Europe Ltd',
                    'country': 'United Kingdom',
                    'contact_email': 'admin@ebet-europe.com',
                    'contact_phone': '+44 20 7123 4567',
                    'max_playoffs_per_day': 100
                },
                {
                    'id': 'company_2',
                    'name': 'eBet Spain S.A.',
                    'country': 'Spain',
                    'contact_email': 'admin@ebet-spain.com',
                    'contact_phone': '+34 91 123 4567',
                    'max_playoffs_per_day': 80
                },
                {
                    'id': 'company_3',
                    'name': 'eBet Germany GmbH',
                    'country': 'Germany',
                    'contact_email': 'admin@ebet-germany.com',
                    'contact_phone': '+49 30 123 4567',
                    'max_playoffs_per_day': 90
                }
            ]
            
            for company_data in companies_data:
                if not Company.query.filter_by(id=company_data['id']).first():
                    company = Company(**company_data)
                    db.session.add(company)
                    logger.info(f"✅ Created company: {company.name}")
            
            # Create leagues
            leagues_data = [
                {
                    'name': 'Premier League',
                    'country': 'England',
                    'tier': 1,
                    'strength_range_min': 70,
                    'strength_range_max': 95,
                    'attack_bonus': 5,
                    'defense_bonus': 3,
                    'home_advantage': 8
                },
                {
                    'name': 'La Liga',
                    'country': 'Spain',
                    'tier': 1,
                    'strength_range_min': 68,
                    'strength_range_max': 93,
                    'attack_bonus': 7,
                    'defense_bonus': 2,
                    'home_advantage': 6
                },
                {
                    'name': 'Bundesliga',
                    'country': 'Germany',
                    'tier': 1,
                    'strength_range_min': 65,
                    'strength_range_max': 90,
                    'attack_bonus': 6,
                    'defense_bonus': 4,
                    'home_advantage': 7
                },
                {
                    'name': 'Serie A',
                    'country': 'Italy',
                    'tier': 1,
                    'strength_range_min': 66,
                    'strength_range_max': 92,
                    'attack_bonus': 4,
                    'defense_bonus': 6,
                    'home_advantage': 5
                },
                {
                    'name': 'Ligue 1',
                    'country': 'France',
                    'tier': 1,
                    'strength_range_min': 60,
                    'strength_range_max': 88,
                    'attack_bonus': 3,
                    'defense_bonus': 3,
                    'home_advantage': 4
                },
                {
                    'name': 'Championship',
                    'country': 'England',
                    'tier': 2,
                    'strength_range_min': 40,
                    'strength_range_max': 70,
                    'attack_bonus': 2,
                    'defense_bonus': 2,
                    'home_advantage': 3
                },
                {
                    'name': 'Segunda División',
                    'country': 'Spain',
                    'tier': 2,
                    'strength_range_min': 35,
                    'strength_range_max': 65,
                    'attack_bonus': 1,
                    'defense_bonus': 1,
                    'home_advantage': 2
                },
                {
                    'name': '2. Bundesliga',
                    'country': 'Germany',
                    'tier': 2,
                    'strength_range_min': 30,
                    'strength_range_max': 70,
                    'attack_bonus': 1,
                    'defense_bonus': 2,
                    'home_advantage': 3
                }
            ]
            
            for league_data in leagues_data:
                if not League.query.filter_by(name=league_data['name']).first():
                    league = League(**league_data)
                    db.session.add(league)
                    logger.info(f"✅ Created league: {league.name}")
            
            # Create sample clients
            clients_data = [
                {
                    'id': 'client_premier',
                    'name': 'Premier Betting Shop London',
                    'company_id': 'company_1',
                    'shop_address': '123 Oxford Street, London W1C 1JN, UK',
                    'contact_email': 'london@premier-betting.com',
                    'contact_phone': '+44 20 7123 4567',
                    'max_playoffs_per_day': 50,
                    'balance': 15000.0,
                    'credit_limit': 25000.0,
                    'daily_limit': 8000.0,
                    'currency': 'GBP'
                },
                {
                    'id': 'client_europe',
                    'name': 'European Sports Betting',
                    'company_id': 'company_1',
                    'shop_address': '456 Regent Street, London W1B 5AH, UK',
                    'contact_email': 'europe@premier-betting.com',
                    'contact_phone': '+44 20 7123 4568',
                    'max_playoffs_per_day': 50,
                    'balance': 22000.0,
                    'credit_limit': 35000.0,
                    'daily_limit': 10000.0,
                    'currency': 'GBP'
                },
                {
                    'id': 'client_spain',
                    'name': 'Casa de Apuestas Madrid',
                    'company_id': 'company_2',
                    'shop_address': 'Calle Gran Vía 45, 28013 Madrid, Spain',
                    'contact_email': 'madrid@casa-apuestas.com',
                    'contact_phone': '+34 91 123 4567',
                    'max_playoffs_per_day': 50,
                    'balance': 12000.0,
                    'credit_limit': 20000.0,
                    'daily_limit': 6000.0,
                    'currency': 'EUR'
                },
                {
                    'id': 'client_germany',
                    'name': 'Wettbüro Berlin',
                    'company_id': 'company_3',
                    'shop_address': 'Unter den Linden 1, 10117 Berlin, Germany',
                    'contact_email': 'berlin@wettbuero.com',
                    'contact_phone': '+49 30 123 4567',
                    'max_playoffs_per_day': 50,
                    'balance': 18000.0,
                    'credit_limit': 30000.0,
                    'daily_limit': 7500.0,
                    'currency': 'EUR'
                },
                {
                    'id': 'client_italy',
                    'name': 'Scommesse Roma',
                    'company_id': 'company_1',
                    'shop_address': 'Via del Corso 123, 00186 Roma, Italy',
                    'contact_email': 'roma@scommesse.com',
                    'contact_phone': '+39 06 123 4567',
                    'max_playoffs_per_day': 50,
                    'balance': 10000.0,
                    'credit_limit': 18000.0,
                    'daily_limit': 5000.0,
                    'currency': 'EUR'
                },
                {
                    'id': 'client_france',
                    'name': 'Paris Sport Pari',
                    'company_id': 'company_1',
                    'shop_address': 'Champs-Élysées 78, 75008 Paris, France',
                    'contact_email': 'paris@sport-pari.com',
                    'contact_phone': '+33 1 42 12 34 56',
                    'max_playoffs_per_day': 50,
                    'balance': 14000.0,
                    'credit_limit': 22000.0,
                    'daily_limit': 7000.0,
                    'currency': 'EUR'
                },
                {
                    'id': 'client_championship',
                    'name': 'Championship Betting Birmingham',
                    'company_id': 'company_1',
                    'shop_address': 'Bull Street 12, Birmingham B4 6AD, UK',
                    'contact_email': 'birmingham@championship-betting.com',
                    'contact_phone': '+44 121 123 4567',
                    'max_playoffs_per_day': 50,
                    'balance': 8000.0,
                    'credit_limit': 15000.0,
                    'daily_limit': 4000.0,
                    'currency': 'GBP'
                },
                {
                    'id': 'client_global',
                    'name': 'Global Sports Betting',
                    'company_id': 'company_1',
                    'shop_address': 'Canary Wharf, London E14 5AB, UK',
                    'contact_email': 'global@sports-betting.com',
                    'contact_phone': '+44 20 7123 4569',
                    'max_playoffs_per_day': 50,
                    'balance': 30000.0,
                    'credit_limit': 50000.0,
                    'daily_limit': 15000.0,
                    'currency': 'USD'
                }
            ]
            
            for client_data in clients_data:
                if not Client.query.filter_by(id=client_data['id']).first():
                    client = Client(**client_data)
                    db.session.add(client)
                    logger.info(f"✅ Created client: {client.name}")
            
            # Assign leagues to clients
            client_league_assignments = {
                'client_premier': ['Premier League', 'Championship'],
                'client_europe': ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1'],
                'client_spain': ['La Liga', 'Segunda División'],
                'client_germany': ['Bundesliga', '2. Bundesliga'],
                'client_italy': ['Serie A'],
                'client_france': ['Ligue 1'],
                'client_championship': ['Championship'],
                'client_global': ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1', 'Championship', 'Segunda División', '2. Bundesliga']
            }
            
            for client_id, league_names in client_league_assignments.items():
                client = Client.query.filter_by(id=client_id).first()
                if client:
                    for league_name in league_names:
                        league = League.query.filter_by(name=league_name).first()
                        if league and league not in client.leagues:
                            client.leagues.append(league)
                            logger.info(f"✅ Assigned {league_name} to {client.name}")
            
            db.session.commit()
            logger.info("✅ Database seeded successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to seed database: {e}")
        db.session.rollback()
        return False

def get_client_leagues(client_id):
    """Get assigned leagues for a client"""
    try:
        client = Client.query.filter_by(id=client_id).first()
        if client:
            return [league.name for league in client.leagues if league.is_active]
        return []
    except Exception as e:
        logger.error(f"❌ Failed to get client leagues for {client_id}: {e}")
        return []

def get_all_clients():
    """Get all active clients with their league assignments"""
    try:
        clients = Client.query.filter_by(is_active=True).all()
        return {client.id: [league.name for league in client.leagues if league.is_active] for client in clients}
    except Exception as e:
        logger.error(f"❌ Failed to get all clients: {e}")
        return {}

def get_client_info(client_id):
    """Get detailed client information"""
    try:
        client = Client.query.filter_by(id=client_id).first()
        if client:
            return client.to_dict()
        return None
    except Exception as e:
        logger.error(f"❌ Failed to get client info for {client_id}: {e}")
        return None

def update_client_balance(client_id, amount, transaction_type='adjustment'):
    """Update client balance with transaction logging"""
    try:
        client = Client.query.filter_by(id=client_id).first()
        if not client:
            return False, "Client not found"
        
        # Validate transaction
        if transaction_type == 'debit' and (client.balance - amount) < -client.credit_limit:
            return False, f"Insufficient balance. Available: {client.balance + client.credit_limit}"
        
        if transaction_type == 'credit' and (client.balance + amount) > client.credit_limit:
            return False, f"Credit limit exceeded. Max: {client.credit_limit}"
        
        # Update balance
        if transaction_type == 'debit':
            client.balance -= amount
        elif transaction_type == 'credit':
            client.balance += amount
        else:  # adjustment
            client.balance = amount
        
        client.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"✅ Updated {client_id} balance: {client.balance} ({transaction_type}: {amount})")
        return True, f"Balance updated to {client.balance}"
        
    except Exception as e:
        logger.error(f"❌ Failed to update balance for {client_id}: {e}")
        db.session.rollback()
        return False, str(e)

def get_client_balance(client_id):
    """Get client balance and financial info"""
    try:
        client = Client.query.filter_by(id=client_id).first()
        if not client:
            return None
        
        return {
            'client_id': client_id,
            'balance': client.balance,
            'credit_limit': client.credit_limit,
            'daily_limit': client.daily_limit,
            'currency': client.currency,
            'available_credit': client.balance + client.credit_limit,
            'is_overdrawn': client.balance < 0
        }
    except Exception as e:
        logger.error(f"❌ Failed to get balance for {client_id}: {e}")
        return None

def check_daily_limit(client_id, amount):
    """Check if transaction exceeds daily limit"""
    try:
        client = Client.query.filter_by(id=client_id).first()
        if not client:
            return False, "Client not found"
        
        # This would need to be implemented with daily transaction tracking
        # For now, just check against the daily limit
        if amount > client.daily_limit:
            return False, f"Transaction exceeds daily limit of {client.daily_limit}"
        
        return True, "Within daily limit"
    except Exception as e:
        logger.error(f"❌ Failed to check daily limit for {client_id}: {e}")
        return False, str(e)
