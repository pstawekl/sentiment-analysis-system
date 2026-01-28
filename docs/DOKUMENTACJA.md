# Dokumentacja systemu analizy sentymentu opinii klientów

## Spis treści

1. [Wprowadzenie](#wprowadzenie)
2. [Wymagania systemowe](#wymagania-systemowe)
3. [Instalacja i uruchomienie](#instalacja-i-uruchomienie)
4. [Architektura](#architektura)
5. [Funkcjonalności](#funkcjonalności)
6. [Źródła danych](#źródła-danych)
7. [Konfiguracja](#konfiguracja)
8. [Rozwiązywanie problemów](#rozwiązywanie-problemów)
9. [Referencje](#referencje)

---

## Wprowadzenie

**System Analizy Sentymentu Opinii Klientów** to aplikacja webowa służąca do automatycznej analizy sentymentu opinii klientów. System:

- Klasyfikuje opinie jako **pozytywne** lub **negatywne**
- Oblicza **polaryzację emocjonalną** w zakresie od -1 (bardzo negatywny) do 1 (bardzo pozytywny)
- Identyfikuje **najczęściej występujące słowa** w opiniach
- Umożliwia **analizę pojedynczej opinii** w czasie rzeczywistym
- Generuje **raport PDF** z podsumowaniem i listą opinii

### Technologie

| Warstwa   | Technologie |
|----------|-------------|
| Backend  | FastAPI, Python 3.10+, Pandas, TextBlob, NLTK, Ollama (LLM), ReportLab |
| Frontend | React 18, Vite, TypeScript, TailwindCSS, Chart.js, Axios |
| Analiza  | Ollama (model LLM) z fallbackiem TextBlob, NLTK (preprocessing) |

---

## Wymagania systemowe

- **Python** 3.10 lub wyższy
- **Node.js** 18+ oraz npm
- **Ollama** (opcjonalnie) – do analizy sentymentu przez model LLM; bez Ollama używany jest TextBlob
- **Git**

---

## Instalacja i uruchomienie

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

**Pobranie danych (jeśli brak pliku `backend/data/dataset.csv`):**

```bash
python scripts/download_data.py
```

**Uruchomienie serwera:**

```bash
uvicorn app.main:app --reload --port 8000
```

**Windows (skróty):**

- PowerShell: `.\start_backend.ps1`
- CMD: `start_backend.bat`

Backend jest dostępny pod: **http://localhost:8000**

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend jest dostępny pod: **http://localhost:5173**

**Uwaga:** Backend musi być uruchomiony przed frontendem. Vite przekierowuje zapytania `/api/*` na `http://127.0.0.1:8000` (proxy).

### 3. Ollama (opcjonalnie)

Aby używać analizy sentymentu przez model LLM:

1. Zainstaluj [Ollama](https://ollama.ai/)
2. Uruchom Ollama i pobierz model (np. domyślny używany w konfiguracji)
3. Backend przy starcie sprawdzi dostępność Ollama; jeśli nie działa, używany jest TextBlob

---

## Architektura

### Struktura projektu

```
sentiment-analysis-system/
├── backend/                 # API i logika analizy
│   ├── app/
│   │   ├── main.py          # Aplikacja FastAPI, endpointy
│   │   ├── config.py        # Konfiguracja (Ollama, cache, retry)
│   │   ├── models.py        # Modele Pydantic (request/response)
│   │   ├── analysis/        # Analiza sentymentu
│   │   │   ├── sentiment.py      # EDA, klasyfikacja, batch
│   │   │   ├── ollama_client.py  # Klient Ollama, prompt, parsowanie JSON
│   │   │   └── preprocessing.py  # NLTK: tokenizacja, stopwords
│   │   ├── data/
│   │   │   └── loader.py    # Wczytywanie/czyszczenie CSV, append_review
│   │   ├── reports/
│   │   │   └── pdf_report.py     # Generowanie raportu PDF (ReportLab)
│   │   └── utils/
│   │       └── cache.py    # Cache wyników sentymentu (LRU, TTL)
│   ├── data/
│   │   └── dataset.csv     # Dataset opinii
│   ├── scripts/
│   │   └── download_data.py      # Generowanie przykładowego datasetu
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/     # Dashboard, Statistics, SentimentChart, SingleAnalysis, ReviewsGrid, WordCloud
│   │   ├── services/
│   │   │   └── api.ts      # Wywołania API (Axios)
│   │   └── types/
│   │       └── index.ts    # Typy TypeScript
│   ├── vite.config.ts      # Proxy /api -> backend:8000
│   └── package.json
├── docs/                   # Dokumentacja
└── README.md
```

### Przepływ danych

1. **Start backendu:** wczytanie `dataset.csv` → czyszczenie → analiza sentymentu (Ollama/TextBlob) → EDA → cache w pamięci.
2. **Frontend:** pobiera statystyki, średnią polaryzację, TOP słowa, listę opinii przez REST API.
3. **Analiza pojedyncza:** użytkownik wpisuje tekst → `POST /api/analyze` → wynik zapisywany do `dataset.csv`, cache i statystyki odświeżane.
4. **Raport PDF:** `GET /api/report/pdf` → generowanie PDF z podsumowaniem i tabelą opinii.

Szczegóły API: [docs/API.md](API.md).  
Opis modułów backendu: [docs/ARCHITEKTURA.md](ARCHITEKTURA.md).

---

## Funkcjonalności

### Dashboard (frontend)

- **Statystyki ogólne:** liczba opinii, pozytywne/negatywne (liczba i %), średnia polaryzacja, średnia długość opinii i liczba słów.
- **Wizualizacja sentymentu:** wykres słupkowy i kołowy (Chart.js) – rozkład pozytywnych vs negatywnych.
- **Analiza pojedynczej opinii:** pole tekstowe, przycisk „Analizuj”, wyświetlanie polaryzacji, etykiety i liczby słów; po analizie dane odświeżane (statystyki, wykresy, grid).
- **Siatka opinii:** tabela wszystkich opinii z fragmentem tekstu, polaryzacją, etykietą sentymentu i liczbą słów.
- **Pobierz raport PDF:** przycisk generuje i pobiera plik PDF z podsumowaniem i listą opinii.

### Backend (API)

- Health check: `/api/health`, `/api/health/ollama`
- Statystyki: `/api/stats`
- Średnia polaryzacja: `/api/polarity/average`
- TOP słowa: `/api/words/top?limit=20`
- Lista opinii: `/api/reviews`
- Analiza pojedynczej opinii: `POST /api/analyze`
- Raport PDF: `GET /api/report/pdf`
- Przeładowanie danych (dev): `POST /api/reload`

Szczegóły request/response w [API.md](API.md).

---

## Źródła danych

- **Plik:** `backend/data/dataset.csv`  
  Kolumny: `review_id`, `review_text`, `rating`, `sentiment`.

- **Generowanie danych:**  
  `python backend/scripts/download_data.py` – tworzy przykładowy zbiór 200 opinii (mieszanka pozytywnych i negatywnych).

- **Dodawanie opinii:**  
  Analiza pojedynczej opinii (`POST /api/analyze`) dopisuje opinię do `dataset.csv` i odświeża cache.

---

## Konfiguracja

Konfiguracja backendu w `backend/app/config.py` oraz zmienne środowiskowe:

| Zmienna                  | Opis                          | Domyślnie              |
|--------------------------|-------------------------------|------------------------|
| `OLLAMA_BASE_URL`        | Adres serwera Ollama          | `http://localhost:11434` |
| `OLLAMA_MODEL`           | Nazwa modelu Ollama           | `gpt-oss:120b-cloud`   |
| `OLLAMA_TIMEOUT`         | Timeout zapytań (s)           | `30`                   |
| `USE_OLLAMA`             | Czy używać Ollama             | `true`                 |
| `OLLAMA_MAX_RETRIES`     | Liczba ponownych prób         | `3`                    |
| `OLLAMA_RETRY_DELAY`     | Opóźnienie między próbami (s) | `1.0`                  |
| `CACHE_TTL`              | Czas życia cache (s)          | `3600`                 |
| `CACHE_MAX_SIZE`         | Maks. liczba wpisów cache     | `10000`                |
| `BATCH_CONCURRENT_LIMIT` | Równoległe zapytania batch    | `5`                    |
| `LOG_LEVEL`              | Poziom logowania              | `INFO`                 |

Frontend łączy się z API przez proxy Vite (`/api` → `http://127.0.0.1:8000`), bez dodatkowej konfiguracji przy lokalnym uruchomieniu.

---

## Rozwiązywanie problemów

### Błąd połączenia z backendem (ERR_CONNECTION_REFUSED, Network Error)

1. Upewnij się, że backend działa: w terminalu powinna być informacja typu `Uvicorn running on http://0.0.0.0:8000`.
2. Sprawdź, czy port 8000 jest wolny (np. `netstat -ano | findstr :8000` w Windows).
3. Uruchom backend ręcznie: `cd backend`, aktywuj venv, `uvicorn app.main:app --reload --port 8000`.

### Backend nie uruchamia się

- Zainstaluj zależności: `pip install -r requirements.txt`
- Sprawdź wersję Pythona: `python --version` (wymagane 3.10+)
- Sprawdź logi w terminalu (błędy importu, brak pliku `dataset.csv` itd.)

### Brak danych / 503 przy `/api/stats` lub innych endpointach

- Uruchom generowanie danych: `python backend/scripts/download_data.py`
- Sprawdź, czy `backend/data/dataset.csv` istnieje i ma kolumnę `review_text`.

### Ollama niedostępny

- Przy starcie backend wyświetli komunikat, że używany jest TextBlob.
- Aby używać Ollama: zainstaluj i uruchom Ollama, upewnij się, że model z `OLLAMA_MODEL` jest dostępny.

### Błędy przy pobieraniu raportu PDF

- Sprawdź, czy backend ma załadowane dane (np. `/api/stats` zwraca 200).
- Zwiększ timeout w frontendzie (w `api.ts` dla `getReportPdf` jest 30000 ms).

---

## Referencje

- [README projektu](../README.md) – szybki start i podstawowe informacje
- [API – referencja endpointów](API.md)
- [Architektura i moduły](ARCHITEKTURA.md)

---

*Projekt akademicki – Systemy Sztucznej Inteligencji. Autorzy: Jakub Stawski, Bartosz Siembor.*
