"""Calibração do AG (observacoes.md, item 13): tipo de mutação × pMUT × N em 3 parcelas de tamanhos
diferentes, com as duas inicializações da população (pura e semeada, docs/adr/0002) e 5 sementes
cada. Escolhe a combinação de menor custo médio
(média das 3 parcelas); empate (diferença < 1e-4) pelo menor número de chamadas da função de fitness.

Saída: resultados/calibracao.json (lido pelos agentes socorristas).
Uso: uv run python src/calibrar.py
"""

from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from itertools import product

import numpy as np

from ag import MUTACOES, ParametrosAG
from comum import DADOS_T3, RESULTADOS, salvar_json
from parcelas import carregar_vitimas, ler_clusters_t3, montar_parcelas
from sequenciamento import sequenciar_parcela

PARCELAS_CALIBRACAO = ("c2-adultos", "c3-geral", "c4-adultos")  # 78, 48 e 13 vítimas
P_MUTACAO = (0.005, 0.01, 0.02)
TAMANHO_POPULACAO = (50, 100, 200)
SEMENTES = range(5)
SAIDA = RESULTADOS / "calibracao.json"


def _rodar(tarefa):
    mutacao, pm, n, nome = tarefa
    vitimas = carregar_vitimas(DADOS_T3 / "map_preenchido.csv")
    parcela = {p.nome: p for p in montar_parcelas(vitimas, *ler_clusters_t3(DADOS_T3))}[nome]
    params = ParametrosAG(tamanho_populacao=n, p_mutacao=pm, mutacao=mutacao)
    r = sequenciar_parcela(vitimas, parcela, params, sementes=SEMENTES)
    custos = [e["custo"] for e in r["execucoes"]]
    return tarefa, {"custo_medio": float(np.mean(custos)), "custo_dp": float(np.std(custos)),
                    "chamadas_media": float(np.mean([e["chamadas_fitness"] for e in r["execucoes"]]))}


def main():
    combinacoes = list(product(MUTACOES, P_MUTACAO, TAMANHO_POPULACAO))
    tarefas = [(*c, nome) for c in combinacoes for nome in PARCELAS_CALIBRACAO]
    with ProcessPoolExecutor() as pool:
        resultados = dict(pool.map(_rodar, tarefas))

    linhas = []
    for mutacao, pm, n in combinacoes:
        por_parcela = {nome: resultados[(mutacao, pm, n, nome)] for nome in PARCELAS_CALIBRACAO}
        linhas.append({
            "mutacao": mutacao, "p_mutacao": pm, "tamanho_populacao": n,
            "custo_medio": float(np.mean([v["custo_medio"] for v in por_parcela.values()])),
            "chamadas_media": float(np.mean([v["chamadas_media"] for v in por_parcela.values()])),
            "por_parcela": por_parcela,
        })
    melhor_custo = min(l["custo_medio"] for l in linhas)
    escolhida = min((l for l in linhas if l["custo_medio"] - melhor_custo < 1e-4),
                    key=lambda l: l["chamadas_media"])
    parametros = ParametrosAG(tamanho_populacao=escolhida["tamanho_populacao"],
                              p_mutacao=escolhida["p_mutacao"], mutacao=escolhida["mutacao"])
    salvar_json(SAIDA, {
        "parcelas": list(PARCELAS_CALIBRACAO),
        "sementes": list(SEMENTES),
        "fixos": {"p_cruzamento": parametros.p_cruzamento, "max_geracoes": parametros.max_geracoes,
                  "estagnacao": parametros.estagnacao},
        "linhas": sorted(linhas, key=lambda l: l["custo_medio"]),
        "parametros_escolhidos": asdict(parametros),
    })
    for l in sorted(linhas, key=lambda l: l["custo_medio"])[:10]:
        print(f"{l['mutacao']:15s} pm={l['p_mutacao']:<6} N={l['tamanho_populacao']:<4} "
              f"custo={l['custo_medio']:.4f} chamadas={l['chamadas_media']:.0f} "
              + " ".join(f"{k}={v['custo_medio']:.4f}" for k, v in l["por_parcela"].items()))
    print("Escolhida:", asdict(parametros))


if __name__ == "__main__":
    main()
