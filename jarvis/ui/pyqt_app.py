import sys
import os
import math
import random
import threading
import time
from datetime import datetime

# Loyiha yo'lini qo'shish (Imports uchun)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, 
                             QGraphicsDropShadowEffect, QScrollArea)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QRect, QRectF, QEasingCurve, 
                          QTimer, QPoint, QPointF, pyqtSignal, QSize, QObject)
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, 
                         QPainterPath, QRadialGradient)

import config
from core.jarvis import jarvis
from core.wake_word import wake_detector

# --- Constants & Stylings ---
NEON_CYAN = config.PRIMARY_COLOR
NEON_MAGENTA = config.SECONDARY_COLOR
DARK_BG = "rgba(5, 5, 10, 245)"
GLASS_PANEL = "rgba(255, 255, 255, 10)"
BORDER_COLOR = "rgba(0, 245, 255, 50)"

QSS_STYLE = f"""
QMainWindow {{
    background: transparent;
}}

#MainFrame {{
    background-color: {DARK_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 20px;
}}

#TitleLabel {{
    color: {NEON_CYAN};
    font-family: 'Orbitron', 'Segoe UI', sans-serif;
    font-size: 20px;
    font-weight: bold;
    letter-spacing: 2px;
}}

#StatusLabel {{
    color: #666;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}}

#ChatArea {{
    background: transparent;
    border: none;
}}

.MessageBubble {{
    background-color: {GLASS_PANEL};
    border-radius: 12px;
    padding: 12px;
    margin: 6px;
    border: 1px solid rgba(0, 245, 255, 25);
}}

#UserMessage {{
    color: #FFFFFF;
    border-left: 3px solid {NEON_CYAN};
}}

#BotMessage {{
    color: #E0E0E0;
    border-right: 3px solid {NEON_MAGENTA};
}}

#ControlPanel {{
    background: rgba(0, 0, 0, 60);
    border-top: 1px solid {BORDER_COLOR};
    border-bottom-left-radius: 20px;
    border-bottom-right-radius: 20px;
}}

QPushButton#IconButton {{
    background: transparent;
    color: #777;
    font-size: 16px;
    border-radius: 8px;
}}

QPushButton#IconButton:hover {{
    color: white;
    background: rgba(255, 255, 255, 15);
}}

QPushButton#CloseButton:hover {{
    background: #cc3333;
}}
"""

class UIBridge(QObject):
    """Callbacklarni thread-safe qilish uchun signallar"""
    listening_started = pyqtSignal()
    listening_stopped = pyqtSignal()
    speaking_started = pyqtSignal()
    speaking_stopped = pyqtSignal()
    text_received = pyqtSignal(str)
    response_received = pyqtSignal(str)

class WaveformWidget(QWidget):
    """Dinamik futuristik to'lqin animatsiyasi"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.phase = 0
        self.active = False
        self.mode = "idle" # idle, listening, speaking

    def start(self, mode="listening"):
        self.active = True
        self.mode = mode
        self.timer.start(45) # Optimization: Higher interval = lower CPU

    def stop(self):
        self.active = False
        self.timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        mid_y = height / 2

        if not self.active:
            painter.setPen(QPen(QColor(NEON_CYAN if self.mode != "error" else "#ff4444"), 1, Qt.PenStyle.DotLine))
            painter.setOpacity(0.3)
            painter.drawLine(40, int(mid_y), width - 40, int(mid_y))
            return

        self.phase += 0.25
        painter.setPen(Qt.PenStyle.NoPen)

        # To'lqin ranglari (Optimization: Reduced layers)
        if self.mode == "listening":
            wave_colors = [QColor(0, 245, 255, 160), QColor(0, 245, 255, 40)]
            base_amp = 30
        else: # speaking
            wave_colors = [QColor(255, 215, 0, 160), QColor(255, 215, 0, 40)]
            base_amp = 20

        for i, color in enumerate(wave_colors):
            path = QPainterPath()
            path.moveTo(0, mid_y)
            
            for x in range(0, width + 1, 6): # Optimization: Step 6 instead of 3
                rel_x = x / width
                # Fade out corners (sin envelope)
                envelope = math.sin(rel_x * math.pi) 
                # Waviness
                y = mid_y + math.sin(x * 0.04 + self.phase + i*1.2) * (base_amp + i * 8) * envelope
                path.lineTo(float(x), y)
            
            painter.setPen(QPen(color, 2))
            painter.drawPath(path)

class MicButton(QPushButton):
    """Glanetsli va neon nur taratuvchi markaziy tugma"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(90, 90)
        self._is_active = False
        self._thinking = False
        self._pulse = 0
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._animate_pulse)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_thinking(self, state):
        self._thinking = state
        if state: self.pulse_timer.start(50) # Optimization
        elif not self._is_active: self.pulse_timer.stop()
        self.update()

    def set_active(self, state):
        self._is_active = state
        if state: self.pulse_timer.start(50) # Optimization
        elif not self._thinking: self.pulse_timer.stop()
        self.update()

    def _animate_pulse(self):
        self._pulse = (self._pulse + 0.15) % (math.pi * 2)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        center = rect.center()
        cx, cy = float(center.x()), float(center.y())
        
        # 1. Outer Glow (Pulsing)
        if self._is_active or self._thinking:
            glow_col = NEON_CYAN if self._is_active else NEON_MAGENTA
            p_val = math.sin(self._pulse) * 5
            radius = 38.0 + p_val
            grad = QRadialGradient(QPointF(cx, cy), radius)
            grad.setColorAt(0, QColor(glow_col))
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            # Use QRectF for robust float handling
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

        # 2. Main Circle
        main_col = QColor(NEON_CYAN) if self._is_active else QColor(40, 40, 50)
        if self._thinking: main_col = QColor(NEON_MAGENTA)
        
        painter.setBrush(main_col)
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        painter.drawEllipse(QRectF(cx - 32, cy - 32, 64, 64))
        
        # 3. Icon (Mic)
        painter.setPen(QPen(Qt.GlobalColor.black if (self._is_active or self._thinking) else Qt.GlobalColor.white, 2.5))
        # Simple Mic Shape using float coordinates
        painter.drawRoundedRect(QRectF(cx - 6, cy - 11, 12, 18), 6, 6)
        painter.drawArc(QRectF(cx - 10, cy - 3, 20, 13), 0, -180 * 16)
        painter.drawLine(QPointF(cx, cy + 10), QPointF(cx, cy + 15))

class JarvisPyQtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Oyna sozlamalari
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 800)
        
        self.bridge = UIBridge()
        self._is_handling_mic = False
        self._drag_pos = QPoint()
        
        self._init_ui()
        self._setup_logic()
        
        # O'tish animatsiyasi
        self._fade_in()

    def _init_ui(self):
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("MainFrame")
        self.setCentralWidget(self.main_frame)
        self.main_frame.setStyleSheet(QSS_STYLE)
        
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Header (Title bar)
        header = QFrame()
        header.setFixedHeight(70)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(25, 10, 15, 0)

        title = QLabel(config.JARVIS_NAME.upper())
        title.setObjectName("TitleLabel")
        h_layout.addWidget(title)
        
        h_layout.addStretch()

        self.min_btn = QPushButton("-")
        self.min_btn.setObjectName("IconButton")
        self.min_btn.setFixedSize(35, 35)
        self.min_btn.clicked.connect(self.showMinimized)

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("IconButton")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(35, 35)
        self.close_btn.clicked.connect(self.close)

        h_layout.addWidget(self.min_btn)
        h_layout.addWidget(self.close_btn)
        layout.addWidget(header)

        # 2. Status Bar
        status_frame = QFrame()
        st_layout = QHBoxLayout(status_frame)
        st_layout.setContentsMargins(25, 0, 25, 5)
        self.status_lbl = QLabel("CONNECTING TO NEURAL NETWORK...")
        self.status_lbl.setObjectName("StatusLabel")
        st_layout.addWidget(self.status_lbl)
        layout.addWidget(status_frame)

        # 3. Chat Log (Glass scroll)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("ChatArea")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setContentsMargins(15, 10, 15, 10)
        self.scroll.setWidget(self.chat_widget)
        
        layout.addWidget(self.scroll, stretch=1)

        # 4. Waveform
        self.wave = WaveformWidget()
        layout.addWidget(self.wave)

        # 5. Bottom Control
        bottom = QFrame()
        bottom.setObjectName("ControlPanel")
        bottom.setFixedHeight(140)
        b_layout = QHBoxLayout(bottom)
        
        self.mic_btn = MicButton()
        self.mic_btn.clicked.connect(self._toggle_mic)
        b_layout.addWidget(self.mic_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(bottom)

    def _setup_logic(self):
        """Jarvis logic callbacks"""
        # Signallarni connect qilish
        self.bridge.listening_started.connect(self._on_listen_start_ui)
        self.bridge.listening_stopped.connect(self._on_listen_stop_ui)
        self.bridge.speaking_started.connect(self._on_speak_start_ui)
        self.bridge.speaking_stopped.connect(self._on_speak_stop_ui)
        self.bridge.text_received.connect(lambda t: self.add_message(t, True))
        self.bridge.response_received.connect(lambda t: self.add_message(t, False))

        # Jarvis klassini o'rnatish
        jarvis.on_listening_start = self.bridge.listening_started.emit
        jarvis.on_listening_stop = self.bridge.listening_stopped.emit
        jarvis.on_speaking_start = self.bridge.speaking_started.emit
        jarvis.on_speaking_stop = self.bridge.speaking_stopped.emit
        jarvis.on_text_received = self.bridge.text_received.emit
        jarvis.on_response = self.bridge.response_received.emit

        # Wake word detector
        wake_detector.start(self._on_wake_word)
        
        QTimer.singleShot(2000, lambda: self.status_lbl.setText("JARVIS V7 ONLINE // SAY 'JARVIS' OR CLICK MIC"))
        self.add_message("System online. Encryption active. Welcome, User.", False)
        
        # Dasturlarni scan qilish
        threading.Thread(target=jarvis.update_app_list, daemon=True).start()

    def _on_wake_word(self):
        """Jarvis deyilganda"""
        print("[UI] Wake Word signal received from detector!")
        # Bu callback boshqa thread dan keladi, QTimer orqali UI ga o'tamiz
        QTimer.singleShot(0, self._start_hands_free)

    def _start_hands_free(self):
        """Wake word aniqlanganda oynani ko'rsatish va tinglashni boshlash"""
        # Oynani oldingi planga chiqarish
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()
        self.raise_()
        
        if not jarvis.is_listening and not jarvis.is_speaking:
            wake_detector.pause()
            jarvis.listen_and_execute(on_done_callback=self._hands_free_done)

    def _hands_free_done(self):
        """Hands-free tugaganda wake detector-ni qayta yoqish"""
        wake_detector.resume()
        print("[UI] Wake Word Detector qayta yoqildi.")

    def _toggle_mic(self):
        """Mic tugmasi bosilganda"""
        if jarvis.is_speaking:
            return # Gapirayotgan bo'lsa kutish kerak
            
        if not jarvis.is_listening:
            wake_detector.pause()
            jarvis.listen()
            self.mic_btn.set_active(True)
        else:
            self.mic_btn.set_active(False)
            self.mic_btn.set_thinking(True)
            self.status_lbl.setText("PROCESSING NEURAL DATA...")
            
            def process():
                text = jarvis.stop_listening()
                if text:
                    res = jarvis.process_command(text)
                    jarvis.speak(res, callback=lambda: QTimer.singleShot(0, self._process_done))
                else:
                    QTimer.singleShot(0, self._process_done)
            
            threading.Thread(target=process, daemon=True).start()

    def _process_done(self):
        self.mic_btn.set_thinking(False)
        wake_detector.resume()
        self.status_lbl.setText("READY // STANDBY")

    # --- UI Callbacks (Thread Safe) ---
    def _on_listen_start_ui(self):
        self.status_lbl.setText("LISTENING... SOURCE IDENTIFIED")
        self.mic_btn.set_active(True)
        self.wave.start("listening")

    def _on_listen_stop_ui(self):
        self.wave.stop()
        self.mic_btn.set_active(False)

    def _on_speak_start_ui(self):
        self.status_lbl.setText("JARVIS SPEAKING // OUTPUT ACTIVE")
        self.wave.start("speaking")

    def _on_speak_stop_ui(self):
        self.wave.stop()
        self.status_lbl.setText("READY // WAITING FOR INPUT")

    def add_message(self, text, is_user=True):
        bubble = QFrame()
        bubble.setProperty("class", "MessageBubble")
        bubble.setObjectName("UserMessage" if is_user else "BotMessage")
        
        l = QVBoxLayout(bubble)
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("background: transparent; border: none;")
        l.addWidget(lbl)
        
        self.chat_layout.addWidget(bubble)
        
        # Scroll pastga
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()))
        
        # Animatsiya
        anim = QPropertyAnimation(bubble, b"geometry")
        anim.setDuration(300)
        anim.setStartValue(QRect(bubble.x(), bubble.y() + 15, bubble.width(), bubble.height()))
        anim.setEndValue(bubble.geometry())
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()

    def _fade_in(self):
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(800)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1.0)
        self.anim.start()

    # --- Mouse Events (Dragging) ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Orbitron fontini tekshirish
    # QFontDatabase orqali yuklash mumkin edi agar Assets da bo'lsa
    
    window = JarvisPyQtApp()
    window.show()
    sys.exit(app.exec())
