"""
Umumiy buyruqlar - Salomlashish, vaqt, sana
"""

import datetime
import random
from typing import Dict, Any


class GeneralFeatures:
    """Umumiy funksiyalar"""
    
    def __init__(self):
        self.greetings = [
            "Salom! Sizga qanday yordam bera olaman?",
            "Assalomu alaykum! Xizmatingizdaman!",
            "Salom! Buyuring, tinglayapman.",
            "Ha, eshitayapman. Qanday yordam kerak?",
            "Salom, sizga yordam berishdan xursandman!",
            "Eshitaman, sizga nima kerak?",
            "Salom, buyruqlaringizni kutyapman!"
        ]
        
        self.goodbyes = [
            "Xayr! Yaxshi kun tilayman!",
            "Ko'rishguncha! Menga murojaat qilganingiz uchun rahmat!",
            "Mayli, xayr! Yana murojaat qiling!",
            "Yaxshi dam oling! Ko'rishguncha!",
            "Salomat bo'ling!",
            "Keyingi safargacha xayr!"
        ]
        
        self.how_are_you_responses = [
            "Yaxshi! Rahmat so'raganingiz uchun. Sizga qanday yordam bera olaman?",
            "Ajoyib! Sizga xizmat qilishga tayyorman!",
            "Zo'rman! Sizni yana ko'rganimdan xursandman!",
            "Hammasi joyida! Siz-chi, qalaysiz?",
            "Rahmat, hammasi a'lo darajada. O'zingizda nima gaplar?",
            "Yaxshi, doimiy tayyorman!"
        ]
        
        # Uzbek months
        self.months = {
            1: "yanvar", 2: "fevral", 3: "mart", 4: "aprel",
            5: "may", 6: "iyun", 7: "iyul", 8: "avgust",
            9: "sentyabr", 10: "oktyabr", 11: "noyabr", 12: "dekabr"
        }
        
        # Uzbek weekdays
        self.weekdays = {
            0: "dushanba", 1: "seshanba", 2: "chorshanba",
            3: "payshanba", 4: "juma", 5: "shanba", 6: "yakshanba"
        }
    
    def greet(self) -> str:
        """Salomlashish"""
        now = datetime.datetime.now()
        hour = now.hour
        
        if 5 <= hour < 12:
            time_greeting = "Hayrli tong"
        elif 12 <= hour < 17:
            time_greeting = "Hayrli kun"
        elif 17 <= hour < 22:
            time_greeting = "Hayrli kech"
        else:
            time_greeting = "Hayrli tun"
        
        return f"{time_greeting}! {random.choice(self.greetings)}"
    
    def goodbye(self) -> str:
        """Xayrlashish"""
        return random.choice(self.goodbyes)
    
    def how_are_you(self) -> str:
        """Holat so'rash javob"""
        return random.choice(self.how_are_you_responses)
    
    def get_time(self) -> str:
        """Hozirgi vaqtni aytish"""
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        
        return f"Hozir soat {hour} va {minute} daqiqa."
    
    def get_date(self) -> str:
        """Bugungi sanani aytish"""
        now = datetime.datetime.now()
        day = now.day
        month = self.months[now.month]
        year = now.year
        weekday = self.weekdays[now.weekday()]
        
        return f"Bugun {year} yil {day} {month}, {weekday}."
    
    def execute(self, action: str, params: Dict[str, Any]) -> str:
        """Buyruqni bajarish"""
        if action == "hello":
            return self.greet()
        elif action == "goodbye":
            return self.goodbye()
        elif action == "how_are_you":
            return self.how_are_you()
        elif action == "time":
            return self.get_time()
        elif action == "date":
            return self.get_date()
        else:
            return "Kechirasiz, tushunmadim."


# Global instance
general = GeneralFeatures()
