"""
Kengaytirilgan buyruqlar
Ko'proq funksiyalar va aqlli javoblar
"""

import os
import re
import json
import random
import string
import subprocess
import webbrowser
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import config


class SmartCommands:
    """Kengaytirilgan aqlli buyruqlar tizimi"""
    
    def __init__(self):
        self.jokes = [
            "Dasturchi nima uchun ko'zoynakli? Chunki u JavaScript'ni ko'ra olmaydi! 😄",
            "Kompyuter nima uchun shifokorga bordi? Chunki unda virus bor edi! 🤒",
            "Qanday qilib dasturchi suv ichadi? Catch blokida! 💧",
            "0 va 1 barchasi. Qolganlar shunchaki raqamlar! 🔢",
            "Dasturchi uyda nima qiladi? Home() ga qaytadi! 🏠",
            "Nima uchun ilonlar dasturlashni yaxshi ko'radi? Chunki ular Python'ni yaxshi tushunadi! 🐍",
            "Dasturchining eng yaxshi do'sti kim? Google! 🔍",
            "Nima uchun dasturchi cho'l sevmaydi? Chunki u yerda cache yo'q! 🏜️",
            "Dasturchi qahvaxonada nima ichadi? Java! ☕",
            "Nega dasturchi Halloweenni yaxshi ko'radi? Chunki Oct 31 = Dec 25! 🎃",
            "Git commit qilishni unutsang, bug kelmasa ham keladi! 🐛",
            "Frontend dasturchi shimolga bordi, CSS'ni yo'qotdi! ❄️",
        ]
        
        self.motivations = [
            "Har bir katta yutuq kichik qadamlardan boshlanadi! 💪",
            "Bugun qiyin, ertaga oson bo'ladi. Davom eting! 🚀",
            "Siz buni uddalay olasiz! Muvaffaqiyat sizniki! ⭐",
            "Xatolar o'rganish imkoniyatidir. Davom eting! 📚",
            "Katta orzular katta harakatlarni talab qiladi! 🎯",
            "O'zizga ishoning, siz hamma narsani uddalaysiz!",
            "Hech qachon to'xtamang, eng baland cho'qqilar hali oldinda!",
            "Muvaffaqiyat - bu har kuni bir oz yaxshiroq bo'lishdir! 🌱",
            "Bugun qilgan ishingiz, ertangi siz uchun poydevor! 🧱",
            "Aqlli odam o'rganishni hech qachon to'xtatmaydi! 🧠",
        ]
        
        self.facts = [
            "Birinchi kompyuter dasturini Augusta Ada Lovelace yozgan, 1843 yilda!",
            "Internetdagi birinchi veb-sayt info.cern.ch edi, 1991 yilda.",
            "Python dasturlash tili ilon emas, Monty Python shousi sharafiga nomlangan!",
            "Dunyadagi eng ko'p ishlatiladigan parol hali ham '123456'!",
            "Google nomi 'googol' (1 dan keyin 100 ta nol) so'zidan kelib chiqqan.",
            "Inson miyasi dunyodagi eng kuchli superkompyuterdan ham murakkabroq!",
            "O'zbekistonda birinchi marta kompyuter tarmog'i 1990-yillarda paydo bo'lgan.",
            "Wi-Fi aslida hech nimaning qisqartmasi emas, u marketing nomi!",
            "Dunyodagi birinchi kompyuter virusi 1986 yilda yaratilgan - 'Brain' deb atalgan.",
            "YouTube'dagi birinchi video 'Me at the zoo' - 2005 yil 23 aprelda yuklangan.",
            "Har soniyada taxminan 6,000 ta tvit yoziladi!",
            "Birinchi SMS xabar 1992 yilda yuborilgan: 'Merry Christmas'!",
        ]
        
        self.compliments = [
            "Siz juda aqllisiz! 🌟",
            "Sizning savolingiz juda yaxshi! 👏",
            "Siz bilan ishlash menga yoqadi! 😊",
            "Ajoyib fikr! Davom eting! 💡",
            "Sizday aqlli foydalanuvchim bor ekanligidan xursandman! 🎉",
        ]
    
    def tell_joke(self) -> str:
        return random.choice(self.jokes)
    
    def motivate(self) -> str:
        return random.choice(self.motivations)
    
    def tell_fact(self) -> str:
        return random.choice(self.facts)
    
    def compliment(self) -> str:
        return random.choice(self.compliments)
    
    def get_day_info(self) -> str:
        """Kun haqida ma'lumot"""
        now = datetime.now()
        day_of_year = now.timetuple().tm_yday
        days_left = 365 - day_of_year
        week_number = now.isocalendar()[1]
        return f"Bugun yilning {day_of_year}-kuni, {week_number}-hafta. Yil oxirigacha {days_left} kun qoldi."
    
    def calculate_age(self, birth_year: int) -> str:
        current_year = datetime.now().year
        age = current_year - birth_year
        return f"Agar {birth_year} yilda tug'ilgan bo'lsangiz, sizga {age} yosh."
    
    def convert_currency_info(self) -> str:
        return "Hozircha valyuta kurslari API'si ulanmagan. Tez orada qo'shiladi!"
    
    def get_random_number(self, min_val: int = 1, max_val: int = 100) -> str:
        num = random.randint(min_val, max_val)
        return f"Tasodifiy son: {num}"
    
    def flip_coin(self) -> str:
        result = random.choice(["Bosh", "Yozuv"])
        return f"Tanga tashlandi: {result}!"
    
    def roll_dice(self) -> str:
        num = random.randint(1, 6)
        return f"Zar tashlandi: {num} 🎲"
    
    def get_week_day(self, days_offset: int = 0) -> str:
        weekdays = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
        target = datetime.now() + timedelta(days=days_offset)
        return weekdays[target.weekday()]
    
    def days_until(self, month: int, day: int) -> str:
        now = datetime.now()
        target = datetime(now.year, month, day)
        if target < now:
            target = datetime(now.year + 1, month, day)
        delta = (target - now).days
        return f"{delta} kun qoldi."
    
    def open_social(self, platform: str) -> str:
        """Ijtimoiy tarmoqlarni ochish"""
        urls = {
            "youtube": "https://youtube.com",
            "telegram": "https://web.telegram.org",
            "instagram": "https://instagram.com",
            "facebook": "https://facebook.com",
            "twitter": "https://twitter.com",
            "tiktok": "https://tiktok.com",
            "linkedin": "https://linkedin.com",
            "github": "https://github.com",
        }
        url = urls.get(platform.lower())
        if url:
            webbrowser.open(url)
            return f"{platform.capitalize()} ochilmoqda."
        return f"Kechirasiz, {platform} topilmadi."
    
    def get_ip_info(self) -> str:
        try:
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return f"Kompyuter nomi: {hostname}, IP manzil: {ip}"
        except:
            return "IP manzilni olishda xatolik."
    
    # ===== YANGI FUNKSIYALAR =====
    
    def generate_password(self, length: int = 16) -> str:
        """Kuchli parol generatsiyasi"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(length))
        return f"🔐 Yangi kuchli parol: {password}"
    
    def count_words(self, text: str) -> str:
        """So'zlar va belgilar soni"""
        words = len(text.split())
        chars = len(text)
        chars_no_space = len(text.replace(" ", ""))
        return f"📊 {words} ta so'z, {chars} ta belgi ({chars_no_space} ta bo'shliqsiz)."
    
    def translate_simple(self, text: str, target: str = "en") -> str:
        """Oddiy tarjima (internet orqali)"""
        try:
            import urllib.parse
            import urllib.request
            # Google Translate API (unofficial)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target}&dt=t&q={urllib.parse.quote(text)}"
            headers = {"User-Agent": "Mozilla/5.0"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                translated = data[0][0][0]
                source_lang = data[2]
                return f"🌐 [{source_lang} → {target}]: {translated}"
        except Exception as e:
            return f"Tarjima qilishda xatolik: {e}"
    
    def start_timer(self, seconds: int) -> str:
        """Oddiy timer (asinxron emas, faqat xabar beradi)"""
        if seconds <= 0:
            return "Noto'g'ri vaqt. Masalan: '30 soniya taymer' deb ayting."
        minutes = seconds // 60
        secs = seconds % 60
        if minutes > 0:
            return f"⏱️ Taymer {minutes} daqiqa {secs} soniyaga o'rnatildi."
        return f"⏱️ Taymer {seconds} soniyaga o'rnatildi."
    
    def get_disk_space(self) -> str:
        """Disk hajmi"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("C:\\")
            total_gb = total // (1024**3)
            used_gb = used // (1024**3)
            free_gb = free // (1024**3)
            percent = int((used / total) * 100)
            return f"💾 C disk: {used_gb}GB/{total_gb}GB ishlatilgan ({percent}%). Bo'sh joy: {free_gb}GB."
        except:
            return "Disk ma'lumotini olishda xatolik."
    
    def list_running_apps(self) -> str:
        """Ishga tushirilgan dasturlar"""
        try:
            import psutil
            apps = set()
            for proc in psutil.process_iter(['name']):
                name = proc.info['name']
                if name and not name.startswith('svchost') and not name.startswith('System'):
                    clean = name.replace('.exe', '')
                    if len(clean) > 2:
                        apps.add(clean)
            
            app_list = sorted(list(apps))[:20]
            return f"📋 Ishga tushirilgan dasturlar ({len(app_list)} ta):\n" + ", ".join(app_list)
        except:
            return "Dasturlar ro'yxatini olishda xatolik."
    
    def system_uptime(self) -> str:
        """Tizim qancha vaqtdan beri ishlayapti"""
        try:
            import psutil
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            return f"⏰ Kompyuter {uptime.days} kun, {hours} soat, {minutes} daqiqadan beri ishlayapti."
        except:
            return "Tizim vaqtini olishda xatolik."


# Global instance
smart = SmartCommands()
