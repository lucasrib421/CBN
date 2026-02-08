import { useAuth } from 'react-oidc-context';

export function Dashboard() {
  const auth = useAuth();

  // 1. Estado de Carregando (Verificando se está logado...)
  if (auth.isLoading) {
    return <div className="p-10">Carregando autenticação...</div>;
  }

  // 2. Não Logado? Mostra botão de Login
  if (!auth.isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
        <h1 className="text-2xl font-bold mb-4 text-gray-800">Acesso Restrito</h1>
        <p className="mb-6 text-gray-600">Você precisa estar logado para acessar o painel.</p>
        <button 
          type="button"
          onClick={() => auth.signinRedirect()}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
        >
          Entrar com Keycloak
        </button>
      </div>
    );
  }

  // 3. Logado? Mostra o Painel com os dados do usuário
  return (
    <div className="min-h-screen bg-gray-900 text-white p-10">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-red-500">Painel Administrativo</h1>
        <div className="flex items-center gap-4">
          <span className="text-gray-300">
            Olá, <strong>{auth.user?.profile.preferred_username}</strong>
          </span>
          <button 
            type="button"
            onClick={() => auth.signoutRedirect()}
            className="bg-red-600 px-4 py-1 rounded text-sm hover:bg-red-700"
          >
            Sair
          </button>
        </div>
      </div>
      
      <div className="mt-10 p-6 bg-gray-800 rounded-lg border border-gray-700">
        <h2 className="text-xl font-semibold mb-4">Gerenciar Notícias</h2>
        <p className="text-gray-400">Aqui virá a listagem de posts para edição.</p>
      </div>

      <a href="/" className="mt-8 inline-block text-gray-500 hover:text-white underline">
        &larr; Voltar para o Site
      </a>
    </div>
  );
}
