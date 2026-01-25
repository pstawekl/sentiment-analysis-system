/**
 * Komponent wykresów do wizualizacji sentymentu.
 * Używa Chart.js do wyświetlania wykresów słupkowego i kołowego.
 */

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import type { Statistics } from '../types';

// Rejestracja komponentów Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface SentimentChartProps {
  statistics: Statistics | null;
  loading: boolean;
}

export const SentimentChart: React.FC<SentimentChartProps> = ({ statistics, loading }) => {
  if (loading || !statistics) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Wizualizacja Sentymentu</h2>
        <div className="animate-pulse h-64 bg-gray-200 rounded"></div>
      </div>
    );
  }

  // Dane dla wykresu słupkowego
  const barData = {
    labels: ['Pozytywne', 'Negatywne'],
    datasets: [
      {
        label: 'Liczba opinii',
        data: [statistics.positive_count, statistics.negative_count],
        backgroundColor: ['#10b981', '#ef4444'],
        borderColor: ['#059669', '#dc2626'],
        borderWidth: 2,
      },
    ],
  };

  // Dane dla wykresu kołowego
  const doughnutData = {
    labels: ['Pozytywne', 'Negatywne'],
    datasets: [
      {
        data: [statistics.positive_count, statistics.negative_count],
        backgroundColor: ['#10b981', '#ef4444'],
        borderColor: ['#ffffff', '#ffffff'],
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: false,
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Wizualizacja Sentymentu</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Wykres słupkowy */}
        <div>
          <h3 className="text-lg font-semibold mb-4 text-gray-700">Wykres Słupkowy</h3>
          <div className="h-64">
            <Bar data={barData} options={chartOptions} />
          </div>
        </div>

        {/* Wykres kołowy */}
        <div>
          <h3 className="text-lg font-semibold mb-4 text-gray-700">Rozkład Procentowy</h3>
          <div className="h-64">
            <Doughnut data={doughnutData} options={chartOptions} />
          </div>
        </div>
      </div>
    </div>
  );
};

