# Backend - FastAPI Sentiment Analysis

## Wymagania

### Python Dependencies
- Python 3.10+
- Wszystkie zależności z `requirements.txt`

### Ollama (Wymagane)

System używa **gpt-oss:120b-cloud** przez Ollama do analizy sentymentu.

#### Instalacja Ollama

1. **Pobierz i zainstaluj Ollama:**
   - Windows/Mac/Linux: https://ollama.com
   - Ollama uruchamia się automatycznie jako serwis lokalny

2. **Skonfiguruj model gpt-oss:120b-cloud:**
   ```bash
   ollama pull gpt-oss:120b-cloud
   ```
   
   **Uwaga:** Model `gpt-oss:120b-cloud` to model chmurowy, który może wymagać dostępu do internetu i odpowiedniej konfiguracji Ollama Cloud.

3. **Weryfikacja:**
   ```bash
   ollama list
   # Powinien pokazać gpt-oss:120b-cloud
   ```

#### Konfiguracja Ollama

Domyślnie Ollama działa na `http://localhost:11434`.

Możesz zmienić ustawienia przez zmienne środowiskowe:
```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="gpt-oss:120b-cloud"
export USE_OLLAMA="true"  # false aby używać TextBlob
```

## Instalacja

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Pobranie danych corpora NLTK (pierwsze uruchomienie)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

## Uruchomienie

**WAŻNE:** Upewnij się, że Ollama jest uruchomiony przed startem backendu.

```bash
# Sprawdź czy Ollama działa
ollama list

# Uruchom backend
uvicorn app.main:app --reload --port 8000
```

Backend automatycznie:
- Sprawdzi dostępność Ollama przy starcie
- Użyje TextBlob jako fallback jeśli Ollama nie jest dostępny
- Załaduje i przeanalizuje dane przy starcie aplikacji

## API Endpoints

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### GET /api/health/ollama
Health check endpoint dla Ollama. Sprawdza czy Ollama jest dostępny i działa.

**Response (sukces):**
```json
{
  "status": "ok",
  "ollama_available": true,
  "model": "gpt-oss:120b-cloud",
  "base_url": "http://localhost:11434"
}
```

**Response (Ollama niedostępny):**
```json
{
  "status": "degraded",
  "ollama_available": false,
  "message": "Ollama nie jest dostępny, używany jest TextBlob jako fallback"
}
```

### GET /api/stats
Zwraca statystyki ogólne dotyczące analizowanych opinii.

**Response:**
```json
{
  "total_reviews": 1000,
  "positive_count": 650,
  "negative_count": 350,
  "positive_percentage": 65.0,
  "negative_percentage": 35.0
}
```

### GET /api/polarity/average
Zwraca średnią polaryzację wszystkich opinii.

**Response:**
```json
{
  "average_polarity": 0.42
}
```

### GET /api/words/top?limit=20
Zwraca najczęściej występujące słowa (domyślnie 20).

**Query Parameters:**
- `limit` (int, optional): Liczba słów do zwrócenia (default: 20)

**Response:**
```json
{
  "words": [
    {"word": "great", "count": 234},
    {"word": "excellent", "count": 189},
    ...
  ]
}
```

### POST /api/analyze
Analizuje pojedynczą opinię przy użyciu gpt-oss:120b-cloud przez Ollama.

**Request Body:**
```json
{
  "review_text": "This product is amazing!"
}
```

**Response:**
```json
{
  "polarity": 0.8,
  "sentiment_label": "positive",
  "word_count": 4
}
```

**Uwagi:**
- Wyniki są cache'owane dla identycznych tekstów (TTL: 1 godzina)
- Jeśli Ollama nie jest dostępny, używa TextBlob jako fallback
- Analiza jest asynchroniczna dla lepszej wydajności

### POST /api/reload
Ręczne przeładowanie danych i cache (tylko development).

**Response:**
```json
{
  "status": "success",
  "message": "Zaladowano 50 opinii",
  "cache_stats": {
    "hits": 10,
    "misses": 5,
    "evictions": 0,
    "size": 15,
    "max_size": 10000,
    "hit_rate": 66.67,
    "ttl": 3600
  }
}
```

## Troubleshooting

### Ollama nie jest dostępny

**Problem:** Backend nie może połączyć się z Ollama.

**Rozwiązanie:**
1. Sprawdź czy Ollama jest uruchomiony:
   ```bash
   ollama list
   ```
2. Sprawdź port 11434:
   ```bash
   curl http://localhost:11434/api/tags
   ```
3. Uruchom Ollama jeśli nie działa:
   ```bash
   ollama serve
   ```

### Model nie został pobrany/skonfigurowany

**Problem:** `gpt-oss:120b-cloud` nie jest dostępny.

**Rozwiązanie:**
```bash
ollama pull gpt-oss:120b-cloud
```

**Uwaga:** Model `gpt-oss:120b-cloud` to model chmurowy. Upewnij się, że:
- Masz dostęp do internetu
- Ollama Cloud jest poprawnie skonfigurowane (jeśli wymagane)
- Masz odpowiednie uprawnienia do użycia modelu w chmurze

### Wolna analiza batch

**Problem:** Analiza wielu opinii trwa zbyt długo.

**Rozwiązanie:**
- Zwiększ `BATCH_CONCURRENT_LIMIT` w `config.py` (domyślnie 5)
- System cache'uje wyniki, kolejne uruchomienia będą szybsze

### Błędy parsowania JSON

**Problem:** Model zwraca niepoprawny format JSON.

**Rozwiązanie:**
- System automatycznie próbuje 3 razy z retry logic
- Jeśli wszystkie próby nie powiodą się, używa TextBlob jako fallback
- Sprawdź logi backendu dla szczegółów błędów
- Model chmurowy może wymagać dodatkowego czasu na odpowiedź

