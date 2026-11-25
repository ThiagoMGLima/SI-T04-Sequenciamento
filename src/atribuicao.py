"""Atribuição das parcelas aos socorristas (feita pelo socorrista mestre) e fila de cada um.

- Parcelas de adultos vão para os socorristas de adultos (3, 4, 5); parcelas gerais (crianças +
  vítimas-ruído) para os socorristas gerais (1, 2).
- O custo de cada parcela é estimado pela sequência do vizinho mais próximo (antes do AG).
- A divisão é ótima por enumeração exaustiva (3^7 e 2^7 combinações): minimiza o makespan do grupo
  e, no empate, a latência ponderada total.
- A fila de cada socorrista segue a regra de Smith (1956): maior peso total / custo de viagem
  primeiro, que minimiza a soma dos tempos de conclusão ponderados.
"""

from dataclasses import dataclass
from itertools import product

from comum import SOCORRISTAS_ADULTOS, SOCORRISTAS_GERAIS
from heuristicas import vizinho_mais_proximo


@dataclass(frozen=True)
class EstimativaParcela:
    nome: str
    tipo: str               # "adultos" ou "geral"
    custo_viagem: float     # distância da sequência + custo de socorro de cada vítima
    peso_total: float       # soma dos pesos de urgência
    latencia_interna: float # latência ponderada da sequência, a partir da saída da base


def estimar(nome, tipo, problema, ordem=None):
    """Estimativa da parcela pela sequência dada (padrão: a do vizinho mais próximo)."""
    ordem = vizinho_mais_proximo(problema) if ordem is None else ordem
    distancia, latencia = problema.avaliar(ordem)
    return EstimativaParcela(nome, tipo, float(distancia + problema.custo_socorro * problema.n),
                             float(problema.pesos.sum()), float(latencia))


def ordenar_fila(parcelas):
    """Regra de Smith; empate pelo nome, para ser determinística."""
    return sorted(parcelas, key=lambda p: (-p.peso_total / p.custo_viagem, p.nome))


def avaliar_fila(fila):
    """Custo total da fila e latência ponderada total: as vítimas de uma parcela esperam, além da
    latência interna, o custo de todas as parcelas anteriores da fila."""
    inicio, latencia = 0.0, 0.0
    for p in fila:
        latencia += p.peso_total * inicio + p.latencia_interna
        inicio += p.custo_viagem
    return inicio, latencia


def _dividir(parcelas, socorristas):
    """Divisão ótima de um grupo de parcelas entre socorristas equivalentes, por enumeração."""
    melhor_chave, melhor = None, None
    for escolha in product(socorristas, repeat=len(parcelas)):
        filas = {s: ordenar_fila([p for p, e in zip(parcelas, escolha) if e == s]) for s in socorristas}
        avaliacoes = [avaliar_fila(f) for f in filas.values()]
        chave = (max(c for c, _ in avaliacoes), sum(l for _, l in avaliacoes))
        # tolerância para não decidir empates por erro de arredondamento
        if melhor_chave is None or chave[0] < melhor_chave[0] - 1e-9 or (
                abs(chave[0] - melhor_chave[0]) <= 1e-9 and chave[1] < melhor_chave[1] - 1e-9):
            melhor_chave, melhor = chave, filas
    return melhor


def atribuir(parcelas):
    """{socorrista: fila de parcelas}, com os socorristas de 1 a 5."""
    filas = _dividir([p for p in parcelas if p.tipo == "geral"], SOCORRISTAS_GERAIS)
    filas.update(_dividir([p for p in parcelas if p.tipo == "adultos"], SOCORRISTAS_ADULTOS))
    return dict(sorted(filas.items()))
