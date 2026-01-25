# System Analizy Sentymentu Opinii Klientów

System do automatycznej analizy sentymentu opinii klientów z klasyfikacją pozytywnych/negatywnych, analizą polaryzacji emocjonalnej oraz identyfikacją najczęściej występujących słów.

## 🏗️ Architektura

- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: React + Vite + TailwindCSS
- **Analiza**: Pandas, TextBlob, NLTK
- **Wizualizacja**: Chart.js

## 📋 Wymagania Systemowe

- Python 3.10 lub wyższy
- Node.js 18+ i npm/yarn
- Git

## 🚀 Instalacja i Uruchomienie

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Pobranie danych (jeśli potrzebne)
python scripts/download_data.py

# Uruchomienie serwera
uvicorn app.main:app --reload --port 8000
```

**Windows (PowerShell):**
```powershell
cd backend
.\start_backend.ps1
```

**Windows (CMD):**
```cmd
cd backend
start_backend.bat
```

Backend będzie dostępny pod adresem: `http://localhost:8000`

**WAŻNE:** Backend musi być uruchomiony przed uruchomieniem frontendu!

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend będzie dostępny pod adresem: `http://localhost:5173`

## 📁 Struktura Projektu

```
sentiment-analysis-system/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── docs/            # Dokumentacja (raport akademicki)
└── README.md        # Ten plik
```

## 🔌 API Endpoints

- `GET /api/health` - Health check
- `GET /api/stats` - Statystyki ogólne
- `GET /api/polarity/average` - Średnia polaryzacja
- `GET /api/words/top?limit=20` - TOP słowa
- `POST /api/analyze` - Analiza pojedynczej opinii

## 📊 Funkcjonalności

- Klasyfikacja opinii jako pozytywne/negatywne
- Analiza polaryzacji emocjonalnej (-1 do 1)
- Identyfikacja najczęstszych słów
- Wizualizacja wyników w dashboardzie
- Analiza pojedynczej opinii w czasie rzeczywistym

## 🛠️ Technologie

### Backend
- FastAPI - framework REST API
- Pandas - analiza danych
- TextBlob - analiza sentymentu
- NLTK - preprocessing tekstu
- NumPy - operacje numeryczne

### Frontend
- React + Vite - framework UI
- TailwindCSS - stylowanie
- Chart.js - wizualizacje
- Axios - komunikacja z API

## 🔧 Rozwiązywanie Problemów

### Błąd: ERR_CONNECTION_REFUSED lub Network Error

Jeśli frontend wyświetla błąd połączenia z backendem:

1. **Sprawdź, czy backend jest uruchomiony:**
   ```bash
   # W terminalu backendu powinieneś widzieć:
   # INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

2. **Sprawdź, czy port 8000 jest wolny:**
   ```bash
   # Windows PowerShell
   netstat -ano | findstr :8000
   
   # Jeśli port jest zajęty, zatrzymaj proces lub zmień port w uvicorn
   ```

3. **Uruchom backend ręcznie:**
   ```bash
   cd backend
   # Aktywuj środowisko wirtualne
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   
   # Uruchom serwer
   uvicorn app.main:app --reload --port 8000
   ```

4. **Sprawdź logi backendu** - powinny pojawić się informacje o:
   - Wczytywaniu danych
   - Statusie Ollama (jeśli używany)
   - Gotowości serwera

### Backend nie uruchamia się

- Sprawdź, czy wszystkie zależności są zainstalowane: `pip install -r requirements.txt`
- Sprawdź, czy Python 3.10+ jest zainstalowany
- Sprawdź logi błędów w terminalu

### Frontend nie łączy się z backendem

- Upewnij się, że backend działa na `http://localhost:8000`
- Sprawdź konfigurację CORS w `backend/app/main.py`
- Sprawdź konfigurację API w `frontend/src/services/api.ts`

## 📝 Licencja

Projekt akademicki - Systemy Sztucznej Inteligencji

