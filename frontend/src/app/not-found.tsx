import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-32 text-center">
      <h1 className="text-7xl font-black text-red-600 mb-4">404</h1>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Página não encontrada</h2>
      <p className="text-gray-500 mb-8 max-w-md">
        A página que você está procurando não existe ou foi removida.
      </p>
      <Link
        href="/"
        className="bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors"
      >
        Voltar para a Home
      </Link>
    </div>
  );
}
