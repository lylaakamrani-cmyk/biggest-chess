# © 2025 AmirAli Kamrani. All rights reserved.

# ui/__init__.py
from .home import HomeScreen
from .board import BoardScreen
from .login import LoginScreen
from .profile import ProfileScreen
from .shop import ShopScreen
from .settings import SettingsScreen
from .online import OnlineScreen
from .local import LocalScreen
from .widgets import ChessWidgets
from .dialogs import DialogManager

__all__ = [
    'HomeScreen',
    'BoardScreen',
    'LoginScreen',
    'ProfileScreen',
    'ShopScreen',
    'SettingsScreen',
    'OnlineScreen',
    'LocalScreen',
    'ChessWidgets',
    'DialogManager'
]