# Issue #47 - Spike de Editor WYSIWYG

## Contexto
A issue #47 exige um editor WYSIWYG no admin com integração via adapter, `react-hook-form`, preview fiel e segurança ponta a ponta no backend.

Dependência parcial com #50 (inserção de imagem) foi mantida fora de escopo nesta entrega.

## Alternativas avaliadas

### Novel
- Tempo para MVP: médio.
- UX pronta: boa para casos de escrita moderna.
- Integração com formulário: viável.
- Manutenibilidade/extensibilidade: boa, mas com menor maturidade ecossistêmica para customizações mais específicas de newsroom.

### TipTap
- Tempo para MVP: baixo.
- UX pronta: boa e previsível.
- Integração com formulário: direta, especialmente com adapter dedicado e `Controller`.
- Manutenibilidade/extensibilidade: alta, com extensões consolidadas e API estável para evoluções futuras.

### Plate
- Tempo para MVP: médio/alto.
- UX pronta: robusta, porém com maior overhead inicial.
- Integração com formulário: viável.
- Manutenibilidade/extensibilidade: alta, porém com curva de adoção e setup maiores para o contexto atual.

## Decisão
`TipTap` foi adotado por melhor equilíbrio entre:
- velocidade de entrega sem comprometer qualidade,
- API de extensão madura,
- integração simples com adapter e `react-hook-form`,
- menor custo de manutenção para o roadmap imediato.

## Implementado nesta entrega
- Adapter `PostRichTextEditor` encapsulando a biblioteca.
- Toolbar com blocos mínimos do escopo atual:
  - parágrafo,
  - `h2`, `h3`,
  - negrito, itálico,
  - lista ordenada e não ordenada,
  - citação,
  - link,
  - separador.
- Controle de colagem com sanitização no cliente para manter contrato de tags permitidas.
- Preview fiel do HTML sanitizado durante a edição.

## Fora de escopo nesta entrega
- Inserção de imagem com legenda/alt dentro do editor (dependência parcial da #50).
