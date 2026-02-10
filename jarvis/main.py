"""
Jarvis - O'zbekcha Voice Assistant
Asosiy ishga tushirish fayli
"""

import sys
import os

# Loyiha yo'lini qo'shish
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import main

if __name__ == "__main__":
    print("=" * 50)
    print("  JARVIS - O'zbekcha Voice Assistant")
    print("  Ishga tushirilmoqda...")
    print("=" * 50)
    
    main()
