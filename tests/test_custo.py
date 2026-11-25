"""Custo da sequência: distância (base -> vítimas -> base), latência ponderada e peso de urgência."""

import numpy as np
import pytest

from custo import ProblemaSequenciamento, peso_urgencia

VERDE, AMARELO, VERMELHO, PRETO = 0, 1, 2, 3


def problema_de_duas_vitimas():
    # Base em (0, 0); vítima 0 em (3, 4) com peso 2; vítima 1 em (3, 0) com peso 1.
    return ProblemaSequenciamento(xy=np.array([[3.0, 4.0], [3.0, 0.0]]), pesos=np.array([2.0, 1.0]),
                                  base=(0.0, 0.0), custo_socorro=1.0)


def test_distancia_sai_da_base_e_volta_a_ela():
    # 0 -> (3,4) = 5; (3,4) -> (3,0) = 4; (3,0) -> base = 3.
    distancia, _ = problema_de_duas_vitimas().avaliar(np.array([0, 1]))
    assert distancia == pytest.approx(12.0)


def test_latencia_pondera_o_tempo_de_chegada_pela_urgencia():
    # Chegada à vítima 0: 5. À vítima 1: 5 + 4 + 1 (socorro da vítima 0) = 10. L = 2*5 + 1*10 = 20.
    # Na ordem inversa: vítima 1 em 3, vítima 0 em 3 + 4 + 1 = 8. L = 1*3 + 2*8 = 19.
    _, latencias = problema_de_duas_vitimas().avaliar(np.array([[0, 1], [1, 0]]))
    assert latencias.tolist() == pytest.approx([20.0, 19.0])


def test_peso_de_urgencia_segue_a_faixa_start_e_depois_a_sobr():
    assert peso_urgencia(VERMELHO, 0.4) == pytest.approx(3.3)
    assert peso_urgencia(VERMELHO, 1.0) > peso_urgencia(AMARELO, 0.0) > peso_urgencia(VERDE, 0.0)
    assert peso_urgencia(VERDE, 1.0) > peso_urgencia(PRETO, 0.0) > 0


def test_tempos_de_chegada_por_vitima():
    # Ordem [1, 0]: vítima 1 em 3; vítima 0 em 3 + 4 + 1 = 8 (indexados pela vítima, não pela posição).
    assert problema_de_duas_vitimas().tempos_de_chegada(np.array([1, 0])).tolist() == pytest.approx([8.0, 3.0])
