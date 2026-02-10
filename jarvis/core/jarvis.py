"""
Asosiy Jarvis klassi
Barcha funksiyalarni birlashtirib boshqaradi
"""

import os
import subprocess
from typing import Callable, Optional
import threading

from core.commands import parser, CommandType, Command
from core.speech import muxlisa, recorder
from features.general import general
from features.system import system
from features.web import web
from features.media import media
from features.productivity import productivity
from features.ai_chat import ai_chat
from features.smart import smart
from features.keyboard import keyboard
from features.app_scanner import app_scanner
from core.database import db
import config


class Jarvis:
    """Asosiy Jarvis klassi"""
    
    def __init__(self):
        self.name = config.JARVIS_NAME
        self.is_listening = False
        self.is_speaking = False
        self.apps = config.APPS.copy()  # Manual config
        self.folders = config.FOLDERS
        
        # Scan qilingan dasturlarni yuklash
        self._load_scanned_apps()
        
        # Callbacks
        self.on_listening_start: Optional[Callable] = None
        self.on_listening_stop: Optional[Callable] = None
        self.on_speaking_start: Optional[Callable] = None
        self.on_speaking_stop: Optional[Callable] = None
        self.on_text_received: Optional[Callable[[str], None]] = None
        self.on_response: Optional[Callable[[str], None]] = None
        
        # Taymer callback
        productivity.reminder_callback = self._on_reminder
    
    def _load_scanned_apps(self):
        """Skanerlangan dasturlarni yuklash (Bazadan va keshdan)"""
        # 1. Bazadan yuklash (Persistent)
        db_apps = db.get_all_apps()
        if db_apps:
            for name, path in db_apps.items():
                if name not in self.apps:
                    self.apps[name] = path
        
        # 2. JSON keshdan yuklash (Fallback)
        scanned = app_scanner.load_cache()
        if scanned:
            for app_name, path in scanned.items():
                if app_name not in self.apps:
                    self.apps[app_name] = path
    
    def update_app_list(self):
        """Dasturlar va URL'larni yangilash (scan qilish)"""
        print("[Jarvis] Skanerlash boshlandi...")
        
        # Dasturlar
        scanned_apps = app_scanner.scan_apps()
        
        # URL'lar (User ruxsat bergan bo'lsa)
        scanned_urls = app_scanner.scan_urls()
        
        # Hammasini bir joyga yig'ish
        all_detected = {**scanned_apps, **scanned_urls}
        
        # Bazaga saqlash (Persistent)
        db.save_apps(all_detected)
        
        # JSON keshga ham saqlash (Zaxira)
        app_scanner.save_cache(all_detected)
        
        # Qayta yuklash
        for name, path in all_detected.items():
            self.apps[name] = path
            
        print(f"[Jarvis] {len(all_detected)} ta element aniqlandi va bazaga saqlandi.")
        return len(all_detected)
    
    def _on_reminder(self, message: str):
        """Eslatma callback"""
        self.speak(message)
    
    def listen(self):
        """Foydalanuvchi ovozini tinglash"""
        if self.is_listening:
            return
        
        self.is_listening = True
        if self.on_listening_start:
            self.on_listening_start()
        
        # Ovoz yozishni boshlash
        if recorder.start_recording():
            pass  # UI tugmani bossak to'xtaydi
    
    def stop_listening(self) -> Optional[str]:
        """Tinglashni to'xtatish va matnni olish"""
        if not self.is_listening:
            return None
        
        self.is_listening = False
        if self.on_listening_stop:
            self.on_listening_stop()
        
        # Ovoz yozishni to'xtatish
        audio_data = recorder.stop_recording()
        
        if audio_data:
            # Ovozni matnga aylantirish
            text = muxlisa.speech_to_text(audio_data)
            if text and self.on_text_received:
                self.on_text_received(text)
            return text
        
        return None

    def listen_and_execute(self, on_done_callback: Optional[Callable] = None):
        """
        Hands-free rejim: Tinglash -> Bajarish -> Gapirish
        """
        def run():
            if self.on_listening_start:
                self.on_listening_start()
            
            # 1. Silence bo'lguncha eshitish
            audio_data = muxlisa.listen_auto()
            
            if self.on_listening_stop:
                self.on_listening_stop()
                
            if audio_data:
                # 2. Matnga aylantirish
                text = muxlisa.speech_to_text(audio_data)
                
                if text:
                    if self.on_text_received:
                        self.on_text_received(text)
                    
                    # 3. Buyruqni bajarish
                    response = self.process_command(text)
                    
                    # 4. Javobni aytish
                    self.speak(response, on_done_callback)
                    return
            
            # Agar eshitmasa yoki xato bo'lsa
            if on_done_callback:
                on_done_callback()
                
        threading.Thread(target=run, daemon=True).start()
    
    def speak(self, text: str, callback: Optional[Callable] = None):
        """Matnni ovozga aylantirish va gapirish"""
        self.is_speaking = True
        if self.on_speaking_start:
            self.on_speaking_start()
        
        def on_done():
            self.is_speaking = False
            if self.on_speaking_stop:
                self.on_speaking_stop()
            if callback:
                callback()
        
        # Javobni UI ga yuborish
        if self.on_response:
            self.on_response(text)
        
        # Muxlisa orqali gapirish
        muxlisa.text_to_speech(text, on_done)
    
    # Keshlamaslik kerak bo'lgan buyruq turlari (har safar yangi natija beradi)
    DYNAMIC_COMMAND_TYPES = {
        CommandType.SYSTEM, CommandType.SCREENSHOT, CommandType.TIME_DATE,
        CommandType.WEATHER, CommandType.APP_CONTROL, CommandType.FILE_MANAGER,
        CommandType.MEDIA, CommandType.KEYBOARD,
    }
    
    def process_command(self, text: str) -> str:
        """Buyruqni qayta ishlash va javob berish"""
        if not text:
            return "Kechirasiz, eshitmadim."
        
        # 1. Buyruqni tahlil qilish (avval, cache dan oldin)
        command = parser.parse(text)
        
        # 2. Faqat statik buyruqlar uchun bazadan tekshirish
        #    Sistema buyruqlari (ovoz, batareya, ...) har safar yangi bo'lishi kerak
        if command.type not in self.DYNAMIC_COMMAND_TYPES:
            cached_answer = db.get_answer(text)
            if cached_answer:
                print(f"[Jarvis] Bazadan javob topildi: {text}")
                return cached_answer

        # 3. Buyruqni bajarish
        response = self._execute_command(command)
        
        # 4. Aqlli fallback: Faqat haqiqiy savollar uchun internetdan qidirish
        if command.type == CommandType.AI_CHAT:
            search_keywords = ["nima", "qanday", "haqida", "kim", "qayerda", "necha", "qachon", "search", "google", "wikipedia"]
            is_question = any(word in text.lower() for word in search_keywords) or text.strip().endswith("?")
            
            if is_question:
                print(f"[Jarvis] Internetdan qidirilmoqda: {text}")
                web_response = self._handle_internet_search(text)
                if web_response and "topilmadi" not in web_response:
                    response = web_response
        
        # 5. Faqat statik javoblarni saqlash
        if command.type not in self.DYNAMIC_COMMAND_TYPES:
            if response and "tushunmadim" not in response and "xatolik" not in response and "ishlamayapti" not in response:
                db.save_qa(text, response)
            
        return response

    def _handle_internet_search(self, query: str) -> Optional[str]:
        """Internetdan ma'lumot qidirish va javob berish"""
        try:
            # 0. So'rovni tozalash
            cleaned_query = self._clean_text(query)
            
            # 1. Web search orqali content olish
            print(f"[Jarvis] Internetdan qidirilmoqda: {cleaned_query}")
            search_results = web.silent_google_search(cleaned_query)
            
            # 2. To'g'ridan-to'g'ri natijani qaytarish (AI-siz)
            if search_results and "xatolik" not in search_results:
                return search_results
            
            return None
        except Exception as e:
            print(f"[Jarvis] Internet qidiruvida xato: {e}")
            return None
    
    def _execute_command(self, command: Command) -> str:
        """Buyruqni bajarish"""
        
        if command.type == CommandType.GREETING:
            return general.execute(command.action, command.params)
        
        elif command.type == CommandType.TIME_DATE:
            return general.execute(command.action, command.params)
        
        elif command.type == CommandType.EXIT:
            name = "Alisa" if config.ALICE_MODE else config.JARVIS_NAME
            return f"Xayr! {name} o'chmoqda."
        
        elif command.type == CommandType.WEATHER:
            return web.execute(command.action, command.params)
        
        elif command.type == CommandType.APP_CONTROL:
            return self._handle_app_control(command)
        
        elif command.type == CommandType.FILE_MANAGER:
            return self._handle_file_manager(command)
        
        elif command.type == CommandType.WEB_SEARCH:
            if command.action == "app_search":
                return self._handle_app_search(command)
            query = command.params.get("query", "")
            engine = command.params.get("engine", "google")
            if engine == "youtube":
                return web.search_youtube(query)
            elif engine == "wikipedia":
                return web.search_wikipedia(query)
            return web.search_google(query)
        
        elif command.type == CommandType.MATH:
            return productivity.calculate(command.params.get("expression", ""))
        
        elif command.type == CommandType.SYSTEM:
            return system.execute(command.action, command.params)
        
        elif command.type == CommandType.REMINDER:
            return productivity.execute(command.action, command.params)
        
        elif command.type == CommandType.MEDIA:
            if command.action == "youtube_music":
                return web.execute("youtube_music", command.params)
            return media.execute(command.action, command.params)
        
        elif command.type == CommandType.SCREENSHOT:
            return self._take_screenshot()
        
        elif command.type == CommandType.SMART:
            return self._handle_smart(command)
        
        elif command.type == CommandType.SOCIAL:
            return web.execute("social", command.params)
        
        elif command.type == CommandType.KEYBOARD:
            if command.action == "type_in_app":
                return self._handle_type_in_app(command)
            return keyboard.execute(command.action, command.params)
        
        elif command.type == CommandType.AI_CHAT:
            # AI o'chirilgan - buyruqlarni o'zi aniqlaydi
            msg = command.params.get("message", "")
            return f"Kechirasiz, '{msg[:50]}...' buyrug'ini tushunmadim. Mavjud buyruqlar: dastur ochish/yopish, ovoz boshqaruvi, vaqt/sana, ob-havo."
        
        else:
            return "Kechirasiz, tushunmadim. Iltimos, qayta ayting."
    
    def _handle_type_in_app(self, command: Command) -> str:
        """Dastur ichida yozish"""
        app = command.params.get("app", "")
        text = command.params.get("text", "")
        
        if not app:
            return keyboard.execute("type", {"text": text})
            
        # 1. Fokusga keltirish
        focused = system.focus_window(app)
        
        # 2. Yozish
        if focused:
            res = keyboard.execute("type", {"text": text})
            return f"{app.capitalize()} ichiga '{text[:20]}...' yozildi."
        else:
            res = keyboard.execute("type", {"text": text})
            return f"Kechirasiz, '{app}' oynasini topa olmadim, lekin yozishga harakat qildim."

    def _handle_smart(self, command: Command) -> str:
        """Smart buyruqlarni bajarish"""
        action = command.action
        text = command.original_text
        
        if action == "joke":
            return smart.tell_joke()
        elif action == "motivation":
            return smart.motivate()
        elif action == "fact":
            return smart.tell_fact()
        elif action == "coin":
            return smart.flip_coin()
        elif action == "dice":
            return smart.roll_dice()
        elif action == "random":
            return smart.get_random_number()
        elif action == "day_info":
            return smart.get_day_info()
        elif action == "ip":
            return smart.get_ip_info()
        elif action == "password":
            return smart.generate_password()
        elif action == "translate":
            # Matnni ajratib olish
            import re
            translate_text = text
            target_lang = "en"
            if "ruscha" in text.lower() or "rus" in text.lower():
                target_lang = "ru"
            elif "inglizcha" in text.lower() or "english" in text.lower():
                target_lang = "en"
            elif "uzbek" in text.lower() or "o'zbek" in text.lower():
                target_lang = "uz"
            # "tarjima qil: matn" yoki "matn tarjima qil" formatini aniqlash
            clean = re.sub(r'(tarjima\s*(qil|etib|et)|translate|inglizcha|ruscha|o\'zbekcha)', '', text, flags=re.IGNORECASE).strip()
            clean = clean.strip(':').strip()
            if clean:
                return smart.translate_simple(clean, target_lang)
            return "Nima tarjima qilishni ayting. Masalan: 'Salom tarjima qil'"
        elif action == "disk":
            return smart.get_disk_space()
        elif action == "uptime":
            return smart.system_uptime()
        elif action == "running_apps":
            return smart.list_running_apps()
        elif action == "timer":
            import re
            nums = re.findall(r'(\d+)', text)
            seconds = 60  # default 1 daqiqa
            if nums:
                val = int(nums[0])
                if "daqiqa" in text.lower() or "minut" in text.lower():
                    seconds = val * 60
                else:
                    seconds = val
            return smart.start_timer(seconds)
        else:
            return "Bu buyruqni tushunmadim. Mavjud: hazil, fakt, tarjima, parol, disk, dasturlar ro'yxati."
    
    def _handle_app_search(self, command: Command) -> str:
        """Dastur ichidan qidirish"""
        app = command.params.get("app", "").lower().strip()
        query = command.params.get("query", "").lower().strip()
        
        if not app or not query:
            return "Nima qidirishni va qaysi dasturda ekanligini ayting."
            
        # 1. YouTube
        if "youtube" in app:
            import features.web as web
            return web.web.search_youtube(query)
            
        # 2. Spotify
        if "spotify" in app:
            import urllib.parse
            os.system(f"start spotify:search:{urllib.parse.quote(query)}")
            return f"Spotify-da '{query}' qidirilmoqda."
            
        # 3. Wikipedia
        if "wikipedia" in app:
            import features.web as web
            return web.web.search_wikipedia(query)
            
        # 4. Google (fallback)
        import features.web as web
        return web.web.search_google(f"{query} {app}")

    def _clean_text(self, text: str) -> str:
        """Matnni qo'shimchalardan tozalash (O'zbek tili uchun)"""
        if not text:
            return ""
            
        # Keng tarqalgan qo'shimchalar
        suffixes = ["ni", "ga", "da", "dan", "ning", "di", "li", "cha", "i"]
        cleaned = text.lower().strip()
        
        # Eng uzun qo'shimchadan boshlab tekshirish
        # Faqat so'z oxirida bo'lsa va so'z o'zagi kamida 3ta harf qolsa
        for suffix in sorted(suffixes, key=len, reverse=True):
            if cleaned.endswith(suffix) and len(cleaned) > len(suffix) + 2:
                # Maxsus holatlar: 'telegramni' -> 'telegram'
                cleaned = cleaned[:-len(suffix)]
                break
                
        return cleaned.strip()

    def _handle_app_control(self, command: Command) -> str:
        """Dasturlarni boshqarish"""
        import difflib
        
        action = command.action
        raw_app_name = command.params.get("app", "").lower().strip()
        target = command.params.get("target", "").lower().strip()
        
        if not raw_app_name:
            return "Qaysi dasturni nazarda tutyapsiz?"

        # 1. To'g'ridan-to'g'ri qidirish
        app_path = self.apps.get(raw_app_name)
        app_name = raw_app_name
        
        # 2. Tozalangan nom bilan qidirish (qo'shimchalarsiz)
        if not app_path:
            cleaned_name = self._clean_text(raw_app_name)
            app_path = self.apps.get(cleaned_name)
            if app_path:
                app_name = cleaned_name
        
        # 3. Fuzzy matching (yaqin nomlarni topish)
        if not app_path:
            all_apps = list(self.apps.keys())
            matches = difflib.get_close_matches(raw_app_name, all_apps, n=1, cutoff=0.6)
            if not matches:
                matches = difflib.get_close_matches(self._clean_text(raw_app_name), all_apps, n=1, cutoff=0.6)
                
            if matches:
                app_name = matches[0]
                app_path = self.apps.get(app_name)

        print(f"[Jarvis] App Control: action={action}, raw={raw_app_name}, identified={app_name}, path={app_path}")

        if action in ["open", "open_context"]:
            # Dastur yo'lini aniq tekshirish va ochish
            if app_path:
                # 1. URI yoki Protocol bo;lsa (e.g., spotify:, shell:AppsFolder)
                if isinstance(app_path, str) and (":" in app_path and not "\\" in app_path or app_path.startswith("shell:")):
                    # Contextual opening (Masalan: chrome da facebook)
                    if action == "open_context" and target:
                        if "http" not in target:
                            # Website-ni topishga urinish
                            urls = web.get_urls() if hasattr(web, 'get_urls') else {}
                            target_url = urls.get(target, f"https://www.google.com/search?q={target}")
                            os.system(f"start {app_path} {target_url}")
                        else:
                            os.system(f"start {app_path} {target}")
                        return f"{app_name.capitalize()} orqali {target} ochilmoqda."
                    
                    os.system(f"start {app_path}")
                    return f"{app_name.capitalize()} ochilmoqda."

                # 2. URL bo'lsa
                if isinstance(app_path, str) and (app_path.startswith("http") or app_path.endswith(".com") or app_path.endswith(".uz")):
                    return web.open_website(app_path)
                
                # 3. Fayl yo'li bo'lsa
                try:
                    username = os.getlogin()
                    app_path = str(app_path).replace("{username}", username).replace("{user}", username)
                except:
                    pass
                
                app_path = os.path.normpath(app_path)
                
                try:
                    if os.path.exists(app_path):
                        # Contextual opening fayl yo'li uchun
                        if action == "open_context" and target:
                            subprocess.Popen([app_path, target])
                            return f"{app_name.capitalize()} orqali {target} ochilmoqda."
                            
                        os.startfile(app_path)
                        return f"{app_name.capitalize()} ochilmoqda."
                    else:
                        subprocess.Popen(app_name, shell=True)
                        return f"{app_name.capitalize()} ochilmoqda."
                except Exception as e:
                    try:
                        subprocess.Popen(app_name, shell=True)
                        return f"{app_name.capitalize()} ochilmoqda."
                    except:
                        return f"Dasturni ochib bo'lmadi: {app_name}"
            else:
                # Scan qilinmagan nom bo'lsa, shell orqali urinib ko'risk
                try:
                    subprocess.Popen(raw_app_name, shell=True)
                    return f"{raw_app_name.capitalize()} ochilmoqda."
                except:
                    return f"Kechirasiz, '{raw_app_name}' dasturini topa olmadim."
        
        elif action == "close":
            # Dastur nomini tozalash
            close_name = app_name.lower().strip()
            # "ni", "dasturini" kabi qo'shimchalarni olib tashlash
            for suffix in ["ni", "ning", "dasturini", "dasturi", "ilovasini", "ilovasi", "programmasini"]:
                if close_name.endswith(suffix) and len(close_name) > len(suffix) + 2:
                    close_name = close_name[:-len(suffix)].strip()
            
            # Ma'lum dasturlarning process nomlari
            process_map = {
                "chrome": "chrome.exe", "google chrome": "chrome.exe",
                "firefox": "firefox.exe", "mozilla": "firefox.exe",
                "edge": "msedge.exe", "microsoft edge": "msedge.exe",
                "notepad": "notepad.exe", "bloknot": "notepad.exe",
                "word": "WINWORD.EXE", "excel": "EXCEL.EXE", "powerpoint": "POWERPNT.EXE",
                "vscode": "Code.exe", "vs code": "Code.exe", "visual studio code": "Code.exe",
                "telegram": "Telegram.exe", "discord": "Discord.exe",
                "spotify": "Spotify.exe", "steam": "steam.exe",
                "calculator": "Calculator.exe", "kalkulyator": "Calculator.exe",
                "explorer": "explorer.exe", "file explorer": "explorer.exe",
                "paint": "mspaint.exe",
                "task manager": "Taskmgr.exe",
                "cmd": "cmd.exe", "terminal": "WindowsTerminal.exe",
                "brave": "brave.exe", "opera": "opera.exe",
                "vlc": "vlc.exe", "media player": "wmplayer.exe",
                "skype": "Skype.exe", "zoom": "Zoom.exe",
                "obs": "obs64.exe", "obs studio": "obs64.exe",
            }
            
            # 1. Process map dan qidirish
            process_name = process_map.get(close_name)
            
            # 2. App path dan exe nomini olish
            if not process_name and app_path:
                try:
                    process_name = os.path.basename(str(app_path))
                except:
                    pass
            
            # 3. Oddiy nom + .exe
            if not process_name:
                process_name = close_name + ".exe"
            
            print(f"[Jarvis] Yopish: '{close_name}' -> process: '{process_name}'")
            
            # Taskkill bilan yopish
            try:
                result = subprocess.run(
                    f"taskkill /f /im {process_name}",
                    shell=True, capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return f"{close_name.capitalize()} yopildi."
                
                # Agar aniq nom ishlamasa, wildcard bilan qidirish
                result2 = subprocess.run(
                    f'taskkill /f /fi "IMAGENAME eq *{close_name}*"',
                    shell=True, capture_output=True, text=True, timeout=5
                )
                if result2.returncode == 0 and "SUCCESS" in (result2.stdout or ""):
                    return f"{close_name.capitalize()} yopildi."
                
                # Tasklist dan qidirish
                tasklist = subprocess.run(
                    "tasklist /fo csv /nh", shell=True, capture_output=True, text=True, timeout=5
                )
                if tasklist.returncode == 0:
                    import difflib
                    running = []
                    for line in tasklist.stdout.split("\n"):
                        parts = line.strip().strip('"').split('","')
                        if parts and len(parts) > 0:
                            running.append(parts[0].strip('"'))
                    
                    matches = difflib.get_close_matches(process_name, running, n=1, cutoff=0.5)
                    if not matches:
                        matches = difflib.get_close_matches(close_name, running, n=1, cutoff=0.5)
                    if not matches:
                        matches = difflib.get_close_matches(close_name + ".exe", running, n=1, cutoff=0.5)

                    if matches:
                        matched_proc = matches[0]
                        result3 = subprocess.run(
                            f'taskkill /f /im "{matched_proc}"',
                            shell=True, capture_output=True, text=True, timeout=5
                        )
                        if result3.returncode == 0:
                            return f"{close_name.capitalize()} ({matched_proc}) yopildi."
                
                return f"Kechirasiz, '{close_name}' dasturi ishlab turgan emas yoki topilmadi."
            except Exception as e:
                print(f"[Jarvis] Close error: {e}")
                return f"Kechirasiz, '{close_name}' ni yopishda xatolik bo'ldi."
        
        return "Kechirasiz, bu buyruqni bajara olmadim."
    
    def _handle_file_manager(self, command: Command) -> str:
        """Fayl va papkalarni boshqarish"""
        folder = command.params.get("folder")
        
        if folder:
            folder_name = self.folders.get(folder.lower(), folder)
            user_folder = os.path.expanduser(f"~/{folder_name}")
            
            if os.path.exists(user_folder):
                os.startfile(user_folder)
                return f"{folder.capitalize()} papkasi ochilmoqda."
            else:
                return f"Kechirasiz, {folder} papkasi topilmadi."
        else:
            # Umumiy fayl menejerni ochish
            os.startfile(os.path.expanduser("~"))
            return "Fayl menejeri ochilmoqda."
    
    def _take_screenshot(self) -> str:
        """Ekran suratini olish"""
        try:
            import pyautogui
            from datetime import datetime
            
            # Saqlash joyi
            screenshots_dir = os.path.expanduser("~/Pictures/Screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Fayl nomi
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(screenshots_dir, filename)
            
            # Screenshot olish
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            return f"Ekran surati saqlandi: {filename}"
        except Exception as e:
            return f"Ekran suratini olishda xatolik: {str(e)}"


# Global instance
jarvis = Jarvis()
