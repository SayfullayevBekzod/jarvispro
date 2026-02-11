"""
Jarvis Desktop UI - Premium Pro Version
Ultra-zamonaviy glassmorphism va neon effektlar
"""

import customtkinter as ctk
import threading
import math
import random
import time
from PIL import Image, ImageDraw, ImageFilter
import os
from datetime import datetime

import config
from core.jarvis import jarvis
from core.wake_word import wake_detector
from core.updater import updater
from ui.components import AnimatedBackground, MagneticButton

# Notification ovozlari
try:
    import pygame.mixer
    pygame.mixer.init()
    _SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "sounds")
    _LISTEN_START_SOUND = os.path.join(_SOUNDS_DIR, "listen_start.wav")
    _LISTEN_STOP_SOUND = os.path.join(_SOUNDS_DIR, "listen_stop.wav")
    
    def _play_sound(filepath):
        """Ovozni non-blocking ijro etish"""
        try:
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(0.5)
                sound.play()
        except Exception as e:
            print(f"[Sound] Xato: {e}")
    
    SOUNDS_AVAILABLE = True
except Exception:
    SOUNDS_AVAILABLE = False
    def _play_sound(filepath):
        pass

# Premium rang palitrasi
NEON_CYAN = "#00F5FF"
NEON_MAGENTA = "#FF00FF"
NEON_GOLD = "#FFD700"
GLASS_BG = "#0a0a14"
GLASS_PANEL = "#12121f"
GLASS_CARD = "#1a1a2e"

class PulsingOrb(ctk.CTkCanvas):
    """Ultra-premium pulsating orb animatsiyasi - Jarvis Core Style"""
    def __init__(self, parent, size=240, **kwargs):
        super().__init__(parent, width=size, height=size, 
                         bg=kwargs.get("bg_color", config.BG_COLOR),
                         highlightthickness=0, borderwidth=0)
        self.size = size
        self.center = size // 2
        self.animation_phase = 0
        self.mode = "idle"
        self.is_animating = True
        
        # Ranglar va effektlar
        self.colors = {
            "idle": [NEON_CYAN, "#0088AA", "#004455"],
            "listening": ["#FF6B35", "#CC5500", "#662200"],
            "speaking": [NEON_GOLD, "#AA8800", "#443300"],
            "error": ["#FF4444", "#AA2222", "#551111"]
        }
        
        self._init_particles()
        self._animate()

    def _init_particles(self):
        """Particle tizimi"""
        self.particles = []
        for _ in range(30):
            self.particles.append({
                "angle": random.uniform(0, 2 * math.pi),
                "distance": random.uniform(40, 90),
                "speed": random.uniform(0.02, 0.05),
                "size": random.uniform(1, 3),
                "opacity": random.uniform(0.3, 0.8)
            })

    def draw_active(self, phase, mode="listening"):
        """Dinamik multi-qatlamli animatsiya"""
        self.delete("all")
        colors = self.colors.get(mode, self.colors["idle"])
        main_color = colors[0]
        glow_color = colors[1]
        
        # 1. Tashqi Ambient Glow (pulsating background)
        ambient_r = 100 + math.sin(phase) * 10
        self.create_oval(
            self.center - ambient_r, self.center - ambient_r,
            self.center + ambient_r, self.center + ambient_r,
            fill="", outline=glow_color, width=1, dash=(5, 5)
        )
        
        # 2. Dinamik To'lqinlar (Dynamic Waves)
        num_waves = 4
        for i in range(num_waves):
            # Har bir to'lqin alohida fazada va tezlikda
            wave_phase = phase * (1 + i * 0.2)
            wave_r = 60 + i * 12 + math.sin(wave_phase) * 8
            opacity_factor = max(0.1, 0.8 - (i * 0.2))
            
            self.create_oval(
                self.center - wave_r, self.center - wave_r,
                self.center + wave_r, self.center + wave_r,
                fill="", outline=main_color, width=2, 
                stipple="gray50" if i > 1 else "" # CTK simulation of opacity
            )
            
        # 3. Rotating Particles
        for p in self.particles:
            p["angle"] += p["speed"]
            # To'lqinli harakat
            dist = p["distance"] + math.sin(phase + p["angle"]) * 5
            x = self.center + math.cos(p["angle"]) * dist
            y = self.center + math.sin(p["angle"]) * dist
            
            p_size = p["size"] + math.sin(phase * 4) * 0.5
            self.create_oval(
                x - p_size, y - p_size, x + p_size, y + p_size,
                fill=main_color, outline=""
            )
            
        # 4. Markaziy Core Orb (Solid with pulse)
        core_pulse = math.sin(phase * 3) * 5
        core_r = 45 + core_pulse
        
        # Core Glow (gradient simulation with rings)
        for i in range(3):
            gr = core_r - i * 4
            self.create_oval(
                self.center - gr, self.center - gr,
                self.center + gr, self.center + gr,
                fill="", outline=glow_color, width=2
            )
            
        # Final Solid Core
        self.create_oval(
            self.center - (core_r-5), self.center - (core_r-5),
            self.center + (core_r-5), self.center + (core_r-5),
            fill=main_color, outline="#FFFFFF", width=1
        )
        
        # Inner Neon Ring (Rotating crosshair style)
        cross_r = core_r + 10
        angle_off = phase * 2
        for i in range(4):
            a = angle_off + i * (math.pi / 2)
            x1 = self.center + math.cos(a) * (cross_r - 5)
            y1 = self.center + math.sin(a) * (cross_r - 5)
            x2 = self.center + math.cos(a) * (cross_r + 5)
            y2 = self.center + math.sin(a) * (cross_r + 5)
            self.create_line(x1, y1, x2, y2, fill=NEON_CYAN, width=2)

    def start_animation(self, mode="listening"):
        self.mode = mode
        self.is_animating = True

    def stop_animation(self):
        self.mode = "idle"

    def _animate(self):
        if self.is_animating:
            self.animation_phase += 0.05
            self.draw_active(self.animation_phase, self.mode)
            self.after(30, self._animate)


class ChatMessage(ctk.CTkFrame):
    """Premium modern chat bubble - Glassmorphism style"""
    def __init__(self, parent, text: str, is_user: bool = True, **kwargs):
        # Bubble ranglari
        bg = "#1a2a3a" if is_user else "#1a1a2e"
        border = NEON_CYAN if is_user else NEON_MAGENTA
        
        super().__init__(parent, fg_color=bg, corner_radius=18, 
                         border_width=1, border_color=border, **kwargs)
        
        # Foydalanuvchi nomi/ikona
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(8, 2))
        
        icon = "👤 Siz" if is_user else f"🤖 {config.JARVIS_NAME}"
        header = ctk.CTkLabel(header_frame, text=icon, 
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=border)
        header.pack(side="left" if is_user else "right")
        
        # Xabar matni
        self.message = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=14),
            text_color="#FFFFFF",
            wraplength=380,
            justify="left"
        )
        self.message.pack(anchor="w", padx=15, pady=(2, 12))
        
        # Vaqt
        time_str = datetime.now().strftime("%H:%M")
        self.time_lbl = ctk.CTkLabel(self, text=time_str, font=ctk.CTkFont(size=9), text_color="#555577")
        self.time_lbl.pack(side="bottom", anchor="e", padx=10, pady=(0, 5))
        
        # Animation state
        self.is_user = is_user
        self.v_offset = 20
        self.opacity = 0.0

    def animate_entry(self):
        """Silliq paydo bo'lish animatsiyasi"""
        if self.v_offset > 0:
            self.v_offset -= 4
            # CTK da haqiqiy opacity yo'q, lekin biz padding orqali slide-up simulatsiya qilamiz
            self.pack_configure(pady=(5 + self.v_offset, 5))
            self.after(20, self.animate_entry)


class JarvisApp(ctk.CTk):
    """Premium Jarvis dastur oynasi"""
    
    def __init__(self):
        super().__init__()
        
        # Oyna sozlamalari
        self.title(f"✨ {config.JARVIS_NAME} - Premium Voice Assistant")
        self.geometry("900x700")
        self.minsize(800, 600)
        self.configure(fg_color=config.BG_COLOR)
        
        # Tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Holat
        self.is_recording = False
        self.chat_history = []
        self.settings_window = None
        self.typing_msg = None
        
        # UI
        self._create_ui()
        self._setup_callbacks()
        self._setup_hotkeys()
        
        # Wake word boshlash
        self.after(500, self._start_wake_word)
        
        # Animatsiyani boshlash
        self.after(100, self._start_breathing)
        
        # App scan ruxsatini tekshirish
        self.after(2000, self._check_app_scan)
        
        # Yangilanishni tekshirish
        self.after(3000, self._check_updates)
    
    def _check_app_scan(self):
        """Dasturlarni skanerlash ruxsatini tekshirish"""
        if not config.SCAN_APPS_ENABLED:
            # Ruxsat so'rash dialogi
            self._ask_scan_permission()
        else:
            # Orqa fonda skanerlash
            threading.Thread(target=jarvis.update_app_list, daemon=True).start()
    
    def _ask_scan_permission(self):
        """Skanerlash uchun ruxsat so'rash (Modern Dialog)"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Ruxsat so'rash")
        dialog.geometry("450x250")
        dialog.resizable(False, False)
        dialog.configure(fg_color="#0a0a14")
        dialog.attributes("-topmost", True)
        
        # Dialogni markazga qo'yish
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 225
        y = self.winfo_y() + (self.winfo_height() // 2) - 125
        dialog.geometry(f"+{x}+{y}")
        
        # UI elementlari
        ctk.CTkLabel(
            dialog,
            text="🚀 Dasturlarni avtomatik aniqlash",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=config.PRIMARY_COLOR
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text="Jarvis tizimingizdagi o'rnatilgan dasturlarni\navtomatik aniqlashi uchun ruxsat berasizmi?\nBu buyruqlarni aniqroq bajarishga yordam beradi.",
            font=ctk.CTkFont(size=13),
            text_color="#AAAAAA",
            justify="center"
        ).pack(pady=10)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def on_allow():
            # Config faylni yangilash (memoryda)
            config.SCAN_APPS_ENABLED = True
            dialog.destroy()
            self._update_status("Skanerlanmoqda...", config.PRIMARY_COLOR)
            
            def do_scan():
                count = jarvis.update_app_list()
                self.after(0, lambda: self._add_chat_message(
                    f"Tizim skanerlandi. {count} ta yangi dastur topildi va ro'yxatga qo'shildi.", 
                    is_user=False
                ))
                self.after(0, lambda: self._update_status("'Jarvis' deng...", "#666666"))
            
            threading.Thread(target=do_scan, daemon=True).start()
            
        def on_deny():
            dialog.destroy()
            self._add_chat_message("Dasturlarni avtomatik aniqlash bekor qilindi. Manual sozlamalar ishlatiladi.", is_user=False)
        
        ctk.CTkButton(
            btn_frame,
            text="Ruxsat berish",
            fg_color=config.PRIMARY_COLOR,
            hover_color=config.SECONDARY_COLOR,
            command=on_allow,
            width=150
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Keyinroq",
            fg_color="#333333",
            hover_color="#444444",
            command=on_deny,
            width=100
        ).pack(side="left", padx=10)

    def _create_ui(self):
        """Ultra-premium V3 UI yaratish"""
        self.current_layout = None 
        
        # ========== ANIMATED BACKGROUND (V3) ==========
        self.bg_anim = AnimatedBackground(self)
        self.bg_anim.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bg_anim.start()
        
        # ========== TOP BAR (Neon Crystal) ==========
        self.top_bar = ctk.CTkFrame(self, fg_color=GLASS_BG, height=65, corner_radius=0)
        self.top_bar.pack(fill="x")
        self.top_bar.pack_propagate(False)
        
        # Neon header accent with gradient effect simulation
        accent_line = ctk.CTkFrame(self, fg_color=NEON_CYAN, height=3, corner_radius=0)
        accent_line.pack(fill="x")
        
        # Logo frame
        logo_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        logo_frame.pack(side="left", padx=25)
        
        logo_icon = ctk.CTkLabel(logo_frame, text="⚡", font=ctk.CTkFont(size=32), text_color=NEON_GOLD)
        logo_icon.pack(side="left")
        
        title_lbl = ctk.CTkLabel(logo_frame, text=config.JARVIS_NAME.upper(), 
                                font=ctk.CTkFont(size=24, weight="bold", family="Orbitron" if os.name == "nt" else "Arial"), 
                                text_color=NEON_CYAN)
        title_lbl.pack(side="left", padx=12)
        
        pro_badge = ctk.CTkLabel(logo_frame, text=" SERIES 7 ", font=ctk.CTkFont(size=10, weight="bold"), 
                                text_color="#000000", fg_color=NEON_GOLD, corner_radius=6)
        pro_badge.pack(side="left", padx=5)
        
        # Info indicators
        self.time_label = ctk.CTkLabel(self.top_bar, text="", font=ctk.CTkFont(size=14, family="Consolas"), text_color=NEON_CYAN)
        self.time_label.pack(side="right", padx=30)
        self._update_time()
        
        # Settings button with hover effect
        self.settings_btn = ctk.CTkButton(self.top_bar, text="⚙", width=50, height=50, corner_radius=12, 
                                        fg_color=GLASS_CARD, hover_color="#223355", border_width=1, 
                                        border_color="#334466", command=self._open_settings)
        self.settings_btn.pack(side="right", padx=10)
        
        # ========== MAIN VIEWPORT ==========
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        # LEFT PANEL (Control Center)
        self.left_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        # Orb section with glowing border
        orb_container = ctk.CTkFrame(self.left_panel, fg_color=GLASS_PANEL, corner_radius=25, 
                                    border_width=2, border_color="#1a1a2e")
        orb_container.pack(fill="x", pady=(0, 20))
        
        self.orb = PulsingOrb(orb_container, size=240)
        self.orb.pack(pady=30, padx=30)
        
        # Status Card (Ultra Premium)
        self.status_frame = ctk.CTkFrame(self.left_panel, fg_color=GLASS_CARD, corner_radius=20, 
                                        border_width=2, border_color="#223355")
        self.status_frame.pack(fill="x", pady=10)
        
        self.status_glow = ctk.CTkFrame(self.status_frame, fg_color=NEON_CYAN, width=4, corner_radius=2)
        self.status_glow.pack(side="left", fill="y", padx=(10, 0), pady=12)
        
        st_container = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        st_container.pack(side="left", fill="both", expand=True, padx=15, pady=12)
        
        ctk.CTkLabel(st_container, text="SYSTEM STATUS", font=ctk.CTkFont(size=9, weight="bold"), 
                    text_color="#556677").pack(anchor="w")
        self.status_text = ctk.CTkLabel(st_container, text="ACTIVE", font=ctk.CTkFont(size=16, weight="bold"), 
                                      text_color=NEON_CYAN)
        self.status_text.pack(anchor="w")
        
        # Buttons (Redesigned with Magnetic effect)
        self.mic_btn = MagneticButton(self.left_panel, text="⬛ PRIMARY MIC", 
                                    font=ctk.CTkFont(size=16, weight="bold"),
                                    width=220, height=60, corner_radius=15, 
                                    fg_color=config.PRIMARY_COLOR, text_color="#000000",
                                    hover_color="#FFFFFF", command=self._toggle_recording)
        self.mic_btn.pack(pady=20)
        
        # Quick Actions with neon borders
        quick_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        quick_frame.pack(fill="x")
        
        def create_quick_row(parent, btns):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(pady=5)
            for icon, cmd in btns:
                btn = ctk.CTkButton(row, text=icon, width=50, height=50, corner_radius=10, 
                                   fg_color=GLASS_CARD, hover_color="#2a2a4e", 
                                   border_width=1, border_color="#223344",
                                   command=cmd)
                btn.pack(side="left", padx=5)
                # Hover bind simulation
                btn.bind("<Enter>", lambda e, b=btn: b.configure(border_color=NEON_CYAN))
                btn.bind("<Leave>", lambda e, b=btn: b.configure(border_color="#223344"))

        create_quick_row(quick_frame, [
            ("🕐", lambda: self._quick_command("Soat necha?")),
            ("🌤️", lambda: self._quick_command("Ob-havo qanday?")),
            ("📸", lambda: self._quick_command("Skrinshot ol")),
            ("🔋", lambda: self._quick_command("Batareya holati"))
        ])
        
        create_quick_row(quick_frame, [
            ("🎬", lambda: self._quick_command("YouTube-ni och")),
            ("💬", lambda: self._quick_command("Telegramni och")),
            ("🎨", lambda: self._quick_command("Yorqinlikni oshir")),
            ("🛠️", lambda: self._quick_command("Dasturlar ro'yxati"))
        ])
        
        # Shortcut Hint
        ctk.CTkLabel(self.left_panel, text="PRESS [SPACE] TO OVERRIDE", 
                    font=ctk.CTkFont(size=10, slant="italic"), text_color="#445566").pack(pady=10)
        
        # RIGHT PANEL (Comms Matrix)
        self.right_panel = ctk.CTkFrame(self.main_container, fg_color="#080812", 
                                       corner_radius=25, border_width=2, border_color="#12121f")
        
        # Chat Header with scanline effect (simulated)
        chat_header = ctk.CTkFrame(self.right_panel, fg_color="#12121f", height=50, corner_radius=0)
        chat_header.pack(fill="x")
        chat_header.pack_propagate(False)
        
        ctk.CTkLabel(chat_header, text="📡 NEURAL FEED: ACTIVE", 
                    font=ctk.CTkFont(size=12, weight="bold"), text_color=NEON_GOLD).pack(side="left", padx=20)
        
        ctk.CTkButton(chat_header, text="× CLEAR", width=70, height=28, corner_radius=6, 
                     fg_color="#332211", hover_color="#550000", font=ctk.CTkFont(size=10),
                     command=self._clear_chat).pack(side="right", padx=10)
        
        # Chat area
        self.chat_scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent", 
                                                scrollbar_button_color="#223344")
        self.chat_scroll.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Initial Feed
        self._add_chat_message(
            f"JARVIS ONLINE. Encryption active. Welcome, User. How shall we proceed?",
            is_user=False
        )

        self.after(100, self._check_layout)
        self.bind("<Configure>", self._on_resize)
        
        # ========== FOOTER HINTS ==========
        self.bottom_bar = ctk.CTkFrame(self, fg_color=GLASS_BG, height=40, corner_radius=0)
        self.bottom_bar.pack(fill="x", side="bottom")
        
        hints = "CMD: 'Ovozni 50% qil' • 'Google-da Python-ni qidir' • 'Eslatma yoz: Soat 5-da uchrashuv'"
        self.hint_label = ctk.CTkLabel(self.bottom_bar, text=hints.upper(), 
                                     font=ctk.CTkFont(size=10, family="Consolas"), text_color="#334455")
        self.hint_label.pack(pady=10)
    
    def _on_resize(self, event):
        """Oyna o'zgarishini kuzatish"""
        if event.widget == self:
            self._check_layout()

    def _check_layout(self):
        """ Layoutni tekshirish va yangilash """
        width = self.winfo_width()
        new_layout = "mobile" if width < config.MOBILE_BREAKPOINT else "desktop"
        
        if new_layout != self.current_layout:
            self.current_layout = new_layout
            self._apply_layout()

    def _apply_layout(self):
        """Layoutni qo'llash"""
        # Pack tozalash
        self.left_panel.pack_forget()
        self.right_panel.pack_forget()
        
        if self.current_layout == "desktop":
            self.left_panel.pack(side="left", fill="y", padx=(0, 20))
            self.left_panel.configure(width=280)
            self.right_panel.pack(side="right", fill="both", expand=True)
            self.orb.configure(width=220, height=220)
        else:
            self.left_panel.pack(side="top", fill="x", pady=(0, 10))
            self.left_panel.configure(width=0) # Auto width
            self.right_panel.pack(side="bottom", fill="both", expand=True)
            self.orb.configure(width=180, height=180)
    
    def _setup_callbacks(self):
        """Callbacks"""
        jarvis.on_listening_start = self._on_listening_start
        jarvis.on_listening_stop = self._on_listening_stop
        jarvis.on_speaking_start = self._on_speaking_start
        jarvis.on_speaking_stop = self._on_speaking_stop
        jarvis.on_text_received = self._on_text_received
        jarvis.on_response = self._on_response
    
    def _setup_hotkeys(self):
        """Hotkeys"""
        self.bind("<space>", lambda e: self._toggle_recording())
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Control-q>", lambda e: self.destroy())
    
    def _start_wake_word(self):
        """Wake word tinglashni boshlash"""
        wake_detector.start(self._on_wake_word)
        self._update_status("'Jarvis' deng...", "#666666")
    
    def _on_wake_word(self):
        """Wake word aniqlanganda"""
        # UI thread'da bajarish
        self.after(0, self._start_recording_from_wake)
    
    def _start_recording_from_wake(self):
        """Wake word'dan keyin yozish (Hands-free)"""
        if not self.is_recording:
            # Wake word'ni to'xtatish
            wake_detector.pause()
            
            # Eshitish boshlandi ovozi
            _play_sound(_LISTEN_START_SOUND)
            
            self._update_status("Tinglayapman...", "#FF6B35")
            self.orb.start_animation("listening")
            
            # Auto-listen va bajarish sikli
            def on_done():
                _play_sound(_LISTEN_STOP_SOUND)
                self.after(0, self._resume_wake_word)
                
            jarvis.listen_and_execute(on_done_callback=on_done)
    
    def _start_breathing(self):
        """Breathing animatsiyasini boshlash"""
        # Idle rejimda ham yengil animatsiya
        pass
    
    def _update_time(self):
        """Vaqtni yangilash"""
        now = datetime.now()
        self.time_label.configure(text=now.strftime("%H:%M:%S  •  %d.%m.%Y"))
        self.after(1000, self._update_time)
    
    def _toggle_recording(self):
        """Yozishni toggle"""
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()
    
    def _start_recording(self):
        """Yozish boshlash"""
        self.is_recording = True
        self.mic_btn.configure(
            text="⏹ To'xtatish",
            fg_color="#FF4444",
            hover_color="#CC3333"
        )
        # Eshitish boshlandi ovozi
        _play_sound(_LISTEN_START_SOUND)
        
        self._update_status("Tinglayapman...", "#FF6B35")
        self.orb.start_animation("listening")
        jarvis.listen()
    
    def _stop_recording(self):
        """Yozish to'xtatish"""
        self.is_recording = False
        self.mic_btn.configure(
            text="🎤 Gapirish",
            fg_color=config.PRIMARY_COLOR,
            hover_color=config.SECONDARY_COLOR
        )
        self._update_status("Qayta ishlanmoqda...", "#00FF88")
        self.orb.start_animation("thinking")
        
        def process():
            text = jarvis.stop_listening()
            if text:
                self.after(0, lambda: self._add_chat_message(text, is_user=True))
                # Typing indicator ko'rsatish
                self.after(0, self._show_typing)
                
                response = jarvis.process_command(text)
                
                # Typing indicatorni o'chirish va javobni qo'shish
                self.after(0, self._hide_typing)
                self.after(0, lambda: self._add_chat_message(response, is_user=False))
                self.after(0, lambda: jarvis.speak(response, self._on_speak_done))
            else:
                self.after(0, lambda: self._update_status("Eshitmadim", "#FF4444"))
                self.after(0, self.orb.stop_animation)
                self.after(0, self._resume_wake_word)
        
        threading.Thread(target=process, daemon=True).start()

    def _show_typing(self):
        """Jarvis o'ylayotganini ko'rsatish"""
        self._hide_typing()
        self.typing_msg = ChatMessage(self.chat_scroll, "...", is_user=False)
        self.typing_msg.pack(fill="x", pady=5, padx=5, anchor="w")
        self.typing_msg.animate_entry()
        
    def _hide_typing(self):
        """Typing indicatorni yashirish"""
        if self.typing_msg:
            self.typing_msg.destroy()
            self.typing_msg = None
    
    def _on_speak_done(self):
        """Gapirish tugaganda"""
        self._resume_wake_word()
    
    def _resume_wake_word(self):
        """Wake word tinglashni davom ettirish"""
        wake_detector.resume()
        self._update_status("'Jarvis' deng...", "#556677")
    
    def _quick_command(self, cmd: str):
        """Tezkor buyruq"""
        self._add_chat_message(cmd, is_user=True)
        self._show_typing()
        
        def process():
            response = jarvis.process_command(cmd)
            self.after(0, self._hide_typing)
            self.after(0, lambda: self._add_chat_message(response, is_user=False))
            jarvis.speak(response)
            
        threading.Thread(target=process, daemon=True).start()
    
    def _on_listening_start(self):
        self.after(0, lambda: self.orb.start_animation("listening"))
    
    def _on_listening_stop(self):
        pass
    
    def _on_speaking_start(self):
        self.after(0, lambda: self.orb.start_animation("speaking"))
        self.after(0, lambda: self._update_status("Javob bermoqda...", NEON_MAGENTA))
    
    def _on_speaking_stop(self):
        self.after(0, self.orb.stop_animation)
        self.after(0, lambda: self._update_status("TAYYOR", NEON_CYAN))
    
    def _on_text_received(self, text: str):
        self.after(0, lambda: self._add_chat_message(text, is_user=True))
    
    def _on_response(self, text: str):
        self.after(0, lambda: self._add_chat_message(text, is_user=False))
    
    def _update_status(self, text: str, color: str = NEON_CYAN):
        """Status yangilash - Neon glow bilan"""
        self.status_text.configure(text=text.upper(), text_color=color)
        self.status_glow.configure(fg_color=color)
    
    def _add_chat_message(self, text: str, is_user: bool):
        """Chat xabar qo'shish - Animatsiya bilan"""
        msg = ChatMessage(self.chat_scroll, text, is_user)
        msg.pack(fill="x", pady=5, padx=5, anchor="e" if is_user else "w")
        msg.animate_entry() # V3 Animatsiyasi
        
        self.chat_history.append({"role": "user" if is_user else "assistant", "text": text})
        
        # Scroll pastga
        self.after(100, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))
    
    def _clear_chat(self):
        """Chatni tozalash"""
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()
        self.chat_history = []
        self._add_chat_message(f"JARVIS ONLINE. Chat cleared. How shall we proceed?", is_user=False)
    
    def _check_updates(self):
        """Yangilanishni orqa fonda tekshirish"""
        def thread_func():
            data = updater.check_for_updates()
            if data.get("update_available"):
                self.after(0, lambda: self._show_update_dialog(data))
        
        threading.Thread(target=thread_func, daemon=True).start()

    def _show_update_dialog(self, data):
        """Yangilanish dialogini ko'rsatish"""
        new_ver = data["version"]
        changelog = data["changelog"]
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Yangi versiya!")
        dialog.geometry("500x350")
        dialog.attributes("-topmost", True)
        dialog.configure(fg_color=config.BG_COLOR)
        
        # UI elementlar
        ctk.CTkLabel(dialog, text="🚀 YANGILANISH MAVJUD", font=ctk.CTkFont(size=18, weight="bold"), 
                    text_color=NEON_GOLD).pack(pady=(20, 10))
        
        ctk.CTkLabel(dialog, text=f"Versiya: {config.APP_VERSION} → {new_ver}", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Changelog
        cf = ctk.CTkFrame(dialog, fg_color=GLASS_CARD, corner_radius=10, border_width=1, border_color="#334466")
        cf.pack(fill="both", expand=True, padx=20, pady=10)
        
        cl_text = ctk.CTkTextbox(cf, fg_color="transparent", font=ctk.CTkFont(size=12))
        cl_text.pack(fill="both", expand=True, padx=10, pady=10)
        cl_text.insert("1.0", f"O'zgarishlar:\n\n{changelog}")
        cl_text.configure(state="disabled")
        
        # Progress bar (yashirin)
        pb = ctk.CTkProgressBar(dialog, width=400, fg_color="#1a1a1a", progress_color=NEON_CYAN)
        pb.set(0)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        def start_update():
            btn_frame.pack_forget()
            pb.pack(pady=10)
            
            def download_thread():
                def progress(p):
                    self.after(0, lambda: pb.set(p))
                
                new_exe = updater.download_update(data["download_url"], progress_callback=progress)
                if new_exe:
                    self.after(0, lambda: self._update_status("O'rnatilmoqda...", NEON_GOLD))
                    time.sleep(1)
                    updater.apply_update(new_exe)
                else:
                    self.after(0, lambda: self._update_status("Xato: Yuklab bo'lmadi", "#FF4444"))
                    self.after(0, dialog.destroy)

            threading.Thread(target=download_thread, daemon=True).start()

        ctk.CTkButton(btn_frame, text="Yopish", width=120, fg_color="#333333", 
                     command=dialog.destroy).pack(side="right", padx=20)
        
        ctk.CTkButton(btn_frame, text="Hozir yangilash", width=200, fg_color=NEON_CYAN, 
                     text_color="#000000", font=ctk.CTkFont(weight="bold"),
                     command=start_update).pack(side="right")

    def _open_settings(self):
        """Sozlamalar"""
        if self.settings_window is None or not self.settings_window.winfo_exists():
            from ui.settings import SettingsWindow
            self.settings_window = SettingsWindow(self)


def main():
    """Main"""
    app = JarvisApp()
    app.mainloop()


if __name__ == "__main__":
    main()
