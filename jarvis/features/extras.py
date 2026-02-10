"""
Qo'shimcha funksiyalar
Ekran surati, clipboard, va boshqalar
"""

import os
import datetime
from typing import Dict, Any

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False


class ExtraFeatures:
    """Qo'shimcha funksiyalar"""
    
    def __init__(self):
        self.screenshots_dir = os.path.expanduser("~/Pictures/Screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def take_screenshot(self) -> str:
        """Ekran suratini olish"""
        if not PYAUTOGUI_AVAILABLE:
            return "Skrinshot olish uchun pyautogui kutubxonasi kerak."
        
        try:
            filename = f"jarvis_screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            return f"Ekran surati saqlandi: {filename}"
        except Exception as e:
            return f"Skrinshot olishda xatolik: {str(e)}"
    
    def copy_to_clipboard(self, text: str) -> str:
        """Matnni clipboard ga nusxalash"""
        if not PYPERCLIP_AVAILABLE:
            return "Clipboard uchun pyperclip kutubxonasi kerak."
        
        try:
            pyperclip.copy(text)
            return "Matn nusxalandi."
        except Exception as e:
            return f"Nusxalashda xatolik: {str(e)}"
    
    def get_clipboard(self) -> str:
        """Clipboard dan o'qish"""
        if not PYPERCLIP_AVAILABLE:
            return "Clipboard uchun pyperclip kutubxonasi kerak."
        
        try:
            text = pyperclip.paste()
            return f"Clipboard: {text[:100]}..." if len(text) > 100 else f"Clipboard: {text}"
        except Exception as e:
            return f"O'qishda xatolik: {str(e)}"
    
    def execute(self, action: str, params: Dict[str, Any]) -> str:
        """Buyruqni bajarish"""
        if action == "screenshot":
            return self.take_screenshot()
        elif action == "copy":
            return self.copy_to_clipboard(params.get("text", ""))
        elif action == "paste":
            return self.get_clipboard()
        
        return "Kechirasiz, bu buyruqni bajara olmadim."


# Global instance
extras = ExtraFeatures()
