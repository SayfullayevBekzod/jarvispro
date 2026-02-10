import json
import os
import sys

# Loyiha yo'lini qo'shish
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis"))

import config

def generate_version_json():
    version_data = {
        "version": config.APP_VERSION,
        "download_url": f"https://github.com/SayfullayevBekzod/jarvispro/releases/download/v{config.APP_VERSION}/JarvisPro_v{config.APP_VERSION.replace('.', '_')}.exe",
        "changelog": "Yangi versiya avtomatik ravishda GitHub Actions orqali yuklandi."
    }
    
    with open("version.json", "w") as f:
        json.dump(version_data, f, indent=4)
    print(f"version.json yaratildi: v{config.APP_VERSION}")

if __name__ == "__main__":
    generate_version_json()
