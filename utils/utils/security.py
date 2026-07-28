# © 2025 AmirAli Kamrani. All rights reserved.

# utils/security.py - نسخه ساده بدون cryptography
import hashlib
import secrets
import time
import json
import os
import base64
from typing import Optional, Dict, Any

class SecurityManager:
    """مدیریت امنیت و رمزنگاری (نسخه ساده - بدون نیاز به کتابخانه خارجی)"""
    
    def __init__(self, key_file: str = ".secret.key"):
        self.key_file = key_file
        self.key = None
        self._load_or_create_key()
        
    def _load_or_create_key(self):
        """بارگذاری یا ایجاد کلید"""
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, 'r') as f:
                    self.key = f.read()
            except:
                self._create_key()
        else:
            self._create_key()
            
    def _create_key(self):
        """ایجاد کلید جدید"""
        self.key = secrets.token_hex(32)
        try:
            with open(self.key_file, 'w') as f:
                f.write(self.key)
        except:
            pass
            
    def encrypt(self, data: Any) -> str:
        """رمزنگاری ساده"""
        if isinstance(data, dict):
            data = json.dumps(data)
        elif not isinstance(data, str):
            data = str(data)
            
        # رمزنگاری ساده با XOR
        key_bytes = self.key.encode() if self.key else b'default_key_12345'
        data_bytes = data.encode()
        
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            
        return base64.b64encode(bytes(encrypted)).decode()
        
    def decrypt(self, encrypted_data: str) -> Any:
        """رمزگشایی ساده"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            key_bytes = self.key.encode() if self.key else b'default_key_12345'
            
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
                
            result = decrypted.decode()
            
            # تلاش برای تبدیل به JSON
            try:
                return json.loads(result)
            except:
                return result
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
            
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """هش کردن رمز عبور با Salt"""
        if salt is None:
            salt = secrets.token_hex(16)
            
        combined = salt + password
        password_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        return password_hash, salt
        
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """تایید رمز عبور"""
        computed_hash, _ = self.hash_password(password, salt)
        return computed_hash == password_hash
        
    def generate_token(self, length: int = 32) -> str:
        """تولید توکن امن"""
        return secrets.token_hex(length)
        
    def generate_otp(self, length: int = 6) -> str:
        """تولید کد یکبار مصرف"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
        
    def validate_input(self, data: str, max_length: int = 1000) -> bool:
        """اعتبارسنجی ورودی"""
        if len(data) > max_length:
            return False
            
        # جلوگیری از تزریق
        dangerous = ['<script>', 'javascript:', 'onclick', 'onerror', 'alert(']
        for item in dangerous:
            if item in data.lower():
                return False
                
        return True
        
    def sanitize_filename(self, filename: str) -> str:
        """پاکسازی نام فایل"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:255]
        
    def secure_delete(self, file_path: str, passes: int = 3):
        """حذف امن فایل"""
        if not os.path.exists(file_path):
            return
            
        try:
            with open(file_path, 'wb') as f:
                size = f.seek(0, 2)
                f.seek(0)
                
                for _ in range(passes):
                    f.write(secrets.token_bytes(size))
                    f.seek(0)
                    
            os.remove(file_path)
        except:
            try:
                os.remove(file_path)
            except:
                pass
                
    def encrypt_file(self, input_path: str, output_path: str = None):
        """رمزنگاری فایل"""
        if output_path is None:
            output_path = input_path + '.enc'
            
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = f.read()
                
            encrypted = self.encrypt(data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(encrypted)
        except Exception as e:
            print(f"Encrypt file error: {e}")
            
    def decrypt_file(self, input_path: str, output_path: str = None):
        """رمزگشایی فایل"""
        if output_path is None:
            output_path = input_path.replace('.enc', '')
            
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                encrypted = f.read()
                
            decrypted = self.decrypt(encrypted)
            
            if decrypted is not None:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(str(decrypted))
        except Exception as e:
            print(f"Decrypt file error: {e}")