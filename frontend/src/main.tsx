import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom'; // Precisamos disto para as rotas!
import { AuthProvider } from 'react-oidc-context'; // Precisamos disto para o Login!
import App from './App.tsx';
import './index.css';

// Configuração do Keycloak
const oidcConfig = {
  authority: `${import.meta.env.VITE_KEYCLOAK_URL}/realms/${import.meta.env.VITE_KEYCLOAK_REALM}`,
  client_id: import.meta.env.VITE_KEYCLOAK_CLIENT_ID,
  redirect_uri: window.location.origin + '/admin', // Volta para o admin após logar
  onSigninCallback: () => {
    // Limpa os parâmetros feios da URL (code=...) após o login
    window.history.replaceState({}, document.title, window.location.pathname);
  }
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* 1. O AuthProvider envolve tudo para dar acesso ao usuário */}
    <AuthProvider {...oidcConfig}>
      {/* 2. O BrowserRouter fica dentro, para gerenciar as páginas */}
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>,
);