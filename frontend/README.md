# Frontend - React + Vite Dashboard

Frontend aplikacji do analizy sentymentu opinii klientów.

## Technologie

- **React 18** - framework UI
- **TypeScript** - typowanie statyczne
- **Vite** - build tool i dev server
- **TailwindCSS** - utility-first CSS framework
- **Chart.js + react-chartjs-2** - wizualizacje danych
- **Axios** - klient HTTP do komunikacji z API

## Instalacja

```bash
npm install
```

## Uruchomienie

```bash
npm run dev
```

Aplikacja będzie dostępna pod adresem: `http://localhost:5173`

## Build

```bash
npm run build
```

## Struktura Projektu

```
src/
├── components/          # Komponenty React
│   ├── Dashboard.tsx   # Główny dashboard
│   ├── Statistics.tsx  # Statystyki ogólne
│   ├── SentimentChart.tsx  # Wykresy sentymentu
│   ├── WordCloud.tsx   # Najczęstsze słowa
│   └── SingleAnalysis.tsx  # Analiza pojedynczej opinii
├── services/           # Serwisy API
│   └── api.ts         # Klient Axios
├── types/             # Definicje typów TypeScript
│   └── index.ts
├── App.tsx           # Główny komponent
└── main.tsx          # Punkt wejścia
```

## Komponenty

### Dashboard
Główny komponent integrujący wszystkie sekcje dashboardu.

### StatisticsComponent
Wyświetla statystyki ogólne:
- Całkowita liczba opinii
- Liczba pozytywnych/negatywnych
- Średnia polaryzacja
- Statystyki długości opinii

### SentimentChart
Wizualizuje sentyment przy użyciu Chart.js:
- Wykres słupkowy (pozytywne vs negatywne)
- Wykres kołowy (rozkład procentowy)

### WordCloud
Wyświetla najczęściej występujące słowa z wizualnymi wagami.

### SingleAnalysis
Formularz do analizy pojedynczej opinii z wyświetlaniem wyników w czasie rzeczywistym.

## Konfiguracja API

Domyślny URL backendu: `http://localhost:8000`

Można zmienić w pliku `src/services/api.ts`:

```typescript
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  // ...
});
```

## Wymagania

- Node.js 18+
- npm lub yarn

