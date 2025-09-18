# 🏆 Aviator Sports - Virtual Football Betting Simulation

A real-time sports betting simulation platform featuring live football matches, dynamic odds, and WebSocket-powered events.

## 🎯 Overview

Aviator Sports is a comprehensive virtual football simulation that provides:
- **Real-time match simulation** with live events and scoring
- **Dynamic betting odds** that update based on match conditions
- **WebSocket-powered updates** for instant UI synchronization
- **Balanced team statistics** for unpredictable, exciting matches
- **Professional sports betting interface** with live scores and betting options

## ⚽ Key Features

### 🎲 **Realistic Match Simulation**
- **6 matches per playoff** with staggered start times
- **Balanced team stats** generated randomly for unpredictability
- **Goal limits**: Max 2 goals per team, some matches limited to 2 total goals
- **Dynamic form changes** during matches for momentum shifts
- **Upset potential** system allowing weaker teams to beat stronger ones

### 📊 **Sports Betting Interface**
- **Dynamic display switching**: Shows odds pre-match, scores/events during live matches
- **HOME | AWAY column separation** for clear team identification
- **Real-time odds generation** (1.3-2.5 range) including Over/Under 2.5 goals
- **Live match cycling** every 10 seconds in the left panel
- **Professional betting call-to-action** that updates with match status

### ⚡ **Real-time Event System**
- **WebSocket-powered** instant updates using Flask-SocketIO
- **Event-driven architecture** with observer pattern
- **Session management** for reliable event delivery
- **Live match events**: Goals, cards, corners, fouls, offsides
- **Playoff lifecycle management** with automatic new playoff generation

### 🎮 **User Experience**
- **Continuous action**: Each client maintains exactly 1 active playoff
- **Auto-generation**: New playoffs start within 30 seconds of completion
- **Live scores table**: Shows all matches from current playoff
- **Event notifications**: Real-time visual feedback for all match events
- **Stadium background** with authentic football field design

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nkukehenry/aviator-sports.git
   cd aviator-sports
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start the server**
   ```bash
   python websocket_main.py
   ```

4. **Open the application**
   - Navigate to `http://localhost:5000/sports` for the sports betting interface
   - Or `http://localhost:5000/` for the enhanced events UI

## 📁 Project Structure

```
aviator-sports/
├── backend/
│   ├── modules/
│   │   ├── engine.py              # Core simulation engine
│   │   ├── event_driven_websocket.py  # WebSocket event manager
│   │   ├── websocket_app.py       # Flask-SocketIO application
│   │   ├── models.py              # Data models (Team, Match, Playoff)
│   │   └── api.py                 # REST API endpoints
│   ├── sports_betting_ui.html     # Main sports betting interface
│   ├── enhanced_events_ui.html    # Debug/testing interface
│   ├── websocket_main.py          # Application entry point
│   ├── database.py                # Database configuration
│   └── requirements.txt           # Python dependencies
├── frontend/                      # Next.js frontend (future)
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🔧 Core Components

### 🎯 **Simulation Engine** (`modules/engine.py`)
- **Team Management**: 58+ teams across Premier League, La Liga, Bundesliga
- **Match Simulation**: Probabilistic event generation with realistic timing
- **Playoff Management**: Automatic creation and lifecycle management
- **Statistics**: Random team stats for balanced, unpredictable matches

### 📡 **WebSocket Manager** (`modules/event_driven_websocket.py`)
- **Event Broadcasting**: Real-time event delivery to connected clients
- **Session Management**: Reliable client-to-session mapping
- **Observer Pattern**: Listens to simulation engine events
- **Event Queue**: Threaded event processing for performance

### 🎨 **Sports Betting UI** (`sports_betting_ui.html`)
- **Two-column layout**: Live match display + scores table
- **Dynamic content**: Switches between odds and scores based on match status
- **Real-time updates**: WebSocket integration for instant synchronization
- **Professional design**: Stadium background with modern betting interface

## 🎮 How It Works

### 🔄 **Match Lifecycle**
1. **Playoff Creation**: 6 matches generated with random teams
2. **Betting Phase**: 45 seconds for playoff betting, then individual match betting
3. **Live Phase**: Matches start with 5-second intervals, 60-second duration
4. **Event Generation**: Goals, cards, corners generated probabilistically
5. **Completion**: New playoff auto-generated within 30 seconds

### 📊 **Event Flow**
```
Simulation Engine → Observer Pattern → WebSocket Manager → Client UI
```

1. **Engine** generates match events (goals, cards, etc.)
2. **Observer** notifies WebSocket manager of events
3. **WebSocket** broadcasts events to connected clients
4. **UI** receives events and updates display in real-time

### 🎯 **Betting Logic**
- **Pre-match**: Display betting odds for match result and total goals
- **Live**: Switch to scores, events, and status display
- **Finished**: Show final results and prepare for next playoff

## 🔥 Recent Enhancements

### ⚽ **Realistic Match Simulation**
- **Goal Limits**: No team scores more than 2 goals
- **Low-scoring matches**: 30% of matches limited to 2 total goals
- **Balanced stats**: Random team attributes for unpredictable outcomes
- **Dynamic form**: Teams gain/lose form during matches

### 🎨 **UI Improvements**
- **HOME | AWAY columns**: Separate team name display
- **Wider layout**: 800px right panel for better content visibility
- **Bigger fonts**: Enhanced readability for odds and scores
- **No text wrapping**: Clean, single-line row display

### 🔧 **Technical Optimizations**
- **Event-driven architecture**: Replaced polling with real-time events
- **Session management**: Fixed WebSocket event delivery issues
- **Dynamic display**: Automatic switching between betting and live modes
- **Performance**: Optimized update intervals and event processing

## 🛠️ Development

### 🧪 **Testing**
The application includes comprehensive testing tools:
- **WebSocket connectivity testing**
- **Event delivery verification**
- **Match simulation debugging**
- **UI responsiveness testing**

### 🔧 **Configuration**
Key settings in `modules/engine.py`:
```python
self.playoffs_per_playoff = 6          # 6 matches per playoff
self.update_interval = 0.1             # 100ms updates
self.half_duration = 30.0              # 30 seconds per half
self.betting_window_duration = 30.0    # 30 seconds for betting
```

### 📝 **Logging**
Comprehensive logging system tracks:
- Match events and scoring
- WebSocket connections and disconnections
- Playoff lifecycle changes
- Event delivery status

## 🎯 **API Endpoints**

### 🏆 **Match Management**
- `GET /api/matches` - Get all matches
- `POST /api/matches/<id>/start` - Start a match
- `POST /api/matches/<id>/stop` - Stop a match

### 🎲 **Playoff Management**
- `GET /api/playoffs` - Get all playoffs
- `POST /api/playoffs/generate/<client_id>` - Generate new playoff
- `POST /api/playoffs/<id>/start` - Start playoff betting

### 👥 **Client Management**
- `GET /api/clients` - Get all clients
- `GET /api/clients/<id>/balance` - Get client balance
- `POST /api/clients/<id>/balance` - Update balance

## 🌐 **WebSocket Events**

### 📡 **Real-time Events**
- `match_event` - Goals, cards, corners, fouls
- `match_start` - Match begins
- `match_end` - Match finishes
- `betting_opened` - Betting window opens
- `betting_locked` - Betting window closes
- `playoff_start` - Playoff begins
- `playoff_finished` - Playoff completes

### 🔄 **Client Events**
- `full_update` - Complete data refresh
- `client_balance` - Balance updates
- `joined` - Client connection confirmation

## 🎨 **UI Features**

### 📱 **Sports Betting Interface** (`/sports`)
- **Left Panel**: Stadium view with rotating live matches
- **Right Panel**: Live scores table with all playoff matches
- **Dynamic Headers**: Changes between "HOME | AWAY | Odds" and "HOME | AWAY | Score | Events | Status"
- **Call-to-Action**: Updates based on match/playoff status

### 🛠️ **Debug Interface** (`/`)
- **Enhanced events UI** for development and testing
- **Connection debugging tools**
- **Event logging and visualization**
- **Manual controls** for testing

## 🔒 **Security & Performance**

### 🛡️ **Security Features**
- **CORS enabled** for cross-origin requests
- **Session validation** for WebSocket events
- **Environment variable support** for sensitive configuration
- **SQL injection protection** with SQLAlchemy

### ⚡ **Performance Optimizations**
- **Event-driven architecture** eliminates polling overhead
- **Threaded event processing** for non-blocking operations
- **Efficient session management** with automatic cleanup
- **Optimized update intervals** (100ms) for smooth real-time experience

## 🎲 **Match Simulation Details**

### ⚽ **Realistic Scoring**
- **Balanced team stats**: Strength (65-90), Attack (60-95), Defense (55-90)
- **Form system**: Dynamic form changes (-3 to +3) during matches
- **Home advantage**: Random values (1-8) for varied conditions
- **Upset potential**: 15% chance for weaker teams to get attack boosts

### 📊 **Event Generation**
- **Probabilistic events**: Goals, cards, corners based on team stats
- **Frequency control**: Max 2 goals per 5-second period
- **Realistic timing**: Events distributed throughout 60-second matches
- **Momentum system**: Random ±20% variation in attack probability

## 🚀 **Deployment**

### 🐳 **Production Ready**
The application includes production dependencies:
- **Gunicorn**: WSGI server for production
- **Gevent**: High-performance async server
- **Redis**: Caching and session storage
- **PostgreSQL/MySQL**: Database support

### 🌍 **Environment Setup**
Create a `.env` file for production:
```env
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/aviator
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

## 📋 **Requirements**

See `backend/requirements.txt` for complete dependency list including:
- Flask & Flask-SocketIO for web framework and real-time events
- NumPy for mathematical calculations and random generation
- SQLAlchemy for database operations
- Redis for caching and session management
- Pytest for testing framework

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 **Features in Development**

- **Multi-league support**: Expansion to more football leagues
- **Advanced betting**: More betting options and markets
- **User accounts**: Registration and authentication system
- **Match history**: Historical data and statistics
- **Mobile responsiveness**: Optimized mobile experience

## 🏆 **Acknowledgments**

- Built with Flask-SocketIO for real-time WebSocket communication
- Uses NumPy for mathematical simulation and random generation
- Inspired by modern sports betting platforms
- Designed for educational and entertainment purposes

---

**🎲 Ready to experience the thrill of virtual football betting with real-time action!** 

Visit `http://localhost:5000/sports` to start betting on live virtual matches! ⚽🏆
