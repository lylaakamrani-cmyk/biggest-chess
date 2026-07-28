# © 2025 AmirAli Kamrani. All rights reserved.

# utils/sounds.py - نسخه فقط لاگ (بدون خطا)
from enum import Enum
from typing import Optional, Dict, List

class SoundType(Enum):
    MOVE = "move"
    CHECK = "check"
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
    START = "start"
    NOTIFICATION = "notification"
    CLICK = "click"
    TIMER = "timer"

class SoundManager:
    """مدیریت صدا - نسخه لاگ (بدون خطا)"""
    
    def __init__(self, assets_manager=None):
        self.assets_manager = assets_manager
        self.enabled = True
        self.volume = 0.7
        self.sounds = {}
        self.is_playing = False
        print("🔊 SoundManager initialized (log mode)")
        
    def play(self, sound_type: SoundType, volume: float = None):
        """لاگ صدا (بدون پخش واقعی)"""
        if not self.enabled:
            return
        print(f"🔊 Sound: {sound_type.value} (volume: {volume or self.volume})")
        
    def play_move_sound(self):
        self.play(SoundType.MOVE)
        
    def play_check_sound(self):
        self.play(SoundType.CHECK)
        
    def play_win_sound(self):
        self.play(SoundType.WIN)
        
    def play_lose_sound(self):
        self.play(SoundType.LOSE)
        
    def play_draw_sound(self):
        self.play(SoundType.DRAW)
        
    def play_start_sound(self):
        self.play(SoundType.START)
        
    def play_notification(self):
        self.play(SoundType.NOTIFICATION)
        
    def play_click(self):
        self.play(SoundType.CLICK)
        
    def play_timer(self):
        self.play(SoundType.TIMER)
        
    def set_volume(self, volume: float):
        self.volume = max(0, min(1, volume))
        
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        
    def stop_all(self):
        pass
        
    def is_playing_sound(self) -> bool:
        return False
        
    def get_available_sounds(self) -> List[str]:
        return []
        
    def test_sound(self):
        print("🔊 Test sound: OK (log mode)")
        return True
