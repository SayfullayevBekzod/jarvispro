"""
Media boshqaruvi - Musiqa, video
"""

import os
import subprocess
from typing import Dict, Any

try:
    from pycaw.pycaw import AudioUtilities
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False


class MediaFeatures:
    """Media boshqaruvi"""
    
    def __init__(self):
        self.music_dir = os.path.expanduser("~/Music")
    
    def play_music(self) -> str:
        """Musiqa qo'yish"""
        try:
            # Windows Media Player yoki default player
            if os.path.exists(self.music_dir):
                files = [f for f in os.listdir(self.music_dir) 
                        if f.endswith(('.mp3', '.wav', '.wma', '.m4a'))]
                if files:
                    os.startfile(os.path.join(self.music_dir, files[0]))
                    return "Musiqa ijro etilmoqda."
            return "Musiqa papkasida fayllar topilmadi."
        except Exception as e:
            return f"Musiqani qo'yishda xatolik: {str(e)}"
    
    def pause_media(self) -> str:
        """Media to'xtatish (Windows klavish simulyatsiya)"""
        try:
            import pyautogui
            pyautogui.press('playpause')
            return "Media to'xtatildi."
        except:
            return "Media boshqaruvida xatolik."
    
    def resume_media(self) -> str:
        """Media davom ettirish"""
        try:
            import pyautogui
            pyautogui.press('playpause')
            return "Media davom etmoqda."
        except:
            return "Media boshqaruvida xatolik."
    
    def next_track(self) -> str:
        """Keyingi trek"""
        try:
            import pyautogui
            pyautogui.press('nexttrack')
            return "Keyingi trekka o'tildi."
        except:
            return "Media boshqaruvida xatolik."
    
    def previous_track(self) -> str:
        """Oldingi trek"""
        try:
            import pyautogui
            pyautogui.press('prevtrack')
            return "Oldingi trekka qaytildi."
        except:
            return "Media boshqaruvida xatolik."
    
    def execute(self, action: str, params: Dict[str, Any]) -> str:
        """Buyruqni bajarish"""
        if action == "play":
            return self.play_music()
        elif action == "pause":
            return self.pause_media()
        elif action == "resume":
            return self.resume_media()
        elif action == "next":
            return self.next_track()
        elif action == "previous":
            return self.previous_track()
        
        return "Kechirasiz, bu buyruqni bajara olmadim."


# Global instance
media = MediaFeatures()
