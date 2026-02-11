"""
Jarvis Configuration / Sozlamalar
"""

# AI API (Gemini, Whisper, GPT-4 uchun)
# O'zingizning API kalitingizni bu yerga yozing
GEMINI_API_KEY = ""
OPENAI_API_KEY = ""
OPENAI_MODEL = "gpt-4o-mini"
AI_PROVIDER = "gemini" # gemini yoki openai

# AiVOOV API (TTS uchun - ixtiyoriy)
AIVOOV_API_KEY = ""
AIVOOV_TTS_URL = "https://aivoov.com/api/v8/create"
# O'zbek ovozlari:
# Madina (Female Premium): d31025db-828a-460b-ad24-1d44ba6def24
# Sardor (Male Premium): 456d8b4b-9071-4b02-a99a-1eddd22b2880
AIVOOV_VOICE_ID = "456d8b4b-9071-4b02-a99a-1eddd22b2880"  # Sardor - erkak

# Jarvis Sozlamalari
JARVIS_NAME = "Jarvis"
JARVIS_WAKE_WORDS = ["jarvis", "жарвис", "jarvi", "alisa", "алиса", "alica", "джарвис", "jarvisuz", "hello jarvis", "jar", "jori", 'ja']
LANGUAGE = "uz"
APP_VERSION = "1.0.3"
UPDATE_URL = "https://raw.githubusercontent.com/SayfullayevBekzod/jarvispro/main/version.json"
REPO_URL = "https://github.com/SayfullayevBekzod/jarvispro"

# Ovoz Sozlamalari
VOICE_SPEED = 1.0
VOICE_VOLUME = 0.8

# UI Sozlamalari
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
MOBILE_BREAKPOINT = 600  # Mobile rejimga o'tish chegarasi
THEME = "dark"
PRIMARY_COLOR = "#00F5FF"  # Neon Cyan
SECONDARY_COLOR = "#FF00FF" # Neon Magenta
BG_COLOR = "#05050a"       # Deep Space Black
TEXT_COLOR = "#E0E0E0"
NEON_GOLD = "#FFD700"
NEON_GREEN = "#00FF7F"     # Spring Green
GLASS_ALPHA = "0.7"        # UI element opacity hint

# Ob-havo API (OpenWeatherMap - bepul)
WEATHER_API_KEY = ""
DEFAULT_CITY = "Toshkent"

# Dasturlar yo'llari (Windows)
APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "notepad": "notepad.exe",
    "bloknot": "notepad.exe",
    "calculator": "calc.exe",
    "kalkulyator": "calc.exe",
    "telegram": r"C:\Users\{username}\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "vscode": r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vs code": r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
}

# Fayl yo'llari
FOLDERS = {
    "yuklamalar": "Downloads",
    "downloads": "Downloads",
    "hujjatlar": "Documents",
    "documents": "Documents",
    "rasmlar": "Pictures",
    "pictures": "Pictures",
    "musiqa": "Music",
    "music": "Music",
    "video": "Videos",
    "videos": "Videos",
    "ish stoli": "Desktop",
    "desktop": "Desktop",
}
# Avtomatik aniqlash
SCAN_APPS_ENABLED = False  # Foydalanuvchi ruxsatidan keyin True bo'ladi
ALICE_MODE = False        # Alisa rejimini yoqish/o'chirish
