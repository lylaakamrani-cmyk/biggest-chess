# © 2025 AmirAli Kamrani. All rights reserved.
import os

# متن کپی‌رایت
COPYRIGHT = "# © 2025 AmirAli Kamrani. All rights reserved.\n\n"

# پوشه‌هایی که باید اسکن بشن (همون ساختار پروژه‌ات)
FOLDERS = [
    "core",
    "ui",
    "utils",
    "server",
    "web",
    "data",
    "logs",
    "tests",
    "docs",
    "assets"
]

def add_copyright_to_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # اگه کپی‌رایت قبلاً اضافه شده، دوباره اضافه نکن
    if "© 2025 AmirAli Kamrani" in content:
        return
    
    # کپی‌رایت رو به اول فایل اضافه کن
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(COPYRIGHT + content)

def main():
    for folder in FOLDERS:
        if not os.path.exists(folder):
            continue
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".py"):   # فقط فایل‌های پایتون
                    path = os.path.join(root, file)
                    add_copyright_to_file(path)
                    print(f"✅ {path}")

if __name__ == "__main__":
    main()