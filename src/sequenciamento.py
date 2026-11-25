"""Sequenciamento de uma parcela pelo AG: várias sementes, guarda a melhor execução.
Usado pelos agentes socorristas (sma/) e pelas análises."""

import numpy as np

from ag import executar_ag
from comum import LAMBDA, SEMENTE
from custo import CustoNormalizado
from heuristicas import vizinho_mais_proximo
from parcelas import ordem_start, problema_da_parcela

N_SEMENTES = 10  # por inicialização
INICIALIZACOES = ("puro", "semeado")


def indices_start(vitimas, parcela):
    """Ordem START da T3 como permutação dos índices da parcela."""
    posicao = {i: k for k, i in enumerate(parcela.ids)}
    return np.array([posicao[i] for i in ordem_start(vitimas, parcela.ids)])


def rng_da_execucao(parcela, semente, inicializacao="puro"):
    """Gerador reprodutível e independente por parcela, inicialização e semente."""
    return np.random.default_rng([SEMENTE, parcela.cluster, 0 if parcela.tipo == "adultos" else 1,
                                  INICIALIZACOES.index(inicializacao), semente])


def sequenciar_parcela(vitimas, parcela, parametros, lam=LAMBDA,
                       inicializacoes=INICIALIZACOES, sementes=range(N_SEMENTES)):
    """Roda o AG com cada inicialização da população (pura: só permutações aleatórias; semeada: com
    o vizinho mais próximo e a ordem START) e cada semente, e devolve a melhor sequência (ids na
    ordem de socorro), as métricas dela, o histórico da melhor execução de cada inicialização e o
    resumo de todas as execuções. Ver docs/adr/0002."""
    problema = problema_da_parcela(vitimas, parcela)
    vmp = vizinho_mais_proximo(problema)
    semeaduras = {"puro": [], "semeado": [vmp, indices_start(vitimas, parcela)]}
    execucoes, resultados = [], {}
    for inicializacao in inicializacoes:
        for s in sementes:
            custo = CustoNormalizado(problema, vmp, lam)
            r = executar_ag(custo, parametros, rng_da_execucao(parcela, s, inicializacao),
                            sementes=semeaduras[inicializacao])
            distancia, latencia = problema.avaliar(r.ordem)
            execucoes.append({"inicializacao": inicializacao, "semente": s, "custo": r.custo,
                              "distancia": float(distancia), "latencia": float(latencia),
                              "geracoes": r.geracoes, "chamadas_fitness": r.chamadas_fitness})
            resultados[(inicializacao, s)] = r

    def melhor_de(execs):
        return min(execs, key=lambda e: (e["custo"], INICIALIZACOES.index(e["inicializacao"]), e["semente"]))

    melhor = melhor_de(execucoes)
    historicos = {}
    for inicializacao in inicializacoes:
        e = melhor_de([x for x in execucoes if x["inicializacao"] == inicializacao])
        r = resultados[(inicializacao, e["semente"])]
        historicos[inicializacao] = {"melhor_por_geracao": r.melhor_por_geracao,
                                     "media_por_geracao": r.media_por_geracao}
    ordem = resultados[(melhor["inicializacao"], melhor["semente"])].ordem
    return {
        "parcela": parcela.nome,
        "ids": [parcela.ids[k] for k in ordem],
        "custo": melhor["custo"],
        "distancia": melhor["distancia"],
        "latencia": melhor["latencia"],
        "inicializacao": melhor["inicializacao"],
        "semente": melhor["semente"],
        "historicos": historicos,
        "execucoes": execucoes,
    }
