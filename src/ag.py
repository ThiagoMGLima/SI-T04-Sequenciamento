"""Algoritmo genético para o sequenciamento do socorro, com os operadores de permutação do
material do professor (Ref_Material-Professor/07-algoritmos-geneticos.md)."""

from dataclasses import dataclass, field

import numpy as np


def pmx(pai1, pai2, inicio, fim):
    """Crossover PMX (slide 34). Cada filho recebe o segmento [inicio, fim) do outro pai, herda o
    resto do próprio pai e troca as repetições pelo mapeamento entre os dois segmentos."""
    return _filho_pmx(pai1, pai2, inicio, fim), _filho_pmx(pai2, pai1, inicio, fim)


def _filho_pmx(proprio, outro, inicio, fim):
    filho = proprio.copy()
    filho[inicio:fim] = outro[inicio:fim]
    # gene do segmento recebido -> gene do próprio pai na mesma posição
    mapa = dict(zip(outro[inicio:fim].tolist(), proprio[inicio:fim].tolist()))
    for i in [*range(inicio), *range(fim, len(filho))]:
        gene = filho[i]
        while gene in mapa:
            gene = mapa[gene]
        filho[i] = gene
    return filho


def mutacao_troca(individuo, i, j):
    """Mutação baseada em ordem (slide 35): troca os alelos das posições i e j."""
    mutante = individuo.copy()
    mutante[[i, j]] = mutante[[j, i]]
    return mutante


def mutacao_insercao(individuo, i, j):
    """Mutação baseada em posição (slide 35): retira o elemento da posição i e o insere na j."""
    mutante = np.delete(individuo, i)
    return np.insert(mutante, j, individuo[i])


def mutacao_embaralhamento(individuo, inicio, fim, rng):
    """Mutação por embaralhamento (slide 36): embaralha a sublista [inicio, fim)."""
    mutante = individuo.copy()
    mutante[inicio:fim] = rng.permutation(mutante[inicio:fim])
    return mutante


MUTACOES = ("troca", "insercao", "embaralhamento")


@dataclass(frozen=True)
class ParametrosAG:
    """Parametrização do AG. Valores típicos do material: pCROSS 0.8 e pMUT <= 0.05 (slides 20 e 22)."""

    tamanho_populacao: int = 100  # N (e R = N descendentes por geração)
    p_cruzamento: float = 0.8
    p_mutacao: float = 0.005      # por gene (locus), como na mutação uniforme do slide 20; valor calibrado
    mutacao: str = "insercao"
    max_geracoes: int = 1000
    estagnacao: int = 150         # gerações sem melhorar o melhor indivíduo


@dataclass
class ResultadoAG:
    ordem: np.ndarray
    custo: float
    geracoes: int
    chamadas_fitness: int
    melhor_por_geracao: list = field(default_factory=list)
    media_por_geracao: list = field(default_factory=list)


def executar_ag(custo, parametros, rng, sementes=()):
    """AG do slide 22: roleta, PMX, mutação por gene e sobrevivência dos N melhores entre pais e
    filhos. `custo` é minimizado; a roleta usa fitness = 1/custo. `sementes` substituem os
    primeiros indivíduos da população inicial (aleatória)."""
    p = parametros
    n, N = custo.problema.n, p.tamanho_populacao
    populacao = np.array([rng.permutation(n) for _ in range(N)])
    for k, semente in enumerate(sementes):
        populacao[k] = semente
    custos = custo(populacao)
    chamadas = N
    melhor_hist, media_hist = [float(custos.min())], [float(custos.mean())]
    melhor, sem_melhora, geracao = custos.min(), 0, 0

    while geracao < p.max_geracoes and sem_melhora < p.estagnacao:
        fitness = 1.0 / custos
        pais = populacao[rng.choice(N, N, p=fitness / fitness.sum())]  # roleta, R = N
        filhos = pais.copy()
        if n >= 2:
            for i in range(0, N - 1, 2):
                if rng.random() < p.p_cruzamento:
                    inicio, fim = sorted(rng.choice(n + 1, 2, replace=False))
                    filhos[i], filhos[i + 1] = pmx(pais[i], pais[i + 1], inicio, fim)
            for i, locus in zip(*np.nonzero(rng.random((N, n)) < p.p_mutacao)):
                filhos[i] = _mutar(filhos[i], locus, int(rng.integers(n)), p.mutacao, rng)
        custos_filhos = custo(filhos)
        chamadas += N
        todos = np.vstack([populacao, filhos])
        custos_todos = np.concatenate([custos, custos_filhos])
        sobreviventes = np.argsort(custos_todos, kind="stable")[:N]
        populacao, custos = todos[sobreviventes], custos_todos[sobreviventes]
        geracao += 1
        melhor_hist.append(float(custos[0]))
        media_hist.append(float(custos.mean()))
        if custos[0] < melhor - 1e-12:
            melhor, sem_melhora = custos[0], 0
        else:
            sem_melhora += 1

    return ResultadoAG(populacao[0].copy(), float(custos[0]), geracao, chamadas, melhor_hist, media_hist)


def _mutar(individuo, i, j, tipo, rng):
    if tipo == "troca":
        return mutacao_troca(individuo, i, j)
    if tipo == "insercao":
        return mutacao_insercao(individuo, i, j)
    if tipo == "embaralhamento":
        inicio, fim = min(i, j), max(i, j) + 1
        return mutacao_embaralhamento(individuo, inicio, fim, rng)
    raise ValueError(f"mutação desconhecida: {tipo}")
