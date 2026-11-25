"""Heurísticas de sequenciamento usadas como semente e como referência para o AG."""

import numpy as np


def vizinho_mais_proximo(problema):
    """Sai da base e vai sempre à vítima ainda não socorrida mais perto (empate: menor índice)."""
    livres = np.ones(problema.n, bool)
    ordem, atual = [], 0  # nó 0 = base
    for _ in range(problema.n):
        dist = np.where(livres, problema.dist[atual, 1:], np.inf)
        proxima = int(np.argmin(dist))
        ordem.append(proxima)
        livres[proxima] = False
        atual = proxima + 1
    return np.array(ordem)


def dois_opt(custo, ordem):
    """Subida de encosta com vizinhança 2-opt (inverte um trecho da sequência) sobre o mesmo custo
    do AG; para no primeiro ótimo local. Só referência nas análises."""
    melhor, valor = np.asarray(ordem).copy(), custo(ordem)
    melhorou = True
    while melhorou:
        melhorou = False
        for i in range(len(melhor) - 1):
            candidatos = []
            for j in range(i + 2, len(melhor) + 1):
                c = melhor.copy()
                c[i:j] = c[i:j][::-1]
                candidatos.append(c)
            valores = custo(np.array(candidatos))
            k = int(np.argmin(valores))
            if valores[k] < valor - 1e-12:
                melhor, valor, melhorou = candidatos[k], float(valores[k]), True
    return melhor, valor
