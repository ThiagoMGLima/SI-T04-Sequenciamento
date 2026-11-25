# Tarefa 4: Sequenciamento de socorro (VictSim, cenário 75x75_410v)

Atribuição dos agrupamentos da Tarefa 3 aos 5 socorristas e sequenciamento do socorro de cada um por
algoritmo genético, dentro de agentes do VictSim3.

## Como rodar

Projeto `uv` (Python 3.14). Em ordem:

```
uv run pytest                          # testes (operadores, custo, parcelas, atribuição, agentes)
uv run python src/calibrar.py          # calibração do AG -> resultados/calibracao.json
uv run python sma/main_t4.py           # 5 socorristas no VictSim3 -> clusters/cluster_*.txt, resultados/sequenciamento.json
uv run python src/plotar_victsim.py    # sequências com o plot do professor -> resultados/sequencias_victsim.png
uv run python src/analises.py          # análises -> resultados/analises.json
uv run python src/figuras.py           # figuras do relatório
uv run python src/gerar_relatorio.py   # entrega/: relatorio_T04.pdf, clusters/, clusters.zip, codigo_fonte_T04.zip
uv run python src/conferir_entrega.py  # confere PDF × JSON, arquivos de sequência e zips
```

`sma/main_t4.py`, `src/plotar_victsim.py` e os testes dos agentes usam o VictSim3
(https://github.com/tacla/VictSim3, commit `803a01e`) em `vendor/victsim3/`, com a mesma estrutura de
pastas do repositório e sem nenhuma modificação. Ele não vai no zip de entrega (o enunciado pede para
não enviar o simulador): para rodar a partir do zip, copie para `vendor/victsim3/` as pastas `vs/`,
`datasets/env/75x75_410v/`, `datasets/vict/410v/` e `data_vis_and_stats/plot_clusters_and_sequencing.py`.

## Entradas

- `dados/t3/`: saídas da Tarefa 3, sem modificação: `map_preenchido.csv` (o `map.csv` com tri e sobr
  preditos pelos modelos da T1 e da T2), `cluster_1.txt` a `cluster_7.txt`, `ruido.txt` e
  `agrupamento_t3.json` (plano de atribuição da T3, usado só na comparação).
- `map.csv`: o mapa do enunciado (igual ao da T3).

## Organização

- `src/`: AG (`ag.py`), custo (`custo.py`), heurísticas (`heuristicas.py`), parcelas, atribuição,
  sequenciamento, calibração, análises, figuras e relatório.
- `sma/`: os agentes socorristas (`socorrista.py`, que estende a `AbstAgent` do VictSim3), o
  `main_t4.py` e os configs `cfg/soc_1.txt` a `soc_5.txt`.
- `tests/`: testes (`uv run pytest`).
- `GLOSSARY.md`, `docs/adr/`: vocabulário e decisões de arquitetura; `observacoes.md`: todas as decisões
  e números (fora do zip).

## Saídas

- `clusters/cluster_k.txt`: um id de vítima por linha, na ordem de socorro; k = número da sequência
  (linha "Seq." da Tabela 1 do relatório). Cada cluster da T3 foi dividido em parcela de adultos e
  parcela geral (crianças + vítimas-ruído), por isso são 14 arquivos (`docs/adr/0001`).
- `resultados/`: JSON com todos os números e as figuras do relatório.
- `entrega/`: o que vai para o Moodle.
