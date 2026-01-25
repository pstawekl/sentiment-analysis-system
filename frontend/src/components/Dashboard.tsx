/**
 * Główny komponent dashboardu - integruje wszystkie komponenty.
 */

import React, { useEffect, useState } from 'react';
import { getStatistics, getTopWords } from '../services/api';
import type { Statistics, WordCount } from '../types';
import { SentimentChart } from './SentimentChart';
import { SingleAnalysis } from './SingleAnalysis';
import { StatisticsComponent } from './Statistics';
import { WordCloud } from './WordCloud';

export const Dashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [topWords, setTopWords] = useState<WordCount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Pobierz statystyki i TOP słowa równolegle
      const [stats, words] = await Promise.all([
        getStatistics(),
        getTopWords(30),
      ]);

      setStatistics(stats);
      setTopWords(words.words);
    } catch (err: any) {
      let errorMessage = 'Błąd podczas ładowania danych';

      if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error') || err.message?.includes('ERR_CONNECTION_REFUSED')) {
        errorMessage = 'Nie można połączyć się z backendem. Upewnij się, że backend jest uruchomiony na porcie 8000.';
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      console.error('Błąd ładowania danych:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Nagłówek */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            System Analizy Sentymentu Opinii
          </h1>
          <p className="text-gray-600">
            Dashboard do analizy i wizualizacji sentymentu opinii klientów
          </p>
        </div>

        {/* Komunikat błędu */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <div className="font-semibold mb-1">Błąd:</div>
            <div>{error}</div>
            <button
              onClick={loadData}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
            >
              Spróbuj ponownie
            </button>
          </div>
        )}

        {/* Statystyki */}
        <div className="mb-8">
          <StatisticsComponent statistics={statistics} loading={loading} />
        </div>

        {/* Wykresy */}
        <div className="mb-8">
          <SentimentChart statistics={statistics} loading={loading} />
        </div>

        {/* Grid z chmurą słów i analizą pojedynczą */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Chmura słów */}
          <div>
            <WordCloud words={topWords} loading={loading} />
          </div>

          {/* Analiza pojedyncza */}
          <div>
            <SingleAnalysis />
          </div>
        </div>

        {/* Stopka */}
        <div className="text-center text-sm text-gray-500 mt-8">
          Autorzy: Jakub Stawski, Bartosz Siembor
        </div>
      </div>
    </div>
  );
};

