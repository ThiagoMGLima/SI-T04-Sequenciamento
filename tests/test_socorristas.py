"""Agentes socorristas no VictSim3: atribuição pelo mestre e arquivos gravados por cada socorrista."""

import pytest

from ag import ParametrosAG
from comum import DADOS_T3
from main_t4 import criar_socorristas
from parcelas import carregar_vitimas, ler_clusters_t3, montar_parcelas

RAPIDO = ParametrosAG(tamanho_populacao=10, max_geracoes=3)


def test_socorrista_de_adultos_recusa_parcela_com_crianca(tmp_path):
    socorristas = criar_socorristas()
    vitimas = carregar_vitimas(DADOS_T3 / "map_preenchido.csv")
    geral = next(p for p in montar_parcelas(vitimas, *ler_clusters_t3(DADOS_T3)) if p.tipo == "geral")
    with pytest.raises(ValueError):
        socorristas[2].do_rescue(vitimas, [(1, geral)], RAPIDO, tmp_path, sementes=range(1))


def test_cada_socorrista_grava_suas_sequencias_um_id_por_linha(tmp_path):
    socorristas = criar_socorristas()
    plano = socorristas[0].planejar_socorro(DADOS_T3 / "map_preenchido.csv", DADOS_T3, RAPIDO, tmp_path,
                                            sementes=range(1))
    arquivos = sorted(tmp_path.glob("cluster_*.txt"), key=lambda f: int(f.stem.split("_")[1]))
    assert [f.name for f in arquivos] == [f"cluster_{k}.txt" for k in range(1, 15)]
    ids = [int(l) for f in arquivos for l in f.read_text().splitlines()]
    assert len(ids) == len(set(ids)) == 410
    gravadas = sorted(s["seq"] for soc in socorristas for s in soc.sequencias)
    assert gravadas == list(range(1, 15))
    assert {s["socorrista"] for s in plano["sequencias"]} == {1, 2, 3, 4, 5}
