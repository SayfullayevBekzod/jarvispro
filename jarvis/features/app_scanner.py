"""
App Scanner - O'rnatilgan dasturlarni avtomatik aniqlash
"""

import os
import glob
import json
import winreg
from typing import Dict, List, Optional
from pathlib import Path


class AppScanner:
    """Windows dasturlarini avtomatik aniqlash"""
    
    def __init__(self):
        self.apps_cache_file = os.path.join(os.path.dirname(__file__), "..", "data", "apps_cache.json")
        self.common_apps = {
            # Brauzerlar
            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],
            "firefox": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            ],
            "edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ],
            "opera": [
                r"C:\Users\{user}\AppData\Local\Programs\Opera\launcher.exe",
            ],
            "brave": [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Users\{user}\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe",
            ],
            
            # Messenjerlar
            "telegram": [
                r"C:\Users\{user}\AppData\Roaming\Telegram Desktop\Telegram.exe",
                r"C:\Program Files\Telegram Desktop\Telegram.exe",
            ],
            "unigram": [
                r"C:\Users\{user}\AppData\Local\Programs\Unigram\Unigram.exe",
                r"C:\Program Files\Unigram\Unigram.exe",
            ],
            "whatsapp": [
                r"C:\Users\{user}\AppData\Local\WhatsApp\WhatsApp.exe",
            ],
            "discord": [
                r"C:\Users\{user}\AppData\Local\Discord\Update.exe",
            ],
            "skype": [
                r"C:\Program Files\Microsoft\Skype for Desktop\Skype.exe",
                r"C:\Users\{user}\AppData\Local\Microsoft\Skype\Skype.exe",
            ],
            
            # Unumdorlik va Ish
            "zoom": [
                r"C:\Users\{user}\AppData\Roaming\Zoom\bin\Zoom.exe",
            ],
            "teams": [
                r"C:\Users\{user}\AppData\Local\Microsoft\Teams\current\Teams.exe",
            ],
            "obsidian": [
                r"C:\Users\{user}\AppData\Local\Obsidian\Obsidian.exe",
            ],
            "anydesk": [
                r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe",
            ],
            
            # Kod redaktorlari
            "vscode": [
                r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                r"C:\Program Files\Microsoft VS Code\Code.exe",
            ],
            "sublime": [
                r"C:\Program Files\Sublime Text\sublime_text.exe",
                r"C:\Program Files\Sublime Text 3\sublime_text.exe",
            ],
            "notepad++": [
                r"C:\Program Files\Notepad++\notepad++.exe",
                r"C:\Program Files (x86)\Notepad++\notepad++.exe",
            ],
            "pycharm": [
                r"C:\Program Files\JetBrains\PyCharm*\bin\pycharm64.exe",
            ],
            
            # Office
            "word": [
                r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
            ],
            "excel": [
                r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
            ],
            "powerpoint": [
                r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
            ],
            
            # Media
            "vlc": [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            ],
            "spotify": [
                r"C:\Users\{user}\AppData\Roaming\Spotify\Spotify.exe",
            ],
            
            # O'yinlar / Platformalar
            "steam": [
                r"C:\Program Files (x86)\Steam\steam.exe",
                r"C:\Program Files\Steam\steam.exe",
            ],
            "epic games": [
                r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe",
            ],
            
            # Tizim
            "notepad": ["notepad.exe"],
            "bloknot": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "kalkulyator": ["calc.exe"],
            "paint": ["mspaint.exe"],
            "cmd": ["cmd.exe"],
            "terminal": ["wt.exe", "cmd.exe"],
            "powershell": ["powershell.exe"],
        }
        
        # URI protokollari (Deep Links)
        self.app_uris = {
            "spotify": "spotify:",
            "discord": "discord:",
            "telegram": "tg:",
            "unigram": "tg:",
            "whatsapp": "whatsapp:",
            "skype": "skype:",
            "calculator": "calculator:",
            "mail": "outlookmail:",
            "calendar": "outlookcal:",
            "store": "ms-windows-store:",
            "settings": "ms-settings:",
            "weather": "bingweather:",
            "maps": "bingmaps:",
        }
        
        self.username = os.environ.get("USERNAME", "")
    
    def scan_apps(self) -> Dict[str, str]:
        """Barcha dasturlarni skanerlash"""
        found_apps = {}
        
        # 1. Common app paths
        username = os.getlogin()
        for app_name, paths in self.common_apps.items():
            for path in paths:
                real_path = path.replace("{user}", username).replace("{username}", username)
                if "*" in real_path:
                    try:
                        matches = glob.glob(real_path)
                        if matches:
                            found_apps[app_name] = matches[0]
                            break
                    except:
                        continue
                elif os.path.exists(real_path):
                    found_apps[app_name] = real_path
                    break
        
        # 2. URI protokollarini qo'shish
        for app_name, uri in self.app_uris.items():
            if app_name not in found_apps:
                found_apps[app_name] = uri
        
        # 3. Start Menu'dan qidirish
        start_menu_apps = self._scan_start_menu()
        for app_name, path in start_menu_apps.items():
            if app_name.lower() not in found_apps:
                found_apps[app_name.lower()] = path
        
        # 4. UWP (Microsoft Store) dasturlarini qidirish
        uwp_apps = self._scan_uwp_apps()
        for app_name, path in uwp_apps.items():
            if app_name.lower() not in found_apps:
                found_apps[app_name.lower()] = path
        
        return found_apps

    def scan_urls(self) -> Dict[str, str]:
        """Foydali URL'larni aniqlash"""
        return {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "telegram": "https://web.telegram.org",
            "kundalik": "https://kundalik.com",
            "myuzb": "https://my.gov.uz",
            "lex": "https://lex.uz",
            "zamin": "https://zamin.uz",
            "kun": "https://kun.uz",
            "daryo": "https://daryo.uz",
            "chatgpt": "https://chat.openai.com",
            "github": "https://github.com",
        }

    def _scan_uwp_apps(self) -> Dict[str, str]:
        """Microsoft Store (UWP) dasturlarini aniqlash"""
        uwp_apps = {}
        try:
            # shell:AppsFolder orqali barcha appslarni ko'rish mumkin
            # Lekin Python orqali registry ko'proq ishonchli
            reg_path = r"Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        pkg_name = winreg.EnumKey(key, i)
                        # Bu yerda package nomidan qisqa nomni chiqarish kerak
                        # Masalan: Microsoft.WindowsCalculator -> calculator
                        name = pkg_name.split('_')[0].split('.')[-1].lower()
                        if name:
                            # UWP ilovalarni 'shell:AppsFolder\PackageFamilyName!App' orqali ochish mumkin
                            # Lekin hozircha oddiyroq usul - shell command
                            uwp_apps[name] = f"shell:AppsFolder\\{pkg_name}!App"
                    except:
                        continue
        except:
            pass
        return uwp_apps
    
    def _scan_start_menu(self) -> Dict[str, str]:
        """Start Menu shortcut'larini skanerlash"""
        apps = {}
        
        # Start Menu yo'llari
        start_menu_paths = [
            os.path.join(os.environ.get("ProgramData", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
        ]
        
        for start_path in start_menu_paths:
            if os.path.exists(start_path):
                for root, dirs, files in os.walk(start_path):
                    for file in files:
                        if file.endswith(".lnk"):
                            app_name = file[:-4]  # .lnk ni olib tashlash
                            lnk_path = os.path.join(root, file)
                            
                            # .lnk fayldan exe yo'lini olish mumkin, lekin murakkab
                            # Shunchaki shortcut nomini saqlaymiz
                            apps[app_name] = lnk_path
        
        return apps
    
    def save_cache(self, apps: Dict[str, str]):
        """Topilgan dasturlarni cache'ga saqlash"""
        os.makedirs(os.path.dirname(self.apps_cache_file), exist_ok=True)
        with open(self.apps_cache_file, "w", encoding="utf-8") as f:
            json.dump(apps, f, indent=2, ensure_ascii=False)
        print(f"[App Scanner] {len(apps)} ta dastur saqlandi")
    
    def load_cache(self) -> Optional[Dict[str, str]]:
        """Cache'dan o'qish"""
        if os.path.exists(self.apps_cache_file):
            try:
                with open(self.apps_cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def get_apps(self, rescan: bool = False) -> Dict[str, str]:
        """Dasturlar ro'yxatini olish"""
        if not rescan:
            cached = self.load_cache()
            if cached:
                return cached
        
        apps = self.scan_apps()
        self.save_cache(apps)
        return apps


# Global instance
app_scanner = AppScanner()
