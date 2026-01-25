/**
 * Komponent wyświetlający najczęściej występujące słowa.
 * Alternatywnie może wyświetlać wizualizację chmury słów.
 */

import React from 'react';
import type { WordCount } from '../types';

interface WordCloudProps {
  words: WordCount[];
  loading: boolean;
}

export const WordCloud: React.FC<WordCloudProps> = ({ words, loading }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Najczęstsze Słowa</h2>
        <div className="animate-pulse space-y-3">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-6 bg-gray-200 rounded w-full"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!words || words.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Najczęstsze Słowa</h2>
        <p className="text-gray-600">Brak danych do wyświetlenia</p>
      </div>
    );
  }

  // Znajdź maksymalną liczbę wystąpień dla skalowania
  const maxCount = Math.max(...words.map(w => w.count));

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Najczęstsze Słowa</h2>
      
      {/* Lista słów z wagami wizualnymi */}
      <div className="space-y-3">
        {words.slice(0, 30).map((wordData, index) => {
          // Oblicz szerokość paska na podstawie względnej liczby wystąpień
          const percentage = (wordData.count / maxCount) * 100;
          
          return (
            <div key={index} className="flex items-center gap-4">
              {/* Numer pozycji */}
              <div className="w-8 text-sm font-semibold text-gray-500">
                {index + 1}.
              </div>
              
              {/* Słowo */}
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="font-medium text-gray-800 min-w-[120px]">
                    {wordData.word}
                  </span>
                  
                  {/* Pasek wizualny */}
                  <div className="flex-1 bg-gray-200 rounded-full h-6 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  
                  {/* Liczba wystąpień */}
                  <span className="text-sm font-semibold text-gray-700 min-w-[60px] text-right">
                    {wordData.count}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Informacja o liczbie słów */}
      {words.length > 30 && (
        <div className="mt-4 text-sm text-gray-500 text-center">
          Wyświetlono 30 z {words.length} słów
        </div>
      )}
    </div>
  );
};

