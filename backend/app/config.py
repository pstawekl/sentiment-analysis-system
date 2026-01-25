"""
Konfiguracja aplikacji - ustawienia Ollama i innych komponentów.
"""

import os
from typing import Optional

# Konfiguracja Ollama
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")
OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "30"))

# Flaga do przełączania między Ollama a TextBlob
USE_OLLAMA: bool = os.getenv("USE_OLLAMA", "true").lower() == "true"

# Ustawienia cache
CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 godzina w sekundach
CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "10000"))  # maksymalna liczba wpisów

# Ustawienia batch processing
BATCH_CONCURRENT_LIMIT: int = int(os.getenv("BATCH_CONCURRENT_LIMIT", "5"))  # równoległe zapytania

# Ustawienia retry dla Ollama
OLLAMA_MAX_RETRIES: int = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
OLLAMA_RETRY_DELAY: float = float(os.getenv("OLLAMA_RETRY_DELAY", "1.0"))  # sekundy

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

