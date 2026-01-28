/**
 * Siatka z listą wszystkich opinii i wynikami analizy sentymentu.
 */

import React from 'react';
import type { ReviewItem } from '../types';

interface ReviewsGridProps {
  reviews: ReviewItem[];
  loading: boolean;
}

const MAX_TEXT_PREVIEW = 120;

function truncateText(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen - 3).trim() + '...';
}

export const ReviewsGrid: React.FC<ReviewsGridProps> = ({ reviews, loading }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">
          Opinie i analiza
        </h2>
        <div className="flex items-center justify-center py-12 text-gray-500">
          Ładowanie opinii...
        </div>
      </div>
    );
  }

  if (reviews.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">
          Opinie i analiza
        </h2>
        <p className="text-gray-500 py-4">
          Brak opinii. Wykonaj analizę pojedynczej opinii lub upewnij się, że
          plik dataset.csv jest załadowany.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        Opinie i analiza ({reviews.length})
      </h2>
      <div className="overflow-x-auto -mx-6 px-6">
        <table className="min-w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-2 font-semibold text-gray-700 w-12">
                Lp.
              </th>
              <th className="text-left py-3 px-2 font-semibold text-gray-700 min-w-[200px]">
                Opinia
              </th>
              <th className="text-left py-3 px-2 font-semibold text-gray-700 w-24">
                Polaryzacja
              </th>
              <th className="text-left py-3 px-2 font-semibold text-gray-700 w-28">
                Sentyment
              </th>
              <th className="text-left py-3 px-2 font-semibold text-gray-700 w-20">
                Słowa
              </th>
            </tr>
          </thead>
          <tbody className="overflow-y-auto max-h-[500px]">
            {reviews.map((r) => (
              <tr
                key={r.index}
                className="border-b border-gray-100 hover:bg-gray-50"
              >
                <td className="py-2 px-2 text-gray-600">{r.index}</td>
                <td className="py-2 px-2 text-gray-800" title={r.review_text}>
                  {truncateText(r.review_text, MAX_TEXT_PREVIEW)}
                </td>
                <td className="py-2 px-2 text-gray-700">
                  {r.polarity.toFixed(3)}
                </td>
                <td className="py-2 px-2">
                  <span
                    className={
                      r.sentiment_label === 'positive'
                        ? 'text-green-600 font-medium'
                        : 'text-red-600 font-medium'
                    }
                  >
                    {r.sentiment_label === 'positive'
                      ? 'Pozytywny'
                      : 'Negatywny'}
                  </span>
                </td>
                <td className="py-2 px-2 text-gray-600">{r.word_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
