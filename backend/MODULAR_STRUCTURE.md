# VFL Virtual Soccer MVP - Modular Structure

The simulation engine has been successfully split into smaller, more manageable modules organized in a `modules/` folder.

## 📁 Project Structure

```
backend/
├── modules/
│   ├── __init__.py          # Package initialization and exports
│   ├── models.py            # Data models (Team, Match, MatchEvent, Playoff)
│   ├── engine.py            # Core simulation engine logic
│   └── api.py               # Flask API endpoints
├── database.py              # MySQL database models and functions
├── main.py                  # Main application entry point
├── simulation_engine.py     # Original monolithic file (kept for reference)
└── test_modular.py          # Test script for modular structure
```

## 🧩 Module Breakdown

### `modules/models.py`
Contains all the dataclasses and data structures:
- **Team**: Football team with stats (strength, attack, defense, form, etc.)
- **Match**: Football match between two teams
- **MatchEvent**: Individual events during a match (goals, cards, etc.)
- **Playoff**: Collection of 4 matches for a client
- **Helper functions**: `team_to_dict()`, `match_to_dict()`, `playoff_to_dict()`

### `modules/engine.py`
Core simulation logic:
- **SimulationEngine**: Main engine class
- **Team/League management**: Initialize teams and leagues
- **Match simulation**: Probabilistic event generation
- **Playoff management**: Create, start, stop playoffs
- **Auto-scheduling**: Daily playoff generation at midnight
- **Client management**: Load client data from MySQL

### `modules/api.py`
Flask REST API endpoints:
- **Health check**: `/api/health`
- **Matches**: `/api/matches/*`
- **Leagues/Teams**: `/api/leagues`, `/api/teams/*`
- **Playoffs**: `/api/playoffs/*`
- **Clients**: `/api/clients/*`
- **Companies**: `/api/companies/*`
- **Scheduler**: `/api/scheduler/*`
- **Database**: `/api/database/*`

### `main.py`
Application entry point:
- Creates Flask app using `create_app()`
- Configures logging
- Starts the server

## 🚀 Usage

### Running the Application
```bash
# Start the modular application
python main.py

# Or run the original monolithic version
python simulation_engine.py
```

### Testing the Modules
```bash
# Test module imports
python -c "from modules import Team, Match, SimulationEngine; print('✅ Modules working')"

# Test the full application
python test_modular.py
```

## 🔧 Benefits of Modular Structure

1. **Maintainability**: Each module has a single responsibility
2. **Readability**: Easier to understand and navigate
3. **Testability**: Individual modules can be tested separately
4. **Reusability**: Modules can be imported and used independently
5. **Scalability**: Easy to add new features or modify existing ones

## 📊 Database Integration

The modular structure maintains full MySQL integration:
- **Client data**: Loaded from database on startup
- **League assignments**: Stored in MySQL
- **Companies**: Managed through database
- **Auto-seeding**: Database populated with sample data

## 🎯 Key Features

- ✅ **Modular architecture**: Clean separation of concerns
- ✅ **MySQL integration**: Client/company data in database
- ✅ **Auto-scheduling**: Daily playoff generation at midnight
- ✅ **REST API**: Complete API for all functionality
- ✅ **Playoff system**: 4 matches per playoff, 50 per client per day
- ✅ **Multi-league support**: 8 leagues with 139 teams
- ✅ **Real-time simulation**: Live match updates

## 🔄 Migration from Monolithic

The original `simulation_engine.py` is kept for reference. The new modular structure:
- Maintains all existing functionality
- Improves code organization
- Makes future development easier
- Preserves database integration
- Keeps all API endpoints working

## 🧪 Testing

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
