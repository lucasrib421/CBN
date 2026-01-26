import { useEffect, useState } from 'react';
import { api } from '../../services/api'; // <--- Importamos nossa configuração

export function Home() {
  const [status, setStatus] = useState('Carregando...');

  useEffect(() => {
    // Teste simples para ver se a API responde
    // Vamos tentar bater na raiz da API ou em algum endpoint que você já tenha
    api.get('') 
      .then(() => setStatus('Online e Conectado! 🟢'))
      .catch((error) => {
        console.error(error);
        setStatus('Erro de Conexão 🔴 (Verifique o console)');
      });
  }, []);

  return (
    <div className="min-h-screen bg-blue-50 flex flex-col items-center justify-center gap-4">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-blue-900 mb-4">
          Portal CBN
        </h1>
        
        {/* Mostra o status da conexão */}
        <div className="p-4 bg-white rounded shadow-md">
          <p className="text-gray-600 font-semibold">Status da API:</p>
          <p className="text-xl">{status}</p>
        </div>

        <a 
          href="/admin" 
          className="mt-6 inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Ir para o Painel Admin
        </a>
      </div>
    </div>
  );
}