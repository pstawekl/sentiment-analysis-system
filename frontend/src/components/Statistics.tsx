/**
 * Komponent wyświetlający statystyki ogólne dotyczące opinii.
 */

import React from 'react';
import type { Statistics } from '../types';

interface StatisticsProps {
  statistics: Statistics | null;
  loading: boolean;
}

export const StatisticsComponent: React.FC<StatisticsProps> = ({ statistics, loading }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Statystyki Ogólne</h2>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (!statistics) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Statystyki Ogólne</h2>
        <p className="text-gray-600">Brak danych do wyświetlenia</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Statystyki Ogólne</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Całkowita liczba opinii */}
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div className="text-sm text-gray-600 mb-1">Całkowita liczba opinii</div>
          <div className="text-3xl font-bold text-blue-600">{statistics.total_reviews}</div>
        </div>

        {/* Pozytywne */}
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <div className="text-sm text-gray-600 mb-1">Pozytywne</div>
          <div className="text-3xl font-bold text-green-600">{statistics.positive_count}</div>
          <div className="text-sm text-gray-500 mt-1">
            {statistics.positive_percentage.toFixed(1)}%
          </div>
        </div>

        {/* Negatywne */}
        <div className="bg-red-50 rounded-lg p-4 border border-red-200">
          <div className="text-sm text-gray-600 mb-1">Negatywne</div>
          <div className="text-3xl font-bold text-red-600">{statistics.negative_count}</div>
          <div className="text-sm text-gray-500 mt-1">
            {statistics.negative_percentage.toFixed(1)}%
          </div>
        </div>

        {/* Średnia polaryzacja */}
        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
          <div className="text-sm text-gray-600 mb-1">Średnia polaryzacja</div>
          <div className="text-3xl font-bold text-purple-600">
            {statistics.average_polarity.toFixed(3)}
          </div>
        </div>
      </div>

      {/* Dodatkowe statystyki */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Średnia długość opinii</div>
          <div className="text-xl font-semibold text-gray-800">
            {statistics.average_review_length.toFixed(0)} znaków
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Średnia liczba słów</div>
          <div className="text-xl font-semibold text-gray-800">
            {statistics.average_word_count.toFixed(1)} słów
          </div>
        </div>
      </div>
    </div>
  );
};

