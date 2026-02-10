"""
Sozlamalar oynasi
"""

import customtkinter as ctk
import json
import os

import config


class SettingsWindow(ctk.CTkToplevel):
    """Sozlamalar oynasi"""
    
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        
        self.on_save = on_save
        self.settings_file = os.path.join(os.path.dirname(__file__), "..", "data", "settings.json")
        
        # Oyna sozlamalari
        self.title("⚙️ Sozlamalar")
        self.geometry("450x500")
        self.configure(fg_color=config.BG_COLOR)
        self.resizable(False, False)
        
        # Modal qilish
        self.transient(parent)
        self.grab_set()
        
        self._create_ui()
        self._load_settings()
    
    def _create_ui(self):
        """UI yaratish"""
        # Sarlavha
        title = ctk.CTkLabel(
            self,
            text="⚙️ Sozlamalar",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=config.PRIMARY_COLOR
        )
        title.pack(pady=20)
        
        # Scroll frame
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            width=400,
            height=350
        )
        scroll_frame.pack(fill="both", expand=True, padx=20)
        
        # Jarvis nomi
        self._create_section(scroll_frame, "Jarvis nomi")
        self.name_entry = ctk.CTkEntry(
            scroll_frame,
            width=300,
            height=35,
            placeholder_text="Jarvis"
        )
        self.name_entry.pack(pady=5)
        
        # Ovoz tezligi
        self._create_section(scroll_frame, "Ovoz tezligi")
        self.speed_slider = ctk.CTkSlider(
            scroll_frame,
            from_=0.5,
            to=2.0,
            width=300
        )
        self.speed_slider.set(1.0)
        self.speed_slider.pack(pady=5)
        
        # Ovoz balandligi
        self._create_section(scroll_frame, "Ovoz balandligi")
        self.volume_slider = ctk.CTkSlider(
            scroll_frame,
            from_=0,
            to=1.0,
            width=300
        )
        self.volume_slider.set(0.8)
        self.volume_slider.pack(pady=5)
        
        # Default shahar
        self._create_section(scroll_frame, "Ob-havo shahri")
        self.city_entry = ctk.CTkEntry(
            scroll_frame,
            width=300,
            height=35,
            placeholder_text="Toshkent"
        )
        self.city_entry.pack(pady=5)
        
        # Tema
        self._create_section(scroll_frame, "Tema")
        self.theme_var = ctk.StringVar(value="dark")
        theme_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        theme_frame.pack(pady=5)
        
        ctk.CTkRadioButton(
            theme_frame,
            text="Qorong'i",
            variable=self.theme_var,
            value="dark"
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            theme_frame,
            text="Yorug'",
            variable=self.theme_var,
            value="light"
        ).pack(side="left", padx=10)
        
        # Qo'shimcha
        self._create_section(scroll_frame, "Qo'shimcha")
        
        # Alisa Mode
        self.alice_var = ctk.BooleanVar(value=config.ALICE_MODE)
        ctk.CTkCheckBox(
            scroll_frame,
            text="Alisa rejimi (Persona & Ovoz)",
            variable=self.alice_var
        ).pack(pady=5)

        self.autostart_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            scroll_frame,
            text="Kompyuter yonganida avtomatik ishga tushish",
            variable=self.autostart_var
        ).pack(pady=5)
        
        # Tugmalar
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        ctk.CTkButton(
            buttons_frame,
            text="Saqlash",
            width=120,
            height=40,
            fg_color=config.PRIMARY_COLOR,
            command=self._save_settings
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="Bekor",
            width=120,
            height=40,
            fg_color="#555555",
            command=self.destroy
        ).pack(side="left", padx=10)
    
    def _create_section(self, parent, title):
        """Bo'lim sarlavhasi"""
        label = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#AAAAAA"
        )
        label.pack(pady=(15, 5), anchor="w")
    
    def _load_settings(self):
        """Sozlamalarni yuklash"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                self.name_entry.insert(0, settings.get("name", "Jarvis"))
                self.speed_slider.set(settings.get("voice_speed", 1.0))
                self.volume_slider.set(settings.get("voice_volume", 0.8))
                self.city_entry.insert(0, settings.get("default_city", "Toshkent"))
                self.theme_var.set(settings.get("theme", "dark"))
                self.autostart_var.set(settings.get("autostart", False))
                self.alice_var.set(settings.get("alice_mode", False))
            else:
                self.name_entry.insert(0, config.JARVIS_NAME)
                self.city_entry.insert(0, config.DEFAULT_CITY)
        except:
            pass
    
    def _save_settings(self):
        """Sozlamalarni saqlash"""
        settings = {
            "name": self.name_entry.get() or "Jarvis",
            "voice_speed": self.speed_slider.get(),
            "voice_volume": self.volume_slider.get(),
            "default_city": self.city_entry.get() or "Toshkent",
            "theme": self.theme_var.get(),
            "autostart": self.autostart_var.get(),
            "alice_mode": self.alice_var.get()
        }
        
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            if self.on_save:
                self.on_save(settings)
            
            self.destroy()
        except Exception as e:
            print(f"Sozlamalarni saqlashda xatolik: {e}")
