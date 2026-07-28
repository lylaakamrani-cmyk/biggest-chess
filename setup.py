# setup.py - اجرای همه کارها با هم
import os
import sys

def run_all():
    print("=" * 60)
    print("🚀 Chess Master Pro - Setup")
    print("=" * 60)
    
    # 1. ایجاد دیتابیس
    print("\n📊 Step 1: Creating database...")
    os.system("python create_database.py")
    
    # 2. پر کردن داده‌ها
    print("\n📊 Step 2: Initializing data...")
    os.system("python data/init_data.py")
    
    # 3. ایجاد پشتیبان
    print("\n📊 Step 3: Creating backup...")
    os.system("python data/backup.py")
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print("\n📁 Files created:")
    print("   - data/chess_data.db")
    print("   - data/config.json")
    print("   - data/.secret.key")
    print("   - data/backups/")

if __name__ == "__main__":
    run_all()