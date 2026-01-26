import { Routes, Route } from 'react-router-dom';
import { Home } from '../pages/HomeNews/Home';
import { Dashboard } from '../pages/PainelControle/Dashboard';

export function AppRoutes() {
  return (
    <Routes>
      {/* Rota Raiz (Site Público) */}
      <Route path="/" element={<Home />} />
      
      {/* Rota Admin (Painel) */}
      <Route path="/admin" element={<Dashboard />} />
    </Routes>
  );
}