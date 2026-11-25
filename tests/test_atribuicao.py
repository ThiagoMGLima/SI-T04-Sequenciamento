"""Atribuição das parcelas aos socorristas e fila de cada socorrista (regra de Smith)."""

import pytest

from atribuicao import EstimativaParcela, atribuir, avaliar_fila, ordenar_fila


def est(nome, tipo, custo, peso=1.0, latencia=0.0):
    return EstimativaParcela(nome=nome, tipo=tipo, custo_viagem=custo, peso_total=peso, latencia_interna=latencia)


def test_fila_segue_a_regra_de_smith():
    # A: muito longe e pouco urgente; B: perto e com a mesma urgência -> B primeiro.
    fila = ordenar_fila([est("A", "adultos", 10.0, 1.0), est("B", "adultos", 1.0, 1.0)])
    assert [p.nome for p in fila] == ["B", "A"]


def test_avaliar_fila_soma_custos_e_atrasa_as_parcelas_seguintes():
    # A (C=10, W=2, L=5) e depois B (C=4, W=1, L=3): custo 14; latência 5 + (1*10 + 3) = 18.
    custo, latencia = avaliar_fila([est("A", "adultos", 10.0, 2.0, 5.0), est("B", "adultos", 4.0, 1.0, 3.0)])
    assert (custo, latencia) == pytest.approx((14.0, 18.0))


def test_atribuicao_minimiza_o_makespan():
    # Custos 5, 5, 5, 4, 3, 3 em 3 socorristas: o melhor é {5,3}, {5,3}, {5,4} -> makespan 9.
    parcelas = [est(f"p{i}", "adultos", c) for i, c in enumerate([5, 5, 5, 4, 3, 3])]
    filas = atribuir(parcelas)
    assert max(avaliar_fila(f)[0] for f in filas.values()) == pytest.approx(9.0)


def test_criancas_e_ruido_so_vao_para_socorristas_gerais():
    parcelas = [est("a1", "adultos", 5), est("g1", "geral", 5), est("a2", "adultos", 2), est("g2", "geral", 7)]
    filas = atribuir(parcelas)
    assert {p.tipo for s in (1, 2) for p in filas[s]} == {"geral"}
    assert {p.tipo for s in (3, 4, 5) for p in filas[s]} == {"adultos"}
    assert sorted(p.nome for f in filas.values() for p in f) == ["a1", "a2", "g1", "g2"]
