# assets/build_assets.py
import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_PATH = '/storage/emulated/0/Biggest_chess/assets/'
PIECES_PATH = os.path.join(ASSETS_PATH, 'images/pieces/')

def create_directories():
    """ساخت پوشه‌های مورد نیاز"""
    dirs = [
        PIECES_PATH + 'white/',
        PIECES_PATH + 'black/',
        ASSETS_PATH + 'images/backgrounds/',
        ASSETS_PATH + 'images/boards/',
        ASSETS_PATH + 'images/icons/',
        ASSETS_PATH + 'sounds/',
        ASSETS_PATH + 'themes/',
        ASSETS_PATH + 'fonts/',
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f'✅ Created: {d}')

def create_piece_images():
    """ساخت تصاویر مهره‌ها با PIL"""
    pieces = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']
    colors = ['white', 'black']
    size = 80
    
    unicode_pieces = {
        'king': '♔',
        'queen': '♕',
        'rook': '♖',
        'bishop': '♗',
        'knight': '♘',
        'pawn': '♙'
    }
    
    for color in colors:
        for piece in pieces:
            path = os.path.join(PIECES_PATH, color, f'{piece}.png')
            
            # ساخت تصویر
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # رنگ مهره
            if color == 'white':
                fill_color = (255, 255, 255, 255)
                bg_color = (240, 240, 240, 255)
                outline_color = (200, 200, 200, 255)
                text_color = (0, 0, 0, 255)
            else:
                fill_color = (0, 0, 0, 255)
                bg_color = (30, 30, 30, 255)
                outline_color = (50, 50, 50, 255)
                text_color = (255, 255, 255, 255)
            
            # رسم دایره پس‌زمینه
            draw.ellipse([5, 5, size-5, size-5], fill=bg_color, outline=outline_color)
            
            # رسم نماد مهره
            try:
                font = ImageFont.truetype("/system/fonts/NotoSansSymbols-Regular.ttf", size-20)
            except:
                try:
                    font = ImageFont.truetype(os.path.join(ASSETS_PATH, 'fonts/chess.ttf'), size-20)
                except:
                    font = ImageFont.load_default()
            
            draw.text((size//2 - 20, size//2 - 25), unicode_pieces.get(piece, '?'), 
                     fill=text_color, font=font)
            
            img.save(path)
            print(f'✅ Created: {path}')

def create_backgrounds():
    """ساخت تصاویر پس‌زمینه"""
    bg_path = ASSETS_PATH + 'images/backgrounds/'
    backgrounds = {
        'wooden.jpg': (139, 90, 43),
        'dark.jpg': (20, 20, 30),
        'gradient.jpg': None,
        'chess_pattern.jpg': None
    }
    
    size = (512, 512)
    
    for name, color in backgrounds.items():
        path = os.path.join(bg_path, name)
        if name == 'wooden.jpg':
            img = Image.new('RGB', size, color)
            draw = ImageDraw.Draw(img)
            for i in range(0, size[0], 20):
                draw.line([(i, 0), (i, size[1])], fill=(100, 70, 30, 50), width=2)
        elif name == 'dark.jpg':
            img = Image.new('RGB', size, (10, 10, 20))
        elif name == 'gradient.jpg':
            img = Image.new('RGB', size)
            for y in range(size[1]):
                r = int(30 + (y / size[1]) * 100)
                g = int(30 + (y / size[1]) * 80)
                b = int(60 + (y / size[1]) * 120)
                for x in range(size[0]):
                    img.putpixel((x, y), (r, g, b))
        elif name == 'chess_pattern.jpg':
            img = Image.new('RGB', size, (50, 50, 50))
            draw = ImageDraw.Draw(img)
            square_size = 64
            for i in range(0, size[0], square_size):
                for j in range(0, size[1], square_size):
                    if (i // square_size + j // square_size) % 2 == 0:
                        draw.rectangle([i, j, i+square_size, j+square_size], fill=(80, 80, 80))
        else:
            continue
        
        img.save(path, quality=85)
        print(f'✅ Created: {path}')

def create_icons():
    """ساخت آیکون‌ها"""
    icons_path = ASSETS_PATH + 'images/icons/'
    icons = {
        'settings.png': '⚙️',
        'profile.png': '👤',
        'friends.png': '👥',
        'shop.png': '🛒',
        'home.png': '🏠',
        'chess_icon.png': '♟️',
        'notification.png': '🔔',
        'trophy.png': '🏆',
        'logo.png': '♔'
    }
    
    size = 64
    
    for name, symbol in icons.items():
        path = os.path.join(icons_path, name)
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # پس‌زمینه
        draw.ellipse([5, 5, size-5, size-5], fill=(60, 60, 90, 200))
        
        # نماد
        try:
            font = ImageFont.truetype("/system/fonts/NotoSansSymbols-Regular.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        draw.text((size//2 - 15, size//2 - 15), symbol, fill=(255, 255, 255, 255), font=font)
        img.save(path)
        print(f'✅ Created: {path}')

def create_themes():
    """ساخت فایل‌های تم"""
    themes_path = ASSETS_PATH + 'themes/'
    themes = {
        'classic.json': {'name': 'Classic', 'colors': {'light': '#F0D9B5', 'dark': '#B58863'}},
        'dark.json': {'name': 'Dark', 'colors': {'light': '#779952', 'dark': '#446633'}},
        'neon.json': {'name': 'Neon', 'colors': {'light': '#00FFAA', 'dark': '#003322'}},
        'blue.json': {'name': 'Blue', 'colors': {'light': '#4A90D9', 'dark': '#2C5F8A'}},
        'green.json': {'name': 'Green', 'colors': {'light': '#90EE90', 'dark': '#228B22'}},
    }
    
    import json
    for name, theme in themes.items():
        path = os.path.join(themes_path, name)
        with open(path, 'w') as f:
            json.dump(theme, f, indent=2)
        print(f'✅ Created: {path}')

def create_sounds():
    """ساخت فایل‌های صوتی خالی"""
    sounds_path = ASSETS_PATH + 'sounds/'
    sounds = ['move.wav', 'capture.wav', 'check.wav', 'win.wav', 'lose.wav', 
              'draw.wav', 'start.wav', 'notification.wav', 'click.wav']
    
    for sound in sounds:
        path = os.path.join(sounds_path, sound)
        with open(path, 'wb') as f:
            # RIFF header ساده
            f.write(b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
        print(f'✅ Created: {path}')

def main():
    print('=' * 50)
    print('Building Chess Assets...')
    print('=' * 50)
    
    create_directories()
    create_piece_images()
    create_backgrounds()
    create_icons()
    create_themes()
    create_sounds()
    
    print('\n' + '=' * 50)
    print('✅ All assets created successfully!')
    print('=' * 50)

if __name__ == '__main__':
    main()