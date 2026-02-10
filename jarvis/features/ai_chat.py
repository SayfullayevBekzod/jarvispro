"""
AI Chat - Muxlisa.ai orqali suhbat
"""

from typing import Dict, Any, List
from core.speech import muxlisa


class AIChatFeatures:
    """AI suhbat"""
    
    def __init__(self):
        self.context: List[Dict] = []
        self.max_context = 10
    
    def chat(self, message: str) -> str:
        """AI bilan suhbat"""
        # Muxlisa API orqali javob olish
        response = muxlisa.chat(message, self.context)
        
        # Kontekstga qo'shish
        self.context.append({"role": "user", "content": message})
        self.context.append({"role": "assistant", "content": response})
        
        # Kontekstni cheklash
        if len(self.context) > self.max_context * 2:
            self.context = self.context[-self.max_context * 2:]
        
        return response or "Kechirasiz, javob olishda xatolik yuz berdi."
    
    def clear_context(self) -> str:
        """Kontekstni tozalash"""
        self.context = []
        return "Suhbat tarixi tozalandi."
    
    def execute(self, action: str, params: Dict[str, Any]) -> str:
        """Buyruqni bajarish"""
        if action == "chat":
            message = params.get("message", "")
            return self.chat(message)
        elif action == "clear":
            return self.clear_context()
        
        return "Kechirasiz, bu buyruqni bajara olmadim."


# Global instance
ai_chat = AIChatFeatures()
