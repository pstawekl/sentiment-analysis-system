/**
 * Komponent do analizy pojedynczej opinii.
 * Zawiera formularz do wprowadzenia tekstu i wyświetla wyniki analizy.
 */

import React, { useState } from 'react';
import { analyzeSingle } from '../services/api';
import type { SentimentAnalysis } from '../types';

export const SingleAnalysis: React.FC = () => {
  const [reviewText, setReviewText] = useState('');
  const [result, setResult] = useState<SentimentAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!reviewText.trim()) {
      setError('Wprowadź tekst opinii');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const analysisResult = await analyzeSingle(reviewText);
      setResult(analysisResult);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Błąd podczas analizy opinii');
      console.error('Błąd analizy:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setReviewText('');
    setResult(null);
    setError(null);
  };

  // Przykładowe teksty do testowania
  const exampleTexts = [
    "This product is absolutely amazing! I love it so much.",
    "Terrible product! It broke after just one use. Very disappointed.",
  ];

  const handleUseExample = (text: string) => {
    setReviewText(text);
    setResult(null);
    setError(null);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Analiza Pojedynczej Opinii</h2>

      {/* Formularz */}
      <div className="space-y-4">
        <div>
          <label htmlFor="review-text" className="block text-sm font-medium text-gray-700 mb-2">
            Wprowadź tekst opinii:
          </label>
          <textarea
            id="review-text"
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            rows={6}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            placeholder="Wprowadź tekst opinii do analizy..."
          />
        </div>

        {/* Przykładowe teksty */}
        <div>
          <div className="text-sm text-gray-600 mb-2">Przykładowe teksty:</div>
          <div className="flex gap-2 flex-wrap">
            {exampleTexts.map((text, index) => (
              <button
                key={index}
                onClick={() => handleUseExample(text)}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md text-gray-700 transition-colors"
              >
                {index === 0 ? 'Pozytywna' : 'Negatywna'}
              </button>
            ))}
          </div>
        </div>

        {/* Przyciski */}
        <div className="flex gap-3">
          <button
            onClick={handleAnalyze}
            disabled={loading || !reviewText.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? 'Analizowanie...' : 'Analizuj'}
          </button>
          
          <button
            onClick={handleClear}
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Wyczyść
          </button>
        </div>

        {/* Błąd */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Wyniki */}
        {result && (
          <div className="mt-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
            <h3 className="text-xl font-bold mb-4 text-gray-800">Wyniki Analizy</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              {/* Polaryzacja */}
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-sm text-gray-600 mb-1">Polaryzacja</div>
                <div className="text-2xl font-bold text-purple-600">
                  {result.polarity.toFixed(3)}
                </div>
                <div className="text-xs text-gray-500 mt-1">(-1 do 1)</div>
              </div>

              {/* Etykieta */}
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-sm text-gray-600 mb-1">Sentyment</div>
                <div
                  className={`text-2xl font-bold ${
                    result.sentiment_label === 'positive'
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}
                >
                  {result.sentiment_label === 'positive' ? 'Pozytywny' : 'Negatywny'}
                </div>
              </div>

              {/* Liczba słów */}
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-sm text-gray-600 mb-1">Liczba słów</div>
                <div className="text-2xl font-bold text-blue-600">
                  {result.word_count}
                </div>
              </div>
            </div>

            {/* Wizualizacja polaryzacji */}
            <div className="mt-4">
              <div className="text-sm text-gray-600 mb-2">Wizualizacja polaryzacji:</div>
              <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    result.polarity >= 0
                      ? 'bg-gradient-to-r from-green-400 to-green-600'
                      : 'bg-gradient-to-r from-red-600 to-red-400'
                  }`}
                  style={{
                    width: `${Math.abs(result.polarity) * 100}%`,
                    marginLeft: result.polarity < 0 ? 'auto' : '0',
                  }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Negatywny (-1)</span>
                <span>0</span>
                <span>Pozytywny (+1)</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

