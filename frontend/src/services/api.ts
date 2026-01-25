/**
 * Serwis API do komunikacji z backendem FastAPI.
 * Używa Axios do wykonywania zapytań HTTP.
 */

import axios from 'axios';
import type {
  Statistics,
  TopWords,
  SentimentAnalysis,
  AveragePolarity,
} from '../types';

// Konfiguracja Axios
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

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

