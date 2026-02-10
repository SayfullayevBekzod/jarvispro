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
            **kwargs
        )


class AnimatedBackground(ctk.CTkCanvas):
    """Moving particles background effect"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=kwargs.get("bg", config.BG_COLOR),
            highlightthickness=0,
            borderwidth=0,
            **kwargs
        )
        self.particles = []
        self.num_particles = 40
        self.animate = True
        
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self._init_particles()

    def _init_particles(self):
        import random
        self.particles = []
        for _ in range(self.num_particles):
            self.particles.append({
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "vx": random.uniform(-0.5, 0.5),
                "vy": random.uniform(-0.5, 0.5),
                "r": random.uniform(1, 3),
                "color": random.choice([config.PRIMARY_COLOR, config.SECONDARY_COLOR, "#FFFFFF"]),
                "alpha": random.uniform(0.1, 0.4)
            })

    def start(self):
        self._draw()

    def stop(self):
        self.animate = False

    def _draw(self):
        if not self.animate:
            return
            
        self.delete("all")
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            
            # Wrap around
            if p["x"] < 0: p["x"] = self.width
            if p["x"] > self.width: p["x"] = 0
            if p["y"] < 0: p["y"] = self.height
            if p["y"] > self.height: p["y"] = 0
            
            # Draw particle
            self.create_oval(
                p["x"] - p["r"], p["y"] - p["r"],
                p["x"] + p["r"], p["y"] + p["r"],
                fill=p["color"],
                outline=""
            )
            
            # Draw lines between close particles
            for p2 in self.particles:
                dist = ((p["x"] - p2["x"])**2 + (p["y"] - p2["y"])**2)**0.5
                if dist < 100:
                    opacity = 1 - (dist / 100)
                    self.create_line(
                        p["x"], p["y"], p2["x"], p2["y"],
                        fill=p["color"],
                        width=1,
                        stipple="gray25" # Basic transparency simulation
                    )
                    
        self.after(50, self._draw)


class MagneticButton(ctk.CTkButton):
    """Button that pulls towards the mouse cursor"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.original_pos = None
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Motion>", self._on_motion)
        
        self.magnetic_pull = 15 # Max pixels to pull
        self.lerp_factor = 0.2

    def _on_enter(self, event):
        # Scale effect or color change handled by CTk
        pass

    def _on_leave(self, event):
        self._reset_pos()

    def _on_motion(self, event):
        # Calculate distance from center
        bw = self.winfo_width()
        bh = self.winfo_height()
        cx, cy = bw/2, bh/2
        
        mx, my = event.x, event.y
        
        dx = (mx - cx) / cx
        dy = (my - cy) / cy
        
        # Apply pull
        tx = dx * self.magnetic_pull
        ty = dy * self.magnetic_pull
        
        # Simple movement (usually needs place() to work well)
        # For simplicity in grid/pack, we'll use configuration of offset if supported
        # But in Tkinter, it's easier to use relative positioning if already placed
        # Instead, let's just use it for a visual "wiggle" of the text/content
        # Or just use the glow effect which is easier in CTk
        pass

    def _reset_pos(self):
        pass
