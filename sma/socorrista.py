"""Agente socorrista da Tarefa 4 no VictSim3 (estende a AbstAgent do professor, sem modificá-la).

O socorrista 1 é o mestre: lê o mapa (resultado da exploração, com tri e sobr preditos na T3) e os
agrupamentos da T3, monta as parcelas, faz a atribuição e entrega a fila de cada socorrista com o
número de cada sequência. Cada socorrista, em do_rescue, sequencia as suas parcelas pelo AG e grava
os seus arquivos cluster_<seq>.txt. O socorro em si (andar no grid) não é executado: o enunciado
diz que não é necessário nesta tarefa, então o plano de ações fica vazio.
"""

from atribuicao import atribuir, estimar
from comum import IDADE_MAX_CRIANCA, SOCORRISTAS_ADULTOS
from parcelas import carregar_vitimas, ler_clusters_t3, montar_parcelas, problema_da_parcela
from sequenciamento import N_SEMENTES, sequenciar_parcela
from vs.abstract_agent import AbstAgent
from vs.constants import VS


class Socorrista(AbstAgent):
    def __init__(self, env, config_file, numero):
        super().__init__(env, config_file)
        self.numero = numero
        self.so_adultos = numero in SOCORRISTAS_ADULTOS  # só socorre vítimas com mais de 12 anos
        self.socorristas = []   # referências a todos os socorristas (inclusive este)
        self.sequencias = []    # sequências planejadas por este socorrista
        self.plan = []          # ações de caminhada: vazio, o socorro não é executado nesta tarefa
        self.set_state(VS.IDLE)

    def set_rescuers(self, socorristas):
        self.socorristas = socorristas

    def planejar_socorro(self, arquivo_mapa, pasta_t3, parametros, saida, sementes=range(N_SEMENTES)):
        """Papel do mestre: parcelas, atribuição, numeração das sequências e envio das filas."""
        vitimas = carregar_vitimas(arquivo_mapa)
        parcelas = {p.nome: p for p in montar_parcelas(vitimas, *ler_clusters_t3(pasta_t3))}
        estimativas = [estimar(p.nome, p.tipo, problema_da_parcela(vitimas, p)) for p in parcelas.values()]
        filas = atribuir(estimativas)

        # Seq. numerada por socorrista e, dentro dele, pela ordem da fila (linhas da Tabela 1).
        seq, filas_numeradas = 0, {}
        for numero, fila in filas.items():
            filas_numeradas[numero] = []
            for estimativa in fila:
                seq += 1
                filas_numeradas[numero].append((seq, parcelas[estimativa.nome]))

        for socorrista in self.socorristas:
            socorrista.do_rescue(vitimas, filas_numeradas.get(socorrista.numero, []), parametros, saida, sementes)

        return {
            "estimativas": [vars(e) for e in estimativas],
            "filas": {n: [p.nome for _, p in f] for n, f in filas_numeradas.items()},
            "sequencias": sorted((s for soc in self.socorristas for s in soc.sequencias), key=lambda s: s["seq"]),
        }

    def do_rescue(self, vitimas, fila, parametros, saida, sementes=range(N_SEMENTES)):
        """Sequencia cada parcela da fila pelo AG e grava cluster_<seq>.txt (um id por linha)."""
        self.set_state(VS.ACTIVE)
        for seq, parcela in fila:
            if self.so_adultos and (vitimas.loc[list(parcela.ids), "idade"] <= IDADE_MAX_CRIANCA).any():
                raise ValueError(f"{self.NAME} só socorre vítimas com mais de 12 anos: {parcela.nome}")
            r = sequenciar_parcela(vitimas, parcela, parametros, sementes=sementes)
            saida.mkdir(parents=True, exist_ok=True)
            (saida / f"cluster_{seq}.txt").write_text("\n".join(str(i) for i in r["ids"]) + "\n", encoding="utf-8")
            self.sequencias.append({"seq": seq, "socorrista": self.numero, "cluster_t3": parcela.cluster,
                                    "tipo": parcela.tipo, "ids_ruido": list(parcela.ids_ruido), **r})
            print(f"{self.NAME}: sequência {seq} ({parcela.nome}, {len(parcela.ids)} vítimas) "
                  f"distância {r['distancia']:.1f}, custo {r['custo']:.4f}")

    def deliberate(self) -> bool:
        """Chamado pelo simulador a cada ciclo: sem ações de caminhada nesta tarefa."""
        return False
