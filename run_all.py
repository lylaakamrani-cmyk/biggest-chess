# © 2025 AmirAli Kamrani. All rights reserved.
# run_all.py
# Chess Master Pro - Complete Setup
# اجرای همه مراحل نصب و راه‌اندازی به صورت خودکار

import os
import sys
import subprocess
import time

# ============================================
# COLOR CODES
# ============================================
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{'='*60}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{'='*60}")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ️  {text}{RESET}")

def print_step(text):
    print(f"{BLUE}▶ {text}{RESET}")

# ============================================
# STEP 1: CHECK PYTHON
# ============================================
def check_python():
    print_step("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} found")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} is too old. Need Python 3.8+")
        return False

# ============================================
# STEP 2: CREATE DIRECTORIES
# ============================================
def create_directories():
    print_step("Creating directories...")
    dirs = [
        'data',
        'data/backups',
        'logs',
        'assets/images/pieces/white',
        'assets/images/pieces/black',
        'assets/images/backgrounds',
        'assets/images/boards',
        'assets/images/icons',
        'assets/sounds',
        'assets/themes',
        'assets/fonts',
        'assets/stockfish',
        'server',
        'web',
        'tests',
        'docs'
    ]
    
    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
            print_success(f"Created: {d}")
        except Exception as e:
            print_error(f"Failed to create {d}: {e}")
            return False
    return True

# ============================================
# STEP 3: INSTALL REQUIREMENTS
# ============================================
def install_requirements():
    print_step("Installing requirements...")
    
    requirements = [
        'kivy==2.1.0',
        'python-chess==1.9.4',
        'pillow==9.4.0',
        'requests==2.28.2',
        'websockets==10.4',
        'numpy==1.24.1'
    ]
    
    print_info("Installing packages...")
    for package in requirements:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            print_success(f"   {package} installed")
        except Exception as e:
            print_error(f"   Failed to install {package}")
            print_info(f"   Try manually: pip install {package}")
    
    return True

# ============================================
# STEP 4: CREATE DATABASE
# ============================================
def create_database():
    print_step("Creating database...")
    
    if os.path.exists("create_database.py"):
        try:
            subprocess.check_call([sys.executable, 'create_database.py'])
            print_success("Database created successfully!")
            return True
        except Exception as e:
            print_error(f"Failed to create database: {e}")
            return False
    else:
        print_error("create_database.py not found!")
        return False

# ============================================
# STEP 5: INIT DATA
# ============================================
def init_data():
    print_step("Initializing data...")
    
    if os.path.exists("data/init_data.py"):
        try:
            subprocess.check_call([sys.executable, 'data/init_data.py'])
            print_success("Data initialized successfully!")
            return True
        except Exception as e:
            print_error(f"Failed to initialize data: {e}")
            return False
    else:
        print_info("data/init_data.py not found - skipping")
        return True

# ============================================
# STEP 6: BUILD ASSETS
# ============================================
def build_assets():
    print_step("Building assets...")
    
    if os.path.exists("assets/build_assets.py"):
        try:
            subprocess.check_call([sys.executable, 'assets/build_assets.py'])
            print_success("Assets built successfully!")
            return True
        except Exception as e:
            print_error(f"Failed to build assets: {e}")
            return False
    else:
        print_info("assets/build_assets.py not found - skipping")
        return True

# ============================================
# STEP 7: CREATE CONFIG
# ============================================
def create_config():
    print_step("Creating config file...")
    
    import json
    config = {
        "app": {
            "name": "Chess Master Pro",
            "version": "1.0.0",
            "language": "en",
            "dark_mode": False
        },
        "game": {
            "time_control": "10+0",
            "initial_time": 600,
            "increment": 0,
            "rated": True
        },
        "board": {
            "theme": "classic",
            "piece_theme": "classic",
            "show_legal_moves": True,
            "highlight_last_move": True,
            "animation_speed": 300
        },
        "sound": {
            "enabled": True,
            "volume": 70
        },
        "ai": {
            "difficulty": "medium",
            "depth": 4
        },
        "network": {
            "server_url": "ws://localhost:8765"
        }
    }
    
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/config.json", "w") as f:
            json.dump(config, f, indent=2)
        print_success("Config file created: data/config.json")
        return True
    except Exception as e:
        print_error(f"Failed to create config: {e}")
        return False

# ============================================
# STEP 8: CHECK STOCKFISH
# ============================================
def check_stockfish():
    print_step("Checking Stockfish...")
    
    stockfish_paths = [
        "assets/stockfish/stockfish",
        "assets/stockfish/stockfish.exe",
        "assets/stockfish/stockfish_android",
        "stockfish",
        "stockfish.exe"
    ]
    
    found = False
    for path in stockfish_paths:
        if os.path.exists(path):
            print_success(f"Stockfish found: {path}")
            found = True
            break
    
    if not found:
        print_info("Stockfish not found - AI will use built-in engine")
        print_info("Download Stockfish from: https://stockfishchess.org/download/")
    
    return True

# ============================================
# STEP 9: SHOW SUMMARY
# ============================================
def show_summary():
    print_header("SETUP COMPLETE!")
    
    print(f"\n{BOLD}📁 Project Structure:{RESET}")
    print(f"   /storage/emulated/0/Biggest_chess/")
    print(f"   ├── ui/app.py        ← {GREEN}Run this{RESET}")
    print(f"   ├── core/            ← Game logic")
    print(f"   ├── utils/           ← Tools")
    print(f"   ├── data/            ← Database & config")
    print(f"   └── assets/          ← Images & sounds")
    
    print(f"\n{BOLD}🚀 To run the game:{RESET}")
    print(f"   {GREEN}python ui/app.py{RESET}")
    
    print(f"\n{BOLD}👤 Default users:{RESET}")
    print(f"   admin / admin")
    print(f"   guest / guest")
    print(f"   player1 / player1")
    print(f"   player2 / player2")
    
    print(f"\n{BOLD}📚 Documentation:{RESET}")
    print(f"   docs/README.md")
    print(f"   docs/API.md")
    print(f"   docs/USER_GUIDE.md")
    
    print(f"\n{'='*60}")
    print(f"{GREEN}{BOLD}🎉 Chess Master Pro is ready!{RESET}")
    print(f"{'='*60}")

# ============================================
# MAIN
# ============================================
def main():
    print_header("CHESS MASTER PRO - COMPLETE SETUP")
    
    steps = [
        ("Checking Python...", check_python),
        ("Creating directories...", create_directories),
        ("Installing requirements...", install_requirements),
        ("Creating database...", create_database),
        ("Initializing data...", init_data),
        ("Building assets...", build_assets),
        ("Creating config...", create_config),
        ("Checking Stockfish...", check_stockfish),
    ]
    
    failed = []
    
    for step_name, step_func in steps:
        print_header(step_name)
        try:
            if step_func():
                print_success(f"{step_name} Done!")
            else:
                print_error(f"{step_name} Failed!")
                failed.append(step_name)
        except Exception as e:
            print_error(f"{step_name} Error: {e}")
            failed.append(step_name)
        time.sleep(0.5)
    
    print_header("SETUP SUMMARY")
    
    if failed:
        print_error(f"❌ {len(failed)} steps failed:")
        for f in failed:
            print(f"   - {f}")
        print_info("Try running individual scripts manually.")
    else:
        print_success("✅ All steps completed successfully!")
        show_summary()
    
    print("\n")
    return len(failed) == 0

# ============================================
# EXECUTE
# ============================================
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)