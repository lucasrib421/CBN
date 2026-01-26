export function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-10">
      <h1 className="text-3xl font-bold text-red-500 mb-4">
        Painel Administrativo
      </h1>
      <p className="text-gray-400">
        Área restrita. Aqui você gerenciará posts e categorias.
      </p>
      <a 
        href="/" 
        className="mt-6 inline-block text-gray-300 hover:text-white underline"
      >
        Voltar para o Site
      </a>
    </div>
  );
}