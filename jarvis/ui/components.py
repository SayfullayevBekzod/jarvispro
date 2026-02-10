"""
Jarvis UI Components
Qo'shimcha UI komponentlari
"""

import customtkinter as ctk
import config


class StatusIndicator(ctk.CTkFrame):
    """Status ko'rsatkichi"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.indicator = ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color="#00FF00"
        )
        self.indicator.pack(side="left", padx=5)
        
        self.status_text = ctk.CTkLabel(
            self,
            text="Tayyor",
            font=ctk.CTkFont(size=12),
            text_color="#AAAAAA"
        )
        self.status_text.pack(side="left")
    
    def set_status(self, status: str, color: str = "#00FF00"):
        """Statusni o'zgartirish"""
        self.indicator.configure(text_color=color)
        self.status_text.configure(text=status)
    
    def set_listening(self):
        self.set_status("Tinglayapman...", "#FF6600")
    
    def set_speaking(self):
        self.set_status("Gapirmoqda...", "#00D4FF")
    
    def set_ready(self):
        self.set_status("Tayyor", "#00FF00")
    
    def set_error(self):
        self.set_status("Xatolik", "#FF0000")


class MessageBubble(ctk.CTkFrame):
    """Xabar bubblelari"""
    
    def __init__(self, parent, text: str, is_user: bool = True, **kwargs):
        bg_color = "#1E3A5F" if is_user else "#2D1B4E"
        super().__init__(parent, fg_color=bg_color, corner_radius=15, **kwargs)
        
        icon = "👤" if is_user else "🤖"
        
        self.label = ctk.CTkLabel(
            self,
            text=f"{icon} {text}",
            font=ctk.CTkFont(size=14),
            text_color="#FFFFFF",
            wraplength=350,
            justify="left"
        )
        self.label.pack(padx=15, pady=10)


class CommandHint(ctk.CTkFrame):
    """Buyruq ko'rsatmalari"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#1a1a2e", corner_radius=10, **kwargs)
        
        self.hints = [
            "💬 \"Salom Jarvis\"",
            "🕐 \"Soat necha?\"",
            "🌐 \"Chrome ochib ber\"",
            "🔢 \"5 plyus 5 necha?\"",
            "🔍 \"Google'da ... qidir\"",
            "📸 \"Skrinshot ol\"",
        ]
        
        title = ctk.CTkLabel(
            self,
            text="Buyruq namunalari:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#888888"
        )
        title.pack(pady=(10, 5))
        
        hints_text = " • ".join(self.hints)
        label = ctk.CTkLabel(
            self,
            text=hints_text,
            font=ctk.CTkFont(size=11),
            text_color="#666666",
            wraplength=500
        )
        label.pack(padx=10, pady=(0, 10))


class VolumeSlider(ctk.CTkFrame):
    """Ovoz balandligi slayderi"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        label = ctk.CTkLabel(
            self,
            text="🔊",
            font=ctk.CTkFont(size=16)
        )
        label.pack(side="left", padx=5)
        
        self.slider = ctk.CTkSlider(
            self,
            from_=0,
            to=100,
            width=100,
            height=16,
            fg_color="#333333",
            progress_color=config.PRIMARY_COLOR
        )
        self.slider.set(80)
        self.slider.pack(side="left", padx=5)


class SettingsButton(ctk.CTkButton):
    """Sozlamalar tugmasi"""
    
    def __init__(self, parent, command=None, **kwargs):
        super().__init__(
            parent,
            text="⚙️",
            width=40,
            height=40,
            corner_radius=20,
            fg_color="#333333",
            hover_color="#555555",
            command=command,
            **kwargs
        )
