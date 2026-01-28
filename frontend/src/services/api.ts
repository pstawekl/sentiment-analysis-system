/**
 * Serwis API do komunikacji z backendem FastAPI.
 * Używa Axios do wykonywania zapytań HTTP.
 */

import axios from 'axios';
import type {
    AveragePolarity,
    ReviewItem,
    SentimentAnalysis,
    Statistics,
    TopWords,
} from '../types';

// Konfiguracja Axios
// Używamy względnych ścieżek, aby Vite proxy mogło przechwycić zapytania
const apiClient = axios.create({
  baseURL: '', // Pusty baseURL - użyjemy względnych ścieżek, które przejdą przez Vite proxy
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Interceptor do obsługi błędów
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Przekazuj szczegóły błędu dalej
    if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
      error.message = 'Nie można połączyć się z backendem. Upewnij się, że serwer jest uruchomiony na porcie 8000.';
    } else if (error.code === 'ECONNREFUSED' || error.message?.includes('ERR_CONNECTION_REFUSED')) {
      error.message = 'Połączenie odrzucone. Backend nie jest uruchomiony lub nie nasłuchuje na porcie 8000.';
    }
    return Promise.reject(error);
  }
);

/**
 * Pobiera listę wszystkich opinii z analizą (do gridu).
 */
export const getReviews = async (): Promise<ReviewItem[]> => {
  const response = await apiClient.get<{ reviews: ReviewItem[] }>('/api/reviews');
  return response.data.reviews;
};

/**
 * Pobiera statystyki ogólne z API.
 */
export const getStatistics = async (): Promise<Statistics> => {
  const response = await apiClient.get<Statistics>('/api/stats');
  return response.data;
};

/**
 * Pobiera średnią polaryzację wszystkich opinii.
 */
export const getAveragePolarity = async (): Promise<AveragePolarity> => {
  const response = await apiClient.get<AveragePolarity>('/api/polarity/average');
  return response.data;
};

/**
 * Pobiera najczęściej występujące słowa.
 * @param limit - Liczba słów do pobrania (domyślnie 20)
 */
export const getTopWords = async (limit: number = 20): Promise<TopWords> => {
  const response = await apiClient.get<TopWords>(`/api/words/top?limit=${limit}`);
  return response.data;
};

/**
 * Analizuje pojedynczą opinię.
 * @param reviewText - Tekst opinii do analizy
 */
export const analyzeSingle = async (reviewText: string): Promise<SentimentAnalysis> => {
  const response = await apiClient.post<SentimentAnalysis>('/api/analyze', {
    review_text: reviewText,
  });
  return response.data;
};

/**
 * Health check endpoint.
 */
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await apiClient.get<{ status: string }>('/api/health');
  return response.data;
};

/**
 * Pobiera raport końcowy w formacie PDF (wszystkie opinie i analiza).
 * Zwraca Blob do pobrania pliku po stronie klienta.
 */
export const getReportPdf = async (): Promise<Blob> => {
  const response = await apiClient.get('/api/report/pdf', {
    responseType: 'blob',
    timeout: 30000,
  });
  return response.data as Blob;
};

