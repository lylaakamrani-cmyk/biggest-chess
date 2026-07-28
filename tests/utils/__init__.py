# © 2025 AmirAli Kamrani. All rights reserved.

# utils/__init__.py
"""
ابزارهای کاربردی Chess Master Pro
"""

from utils.config import ConfigManager
from utils.assets import AssetManager
from utils.sounds import SoundManager
from utils.logger import Logger
from utils.security import SecurityManager

__all__ = [
    'ConfigManager',
    'AssetManager',
    'SoundManager',
    'Logger',
    'SecurityManager'
]

# برای سازگاری با روش‌های مختلف import
__version__ = '1.0.0'