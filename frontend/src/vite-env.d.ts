/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  // Aqui você adicionaria outras variáveis no futuro, se precisar
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}