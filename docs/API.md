# Referencja API – System Analizy Sentymentu

Bazowy URL: `http://localhost:8000` (lub przez proxy frontendu: `/api`).

Wszystkie endpointy zwracają JSON, oprócz `GET /api/report/pdf`, który zwraca plik PDF.

---

## Health check

### GET /api/health

Sprawdzenie dostępności API.

**Odpowiedź 200**

```json
{
  "status": "ok"
}
```

---

### GET /api/health/ollama

Sprawdzenie dostępności Ollama.

**Odpowiedź 200 (Ollama dostępny)**

```json
{
  "status": "ok",
  "ollama_available": true,
  "model": "gpt-oss:120b-cloud",
  "base_url": "http://localhost:11434"
}
```

**Odpowiedź 200 (Ollama niedostępny)**

```json
{
  "status": "degraded",
  "ollama_available": false,
  "message": "Ollama nie jest dostępny, używany jest TextBlob jako fallback"
}
```

**Odpowiedź 200 (błąd)**

```json
{
  "status": "error",
  "ollama_available": false,
  "error": "opis błędu"
}
```

---

## Statystyki i dane zbiorcze

### GET /api/stats

Zwraca statystyki ogólne dotyczące analizowanych opinii (z cache EDA).

**Odpowiedź 200**

```json
{
  "total_reviews": 200,
  "positive_count": 120,
  "negative_count": 80,
  "positive_percentage": 60.0,
  "negative_percentage": 40.0,
  "average_polarity": 0.25,
  "average_review_length": 85.5,
  "average_word_count": 15.2
}
```

**Odpowiedź 503** – dane nie załadowane (np. brak pliku dataset).

```json
{
  "detail": "Dane nie zostały załadowane. Uruchom: python scripts/download_data.py"
}
```

---

### GET /api/polarity/average

Zwraca średnią polaryzację wszystkich opinii.

**Odpowiedź 200**

```json
{
  "average_polarity": 0.25
}
```

**Odpowiedź 503** – gdy dane nie załadowane.

---

### GET /api/words/top

Zwraca najczęściej występujące słowa w opiniach.

**Parametry query**

| Parametr | Typ   | Domyślnie | Opis              |
|----------|-------|-----------|-------------------|
| `limit`  | int   | 20        | Liczba słów (1–100) |

**Przykład:** `GET /api/words/top?limit=30`

**Odpowiedź 200**

```json
{
  "words": [
    { "word": "product", "count": 45 },
    { "word": "quality", "count": 32 }
  ],
  "total_words_analyzed": 1200
}
```

**Odpowiedź 503** – gdy dane nie załadowane.

---

### GET /api/reviews

Zwraca listę wszystkich opinii z wynikami analizy (do wyświetlenia w gridzie).

**Odpowiedź 200**

```json
{
  "reviews": [
    {
      "index": 1,
      "review_id": 1,
      "review_text": "This product is absolutely amazing!...",
      "polarity": 0.85,
      "sentiment_label": "positive",
      "word_count": 12,
      "review_length": 52
    }
  ]
}
```

**Odpowiedź 200 (brak danych):** `{ "reviews": [] }`

---

## Analiza pojedynczej opinii

### POST /api/analyze

Analizuje pojedynczą opinię, zapisuje ją do `dataset.csv` i aktualizuje cache (statystyki, wykresy).

**Body (JSON)**

```json
{
  "review_text": "Tekst opinii do analizy."
}
```

- `review_text` – wymagane, niepuste.

**Odpowiedź 200**

```json
{
  "polarity": 0.65,
  "sentiment_label": "positive",
  "word_count": 8
}
```

- `polarity`: liczba z zakresu -1.0 do 1.0  
- `sentiment_label`: `"positive"` lub `"negative"`  
- `word_count`: liczba słów w tekście

**Odpowiedź 400** – pusty tekst opinii

```json
{
  "detail": "Tekst opinii nie może być pusty"
}
```

---

## Raport PDF

### GET /api/report/pdf

Generuje i zwraca raport PDF (podsumowanie + lista opinii).

**Odpowiedź 200**

- `Content-Type: application/pdf`
- `Content-Disposition: attachment; filename="raport_sentyment.pdf"`
- Body: binarny plik PDF

**Odpowiedź 503** – dane nie załadowane.

**Odpowiedź 500** – błąd podczas generowania PDF (np. brak kolumn w danych).

---

## Development

### POST /api/reload

Przeładowuje dane z pliku (wczytanie, czyszczenie, analiza batch, EDA). Przydatne po ręcznej edycji `dataset.csv`.

**Odpowiedź 200**

```json
{
  "status": "success",
  "message": "Zaladowano 200 opinii",
  "cache_stats": {
    "hits": 0,
    "misses": 0,
    "evictions": 0,
    "size": 0,
    "max_size": 10000,
    "hit_rate": 0,
    "ttl": 3600
  }
}
```

**Odpowiedź 500** – błąd podczas wczytywania danych.

---

## Kody błędów i CORS

- **400** – Nieprawidłowe żądanie (np. pusty `review_text`).
- **500** – Błąd serwera (np. generowanie PDF, przeładowanie danych).
- **503** – Serwis niedostępny (brak załadowanych danych).

CORS: dozwolone originy to `http://localhost:5173` i `http://localhost:3000` (konfiguracja w `backend/app/main.py`).
