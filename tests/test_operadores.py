"""Operadores genéticos de permutação, conferidos com os exemplos dos slides do professor
(Ref_Material-Professor/07-algoritmos-geneticos.md, páginas 34 a 36)."""

import numpy as np

from ag import mutacao_embaralhamento, mutacao_insercao, mutacao_troca, pmx


def test_pmx_reproduz_o_exemplo_do_slide_34():
    # Pais 123456 e 235614; segmento trocado nas posições 3 a 5 (índices 2:5).
    filho1, filho2 = pmx(np.array([1, 2, 3, 4, 5, 6]), np.array([2, 3, 5, 6, 1, 4]), 2, 5)
    assert filho1.tolist() == [3, 2, 5, 6, 1, 4]
    assert filho2.tolist() == [2, 1, 3, 4, 5, 6]


def test_mutacao_por_troca_reproduz_o_exemplo_do_slide_35():
    # 123456 -> 153426: troca os alelos das posições 2 e 5 (índices 1 e 4).
    assert mutacao_troca(np.array([1, 2, 3, 4, 5, 6]), 1, 4).tolist() == [1, 5, 3, 4, 2, 6]


def test_mutacao_por_insercao_reproduz_o_exemplo_do_slide_35():
    # ABCDEF -> ACDEBF: retira o elemento da posição 2 (B) e o insere na posição 5.
    assert mutacao_insercao(np.array(list("ABCDEF")), 1, 4).tolist() == list("ACDEBF")


def test_mutacao_por_embaralhamento_so_mexe_na_sublista():
    # Slide 36: 123456 -> 124536 embaralha a sublista 345 (índices 2:5).
    resultado = mutacao_embaralhamento(np.array([1, 2, 3, 4, 5, 6]), 2, 5, np.random.default_rng(0))
    assert resultado[:2].tolist() == [1, 2] and resultado[5:].tolist() == [6]
    assert sorted(resultado[2:5].tolist()) == [3, 4, 5]
