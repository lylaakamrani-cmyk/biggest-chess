# © 2025 AmirAli Kamrani. All rights reserved.

# core/network.py
import asyncio
import json
import websocket
import socket
import threading
import queue
import time
import uuid
import hashlib
import ssl
from typing import Optional, Dict, List, Tuple, Any, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import pickle
import zlib

class MessageType(Enum):
    # Connection messages
    HANDSHAKE = "handshake"
    AUTH = "auth"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # Game messages
    MOVE = "move"
    GAME_STATE = "game_state"
    GAME_START = "game_start"
    GAME_END = "game_end"
    DRAW_OFFER = "draw_offer"
    RESIGN = "resign"
    TAKEOFF = "takeoff"
    
    # Chat messages
    CHAT = "chat"
    CHAT_HISTORY = "chat_history"
    
    # Lobby messages
    LOBBY_LIST = "lobby_list"
    JOIN_LOBBY = "join_lobby"
    LEAVE_LOBBY = "leave_lobby"
    CREATE_GAME = "create_game"
    JOIN_GAME = "join_game"
    
    # Tournament messages
    TOURNAMENT_CREATE = "tournament_create"
    TOURNAMENT_JOIN = "tournament_join"
    TOURNAMENT_LIST = "tournament_list"
    TOURNAMENT_START = "tournament_start"
    TOURNAMENT_END = "tournament_end"
    
    # Profile messages
    PROFILE_GET = "profile_get"
    PROFILE_UPDATE = "profile_update"
    PROFILE_STATS = "profile_stats"
    FRIEND_LIST = "friend_list"
    FRIEND_REQUEST = "friend_request"
    FRIEND_ACCEPT = "friend_accept"
    
    # Analysis messages
    ANALYSIS_REQUEST = "analysis_request"
    ANALYSIS_RESPONSE = "analysis_response"
    
    # Error messages
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"

@dataclass
class NetworkMessage:
    """Network message structure"""
    type: MessageType
    payload: Any
    timestamp: float
    sender_id: Optional[str] = None
    target_id: Optional[str] = None
    message_id: str = None
    game_id: Optional[str] = None
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = time.time()
            
    def to_json(self) -> str:
        """Convert to JSON"""
        data = {
            'type': self.type.value,
            'payload': self.payload,
            'timestamp': self.timestamp,
            'sender_id': self.sender_id,
            'target_id': self.target_id,
            'message_id': self.message_id,
            'game_id': self.game_id
        }
        return json.dumps(data)
        
    @classmethod
    def from_json(cls, json_str: str) -> 'NetworkMessage':
        """Create from JSON"""
        data = json.loads(json_str)
        return cls(
            type=MessageType(data['type']),
            payload=data.get('payload'),
            timestamp=data.get('timestamp', time.time()),
            sender_id=data.get('sender_id'),
            target_id=data.get('target_id'),
            message_id=data.get('message_id'),
            game_id=data.get('game_id')
        )

class NetworkServer:
    """WebSocket server for chess game networking"""
    
    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port
        self.websocket_server = None
        self.clients = {}  # client_id -> websocket
        self.client_info = {}  # client_id -> info
        self.games = {}  # game_id -> game_info
        self.lobbies = {}  # lobby_id -> lobby_info
        self.tournaments = {}  # tournament_id -> tournament_info
        self.message_handlers = {}
        self.running = False
        self.server_thread = None
        
        # Authentication
        self.users = {}  # username -> password_hash
        self.sessions = {}  # session_token -> client_id
        self.authenticated_clients = set()
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'total_messages': 0,
            'total_games': 0
        }
        
        # Callbacks
        self.connection_callbacks = []
        self.message_callbacks = []
        
    def start(self):
        """Start the server"""
        if self.running:
            return
            
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        print(f"Network server started on {self.host}:{self.port}")
        
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.websocket_server:
            try:
                self.websocket_server.close()
            except:
                pass
        if self.server_thread:
            self.server_thread.join(timeout=2)
        print("Network server stopped")
        
    def _run_server(self):
        """Run the server loop"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        start_server = websockets.serve(
            self._handle_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=60
        )
        
        loop.run_until_complete(start_server)
        loop.run_forever()
        
    async def _handle_client(self, websocket, path):
        """Handle a client connection"""
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket
        self.client_info[client_id] = {
            'connected_at': time.time(),
            'ip': websocket.remote_address[0] if websocket.remote_address else 'unknown',
            'authenticated': False,
            'username': None
        }
        self.stats['total_connections'] += 1
        self.stats['active_connections'] += 1
        
        # Send connection confirmation
        await self._send_message(websocket, NetworkMessage(
            type=MessageType.CONNECT,
            payload={'client_id': client_id, 'message': 'Connected to server'}
        ))
        
        # Notify callbacks
        self._notify_callbacks('connect', {'client_id': client_id})
        
        try:
            async for message in websocket:
                try:
                    msg = NetworkMessage.from_json(message)
                    self.stats['total_messages'] += 1
                    await self._process_message(client_id, msg)
                except Exception as e:
                    print(f"Error processing message: {e}")
                    await self._send_message(websocket, NetworkMessage(
                        type=MessageType.ERROR,
                        payload={'message': f'Error: {str(e)}'}
                    ))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Clean up
            self.stats['active_connections'] -= 1
            if client_id in self.clients:
                del self.clients[client_id]
            if client_id in self.client_info:
                del self.client_info[client_id]
            if client_id in self.authenticated_clients:
                self.authenticated_clients.remove(client_id)
            self._notify_callbacks('disconnect', {'client_id': client_id})
            
    async def _process_message(self, client_id: str, message: NetworkMessage):
        """Process incoming message"""
        # Check authentication if required
        if message.type not in [MessageType.HANDSHAKE, MessageType.AUTH, MessageType.CONNECT]:
            if client_id not in self.authenticated_clients:
                await self._send_message(self.clients[client_id], NetworkMessage(
                    type=MessageType.ERROR,
                    payload={'message': 'Not authenticated'}
                ))
                return
                
        # Route message based on type
        handler = self.message_handlers.get(message.type)
        if handler:
            try:
                await handler(client_id, message)
            except Exception as e:
                print(f"Handler error: {e}")
        else:
            # Default handling
            await self._default_message_handler(client_id, message)
            
    async def _default_message_handler(self, client_id: str, message: NetworkMessage):
        """Default message handler"""
        if message.type == MessageType.AUTH:
            await self._handle_auth(client_id, message)
        elif message.type == MessageType.PING:
            await self._handle_ping(client_id, message)
        elif message.type == MessageType.MOVE:
            await self._handle_move(client_id, message)
        elif message.type == MessageType.CHAT:
            await self._handle_chat(client_id, message)
        elif message.type == MessageType.CREATE_GAME:
            await self._handle_create_game(client_id, message)
        elif message.type == MessageType.JOIN_GAME:
            await self._handle_join_game(client_id, message)
        elif message.type == MessageType.ANALYSIS_REQUEST:
            await self._handle_analysis(client_id, message)
        elif message.type == MessageType.TOURNAMENT_CREATE:
            await self._handle_tournament_create(client_id, message)
        elif message.type == MessageType.PROFILE_GET:
            await self._handle_profile_get(client_id, message)
        else:
            await self._send_message(self.clients[client_id], NetworkMessage(
                type=MessageType.WARNING,
                payload={'message': f'Unknown message type: {message.type}'}
            ))
            
    async def _handle_auth(self, client_id: str, message: NetworkMessage):
        """Handle authentication"""
        payload = message.payload
        username = payload.get('username')
        password = payload.get('password')
        
        # Check credentials
        if username in self.users and self.users[username] == self._hash_password(password):
            # Authentication success
            token = self._generate_token()
            self.sessions[token] = client_id
            self.authenticated_clients.add(client_id)
            self.client_info[client_id]['authenticated'] = True
            self.client_info[client_id]['username'] = username
            
            await self._send_message(self.clients[client_id], NetworkMessage(
                type=MessageType.AUTH,
                payload={'success': True, 'token': token, 'username': username}
            ))
            
            # Broadcast user online
            await self._broadcast_message(NetworkMessage(
                type=MessageType.SUCCESS,
                payload={'message': f'{username} joined the server'}
            ), exclude=[client_id])
        else:
            await self._send_message(self.clients[client_id], NetworkMessage(
                type=MessageType.ERROR,
                payload={'message': 'Authentication failed'}
            ))
            
    async def _handle_ping(self, client_id: str, message: NetworkMessage):
        """Handle ping/pong"""
        await self._send_message(self.clients[client_id], NetworkMessage(
            type=MessageType.PONG,
            payload={'timestamp': time.time()}
        ))
        
    async def _handle_move(self, client_id: str, message: NetworkMessage):
        """Handle game move"""
        game_id = message.game_id
        if game_id in self.games:
            game = self.games[game_id]
            # Forward move to other player
            other_player = game['white'] if game['black'] == client_id else game['black']
            if other_player in self.clients:
                await self._send_message(self.clients[other_player], message)
            # Update game state
            game['last_move'] = message.payload
            game['last_update'] = time.time()
            
    async def _handle_chat(self, client_id: str, message: NetworkMessage):
        """Handle chat message"""
        # Broadcast to game participants or lobby
        target = message.target_id
        if target and target in self.clients:
            await self._send_message(self.clients[target], message)
        else:
            # Broadcast to all
            await self._broadcast_message(message)
            
    async def _handle_create_game(self, client_id: str, message: NetworkMessage):
        """Handle game creation"""
        game_id = str(uuid.uuid4())
        self.games[game_id] = {
            'id': game_id,
            'white': client_id,
            'black': None,
            'status': 'waiting',
            'created_at': time.time(),
            'last_move': None,
            'last_update': time.time(),
            'config': message.payload.get('config', {})
        }
        self.stats['total_games'] += 1
        
        # Add to lobby
        lobby_id = message.payload.get('lobby_id', 'public')
        if lobby_id not in self.lobbies:
            self.lobbies[lobby_id] = {'games': [], 'players': []}
        self.lobbies[lobby_id]['games'].append(game_id)
        
        # Notify creator
        await self._send_message(self.clients[client_id], NetworkMessage(
            type=MessageType.SUCCESS,
            payload={'game_id': game_id, 'message': 'Game created'}
        ))
        
        # Notify lobby
        await self._broadcast_lobby_update(lobby_id)
        
    async def _handle_join_game(self, client_id: str, message: NetworkMessage):
        """Handle game join"""
        game_id = message.payload.get('game_id')
        if game_id in self.games:
            game = self.games[game_id]
            if game['status'] == 'waiting':
                game['black'] = client_id
                game['status'] = 'playing'
                game['started_at'] = time.time()
                
                # Notify both players
                for player in [game['white'], game['black']]:
                    if player in self.clients:
                        await self._send_message(self.clients[player], NetworkMessage(
                            type=MessageType.GAME_START,
                            payload={'game_id': game_id, 'players': {'white': game['white'], 'black': game['black']}}
                        ))
                        
                # Broadcast game started
                await self._broadcast_message(NetworkMessage(
                    type=MessageType.SUCCESS,
                    payload={'message': f'Game {game_id} started'}
                ))
                
                # Update lobby
                await self._broadcast_lobby_update(message.payload.get('lobby_id', 'public'))
            else:
                await self._send_message(self.clients[client_id], NetworkMessage(
                    type=MessageType.ERROR,
                    payload={'message': 'Game already in progress'}
                ))
        else:
            await self._send_message(self.clients[client_id], NetworkMessage(
                type=MessageType.ERROR,
                payload={'message': 'Game not found'}
            ))
            
    async def _handle_analysis(self, client_id: str, message: NetworkMessage):
        """Handle analysis request"""
        # Forward to analysis service or return mock data
        await self._send_message(self.clients[client_id], NetworkMessage(
            type=MessageType.ANALYSIS_RESPONSE,
            payload={'analysis': 'Analysis result', 'timestamp': time.time()}
        ))
        
    async def _handle_tournament_create(self, client_id: str, message: NetworkMessage):
        """Handle tournament creation"""
        tournament_id = str(uuid.uuid4())
        self.tournaments[tournament_id] = {
            'id': tournament_id,
            'creator': client_id,
            'name': message.payload.get('name', 'Tournament'),
            'players': [client_id],
            'games': [],
            'status': 'waiting',
            'created_at': time.time(),
            'config': message.payload.get('config', {})
        }
        
        await self._send_message(self.clients[client_id], NetworkMessage(
            type=MessageType.SUCCESS,
            payload={'tournament_id': tournament_id, 'message': 'Tournament created'}
        ))
        
    async def _handle_profile_get(self, client_id: str, message: NetworkMessage):
        """Handle profile request"""
        username = message.payload.get('username')
        # Return mock profile data
        await self._send_message(self.clients[client_id], NetworkMessage(
            type=MessageType.PROFILE_GET,
            payload={
                'username': username or 'Unknown',
                'rating': 1500,
                'games_played': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0
            }
        ))
        
    async def _broadcast_lobby_update(self, lobby_id: str):
        """Broadcast lobby update"""
        if lobby_id in self.lobbies:
            lobby = self.lobbies[lobby_id]
            await self._broadcast_message(NetworkMessage(
                type=MessageType.LOBBY_LIST,
                payload={'lobby_id': lobby_id, 'data': lobby}
            ))
            
    async def _broadcast_message(self, message: NetworkMessage, exclude: List[str] = None):
        """Broadcast message to all clients"""
        exclude = exclude or []
        for client_id, websocket in self.clients.items():
            if client_id not in exclude:
                try:
                    await self._send_message(websocket, message)
                except:
                    pass
                    
    async def _send_message(self, websocket, message: NetworkMessage):
        """Send message to a specific client"""
        try:
            await websocket.send(message.to_json())
        except Exception as e:
            print(f"Error sending message: {e}")
            
    def _notify_callbacks(self, event: str, data: Dict):
        """Notify callbacks of events"""
        for callback in self.connection_callbacks:
            try:
                callback(event, data)
            except Exception as e:
                print(f"Callback error: {e}")
                
    def add_connection_callback(self, callback: Callable):
        """Add connection callback"""
        self.connection_callbacks.append(callback)
        
    def add_message_handler(self, message_type: MessageType, handler: Callable):
        """Add message handler"""
        self.message_handlers[message_type] = handler
        
    def register_user(self, username: str, password: str):
        """Register a new user"""
        self.users[username] = self._hash_password(password)
        
    def _hash_password(self, password: str) -> str:
        """Hash a password"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def _generate_token(self) -> str:
        """Generate session token"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        
    def get_stats(self) -> Dict:
        """Get server statistics"""
        return {
            **self.stats,
            'lobbies': len(self.lobbies),
            'games': len(self.games),
            'tournaments': len(self.tournaments),
            'authenticated': len(self.authenticated_clients)
        }

class NetworkClient:
    """Network client for connecting to the chess server"""
    
    def __init__(self, server_address: str = 'ws://localhost:8765'):
        self.server_address = server_address
        self.websocket = None
        self.connected = False
        self.authenticated = False
        self.client_id = None
        self.token = None
        self.username = None
        
        # Message handling
        self.message_handlers = {}
        self.message_queue = queue.Queue()
        self.receive_thread = None
        self.running = False
        
        # Callbacks
        self.connection_callbacks = []
        self.message_callbacks = []
        
    def connect(self) -> bool:
        """Connect to server"""
        try:
            self.running = True
            self.receive_thread = threading.Thread(target=self._run_receiver, daemon=True)
            self.receive_thread.start()
            
            # Wait for connection
            import time
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
                
            return self.connected
        except Exception as e:
            print(f"Connection error: {e}")
            return False
            
    def _run_receiver(self):
        """Run the receiver loop"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        loop.run_until_complete(self._connect_and_receive())
        
    async def _connect_and_receive(self):
        """Connect and receive messages"""
        try:
            self.websocket = await websockets.connect(self.server_address)
            self.connected = True
            self._notify_callbacks('connected', {})
            
            # Receive messages
            async for message in self.websocket:
                try:
                    msg = NetworkMessage.from_json(message)
                    await self._process_received_message(msg)
                except Exception as e:
                    print(f"Error processing received message: {e}")
                    
        except Exception as e:
            print(f"Connection lost: {e}")
            self.connected = False
            self._notify_callbacks('disconnected', {})
            
    async def _process_received_message(self, message: NetworkMessage):
        """Process received message"""
        # Handle authentication response
        if message.type == MessageType.AUTH:
            payload = message.payload
            if payload.get('success'):
                self.authenticated = True
                self.token = payload.get('token')
                self.username = payload.get('username')
                self._notify_callbacks('authenticated', {'username': self.username})
                
        # Handle game messages
        elif message.type == MessageType.GAME_START:
            self._notify_callbacks('game_start', message.payload)
        elif message.type == MessageType.MOVE:
            self._notify_callbacks('game_move', message.payload)
        elif message.type == MessageType.GAME_END:
            self._notify_callbacks('game_end', message.payload)
            
        # Handle chat
        elif message.type == MessageType.CHAT:
            self._notify_callbacks('chat', message.payload)
            
        # Handle errors
        elif message.type == MessageType.ERROR:
            self._notify_callbacks('error', message.payload)
            
        # Store client_id
        if message.type == MessageType.CONNECT:
            self.client_id = message.payload.get('client_id')
            
        # Call generic message handlers
        for callback in self.message_callbacks:
            try:
                callback(message)
            except Exception as e:
                print(f"Message callback error: {e}")
                
    def send_message(self, message: NetworkMessage):
        """Send a message to server"""
        if not self.connected or not self.websocket:
            return False
            
        try:
            # Add authentication if available
            if self.token:
                message.sender_id = self.client_id
                
            # Send asynchronously
            asyncio.run(self._send_async(message))
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
            
    async def _send_async(self, message: NetworkMessage):
        """Send message asynchronously"""
        if self.websocket:
            await self.websocket.send(message.to_json())
            
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with server"""
        message = NetworkMessage(
            type=MessageType.AUTH,
            payload={'username': username, 'password': password}
        )
        self.username = username
        return self.send_message(message)
        
    def create_game(self, config: Dict = None) -> bool:
        """Create a new game"""
        message = NetworkMessage(
            type=MessageType.CREATE_GAME,
            payload={'config': config or {}}
        )
        return self.send_message(message)
        
    def join_game(self, game_id: str) -> bool:
        """Join an existing game"""
        message = NetworkMessage(
            type=MessageType.JOIN_GAME,
            payload={'game_id': game_id}
        )
        return self.send_message(message)
        
    def send_move(self, game_id: str, move: str) -> bool:
        """Send a move to server"""
        message = NetworkMessage(
            type=MessageType.MOVE,
            payload={'move': move},
            game_id=game_id
        )
        return self.send_message(message)
        
    def send_chat(self, message: str, target: str = None) -> bool:
        """Send a chat message"""
        msg = NetworkMessage(
            type=MessageType.CHAT,
            payload={'message': message},
            target_id=target
        )
        return self.send_message(msg)
        
    def get_profile(self, username: str = None) -> bool:
        """Get user profile"""
        message = NetworkMessage(
            type=MessageType.PROFILE_GET,
            payload={'username': username or self.username}
        )
        return self.send_message(message)
        
    def add_connection_callback(self, callback: Callable):
        """Add connection callback"""
        self.connection_callbacks.append(callback)
        
    def add_message_callback(self, callback: Callable):
        """Add message callback"""
        self.message_callbacks.append(callback)
        
    def _notify_callbacks(self, event: str, data: Dict):
        """Notify callbacks"""
        for callback in self.connection_callbacks:
            try:
                callback(event, data)
            except Exception as e:
                print(f"Callback error: {e}")
                
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.websocket:
            try:
                asyncio.run(self.websocket.close())
            except:
                pass
        self.connected = False
        
    def is_connected(self) -> bool:
        """Check if connected"""
        return self.connected
        
    def is_authenticated(self) -> bool:
        """Check if authenticated"""
        return self.authenticated