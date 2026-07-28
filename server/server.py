# © 2025 AmirAli Kamrani. All rights reserved.

# server/server.py
import asyncio
import json
import websockets
import uuid
import time

class ChessServer:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.clients = {}
        self.players = {}
        self.games = {}
        self.lobby = set()
        
    async def start(self):
        print(f"Server starting on {self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()
            
    async def handle_client(self, websocket, path):
        client_id = str(uuid.uuid4())[:8]
        self.clients[client_id] = websocket
        print(f"Client {client_id} connected")
        
        await websocket.send(json.dumps({
            'type': 'welcome',
            'client_id': client_id
        }))
        
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process(client_id, data)
        except:
            pass
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
            if client_id in self.players:
                del self.players[client_id]
            if client_id in self.lobby:
                self.lobby.remove(client_id)
            print(f"Client {client_id} disconnected")
            
    async def process(self, client_id, data):
        msg_type = data.get('type')
        payload = data.get('payload', {})
        
        if msg_type == 'auth':
            username = payload.get('username', f'Player{client_id[:4]}')
            self.players[client_id] = username
            self.lobby.add(client_id)
            await self.send(client_id, {'type': 'auth_ok', 'username': username})
            await self.broadcast_lobby()
            
        elif msg_type == 'create_game':
            game_id = str(uuid.uuid4())[:6]
            self.games[game_id] = {
                'id': game_id,
                'white': client_id,
                'black': None,
                'status': 'waiting',
                'moves': []
            }
            await self.send(client_id, {'type': 'game_created', 'game_id': game_id})
            await self.broadcast_games()
            
        elif msg_type == 'join_game':
            game_id = payload.get('game_id')
            if game_id in self.games and self.games[game_id]['status'] == 'waiting':
                self.games[game_id]['black'] = client_id
                self.games[game_id]['status'] = 'playing'
                white = self.games[game_id]['white']
                await self.send(white, {'type': 'game_start', 'game_id': game_id})
                await self.send(client_id, {'type': 'game_start', 'game_id': game_id})
                await self.broadcast_games()
                
        elif msg_type == 'move':
            game_id = payload.get('game_id')
            move = payload.get('move')
            if game_id in self.games:
                game = self.games[game_id]
                opponent = game['white'] if game['black'] == client_id else game['black']
                if opponent in self.clients:
                    await self.send(opponent, {'type': 'opponent_move', 'move': move})
                    
        elif msg_type == 'chat':
            msg = payload.get('message', '')
            for cid in self.lobby:
                if cid != client_id and cid in self.clients:
                    await self.send(cid, {'type': 'chat', 'from': self.players.get(client_id, 'Unknown'), 'msg': msg})
                    
        elif msg_type == 'get_lobby':
            await self.send(client_id, {'type': 'lobby', 'players': [self.players[c] for c in self.lobby if c in self.players]})
            
        elif msg_type == 'get_games':
            waiting = [{'id': gid, 'white': self.players.get(g['white'], 'Unknown')} 
                      for gid, g in self.games.items() if g['status'] == 'waiting']
            await self.send(client_id, {'type': 'games', 'games': waiting})
            
    async def send(self, client_id, data):
        if client_id in self.clients:
            try:
                await self.clients[client_id].send(json.dumps(data))
            except:
                pass
                
    async def broadcast_lobby(self):
        players = [self.players[c] for c in self.lobby if c in self.players]
        for cid in self.lobby:
            if cid in self.clients:
                await self.send(cid, {'type': 'lobby', 'players': players})
                
    async def broadcast_games(self):
        waiting = [{'id': gid, 'white': self.players.get(g['white'], 'Unknown')} 
                  for gid, g in self.games.items() if g['status'] == 'waiting']
        for cid in self.lobby:
            if cid in self.clients:
                await self.send(cid, {'type': 'games', 'games': waiting})

def main():
    server = ChessServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("Server stopped")

if __name__ == '__main__':
    main()