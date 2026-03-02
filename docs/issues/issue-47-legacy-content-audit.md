# Issue #47 - Estratégia para Conteúdo Legado

## Objetivo
Garantir compatibilidade de conteúdo existente após ativação da sanitização obrigatória no backend.

## Riscos principais
- HTML legado contendo tags fora da whitelist ser reduzido/alterado após persistência.
- Links com protocolos não permitidos perderem atributos válidos.
- Diferenças de formatação em conteúdo histórico após nova política de sanitização.

## Estratégia recomendada
1. Auditar base atual de `Post.content` antes de rollout completo.
2. Classificar ocorrências por tipo:
   - tags não permitidas,
   - atributos não permitidos,
   - protocolos inválidos em `href`/`src`.
3. Rodar sanitização em modo dry-run para medir impacto de diff entre HTML original e sanitizado.
4. Definir ações por severidade:
   - baixo impacto: sanitização automática no próximo ciclo de edição,
   - alto impacto: revisão editorial assistida antes de republicação.
5. Monitorar métricas de erro/feedback editorial no pós-rollout.

## Política aplicada nesta entrega
- Sanitização centralizada e obrigatória antes de persistência.
- `reading_time` calculado automaticamente a partir de texto limpo.
- Escrita de `reading_time` bloqueada na API de admin.

## Observação de escopo
- Inserção de imagens no editor permanece fora de escopo nesta entrega (dependência parcial da #50).
