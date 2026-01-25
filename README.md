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

Backend będzie dostępny pod adresem: `http://localhost:8000`

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

## 📝 Licencja

Projekt akademicki - Systemy Sztucznej Inteligencji

