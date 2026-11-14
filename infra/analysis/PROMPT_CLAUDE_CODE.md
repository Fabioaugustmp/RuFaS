Continue a análise do repositório RuFaS (pasta C:\Workspace\RuFaS) para integrar um modelo próprio de ML/IA.

1. Leia `infra/analysis/ANALISE_MODELOS.md`. É um resumo de uma análise feita no clone público. Confirme cada ponto contra o código local.
2. Use o servidor MCP do GitNexus (`gitnexus-mcp`, porta 3000) para:
   - `callers`/`impact` de `calculate_heifer_methane`, `calculate_cow_methane` e `calculate_nutrition_requirements`;
   - listar os processos do laço diário que passam por `_execute_daily_animal_operations`.
   Se o MCP não responder, diga qual erro apareceu e siga só com a leitura do código.
3. Rode `python infra/analysis/callgraph.py .` e compare com o resumo.
4. Confirme `methane_model` em `input/data/animal` para vacas lactantes e secas.
5. Não altere código do RuFaS. Entregue uma lista de pontos de integração, do mais simples ao mais impactante, com arquivo e linha, e os riscos de reprodutibilidade e latência.
