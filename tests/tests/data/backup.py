# © 2025 AmirAli Kamrani. All rights reserved.

# data/backup.py
import sqlite3
import json
import os
import time
import shutil
from datetime import datetime

class DatabaseBackup:
    """پشتیبان‌گیری از دیتابیس"""
    
    def __init__(self, db_path="data/chess_data.db", backup_dir="data/backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
        
    def backup(self) -> str:
        """ایجاد پشتیبان"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"chess_data_{timestamp}.db")
        
        # کپی فایل
        shutil.copy2(self.db_path, backup_file)
        
        # فشرده‌سازی (اختیاری)
        # import gzip
        # with open(backup_file, 'rb') as f:
        #     with gzip.open(backup_file + '.gz', 'wb') as gz:
        #         shutil.copyfileobj(f, gz)
        
        print(f"✅ Backup created: {backup_file}")
        return backup_file
        
    def backup_to_json(self) -> str:
        """پشتیبان‌گیری به صورت JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"chess_data_{timestamp}.json")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # دریافت همه جداول
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        data = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            data[table] = [dict(row) for row in rows]
            
        conn.close()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
        print(f"✅ JSON backup created: {backup_file}")
        return backup_file
        
    def restore(self, backup_file: str) -> bool:
        """بازگردانی از پشتیبان"""
        if not os.path.exists(backup_file):
            print(f"❌ Backup file not found: {backup_file}")
            return False
            
        # پشتیبان از فایل فعلی
        self.backup()
        
        # بازگردانی
        shutil.copy2(backup_file, self.db_path)
        print(f"✅ Database restored from: {backup_file}")
        return True
        
    def list_backups(self) -> list:
        """لیست پشتیبان‌ها"""
        files = []
        for f in os.listdir(self.backup_dir):
            if f.startswith("chess_data_"):
                path = os.path.join(self.backup_dir, f)
                size = os.path.getsize(path)
                modified = os.path.getmtime(path)
                files.append({
                    'name': f,
                    'path': path,
                    'size': size,
                    'size_mb': size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M:%S")
                })
        return sorted(files, key=lambda x: x['modified'], reverse=True)
        
    def cleanup(self, keep: int = 10):
        """پاک کردن پشتیبان‌های قدیمی"""
        backups = self.list_backups()
        if len(backups) > keep:
            for backup in backups[keep:]:
                os.remove(backup['path'])
                print(f"🗑️ Removed old backup: {backup['name']}")

def main():
    backup = DatabaseBackup()
    
    # ایجاد پشتیبان
    backup.backup()
    backup.backup_to_json()
    
    # نمایش لیست
    print("\n📋 Backup list:")
    for b in backup.list_backups()[:5]:
        print(f"   - {b['name']} ({b['size_mb']:.2f} MB)")

if __name__ == "__main__":
    main()