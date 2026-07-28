// © 2025 AmirAli Kamrani. All rights reserved.
class ChessWebApp {
    constructor() {
        this.board = null;
        this.selectedSquare = null;
        this.gameState = {
            fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            turn: 'white',
            moves: [],
            moveHistory: [],
            selectedPiece: null,
            legalMoves: []
        };
        this.isFlipped = false;
        this.isOnline = false;
        this.ws = null;
        this.currentPage = 'home';
        this.username = 'مهمان';
        this.isAuthenticated = false;
        this.boardElement = document.getElementById('board');
        this.movesList = document.getElementById('moves-list');
        this.statusElement = document.getElementById('game-status');
        
        this.init();
    }
    
    init() {
        this.setupNavigation();
        this.setupBoard();
        this.setupModals();
        this.setupEventListeners();
        this.updateUI();
        this.startClock();
        console.log('♟️ Chess Master Pro Web loaded!');
    }
    
    setupNavigation() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const page = btn.dataset.page;
                this.navigateTo(page);
            });
        });
    }
    
    navigateTo(page) {
        this.currentPage = page;
        
        // Update nav buttons
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        const navBtn = document.querySelector(`.nav-btn[data-page="${page}"]`);
        if (navBtn) navBtn.classList.add('active');
        
        // Update pages
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        const targetPage = document.getElementById(`page-${page}`);
        if (targetPage) targetPage.classList.add('active');
        
        if (page === 'play') {
            this.renderBoard();
        }
    }
    
    setupBoard() {
        this.renderBoard();
    }
    
    renderBoard() {
        const board = document.getElementById('board');
        board.innerHTML = '';
        
        const fen = this.gameState.fen;
        const boardArray = this.fenToArray(fen);
        
        for (let rank = 0; rank < 8; rank++) {
            for (let file = 0; file < 8; file++) {
                const square = document.createElement('div');
                const row = this.isFlipped ? 7 - rank : rank;
                const col = this.isFlipped ? 7 - file : file;
                const squareIndex = row * 8 + col;
                const piece = boardArray[squareIndex];
                
                square.className = `square ${(row + col) % 2 === 0 ? 'light' : 'dark'}`;
                square.dataset.square = `${String.fromCharCode(97 + col)}${8 - row}`;
                square.dataset.index = squareIndex;
                
                if (piece) {
                    square.textContent = this.getPieceSymbol(piece);
                }
                
                if (this.selectedSquare === squareIndex) {
                    square.classList.add('selected');
                }
                
                if (this.gameState.legalMoves.includes(squareIndex)) {
                    square.classList.add('legal-move');
                }
                
                square.addEventListener('click', () => this.onSquareClick(squareIndex));
                board.appendChild(square);
            }
        }
        
        this.updateMoveHistory();
        this.updateStatus();
    }
    
    fenToArray(fen) {
        const board = [];
        const parts = fen.split(' ');
        const rows = parts[0].split('/');
        
        for (const row of rows) {
            for (const char of row) {
                if (isNaN(parseInt(char))) {
                    board.push(char);
                } else {
                    for (let i = 0; i < parseInt(char); i++) {
                        board.push(null);
                    }
                }
            }
        }
        return board;
    }
    
    getPieceSymbol(piece) {
        const symbols = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        };
        return symbols[piece] || piece;
    }
    
    onSquareClick(index) {
        // Simple move simulation
        const piece = this.gameState.fen.split(' ')[0].replace(/\//g, '')[index];
        
        if (this.selectedSquare === null) {
            if (piece && this.isPlayerPiece(piece)) {
                this.selectedSquare = index;
                this.gameState.legalMoves = this.getLegalMoves(index);
                this.renderBoard();
            }
        } else {
            if (index === this.selectedSquare) {
                this.selectedSquare = null;
                this.gameState.legalMoves = [];
                this.renderBoard();
                return;
            }
            
            // Make a move (simplified)
            this.makeMove(this.selectedSquare, index);
            this.selectedSquare = null;
            this.gameState.legalMoves = [];
            this.renderBoard();
        }
    }
    
    isPlayerPiece(piece) {
        if (!piece) return false;
        const turn = this.gameState.turn;
        if (turn === 'white') {
            return piece === piece.toUpperCase();
        } else {
            return piece === piece.toLowerCase();
        }
    }
    
    getLegalMoves(index) {
        // Simplified - in real implementation would use chess.js
        const legalMoves = [];
        const col = index % 8;
        const row = Math.floor(index / 8);
        const piece = this.gameState.fen.split(' ')[0].replace(/\//g, '')[index];
        
        if (!piece) return legalMoves;
        
        const isWhite = piece === piece.toUpperCase();
        const directions = {
            'P': [[-1, 0]],
            'p': [[1, 0]],
            'N': [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]],
            'n': [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]],
            'B': [[1, 1], [1, -1], [-1, 1], [-1, -1]],
            'b': [[1, 1], [1, -1], [-1, 1], [-1, -1]],
            'R': [[0, 1], [0, -1], [1, 0], [-1, 0]],
            'r': [[0, 1], [0, -1], [1, 0], [-1, 0]],
            'Q': [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]],
            'q': [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]],
            'K': [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]],
            'k': [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]]
        };
        
        const pieceDirs = directions[piece] || [];
        
        for (const [dr, dc] of pieceDirs) {
            let r = row + dr;
            let c = col + dc;
            let canContinue = true;
            
            while (r >= 0 && r < 8 && c >= 0 && c < 8 && canContinue) {
                const targetIndex = r * 8 + c;
                const target = this.gameState.fen.split(' ')[0].replace(/\//g, '')[targetIndex];
                
                if (target) {
                    if (this.isPlayerPiece(target) !== this.isPlayerPiece(piece)) {
                        legalMoves.push(targetIndex);
                    }
                    canContinue = false;
                } else {
                    legalMoves.push(targetIndex);
                }
                
                // Stop for non-sliding pieces
                if (['P', 'p', 'N', 'n', 'K', 'k'].includes(piece)) {
                    canContinue = false;
                }
                
                r += dr;
                c += dc;
            }
        }
        
        return legalMoves;
    }
    
    makeMove(from, to) {
        // Simplified move
        const fen = this.gameState.fen;
        const board = fen.split(' ')[0].replace(/\//g, '');
        const boardArray = [...board];
        const piece = boardArray[from];
        
        boardArray[to] = piece;
        boardArray[from] = null;
        
        let newBoard = '';
        for (let i = 0; i < 8; i++) {
            let empty = 0;
            let row = '';
            for (let j = 0; j < 8; j++) {
                const idx = i * 8 + j;
                if (boardArray[idx]) {
                    if (empty > 0) {
                        row += empty;
                        empty = 0;
                    }
                    row += boardArray[idx];
                } else {
                    empty++;
                }
            }
            if (empty > 0) row += empty;
            newBoard += row + (i < 7 ? '/' : '');
        }
        
        const turn = this.gameState.turn === 'white' ? 'black' : 'white';
        this.gameState.fen = `${newBoard} ${turn} - - 0 1`;
        this.gameState.turn = turn;
        
        // Add to history
        const fromSquare = `${String.fromCharCode(97 + from % 8)}${8 - Math.floor(from / 8)}`;
        const toSquare = `${String.fromCharCode(97 + to % 8)}${8 - Math.floor(to / 8)}`;
        this.gameState.moveHistory.push(`${fromSquare}-${toSquare}`);
        
        this.updateUI();
    }
    
    updateUI() {
        this.updateMoveHistory();
        this.updateStatus();
        this.updateTimers();
    }
    
    updateMoveHistory() {
        const movesList = document.getElementById('moves-list');
        movesList.innerHTML = '';
        
        this.gameState.moveHistory.forEach((move, i) => {
            const div = document.createElement('div');
            div.className = `move-item ${i % 2 === 0 ? 'white-move' : 'black-move'}`;
            div.textContent = `${i + 1}. ${move}`;
            movesList.appendChild(div);
        });
    }
    
    updateStatus() {
        const status = document.getElementById('game-status');
        const turn = this.gameState.turn === 'white' ? 'سفید' : 'سیاه';
        status.innerHTML = `<span>⏳ نوبت: ${turn}</span>`;
    }
    
    updateTimers() {
        // Simple timer simulation
        setInterval(() => {
            const whiteTime = document.getElementById('white-time');
            const blackTime = document.getElementById('black-time');
            
            if (whiteTime && blackTime) {
                // Update times (simplified)
            }
        }, 1000);
    }
    
    startClock() {
        // Timer logic
    }
    
    setupModals() {
        // Login modal
        document.getElementById('login-btn').addEventListener('click', () => {
            document.getElementById('login-modal').classList.add('show');
        });
        
        document.getElementById('login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;
            this.login(username, password);
        });
        
        document.getElementById('register-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('register-username').value;
            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;
            this.register(username, email, password);
        });
    }
    
    setupEventListeners() {
        // Close modals
        document.querySelectorAll('.close').forEach(el => {
            el.addEventListener('click', () => {
                el.closest('.modal').classList.remove('show');
            });
        });
        
        // Shop filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.filterShop(btn.dataset.category);
            });
        });
    }
    
    login(username, password) {
        this.username = username;
        this.isAuthenticated = true;
        document.getElementById('username-display').textContent = username;
        document.getElementById('login-modal').classList.remove('show');
        document.getElementById('login-btn').textContent = '🚪 خروج';
        document.getElementById('login-btn').onclick = () => this.logout();
        this.updateProfile();
        console.log(`✅ Logged in as ${username}`);
    }
    
    logout() {
        this.username = 'مهمان';
        this.isAuthenticated = false;
        document.getElementById('username-display').textContent = 'مهمان';
        document.getElementById('login-btn').textContent = 'ورود';
        document.getElementById('login-btn').onclick = () => {
            document.getElementById('login-modal').classList.add('show');
        };
    }
    
    register(username, email, password) {
        console.log(`📝 Registering: ${username}, ${email}`);
        document.getElementById('register-modal').style.display = 'none';
        this.login(username, password);
    }
    
    showRegister() {
        document.getElementById('login-modal').classList.remove('show');
        document.getElementById('register-modal').style.display = 'block';
    }
    
    showLogin() {
        document.getElementById('register-modal').style.display = 'none';
        document.getElementById('login-modal').classList.add('show');
    }
    
    closeLogin() {
        document.getElementById('login-modal').classList.remove('show');
    }
    
    closeRegister() {
        document.getElementById('register-modal').style.display = 'none';
    }
    
    updateProfile() {
        document.getElementById('profile-username').textContent = this.username;
        // Update stats
        document.getElementById('profile-games').textContent = Math.floor(Math.random() * 100);
        document.getElementById('profile-wins').textContent = Math.floor(Math.random() * 50);
        document.getElementById('profile-losses').textContent = Math.floor(Math.random() * 40);
        document.getElementById('profile-draws').textContent = Math.floor(Math.random() * 20);
    }
    
    filterShop(category) {
        // Shop filtering logic
        console.log(`Filtering shop: ${category}`);
    }
    
    // Game actions
    undoMove() {
        if (this.gameState.moveHistory.length > 0) {
            this.gameState.moveHistory.pop();
            this.updateUI();
            this.renderBoard();
        }
    }
    
    redoMove() {
        // Redo logic
    }
    
    resetGame() {
        this.gameState.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
        this.gameState.turn = 'white';
        this.gameState.moveHistory = [];
        this.selectedSquare = null;
        this.gameState.legalMoves = [];
        this.renderBoard();
        this.updateUI();
    }
    
    toggleFlip() {
        this.isFlipped = !this.isFlipped;
        this.renderBoard();
    }
    
    offerDraw() {
        if (confirm('آیا می‌خواهید مساوی پیشنهاد دهید؟')) {
            alert('🤝 پیشنهاد مساوی ارسال شد');
        }
    }
    
    resignGame() {
        if (confirm('آیا مطمئن هستید که می‌خواهید تسلیم شوید؟')) {
            alert('🏳️ شما تسلیم شدید');
        }
    }
    
    // Online functions
    connectOnline() {
        this.isOnline = !this.isOnline;
        const status = document.getElementById('connection-status');
        if (this.isOnline) {
            status.textContent = '✅ متصل';
            status.style.color = '#4caf50';
            document.querySelector('.online-actions .btn-primary').textContent = '🔌 قطع';
            this.simulateOnlinePlayers();
        } else {
            status.textContent = '📡 قطع';
            status.style.color = '#ff4444';
            document.querySelector('.online-actions .btn-primary').textContent = '🔗 اتصال';
        }
    }
    
    createGame() {
        if (!this.isOnline) {
            alert('لطفاً ابتدا به سرور متصل شوید');
            return;
        }
        alert('🎮 بازی جدید ایجاد شد!');
    }
    
    simulateOnlinePlayers() {
        const players = ['Ali_Chess', 'Master_Mind', 'Queen_Gambit', 'Rook_Rider', 'Knight_Fury'];
        const list = document.getElementById('online-players-list');
        list.innerHTML = '';
        players.forEach(p => {
            const div = document.createElement('div');
            div.className = 'player-item';
            div.innerHTML = `<span>${p}</span><span>🟢 آنلاین</span>`;
            list.appendChild(div);
        });
    }
    
    saveSettings() {
        const settings = {
            boardTheme: document.getElementById('board-theme').value,
            pieceTheme: document.getElementById('piece-theme').value,
            darkMode: document.getElementById('dark-mode').checked,
            soundEnabled: document.getElementById('sound-enabled').checked,
            soundVolume: document.getElementById('sound-volume').value,
            aiLevel: document.getElementById('ai-level').value,
            timeControl: document.getElementById('time-control').value
        };
        
        console.log('💾 Settings saved:', settings);
        alert('✅ تنظیمات ذخیره شد!');
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    const app = new ChessWebApp();
    window.app = app;
    
    // Make functions globally accessible
    window.navigateTo = (page) => app.navigateTo(page);
    window.undoMove = () => app.undoMove();
    window.redoMove = () => app.redoMove();
    window.resetGame = () => app.resetGame();
    window.toggleFlip = () => app.toggleFlip();
    window.offerDraw = () => app.offerDraw();
    window.resignGame = () => app.resignGame();
    window.connectOnline = () => app.connectOnline();
    window.createGame = () => app.createGame();
    window.saveSettings = () => app.saveSettings();
    window.showRegister = () => app.showRegister();
    window.showLogin = () => app.showLogin();
    window.closeLogin = () => app.closeLogin();
    window.closeRegister = () => app.closeRegister();
    window.login = (u, p) => app.login(u, p);
});