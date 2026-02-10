"""
O'zbekcha Speech Engine
- STT: Google Speech Recognition (uz-UZ)
- TTS: AiVOOV (Sardor - O'zbek erkak ovozi)
"""

import os
import io
import wave
import base64
import tempfile
import threading
from typing import Optional, Callable
import requests
import pygame
from openai import OpenAI
import google.generativeai as genai
import asyncio
import edge_tts
import threading

import config


class SpeechEngine:
    """O'zbekcha ovoz aniqlash va gapirish (Gemini/OpenAI + gTTS)"""
    
    def __init__(self):
        # Gemini Client
        if config.AI_PROVIDER == "gemini":
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # OpenAI Client (STT va Fallback uchun)
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # AiVOOV TTS (Old version support)
        self.aivoov_api_key = config.AIVOOV_API_KEY
        self.aivoov_tts_url = config.AIVOOV_TTS_URL
        self.aivoov_voice_id = config.AIVOOV_VOICE_ID
        
        # Pygame mixer
        pygame.mixer.init()
        print("[Speech Engine] OpenAI stack tayyor")
    
    def listen_auto(self) -> Optional[bytes]:
        """
        Silence aniqlanguncha tinglash va audio ma'lumotni qaytarish
        Pro hearing: Dynamic threshold va noise filtration
        """
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            
            # Pro Parameters
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            recognizer.dynamic_energy_adjustment_damping = 0.15
            recognizer.dynamic_energy_ratio = 1.5
            recognizer.pause_threshold = 0.8  # Gapni tugatganini kutish
            recognizer.non_speaking_duration = 0.5
            
            with sr.Microphone() as source:
                print(f"[Speech Engine] Pro Hearing faol. Mik: {source.device_index}")
                # Shovqinni agressivroq o'lchash
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                print(f"[Speech Engine] Shovqin darajasi: {int(recognizer.energy_threshold)}")
                
                try:
                    # Timeouts
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=12)
                    return audio.get_wav_data()
                except sr.WaitTimeoutError:
                    return None
        except Exception as e:
            print(f"[Speech Engine] Pro-listen xato: {e}")
            return None

    def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """
        Ovozni matnga aylantirish (Google STT asosiy + Whisper fallback)
        """
        if not audio_data:
            return None
        
        # 1. Google Speech Recognition (Asosiy - bepul va ishonchli)
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            audio_file = io.BytesIO(audio_data)
            
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
            
            # Ketma-ket tekshirish: Uz -> En -> Ru
            for lang in ["uz-UZ", "en-US", "ru-RU"]:
                try:
                    text = recognizer.recognize_google(audio, language=lang)
                    print(f"[Google STT] {lang}: {text}")
                    return text
                except sr.UnknownValueError:
                    continue
        except Exception as e:
            print(f"[Google STT] Xato: {e}")
            
        # 2. OpenAI Whisper (Fallback - agar Google ishlamasa)
        if not getattr(self, '_whisper_disabled', False) and "YOUR_OPENAI_API_KEY_HERE" not in config.OPENAI_API_KEY:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
                    f.write(audio_data)
                    temp_path = f.name

                with open(temp_path, "rb") as audio_file:
                    transcription = self.openai_client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=audio_file
                    )
                
                os.unlink(temp_path)
                text = transcription.text
                print(f"[Whisper STT] {text}")
                return text
            except Exception as e:
                print(f"[Whisper STT] Xato: {e}")
                # 403 yoki authentication xatosi bo'lsa, Whisper-ni o'chirib qo'yamiz
                if "403" in str(e) or "401" in str(e) or "model_not_found" in str(e):
                    self._whisper_disabled = True
                    print("[Whisper STT] API kalit ishlamayapti, Whisper o'chirildi. Google STT ishlatiladi.")

        return None
    
    def _detect_language(self, text: str) -> str:
        """Matn tilini aniqlash (uz yoki en)"""
        # Oddiy heuristika: ko'p ishlatiladigan inglizcha so'zlar
        en_words = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "not", "to", "of", "in", "it", "i", "you", "my"}
        text_words = set(text.lower().split())
        
        # Agar inglizcha so'zlar bo'lsa yoki lotin alifbosi (O'zbekchada ham lotin, lekin En specific so'zlar muhim)
        if text_words.intersection(en_words):
            return "en"
        
        # O'zbekcha fallback (ko'proq ehtimol)
        return "uz"

    def text_to_speech(self, text: str, callback: Optional[Callable] = None) -> bool:
        """
        Matnni ovozga aylantirish (Edge TTS - Bilingual)
        """
        if not text:
            if callback: callback()
            return False
            
        try:
            lang = self._detect_language(text)
            print(f"[Edge TTS] Language: {lang}, Text: '{text[:40]}...'")
            
            def run_edge_tts():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Tilga qarab ovoz tanlash
                    if lang == "en":
                        voice = "en-US-AndrewMultilingualNeural" 
                    elif config.ALICE_MODE:
                        # Alisa rejimi uchun ruscha ayol ovozi (Alice-ga yaqin)
                        voice = "ru-RU-SvetlanaNeural"
                    else:
                        voice = "uz-UZ-SardorNeural"
                        
                    temp_path = tempfile.mktemp(suffix=".mp3")
                    
                    communicate = edge_tts.Communicate(text, voice)
                    loop.run_until_complete(communicate.save(temp_path))
                    
                    self.after_main_thread(lambda: self._play_audio(temp_path, callback))
                    return True
                except Exception as e:
                    print(f"[Edge TTS] Xato: {e}")
                    self.after_main_thread(lambda: self._aivoov_fallback(text, callback))
                    return False
            
            threading.Thread(target=run_edge_tts, daemon=True).start()
            return True
                
        except Exception as e:
            print(f"[TTS] Xato: {e}")
            return self._aivoov_fallback(text, callback)

    def after_main_thread(self, func):
        """Timer yoki thread orqali yuborish (agar kerak bo'lsa)"""
        func()

    def _aivoov_fallback(self, text: str, callback: Optional[Callable] = None) -> bool:
        """AiVOOV fallback"""
        if config.AIVOOV_API_KEY == "YOUR_AIVOOV_API_KEY_HERE":
            return self._pyttsx3_fallback(text, callback)
            
        try:
            headers = {"X-API-KEY": self.aivoov_api_key, "Content-Type": "application/x-www-form-urlencoded"}
            data = {"voice_id[]": self.aivoov_voice_id, "transcribe_text[]": text}
            response = requests.post(self.aivoov_tts_url, headers=headers, data=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('status'):
                    audio_bytes = base64.b64decode(result.get('audio', ''))
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                        f.write(audio_bytes)
                        self._play_audio(f.name, callback)
                        return True
            return self._pyttsx3_fallback(text, callback)
        except:
            return self._pyttsx3_fallback(text, callback)
    
    def _pyttsx3_fallback(self, text: str, callback: Optional[Callable] = None) -> bool:
        """Lokal pyttsx3 fallback (Offline)"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            print("[pyttsx3] Offline fallback...")
            engine.say(text)
            engine.runAndWait()
            if callback: callback()
            return True
        except:
            if callback: callback()
            return False
    
    def _gtts_fallback(self, text: str, callback: Optional[Callable] = None) -> bool:
        """gTTS fallback (rus tilida)"""
        try:
            from gtts import gTTS
            
            print(f"[gTTS Fallback] Matn: '{text[:30]}...'")
            
            tts = gTTS(text=text, lang='ru', slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                tts.save(f.name)
                temp_path = f.name
            
            self._play_audio(temp_path, callback)
            return True
            
        except Exception as e:
            print(f"[gTTS] Xato: {e}")
            if callback:
                callback()
            return False
    
    def _play_audio(self, file_path: str, callback: Optional[Callable] = None):
        """Audio faylni ijro etish"""
        def play():
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.set_volume(config.VOICE_VOLUME)
                pygame.mixer.music.play()
                
                print("[Audio] Ijro etilmoqda...")
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                print("[Audio] Tugadi")
                
                try:
                    os.unlink(file_path)
                except:
                    pass
                    
                if callback:
                    callback()
                    
            except Exception as e:
                print(f"[Audio] Xato: {e}")
                if callback:
                    callback()
        
        thread = threading.Thread(target=play, daemon=True)
        thread.start()
    
    def chat(self, message: str, context: list = None) -> Optional[str]:
        """Gemini yoki OpenAI orqali suhbat"""
        # 1. Gemini Provider
        if config.AI_PROVIDER == "gemini":
            if "YOUR_GEMINI_API_KEY_HERE" in config.GEMINI_API_KEY:
                return "Kechirasiz, Gemini API kaliti sozlanmagan."
            
            try:
                # Kontekstni Gemini formatiga o'tkazish
                history = []
                if context:
                    for msg in context:
                        role = "user" if msg.get("role") == "user" else "model"
                        history.append({"role": role, "parts": [msg.get("content", "")]})
                
                chat = self.gemini_model.start_chat(history=history)
                if config.ALICE_MODE:
                    system_instruction = (
                        f"Имя вашего персонажа - Алиса. Вы - умный и остроумный голосовой помощник от Яндекса. "
                        f"Вы вежливы, но можете позволить себе немного юмора. Вы помогаете пользователю управлять компьютером. "
                        f"Пожалуйста, отвечайте на русском языке (или на узбекском/английском, если пользователь обращается на них)."
                    )
                else:
                    system_instruction = (
                        f"Sizning ismingiz {config.JARVIS_NAME}. Siz 'Jarvis Pro' darajasidagi premium ovozli yordamchisiz. "
                        f"Sizda kompyuterni to'liq boshqarish, dasturlarni yopish, tizim holatini tekshirish va automation macros (Xonani tozalash, Dars rejimi) imkoniyatlari mavjud. "
                        f"Siz juda aqlli, do'stona va professional muomala qilasiz. Foydalanuvchi qaysi tilda (O'zbek yoki Ingliz) gapirsa, "
                        f"siz ham o'sha tilda javob berasiz va kerak bo'lsa tizimni boshqarish bo'yicha maslahatlar berasiz."
                    )
                
                # Agar tarix bo'sh bo'lsa, tizim ko'rsatmasini qo'shish (Gemini 1.5 uchun)
                response = chat.send_message(f"{system_instruction}\n\nUser: {message}")
                answer = response.text
                print(f"[Gemini] Javob: {answer[:50]}...")
                return answer
            except Exception as e:
                print(f"[Gemini] Xato: {e}")
                return "Kechirasiz, Gemini bilan bog'lanishda xatolik yuz berdi."

        # 2. OpenAI Provider (Fallback yoki tanlov)
        if config.AI_PROVIDER == "openai":
            if "YOUR_OPENAI_API_KEY_HERE" in config.OPENAI_API_KEY:
                return "Kechirasiz, OpenAI API kaliti sozlanmagan."

            try:
                if config.ALICE_MODE:
                    system_prompt = (
                        f"Your character's name is Alice (Alisa). You are a witty and helpful AI assistant from Yandex. "
                        f"You are polite yet can be slightly humorous. Please respond in Russian by default "
                        f"(or Uzbek/English if the user speaks to you in those languages)."
                    )
                else:
                    system_prompt = (
                        f"Your name is {config.JARVIS_NAME}. You are a 'Jarvis Pro' level premium voice assistant. "
                        f"You have full computer control, process management, and automation capabilities. "
                        f"You are professional, intelligent, and friendly. Please respond in the same language as the user (Uzbek or English) "
                        f"and provide helpful advice on system management when relevant."
                    )
                messages = [{"role": "system", "content": system_prompt}]
                if context:
                    for msg in context:
                        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
                messages.append({"role": "user", "content": message})
                
                response = self.openai_client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages,
                    temperature=0.7
                )
                answer = response.choices[0].message.content
                print(f"[GPT-4] Javob: {answer[:50]}...")
                return answer
            except Exception as e:
                print(f"[GPT-4] Xato: {e}")
                return "Kechirasiz, GPT bilan bog'lanishda xatolik yuz berdi."
        
        return "AI provayderi noto'g'ri sozlangan."


class AudioRecorder:
    """Mikrofondan ovoz yozish"""
    
    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.chunk = 1024
        self.is_recording = False
        self.frames = []
        self.audio = None
        self.stream = None
        
    def start_recording(self) -> bool:
        """Ovoz yozishni boshlash"""
        try:
            import pyaudio
            
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            self.is_recording = True
            self.frames = []
            
            self.record_thread = threading.Thread(target=self._record, daemon=True)
            self.record_thread.start()
            
            print("[Mikrofon] Yozish boshlandi")
            return True
            
        except Exception as e:
            print(f"[Xato] Mikrofon: {e}")
            return False
    
    def _record(self):
        """Ovoz yozish loop"""
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except:
                break
    
    def stop_recording(self) -> bytes:
        """Ovoz yozishni to'xtatish"""
        self.is_recording = False
        
        if hasattr(self, 'record_thread') and self.record_thread:
            self.record_thread.join(timeout=1)
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
        
        print(f"[Mikrofon] Yozish to'xtadi. {len(self.frames)} frame")
        
        # WAV formatga aylantirish
        if self.frames:
            import pyaudio
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.frames))
            
            return buffer.getvalue()
        
        return b''


# Global instances (eski nomlar bilan orqaga mos)
muxlisa = SpeechEngine()
recorder = AudioRecorder()
