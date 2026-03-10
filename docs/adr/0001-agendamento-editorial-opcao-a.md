# ADR 0001: Agendamento editorial com `PUBLISHED` + filtro temporal

- Data: 2026-03-02
- Status: Aceito
- Issue relacionada: [#48](https://github.com/lucasrib421/CBN/issues/48)
- Dependência correlata: #56 (revalidation on-demand)

## Contexto

O fluxo editorial precisa suportar:

- revisão (`REVIEW`);
- publicação controlada por papel;
- agendamento sem ambiguidade operacional.

Foram avaliadas duas opções:

- Opção A: manter `status=PUBLISHED` e usar `published_at` para controlar visibilidade temporal.
- Opção B: introduzir `status=SCHEDULED` com promoção automática para `PUBLISHED`.

## Decisão

Adotar **Opção A**:

- post agendado é um post `PUBLISHED` com `published_at` no futuro;
- visibilidade pública considera somente `PUBLISHED` com `published_at <= now()` (ou `null` para legado);
- quando o usuário publica sem informar `published_at`, o backend define `published_at=now()`.

## Consequências

### Positivas

- evita infraestrutura assíncrona adicional (scheduler/worker) neste momento;
- reduz superfície de falha operacional;
- mantém modelo de dados enxuto.

### Negativas

- exige disciplina na consulta pública para não expor conteúdo antes da hora;
- sem `SCHEDULED`, o estado "agendado" é implícito em (`status`, `published_at`).

## Integração com cache/revalidation

- O backend já invalida cache de endpoints públicos via sinais em mudanças de `Post`.
- A integração com revalidation on-demand do frontend segue dependente da issue #56.
- Até #56, a consistência fica garantida por invalidação no backend + TTL.
