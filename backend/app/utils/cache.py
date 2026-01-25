"""
System cache'owania wyników analizy sentymentu.
In-memory cache z TTL (Time To Live) dla optymalizacji wydajności.
"""

import hashlib
import time
from typing import Dict, Optional
from collections import OrderedDict
import threading

from ..config import CACHE_TTL, CACHE_MAX_SIZE


class SentimentCache:
    """
    Cache dla wyników analizy sentymentu.
    Używa LRU (Least Recently Used) eviction policy.
    """
    
    def __init__(self, ttl: int = CACHE_TTL, max_size: int = CACHE_MAX_SIZE):
        """
        Inicjalizuje cache.
        
        Args:
            ttl: Time To Live w sekundach (domyślnie 3600 = 1 godzina)
            max_size: Maksymalna liczba wpisów w cache
        """
        self.ttl = ttl
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.Lock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def _hash_text(self, text: str) -> str:
        """
        Tworzy hash tekstu dla klucza cache.
        
        Args:
            text: Tekst do zahashowania
        
        Returns:
            Hash MD5 tekstu
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get(self, text: str) -> Optional[Dict]:
        """
        Pobiera wynik z cache jeśli istnieje i nie wygasł.
        
        Args:
            text: Tekst opinii
        
        Returns:
            Słownik z wynikiem analizy lub None jeśli nie znaleziono
        """
        key = self._hash_text(text)
        current_time = time.time()
        
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                # Sprawdź czy wpis nie wygasł
                if current_time - entry['timestamp'] < self.ttl:
                    # Przenieś na koniec (LRU)
                    self.cache.move_to_end(key)
                    self.stats["hits"] += 1
                    return entry['result']
                else:
                    # Wpis wygasł, usuń go
                    del self.cache[key]
            
            self.stats["misses"] += 1
            return None
    
    def set(self, text: str, result: Dict, ttl: Optional[int] = None) -> None:
        """
        Zapisuje wynik do cache.
        
        Args:
            text: Tekst opinii
            result: Wynik analizy sentymentu (słownik z polarity, subjectivity itp.)
            ttl: Time To Live w sekundach (opcjonalnie, domyślnie używa self.ttl)
        """
        key = self._hash_text(text)
        current_time = time.time()
        cache_ttl = ttl if ttl is not None else self.ttl
        
        with self.lock:
            # Usuń wpis jeśli istnieje
            if key in self.cache:
                del self.cache[key]
            
            # Sprawdź czy cache nie jest pełny
            if len(self.cache) >= self.max_size:
                # Usuń najstarszy wpis (LRU)
                self.cache.popitem(last=False)
                self.stats["evictions"] += 1
            
            # Dodaj nowy wpis
            self.cache[key] = {
                'result': result,
                'timestamp': current_time,
                'ttl': cache_ttl
            }
            # Przenieś na koniec (LRU)
            self.cache.move_to_end(key)
    
    def clear(self) -> None:
        """Czyści cały cache."""
        with self.lock:
            self.cache.clear()
            self.stats["hits"] = 0
            self.stats["misses"] = 0
            self.stats["evictions"] = 0
    
    def get_stats(self) -> Dict:
        """
        Zwraca statystyki cache.
        
        Returns:
            Słownik ze statystykami (hits, misses, evictions, size, hit_rate)
        """
        with self.lock:
            total = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0.0
            
            return {
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "evictions": self.stats["evictions"],
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": round(hit_rate, 2),
                "ttl": self.ttl
            }
    
    def cleanup_expired(self) -> int:
        """
        Usuwa wygasłe wpisy z cache.
        
        Returns:
            Liczba usuniętych wpisów
        """
        current_time = time.time()
        removed = 0
        
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if current_time - entry['timestamp'] >= entry['ttl']
            ]
            
            for key in expired_keys:
                del self.cache[key]
                removed += 1
        
        return removed


# Globalna instancja cache
sentiment_cache = SentimentCache()

