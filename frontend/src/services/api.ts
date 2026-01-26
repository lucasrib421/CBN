import axios from 'axios';

// Cria uma instância do Axios com as configurações padrão
export const api = axios.create({
  // O Vite substitui isso automaticamente pela URL definida no .env (local ou prod)
  baseURL: import.meta.env.VITE_API_URL, 
  timeout: 10000, // Tempo limite de 10 segundos para não travar a tela se a net cair
  headers: {
    'Content-Type': 'application/json',
  }
});

/**
 * DICA DE OURO PARA DJANGO:
 * O Django, por padrão, exige que as URLs terminem com barra '/'.
 * Ex: /api/posts/ funciona. /api/posts dá erro ou redirect.
 * * Se quiser garantir que nunca vai esquecer, podemos adicionar um interceptador aqui no futuro.
 * Por enquanto, lembre-se de sempre colocar a barra final nas suas chamadas.
 */