"""Análises dos sequenciamentos (observacoes.md, item 15). Lê resultados/sequenciamento.json
(gravado pelos agentes) e grava resultados/analises.json:

1. tabela_1: a Tabela 1 do enunciado (uma linha por sequência e a linha μ ± σ).
2. comparacao: AG × ordem START da T3 × vizinho mais próximo × ordem aleatória × VMP + 2-opt.
3. lambda: varredura do peso λ da latência (3 sementes por inicialização e parcela).
4. convergencia: melhor e média do custo por geração (melhor execução pura e semeada) na maior parcela.
5. robustez: dispersão do custo entre as 20 execuções de cada sequência.
6. semeadura: inicialização pura × semeada (10 sementes cada).
7. socorristas: custo de viagem, makespan e latência por socorrista, T4 × plano da T3, e o TLIM.

Uso: uv run python src/analises.py   (depois de sma/main_t4.py)
"""

from concurrent.futures import ProcessPoolExecutor

import numpy as np

from ag import ParametrosAG
from atribuicao import avaliar_fila, estimar
from comum import CFG_SOCORRISTAS, CUSTO_SOCORRO, DADOS_T3, RESULTADOS, SEMENTE, ler_json, salvar_json
from custo import CustoNormalizado
from heuristicas import dois_opt, vizinho_mais_proximo
from parcelas import carregar_vitimas, ler_clusters_t3, montar_parcelas, ordem_start, problema_da_parcela
from sequenciamento import indices_start, sequenciar_parcela

LAMBDAS = (0.0, 0.25, 0.5, 1.0, 2.0, 4.0)
SEMENTES_LAMBDA = range(3)
N_ALEATORIAS = 100
PARCELA_CONVERGENCIA = "c2-adultos"  # a maior (78 vítimas)
CORES = {0: "VD", 1: "AM", 2: "VM", 3: "PR"}


def _dados():
    vitimas = carregar_vitimas(DADOS_T3 / "map_preenchido.csv")
    parcelas = {p.nome: p for p in montar_parcelas(vitimas, *ler_clusters_t3(DADOS_T3))}
    return vitimas, parcelas


def _media_dp(valores):
    return {"media": float(np.mean(valores)), "dp": float(np.std(valores))}


def tabela_1(vitimas, sequencias):
    """σ populacional (divide por n): descreve as vítimas de cada sequência, não é estimativa."""
    linhas = []
    for s in sequencias:
        v = vitimas.loc[s["ids"]]
        linhas.append({
            "seq": s["seq"], "agente": s["socorrista"], "parcela": s["parcela"],
            **{cor: int((v["tri"] == t).sum()) for t, cor in CORES.items()},
            "total": len(v), "distancia": s["distancia"],
            "sobr_media": float(v["sobr"].mean()), "sobr_dp": float(v["sobr"].std(ddof=0)),
        })
    return {"linhas": linhas,
            "total": _media_dp([l["total"] for l in linhas]),
            "distancia": _media_dp([l["distancia"] for l in linhas]),
            "soma_vitimas": sum(l["total"] for l in linhas),
            "soma_distancia": float(sum(l["distancia"] for l in linhas))}


def comparacao(vitimas, parcelas, sequencias):
    """Por método: distância, latência e custo por parcela, totais e o tempo médio de chegada
    (desde a saída da base, dentro da parcela) das vítimas de cada cor."""
    por_parcela = {}
    chegadas = {m: {t: [] for t in CORES} for m in ("ag", "start", "vmp", "vmp_2opt", "aleatoria")}
    rng = np.random.default_rng(SEMENTE)
    for s in sequencias:
        parcela = parcelas[s["parcela"]]
        problema = problema_da_parcela(vitimas, parcela)
        vmp = vizinho_mais_proximo(problema)
        custo = CustoNormalizado(problema, vmp)
        posicao = {i: k for k, i in enumerate(parcela.ids)}
        ordens = {
            "ag": np.array([posicao[i] for i in s["ids"]]),
            "start": indices_start(vitimas, parcela),
            "vmp": vmp,
            "vmp_2opt": dois_opt(custo, vmp)[0],
        }
        tri = vitimas.loc[list(parcela.ids), "tri"].to_numpy()
        metodos = {}
        for nome, ordem in ordens.items():
            d, l = problema.avaliar(ordem)
            metodos[nome] = {"distancia": float(d), "latencia": float(l), "custo": float(custo(ordem))}
            tempos = problema.tempos_de_chegada(ordem)
            for t in CORES:
                chegadas[nome][t] += tempos[tri == t].tolist()
        aleatorias = np.array([rng.permutation(problema.n) for _ in range(N_ALEATORIAS)])
        tempos = np.mean([problema.tempos_de_chegada(o) for o in aleatorias], axis=0)
        for t in CORES:
            chegadas["aleatoria"][t] += tempos[tri == t].tolist()
        d, l = problema.avaliar(aleatorias)
        metodos["aleatoria"] = {"distancia": float(d.mean()), "latencia": float(l.mean()),
                                "custo": float(custo(aleatorias).mean())}
        por_parcela[s["parcela"]] = metodos
    nomes = ["ag", "start", "vmp", "vmp_2opt", "aleatoria"]
    totais = {m: {k: float(sum(p[m][k] for p in por_parcela.values())) for k in ("distancia", "latencia")}
              for m in nomes}
    custo_medio = {m: float(np.mean([p[m]["custo"] for p in por_parcela.values()])) for m in nomes}
    chegada_media = {m: {CORES[t]: float(np.mean(v)) for t, v in por_tri.items()} for m, por_tri in chegadas.items()}
    return {"por_parcela": por_parcela, "totais": totais, "custo_medio": custo_medio,
            "chegada_media_por_tri": chegada_media, "n_aleatorias": N_ALEATORIAS}


def _rodar(tarefa):
    """Uma parcela da varredura de λ, num processo à parte."""
    nome, parametros, lam = tarefa
    vitimas, parcelas = _dados()
    r = sequenciar_parcela(vitimas, parcelas[nome], ParametrosAG(**parametros), lam=lam,
                           sementes=SEMENTES_LAMBDA)
    return (nome, lam), r


def varredura_lambda(nomes, parametros):
    tarefas = [(n, parametros, lam) for lam in LAMBDAS for n in nomes]
    with ProcessPoolExecutor() as pool:
        resultados = dict(pool.map(_rodar, tarefas))
    linhas = []
    for lam in LAMBDAS:
        rs = [resultados[(n, lam)] for n in nomes]
        linhas.append({"lambda": lam,
                       "distancia_total": float(sum(r["distancia"] for r in rs)),
                       "latencia_total": float(sum(r["latencia"] for r in rs))})
    return {"sementes_por_inicializacao": list(SEMENTES_LAMBDA), "linhas": linhas}


def semeadura(sequencias):
    """Inicialização pura × semeada, a partir das execuções gravadas pelos socorristas."""
    por_parcela = {}
    for s in sequencias:
        linha = {}
        for ini in ("puro", "semeado"):
            execs = [e for e in s["execucoes"] if e["inicializacao"] == ini]
            linha[ini] = _media_dp([e["custo"] for e in execs]) | {
                "melhor": float(min(e["custo"] for e in execs)),
                "chamadas": float(np.mean([e["chamadas_fitness"] for e in execs]))}
        diferenca = linha["puro"]["melhor"] - linha["semeado"]["melhor"]
        linha["vencedora"] = "empate" if abs(diferenca) < 1e-9 else ("puro" if diferenca < 0 else "semeado")
        por_parcela[s["parcela"]] = linha
    vitorias = {r: sum(1 for l in por_parcela.values() if l["vencedora"] == r) for r in ("puro", "semeado", "empate")}
    return {"por_parcela": por_parcela, "vitorias": vitorias,
            "custo_medio_melhor": {ini: float(np.mean([l[ini]["melhor"] for l in por_parcela.values()]))
                                   for ini in ("puro", "semeado")},
            "custo_medio_final": float(np.mean([s["custo"] for s in sequencias]))}


def robustez(sequencias):
    return {s["parcela"]: {
        "custo": _media_dp([e["custo"] for e in s["execucoes"]]),
        "distancia": _media_dp([e["distancia"] for e in s["execucoes"]]),
        "custo_min": float(min(e["custo"] for e in s["execucoes"])),
        "custo_max": float(max(e["custo"] for e in s["execucoes"])),
        "geracoes": _media_dp([e["geracoes"] for e in s["execucoes"]]),
        "chamadas_fitness": _media_dp([e["chamadas_fitness"] for e in s["execucoes"]]),
    } for s in sequencias}


def _tlim():
    for linha in (CFG_SOCORRISTAS / "soc_1.txt").read_text().splitlines():
        if linha.startswith("TLIM"):
            return float(linha.split()[1])
    raise ValueError(f"TLIM não encontrado em {CFG_SOCORRISTAS / 'soc_1.txt'}")


def socorristas(vitimas, parcelas, sequencias, filas_t4):
    """Custo de viagem (distância + socorro) e latência total de cada socorrista em três planos:
    T4 (atribuição por enumeração, AG, regra de Smith), T3 com as sequências do AG (isola o efeito da
    atribuição) e T3 completa (LPT, ordem START, fila pela prioridade P_c da T3)."""
    def est(nome, ordem_ids):
        parcela = parcelas[nome]
        problema = problema_da_parcela(vitimas, parcela)
        posicao = {i: k for k, i in enumerate(parcela.ids)}
        return estimar(nome, parcela.tipo, problema, np.array([posicao[i] for i in ordem_ids]))

    ag = {s["parcela"]: est(s["parcela"], s["ids"]) for s in sequencias}
    start = {n: est(n, ordem_start(vitimas, p.ids)) for n, p in parcelas.items()}

    t3 = ler_json(DADOS_T3 / "agrupamento_t3.json")["atribuicao"]
    filas_t3 = {int(s): [] for s in t3["fila_de_clusters"]}
    for c in sorted(t3["por_cluster"], key=int):  # cluster da T3 numerado por prioridade P_c
        info = t3["por_cluster"][c]
        filas_t3[info["socorrista_adultos"]].append(f"c{c}-adultos")
        filas_t3[info["socorrista_geral"]].append(f"c{c}-geral")

    def plano(filas, estimativas):
        por_socorrista = {}
        for s, nomes in filas.items():
            custo, latencia = avaliar_fila([estimativas[n] for n in nomes])
            por_socorrista[int(s)] = {"parcelas": list(nomes), "custo_viagem": custo, "latencia": latencia,
                                      "vitimas": sum(len(parcelas[n].ids) for n in nomes)}
        custos = [v["custo_viagem"] for v in por_socorrista.values()]
        return {"por_socorrista": por_socorrista, "makespan": max(custos), "custo_total": sum(custos),
                "latencia_total": sum(v["latencia"] for v in por_socorrista.values())}

    return {
        "tlim": _tlim(),
        "custo_socorro": CUSTO_SOCORRO,
        "t4": plano({int(s): f for s, f in filas_t4.items()}, ag),
        "t3_atribuicao_com_ag": plano(filas_t3, ag),
        "t3_completa": plano(filas_t3, start),
    }


def main():
    vitimas, parcelas = _dados()
    seq = ler_json(RESULTADOS / "sequenciamento.json")
    sequencias, parametros = seq["sequencias"], seq["parametros"]
    nomes = [s["parcela"] for s in sequencias]

    resultado = {
        "tabela_1": tabela_1(vitimas, sequencias),
        "comparacao": comparacao(vitimas, parcelas, sequencias),
        "lambda": varredura_lambda(nomes, parametros),
        "robustez": robustez(sequencias),
        "semeadura": semeadura(sequencias),
        "socorristas": socorristas(vitimas, parcelas, sequencias, seq["filas"]),
    }
    resultado["convergencia"] = {
        "parcela": PARCELA_CONVERGENCIA,
        **next(s for s in sequencias if s["parcela"] == PARCELA_CONVERGENCIA)["historicos"],
    }
    salvar_json(RESULTADOS / "analises.json", resultado)

    t1 = resultado["tabela_1"]
    for l in t1["linhas"]:
        print(f"{l['seq']:>2} {l['agente']} {l['VD']:>3} {l['AM']:>3} {l['VM']:>3} {l['PR']:>3} {l['total']:>3} "
              f"{l['distancia']:7.1f} {l['sobr_media']:.4f} {l['sobr_dp']:.4f}  {l['parcela']}")
    print(f"total {t1['total']}  distância {t1['distancia']}")
    print("custo médio por método:", resultado["comparacao"]["custo_medio"])
    print("totais:", resultado["comparacao"]["totais"])
    print("λ:", resultado["lambda"]["linhas"])
    for k in ("t4", "t3_atribuicao_com_ag", "t3_completa"):
        p = resultado["socorristas"][k]
        print(k, "makespan", round(p["makespan"], 1), "total", round(p["custo_total"], 1),
              "latência", round(p["latencia_total"]),
              {s: round(v["custo_viagem"], 1) for s, v in p["por_socorrista"].items()})


if __name__ == "__main__":
    main()
