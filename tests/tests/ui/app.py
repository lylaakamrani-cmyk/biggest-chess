# © 2025 AmirAli Kamrani. All rights reserved.

# ui/app.py
import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.home import HomeScreen
from ui.board import BoardScreen
from ui.login import LoginScreen
from ui.profile import ProfileScreen
from ui.shop import ShopScreen
from ui.settings import SettingsScreen
from ui.online import OnlineScreen
from ui.local import LocalScreen

class ChessApp(App):
    def build(self):
        Window.size = (420, 750)
        Window.clearcolor = (0.08, 0.08, 0.15, 1)
        
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(BoardScreen(name='board'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(ShopScreen(name='shop'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(OnlineScreen(name='online'))
        sm.add_widget(LocalScreen(name='local'))
        
        return sm

def main():
    ChessApp().run()

if __name__ == '__main__':
    main()