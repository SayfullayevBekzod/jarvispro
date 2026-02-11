"""
Wake Word Detector - "Jarvis" so'zini aniqlash
Orqa fonda doimiy tinglaydi
"""

import io
import wave
import threading
import time
from typing import Callable, Optional

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

import config


class WakeWordDetector:
    """Wake word (Jarvis) aniqlash"""
    
    def __init__(self):
        self.wake_words = config.JARVIS_WAKE_WORDS  # ["jarvis", "жарвис", "jarvi"]
        self.is_listening = False
        self.on_wake_word: Optional[Callable] = None
        self.recognizer = None
        self.microphone = None
        self._stop_event = threading.Event()
        
        if SR_AVAILABLE:
            self.recognizer = sr.Recognizer()
            # Pro Parameters for Wake Word
            self.recognizer.energy_threshold = config.VOICE_VOLUME * 100 # Sensitive default
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.5  # Standard for wake word
            self.recognizer.non_speaking_duration = 0.2
    
    def start(self, callback: Callable):
        """Wake word tinglashni boshlash"""
        if not SR_AVAILABLE:
            print("[Wake Word] SpeechRecognition kutubxonasi topilmadi")
            return
        
        self.on_wake_word = callback
        self.is_listening = True
        self._stop_event.clear()
        
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()
        print("[Wake Word] Jarvis tayyor va tinglamoqda...")
    
    def stop(self):
        """Tinglashni to'xtatish"""
        self.is_listening = False
        self._stop_event.set()
        print("[Wake Word] To'xtatildi")
    
    def pause(self):
        """Vaqtincha to'xtatish"""
        self.is_listening = False
    
    def resume(self):
        """Davom ettirish"""
        self.is_listening = True
    
    def _listen_loop(self):
        """Doimiy tinglash loop"""
        while not self._stop_event.is_set():
            try:
                if not self.is_listening:
                    time.sleep(1.0)
                    continue
                    
                print(f"[Wake Word] Mikrofon ochilmoqda...")
                try:
                    with sr.Microphone() as source:
                        # Faqat bir marta shovqinni o'lchash (barqarorlik uchun)
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                        self.recognizer.dynamic_energy_threshold = True
                        # Sezgirlikni oshirish
                        self.recognizer.energy_threshold = 300 
                        
                        print(f"[Wake Word] Tinglamoqda (Baza Shovqin: {int(self.recognizer.energy_threshold)})")
                        
                        while self.is_listening and not self._stop_event.is_set():
                            try:
                                # phrase_time_limit ni 1.5 ga tushirdik (tezroq javob berish uchun)
                                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=1.5)
                                
                                # Recognition - Parallel kabi tez ishlashi uchun listni qisqartirdik
                                text = ""
                                langs = [f"{config.LANGUAGE}-{config.LANGUAGE.upper()}", "en-US"]
                                langs = list(dict.fromkeys(langs))
                                
                                for lang in langs:
                                    try:
                                        # Google recognition
                                        text = self.recognizer.recognize_google(audio, language=lang).lower()
                                        if text: break
                                    except: continue
                                
                                if text:
                                    print(f"[Wake Word] Eshitildi: '{text}'")
                                    # "Jarvis" so'zi bormi tekshirish
                                    if any(word.lower() in text for word in self.wake_words):
                                        print(f"[Wake Word] TRIGGER DETECTED!")
                                        self._trigger_callback()
                                        break
                                        
                            except sr.WaitTimeoutError:
                                continue
                            except Exception as e:
                                if "Stream closed" not in str(e):
                                    print(f"[Wake Word] Listen xato: {e}")
                                break
                except Exception as e:
                    print(f"[Wake Word] Mikrofon xato: {e}")
                    time.sleep(2)
            except Exception as e:
                print(f"[Wake Word] Loop xatosi: {e}")

    def _trigger_callback(self):
        """Callbackni chaqirish"""
        if self.on_wake_word:
            # UI thread yoki boshqa thread xavfsizligi
            self.on_wake_word()
# Global instance
wake_detector = WakeWordDetector()
