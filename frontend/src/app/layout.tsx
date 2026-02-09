import type { Metadata } from 'next';
import './globals.css';
import Header from '@/components/Header';

export const metadata: Metadata = {
  title: {
    default: 'CBN - Corrupção Brasileira News',
    template: '%s | CBN',
  },
  description: 'Portal jornalístico de notícias sobre corrupção no Brasil.',
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    siteName: 'CBN - Corrupção Brasileira News',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        <Header />
        <main className="max-w-7xl mx-auto px-4 py-8">
          {children}
        </main>
        <footer className="bg-black text-gray-400 text-center py-6 text-sm mt-12">
          <p>&copy; {new Date().getFullYear()} CBN - Corrupção Brasileira News. Todos os direitos reservados.</p>
        </footer>
      </body>
    </html>
  );
}
