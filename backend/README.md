# VFL Virtual Soccer MVP - Python Backend

Enterprise-grade virtual soccer simulation engine built with Python, Flask, and NumPy.

## Features

- **Probabilistic Match Simulation**: Realistic match outcomes based on team statistics
- **Real-time Updates**: Live match progression with configurable time acceleration
- **Multi-league Support**: Premier League, La Liga, Bundesliga, Serie A, and more
- **Playoff System**: 4 matches per playoff, 50 playoffs per client per day
- **Auto-scheduling**: Daily playoff generation at midnight
- **REST API**: Complete API for match management and data access
- **MySQL Integration**: Client and company data stored in database
- **Modular Architecture**: Clean separation of concerns for maintainability

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database**
   ```bash
   python setup_database.py
   ```

3. **Run the Server**
   ```bash
   python main.py
   ```

4. **Test the System**
   ```bash
   python test_modular.py
   ```

## Project Structure

```
backend/
├── modules/
│   ├── __init__.py          # Package initialization
│   ├── models.py            # Data models (Team, Match, Playoff)
│   ├── engine.py            # Core simulation engine
│   └── api.py               # Flask API endpoints
├── database.py              # MySQL database models
├── main.py                  # Main application entry point
├── setup_database.py        # Database setup script
├── seed_data.py             # Data seeding script
└── test_modular.py          # Test script
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/matches` - All matches
- `GET /api/matches/live` - Live matches
- `GET /api/leagues` - Available leagues
- `GET /api/teams` - All teams
- `GET /api/playoffs` - All playoffs
- `POST /api/playoffs/generate` - Generate daily playoffs
- `GET /api/clients` - Client information
- `GET /api/companies` - Company information
- `GET /api/scheduler/status` - Auto-scheduler status

## Modular Architecture

The system uses a clean modular architecture:

- **`modules/models.py`**: Data structures and serialization
- **`modules/engine.py`**: Core simulation logic and match generation
- **`modules/api.py`**: Flask REST API endpoints
- **`database.py`**: MySQL integration and models
- **`main.py`**: Application entry point

## Database Schema

- **Companies**: eBet companies with client limits
- **Clients**: Betting shops with league assignments
- **Leagues**: Football leagues with characteristics
- **Client-League Assignments**: Many-to-many relationships

## Configuration

- **Max playoffs per client per day**: 50
- **Matches per playoff**: 4
- **Match duration**: 90 minutes (accelerated)
- **Auto-generation**: Daily at midnight
- **Total teams**: 139 across 8 leagues
- **Total clients**: 8 with assigned leagues

## Development

### Key Classes

#### SimulationEngine (modules/engine.py)
- Manages all match simulations
- Handles playoff generation and management
- Provides auto-scheduling functionality

#### Team (modules/models.py)
- Represents team with statistical attributes
- Influences match event probabilities

#### Match (modules/models.py)
- Complete match state and events
- Real-time progress tracking

#### Playoff (modules/models.py)
- Collection of 4 matches for a client
- Tracks total goals and events

### Adding New Features

1. **New Event Types**: Add to `_generate_match_event()` method in engine.py
2. **Team Statistics**: Extend `Team` dataclass in models.py
3. **API Endpoints**: Add new Flask routes in api.py
4. **Database Models**: Add new models in database.py

## Testing

Run the test script to verify everything works:
```bash
python test_modular.py
```

This will test:
- Module imports
- Engine creation
- Database connectivity
- API endpoints
- Playoff generation
- Client management

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Connection**: Check MySQL is running and credentials are correct
3. **Port Conflicts**: Check if port 5000 is available
4. **Module Not Found**: Ensure you're running from the backend directory

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

**Ready to simulate some matches?** 🏆

Run `python main.py` to start the server!