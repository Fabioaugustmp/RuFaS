# Onde o RuFaS chama modelos (análise para integração de modelo próprio)

Base: clone público `RuminantFarmSystems/RuFaS` (commit 99c64f7, 07/10/2026). Ainda não foi conferido contra a cópia local em `C:\Workspace\RuFaS`.

## Resumo
- Não há bibliotecas de ML/LLM, nem chamadas HTTP, no núcleo (`RUFAS/`). Dependências: numpy, pandas, scipy, SALib, numba, etc.
- Todos os "modelos" são equações empíricas ou mecanísticas (NASEM 2021, NRC 2001, IPCC 2006/2019, Mills 2003, Wood), executadas em CPU, dentro do processo, a cada dia simulado.
- Não há ponto de plug-in para modelos externos. A integração exige um novo ponto de chamada.

## Pontos de modelo e caminho até o laço diário
Caminhos obtidos por análise AST com nomes de funções (aproximação, sem resolver tipos):

| Modelo | Função que executa | Caminho até o laço diário | Frequência |
|---|---|---|---|
| Exigências NASEM/NRC (DMI, nutrientes) | `Animal.calculate_nutrition_requirements` (`animal.py:2606`) | `_execute_daily_animal_operations` → `_formulate_ration` → `HerdManager.formulate_rations` → `Pen.formulate_optimized_ration` → `Pen.set_animal_nutritional_requirements` | Na reformulação de ração (intervalo configurável) |
| Otimização de ração (scipy.minimize) | `RationOptimizer.attempt_optimization` (`ration_optimizer.py:825`) | `_execute_daily_animal_operations` → `_formulate_ration` → `HerdManager._reformulate_ration_single_pen` → `Pen._run_formulation_attempts` | Na reformulação de ração |
| Metano entérico (novilhas) | `EntericMethaneCalculator.calculate_heifer_methane` (`enteric_methane_calculator.py:44`) | `_execute_daily_animal_operations` → `HerdManager.execute_daily_routines` → `Animal.daily_routines` → `_daily_digestive_system_update` → `DigestiveSystem.process_digestion` | Diária, por grupo |
| Metano entérico (vacas, lactantes e secas) | `_calculate_lactating_cow_enteric_methane` (l.162), `_calculate_dry_cow_enteric_methane` (l.222) | igual ao anterior | Diária |
| Curva de Wood (produção diária) | `MilkProduction._update_daily_milk_production` (`milk_production.py:162`) | `_execute_daily_animal_operations` → ... → `Animal.daily_milking_update` | Diária |
| Curva de Wood (305 dias) | `MilkProduction.calculate_305_day_milk_yield` (l.331) | `_execute_ration_planning` → `HerdManager.update_herd_305_day_milk_yields` → `Animal.update_305_day_milk_yield` | Na reformulação de ração |
| Ajuste da curva de Wood | `LactationCurve._fit_wood_l_param_to_milk_yield` (`lactation_curve.py:386`, `scipy.minimize`) | `set_lactation_parameters` / `_adjust_lactation_curve_to_milk_yield` | Inicialização e ajuste |
| Estocástico | `scipy.stats.truncnorm` (`animal.py`) | — | Por animal |

Detalhes de seleção:
- O método de metano vem do JSON de configuração do animal (`AnimalConfig.methane_model`, `animal_config.py:545`). Nos exemplos de `input/data/animal`, os valores encontrados foram `"calves": "Pattanaik"` e `"heiferIs": "IPCC"` (com `heiferIIs` e `heiferIIIs` também em IPCC). Os valores para vacas não foram confirmados.
- A escolha entre NASEM e NRC é feita pelo enum `NutrientStandard` (`feed_storage_to_animal_connection.py:51`).
- `_execute_ration_planning` (`simulation_engine.py`) reformula a ração quando `current_date >= next_ration_reformulation`, e então atualiza a produção de 305 dias.

## Pontos candidatos para integrar um modelo próprio
1. **Metano entérico** (`enteric_methane_calculator.py`): ponto mais isolado. Há um `if/elif` por string em `methane_model`; basta adicionar um ramo. Chamada diária, por grupo, então é preciso cache ou agregação para não virar gargalo.
2. **Consumo de matéria seca (DMI)** (`ration_manager.py`, opção `PREDICT_DMI`): substitui a previsão NASEM/NRC. Afeta toda a ração, então é o ponto de maior impacto.
3. **Ração** (`ration_optimizer.objective` e `Pen.formulate_optimized_ration`): um modelo pode propor a ração inicial, mas a otimização scipy deve continuar garantindo as restrições.
4. **Produção de leite** (`milk_production.py`): ponto da curva de Wood.

## Riscos
- **Reprodutibilidade.** O projeto valoriza reprodutibilidade (`Strategy.md`). Modelo externo não determinístico quebra os testes e as múltiplas rodadas (`SIMULATION_MULTI_RUN`). É preciso fixar versão, semente e cache.
- **Latência.** A chamada é por animal ou grupo, por dia. Uma chamada HTTP por animal-dia pode tornar a simulação inviável. Agregar por pen ou por dia é o caminho.
- **Licença.** O `Strategy.md` não aceita dependências não open source. O modelo próprio precisa ser compatível com isso.

## O que falta confirmar (fazer no Claude Code com o GitNexus rodando)
- Rodar no MCP do GitNexus: `impact` e `callers` para `calculate_heifer_methane`, `calculate_cow_methane` e `calculate_nutrition_requirements`. Confirmar os caminhos acima com o grafo real.
- Confirmar o método de metano das vacas nos arquivos de `input/data/animal`.
- Rodar `python analysis/callgraph.py C:\Workspace\RuFaS` no repositório local e comparar com este resumo.
