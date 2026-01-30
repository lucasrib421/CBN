import { Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import { Home } from './pages/HomeNews/Home';

function App() {
  return (
    <div style={{ minHeight: '100vh', background: '#f3f4f6' }}>
      <Header />
      
      <main style={{ maxWidth: '1200px', margin: '30px auto', padding: '0 20px' }}>
        <Routes>
          {/* Rota 1: A Home Page (Raiz) */}
          <Route path="/" element={<Home />} />

          {/* Rota 2: Categorias (Política, Esportes, etc) */}
          <Route path="/:slug" element={<h2>Página de Categoria (Em construção)</h2>} />

          {/* Rota 3: Notícia Específica */}
          <Route path="/post/:slug" element={<h2>Leitura da Notícia (Em construção)</h2>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;