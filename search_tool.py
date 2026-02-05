import requests
from bs4 import BeautifulSoup
from googlesearch import search as google_search

class SearchTool:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_google(self, query, num_results=5):
        """Поиск через Google"""
        try:
            results = []
            for url in google_search(query, num_results=num_results, lang='ru'):
                results.append(url)
            return results
        except Exception as e:
            return [f"Ошибка Google поиска: {e}"]
    
    def search_yandex(self, query, num_results=5):
        """Поиск через Yandex"""
        try:
            search_url = f"https://yandex.ru/search/?text={query}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for item in soup.find_all('a', class_='Link', limit=num_results):
                href = item.get('href')
                if href and href.startswith('http'):
                    results.append(href)
            
            return results if results else ["Результаты не найдены"]
        except Exception as e:
            return [f"Ошибка Yandex поиска: {e}"]
    
    def search_practice(self, query):
        """Поиск судебной практики через оба поисковика"""
        full_query = f"судебная практика 44-фз {query}"
        
        google_results = self.search_google(full_query, num_results=3)
        yandex_results = self.search_yandex(full_query, num_results=3)
        
        combined = f"**Google результаты:**\n"
        for i, url in enumerate(google_results, 1):
            combined += f"{i}. {url}\n"
        
        combined += f"\n**Yandex результаты:**\n"
        for i, url in enumerate(yandex_results, 1):
            combined += f"{i}. {url}\n"
        
        return combined
