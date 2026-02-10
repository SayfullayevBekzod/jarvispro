import os
import webbrowser
import requests
import urllib.parse
from typing import Dict, Any, List

import config


class WebFeatures:
    """Internet funksiyalari"""
    
    def get_urls(self) -> Dict[str, str]:
        """Skanerlangan URL'larni olish"""
        from features.app_scanner import app_scanner
        return app_scanner.scan_urls()
    
    def search_google(self, query: str, silent: bool = False) -> str:
        """Googleda qidirish"""
        if silent:
            return self.silent_google_search(query)
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"Google'da '{query}' qidirilmoqda."
    
    def smart_search(self, query: str) -> str:
        """
        Ko'p manbali aqlli qidiruv + AI summarizatsiya
        Manbalar: DuckDuckGo API → Wikipedia → Google Snippets → Web Scraping
        """
        import re
        import json
        import urllib.request
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # So'rovni tozalash
        clean_q = re.sub(
            r'\b(qaysi|nima|haqida|ma\'lumot|ber|ayt|aytun|sizga|menga|qanday|kimdir)\b', 
            '', query, flags=re.IGNORECASE
        ).strip()
        if not clean_q or len(clean_q) < 3:
            clean_q = query
        
        print(f"[Smart Search] So'rov: '{clean_q}' (asl: '{query}')")
        
        collected_info = []
        
        # ===== 1. DuckDuckGo Instant Answer API (eng ishonchli) =====
        try:
            ddg_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(clean_q)}&format=json&no_html=1&skip_disambig=1"
            req = urllib.request.Request(ddg_url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                
                # Abstract (asosiy javob)
                abstract = data.get("AbstractText", "")
                if abstract and len(abstract) > 30:
                    source = data.get("AbstractSource", "DuckDuckGo")
                    collected_info.append(f"[{source}] {abstract}")
                    print(f"[Smart Search] DDG Abstract topildi: {len(abstract)} belgi")
                
                # Answer (to'g'ridan-to'g'ri javob)
                answer = data.get("Answer", "")
                if answer:
                    collected_info.append(f"[Javob] {answer}")
                    print(f"[Smart Search] DDG Answer: {answer[:80]}")
                
                # Related topics
                if not collected_info:
                    topics = data.get("RelatedTopics", [])
                    for topic in topics[:3]:
                        text = topic.get("Text", "")
                        if text and len(text) > 20:
                            collected_info.append(f"[DDG] {text}")
        except Exception as e:
            print(f"[Smart Search] DDG API xato: {e}")
        
        # ===== 2. Wikipedia API (Uz va En) =====
        for lang in ["uz", "en"]:
            if len(collected_info) >= 2:
                break
            try:
                # Avval qidirish
                search_url = f"https://{lang}.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(clean_q)}&limit=1&namespace=0&format=json"
                req = urllib.request.Request(search_url, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
                    if len(data) >= 4 and data[1]:
                        title = data[1][0]
                        
                        # Maqola matnini olish
                        extract_url = f"https://{lang}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={urllib.parse.quote(title)}&format=json&exsentences=5"
                        req2 = urllib.request.Request(extract_url, headers=headers)
                        with urllib.request.urlopen(req2, timeout=5) as resp2:
                            edata = json.loads(resp2.read().decode())
                            pages = edata.get("query", {}).get("pages", {})
                            for pid in pages:
                                txt = pages[pid].get("extract", "")
                                if txt and len(txt) > 30:
                                    collected_info.append(f"[Wikipedia {lang.upper()}] {txt[:800]}")
                                    print(f"[Smart Search] Wiki ({lang}): {len(txt)} belgi")
                                    break
            except Exception as e:
                print(f"[Smart Search] Wiki ({lang}) xato: {e}")
        
        # ===== 3. Google Search Snippets =====
        if not collected_info:
            try:
                google_url = f"https://www.google.com/search?q={urllib.parse.quote(clean_q)}&hl=uz"
                req = urllib.request.Request(google_url, headers=headers)
                with urllib.request.urlopen(req, timeout=7) as resp:
                    html = resp.read().decode(errors='ignore')
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Featured snippet
                    featured = soup.find('div', class_='BNeawe')
                    if featured:
                        text = featured.get_text().strip()
                        if len(text) > 20:
                            collected_info.append(f"[Google] {text[:500]}")
                            print(f"[Smart Search] Google snippet: {text[:80]}")
                    
                    # Search result descriptions
                    if not collected_info:
                        spans = soup.find_all('span', class_='BNeawe')
                        texts = []
                        for s in spans:
                            t = s.get_text().strip()
                            if len(t) > 40 and t not in texts:
                                texts.append(t)
                            if len(texts) >= 3:
                                break
                        if texts:
                            collected_info.append(f"[Google] {' '.join(texts[:3])}")
            except Exception as e:
                print(f"[Smart Search] Google xato: {e}")
        
        # ===== 4. DuckDuckGo HTML Fallback =====
        if not collected_info:
            try:
                ddg_html_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(clean_q)}"
                req = urllib.request.Request(ddg_html_url, headers=headers)
                with urllib.request.urlopen(req, timeout=7) as resp:
                    html = resp.read().decode(errors='ignore')
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    snippets = soup.find_all('a', class_='result__snippet')
                    for s in snippets[:3]:
                        text = s.get_text().strip()
                        if len(text) > 30:
                            collected_info.append(f"[Web] {text}")
                    if collected_info:
                        print(f"[Smart Search] DDG HTML: {len(collected_info)} snippet")
            except Exception as e:
                print(f"[Smart Search] DDG HTML xato: {e}")
        
        # ===== Natijalarni birlashtirish =====
        if not collected_info:
            print(f"[Smart Search] Hech narsa topilmadi: '{query}'")
            return f"Kechirasiz, '{query}' haqida internetdan ma'lumot topib bo'lmadi."
        
        raw_info = "\n".join(collected_info)
        print(f"[Smart Search] Jami {len(collected_info)} ta manba topildi")
        
        # ===== Gemini AI bilan umumlashtirish =====
        summarized = self._ai_summarize(query, raw_info)
        if summarized:
            return summarized
        
        # AI ishlamasa, xom natijani qaytarish (qisqartirib)
        return raw_info[:500]
    
    def _ai_summarize(self, question: str, raw_info: str) -> str:
        """Gemini AI yordamida qidiruv natijalarini umumlashtirish"""
        try:
            import google.generativeai as genai
            
            if "YOUR_GEMINI_API_KEY_HERE" in config.GEMINI_API_KEY:
                return None
            
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            prompt = (
                f"Quyidagi ma'lumotlar asosida savolga qisqa va aniq javob ber (2-3 gap, o'zbek tilida).\n\n"
                f"Savol: {question}\n\n"
                f"Topilgan ma'lumotlar:\n{raw_info[:1500]}\n\n"
                f"Qisqa javob:"
            )
            
            response = model.generate_content(prompt)
            answer = response.text.strip()
            
            if answer and len(answer) > 5:
                print(f"[Smart Search] AI javob: {answer[:80]}...")
                return answer
        except Exception as e:
            print(f"[Smart Search] AI summarize xato: {e}")
        
        return None
    
    def silent_google_search(self, query: str) -> str:
        """Backward compatibility — smart_search ga yo'naltirish"""
        return self.smart_search(query)
    
    def search_youtube(self, query: str) -> str:
        """YouTubeda qidirish"""
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"YouTube'da '{query}' qidirilmoqda."
    
    def play_youtube_music(self, query: str) -> str:
        """YouTubeda musiqa qo'yish"""
        # YouTube Music orqali
        url = f"https://music.youtube.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"YouTube Music'da '{query}' qo'shig'i qo'yilmoqda."
    
    def play_youtube_video(self, query: str) -> str:
        """YouTubeda birinchi videoni ochish"""
        try:
            # YouTube qidiruv sahifasini ochish
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            return f"YouTube'da '{query}' topilmoqda. Birinchi natijani bosing."
        except Exception as e:
            return f"YouTube ochishda xatolik: {e}"
    
    def search_wikipedia(self, query: str) -> str:
        """Wikipediada qidirish"""
        url = f"https://uz.wikipedia.org/wiki/{urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"Wikipedia'da '{query}' haqida ma'lumot qidirilmoqda."
    
    def open_website(self, url: str) -> str:
        """Saytni ochish"""
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Sayt ochilmoqda."
    
    def open_social(self, platform: str) -> str:
        """Ijtimoiy tarmoqni ochish"""
        urls = {
            "youtube": "https://www.youtube.com",
            "telegram": "https://web.telegram.org",
            "instagram": "https://www.instagram.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://twitter.com",
            "tiktok": "https://www.tiktok.com",
            "linkedin": "https://www.linkedin.com",
            "github": "https://github.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
        }
        
        platform_lower = platform.lower()
        if platform_lower in urls:
            webbrowser.open(urls[platform_lower])
            return f"{platform} ochilmoqda."
        else:
            return f"{platform} topilmadi."
    
    def get_weather(self, city: str = None) -> str:
        """Ob-havo ma'lumoti"""
        city = city or self.default_city
        
        if not self.weather_api_key:
            # API yo'q bo'lsa, oddiy javob
            return f"{city} shahridagi ob-havo ma'lumotini olish uchun Weather API kaliti kerak."
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": self.weather_api_key,
                "units": "metric",
                "lang": "uz"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                description = data["weather"][0]["description"]
                
                return f"{city} shahrida hozir {temp:.0f} daraja. His etiladi {feels_like:.0f} daraja. {description.capitalize()}. Namlik {humidity} foiz."
            else:
                return f"Ob-havo ma'lumotini olishda xatolik."
                
        except Exception as e:
            return f"Ob-havo ma'lumotini olishda xatolik: {str(e)}"
    
    def execute(self, action: str, params: Dict[str, Any]) -> str:
        """Buyruqni bajarish"""
        if action == "search":
            engine = params.get("engine", "google")
            query = params.get("query", "")
            
            if engine == "google":
                return self.search_google(query)
            elif engine == "youtube":
                return self.search_youtube(query)
            elif engine == "wikipedia":
                return self.search_wikipedia(query)
            elif engine == "direct":
                return self.open_website(query)
        elif action == "youtube_music":
            query = params.get("query", "")
            return self.play_youtube_music(query)
        elif action == "youtube_video":
            query = params.get("query", "")
            return self.play_youtube_video(query)
        elif action == "social":
            platform = params.get("platform", "")
            return self.open_social(platform)
        elif action == "current":
            city = params.get("city")
            return self.get_weather(city)
        
        return "Kechirasiz, bu buyruqni bajara olmadim."


# Global instance
web = WebFeatures()
