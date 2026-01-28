# Architektura techniczna – Backend i Frontend

## Backend (Python / FastAPI)

### Aplikacja główna – `app/main.py`

- **FastAPI** z CORS dla `localhost:5173` i `localhost:3000`.
- **Startup:** sprawdzenie Ollama (`ollama_client.health_check()`), wczytanie danych (`load_data` → `clean_data` → `analyze_batch_async` → `perform_eda`), zapis wyników w zmiennych globalnych `cached_df` i `eda_stats`.
- **Cache:** wyniki EDA i DataFrame trzymane w pamięci; przy braku danych endpointy mogą wywołać ponownie `load_and_analyze_data()` lub zwrócić 503.

### Modele API – `app/models.py`

Modele Pydantic dla request/response:

| Model                   | Opis |
|-------------------------|------|
| `ReviewInput`           | Wejście: `review_text` (wymagane) |
| `SentimentResponse`     | Wyjście analizy: `polarity`, `sentiment_label`, `word_count` |
| `StatisticsResponse`    | Statystyki: `total_reviews`, `positive_count`, `negative_count`, procenty, średnie |
| `AveragePolarityResponse` | `average_polarity` |
| `TopWordsResponse`      | `words` (lista `{word, count}`), `total_words_analyzed` |
| `ReviewItem`            | Jedna opinia w liście: `index`, `review_id`, `review_text`, `polarity`, `sentiment_label`, `word_count`, `review_length` |
| `ReviewsListResponse`   | `reviews: List[ReviewItem]` |
| `HealthResponse`        | `status` |

### Konfiguracja – `app/config.py`

- **Ollama:** `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT`, `USE_OLLAMA`, `OLLAMA_MAX_RETRIES`, `OLLAMA_RETRY_DELAY`
- **Cache:** `CACHE_TTL`, `CACHE_MAX_SIZE`
- **Batch:** `BATCH_CONCURRENT_LIMIT`
- **Logowanie:** `LOG_LEVEL`  
Wartości z zmiennych środowiskowych, z podanymi wyżej domyślnymi.

---

### Analiza sentymentu – `app/analysis/`

#### `sentiment.py`

- **`analyze_sentiment_async(text, use_cache)`** – analiza jednego tekstu przez Ollama (z cache); zwraca `{polarity, subjectivity, label}`.
- **`analyze_sentiment(text)`** – wersja synchroniczna (wrapper na async).
- **`classify_sentiment(polarity)`** – zwraca `"positive"` jeśli `polarity > 0`, w przeciwnym razie `"negative"`.
- **`perform_eda(df)`** – EDA: `review_length`, `word_count` (apply), ewentualnie `polarity`/`sentiment_label`, `value_counts()`, `str.contains()` (np. "excellent", "terrible"); zwraca `(eda_results dict, df)`.
- **`get_top_words(df, limit, remove_stopwords)`** – tokenizacja przez `preprocess_text`, `pd.Series` → `value_counts()` → `nlargest(limit)`; zwraca lista `{word, count}`.
- **`analyze_batch_async(df, concurrent_limit)`** – równoległa analiza wszystkich opinii (semaphore), zapis `polarity` i `sentiment_label` w DataFrame.
- **`analyze_batch(df)`** – synchroniczny wrapper na `analyze_batch_async`.
- **`get_average_polarity(df)`** – średnia z kolumny `polarity` (lub wyliczenie z `review_text` jeśli brak `polarity`).

#### `ollama_client.py` – klasa `OllamaClient`

- **Prompt:** generuje prompt wymagający odpowiedzi w formacie JSON: `{"polarity": number, "label": "positive"|"negative"}`.
- **`_parse_response(response_text)`** – wyciąga JSON z odpowiedzi (cały tekst lub pierwszy `{...}`), obsługa zagnieżdżeń.
- **`_validate_and_normalize(result)`** – sprawdza zakres `polarity` (-1..1), normalizuje `label`.
- **`analyze_sentiment(text, use_cache)`** (async): sprawdza cache → jeśli `USE_OLLAMA` wywołuje Ollama z retry; przy błędzie/nieparsowaniu używa **TextBlob** (`_analyze_with_textblob_fallback`).
- **`health_check()`** (async) – sprawdza dostępność Ollama (`client.list()` w executorze).

Używana jest globalna instancja `ollama_client`.

#### `preprocessing.py` (NLTK)

- **`get_stopwords(language)`** – zbiór stopwords (domyślnie angielski).
- **`normalize_text(text)`** – lowercase, usunięcie znaków innych niż alfanumeryczne i spacje, sklejenie białych znaków.
- **`tokenize_text(text)`** – `word_tokenize` (NLTK).
- **`remove_stopwords(tokens, language)`** – filtrowanie tokenów.
- **`preprocess_text(text, remove_stop, language)`** – normalizacja → tokenizacja → usunięcie stopwords → filtrowanie tokenów < 2 znaki; zwraca lista tokenów.
- **`preprocess_text_to_string(...)`** – to samo, wynik jako jeden string.

Przy pierwszym imporcie pobierane są NLTK `punkt` i `stopwords` (jeśli brak).

---

### Dane – `app/data/loader.py`

- **`get_dataset_path(file_path)`** – ścieżka do `backend/data/dataset.csv` (lub podany plik).
- **`load_data(file_path)`** – `pd.read_csv`, encoding UTF-8; przy braku pliku wyjątek z komunikatem o `download_data.py`.
- **`clean_data(df)`** – `dropna(subset=['review_text'])`, `drop_duplicates(subset=['review_text'])`, usunięcie pustych po `strip()`.
- **`append_review(review_id, review_text, sentiment, rating, file_path)`** – dopisanie jednego wiersza do CSV (moduł `csv`) z poprawnym escapowaniem.
- **`preprocess_text_basic(text)`** – lowercase i usunięcie nadmiarowych spacji (bez NLTK).
- **`get_dataframe_info(df)`** – liczba wierszy, kolumny, brakujące wartości, typy.

---

### Raporty – `app/reports/pdf_report.py`

- **`build_report_pdf(df, eda_stats)`** – generuje PDF (ReportLab):
  - Nagłówek z datą.
  - Tabela podsumowania: liczba opinii, pozytywne/negatywne (z %), średnia polaryzacja, średnia długość, średnia liczba słów.
  - Tabela opinii: Lp., fragment tekstu (skrócony do `MAX_REVIEW_SNIPPET_LEN`), polaryzacja, sentyment, liczba słów.
- Zwraca `bytes` (zawartość PDF).

---

### Cache – `app/utils/cache.py`

- **Klasa `SentimentCache`:** in-memory, LRU, TTL.
  - Klucz: hash MD5 tekstu.
  - `get(text)` – zwraca wynik jeśli wpis istnieje i nie wygasł; aktualizuje LRU i statystyki (hits/misses).
  - `set(text, result, ttl)` – zapis, przy przepełnieniu usuwa najstarszy wpis (evictions).
  - `get_stats()` – hits, misses, evictions, size, max_size, hit_rate, ttl.
  - `cleanup_expired()` – usuwa wygasłe wpisy.
- W analizie sentymentu używana jest globalna instancja `sentiment_cache`.

---

## Frontend (React / TypeScript)

### Aplikacja – `src/App.tsx`

- Renderuje jeden komponent: **`Dashboard`**; style z `App.css`.

### Serwis API – `src/services/api.ts`

- **Axios** z `baseURL: ''`, timeout 10 s (30 s dla PDF).
- Interceptor błędów: zamiana `ERR_NETWORK` / `ECONNREFUSED` na czytelne komunikaty po polsku.
- Funkcje: `getReviews`, `getStatistics`, `getAveragePolarity`, `getTopWords(limit)`, `analyzeSingle(reviewText)`, `healthCheck`, `getReportPdf()` (responseType blob).

Zapytania idą na `/api/...`; Vite proxy przekierowuje je na `http://127.0.0.1:8000`.

### Typy – `src/types/index.ts`

- `Statistics`, `WordCount`, `TopWords`, `SentimentAnalysis`, `AveragePolarity`, `ReviewItem` – zgodne z modelami backendu.

### Komponenty – `src/components/`

| Komponent           | Opis |
|---------------------|------|
| **Dashboard**       | Ładuje statystyki, TOP słowa, listę opinii; przycisk „Pobierz raport PDF”; wyświetla Statistics, SentimentChart, SingleAnalysis, ReviewsGrid; obsługa błędów i „Spróbuj ponownie”. |
| **Statistics**      | Karty: całkowita liczba opinii, pozytywne (z %), negatywne (z %), średnia polaryzacja; dodatkowo średnia długość i średnia liczba słów. |
| **SentimentChart**  | Chart.js: wykres słupkowy i doughnut (pozytywne vs negatywne). |
| **SingleAnalysis**  | Textarea + przyciski „Analizuj” / „Wyczyść”; przykładowe teksty; wyświetlanie wyniku (polaryzacja, etykieta, liczba słów, pasek wizualizacji); callback `onAnalysisSuccess` do odświeżenia danych. |
| **ReviewsGrid**     | Tabela opinii: Lp., fragment tekstu (skrócony), polaryzacja, sentyment (Pozytywny/Negatywny), liczba słów. |
| **WordCloud**       | Lista TOP słów z paskami proporcjonalnymi do liczby wystąpień (do 30 słów). Obecnie nie jest używany w Dashboardzie; Dashboard ładuje `getTopWords(30)` ale nie renderuje `WordCloud`. |

### Konfiguracja Vite – `vite.config.ts`

- Port 5173.
- Proxy: `/api` → `http://127.0.0.1:8000`, `changeOrigin: false`, `ws: true`.

---

## Diagram zależności (uproszczony)

```
main.py
  ├── config.py
  ├── models.py
  ├── data/loader.py (load_data, clean_data, append_review)
  ├── analysis/sentiment.py (perform_eda, get_top_words, get_average_polarity, analyze_batch_async, analyze_sentiment_async, classify_sentiment)
  │     ├── analysis/preprocessing.py (preprocess_text)
  │     └── analysis/ollama_client.py (analyze_sentiment, health_check)
  │           ├── config (Ollama, retry)
  │           └── utils/cache.py (sentiment_cache)
  ├── reports/pdf_report.py (build_report_pdf)
  └── utils/cache.py
```

Frontend zależy wyłącznie od endpointów REST opisanych w [API.md](API.md).
