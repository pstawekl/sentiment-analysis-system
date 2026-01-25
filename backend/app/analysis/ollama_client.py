"""
Klient Ollama API do analizy sentymentu przy użyciu gpt-oss:120b-cloud.
Zawiera prompt engineering i parsing odpowiedzi JSON.
"""

import json
import re
import asyncio
from typing import Dict, Optional
import ollama
from textblob import TextBlob

from ..config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_MAX_RETRIES,
    OLLAMA_RETRY_DELAY,
    USE_OLLAMA
)
from ..utils.cache import sentiment_cache


class OllamaClient:
    """
    Klient do komunikacji z Ollama API dla analizy sentymentu.
    """
    
    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        timeout: int = OLLAMA_TIMEOUT
    ):
        """
        Inicjalizuje klienta Ollama.
        
        Args:
            base_url: URL serwera Ollama
            model: Nazwa modelu do użycia
            timeout: Timeout dla zapytań w sekundach
        """
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.client = ollama.Client(host=base_url)
    
    def _create_prompt(self, review_text: str) -> str:
        """
        Tworzy prompt dla analizy sentymentu.
        
        Args:
            review_text: Tekst opinii do analizy
        
        Returns:
            Sformatowany prompt
        """
        prompt = f"""You are a sentiment analysis assistant. Analyze the sentiment of the following customer review and return ONLY a valid JSON object with exactly this format:
{{"polarity": <number between -1.0 and 1.0>, "label": "<positive or negative>"}}

Rules:
- polarity: -1.0 (very negative) to 1.0 (very positive), where 0.0 is neutral
- label: "positive" if polarity > 0, "negative" if polarity <= 0
- Return ONLY the JSON object, no additional text, no explanations

Review: {review_text}

JSON:"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Optional[Dict]:
        """
        Parsuje odpowiedź z modelu i wyodrębnia JSON.
        Obsługuje zagnieżdżone JSON i odpowiedzi z dodatkowym tekstem.
        
        Args:
            response_text: Tekst odpowiedzi z modelu
        
        Returns:
            Słownik z polarity i label lub None jeśli parsing się nie powiódł
        """
        if not response_text:
            return None
        
        # Usuń whitespace i nowe linie
        response_text = response_text.strip()
        
        # Strategia 1: Spróbuj sparsować cały tekst jako JSON
        try:
            result = json.loads(response_text)
            if isinstance(result, dict) and 'polarity' in result and 'label' in result:
                return self._validate_and_normalize(result)
        except json.JSONDecodeError:
            pass
        
        # Strategia 2: Znajdź JSON w tekście (obsługuje zagnieżdżone obiekty)
        # Szukamy pierwszego { i ostatniego }, które tworzą prawidłowy JSON
        start_idx = response_text.find('{')
        if start_idx == -1:
            # Brak { w odpowiedzi
            return None
        
        # Znajdź pasujący } dla zagnieżdżonych JSON
        brace_count = 0
        end_idx = -1
        
        for i in range(start_idx, len(response_text)):
            if response_text[i] == '{':
                brace_count += 1
            elif response_text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i
                    break
        
        if end_idx == -1:
            # Nie znaleziono pasującego }
            return None
        
        json_str = response_text[start_idx:end_idx + 1]
        
        try:
            result = json.loads(json_str)
            return self._validate_and_normalize(result)
        except json.JSONDecodeError as e:
            print(f"Błąd parsowania JSON z odpowiedzi: {e}")
            print(f"Próbowano sparsować: {json_str[:200]}...")
            return None
    
    def _validate_and_normalize(self, result: Dict) -> Optional[Dict]:
        """
        Waliduje i normalizuje wynik parsowania JSON.
        
        Args:
            result: Słownik z wynikiem parsowania
        
        Returns:
            Zwalidowany i znormalizowany słownik lub None
        """
        try:
            # Walidacja struktury
            if 'polarity' not in result or 'label' not in result:
                return None
            
            polarity = float(result['polarity'])
            label = str(result['label']).lower()
            
            # Walidacja zakresu polarity
            if not (-1.0 <= polarity <= 1.0):
                polarity = max(-1.0, min(1.0, polarity))  # Clamp do zakresu
            
            # Walidacja label
            if label not in ['positive', 'negative']:
                # Użyj polarity do określenia label
                label = 'positive' if polarity > 0 else 'negative'
            
            return {
                'polarity': polarity,
                'subjectivity': 0.0,  # Model nie zwraca subjectivity, ustawiamy 0
                'label': label
            }
        
        except (ValueError, TypeError) as e:
            print(f"Błąd walidacji wyniku: {e}")
            return None
    
    def _analyze_with_textblob_fallback(self, text: str) -> Dict:
        """
        Fallback do TextBlob jeśli Ollama nie działa.
        
        Args:
            text: Tekst do analizy
        
        Returns:
            Słownik z wynikiem analizy
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        label = 'positive' if polarity > 0 else 'negative'
        
        return {
            'polarity': polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'label': label
        }
    
    async def analyze_sentiment(self, text: str, use_cache: bool = True) -> Dict:
        """
        Analizuje sentyment tekstu przy użyciu Ollama (lub TextBlob jako fallback).
        
        Args:
            text: Tekst opinii do analizy
            use_cache: Czy używać cache
        
        Returns:
            Słownik z polarity (-1 do 1), subjectivity (0 do 1) i label
        """
        if not isinstance(text, str) or len(text.strip()) == 0:
            return {"polarity": 0.0, "subjectivity": 0.0, "label": "negative"}
        
        # Sprawdź cache
        if use_cache:
            cached_result = sentiment_cache.get(text)
            if cached_result:
                return cached_result
        
        # Sprawdź czy Ollama jest włączony
        if not USE_OLLAMA:
            result = self._analyze_with_textblob_fallback(text)
            if use_cache:
                sentiment_cache.set(text, result)
            return result
        
        # Wywołanie Ollama z retry logic
        prompt = self._create_prompt(text)
        
        for attempt in range(OLLAMA_MAX_RETRIES):
            try:
                # Synchronous call do Ollama (ollama library nie jest async)
                # Użyj asyncio.to_thread dla async wrapper
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat(
                        model=self.model,
                        messages=[
                            {
                                'role': 'user',
                                'content': prompt
                            }
                        ],
                        stream=False,  # Wyłącz streaming dla kompletnej odpowiedzi
                        options={'temperature': 0.1}  # Niskie temperature dla konsystencji
                    )
                )
                
                # Wyodrębnij tekst odpowiedzi z chat response
                response_text = response.get('message', {}).get('content', '')
                
                # Parsuj odpowiedź
                result = self._parse_response(response_text)
                
                if result:
                    # Walidacja i normalizacja
                    if use_cache:
                        sentiment_cache.set(text, result)
                    return result
                else:
                    print(f"Nie udało się sparsować odpowiedzi z Ollama (próba {attempt + 1}/{OLLAMA_MAX_RETRIES})")
                    if attempt < OLLAMA_MAX_RETRIES - 1:
                        await asyncio.sleep(OLLAMA_RETRY_DELAY * (attempt + 1))
            
            except Exception as e:
                print(f"Błąd podczas wywoływania Ollama (próba {attempt + 1}/{OLLAMA_MAX_RETRIES}): {e}")
                if attempt < OLLAMA_MAX_RETRIES - 1:
                    await asyncio.sleep(OLLAMA_RETRY_DELAY * (attempt + 1))
                else:
                    # Ostatnia próba nie powiodła się, użyj fallback
                    print("Używam TextBlob jako fallback")
                    result = self._analyze_with_textblob_fallback(text)
                    if use_cache:
                        sentiment_cache.set(text, result)
                    return result
        
        # Jeśli wszystkie próby nie powiodły się, użyj fallback
        result = self._analyze_with_textblob_fallback(text)
        if use_cache:
            sentiment_cache.set(text, result)
        return result
    
    async def health_check(self) -> bool:
        """
        Sprawdza czy Ollama jest dostępny.
        
        Returns:
            True jeśli Ollama jest dostępny, False w przeciwnym razie
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.list()
            )
            return True
        except Exception as e:
            print(f"Ollama health check failed: {e}")
            return False


# Globalna instancja klienta
ollama_client = OllamaClient()

