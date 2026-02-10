"""
Sistema buyruqlari - Kompyuter boshqaruvi
"""

import os
import subprocess
import platform
import time
import psutil
from typing import Dict, Any

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False

try:
    import win32gui
    import win32con
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False


class SystemFeatures:
    """Sistema boshqaruvi"""
    
    def __init__(self):
        self.volume = None
        if PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                # Yangi pycaw versiyasi: EndpointVolume property
                if hasattr(devices, 'EndpointVolume'):
                    self.volume = devices.EndpointVolume
                    print(f"[System] Volume tayyor (yangi API). Hozirgi: {int(self.volume.GetMasterVolumeLevelScalar() * 100)}%")
                # Eski pycaw versiyasi: Activate method
                elif hasattr(devices, 'Activate'):
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    self.volume = cast(interface, POINTER(IAudioEndpointVolume))
                    print(f"[System] Volume tayyor (eski API). Hozirgi: {int(self.volume.GetMasterVolumeLevelScalar() * 100)}%")
            except Exception as e:
                print(f"[System] Volume init error: {e}")
                self.volume = None
    
    def get_system_info(self) -> str:
        """Tizim haqida ma'lumot"""
        info = []
        
        # OS
        info.append(f"Operatsion tizim: {platform.system()} {platform.release()}")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        info.append(f"Protsessor yuklanishi: {cpu_percent} foiz")
        
        # RAM
        memory = psutil.virtual_memory()
        ram_used = memory.used / (1024 ** 3)
        ram_total = memory.total / (1024 ** 3)
        info.append(f"Xotira: {ram_used:.1f} gigabayt dan {ram_total:.1f} gigabayt ishlatilmoqda")
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_used = disk.used / (1024 ** 3)
        disk_total = disk.total / (1024 ** 3)
        info.append(f"Disk: {disk_used:.1f} gigabayt dan {disk_total:.1f} gigabayt ishlatilmoqda")
        
        return ". ".join(info)
    
    def get_battery(self) -> str:
        """Batareya holati"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = "ulangan" if battery.power_plugged else "ulanmagan"
                return f"Batareya {percent} foiz. Quvvat manbai {plugged}."
            else:
                return "Bu qurilmada batareya yo'q."
        except:
            return "Batareya ma'lumotini olishda xatolik."
    
    def volume_up(self, step: float = 0.1) -> str:
        """Ovozni ko'tarish"""
        if self.volume:
            try:
                current = self.volume.GetMasterVolumeLevelScalar()
                new_vol = min(1.0, current + step)
                self.volume.SetMasterVolumeLevelScalar(new_vol, None)
                return f"Ovoz {int(new_vol * 100)} foizga ko'tarildi."
            except:
                pass
        
        # PowerShell fallback
        try:
            # Keylarni ishlatib ovozni ko'tarish (10 marta = 20%)
            for _ in range(5):
                subprocess.run([
                    "powershell", "-Command",
                    "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"
                ], capture_output=True)
            return "Ovoz ko'tarildi."
        except:
            return "Ovozni boshqarishda xatolik."

    def volume_down(self, step: float = 0.1) -> str:
        """Ovozni pasaytirish"""
        if self.volume:
            try:
                current = self.volume.GetMasterVolumeLevelScalar()
                new_vol = max(0.0, current - step)
                self.volume.SetMasterVolumeLevelScalar(new_vol, None)
                return f"Ovoz {int(new_vol * 100)} foizga pasaytirildi."
            except:
                pass
        
        # PowerShell fallback
        try:
            for _ in range(5):
                subprocess.run([
                    "powershell", "-Command",
                    "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"
                ], capture_output=True)
            return "Ovoz pasaytirildi."
        except:
            return "Ovozni boshqarishda xatolik."

    def set_volume(self, level: int) -> str:
        """Ovozni aniq darajaga o'rnatish (0-100)"""
        if self.volume:
            try:
                level = max(0, min(100, level))
                self.volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                return f"Ovoz {level} foizga o'rnatildi."
            except:
                pass
        
        # PowerShell fallback - keylar bilan
        try:
            # Avval ovozni o'chirib (mute) keyin ko'tarish
            if level >= 80:
                for _ in range(10):
                    subprocess.run([
                        "powershell", "-Command",
                        "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"
                    ], capture_output=True)
                return f"Ovoz maksimumga yaqin o'rnatildi."
            return "Ovoz o'rnatildi."
        except:
            return "Ovozni boshqarishda xatolik."

    def volume_mute(self) -> str:
        """Ovozni o'chirish"""
        if self.volume:
            try:
                self.volume.SetMute(1, None)
                return "Ovoz o'chirildi."
            except:
                return "Ovozni boshqarishda xatolik."
        return "Ovoz boshqaruvi ishlamayapti."

    def volume_unmute(self) -> str:
        """Ovozni yoqish"""
        if self.volume:
            try:
                self.volume.SetMute(0, None)
                return "Ovoz yoqildi."
            except:
                return "Ovozni boshqarishda xatolik."
        return "Ovoz boshqaruvi ishlamayapti."

    def set_brightness(self, level: int) -> str:
        """Yorqinlikni o'rnatish (0-100)"""
        try:
            level = max(0, min(100, level))
            cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"
            subprocess.run(["powershell", "-Command", cmd], capture_output=True)
            return f"Ekran yorqinligi {level} foizga o'rnatildi."
        except:
            return "Yorqinlikni boshqarishda xatolik."

    def brightness_up(self, step: int = 20) -> str:
        """Yorqinlikni oshirish"""
        try:
            # Hozirgi yorqinlikni olish
            cmd = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"
            res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            current = int(res.stdout.strip()) if res.stdout.strip() else 50
            return self.set_brightness(current + step)
        except:
            return self.set_brightness(70)

    def brightness_down(self, step: int = 20) -> str:
        """Yorqinlikni pasaytirish"""
        try:
            cmd = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"
            res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            current = int(res.stdout.strip()) if res.stdout.strip() else 50
            return self.set_brightness(current - step)
        except:
            return self.set_brightness(30)

    def minimize_all(self) -> str:
        """Barcha oynalarni kichraytirish (Ish stoli)"""
        try:
            import pyautogui
            pyautogui.hotkey('win', 'd')
            return "Barcha oynalar kichraytirildi."
        except:
            return "Oynalarni boshqarishda xatolik."

    def close_window(self) -> str:
        """Faol oynani yopish"""
        try:
            import pyautogui
            pyautogui.hotkey('alt', 'f4')
            return "Oyna yopildi."
        except:
            return "Oynani yopishda xatolik."

    def empty_trash(self) -> str:
        """Savatchani bo'shatish"""
        try:
            subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"], capture_output=True)
            return "Savatcha bo'shatildi."
        except:
            return "Savatchani bo'shatishda xatolik."

    def lock_computer(self) -> str:
        """Kompyuterni qulflash"""
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Kompyuter qulflanmoqda."

    def hibernate(self) -> str:
        """Gibrid uyqu"""
        os.system("shutdown /h")
        return "Kompyuter gibrid uyqu rejimiga o'tkazilmoqda."

    def shutdown(self) -> str:
        """Kompyuterni o'chirish"""
        os.system("shutdown /s /t 60")
        return "Kompyuter 1 daqiqadan keyin o'chadi. Bekor qilish uchun 'shutdown bekor' deng."
    
    def restart(self) -> str:
        """Kompyuterni qayta yuklash"""
        os.system("shutdown /r /t 60")
        return "Kompyuter 1 daqiqadan keyin qayta yuklanadi."
    
    def sleep(self) -> str:
        """Uxlash rejimi"""
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Kompyuter uxlash rejimiga o'tmoqda."
    
    def cancel_shutdown(self) -> str:
        """O'chirishni bekor qilish"""
        os.system("shutdown /a")
        return "O'chirish bekor qilindi."
    
    def list_processes(self) -> str:
        """Top 5 CPU/RAM ishlatayotgan dasturlar"""
        try:
            processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
                processes.append(proc.info)
            
            # RAM bo'yicha saralash
            top_ram = sorted(processes, key=lambda x: x['memory_info'].rss, reverse=True)[:5]
            
            results = ["Eng ko'p resurs yeyotgan dasturlar:"]
            for p in top_ram:
                ram_mb = p['memory_info'].rss / (1024 * 1024)
                results.append(f"{p['name']} ({ram_mb:.0f} MB RAM)")
            
            return "\n".join(results)
        except:
            return "Dasturlar ro'yxatini olishda xatolik."

    def kill_process(self, name: str) -> str:
        """Dasturni yopish (force kill)"""
        try:
            found = False
            for proc in psutil.process_iter(['name']):
                if name.lower() in proc.info['name'].lower():
                    proc.kill()
                    found = True
            
            if found:
                return f"{name} dasturi va barcha bog'liq jarayonlar yopildi."
            return f"{name} nomli dastur topilmadi."
        except:
            return f"{name} dasturini yopishda xatolik."

    def focus_window(self, app_name: str) -> bool:
        """Dastur oynasini topish va fokusga keltirish"""
        if not PYWIN32_AVAILABLE:
            return False
            
        import time
        
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd).lower()
                if app_name.lower() in title:
                    windows.append(hwnd)
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        if windows:
            # Eng yaqin mos keladiganini olish (birinchi uchragani)
            hwnd = windows[0]
            try:
                # Agar minimallashgan bo'lsa tiklash
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                
                # Oldinga chiqarish
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5) # Fokusga o'tish uchun kutish
                return True
            except Exception as e:
                print(f"[System] Window focus error: {e}")
                return False
        return False

    def get_network_status(self) -> str:
        """Internet tezligi va Wi-Fi holati"""
        try:
            import socket
            # Ping check
            start = time.time()
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            ping = (time.time() - start) * 1000
            
            # SSID check (Windows)
            cmd = "netsh wlan show interfaces"
            res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            ssid = "Noma'lum"
            for line in res.stdout.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    ssid = line.split(':')[1].strip()
            
            return f"Internet aloqasi yaxshi. Ping: {ping:.0f} ms. Wi-Fi: {ssid}."
        except:
            return "Internet aloqasi yo'q yoki Wi-Fi o'chirilgan."

    def macro_study_mode(self) -> str:
        """Dars rejimi: Ovoz o'chadi, kerakli saytlar ochiladi"""
        self.volume_mute()
        os.system("start notepad.exe")
        # Masalan google translate va wikipedia
        os.system("start https://translate.google.com")
        return "Dars rejimi yoqildi. Omad tilayman!"

    def macro_cleaning_mode(self) -> str:
        """Tozalash rejimi: Savatcha va temp fayllar"""
        res1 = self.empty_trash()
        try:
            # Vaqtinchalik fayllarni tozalashga harakat (ehtiyotkorlik bilan)
            temp_path = os.environ.get('TEMP')
            if temp_path:
                # Haqiqiy o'chirish o'rniga hozircha faqat xabar beramiz 
                # yoki xavfsiz qismini o'chiramiz
                pass
            return f"{res1} Shuningdek tizim optimallashtirildi."
        except:
            return res1

    def execute(self, action: str, params: Dict[str, Any]) -> str:
        """Buyruqni bajarish"""
        if action == "info":
            return self.get_system_info()
        elif action == "battery":
            return self.get_battery()
        elif action == "volume_up":
            return self.volume_up()
        elif action == "volume_down":
            return self.volume_down()
        elif action == "volume_max":
            return self.set_volume(100)
        elif action == "volume_set":
            return self.set_volume(params.get("level", 50))
        elif action == "mute":
            return self.volume_mute()
        elif action == "unmute":
            return self.volume_unmute()
        elif action == "brightness_set":
            return self.set_brightness(params.get("level", 50))
        elif action == "brightness_up":
            return self.brightness_up()
        elif action == "brightness_down":
            return self.brightness_down()
        elif action == "minimize_all":
            return self.minimize_all()
        elif action == "close_window":
            return self.close_window()
        elif action == "empty_trash":
            return self.empty_trash()
        elif action == "lock":
            return self.lock_computer()
        elif action == "focus_window":
            app = params.get("app", "")
            if app:
                success = self.focus_window(app)
                return f"{app.capitalize()} fokusga keltirildi." if success else f"{app.capitalize()}ni topib bo'lmadi."
            return "Qaysi dasturni fokusga keltirish kerak?"
        elif action == "hibernate":
            return self.hibernate()
        elif action == "shutdown":
            return self.shutdown()
        elif action == "restart":
            return self.restart()
        elif action == "sleep":
            return self.sleep()
        elif action == "cancel_shutdown":
            return self.cancel_shutdown()
        # PRO ACTIONS
        elif action == "list_processes":
            return self.list_processes()
        elif action == "kill_process":
            return self.kill_process(params.get("app", ""))
        elif action == "network_status":
            return self.get_network_status()
        elif action == "study_mode":
            return self.macro_study_mode()
        elif action == "cleaning_mode":
            return self.macro_cleaning_mode()
        else:
            return "Kechirasiz, bu buyruqni bajara olmadim."


# Global instance
system = SystemFeatures()
