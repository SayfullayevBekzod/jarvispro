import sys
import os
import time

# Loyiha yo'lini qo'shish
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "jarvis"))

from jarvis.core.speech import muxlisa

# Redirect stdout/stderr to file
sys.stdout = open("tts_debug_utf8.log", "w", encoding="utf-8")
sys.stderr = sys.stdout

print("Testing SpeechEngine module integration...")
result = muxlisa.text_to_speech("Salom, bu test.", lambda: print("Callback called!"))
print(f"Result: {result}")

# Keep main thread alive to allow daemon threads to finish
time.sleep(5)
print("Done.")
