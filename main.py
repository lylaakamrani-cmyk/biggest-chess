# © 2025 AmirAli Kamrani. All rights reserved.
# main.py
# Chess Master Pro - Main Entry Point

import sys
import os
import time
import threading
from datetime import datetime

# ============================================
# تنظیم مسیر برای Pydroid / Android
# ============================================
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# ============================================
# Imports
# ============================================
try:
    # Core modules
    from core.board import BoardState
    from core.game_logic import GameLogic, GameConfig, GameMode
    from core.ai_engine import AIEngine, AIDifficulty
    from core.stockfish_engine import StockfishEngine
    from core.network import NetworkClient, NetworkServer
    from core.database import Database
    from core.profile import UserProfile
    from core.elo import EloCalculator, EloSystem
    from core.cloud import CloudSync
    from core.tournament import Tournament, TournamentType
    from core.analysis import GameAnalysis
    from core.replay import GameReplay
    
    # Utils modules
    from utils.config import ConfigManager
    from utils.assets import AssetManager
    from utils.sounds import SoundManager
    from utils.logger import Logger
    from utils.security import SecurityManager
    
    print("✅ All modules imported successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n📁 Please check folder structure:")
    print("   /storage/emulated/0/biggest chess/")
    print("   ├── main.py")
    print("   ├── core/")
    print("   │   ├── __init__.py")
    print("   │   └── ...")
    print("   └── utils/")
    print("       ├── __init__.py")
    print("       └── ...")
    sys.exit(1)

# ============================================
# کلاس اصلی برنامه
# ============================================
class ChessMasterPro:
    """برنامه اصلی Chess Master Pro"""
    
    def __init__(self):
        self.running = True
        self.is_online = False
        self.current_user = None
        
        # Initialize components
        self.config = None
        self.logger = None
        self.db = None
        self.security = None
        self.assets = None
        self.sounds = None
        
        # Game components
        self.game = None
        self.ai = None
        self.stockfish = None
        self.elo = None
        self.profile = None
        self.analysis = None
        self.replay = None
        self.cloud = None
        self.network = None
        self.tournament = None
        
        self._init_components()
        
    def _init_components(self):
        """راه‌اندازی تمام کامپوننت‌ها"""
        print("\n" + "=" * 60)
        print("♟️  CHESS MASTER PRO v1.0")
        print("=" * 60)
        
        # 1. Logger
        print("\n📝 Initializing Logger...")
        try:
            self.logger = Logger()
            self.logger.info("Application starting...")
            print("   ✅ Logger ready!")
        except Exception as e:
            print(f"   ⚠️ Logger error: {e}")
            self.logger = None
            
        # 2. Config
        print("\n📋 Loading Configuration...")
        try:
            self.config = ConfigManager()
            print("   ✅ Config loaded!")
        except Exception as e:
            print(f"   ❌ Config error: {e}")
            self.config = None
            
        # 3. Security
        print("\n🔐 Initializing Security...")
        try:
            self.security = SecurityManager()
            print("   ✅ Security ready!")
        except Exception as e:
            print(f"   ⚠️ Security error: {e}")
            self.security = None
            
        # 4. Assets
        print("\n🖼️  Loading Assets...")
        try:
            self.assets = AssetManager()
            print("   ✅ Assets ready!")
        except Exception as e:
            print(f"   ⚠️ Assets error: {e}")
            self.assets = None
            
        # 5. Sounds
        print("\n🔊 Loading Sounds...")
        try:
            self.sounds = SoundManager(self.assets)
            print("   ✅ Sounds ready!")
        except Exception as e:
            print(f"   ⚠️ Sounds error: {e}")
            self.sounds = None
            
        # 6. Database
        print("\n💾 Connecting to Database...")
        try:
            self.db = Database("data/chess_data.db")
            print("   ✅ Database connected!")
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            self.db = None
            
        # 7. Profile
        print("\n👤 Loading Profile...")
        try:
            if self.db:
                self.profile = UserProfile(self.db)
                print("   ✅ Profile system ready!")
            else:
                print("   ⚠️ Profile system disabled (no database)")
        except Exception as e:
            print(f"   ⚠️ Profile error: {e}")
            self.profile = None
            
        # 8. ELO System
        print("\n📈 Initializing ELO System...")
        try:
            self.elo = EloCalculator(EloSystem.STANDARD)
            print("   ✅ ELO system ready!")
        except Exception as e:
            print(f"   ⚠️ ELO error: {e}")
            self.elo = None
            
        # 9. AI Engine
        print("\n🤖 Initializing AI Engine...")
        try:
            self.ai = AIEngine()
            self.ai.set_difficulty(AIDifficulty.MEDIUM)
            print("   ✅ AI engine ready!")
        except Exception as e:
            print(f"   ❌ AI error: {e}")
            self.ai = None
            
        # 10. Stockfish Engine
        print("\n🔧 Initializing Stockfish Engine...")
        try:
            self.stockfish = StockfishEngine()
            if self.stockfish and self.stockfish.is_ready:
                print("   ✅ Stockfish engine ready!")
            else:
                print("   ⚠️ Stockfish engine not found (optional)")
        except Exception as e:
            print(f"   ⚠️ Stockfish error: {e}")
            self.stockfish = None
            
        # 11. Game Logic
        print("\n🎮 Initializing Game Logic...")
        try:
            game_config = GameConfig()
            self.game = GameLogic(game_config)
            print("   ✅ Game logic ready!")
        except Exception as e:
            print(f"   ❌ Game error: {e}")
            self.game = None
            
        # 12. Analysis
        print("\n📊 Initializing Analysis System...")
        try:
            self.analysis = GameAnalysis(self.stockfish)
            print("   ✅ Analysis system ready!")
        except Exception as e:
            print(f"   ⚠️ Analysis error: {e}")
            self.analysis = None
            
        # 13. Replay
        print("\n🎬 Initializing Replay System...")
        try:
            self.replay = GameReplay()
            print("   ✅ Replay system ready!")
        except Exception as e:
            print(f"   ⚠️ Replay error: {e}")
            self.replay = None
            
        # 14. Cloud Sync
        print("\n☁️  Initializing Cloud Sync...")
        try:
            self.cloud = CloudSync()
            print("   ✅ Cloud sync ready!")
        except Exception as e:
            print(f"   ⚠️ Cloud error: {e}")
            self.cloud = None
            
        # 15. Network
        print("\n🌐 Initializing Network...")
        try:
            self.network = NetworkClient()
            print("   ✅ Network client ready!")
        except Exception as e:
            print(f"   ⚠️ Network error: {e}")
            self.network = None
            
        # 16. Tournament
        print("\n🏆 Initializing Tournament System...")
        try:
            if self.db and self.elo:
                self.tournament = Tournament(self.db, self.elo)
                print("   ✅ Tournament system ready!")
            else:
                print("   ⚠️ Tournament system disabled (requires db & elo)")
        except Exception as e:
            print(f"   ⚠️ Tournament error: {e}")
            self.tournament = None
            
        # 17. Show status
        self._show_status()
        
    def _show_status(self):
        """نمایش وضعیت سیستم"""
        print("\n" + "=" * 60)
        print("📊 SYSTEM STATUS")
        print("=" * 60)
        
        components = [
            ("Config", self.config),
            ("Logger", self.logger),
            ("Security", self.security),
            ("Assets", self.assets),
            ("Sounds", self.sounds),
            ("Database", self.db),
            ("Profile", self.profile),
            ("ELO", self.elo),
            ("AI Engine", self.ai),
            ("Stockfish", self.stockfish and self.stockfish.is_ready),
            ("Game Logic", self.game),
            ("Analysis", self.analysis),
            ("Replay", self.replay),
            ("Cloud", self.cloud),
            ("Network", self.network),
            ("Tournament", self.tournament)
        ]
        
        for name, status in components:
            if isinstance(status, bool):
                icon = "✅" if status else "❌"
            else:
                icon = "✅" if status is not None else "❌"
            print(f"   {icon} {name}")
            
        print("=" * 60)
        
        if self.db and self.profile:
            print("\n👤 Default Users:")
            print("   - admin / admin")
            print("   - guest / guest")
            print("   - player1 / player1")
            print("   - player2 / player2")
            
    # ============================================
    # مدیریت کاربر
    # ============================================
    
    def login(self, username: str, password: str) -> bool:
        """ورود کاربر"""
        if not self.db or not self.profile:
            print("❌ Database not available")
            return False
            
        user = self.db.authenticate_user(username, password)
        if user:
            self.current_user = user
            self.profile.load_profile(user['id'])
            print(f"✅ Welcome back, {username}!")
            self.logger.info(f"User logged in: {username}")
            return True
        else:
            print("❌ Invalid username or password")
            return False
            
    def logout(self):
        """خروج کاربر"""
        if self.current_user:
            username = self.current_user['username']
            self.current_user = None
            print(f"👋 Goodbye, {username}!")
            self.logger.info(f"User logged out: {username}")
            
    def register(self, username: str, password: str, email: str = None) -> bool:
        """ثبت نام کاربر جدید"""
        if not self.db:
            print("❌ Database not available")
            return False
            
        user_id = self.db.create_user(username, password, email)
        if user_id:
            print(f"✅ User '{username}' registered successfully!")
            self.logger.info(f"New user registered: {username}")
            return self.login(username, password)
        else:
            print("❌ Username already exists")
            return False
            
    # ============================================
    # بازی
    # ============================================
    
    def start_local_game(self):
        """شروع بازی محلی"""
        if not self.game:
            print("❌ Game logic not available")
            return
            
        print("\n🎮 Starting local game...")
        self.game.start_game(GameMode.LOCAL)
        print("   ✅ Game started!")
        print("   👤 White: Player 1")
        print("   👤 Black: Player 2")
        self._show_game_status()
        
    def start_ai_game(self, difficulty: str = "medium"):
        """شروع بازی با AI"""
        if not self.game or not self.ai:
            print("❌ Game or AI not available")
            return
            
        # تنظیم سطح AI
        levels = {
            "beginner": AIDifficulty.BEGINNER,
            "easy": AIDifficulty.EASY,
            "medium": AIDifficulty.MEDIUM,
            "hard": AIDifficulty.HARD,
            "expert": AIDifficulty.EXPERT,
            "master": AIDifficulty.MASTER
        }
        
        ai_level = levels.get(difficulty.lower(), AIDifficulty.MEDIUM)
        self.ai.set_difficulty(ai_level)
        
        print(f"\n🤖 Starting AI game (Level: {difficulty})...")
        self.game.start_game(GameMode.AI)
        print("   ✅ Game started!")
        print("   👤 White: You")
        print(f"   🤖 Black: AI ({difficulty})")
        self._show_game_status()
        
    def start_online_game(self):
        """شروع بازی آنلاین"""
        if not self.game or not self.network:
            print("❌ Game or Network not available")
            return
            
        if not self.network.is_connected():
            print("🔗 Connecting to server...")
            if self.network.connect():
                print("   ✅ Connected!")
            else:
                print("   ❌ Connection failed!")
                return
                
        print("\n🌐 Starting online game...")
        self.game.start_game(GameMode.ONLINE)
        print("   ✅ Game started!")
        self._show_game_status()
        
    def _show_game_status(self):
        """نمایش وضعیت بازی"""
        if self.game:
            status = self.game.get_game_state()
            print("\n📊 Game Status:")
            print(f"   Status: {status.get('status', 'unknown')}")
            print(f"   Turn: {status.get('current_player', 'unknown')}")
            print(f"   Moves: {status.get('move_count', 0)}")
            
    # ============================================
    # تحلیل
    # ============================================
    
    def analyze_game(self):
        """تحلیل بازی"""
        if not self.game or not self.analysis:
            print("❌ Analysis not available")
            return
            
        if not self.game.board or not self.game.board.move_history:
            print("⚠️ No game to analyze")
            return
            
        print("\n📊 Analyzing game...")
        result = self.analysis.analyze_game(self.game.board)
        
        if result:
            print("\n📈 Analysis Results:")
            print(f"   Accuracy: {result['stats']['accuracy']:.1f}%")
            print(f"   White Accuracy: {result['stats']['white_accuracy']:.1f}%")
            print(f"   Black Accuracy: {result['stats']['black_accuracy']:.1f}%")
            print(f"   Blunders: {result['stats']['blunders_count']}")
            print(f"   Mistakes: {result['stats']['mistakes_count']}")
            print(f"   Inaccuracies: {result['stats']['inaccuracies_count']}")
            print(f"   Best Moves: {result['stats']['best_move_percentage']:.1f}%")
        else:
            print("❌ Analysis failed")
            
    # ============================================
    # تورنمنت
    # ============================================
    
    def create_tournament(self, name: str, max_players: int = 8, rounds: int = 3):
        """ایجاد تورنمنت"""
        if not self.tournament:
            print("❌ Tournament system not available")
            return
            
        if not self.current_user:
            print("⚠️ Please login first")
            return
            
        print(f"\n🏆 Creating tournament: {name}")
        config = {
            'max_players': max_players,
            'rounds': rounds,
            'time_control': '10+0',
            'rated': True
        }
        
        tournament_id = self.tournament.create_tournament(name, config)
        if tournament_id:
            print(f"   ✅ Tournament created! ID: {tournament_id}")
            self.tournament.register_player(
                self.current_user['id'],
                self.current_user['username'],
                self.current_user['rating']
            )
            print("   ✅ You joined the tournament!")
        else:
            print("   ❌ Failed to create tournament")
            
    def join_tournament(self, tournament_id: str):
        """پیوستن به تورنمنت"""
        if not self.tournament:
            print("❌ Tournament system not available")
            return
            
        if not self.current_user:
            print("⚠️ Please login first")
            return
            
        success = self.tournament.join_tournament(tournament_id, self.current_user['id'])
        if success:
            print("✅ Joined tournament!")
        else:
            print("❌ Failed to join tournament")
            
    # ============================================
    # پشتیبان
    # ============================================
    
    def backup_database(self):
        """پشتیبان‌گیری از دیتابیس"""
        if not self.db:
            print("❌ Database not available")
            return
            
        try:
            from data.backup import DatabaseBackup
            backup = DatabaseBackup()
            file = backup.backup()
            print(f"✅ Backup created: {file}")
        except ImportError:
            print("⚠️ Backup module not available")
            print("   Running manual backup...")
            import shutil
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"data/backups/chess_data_{timestamp}.db"
            shutil.copy2("data/chess_data.db", backup_file)
            print(f"✅ Backup created: {backup_file}")
            
    # ============================================
    # منو
    # ============================================
    
    def show_menu(self):
        """نمایش منوی اصلی"""
        print("\n" + "=" * 60)
        print("♟️  CHESS MASTER PRO - MAIN MENU")
        print("=" * 60)
        
        if self.current_user:
            print(f"👤 User: {self.current_user['username']} (Rating: {self.current_user['rating']})")
        else:
            print("👤 User: Guest")
            
        print("\n📋 Menu:")
        print("   1. 🎮 Local Game")
        print("   2. 🤖 Play vs AI")
        print("   3. 🌐 Online Game")
        print("   4. 📊 Analyze Game")
        print("   5. 🏆 Tournament")
        print("   6. 📈 My Profile")
        print("   7. 🛒 Shop")
        print("   8. ⚙️  Settings")
        print("   9. 💾 Backup Database")
        print("   10. 👤 Login/Register")
        print("   11. ❌ Exit")
        print("-" * 60)
        
        choice = input("👉 Enter your choice (1-11): ").strip()
        
        return choice
        
    def run(self):
        """حلقه اصلی برنامه"""
        while self.running:
            choice = self.show_menu()
            
            if choice == '1':
                self.start_local_game()
                
            elif choice == '2':
                print("\n🤖 AI Difficulty Levels:")
                print("   1. Beginner")
                print("   2. Easy")
                print("   3. Medium")
                print("   4. Hard")
                print("   5. Expert")
                print("   6. Master")
                diff_choice = input("👉 Select difficulty (1-6): ").strip()
                
                levels = {
                    '1': 'beginner',
                    '2': 'easy',
                    '3': 'medium',
                    '4': 'hard',
                    '5': 'expert',
                    '6': 'master'
                }
                
                diff = levels.get(diff_choice, 'medium')
                self.start_ai_game(diff)
                
            elif choice == '3':
                self.start_online_game()
                
            elif choice == '4':
                self.analyze_game()
                
            elif choice == '5':
                print("\n🏆 Tournament Menu:")
                print("   1. Create Tournament")
                print("   2. Join Tournament")
                tourn_choice = input("👉 Select (1-2): ").strip()
                
                if tourn_choice == '1':
                    name = input("📝 Tournament name: ").strip()
                    max_players = int(input("👥 Max players (4-16): ").strip() or 8)
                    rounds = int(input("🔄 Number of rounds: ").strip() or 3)
                    self.create_tournament(name, max_players, rounds)
                elif tourn_choice == '2':
                    tourn_id = input("📝 Tournament ID: ").strip()
                    self.join_tournament(tourn_id)
                    
            elif choice == '6':
                self.show_profile()
                
            elif choice == '7':
                self.show_shop()
                
            elif choice == '8':
                self.show_settings()
                
            elif choice == '9':
                self.backup_database()
                
            elif choice == '10':
                self.show_auth_menu()
                
            elif choice == '11':
                print("\n👋 Goodbye!")
                self.running = False
                
            else:
                print("\n❌ Invalid choice. Please try again.")
                
            if self.running:
                input("\n⏎ Press Enter to continue...")
                
    def show_profile(self):
        """نمایش پروفایل"""
        if not self.profile or not self.current_user:
            print("⚠️ Please login first")
            return
            
        profile_data = self.profile.get_profile_data()
        stats = self.profile.get_user_statistics()
        
        print("\n" + "=" * 60)
        print("👤 USER PROFILE")
        print("=" * 60)
        print(f"   Username: {profile_data['user']['username']}")
        print(f"   Rating: {profile_data['user']['rating']}")
        print(f"   Rank: {profile_data['rank']['name']} ({profile_data['rank']['icon']})")
        print(f"   Level: {stats['level']['level']}")
        print(f"   Coins: {profile_data['user']['total_coins']}")
        print("\n📊 Statistics:")
        print(f"   Games: {stats['overall']['games_played']}")
        print(f"   Wins: {stats['overall']['wins']}")
        print(f"   Losses: {stats['overall']['losses']}")
        print(f"   Draws: {stats['overall']['draws']}")
        print(f"   Win Rate: {stats['overall']['win_rate']:.1f}%")
        print(f"   Best Streak: {stats['streaks']['best']}")
        print("=" * 60)
        
    def show_shop(self):
        """نمایش فروشگاه"""
        if not self.db:
            print("❌ Shop not available")
            return
            
        items = self.db.get_shop_items()
        
        print("\n" + "=" * 60)
        print("🛒 SHOP")
        print("=" * 60)
        print(f"💰 Your coins: {self.current_user['total_coins'] if self.current_user else 0}")
        print("-" * 60)
        
        for i, item in enumerate(items, 1):
            rarity = item.get('rarity', 'common')
            print(f"   {i}. {item['name']} ({rarity})")
            print(f"      💰 {item['price']} coins - {item['description']}")
            
        print("=" * 60)
        
    def show_settings(self):
        """نمایش تنظیمات"""
        print("\n" + "=" * 60)
        print("⚙️  SETTINGS")
        print("=" * 60)
        
        settings = self.config.get_all() if self.config else {}
        
        print(f"   Board Theme: {settings.get('board', {}).get('theme', 'classic')}")
        print(f"   Piece Theme: {settings.get('board', {}).get('piece_theme', 'classic')}")
        print(f"   Sound: {'On' if settings.get('sound', {}).get('enabled', True) else 'Off'}")
        print(f"   AI Level: {settings.get('ai', {}).get('difficulty', 'medium')}")
        print(f"   Time Control: {settings.get('game', {}).get('time_control', '10+0')}")
        print("=" * 60)
        
    def show_auth_menu(self):
        """نمایش منوی احراز هویت"""
        if self.current_user:
            print(f"\n👤 Currently logged in as: {self.current_user['username']}")
            choice = input("🔓 Logout? (y/n): ").strip().lower()
            if choice == 'y':
                self.logout()
            return
            
        print("\n" + "=" * 60)
        print("🔐 AUTHENTICATION")
        print("=" * 60)
        print("   1. Login")
        print("   2. Register")
        print("   3. Back")
        
        choice = input("👉 Select (1-3): ").strip()
        
        if choice == '1':
            username = input("👤 Username: ").strip()
            password = input("🔑 Password: ").strip()
            self.login(username, password)
        elif choice == '2':
            username = input("👤 Username: ").strip()
            password = input("🔑 Password: ").strip()
            email = input("📧 Email (optional): ").strip() or None
            self.register(username, password, email)
            
    # ============================================
    # Command Line Interface
    # ============================================
    
    def cli_mode(self):
        """حالت خط فرمان برای تست سریع"""
        print("\n🚀 Running in CLI mode...")
        print("Type 'help' for commands, 'exit' to quit\n")
        
        while self.running:
            cmd = input("♟️ > ").strip().lower()
            
            if cmd == 'exit':
                self.running = False
                print("👋 Goodbye!")
                
            elif cmd == 'help':
                print("\nCommands:")
                print("  login <user> <pass>  - Login")
                print("  register <user> <pass> - Register")
                print("  local                - Start local game")
                print("  ai <level>           - Play vs AI")
                print("  analyze              - Analyze game")
                print("  profile              - Show profile")
                print("  backup               - Backup database")
                print("  status               - Show system status")
                print("  exit                 - Exit")
                
            elif cmd.startswith('login '):
                parts = cmd.split()
                if len(parts) >= 3:
                    self.login(parts[1], parts[2])
                else:
                    print("❌ Usage: login <username> <password>")
                    
            elif cmd.startswith('register '):
                parts = cmd.split()
                if len(parts) >= 3:
                    self.register(parts[1], parts[2])
                else:
                    print("❌ Usage: register <username> <password>")
                    
            elif cmd == 'local':
                self.start_local_game()
                
            elif cmd.startswith('ai '):
                parts = cmd.split()
                level = parts[1] if len(parts) > 1 else 'medium'
                self.start_ai_game(level)
                
            elif cmd == 'analyze':
                self.analyze_game()
                
            elif cmd == 'profile':
                self.show_profile()
                
            elif cmd == 'backup':
                self.backup_database()
                
            elif cmd == 'status':
                self._show_status()
                
            elif cmd:
                print(f"❌ Unknown command: {cmd}")
                print("Type 'help' for available commands")

# ============================================
# Main Entry Point
# ============================================
def main():
    """ورودی اصلی برنامه"""
    
    # بررسی وجود دیتابیس
    if not os.path.exists("data/chess_data.db"):
        print("\n⚠️ Database not found!")
        print("Please run 'python run_all.py' or 'python create_database.py' first.")
        
        choice = input("\n🔧 Run setup now? (y/n): ").strip().lower()
        if choice == 'y':
            if os.path.exists("run_all.py"):
                os.system("python run_all.py")
            else:
                print("❌ run_all.py not found. Please run create_database.py manually.")
                return
        else:
            print("❌ Cannot start without database.")
            return
    
    # ایجاد برنامه
    app = ChessMasterPro()
    
    # انتخاب حالت
    print("\n" + "=" * 60)
    print("🎮 SELECT MODE")
    print("=" * 60)
    print("   1. 📱 Interactive Menu Mode")
    print("   2. 💻 Command Line Mode")
    print("   3. 🧪 Test Mode")
    
    choice = input("\n👉 Select (1-3): ").strip()
    
    if choice == '1':
        app.run()
    elif choice == '2':
        app.cli_mode()
    elif choice == '3':
        app.test_mode()
    else:
        print("❌ Invalid choice. Running menu mode...")
        app.run()
        
    print("\n🎉 Thank you for playing Chess Master Pro!")

# ============================================
# Execute
# ============================================
if __name__ == "__main__":
    main()