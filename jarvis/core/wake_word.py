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
            self.recognizer.energy_threshold = 150
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.35  # Tezroq aniqlash uchun
            self.recognizer.non_speaking_duration = 0.3
    
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
                while not self._stop_event.is_set():
                    if not self.is_listening:
                        time.sleep(0.5)
                        continue
                        
                    print(f"[Wake Word] Mikrofon ochilmoqda...")
                    try:
                        with sr.Microphone() as source:
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            print(f"[Wake Word] Tinglamoqda (Shovqin: {int(self.recognizer.energy_threshold)})")
                            
                            while self.is_listening and not self._stop_event.is_set():
                                try:
                                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
                                    
                                    # Recognition
                                    text = ""
                                    try:
                                        text = self.recognizer.recognize_google(audio, language="en-US").lower()
                                    except:
                                        try:
                                            text = self.recognizer.recognize_google(audio, language="uz-UZ").lower()
                                        except: pass
                                    
                                    if text:
                                        print(f"[Wake Word] Eshitildi: '{text}'")
                                        if any(word.lower() in text for word in self.wake_words):
                                            print(f"[Wake Word] Trigger!")
                                            self._trigger_callback()
                                            # Callback trigger bo'lganda mikrofondan chiqish kerak 
                                            # chunki Jarvis app listen() ni boshlaydi
                                            break
                                            
                                except sr.WaitTimeoutError:
                                    continue
                                except Exception as e:
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
