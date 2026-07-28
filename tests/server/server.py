# © 2025 AmirAli Kamrani. All rights reserved.

# server/server.py
import asyncio
import json
import websockets
import uuid
import time
from typing import Dict, Set

class ChessServer:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.players: Dict[str, str] = {}  # client_id -> username
        self.games: Dict[str, Dict] = {}   # game_id -> game_data
        self.lobby: Set[str] = set()       # client_id های در لابی
        self.running = False
        
    async def start(self):
        self.running = True
        print(f"🚀 Chess Server starting on {self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"✅ Server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever
            
    async def handle_client(self, websocket, path):
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket
        print(f"🔗 Client {client_id} connected")
        
        try:
            # Send welcome message with client_id
            await websocket.send(json.dumps({
                'type': 'welcome',
                'client_id': client_id,
                'message': 'Connected to Chess Server'
            }))
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(client_id, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON'
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Cleanup
            if client_id in self.clients:
                del self.clients[client_id]
            if client_id in self.players:
                del self.players[client_id]
            if client_id in self.lobby:
                self.lobby.remove(client_id)
            # Remove from games
            for game_id, game in list(self.games.items()):
                if game['white'] == client_id or game['black'] == client_id:
                    del self.games[game_id]
            print(f"🔌 Client {client_id} disconnected")
            await self.broadcast_lobby()
            
    async def process_message(self, client_id: str, data: Dict):
        msg_type = data.get('type')
        
        handlers = {
            'auth': self.handle_auth,
            'join_lobby': self.handle_join_lobby,
            'leave_lobby': self.handle_leave_lobby,
            'create_game': self.handle_create_game,
            'join_game': self.handle_join_game,
            'move': self.handle_move,
            'chat': self.handle_chat,
            'resign': self.handle_resign,
            'draw_offer': self.handle_draw_offer,
            'get_lobby': self.handle_get_lobby,
            'get_games': self.handle_get_games,
            'ping': self.handle_ping
        }
        
        handler = handlers.get(msg_type)
        if handler:
            await handler(client_id, data.get('payload', {}))
        else:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': f'Unknown message type: {msg_type}'
            })
            
    async def handle_auth(self, client_id: str, payload: Dict):
        username = payload.get('username')
        if not username:
            await self.send_to_client(client_id, {
                'type': 'auth_result',
                'success': False,
                'message': 'Username required'
            })
            return
            
        # Check if username already taken
        for cid, name in self.players.items():
            if name == username and cid != client_id:
                await self.send_to_client(client_id, {
                    'type': 'auth_result',
                    'success': False,
                    'message': 'Username already taken'
                })
                return
                
        self.players[client_id] = username
        await self.send_to_client(client_id, {
            'type': 'auth_result',
            'success': True,
            'username': username
        })
        
        # Add to lobby
        self.lobby.add(client_id)
        await self.broadcast_lobby()
        
    async def handle_join_lobby(self, client_id: str, payload: Dict):
        self.lobby.add(client_id)
        await self.broadcast_lobby()
        await self.send_to_client(client_id, {
            'type': 'lobby_joined',
            'message': 'Joined lobby'
        })
        
    async def handle_leave_lobby(self, client_id: str, payload: Dict):
        if client_id in self.lobby:
            self.lobby.remove(client_id)
        await self.broadcast_lobby()
        
    async def handle_create_game(self, client_id: str, payload: Dict):
        if client_id not in self.players:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': 'Please authenticate first'
            })
            return
            
        game_id = str(uuid.uuid4())[:8]
        self.games[game_id] = {
            'id': game_id,
            'white': client_id,
            'black': None,
            'status': 'waiting',
            'created_at': time.time(),
            'time_control': payload.get('time_control', '10+0'),
            'moves': [],
            'result': None,
            'white_time': int(payload.get('time_control', '10+0').split('+')[0]) * 60,
            'black_time': int(payload.get('time_control', '10+0').split('+')[0]) * 60
        }
        
        await self.send_to_client(client_id, {
            'type': 'game_created',
            'game_id': game_id,
            'message': 'Game created! Share this code with opponent.'
        })
        
        await self.broadcast_games()
        
    async def handle_join_game(self, client_id: str, payload: Dict):
        game_id = payload.get('game_id')
        if not game_id or game_id not in self.games:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': 'Game not found'
            })
            return
            
        game = self.games[game_id]
        if game['status'] != 'waiting':
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': 'Game already started'
            })
            return
            
        if game['black']:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': 'Game is full'
            })
            return
            
        # Join as black
        game['black'] = client_id
        game['status'] = 'playing'
        game['started_at'] = time.time()
        
        # Notify both players
        white_name = self.players.get(game['white'], 'White')
        black_name = self.players.get(game['black'], 'Black')
        
        for player_id in [game['white'], game['black']]:
            await self.send_to_client(player_id, {
                'type': 'game_started',
                'game_id': game_id,
                'white': white_name,
                'black': black_name,
                'time_control': game['time_control']
            })
            
        await self.broadcast_games()
        await self.broadcast_lobby()
        
    async def handle_move(self, client_id: str, payload: Dict):
        game_id = payload.get('game_id')
        move = payload.get('move')
        
        if not game_id or game_id not in self.games:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': 'Game not found'
            })
            return
            
        game = self.games[game_id]
        opponent = game['white'] if game['black'] == client_id else game['black']
        
        if opponent and opponent in self.clients:
            # Send move to opponent
            await self.send_to_client(opponent, {
                'type': 'opponent_move',
                'game_id': game_id,
                'move': move
            })
            
        # Store move
        game['moves'].append({
            'player': client_id,
            'move': move,
            'time': time.time()
        })
        
        # Check for game over
        if payload.get('game_over'):
            game['status'] = 'completed'
            game['result'] = payload.get('result')
            await self.broadcast_games()
            
    async def handle_chat(self, client_id: str, payload: Dict):
        game_id = payload.get('game_id')
        message = payload.get('message', '')
        
        if not message:
            return
            
        username = self.players.get(client_id, 'Unknown')
        
        if game_id and game_id in self.games:
            game = self.games[game_id]
            opponent = game['white'] if game['black'] == client_id else game['black']
            
            if opponent and opponent in self.clients:
                await self.send_to_client(opponent, {
                    'type': 'chat_message',
                    'from': username,
                    'message': message,
                    'game_id': game_id
                })
        else:
            # Broadcast to all in lobby
            for cid in self.lobby:
                if cid in self.clients:
                    await self.send_to_client(cid, {
                        'type': 'chat_message',
                        'from': username,
                        'message': message
                    })
                    
    async def handle_resign(self, client_id: str, payload: Dict):
        game_id = payload.get('game_id')
        if not game_id or game_id not in self.games:
            return
            
        game = self.games[game_id]
        opponent = game['white'] if game['black'] == client_id else game['black']
        
        game['status'] = 'completed'
        game['result'] = 'resign'
        
        if opponent and opponent in self.clients:
            await self.send_to_client(opponent, {
                'type': 'opponent_resigned',
                'game_id': game_id
            })
            
        await self.broadcast_games()
        
    async def handle_draw_offer(self, client_id: str, payload: Dict):
        game_id = payload.get('game_id')
        if not game_id or game_id not in self.games:
            return
            
        game = self.games[game_id]
        opponent = game['white'] if game['black'] == client_id else game['black']
        
        if opponent and opponent in self.clients:
            await self.send_to_client(opponent, {
                'type': 'draw_offered',
                'game_id': game_id,
                'from': self.players.get(client_id, 'Unknown')
            })
            
    async def handle_get_lobby(self, client_id: str, payload: Dict):
        players = []
        for cid in self.lobby:
            if cid in self.players:
                players.append(self.players[cid])
                
        await self.send_to_client(client_id, {
            'type': 'lobby_players',
            'players': players
        })
        
    async def handle_get_games(self, client_id: str, payload: Dict):
        games_list = []
        for gid, game in self.games.items():
            if game['status'] == 'waiting':
                games_list.append({
                    'id': gid,
                    'white': self.players.get(game['white'], 'Unknown'),
                    'time_control': game['time_control']
                })
                
        await self.send_to_client(client_id, {
            'type': 'games_list',
            'games': games_list
        })
        
    async def handle_ping(self, client_id: str, payload: Dict):
        await self.send_to_client(client_id, {
            'type': 'pong',
            'timestamp': time.time()
        })
        
    async def send_to_client(self, client_id: str, message: Dict):
        if client_id in self.clients:
            try:
                await self.clients[client_id].send(json.dumps(message))
            except:
                pass
                
    async def broadcast_lobby(self):
        """Broadcast lobby info to all clients"""
        players = []
        for cid in self.lobby:
            if cid in self.players:
                players.append(self.players[cid])
                
        for cid in self.lobby:
            if cid in self.clients:
                await self.send_to_client(cid, {
                    'type': 'lobby_update',
                    'players': players
                })
                
    async def broadcast_games(self):
        """Broadcast game list to all clients"""
        games_list = []
        for gid, game in self.games.items():
            if game['status'] == 'waiting':
                games_list.append({
                    'id': gid,
                    'white': self.players.get(game['white'], 'Unknown'),
                    'time_control': game['time_control']
                })
                
        for cid in self.lobby:
            if cid in self.clients:
                await self.send_to_client(cid, {
                    'type': 'games_list',
                    'games': games_list
                })

def main():
    server = ChessServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == '__main__':
    main()