import re
import os

def bump_patch_version():
    config_path = os.path.join("jarvis", "config.py")
    if not os.path.exists(config_path):
        print(f"Xato: {config_path} topilmadi.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # APP_VERSION = "1.0.0" qatorini qidirish
    pattern = r'APP_VERSION\s*=\s*"(\d+)\.(\d+)\.(\d+)"'
    match = re.search(pattern, content)
    
    if match:
        major, minor, patch = map(int, match.groups())
        new_patch = patch + 1
        new_version = f"{major}.{minor}.{new_patch}"
        
        # O'zgartirish
        new_content = re.sub(pattern, f'APP_VERSION = "{new_version}"', content)
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"Versiya yangilandi: {major}.{minor}.{patch} -> {new_version}")
        return new_version
    else:
        print("Xato: APP_VERSION topilmadi yoki format noto'g'ri.")
        return None

if __name__ == "__main__":
    bump_patch_version()
