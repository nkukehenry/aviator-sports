# VFL Virtual Soccer MVP - WebSocket Implementation

## 🚀 Overview

The VFL Virtual Soccer system now includes full WebSocket functionality for real-time communication between clients and the server. When the application starts, it automatically generates data for each client, and when clients connect via WebSocket, playoffs are queued and started automatically.

## 🔧 Key Features

### ✅ **Auto-Generation on Startup**
- **Automatic Data Generation**: When the application starts, it automatically generates 50 playoffs per client
- **Client-Specific Leagues**: Each client gets playoffs based on their assigned leagues
- **Auto-Start Playoffs**: First 3 playoffs per client are automatically started
- **Database Integration**: All data is stored in MySQL with financial tracking

### ✅ **WebSocket Real-Time Communication**
- **Client Connection Handling**: Clients can connect and identify themselves
- **Real-Time Updates**: Live match updates sent every second
- **Playoff Management**: Start/stop playoffs via WebSocket
- **Balance Tracking**: Real-time financial information
- **Event Broadcasting**: Match events broadcast to all connected clients

### ✅ **Client Financial System**
- **Balance Tracking**: Each client has a balance, credit limit, and daily limit
- **Multi-Currency Support**: GBP, EUR, USD support
- **Transaction Management**: Credit, debit, and adjustment transactions
- **Real-Time Updates**: Balance changes sent via WebSocket

## 📁 New Files Added

### `modules/websocket.py`
- **WebSocketManager**: Manages client connections and real-time updates
- **Event Handlers**: Handle connect, disconnect, join_client, get_playoffs, etc.
- **Real-Time Updates**: Background thread sends live match updates
- **Client Management**: Track connected clients and their sessions

### `websocket_client.html`
- **Test Client**: HTML/JavaScript client for testing WebSocket functionality
- **Real-Time UI**: Live match display, balance tracking, event log
- **Client Selection**: Dropdown to select different clients
- **Interactive Controls**: Start/stop playoffs, get balance, etc.

## 🔌 WebSocket Events

### Client → Server Events
- `connect`: Client connects to server
- `disconnect`: Client disconnects from server
- `join_client`: Client joins with their ID
- `leave_client`: Client leaves their session
- `get_playoffs`: Request client's playoffs
- `start_playoff`: Start a specific playoff
- `stop_playoff`: Stop a specific playoff
- `get_balance`: Request client's balance

### Server → Client Events
- `connected`: Confirmation of connection
- `joined`: Confirmation of client join
- `left`: Confirmation of client leave
- `client_updates`: Real-time match updates
- `playoffs_data`: Playoff information
- `balance_data`: Financial information
- `match_update`: Individual match updates
- `welcome`: Welcome message with auto-generated data
- `error`: Error messages

## 🚀 Usage

### Starting the Server
```bash
python main.py
```

The server will:
1. Initialize database and load client data
2. Auto-generate playoffs for all clients
3. Start some playoffs automatically
4. Start WebSocket server on port 5000
5. Begin real-time update loop

### Testing with HTML Client
1. Open `websocket_client.html` in a browser
2. Click "Connect" to connect to WebSocket
3. Select a client from the dropdown
4. Click "Join as Client" to join that client's session
5. Watch real-time updates for live matches and balance

### WebSocket URL
```
ws://localhost:5000/socket.io/
```

## 📊 Auto-Generation Process

### On Startup
1. **Load Client Data**: Load all clients and their league assignments from MySQL
2. **Generate Playoffs**: Create 50 playoffs per client across their assigned leagues
3. **Auto-Start**: Start first 3 playoffs per client automatically
4. **Log Results**: Log generation statistics and any errors

### When Client Connects
1. **Validate Client**: Check if client exists in database
2. **Join Session**: Add client to their room for targeted updates
3. **Auto-Generate**: If client has no playoffs today, generate them
4. **Start Playoffs**: Auto-start some playoffs for the client
5. **Send Welcome**: Send welcome message with client info

## 💰 Financial System Integration

### Client Balance Fields
- **balance**: Current float balance
- **credit_limit**: Maximum credit limit
- **daily_limit**: Daily betting limit
- **currency**: Currency code (GBP, EUR, USD)

### Financial API Endpoints
- `GET /api/clients/{client_id}/balance`: Get balance info
- `POST /api/clients/{client_id}/balance`: Update balance
- `POST /api/clients/{client_id}/daily-limit`: Check daily limit

### WebSocket Financial Events
- `get_balance`: Request balance information
- `balance_data`: Receive balance updates

## 🔄 Real-Time Updates

### Update Frequency
- **Match Updates**: Every 1 second
- **Client Updates**: Every 1 second
- **Event Broadcasting**: Immediate

### Update Content
- **Live Matches**: Current score, time, events
- **Playoff Status**: Number of live/finished playoffs
- **Balance Info**: Current balance and limits
- **Match Events**: Goals, cards, corners, etc.

## 🧪 Testing

### Manual Testing
1. Start the server: `python main.py`
2. Open `websocket_client.html` in browser
3. Connect and join as different clients
4. Watch real-time updates
5. Test playoff management
6. Check balance updates

### API Testing
```bash
# Test health check
curl http://localhost:5000/api/health

# Test client balance
curl http://localhost:5000/api/clients/client_premier/balance

# Test playoff generation
curl -X POST http://localhost:5000/api/playoffs/generate/client_premier
```

## 🎯 Benefits

1. **Real-Time Experience**: Clients see live match updates instantly
2. **Automatic Setup**: No manual intervention needed for data generation
3. **Scalable**: Supports multiple concurrent clients
4. **Financial Tracking**: Complete balance and limit management
5. **Event-Driven**: Reactive to client actions and match events
6. **Professional**: Enterprise-grade WebSocket implementation

## 🔧 Configuration

### WebSocket Settings
- **Port**: 5000
- **CORS**: Enabled for all origins
- **Async Mode**: eventlet
- **Update Interval**: 1 second

### Auto-Generation Settings
- **Playoffs per Client**: 50 per day
- **Matches per Playoff**: 4
- **Auto-Start**: First 3 playoffs per client
- **Leagues**: Based on client assignments

The WebSocket implementation provides a complete real-time experience for the VFL Virtual Soccer system, with automatic data generation, client management, and live updates for all match activities.
