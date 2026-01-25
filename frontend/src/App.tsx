/**
 * Główny komponent aplikacji React.
 * Integruje routing i wszystkie komponenty.
 */

import React from 'react';
import { Dashboard } from './components/Dashboard';
import './App.css';

function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;

