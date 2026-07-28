import os

COPYRIGHT_PY = "# © 2025 AmirAli Kamrani. All rights reserved.\n\n"
COPYRIGHT_MD = "\n\n---\n\n**Developed by AmirAli Kamrani**  \n© 2025 AmirAli Kamrani. All rights reserved.\n"

FOLDERS = ["core", "ui", "utils", "server", "web", "data", "docs"]

def add_copyright(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "© 2025 AmirAli Kamrani" in content:
        return
    
    if filepath.endswith(".md"):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content + COPYRIGHT_MD)
    elif filepath.endswith((".py", ".js", ".html", ".css", ".kv")):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(COPYRIGHT_PY + content)
    else:
        # فایل‌های دیگه (مثل txt, json) هم می‌تونن شامل بشن
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write("\n# © 2025 AmirAli Kamrani")

    print(f"✅ {filepath}")

def main():
    for folder in FOLDERS:
        if not os.path.exists(folder):
            continue
        for root, _, files in os.walk(folder):
            for file in files:
                path = os.path.join(root, file)
                add_copyright(path)

if __name__ == "__main__":
    main()