/**
 * Główny komponent dashboardu - integruje wszystkie komponenty.
 */

import React, { useEffect, useState } from 'react';
import { getReportPdf, getReviews, getStatistics, getTopWords } from '../services/api';
import type { ReviewItem, Statistics, WordCount } from '../types';
import { ReviewsGrid } from './ReviewsGrid';
import { SentimentChart } from './SentimentChart';
import { SingleAnalysis } from './SingleAnalysis';
import { StatisticsComponent } from './Statistics';

export const Dashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [topWords, setTopWords] = useState<WordCount[]>([]);
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reportPdfLoading, setReportPdfLoading] = useState(false);
  const [reportPdfError, setReportPdfError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [stats, words, reviewsList] = await Promise.all([
        getStatistics(),
        getTopWords(30),
        getReviews(),
      ]);

      setStatistics(stats);
      setTopWords(words.words);
      setReviews(reviewsList);
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

  const handleDownloadReportPdf = async () => {
    setReportPdfLoading(true);
    setReportPdfError(null);
    try {
      const blob = await getReportPdf();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'raport_sentyment.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: unknown) {
      let errorMessage = 'Błąd podczas pobierania raportu PDF.';
      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { data?: unknown; status?: number } };
        if (axErr.response?.data instanceof Blob) {
          try {
            const text = await axErr.response.data.text();
            const json = JSON.parse(text) as { detail?: string };
            if (json.detail) errorMessage = json.detail;
          } catch {
            // leave default message
          }
        } else if (axErr.response?.data && typeof axErr.response.data === 'object' && 'detail' in axErr.response.data) {
          errorMessage = (axErr.response.data as { detail: string }).detail;
        }
      } else if (err instanceof Error && err.message) {
        errorMessage = err.message;
      }
      setReportPdfError(errorMessage);
      console.error('Błąd pobierania raportu PDF:', err);
    } finally {
      setReportPdfLoading(false);
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
          <p className="text-gray-600 mb-4">
            Dashboard do analizy i wizualizacji sentymentu opinii klientów
          </p>
          <button
            type="button"
            onClick={handleDownloadReportPdf}
            disabled={reportPdfLoading || loading}
            className="px-5 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {reportPdfLoading ? 'Generowanie raportu...' : 'Pobierz raport PDF'}
          </button>
          {reportPdfError && (
            <div className="mt-3 text-sm text-red-600">{reportPdfError}</div>
          )}
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

        {/* Analiza pojedyncza */}
        <div className="grid grid-cols-1 gap-8 mb-8">
          <SingleAnalysis onAnalysisSuccess={loadData} />
        </div>

        {/* Grid z opiniami i analizą */}
        <div className="mb-8">
          <ReviewsGrid reviews={reviews} loading={loading} />
        </div>



        {/* Stopka */}
        <div className="text-center text-sm text-gray-500 mt-8">
          Autorzy: Jakub Stawski, Bartosz Siembor
        </div>
      </div>
    </div>
  );
};

