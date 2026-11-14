# Infraestrutura local de apoio (RuFaS / TCC)

Serviços:
- **GitNexus** (`gitnexus-index`, `gitnexus-mcp`, `gitnexus-web`): grafo de código do RuFaS, com consultas de callers/callees e impacto de mudanças. Licença PolyForm Noncommercial.
- **ai-memory** (perfil `memory`, opcional): memória persistente entre sessões de agentes. Licença MIT.

Não incluído: **CodeGraph** (`@colbymchenry/codegraph`, MIT). Ele roda localmente como MCP via stdio, sem Docker, e é uma alternativa mais leve. Instale no próprio Windows se quiser comparar.

## Passos
```bash
cp .env.example .env          # preencha os tokens
docker compose --profile index run --rm gitnexus-index
docker compose up -d gitnexus-mcp gitnexus-web
```

Conectar ao Claude Code:
```bash
claude mcp add --transport http gitnexus http://127.0.0.1:3000/mcp \
  --header "Authorization: Bearer <GITNEXUS_MCP_AUTH_TOKEN>"
```

Já registrado no escopo de usuário (`~/.claude.json`, chave `mcpServers.gitnexus`), válido para todas as sessões e worktrees. Reinicie a sessão do Claude Code para carregar as ferramentas.

## Como o índice é encontrado (validado com Docker em 09/10/2026)
- O `gitnexus-index` monta o repositório em `/src` com leitura e escrita: o `analyze` grava `/src/.gitnexus/` (ignorado pelo git via `.git/info/exclude`).
- O registro global fica no volume (`/data/.gitnexus/registry.json`) e aponta para `/src/.gitnexus`. Por isso `gitnexus-mcp` e `gitnexus-web` também montam o repositório em `/src` (somente leitura). Sem esse mount, o servidor não acha o índice e esvazia o registro ao iniciar (`No indexed repositories`).
- `.claude/worktrees/` não entra no índice (também está em `.git/info/exclude`).
- Reindexar após mudanças no código: `docker compose --profile index run --rm gitnexus-index analyze --skip-agents-md --skip-skills --force --pdg /src` e depois `docker compose restart gitnexus-mcp gitnexus-web`.
- Conferir: `docker compose exec gitnexus-mcp cat /data/.gitnexus/registry.json`.

## Limitações conhecidas (Python)
- Chamadas por atributo (`self.herd_manager.x()`) e por variável de laço (`for animal in d.values(): animal.x()`) não viram arestas; `trace`/`impact` a partir do `SimulationEngine` subestimam. Confirme esses trechos lendo o código.
- O `analyze` trunca fluxos (dos 996 pontos de entrada candidatos, só 200 entraram no ranking); um fluxo ausente não significa que o caminho não exista.
