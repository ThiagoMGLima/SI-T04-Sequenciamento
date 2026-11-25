"""Parcelas: cada cluster da T3 dividido em adultos (> 12 anos) e geral (crianças + vítimas-ruído
anexadas). Ver GLOSSARY.md e docs/adr/0001-parcelas-viram-sequencias.md."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from comum import BASE, CUSTO_SOCORRO, IDADE_MAX_CRIANCA, N_VITIMAS
from custo import ProblemaSequenciamento, peso_urgencia

# Ordem START da T3: vermelho, amarelo, verde, preto (tri: 0 verde, 1 amarelo, 2 vermelho, 3 preto).
POSICAO_START = {2: 0, 1: 1, 0: 2, 3: 3}
IDADE_MIN_IDOSO = 60  # T3: crianças e idosos têm preferência na mesma tri


@dataclass(frozen=True)
class Parcela:
    cluster: int           # número do cluster na T3
    tipo: str              # "adultos" ou "geral"
    ids: tuple             # vítimas da parcela (ordem da T3, sem significado de socorro)
    ids_ruido: tuple = ()  # as que vieram do ruído (só na parcela geral)

    @property
    def nome(self):
        return f"c{self.cluster}-{self.tipo}"


def carregar_vitimas(caminho):
    """As vítimas do mapa preenchido na T3 (tri e sobr preditos), indexadas pelo id, com x e y absolutos."""
    df = pd.read_csv(caminho)
    vitimas = df[df["id"] != -1].copy()
    if len(vitimas) != N_VITIMAS or (vitimas["tri"] == -1).any() or (vitimas["sobr"] == -1).any():
        raise SystemExit(f"{caminho}: esperado o mapa da T3 com tri e sobr preenchidos")
    vitimas["id"] = vitimas["id"].astype(int)
    vitimas["tri"] = vitimas["tri"].astype(int)
    vitimas["x"] = vitimas["x_rel"] + BASE[0]
    vitimas["y"] = vitimas["y_rel"] + BASE[1]
    return vitimas.set_index("id").sort_index()


def _ler_ids(caminho):
    return [int(linha) for linha in caminho.read_text(encoding="utf-8").split()]


def ler_clusters_t3(pasta):
    """{número do cluster: ids} dos cluster_i.txt da T3 e a lista do ruido.txt."""
    clusters = {int(f.stem.split("_")[1]): _ler_ids(f) for f in pasta.glob("cluster_*.txt")}
    return dict(sorted(clusters.items())), _ler_ids(pasta / "ruido.txt")


def anexar_ruido(vitimas, clusters, ruido):
    """Cada vítima-ruído vai para o cluster da vítima agrupada mais próxima em (x, y), como na T3.
    Empate de distância: vence a vítima agrupada de menor id."""
    agrupadas = sorted((i, c) for c, ids in clusters.items() for i in ids)
    pontos = vitimas.loc[[i for i, _ in agrupadas], ["x", "y"]].to_numpy(float)
    anexo = {c: [] for c in clusters}
    for r in ruido:
        d = np.hypot(*(pontos - vitimas.loc[r, ["x", "y"]].to_numpy(float)).T)
        anexo[agrupadas[int(np.argmin(d))][1]].append(r)
    return anexo


def montar_parcelas(vitimas, clusters, ruido):
    anexo = anexar_ruido(vitimas, clusters, ruido)
    parcelas = []
    for c, ids in clusters.items():
        crianca = vitimas.loc[ids, "idade"] <= IDADE_MAX_CRIANCA
        adultos = [i for i, k in zip(ids, crianca) if not k]
        criancas = [i for i, k in zip(ids, crianca) if k]
        parcelas.append(Parcela(c, "adultos", tuple(adultos)))
        parcelas.append(Parcela(c, "geral", tuple(criancas + anexo[c]), tuple(anexo[c])))
    return [p for p in parcelas if p.ids]


def ordem_start(vitimas, ids):
    """Ordem de socorro da T3: START; na mesma tri, crianças e idosos antes; depois menor sobr."""
    def chave(i):
        v = vitimas.loc[i]
        vulneravel = v["idade"] <= IDADE_MAX_CRIANCA or v["idade"] >= IDADE_MIN_IDOSO
        return (POSICAO_START[int(v["tri"])], not vulneravel, v["sobr"], i)
    return sorted(ids, key=chave)


def problema_da_parcela(vitimas, parcela):
    dados = vitimas.loc[list(parcela.ids)]
    pesos = [peso_urgencia(t, s) for t, s in zip(dados["tri"], dados["sobr"])]
    return ProblemaSequenciamento(dados[["x", "y"]].to_numpy(float), pesos, BASE, CUSTO_SOCORRO)
