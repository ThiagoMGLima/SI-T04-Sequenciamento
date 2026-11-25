"""Parcelas montadas a partir dos clusters e do ruído da T3."""

import pandas as pd

from comum import DADOS_T3, IDADE_MAX_CRIANCA
from parcelas import anexar_ruido, carregar_vitimas, ler_clusters_t3, montar_parcelas, ordem_start


def parcelas_reais():
    vitimas = carregar_vitimas(DADOS_T3 / "map_preenchido.csv")
    clusters, ruido = ler_clusters_t3(DADOS_T3)
    return vitimas, montar_parcelas(vitimas, clusters, ruido)


def test_cada_vitima_do_mapa_esta_em_exatamente_uma_parcela():
    vitimas, parcelas = parcelas_reais()
    ids = [i for p in parcelas for i in p.ids]
    assert len(ids) == len(set(ids)) == 410
    assert set(ids) == set(vitimas.index)


def test_sao_duas_parcelas_por_cluster_e_criancas_so_na_parcela_geral():
    vitimas, parcelas = parcelas_reais()
    assert len(parcelas) == 14
    for p in parcelas:
        idades = vitimas.loc[list(p.ids), "idade"]
        if p.tipo == "adultos":
            assert (idades > IDADE_MAX_CRIANCA).all() and not p.ids_ruido
        else:
            assert set(p.ids_ruido) <= set(p.ids)


def test_vitima_ruido_vai_para_o_cluster_da_vitima_agrupada_mais_proxima():
    vitimas = pd.DataFrame({"x": [0, 10, 1, 9], "y": [0, 0, 0, 0]}, index=[100, 200, 300, 400])
    anexo = anexar_ruido(vitimas, clusters={1: [100], 2: [200]}, ruido=[300, 400])
    assert anexo == {1: [300], 2: [400]}


def test_ordem_start_poe_vermelho_amarelo_verde_preto_e_vulneraveis_antes():
    vitimas = pd.DataFrame({
        "tri":   [3, 0, 2, 1, 2],
        "idade": [30, 30, 30, 30, 8],
        "sobr":  [0.1, 0.9, 0.4, 0.7, 0.6],
    }, index=[1, 2, 3, 4, 5])
    # vermelhos: a criança (5) antes do adulto (3); depois amarelo (4), verde (2), preto (1)
    assert ordem_start(vitimas, [1, 2, 3, 4, 5]) == [5, 3, 4, 2, 1]
