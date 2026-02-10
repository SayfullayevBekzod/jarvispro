"""
Keyboard - Yozish, clipboard va ilova ichidagi boshqaruv
"""

import time
import subprocess
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


class KeyboardFeatures:
    """Kengaytirilgan klaviatura boshqaruvi"""
    
    def __init__(self):
        if PYAUTOGUI_AVAILABLE:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
    
    # ============== YOZISH ==============
    def type_text(self, text: str, interval: float = 0.05) -> str:
        """Matnni yozish"""
        if not PYAUTOGUI_AVAILABLE:
            return "Yozish funksiyasi uchun pyautogui kerak."
        try:
            time.sleep(0.5)
            pyautogui.write(text, interval=interval)
            return f"'{text[:30]}...' yozildi."
        except Exception as e:
            return f"Yozishda xatolik: {e}"
    
    def type_text_unicode(self, text: str) -> str:
        """Unicode matnni yozish (kirill, lotin)"""
        if not PYAUTOGUI_AVAILABLE:
            return "Yozish funksiyasi uchun pyautogui kerak."
        try:
            time.sleep(0.5)
            if PYPERCLIP_AVAILABLE:
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            else:
                pyautogui.typewrite(text, interval=0.05)
            return f"'{text[:30]}...' yozildi."
        except Exception as e:
            return f"Yozishda xatolik: {e}"
    
    # ============== TUGMALAR ==============
    def press_key(self, key: str) -> str:
        """Bitta tugmani bosish"""
        if not PYAUTOGUI_AVAILABLE:
            return "Klaviatura funksiyasi uchun pyautogui kerak."
        try:
            pyautogui.press(key)
            return f"'{key}' tugmasi bosildi."
        except Exception as e:
            return f"Tugma bosishda xatolik: {e}"
    
    def hotkey(self, *keys) -> str:
        """Tugmalar kombinatsiyasi"""
        if not PYAUTOGUI_AVAILABLE:
            return "Klaviatura funksiyasi uchun pyautogui kerak."
        try:
            pyautogui.hotkey(*keys)
            return "Tugmalar kombinatsiyasi bajarildi."
        except Exception as e:
            return f"Tugmalar kombinatsiyasida xatolik: {e}"
    
    # ============== CLIPBOARD ==============
    def copy(self) -> str:
        return self.hotkey('ctrl', 'c')
    
    def paste(self) -> str:
        return self.hotkey('ctrl', 'v')
    
    def cut(self) -> str:
        return self.hotkey('ctrl', 'x')
    
    def select_all(self) -> str:
        return self.hotkey('ctrl', 'a')
    
    def read_clipboard(self) -> str:
        """Clipboarddagi matnni o'qish"""
        if PYPERCLIP_AVAILABLE:
            try:
                text = pyperclip.paste()
                if text:
                    return f"Clipboardda: {text[:200]}"
                return "Clipboard bo'sh."
            except:
                return "Clipboardni o'qishda xatolik."
        return "pyperclip kutubxonasi kerak."
    
    def clipboard_to_search(self) -> str:
        """Clipboarddagi matnni Googleda qidirish"""
        if PYPERCLIP_AVAILABLE:
            try:
                text = pyperclip.paste()
                if text:
                    import webbrowser, urllib.parse
                    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(text[:100])}")
                    return f"'{text[:30]}...' Google'da qidirilmoqda."
                return "Clipboard bo'sh."
            except:
                return "Qidirishda xatolik."
        return "pyperclip kutubxonasi kerak."
    
    # ============== APP-SPECIFIC SHORTCUTS ==============
    def undo(self) -> str:
        return self.hotkey('ctrl', 'z')
    
    def redo(self) -> str:
        return self.hotkey('ctrl', 'y')
    
    def save(self) -> str:
        return self.hotkey('ctrl', 's')
    
    def find(self) -> str:
        """Topish (Ctrl+F)"""
        return self.hotkey('ctrl', 'f')
    
    def new_file(self) -> str:
        """Yangi (Ctrl+N)"""
        return self.hotkey('ctrl', 'n')
    
    def print_page(self) -> str:
        """Chop etish (Ctrl+P)"""
        return self.hotkey('ctrl', 'p')
    
    # ============== BROWSER TAB CONTROL ==============
    def new_tab(self) -> str:
        """Yangi tab (Ctrl+T)"""
        self.hotkey('ctrl', 't')
        return "Yangi tab ochildi."
    
    def close_tab(self) -> str:
        """Tabni yopish (Ctrl+W)"""
        self.hotkey('ctrl', 'w')
        return "Tab yopildi."
    
    def refresh_page(self) -> str:
        """Sahifani yangilash (F5)"""
        self.press_key('f5')
        return "Sahifa yangilandi."
    
    def switch_tab(self, direction: str = "next") -> str:
        """Tab o'zgartirish"""
        if direction == "next":
            self.hotkey('ctrl', 'tab')
            return "Keyingi tabga o'tildi."
        else:
            self.hotkey('ctrl', 'shift', 'tab')
            return "Oldingi tabga qaytildi."
    
    def address_bar(self) -> str:
        """Manzil satriga o'tish (Ctrl+L)"""
        self.hotkey('ctrl', 'l')
        return "Manzil satri tanlandi."
    
    def open_url_in_browser(self, url: str) -> str:
        """Brauzerda URL ochish"""
        self.hotkey('ctrl', 'l')
        time.sleep(0.3)
        if PYPERCLIP_AVAILABLE:
            pyperclip.copy(url)
            self.hotkey('ctrl', 'v')
        else:
            pyautogui.write(url, interval=0.02)
        time.sleep(0.2)
        self.press_key('enter')
        return f"'{url[:40]}' brauzerda ochilmoqda."
    
    # ============== WINDOW SHORTCUTS ==============
    def zoom_in(self) -> str:
        self.hotkey('ctrl', 'plus')
        return "Kattalashtrildi."
    
    def zoom_out(self) -> str:
        self.hotkey('ctrl', 'minus')
        return "Kichraytirildi."
    
    def full_screen(self) -> str:
        self.press_key('f11')
        return "To'liq ekran rejimiga o'tildi."
    
    def alt_tab(self) -> str:
        """Dasturlar orasida o'tish"""
        self.hotkey('alt', 'tab')
        return "Boshqa dasturga o'tildi."
    
    def screenshot_region(self) -> str:
        """Ekranning bir qismini suratga olish"""
        self.hotkey('win', 'shift', 's')
        return "Ekran qismini tanlang."
    
    # ============== EXECUTE ==============
    def execute(self, action: str, params: dict) -> str:
        """Buyruqni bajarish"""
        if action == "type":
            return self.type_text_unicode(params.get("text", ""))
        elif action == "press":
            return self.press_key(params.get("key", ""))
        elif action == "copy":
            return self.copy()
        elif action == "paste":
            return self.paste()
        elif action == "cut":
            return self.cut()
        elif action == "select_all":
            return self.select_all()
        elif action == "undo":
            return self.undo()
        elif action == "redo":
            return self.redo()
        elif action == "save":
            return self.save()
        elif action == "find":
            return self.find()
        elif action == "new":
            return self.new_file()
        elif action == "print":
            return self.print_page()
        # Browser
        elif action == "new_tab":
            return self.new_tab()
        elif action == "close_tab":
            return self.close_tab()
        elif action == "refresh":
            return self.refresh_page()
        elif action == "switch_tab":
            return self.switch_tab(params.get("direction", "next"))
        elif action == "address_bar":
            return self.address_bar()
        elif action == "open_url":
            return self.open_url_in_browser(params.get("url", ""))
        # Clipboard
        elif action == "read_clipboard":
            return self.read_clipboard()
        elif action == "clipboard_search":
            return self.clipboard_to_search()
        # Window
        elif action == "zoom_in":
            return self.zoom_in()
        elif action == "zoom_out":
            return self.zoom_out()
        elif action == "full_screen":
            return self.full_screen()
        elif action == "alt_tab":
            return self.alt_tab()
        elif action == "screenshot_region":
            return self.screenshot_region()
        else:
            return "Noma'lum klaviatura buyrug'i."


# Global instance
keyboard = KeyboardFeatures()
