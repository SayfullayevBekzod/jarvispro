"""
Database Manager - Savol-javoblarni saqlash va boshqarish
SQLite ishlatiladi
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Tuple


class DatabaseManager:
    """Jarvis uchun ma'lumotlar bazasi"""
    
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "..", "data", "jarvis.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Bazani yaratish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Savol-javoblar jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT UNIQUE,
                answer TEXT,
                timestamp DATETIME
            )
        ''')
        
        # Dasturlar scan natijalari (kelajakda ishlatish uchun)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                path TEXT,
                last_scanned DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_qa(self, question: str, answer: str):
        """Savol va javobni saqlash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            question = question.lower().strip()
            cursor.execute(
                "INSERT OR REPLACE INTO qa (question, answer, timestamp) VALUES (?, ?, ?)",
                (question, answer, datetime.now())
            )
            
            conn.commit()
            conn.close()
            print(f"[DB] Savol saqlandi: {question[:30]}...")
        except Exception as e:
            print(f"[DB] Saqlashda xato: {e}")
    
    def get_answer(self, question: str) -> Optional[str]:
        """Savolga javobni bazadan qidirish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            question = question.lower().strip()
            cursor.execute("SELECT answer FROM qa WHERE question = ?", (question,))
            result = cursor.fetchone()
            
            conn.close()
            if result:
                return result[0]
        except Exception as e:
            print(f"[DB] O'qishda xato: {e}")
        return None

    def save_apps(self, apps_dict: dict):
        """Dasturlarni bazaga saqlash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for name, path in apps_dict.items():
                cursor.execute(
                    "INSERT OR REPLACE INTO apps (name, path, last_scanned) VALUES (?, ?, ?)",
                    (name.lower(), path, datetime.now())
                )
            
            conn.commit()
            conn.close()
            print(f"[DB] {len(apps_dict)} ta dastur saqlandi.")
        except Exception as e:
            print(f"[DB] Dasturlarni saqlashda xato: {e}")

    def get_all_apps(self) -> dict:
        """Barcha saqlangan dasturlarni olish"""
        apps = {}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, path FROM apps")
            results = cursor.fetchall()
            for name, path in results:
                apps[name] = path
            conn.close()
        except Exception as e:
            print(f"[DB] Dasturlarni o'qishda xato: {e}")
        return apps

    def get_all_qa(self) -> List[Tuple[str, str]]:
        """Barcha savol-javoblarni olish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT question, answer FROM qa ORDER BY timestamp DESC")
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []


# Global instance
db = DatabaseManager()
