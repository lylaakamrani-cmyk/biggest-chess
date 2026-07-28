# utils/sounds.py
import os
import json
from enum import Enum
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

class SoundType(Enum):
    MOVE = "move"
    CAPTURE = "capture"
    CHECK = "check"
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
    START = "start"
    NOTIFICATION = "notification"
    CLICK = "click"
    TIMER = "timer"
    GAME_OVER = "game_over"
    PROMOTION = "promotion"
    CASTLE = "castle"
    EN_PASSANT = "en_passant"

class SoundManager:
    """
    مدیریت صداها با Kivy Core Audio
    بدون وابستگی به Pygame یا SimpleAudio
    """
    
    def __init__(self, assets_manager=None, config_path=None):
        self.assets_manager = assets_manager
        self.config_path = config_path or "data/sound_config.json"
        self.sounds = {}
        self.loading = False
        self.enabled = True
        self.volume = 0.7
        self.muted = False
        
        # لیست صداهای بارگذاری شده
        self.loaded_sounds = []
        
        # بارگذاری تنظیمات
        self._load_config()
        
        # بارگذاری صداها
        self._load_sounds()
        
    # ========== CONFIGURATION ==========
    
    def _load_config(self):
        """بارگذاری تنظیمات صدا از فایل"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.enabled = config.get('enabled', True)
                    self.volume = config.get('volume', 0.7)
                    self.muted = config.get('muted', False)
                print(f"✅ Sound config loaded: {self.config_path}")
            except Exception as e:
                print(f"⚠️ Failed to load sound config: {e}")
        else:
            self._save_config()
            
    def _save_config(self):
        """ذخیره تنظیمات صدا در فایل"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump({
                    'enabled': self.enabled,
                    'volume': self.volume,
                    'muted': self.muted
                }, f, indent=2)
            print(f"✅ Sound config saved: {self.config_path}")
        except Exception as e:
            print(f"⚠️ Failed to save sound config: {e}")
            
    # ========== LOADING ==========
    
    def _load_sounds(self):
        """بارگذاری همه صداها"""
        if self.loading:
            return
            
        self.loading = True
        self.sounds.clear()
        self.loaded_sounds.clear()
        
        print("🔊 Loading sounds...")
        
        for sound_type in SoundType:
            path = self._get_sound_path(sound_type)
            if os.path.exists(path):
                try:
                    sound = SoundLoader.load(path)
                    if sound:
                        self.sounds[sound_type] = sound
                        self.loaded_sounds.append(sound_type.value)
                        print(f"   ✅ Loaded: {sound_type.value}")
                    else:
                        print(f"   ⚠️ Failed to load: {sound_type.value}")
                except Exception as e:
                    print(f"   ❌ Error loading {sound_type.value}: {e}")
            else:
                print(f"   ⚠️ File not found: {path}")
                
        self.loading = False
        print(f"🔊 Loaded {len(self.loaded_sounds)} sounds")
        
    def _get_sound_path(self, sound_type: SoundType) -> str:
        """دریافت مسیر فایل صوتی"""
        if self.assets_manager:
            return self.assets_manager.get_sound_path(sound_type.value)
        
        # مسیر پیش‌فرض
        base_path = os.path.join("assets", "sounds")
        return os.path.join(base_path, f"{sound_type.value}.wav")
        
    def reload(self):
        """بارگذاری مجدد صداها"""
        self._load_sounds()
        
    # ========== PLAYBACK ==========
    
    def play(self, sound_type: SoundType, volume: float = None, loop: bool = False):
        """
        پخش صدا
        
        Args:
            sound_type: نوع صدا
            volume: بلندی صدا (0.0 تا 1.0)
            loop: پخش تکرار شونده
        """
        if not self.enabled or self.muted:
            return
            
        if sound_type not in self.sounds:
            print(f"⚠️ Sound not loaded: {sound_type.value}")
            return
            
        try:
            sound = self.sounds[sound_type]
            vol = volume if volume is not None else self.volume
            sound.volume = vol
            sound.loop = loop
            sound.play()
            return sound
        except Exception as e:
            print(f"❌ Play sound error ({sound_type.value}): {e}")
            return None
            
    def play_async(self, sound_type: SoundType, volume: float = None, delay: float = 0):
        """پخش صدا با تاخیر (غیرهمزمان)"""
        if delay > 0:
            Clock.schedule_once(lambda dt: self.play(sound_type, volume), delay)
        else:
            self.play(sound_type, volume)
            
    def stop(self, sound_type: SoundType):
        """توقف یک صدا"""
        if sound_type in self.sounds:
            try:
                self.sounds[sound_type].stop()
            except:
                pass
                
    def stop_all(self):
        """توقف همه صداها"""
        for sound in self.sounds.values():
            try:
                sound.stop()
            except:
                pass
                
    def is_playing(self, sound_type: SoundType) -> bool:
        """بررسی اینکه صدا در حال پخش است"""
        if sound_type in self.sounds:
            try:
                return self.sounds[sound_type].state == 'play'
            except:
                pass
        return False
        
    def get_duration(self, sound_type: SoundType) -> float:
        """دریافت طول صدا (ثانیه)"""
        if sound_type in self.sounds:
            try:
                return self.sounds[sound_type].length
            except:
                pass
        return 0.0
        
    # ========== VOLUME & MUTE ==========
    
    def set_volume(self, volume: float):
        """تنظیم بلندی صدا"""
        self.volume = max(0, min(1, volume))
        self._save_config()
        
    def get_volume(self) -> float:
        """دریافت بلندی صدا"""
        return self.volume
        
    def set_enabled(self, enabled: bool):
        """فعال/غیرفعال کردن صدا"""
        self.enabled = enabled
        if not enabled:
            self.stop_all()
        self._save_config()
        
    def is_enabled(self) -> bool:
        """بررسی فعال بودن صدا"""
        return self.enabled
        
    def toggle_mute(self):
        """روشن/خاموش کردن صدا"""
        self.muted = not self.muted
        if self.muted:
            self.stop_all()
        self._save_config()
        
    def is_muted(self) -> bool:
        """بررسی خاموش بودن صدا"""
        return self.muted
        
    # ========== SHORTCUT METHODS ==========
    
    def play_move(self):
        """صدای حرکت"""
        self.play(SoundType.MOVE)
        
    def play_capture(self):
        """صدای گرفتن مهره"""
        self.play(SoundType.CAPTURE)
        
    def play_check(self):
        """صدای کیش"""
        self.play(SoundType.CHECK)
        
    def play_win(self):
        """صدای برد"""
        self.play(SoundType.WIN)
        
    def play_lose(self):
        """صدای باخت"""
        self.play(SoundType.LOSE)
        
    def play_draw(self):
        """صدای مساوی"""
        self.play(SoundType.DRAW)
        
    def play_start(self):
        """صدای شروع بازی"""
        self.play(SoundType.START)
        
    def play_notification(self):
        """صدای اعلان"""
        self.play(SoundType.NOTIFICATION)
        
    def play_click(self):
        """صدای کلیک"""
        self.play(SoundType.CLICK)
        
    def play_timer(self):
        """صدای تایمر"""
        self.play(SoundType.TIMER)
        
    def play_game_over(self):
        """صدای پایان بازی"""
        self.play(SoundType.GAME_OVER)
        
    def play_promotion(self):
        """صدای ترفیع مهره"""
        self.play(SoundType.PROMOTION)
        
    def play_castle(self):
        """صدای قلعه"""
        self.play(SoundType.CASTLE)
        
    def play_en_passant(self):
        """صدای آن پاسان"""
        self.play(SoundType.EN_PASSANT)
        
    # ========== UTILITY ==========
    
    def get_loaded_sounds(self) -> list:
        """دریافت لیست صداهای بارگذاری شده"""
        return self.loaded_sounds.copy()
        
    def get_all_sound_types(self) -> list:
        """دریافت لیست همه انواع صداها"""
        return [st.value for st in SoundType]
        
    def get_sound_info(self) -> dict:
        """دریافت اطلاعات صداها"""
        info = {
            'total': len(SoundType),
            'loaded': len(self.loaded_sounds),
            'enabled': self.enabled,
            'muted': self.muted,
            'volume': self.volume,
            'sounds': self.loaded_sounds
        }
        return info
        
    def test_sound(self):
        """تست صدا"""
        print("🔊 Testing sounds...")
        for sound_type in SoundType:
            self.play(sound_type)
            import time
            time.sleep(0.2)
        print("✅ Test complete")