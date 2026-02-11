"""
Buyruqlar analizatori
O'zbekcha buyruqlarni tushunish va qayta ishlash
"""

import re
from typing import Optional, Tuple, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum


class CommandType(Enum):
    """Buyruq turlari"""
    GREETING = "greeting"
    TIME_DATE = "time_date"
    WEATHER = "weather"
    APP_CONTROL = "app_control"
    FILE_MANAGER = "file_manager"
    WEB_SEARCH = "web_search"
    MATH = "math"
    SYSTEM = "system"
    REMINDER = "reminder"
    MEDIA = "media"
    SCREENSHOT = "screenshot"
    AI_CHAT = "ai_chat"
    EXIT = "exit"
    SMART = "smart"  # hazil, motivatsiya, faktlar
    SOCIAL = "social"  # ijtimoiy tarmoqlar
    KEYBOARD = "keyboard"  # Yangi: yozish, clipboard
    DICTATION = "dictation" # Yangi: diktovka rejimi
    UNKNOWN = "unknown"


@dataclass
class Command:
    """Aniqlangan buyruq"""
    type: CommandType
    action: str
    params: Dict[str, Any]
    original_text: str


class CommandParser:
    """O'zbekcha buyruqlar analizatori"""
    
    def __init__(self):
        self._init_patterns()
    
    def _init_patterns(self):
        """Buyruq patternlarini yaratish"""
        
        # ===== Fuzzy matching: kalit so'zlar lug'ati =====
        # STT tez-tez noto'g'ri taniy oladigan so'zlar
        self._keywords = [
            # Sistema
            "ovoz", "ovozni", "batareya", "akkumulyator", "skrinshot", "screenshot",
            "kompyuter", "yorqinlik", "yorug'lik", "brightness",
            "oyna", "qulfla", "uxla", "shutdown", "restart", "hibernate",
            "chiqindi", "savatcha", "minimize", "volume", "sound",
            # Harakatlar
            "ko'tar", "baland", "oshir", "pasayt", "kamayt", "o'chir",
            "kuchaytir", "maksimum", "mute", "unmute", "turn", "up", "down", "off", "on",
            "och", "ochib", "yop", "yopib", "ishga", "tushir", "open", "close", "start", "run",
            # Vaqt/sana
            "soat", "vaqt", "sana", "bugun", "hafta", "time", "date", "today",
            # Salomlashish
            "salom", "hayrli", "rahmat", "xayr", "hello", "hi", "thanks", "goodbye",
            # Boshqa
            "qidir", "izla", "search", "google", "youtube", "wikipedia", "find",
            "musiqa", "music", "play", "pause", "pauza", "stop", "resume",
            "papka", "folder", "yuklamalar", "downloads", "hujjatlar", "documents",
            "eslatma", "reminder", "taymer", "timer", "remind",
            "hazil", "motivatsiya", "fakt", "parol", "joke", "fact", "password",
            "tarjima", "translate", "telegram", "instagram",
            "nusxa", "copy", "joylashtir", "paste", "saqlash", "save",
            "jarvis", "dastur", "dasturlar", "process", "app", "apps",
            "internet", "tarmoq", "network", "wifi",
            "ekran", "kattalashtir", "kichraytir", "screen", "zoom",
            "ob-havo", "havo", "haqida", "tizim", "weather", "about", "system",
        ]
        
        # Tez-tez uchraydigan STT xatolari (qo'lda)
        self._known_corrections = {
            "ovos": "ovoz", "avoz": "ovoz", "ovz": "ovoz", "ovozi": "ovozni",
            "ooz": "ovoz", "ovs": "ovoz",
            "baterya": "batareya", "batarya": "batareya", "batarey": "batareya",
            "baterea": "batareya", "batariya": "batareya",
            "skrishot": "skrinshot", "skrenshot": "skrinshot", "skrinshod": "skrinshot",
            "skinshot": "skrinshot", "screnshot": "screenshot", "skreenshot": "screenshot",
            "komputer": "kompyuter", "komyuter": "kompyuter", "kompyuter": "kompyuter",
            "kotar": "ko'tar", "kotor": "ko'tar", "kutar": "ko'tar",
            "kotarildi": "ko'tarildi",
            "pasayd": "pasayt", "posayt": "pasayt", "posait": "pasayt",
            "uchir": "o'chir", "ochir": "o'chir", "uchir": "o'chir",
            "kuchaytir": "kuchaytir", "kuchaitir": "kuchaytir",
            "yorkinlik": "yorqinlik", "yorkinliq": "yorqinlik",
            "yoruglik": "yorug'lik", "yoruqlik": "yorug'lik",
            "yopib": "yopib", "yopip": "yopib",
            "ochib": "ochib", "ochip": "ochib", "ochi": "ochib",
            "qulfa": "qulfla", "qufla": "qulfla",
            "shutdown": "shutdown", "shutdaun": "shutdown",
            "restrt": "restart", "ristart": "restart", "restar": "restart",
            "minimaliz": "minimize", "minimays": "minimize",
            "chiqudi": "chiqindi", "chiqndi": "chiqindi",
            "savatchi": "savatcha", "savachi": "savatcha",
            "musika": "musiqa", "muzika": "musiqa", "musqa": "musiqa",
            "qidirish": "qidir", "qidiri": "qidir",
            "telgram": "telegram", "telegran": "telegram", "telagram": "telegram",
            "instgram": "instagram", "insagram": "instagram",
            "yutub": "youtube", "yutube": "youtube", "yutup": "youtube",
            "gugul": "google", "gugl": "google",
            "vikipediya": "wikipedia", "vikipedia": "wikipedia",
            "taymar": "taymer", "tamer": "taymer",
            "tarjma": "tarjima", "tarjma": "tarjima",
            "hzil": "hazil", "hazl": "hazil",
            "motivatsya": "motivatsiya",
            "paral": "parol", "porol": "parol",
            "internt": "internet", "intarnet": "internet",
            "tarmoq": "tarmoq", "tarmok": "tarmoq",
            "salom": "salom", "slom": "salom", "salam": "salom",
            "rahma": "rahmat", "raxmat": "rahmat",
            "hayrli": "hayrli", "xayrli": "hayrli",
            "saat": "soat", "soaat": "soat", "soet": "soat",
            "bugun": "bugun", "bugn": "bugun",
            "elatma": "eslatma", "esltma": "eslatma",
            "havo": "havo", "obhavo": "ob-havo",
            "ekrn": "ekran", "ekron": "ekran",
            "yuklaml": "yuklamalar", "yuklama": "yuklamalar",
            "papke": "papka", "popka": "papka",
            "nushxa": "nusxa", "nusha": "nusxa",
            "saqlsh": "saqlash", "saqla": "saqlash",
            "dasur": "dastur", "datur": "dastur", "dastor": "dastur",
            "haqda": "haqida", "haqda": "haqida",
            # Inglizcha STT xatolari
            "volum": "volume", "volumme": "volume",
            "brayness": "brightness", "brigtness": "brightness",
            "screnshoot": "screenshot",
        }
        
        # ===== Regex patternlar =====
        
        # Salomlashish
        self.greetings = [
            r"\bsalom\b", r"\bassalomu alaykum\b", r"\bhayrli kun\b",
            r"\bhayrli tong\b", r"\bhayrli kech\b", r"\bhey\b", r"\bhi\b",
            r"\bhello\b", r"\bgood morning\b", r"\bgood afternoon\b", r"\bgood evening\b"
        ]
        
        # Xayrlashish
        self.goodbyes = [
            r"\bxayr\b", r"\bko'rishguncha\b", r"\brahmat\b", r"\bsalom va sog'liq\b",
            r"\byaxshi qol\b", r"\bmayli\b", r"\bbye\b", r"\bgoodbye\b", r"\bsee you\b"
        ]
        
        # Holat so'rash
        self.how_are_you = [
            r"qanday.*(vorley|voleysan|bor|ey)",
            r"nima.*gap", r"\bqalaysan\b", r"\byaxshimisan\b",
            r"how are you", r"how's it going", r"what's up"
        ]
        
        # Vaqt
        self.time_patterns = [
            r"soat.*necha", r"vaqt.*qancha", r"hozir.*soat",
            r"soatni.*ayt", r"what.*time", r"current time"
        ]
        
        # Sana
        self.date_patterns = [
            r"bugun.*kun", r"qaysi.*kun", r"hafta.*kun",
            r"bugun.*sana", r"sanani.*ayt", r"what.*date", r"today's date"
        ]
        
        # Ob-havo
        self.weather_patterns = [
            r"ob.*havo", r"havo.*qanday", r"tashqarida.*qanday",
            r"weather", r"how's the weather"
        ]
        
        # Papka ochish
        self.folder_patterns = [
            r"(papka|folder|katalog)\s*(och|ochib.*ber)?",
            r"(yuklamalar|downloads|hujjatlar|documents|rasmlar|pictures|musiqa|music|video|videos|ish.*stoli|desktop)\s*(papka|folder)?\s*(och|ochib.*ber|ko'rsat)?",
            r"(open|show)\s*(downloads|documents|pictures|music|videos|desktop)\s*(folder)?"
        ]
        
        # Dastur ochish
        self.open_app_patterns = [
            r"(.*)\s+da\s+(.*)\s+\b(och|ishga.*tushir)\b",
            r"\b(och|ochib.*ber|ishga.*tushir|run|start|open|launch)\b\s*(.*)",
            r"(.*)\s*\b(och|ochib.*ber|ishga.*tushir|run|start|open|launch)\b",
            r"(.*)\b(och|ich|ish|open)\b$"
        ]
        
        # Dastur yopish
        self.close_app_patterns = [
            r"\b(yop|yopib.*ber|o'chir|close|exit|stop|quit)\b\s*(.*)",
            r"(.*)\s*\b(yop|yopib.*ber|o'chir|close|exit|stop|quit)\b",
            r"(.*)\b(yop|yopib|close)\b$"
        ]
        
        # Web qidiruv
        self.web_search_patterns = [
            r"google.*da\s+(.+)\s*(qidir|izla)",
            r"(qidir|izla|search|look up)\s+(.+)\s*google",
            r"youtube.*da\s+(.+)\s*(qidir|izla|qo'y)",
            r"wikipedia.*da\s+(.+)\s*(haqida|qidir)",
            r"(.+)\s*da\s+(.+)\s*(qidir|izla|search)",
            r"(.*)\s*sayt.*ni?\s*(och|ochib.*ber)",
            r"search\s+(.+)\s*(on|in)\s+(google|youtube|wikipedia)",
            r"(search|google|find)\s+(.+)"
        ]
        
        # Matematika
        self.math_patterns = [
            r"(\d+)\s*(plyus|\+|qo'sh|plus)\s*(\d+)",
            r"(\d+)\s*(minus|\-|ayir)\s*(\d+)",
            r"(\d+)\s*(ko'paytir|ko'pay|\*|marta|times|multiplied by)\s*(\d+)",
            r"(\d+)\s*(bo'l|bo'lib|\:|divided by)\s*(\d+)",
            r"(\d+)\s*ning\s*(kvadrat|kub|daraja)",
            r"(\d+)\s*foiz\s*(\d+)",
            r"(\d+)\s*(ildiz|sqrt|root)",
            r"calculate\s+(.+)"
        ]
        
        # Sistema buyruqlari
        self.system_patterns = [
            r"kompyuter.*haqida", r"tizim.*ma'lumot",
            r"batareya", r"akkumulyator", r"battery",
            r"ovoz.*(ko'tar|baland|oshir|qo'sh|up|increase|louder|volume.*up|higher)",
            r"ovoz.*(pasayt|past|kamayt|ayir|down|decrease|lower|volume.*down|quieter)",
            r"ovoz.*(o'chir|o'chish|yo'qot|mute|off|silence)",
            r"ovoz.*(yoq|yoqish|unmute|on|sound.*on)",
            r"ovoz.*(to'liq|maksimum|max|100|full.*volume)",
            r"yorug'lik|yorqinlik|brightness",
            r"oyna.*(kichraytir|yop|berkit|minimize|close)",
            r"chiqindi|savatcha|recycle.*bin|trash",
            r"kompyuter.*(o'chir|shutdown|power off)",
            r"qayta.*(yoq|ishga|tushir|restart|reboot)",
            r"uxla|sleep|gibrid|hibernate",
            r"qulfla|lock|blokla",
            r"system info", r"computer info",
            r"(.*)\s*(oldinda|oldinga|fokus|focus|aktivlashtir|olga)"
        ]
        
        # Eslatma
        self.reminder_patterns = [
            r"(\d+)\s*(daqiqa|minut|soat|sekund|minute|hour|second).*eslatib",
            r"eslatma\s*(yoz|qo'sh)\s*[:.]?\s*(.*)",
            r"eslatmalar.*o'qi",
            r"remind me in (\d+)\s*(minute|hour|second|min|hr|sec)",
            r"set reminder\s*(.*)"
        ]
        
        # Media / YouTube
        self.media_patterns = [
            r"musiqa\s*(qo'y|ijro|och|play|music)",
            r"youtube.*da\s+(.+)\s*(qo'y|ijro|och|play)",
            r"(.+)\s*(qo'shig'ini|musiqasini)\s*(qo'y|ijro|och)",
            r"(to'xtat|pauza|pause|stop)",
            r"(davom.*et|play|resume|boshla)",
            r"keyingi\s*(trek|qo'shiq|musiqa|track|next)",
            r"oldingi\s*(trek|qo'shiq|musiqa|track|previous|prev)",
            r"play\s+(.+)"
        ]
        
        # Keyboard / Yozish / Browser / Clipboard
        self.keyboard_patterns = [
            # Yozish
            r"(.*)\s*da\s*(.*)\s*deb\s*yoz",
            r"yoz\s*[:.]?\s*(.+)",
            r"(.+)\s*deb\s*yoz",
            r"type\s+(.*)\s+in\s+(.*)",
            r"type\s+(.+)",
            # Clipboard
            r"nusxa\s*(ol|ko'chir|copy)",
            r"joylashtir|paste",
            r"hammasini\s*tanla|select all",
            r"kesib\s*ol|cut",
            r"clipboard.*(o'qi|oku|ko'rsat|read)",
            r"clipboard.*(qidir|search|google)",
            # Tahrirlash
            r"bekor\s*qil|undo",
            r"qayta\s*qil|redo",
            r"saqlash|save",
            r"topish|qidirish|find",
            r"yangi\s*(fayl|hujjat|dokument)|new\s*(file|document)",
            r"chop\s*(et|qil)|print",
            # Browser tab
            r"yangi\s*tab|new\s*tab",
            r"tab.*(yop|berkit|close)",
            r"tab.*(almashtir|o'zgartir|switch|keyingi|oldingi)",
            r"sahifa.*(yangi|refresh|qayta|reload)",
            r"manzil\s*satri|address\s*bar",
            # Zoom
            r"kattalashtir|zoom\s*in|yaqinlashtir",
            r"kichraytir|zoom\s*out|uzoqlashtir",
            r"to'liq\s*ekran|full\s*screen",
            # Window
            r"boshqa\s*dastur|alt\s*tab|switch\s*app",
            r"ekran\s*qism|screenshot\s*region",
        ]
        
        # Screenshot
        self.screenshot_patterns = [
            r"(skrinshot|screenshot|ekran.*surat|ekran.*ol)"
        ]
        
        # Chiqish
        self.exit_patterns = [
            r"(chiq|yop|o'chir|exit|dastur.*yop).*\bjarvis\b",
            r"\bjarvis\b.*(chiq|yop|o'chir)"
        ]
        
        # Smart buyruqlar
        self.smart_patterns = {
            "joke": [r"hazil", r"kuldur", r"anekdot", r"qiziq.*gap"],
            "motivation": [r"motivatsiya", r"ruhlantir", r"ilhom", r"kuch.*ber"],
            "fact": [r"fakt", r"qiziqarli", r"bilasanmi"],
            "coin": [r"tanga.*tashla", r"bosh.*yoki.*yozuv"],
            "dice": [r"zar.*tashla", r"kub.*tashla"],
            "random": [r"tasodifiy.*son", r"random"],
            "day_info": [r"yil.*kun", r"hafta.*nomer"],
            "ip": [r"ip.*manzil", r"ip.*address"],
            # Yangi smart buyruqlar
            "password": [r"parol.*(yarat|generatsiya|yaratib)", r"generate.*password", r"kuchli.*parol"],
            "translate": [r"tarjima\s*(qil|etib)", r"translate", r"inglizcha.*(ayt|bo'l)", r"ruscha.*(ayt|bo'l)"],
            "disk": [r"disk.*(hajm|joy|space)", r"xotira.*(qancha|hajm)", r"bo'sh.*joy"],
            "uptime": [r"kompyuter.*qancha.*vaqt", r"tizim.*vaqt", r"uptime", r"qachon.*yoqilgan"],
            "running_apps": [r"ishlab.*turgan.*dastur", r"ochiq.*dastur", r"running.*app", r"qaysi.*dastur.*ochiq"],
            "timer": [r"taymer|timer", r"(\d+)\s*(soniya|daqiqa|minut).*taymer", r"taymer.*(\d+)"],
        }
        
        # Ijtimoiy tarmoqlar
        self.social_patterns = [
            r"\b(youtube|telegram|instagram|facebook|twitter|tiktok|linkedin|github)\b\s*\b(och|ochib.*ber|ishga.*tushir)\b"
        ]
        
        # Diktovka / Yozish rejimi
        self.dictation_patterns = [
            r"yozish.*(rejim|mode).*(yoq|start|boshla|kir)",
            r"diktovka.*(rejim|mode|yoq|start)",
            r"dictation.*(mode|start|on)",
            r"start.*dictation",
            r"text.*input.*mode"
        ]

    @staticmethod
    def _levenshtein(s1: str, s2: str) -> int:
        """Ikki so'z orasidagi Levenshtein masofasini hisoblash"""
        if len(s1) < len(s2):
            return CommandParser._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                cost = 0 if c1 == c2 else 1
                curr_row.append(min(
                    curr_row[j] + 1,
                    prev_row[j + 1] + 1,
                    prev_row[j] + cost
                ))
            prev_row = curr_row
        return prev_row[-1]
    
    def _fuzzy_normalize(self, text: str) -> str:
        """
        Matnni fuzzy normalizatsiya qilish:
        1. Ma'lum xatolarni to'g'rilash (lug'at)
        2. Noma'lum so'zlarni eng yaqin kalit so'zga moslashtirish (Levenshtein)
        """
        words = text.split()
        corrected = []
        
        for word in words:
            word_lower = word.lower().strip()
            
            # 1. Ma'lum xato lug'atdan tekshirish
            if word_lower in self._known_corrections:
                corrected.append(self._known_corrections[word_lower])
                continue
            
            # 2. Agar so'z kalit so'zlar ichida bo'lsa — to'g'ri
            if word_lower in self._keywords:
                corrected.append(word_lower)
                continue
            
            # 3. Levenshtein bilan eng yaqin kalit so'zni topish
            #    Faqat 3+ harfli so'zlar uchun (qisqa so'zlar juda ko'p noto'g'ri mos kelishi mumkin)
            if len(word_lower) >= 3:
                best_match = None
                best_distance = float('inf')
                
                for keyword in self._keywords:
                    # Uzunlik farqi juda katta bo'lsa, o'tkazib yuborish
                    if abs(len(word_lower) - len(keyword)) > 2:
                        continue
                    
                    dist = self._levenshtein(word_lower, keyword)
                    if dist < best_distance:
                        best_distance = dist
                        best_match = keyword
                
                # Faqat 1-2 harf farq bo'lsa tuzatish
                max_dist = 1 if len(word_lower) <= 4 else 2
                if best_match and best_distance <= max_dist and best_distance > 0:
                    print(f"[Fuzzy] '{word_lower}' → '{best_match}' (farq: {best_distance})")
                    corrected.append(best_match)
                    continue
            
            # Hech narsa topmasa, o'zgartirmasdan qo'shish
            corrected.append(word_lower)
        
        result = " ".join(corrected)
        if result != text.lower().strip():
            print(f"[Fuzzy] Asl: '{text}' → Tuzatilgan: '{result}'")
        return result

    def parse(self, text: str) -> Command:
        """
        Matnni tahlil qilish va buyruqni aniqlash
        
        Args:
            text: Foydalanuvchi aytgan matn
            
        Returns:
            Aniqlangan buyruq
        """
        # Fuzzy normalizatsiya — STT xatolarini tuzatish
        text_lower = self._fuzzy_normalize(text)
        
        # Salomlashish
        for pattern in self.greetings:
            if re.search(pattern, text_lower):
                return Command(
                    type=CommandType.GREETING,
                    action="hello",
                    params={},
                    original_text=text
                )
        
        # Xayrlashish
        for pattern in self.goodbyes:
            if re.search(pattern, text_lower):
                return Command(
                    type=CommandType.GREETING,
                    action="goodbye",
                    params={},
                    original_text=text
                )
        
        # Holat
        for pattern in self.how_are_you:
            if re.search(pattern, text_lower):
                return Command(
                    type=CommandType.GREETING,
                    action="how_are_you",
                    params={},
                    original_text=text
                )
        
        # Chiqish
        for pattern in self.exit_patterns:
            if re.search(pattern, text_lower):
                return Command(
                    type=CommandType.EXIT,
                    action="exit",
                    params={},
                    original_text=text
                )

        # 1. Sistema buyruqlari (Eng yuqori prioritet, chunki ular juda aniq)
        for pattern in self.system_patterns:
            if re.search(pattern, text_lower):
                action = "info"
                params = {}
                
                if "batareya" in text_lower or "akkumulyator" in text_lower:
                    action = "battery"
                elif "ovoz" in text_lower:
                    if any(x in text_lower for x in ["o'chir", "mute", "yo'qot"]):
                        action = "mute"
                    elif any(x in text_lower for x in ["yoq", "unmute", "eshitilsin"]):
                        action = "unmute"
                    elif any(x in text_lower for x in ["to'liq", "maksimum", "max", "100"]):
                        action = "volume_max"
                    elif any(x in text_lower for x in ["ko'tar", "baland", "oshir", "qo'sh", "kuchaytir"]):
                        action = "volume_up"
                    else:
                        action = "volume_down"
                elif any(x in text_lower for x in ["yorqinlik", "yorug'lik", "brightness"]):
                    levels = re.findall(r"(\d+)", text_lower)
                    if levels:
                        action = "brightness_set"
                        params["level"] = int(levels[0])
                    elif any(x in text_lower for x in ["oshir", "ko'tar", "baland", "ko'p"]):
                        action = "brightness_up"
                    elif any(x in text_lower for x in ["pasayt", "past", "kamayt", "oz"]):
                        action = "brightness_down"
                    else:
                        action = "brightness_set" # default
                elif "oyna" in text_lower or any(x in text_lower for x in ["minimize", "kichraytir", "yop", "close"]):
                    if any(x in text_lower for x in ["yop", "o'chir", "close", "yopish"]):
                        action = "close_window"
                    else:
                        action = "minimize_all"
                elif any(x in text_lower for x in ["chiqindi", "savatcha", "recycle", "trash"]):
                    if any(x in text_lower for x in ["tozala", "bo'shat", "clear", "empty"]):
                        action = "cleaning_mode" if "pro" in text_lower or "tozalash" in text_lower else "empty_trash"
                    else:
                        action = "empty_trash"
                elif any(x in text_lower for x in ["qulfla", "lock", "blokla"]):
                    action = "lock"
                elif "gibrid" in text_lower or "hibernate" in text_lower:
                    action = "hibernate"
                elif "o'chir" in text_lower or "shutdown" in text_lower or "power off" in text_lower:
                    if "bekor" in text_lower or "cancel" in text_lower:
                        action = "cancel_shutdown"
                    else:
                        action = "shutdown"
                elif "qayta" in text_lower or "restart" in text_lower or "reboot" in text_lower:
                    action = "restart"
                elif "uxla" in text_lower or "sleep" in text_lower:
                    action = "sleep"
                # PRO ACTIONS
                elif any(x in text_lower for x in ["dasturlar", "process", "apps"]) and any(x in text_lower for x in ["ko'p", "yeyapti", "ishlat", "list", "hungry"]):
                    action = "list_processes"
                elif any(x in text_lower for x in ["yop", "kill", "stop", "tugat"]) and ("dastur" in text_lower or "process" in text_lower or any(app in text_lower for app in ["chrome", "notepad", "telegram", "word", "excel"])):
                    action = "kill_process"
                    words = text_lower.split()
                    if "yop" in words: 
                        idx = words.index("yop")
                        if idx > 0: params["app"] = words[idx-1]
                    elif "kill" in words:
                        idx = words.index("kill")
                        if idx < len(words) - 1: params["app"] = words[idx+1]
                elif any(x in text_lower for x in ["internet", "tarmoq", "network", "ping", "wifi"]):
                    action = "network_status"
                elif any(x in text_lower for x in ["dars", "o'qish", "study"]) and ("rejim" in text_lower or "mode" in text_lower):
                    action = "study_mode"
                elif any(x in text_lower for x in ["oldinda", "oldinga", "fokus", "focus", "aktivlashtir", "olga"]):
                    action = "focus_window"
                    # App name extraction
                    for term in ["oldinda", "oldinga", "fokus", "focus", "aktivlashtir", "olga"]:
                        if term in text_lower:
                            params["app"] = text_lower.split(term)[0].strip()
                            break
                
                return Command(type=CommandType.SYSTEM, action=action, params=params, original_text=text)

        # 2. Vaqt va Sana
        for pattern in self.time_patterns:
            if re.search(pattern, text_lower):
                return Command(type=CommandType.TIME_DATE, action="time", params={}, original_text=text)
        
        for pattern in self.date_patterns:
            if re.search(pattern, text_lower):
                return Command(type=CommandType.TIME_DATE, action="date", params={}, original_text=text)
        
        # 3. Ob-havo
        for pattern in self.weather_patterns:
            if re.search(pattern, text_lower):
                city = None
                city_match = re.search(r"(toshkent|samarqand|buxoro|andijon|farg'ona|namangan|qashqadaryo|surxondaryo|xorazm|navoiy|jizzax|sirdaryo|qoraqalpog'iston).*da", text_lower)
                if city_match: city = city_match.group(1)
                return Command(type=CommandType.WEATHER, action="current", params={"city": city}, original_text=text)
        
        # 4. Papka ochish
        for pattern in self.folder_patterns:
            match = re.search(pattern, text_lower)
            if match:
                folder = None
                for folder_name in ["yuklamalar", "downloads", "hujjatlar", "documents", "rasmlar", "pictures", "musiqa", "music", "video", "videos", "ish stoli", "desktop"]:
                    if folder_name in text_lower:
                        folder = folder_name
                        break
                return Command(type=CommandType.FILE_MANAGER, action="open_folder", params={"folder": folder}, original_text=text)
        
        # 5. Dastur ochish
        for pattern in self.open_app_patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                # Exception: "oyna" yoki "chiqindi" bo'lsa app control deb o'ylama (system check qilindi yuqorida)
                if any(x in text_lower for x in ["oyna", "chiqindi", "savatcha"]): continue

                if len(groups) >= 3 and groups[0] and groups[1]:
                    app = groups[0].strip()
                    target = groups[1].strip()
                    return Command(type=CommandType.APP_CONTROL, action="open_context", params={"app": app, "target": target}, original_text=text)
                
                app_name = None
                skip_words = r"\b(och|ochib|ber|ishga|tushir|run|start|ich|ish|da)\b"
                for g in groups:
                    if g and not re.search(skip_words, g.strip()):
                        app_name = g.strip()
                
                if app_name:
                    return Command(type=CommandType.APP_CONTROL, action="open", params={"app": app_name}, original_text=text)
        
        # 6. Dastur yopish
        for pattern in self.close_app_patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                # Exception checklist
                if any(x in text_lower for x in ["oyna", "chiqindi", "savatcha"]): continue

                app_name = None
                skip_words = r"\b(yop|yopib|ber|o'chir)\b"
                for g in groups:
                    if g and not re.search(skip_words, g.strip()):
                        app_name = g.strip()
                
                if app_name:
                    return Command(type=CommandType.APP_CONTROL, action="close", params={"app": app_name}, original_text=text)
        
        # Web qidiruv (Special apps search)
        for pattern in self.web_search_patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                # 1. App-specific search: (app) da (query) (action)
                if " da " in text_lower and len(groups) >= 2:
                    # Agar pattern (app) dan boshlansa (3 groups)
                    if len(groups) >= 3:
                        app = groups[0].strip()
                        query = groups[1].strip()
                    else:
                        # Agar pattern youtube.*da bo'lsa (2 groups: query, action)
                        if "youtube" in text_lower: app = "youtube"
                        elif "google" in text_lower: app = "google"
                        elif "wikipedia" in text_lower: app = "wikipedia"
                        else: app = "google" # fallback
                        query = groups[0].strip()
                        
                    return Command(
                        type=CommandType.WEB_SEARCH,
                        action="app_search",
                        params={"app": app, "query": query},
                        original_text=text
                    )
                
                # 2. General search
                if groups:
                    query = groups[0].strip()
                    engine = "google"
                    if "youtube" in text_lower: engine = "youtube"
                    elif "wikipedia" in text_lower: engine = "wikipedia"
                    
                    return Command(
                        type=CommandType.WEB_SEARCH,
                        action="search",
                        params={"query": query, "engine": engine},
                        original_text=text
                    )
        
        # Matematika
        for pattern in self.math_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return Command(
                    type=CommandType.MATH,
                    action="calculate",
                    params={"expression": text_lower},
                    original_text=text
                )
        
        # Sistema buyruqlari
        for pattern in self.system_patterns:
            if re.search(pattern, text_lower):
                action = "info"
                params = {}
                
                if "batareya" in text_lower or "akkumulyator" in text_lower:
                    action = "battery"
                elif "ovoz" in text_lower:
                    if any(x in text_lower for x in ["o'chir", "mute", "yo'qot"]):
                        action = "mute"
                    elif any(x in text_lower for x in ["yoq", "unmute", "eshitilsin"]):
                        action = "unmute"
                    elif any(x in text_lower for x in ["ko'tar", "baland", "oshir", "qo'sh"]):
                        action = "volume_up"
                    else:
                        action = "volume_down"
                elif any(x in text_lower for x in ["yorqinlik", "yorug'lik", "brightness"]):
                    # Sonni aniqlash (Masalan: 50 foiz)
                    levels = re.findall(r"(\d+)", text_lower)
                    if levels:
                        action = "brightness_set"
                        params["level"] = int(levels[0])
                    elif any(x in text_lower for x in ["oshir", "ko'tar", "baland", "ko'p"]):
                        action = "brightness_up"
                    elif any(x in text_lower for x in ["pasayt", "past", "kamayt", "oz"]):
                        action = "brightness_down"
                    else:
                        action = "brightness_set" # default
                elif "oyna" in text_lower or any(x in text_lower for x in ["minimize", "kichraytir", "yop", "close"]):
                    if any(x in text_lower for x in ["yop", "o'chir", "close", "yopish"]):
                        action = "close_window"
                    else:
                        action = "minimize_all"
                elif any(x in text_lower for x in ["chiqindi", "savatcha", "recycle", "trash"]):
                    if any(x in text_lower for x in ["tozala", "bo'shat", "clear", "empty"]):
                        action = "cleaning_mode" if "pro" in text_lower or "tozalash" in text_lower else "empty_trash"
                    else:
                        action = "empty_trash"
                elif any(x in text_lower for x in ["qulfla", "lock", "blokla"]):
                    action = "lock"
                elif "gibrid" in text_lower or "hibernate" in text_lower:
                    action = "hibernate"
                elif "o'chir" in text_lower or "shutdown" in text_lower or "power off" in text_lower:
                    if "bekor" in text_lower or "cancel" in text_lower:
                        action = "cancel_shutdown"
                    else:
                        action = "shutdown"
                elif "qayta" in text_lower or "restart" in text_lower or "reboot" in text_lower:
                    action = "restart"
                elif "uxla" in text_lower or "sleep" in text_lower:
                    action = "sleep"
                # PRO ACTIONS
                elif any(x in text_lower for x in ["dasturlar", "process", "apps"]) and any(x in text_lower for x in ["ko'p", "yeyapti", "ishlat", "list", "hungry"]):
                    action = "list_processes"
                elif any(x in text_lower for x in ["yop", "kill", "stop", "tugat"]) and ("dastur" in text_lower or "process" in text_lower or any(app in text_lower for app in ["chrome", "notepad", "telegram", "word", "excel"])):
                    action = "kill_process"
                    # App name extraction
                    words = text_lower.split()
                    if "yop" in words: 
                        idx = words.index("yop")
                        if idx > 0: params["app"] = words[idx-1]
                    elif "kill" in words:
                        idx = words.index("kill")
                        if idx < len(words) - 1: params["app"] = words[idx+1]
                elif any(x in text_lower for x in ["internet", "tarmoq", "network", "ping", "wifi"]):
                    action = "network_status"
                elif any(x in text_lower for x in ["dars", "o'qish", "study"]) and ("rejim" in text_lower or "mode" in text_lower):
                    action = "study_mode"
                elif any(x in text_lower for x in ["tozalash", "cleaning"]) and ("rejim" in text_lower or "mode" in text_lower):
                    action = "cleaning_mode"
                
                return Command(
                    type=CommandType.SYSTEM,
                    action=action,
                    params=params,
                    original_text=text
                )
        
        # Eslatma
        for pattern in self.reminder_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if "o'qi" in text_lower:
                    return Command(
                        type=CommandType.REMINDER,
                        action="list",
                        params={},
                        original_text=text
                    )
                elif match.groups():
                    time_value = int(match.group(1)) if match.group(1).isdigit() else 5
                    time_unit = "daqiqa"
                    for unit in ["sekund", "daqiqa", "minut", "soat"]:
                        if unit in text_lower:
                            time_unit = unit
                            break
                    
                    return Command(
                        type=CommandType.REMINDER,
                        action="set",
                        params={"time": time_value, "unit": time_unit},
                        original_text=text
                    )
        
        # Media / YouTube musiqa
        for pattern in self.media_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # YouTube'da musiqa qo'yish
                if "youtube" in text_lower or "qo'shig'" in text_lower or "musiqa" in text_lower:
                    query = ""
                    if match.groups():
                        for g in match.groups():
                            if g and not re.match(r"(qo'y|ijro|och|qo'shig'ini|musiqasini)", g.strip()):
                                query = g.strip()
                                break
                    
                    if query:
                        return Command(
                            type=CommandType.MEDIA,
                            action="youtube_music",
                            params={"query": query},
                            original_text=text
                        )
                
                # Oddiy media buyruqlari
                action = "play"
                if any(x in text_lower for x in ["to'xtat", "pauza", "pause"]):
                    action = "pause"
                elif any(x in text_lower for x in ["davom", "play"]):
                    action = "resume"
                elif "keyingi" in text_lower:
                    action = "next"
                elif "oldingi" in text_lower:
                    action = "previous"
                
                return Command(
                    type=CommandType.MEDIA,
                    action=action,
                    params={},
                    original_text=text
                )

        # Diktovka
        for pattern in self.dictation_patterns:
            if re.search(pattern, text_lower):
                return Command(
                    type=CommandType.DICTATION,
                    action="enable",
                    params={},
                    original_text=text
                )
        
        # Screenshot
        for pattern in self.screenshot_patterns:
            if re.search(pattern, text_lower):
                return Command(
                    type=CommandType.SCREENSHOT,
                    action="capture",
                    params={},
                    original_text=text
                )
        
        # Keyboard / Yozish buyruqlari
        for pattern in self.keyboard_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # ===== CLIPBOARD =====
                if "nusxa" in text_lower or "copy" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="copy", params={}, original_text=text)
                elif "joylashtir" in text_lower or "paste" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="paste", params={}, original_text=text)
                elif "kesib" in text_lower or "cut" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="cut", params={}, original_text=text)
                elif "hammasini" in text_lower or "select all" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="select_all", params={}, original_text=text)
                elif "clipboard" in text_lower and any(w in text_lower for w in ["qidir", "search", "google"]):
                    return Command(type=CommandType.KEYBOARD, action="clipboard_search", params={}, original_text=text)
                elif "clipboard" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="read_clipboard", params={}, original_text=text)
                
                # ===== TAHRIRLASH =====
                elif "bekor" in text_lower or "undo" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="undo", params={}, original_text=text)
                elif "qayta" in text_lower and "qil" in text_lower or "redo" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="redo", params={}, original_text=text)
                elif "saqlash" in text_lower or "save" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="save", params={}, original_text=text)
                elif "topish" in text_lower or "qidirish" in text_lower or "find" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="find", params={}, original_text=text)
                elif any(w in text_lower for w in ["yangi fayl", "yangi hujjat", "new file", "new document"]):
                    return Command(type=CommandType.KEYBOARD, action="new", params={}, original_text=text)
                elif "chop" in text_lower or "print" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="print", params={}, original_text=text)
                
                # ===== BROWSER TAB =====
                elif "yangi" in text_lower and "tab" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="new_tab", params={}, original_text=text)
                elif "tab" in text_lower and any(w in text_lower for w in ["yop", "berkit", "close"]):
                    return Command(type=CommandType.KEYBOARD, action="close_tab", params={}, original_text=text)
                elif "tab" in text_lower:
                    direction = "previous" if any(w in text_lower for w in ["oldingi", "previous", "prev"]) else "next"
                    return Command(type=CommandType.KEYBOARD, action="switch_tab", params={"direction": direction}, original_text=text)
                elif any(w in text_lower for w in ["sahifa", "refresh", "reload"]):
                    return Command(type=CommandType.KEYBOARD, action="refresh", params={}, original_text=text)
                elif "manzil" in text_lower or "address" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="address_bar", params={}, original_text=text)
                
                # ===== ZOOM / WINDOW =====
                elif "kattalashtir" in text_lower or "zoom in" in text_lower or "yaqinlashtir" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="zoom_in", params={}, original_text=text)
                elif "kichraytir" in text_lower or "zoom out" in text_lower or "uzoqlashtir" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="zoom_out", params={}, original_text=text)
                elif "to'liq" in text_lower and "ekran" in text_lower or "full" in text_lower and "screen" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="full_screen", params={}, original_text=text)
                elif "boshqa" in text_lower and "dastur" in text_lower or "alt tab" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="alt_tab", params={}, original_text=text)
                elif "ekran" in text_lower and "qism" in text_lower:
                    return Command(type=CommandType.KEYBOARD, action="screenshot_region", params={}, original_text=text)
                
                # ===== YOZISH =====
                else:
                    text_to_type = ""
                    app_target = None
                    
                    # 1. (app) da (text) deb yoz
                    app_type_match = re.search(r"(.*)\s+da\s+(.*)\s+deb\s+yoz", text_lower)
                    if app_type_match:
                        app_target = app_type_match.group(1).strip()
                        text_to_type = app_type_match.group(2).strip()
                    
                    # 2. type (text) in (app)
                    elif "type" in text_lower and "in" in text_lower:
                        en_match = re.search(r"type\s+(.*)\s+in\s+(.*)", text_lower)
                        if en_match:
                            text_to_type = en_match.group(1).strip()
                            app_target = en_match.group(2).strip()

                    # 3. Oddiy yozish
                    else:
                        if match.groups():
                            text_to_type = match.group(0).replace("yoz", "").replace("deb", "").strip()
                            if match.group(1):
                                text_to_type = match.group(1).strip()
                    
                    if text_to_type:
                        return Command(
                            type=CommandType.KEYBOARD,
                            action="type_in_app" if app_target else "type",
                            params={"text": text_to_type, "app": app_target},
                            original_text=text
                        )
        
        # Smart buyruqlar
        for action, patterns in self.smart_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return Command(
                        type=CommandType.SMART,
                        action=action,
                        params={},
                        original_text=text
                    )
        
        # Ijtimoiy tarmoqlar
        for pattern in self.social_patterns:
            match = re.search(pattern, text_lower)
            if match:
                platform = match.group(1)
                return Command(
                    type=CommandType.SOCIAL,
                    action="open",
                    params={"platform": platform},
                    original_text=text
                )
        
        # Noma'lum buyruq - AI ga yuborish
        return Command(
            type=CommandType.AI_CHAT,
            action="chat",
            params={"message": text},
            original_text=text
        )


# Global parser
parser = CommandParser()
