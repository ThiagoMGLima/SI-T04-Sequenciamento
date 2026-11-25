"""Heurísticas de referência e o algoritmo genético sobre uma parcela pequena."""

import numpy as np
import pytest

from ag import ParametrosAG, executar_ag
from custo import CustoNormalizado, ProblemaSequenciamento
from heuristicas import vizinho_mais_proximo


def problema_em_linha():
    # Base em (0, 0) e vítimas em x = 3, 1, 2 (índices 0, 1, 2), todas com peso 1.
    return ProblemaSequenciamento(xy=np.array([[3.0, 0.0], [1.0, 0.0], [2.0, 0.0]]), pesos=np.ones(3),
                                  base=(0.0, 0.0))


def problema_aleatorio(n=25, semente=7):
    rng = np.random.default_rng(semente)
    return ProblemaSequenciamento(xy=rng.uniform(0, 50, (n, 2)), pesos=rng.uniform(0.25, 3.5, n),
                                  base=(25.0, 25.0))


def test_vizinho_mais_proximo_vai_sempre_a_vitima_mais_perto():
    assert vizinho_mais_proximo(problema_em_linha()).tolist() == [1, 2, 0]


def test_custo_normalizado_vale_1_mais_lambda_na_sequencia_de_referencia():
    problema = problema_aleatorio()
    referencia = vizinho_mais_proximo(problema)
    custo = CustoNormalizado(problema, referencia, lam=0.5)
    assert custo(referencia) == pytest.approx(1.5)


def test_ag_devolve_uma_permutacao_das_vitimas():
    problema = problema_aleatorio()
    custo = CustoNormalizado(problema, vizinho_mais_proximo(problema))
    resultado = executar_ag(custo, ParametrosAG(tamanho_populacao=20, max_geracoes=30), np.random.default_rng(0))
    assert sorted(resultado.ordem.tolist()) == list(range(problema.n))


def test_ag_semeado_nunca_fica_pior_que_a_semente():
    problema = problema_aleatorio()
    semente = vizinho_mais_proximo(problema)
    custo = CustoNormalizado(problema, semente)
    resultado = executar_ag(custo, ParametrosAG(tamanho_populacao=20, max_geracoes=30),
                            np.random.default_rng(0), sementes=[semente])
    assert resultado.custo <= custo(semente)


def test_ag_conta_as_chamadas_da_funcao_de_fitness():
    problema = problema_aleatorio()
    custo = CustoNormalizado(problema, vizinho_mais_proximo(problema))
    resultado = executar_ag(custo, ParametrosAG(tamanho_populacao=20, max_geracoes=30, estagnacao=1000),
                            np.random.default_rng(0))
    # população inicial + uma descendência de tamanho N por geração
    assert resultado.geracoes == 30
    assert resultado.chamadas_fitness == 20 * 31
