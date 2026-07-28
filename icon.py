from PIL import Image, ImageDraw

# ابعاد آیکون
SIZE = 512
CELL = SIZE // 8

# ایجاد تصویر با پس‌زمینه شفاف
img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# رنگ‌های صفحه شطرنج
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)

# رسم صفحه شطرنج
for r in range(8):
    for c in range(8):
        x1, y1 = c * CELL, r * CELL
        x2, y2 = x1 + CELL, y1 + CELL
        color = LIGHT if (r + c) % 2 == 0 else DARK
        draw.rectangle([x1, y1, x2, y2], fill=color)

# رسم مهره اسب (با اشکال ساده)
cx, cy = SIZE // 2, SIZE // 2 + 20
gray = (60, 60, 60)
silver = (200, 200, 200)

# بدن
draw.ellipse([cx-65, cy-55, cx+65, cy+55], fill=gray, outline=silver, width=3)

# گردن
draw.polygon([
    (cx-25, cy-45), (cx+25, cy-45),
    (cx+45, cy-85), (cx-15, cy-85)
], fill=gray, outline=silver, width=3)

# سر
draw.ellipse([cx-35, cy-100, cx+40, cy-70], fill=gray, outline=silver, width=3)

# گوش
draw.polygon([
    (cx-18, cy-95), (cx-30, cy-112),
    (cx-8, cy-100)
], fill=gray, outline=silver, width=2)

# یال (خطوط)
for i in range(4):
    yy = 75 + i * 10
    draw.arc([cx-55, cy-yy, cx+5, cy-yy+22], 180, 270, fill=(170,170,170), width=3)

# چشم
draw.ellipse([cx+5, cy-90, cx+18, cy-78], fill=(255,255,255))
draw.ellipse([cx+9, cy-87, cx+14, cy-82], fill=(0,0,0))

# سایه نرم زیر اسب (بیضی تیره)
draw.ellipse([cx-70, cy+50, cx+70, cy+75], fill=(0,0,0,80))

# هاله طلایی دور آیکون
draw.ellipse([12, 12, SIZE-12, SIZE-12], outline=(255,215,0,120), width=5)

# ذخیره
img.save('chess_icon.png')
img.save('chess_icon.ico', format='ICO', sizes=[(SIZE, SIZE)])

print("✅ آیکون ساخته شد!")
print("📁 chess_icon.png و chess_icon.ico")