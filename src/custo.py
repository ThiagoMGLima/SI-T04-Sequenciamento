"""Custo de uma sequência de socorro: distância euclidiana (sem obstáculos) da base, pelas vítimas,
de volta à base, e latência ponderada (peso de urgência × tempo de chegada). Ver GLOSSARY.md."""

import numpy as np

# Faixa do peso de urgência por tri (0 verde, 1 amarelo, 2 vermelho, 3 preto). O preto é
# expectante: baixa prioridade, mas peso > 0 para não virar só "caminho".
FAIXA_TRI = {2: 3.0, 1: 2.0, 0: 1.0, 3: 0.25}
# Ajuste dentro da faixa pela chance de não sobreviver; 0.5 mantém as faixas sem sobreposição.
AJUSTE_SOBR = 0.5


def peso_urgencia(tri, sobr):
    """Peso de urgência: faixa START da tri mais AJUSTE_SOBR × (1 − sobr)."""
    return FAIXA_TRI[int(tri)] + AJUSTE_SOBR * (1.0 - float(sobr))


class ProblemaSequenciamento:
    """As vítimas de uma parcela, com posições, pesos de urgência e a base."""

    def __init__(self, xy, pesos, base, custo_socorro=1.0):
        self.n = len(pesos)
        self.pesos = np.asarray(pesos, float)
        self.custo_socorro = float(custo_socorro)
        pontos = np.vstack([np.asarray(base, float), np.asarray(xy, float)])  # índice 0 = base
        self.dist = np.hypot(*(pontos[:, None, :] - pontos[None, :, :]).transpose(2, 0, 1))

    def avaliar(self, ordens):
        """Distância e latência ponderada de uma ordem (vetor) ou de várias (matriz, uma por linha)."""
        ordens = np.asarray(ordens)
        unica = ordens.ndim == 1
        ordens = np.atleast_2d(ordens)
        no = ordens + 1  # nós da matriz de distâncias (0 é a base)
        passos = np.empty(ordens.shape)
        passos[:, 0] = self.dist[0, no[:, 0]]
        passos[:, 1:] = self.dist[no[:, :-1], no[:, 1:]]
        chegada = np.cumsum(passos, axis=1) + self.custo_socorro * np.arange(self.n)
        distancias = passos.sum(axis=1) + self.dist[no[:, -1], 0]
        latencias = (chegada * self.pesos[ordens]).sum(axis=1)
        return (distancias[0], latencias[0]) if unica else (distancias, latencias)

    def tempos_de_chegada(self, ordem):
        """Tempo de chegada de cada vítima (indexado pela vítima, não pela posição na ordem)."""
        tempos = np.empty(self.n)
        tempos[np.asarray(ordem)] = _tempos(self, ordem)
        return tempos


def _tempos(problema, ordem):
    no = np.asarray(ordem) + 1
    passos = np.concatenate([[problema.dist[0, no[0]]], problema.dist[no[:-1], no[1:]]])
    return np.cumsum(passos) + problema.custo_socorro * np.arange(problema.n)


class CustoNormalizado:
    """Custo da sequência (o que o AG minimiza): D/D_ref + λ·L/L_ref, com D e L de uma sequência
    de referência da mesma parcela (a do vizinho mais próximo). Conta as avaliações feitas."""

    def __init__(self, problema, referencia, lam=1.0):
        self.problema = problema
        self.lam = float(lam)
        self.d_ref, self.l_ref = problema.avaliar(referencia)
        self.chamadas = 0

    def __call__(self, ordens):
        ordens = np.asarray(ordens)
        self.chamadas += 1 if ordens.ndim == 1 else len(ordens)
        distancias, latencias = self.problema.avaliar(ordens)
        return distancias / self.d_ref + self.lam * latencias / self.l_ref
