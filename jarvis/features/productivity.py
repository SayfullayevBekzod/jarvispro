"""
Unumdorlik funksiyalari - Eslatmalar, taymerlar, hisoblar
"""

import os
import re
import math
import json
import threading
import datetime
from typing import Dict, Any, List
import time as time_module


class ProductivityFeatures:
    """Unumdorlik funksiyalari"""
    
    def __init__(self):
        self.reminders_file = os.path.join(os.path.dirname(__file__), "..", "data", "reminders.json")
        self.reminders: List[Dict] = []
        self.active_timers: List[threading.Timer] = []
        self.reminder_callback = None
        
        # Data papkasini yaratish
        os.makedirs(os.path.dirname(self.reminders_file), exist_ok=True)
        self._load_reminders()
    
    def _load_reminders(self):
        """Eslatmalarni yuklash"""
        try:
            if os.path.exists(self.reminders_file):
                with open(self.reminders_file, 'r', encoding='utf-8') as f:
                    self.reminders = json.load(f)
        except:
            self.reminders = []
    
    def _save_reminders(self):
        """Eslatmalarni saqlash"""
        try:
            with open(self.reminders_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def set_timer(self, time_value: int, unit: str, callback=None) -> str:
        """Taymer qo'yish"""
        # Sekundga aylantirish
        seconds = time_value
        if unit in ["daqiqa", "minut"]:
            seconds = time_value * 60
        elif unit == "soat":
            seconds = time_value * 3600
        
        def timer_done():
            message = f"Taymer tugadi! {time_value} {unit} o'tdi!"
            if callback:
                callback(message)
            elif self.reminder_callback:
                self.reminder_callback(message)
        
        timer = threading.Timer(seconds, timer_done)
        timer.start()
        self.active_timers.append(timer)
        
        return f"{time_value} {unit}dan keyin eslatib qo'yaman."
    
    def add_reminder(self, text: str) -> str:
        """Eslatma qo'shish"""
        reminder = {
            "text": text,
            "created": datetime.datetime.now().isoformat()
        }
        self.reminders.append(reminder)
        self._save_reminders()
        
        return f"Eslatma saqlandi: {text}"
    
    def list_reminders(self) -> str:
        """Eslatmalarni o'qish"""
        if not self.reminders:
            return "Hozircha eslatmalar yo'q."
        
        result = ["Sizning eslatmalaringiz:"]
        for i, r in enumerate(self.reminders, 1):
            result.append(f"{i}. {r['text']}")
        
        return " ".join(result)
    
    def calculate(self, expression: str) -> str:
        """Matematik hisoblash"""
        expression_lower = expression.lower()
        
        try:
            # Plyus
            match = re.search(r"(\d+)\s*(plyus|\+|qo'sh)\s*(\d+)", expression_lower)
            if match:
                a, b = int(match.group(1)), int(match.group(3))
                result = a + b
                return f"{a} plyus {b} teng {result}."
            
            # Minus
            match = re.search(r"(\d+)\s*(minus|\-|ayir)\s*(\d+)", expression_lower)
            if match:
                a, b = int(match.group(1)), int(match.group(3))
                result = a - b
                return f"{a} minus {b} teng {result}."
            
            # Ko'paytirish
            match = re.search(r"(\d+)\s*(ko'paytir|ko'pay|\*|marta)\s*(\d+)", expression_lower)
            if match:
                a, b = int(match.group(1)), int(match.group(3))
                result = a * b
                return f"{a} ko'paytir {b} teng {result}."
            
            # Bo'lish
            match = re.search(r"(\d+)\s*(bo'l|bo'lib|\:)\s*(\d+)", expression_lower)
            if match:
                a, b = int(match.group(1)), int(match.group(3))
                if b == 0:
                    return "Nolga bo'lish mumkin emas!"
                result = a / b
                if result == int(result):
                    return f"{a} bo'linadi {b} ga, natija {int(result)}."
                return f"{a} bo'linadi {b} ga, natija {result:.2f}."
            
            # Kvadrat
            match = re.search(r"(\d+)\s*ning\s*kvadrat", expression_lower)
            if match:
                a = int(match.group(1))
                result = a ** 2
                return f"{a} ning kvadrati {result}."
            
            # Kub
            match = re.search(r"(\d+)\s*ning\s*kub", expression_lower)
            if match:
                a = int(match.group(1))
                result = a ** 3
                return f"{a} ning kubi {result}."
            
            # Foiz
            match = re.search(r"(\d+)\s*foiz\s*(\d+)", expression_lower)
            if match:
                percent, number = int(match.group(1)), int(match.group(2))
                result = (percent / 100) * number
                return f"{number} ning {percent} foizi {result}."
            
            # Ildiz
            match = re.search(r"(\d+)\s*(ildiz|sqrt)", expression_lower)
            if match:
                a = int(match.group(1))
                result = math.sqrt(a)
                if result == int(result):
                    return f"{a} ning ildizi {int(result)}."
                return f"{a} ning ildizi {result:.2f}."
            
            return "Kechirasiz, bu hisob-kitobni tushunmadim."
            
        except Exception as e:
            return f"Hisoblashda xatolik: {str(e)}"
    
    def execute(self, action: str, params: Dict[str, Any]) -> str:
        """Buyruqni bajarish"""
        if action == "set":
            time_value = params.get("time", 5)
            unit = params.get("unit", "daqiqa")
            return self.set_timer(time_value, unit)
        elif action == "add":
            text = params.get("text", "")
            return self.add_reminder(text)
        elif action == "list":
            return self.list_reminders()
        elif action == "calculate":
            expression = params.get("expression", "")
            return self.calculate(expression)
        
        return "Kechirasiz, bu buyruqni bajara olmadim."


# Global instance
productivity = ProductivityFeatures()
