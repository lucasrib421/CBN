import { NextRequest, NextResponse } from 'next/server';
import { revalidateTag } from 'next/cache';

export async function POST(request: NextRequest) {
  // 1. Proteção contra falha humana: E se esquecermos de colocar a senha no .env?
  if (!process.env.REVALIDATION_SECRET) {
    console.error('CRÍTICO: REVALIDATION_SECRET não configurado no .env do frontend.');
    return NextResponse.json({ message: 'Erro de configuração do servidor' }, { status: 500 });
  }

  // 2. Pegamos a senha enviada pelo Django e validamos
  const secret = request.headers.get('x-reval-secret');
  if (secret !== process.env.REVALIDATION_SECRET) {
    console.warn('Tentativa de revalidação com token inválido bloqueada.');
    return NextResponse.json({ message: 'Token inválido' }, { status: 401 });
  }

  try {
    const body = await request.json();
    
    // 3. Agora esperamos um ARRAY de tags. Ex: { "tags": ["post-123", "home", "cat-politica"] }
    const tagsToRevalidate = body.tags;

    // Validamos se realmente chegou um array e se ele não está vazio
    if (!tagsToRevalidate || !Array.isArray(tagsToRevalidate) || tagsToRevalidate.length === 0) {
      return NextResponse.json({ message: 'Array de "tags" não fornecido ou vazio' }, { status: 400 });
    }

    // 4. A mágica acontece em loop: O Next.js limpa o cache de TODAS as tags solicitadas!
    tagsToRevalidate.forEach((tag) => {
      revalidateTag(tag, undefined as any);
      console.log(`[Cache] Tag revalidada: ${tag}`);
    });

    return NextResponse.json({ revalidated: true, tags: tagsToRevalidate, now: Date.now() });
    
  } catch (err) {
    // 5. Se algo explodir, registramos o erro no console do servidor para debug
    console.error('[Cache] Erro no webhook de revalidação:', err);
    return NextResponse.json({ message: 'Erro ao processar a requisição' }, { status: 500 });
  }
}