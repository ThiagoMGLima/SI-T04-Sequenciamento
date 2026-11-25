"""Relatório PDF (Typst) e pacote de entrega da Tarefa 4.

Todos os números do relatório saem dos JSON de resultados/ (e das entradas da T3), formatados aqui
em pt-BR e passados ao Typst por sys_inputs. Monta também entrega/:
- relatorio_T04.pdf;
- clusters/cluster_1.txt ... cluster_n.txt e clusters.zip (os arquivos gravados pelos socorristas);
- codigo_fonte_T04.zip (código, agentes, testes, entradas da T3; sem o VictSim3).

Uso: uv run python src/gerar_relatorio.py   (depois de src/figuras.py)
"""

import json
import re
import shutil
import zipfile

import numpy as np
import typst

from ag import ParametrosAG
from calibrar import P_MUTACAO, PARCELAS_CALIBRACAO, TAMANHO_POPULACAO
from comum import (BASE, CUSTO_SOCORRO, DADOS_T3, IDADE_MAX_CRIANCA, RAIZ, RESULTADOS, SAIDA_CLUSTERS,
                   SOCORRISTAS_ADULTOS, SOCORRISTAS_GERAIS, ler_json)
from custo import AJUSTE_SOBR, FAIXA_TRI
from parcelas import carregar_vitimas, ler_clusters_t3

TEMPLATE = RAIZ / "src" / "relatorio" / "relatorio.typ"
ENTREGA = RAIZ / "entrega"
RELATORIO = ENTREGA / "relatorio_T04.pdf"
CLUSTERS_ZIP = ENTREGA / "clusters.zip"
CODIGO_FONTE = ENTREGA / "codigo_fonte_T04.zip"
PASTA_NO_ZIP = "codigo_fonte_T04"
DATA_FIXA = (2026, 11, 25, 0, 0, 0)
CODIGO = ["src", "sma", "tests", "docs", "dados/t3", "map.csv", "README.md", "GLOSSARY.md", "pyproject.toml",
          "uv.lock", ".python-version"]


def f(x, casas=2):
    """Número em pt-BR: vírgula decimal e ponto de milhar."""
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def g(x):
    """Número sem casas desnecessárias (1, 0,25, 4), em pt-BR."""
    return f"{x:g}".replace(".", ",")


def pct(antes, depois, casas=0):
    """Variação percentual de antes para depois (negativa = redução)."""
    return f(100 * (depois - antes) / antes, casas).replace("-", "−")


def dados_relatorio():
    seq = ler_json(RESULTADOS / "sequenciamento.json")
    an = ler_json(RESULTADOS / "analises.json")
    cal = ler_json(RESULTADOS / "calibracao.json")
    t3 = ler_json(DADOS_T3 / "agrupamento_t3.json")
    vitimas = carregar_vitimas(DADOS_T3 / "map_preenchido.csv")
    clusters, ruido = ler_clusters_t3(DADOS_T3)
    p = ParametrosAG(**seq["parametros"])
    saida_plot = (RESULTADOS / "plot_victsim_saida.txt").read_text(encoding="utf-8")
    sequencias = seq["sequencias"]

    par = t3["tabela_1"][str(t3["par_escolhida"])]
    t1 = an["tabela_1"]
    comp = an["comparacao"]
    soc = an["socorristas"]
    sem = an["semeadura"]
    rob = an["robustez"]
    tot = comp["totais"]

    por_socorrista = []
    for s in sorted(soc["t4"]["por_socorrista"], key=int):
        v = soc["t4"]["por_socorrista"][s]
        seqs = [x for x in sequencias if x["socorrista"] == int(s)]
        por_socorrista.append({
            "socorrista": s, "tipo": "geral" if int(s) in SOCORRISTAS_GERAIS else "adultos",
            "seqs": ", ".join(str(x["seq"]) for x in seqs),
            "parcelas": ", ".join(v["parcelas"]), "vitimas": str(v["vitimas"]),
            "custo": f(v["custo_viagem"], 1), "custo_t3": f(soc["t3_atribuicao_com_ag"]["por_socorrista"][s]["custo_viagem"], 1),
            "excede": v["custo_viagem"] > soc["tlim"],
        })

    linhas_cal = cal["linhas"]
    escolhida = cal["parametros_escolhidos"]
    melhor_troca = min((l for l in linhas_cal if l["mutacao"] == "troca"), key=lambda l: l["custo_medio"])
    melhor_emb = min((l for l in linhas_cal if l["mutacao"] == "embaralhamento"), key=lambda l: l["custo_medio"])

    dp_custos = [r["custo"]["dp"] for r in rob.values()]
    com_criancas = sum(1 for ids in clusters.values() if (vitimas.loc[ids, "idade"] <= IDADE_MAX_CRIANCA).any())
    n_adultos = sum(1 for x in sequencias if x["tipo"] == "adultos")
    n_gerais = len(sequencias) - n_adultos
    top = linhas_cal[:5]
    mutacoes_top = {l["mutacao"] for l in top}
    c2 = next(x for x in sequencias if x["parcela"] == an["convergencia"]["parcela"])
    execs = sequencias[0]["execucoes"]
    por_inicializacao = sum(1 for e in execs if e["inicializacao"] == execs[0]["inicializacao"])
    lam = seq["lambda"]
    varredura = an["lambda"]["linhas"]
    quedas = [a["latencia_total"] - b["latencia_total"] for a, b in zip(varredura, varredura[1:])]
    maior = int(np.argmax(quedas))
    queda_total = varredura[0]["latencia_total"] - varredura[-1]["latencia_total"]
    dist_ini, dist_fim = varredura[0]["distancia_total"], varredura[-1]["distancia_total"]
    vitorias = sem["vitorias"]
    ids_ruido = set(ruido)

    return {
        "base": f"{BASE[0]}, {BASE[1]}",
        "idade_crianca": str(IDADE_MAX_CRIANCA),
        "t3": {
            "eps": f(par["eps"], 3), "min_samples": str(par["min_samples"]), "clusters": str(par["clusters"]),
            "ruido": str(par["pontos_ruido"]), "cobertura": f(par["cobertura"], 3),
            "silhueta": f(par["silhueta_global"], 3), "score": f(par["score_final"], 3),
            "features": ", ".join(t3["features"]),
            "tri": {c: str(int((vitimas["tri"] == t).sum())) for t, c in ((0, "VD"), (1, "AM"), (2, "VM"), (3, "PR"))},
            "vermelhas": str(int((vitimas["tri"] == 2).sum())),
            "ruido_vermelhas": str(int((vitimas.loc[list(ids_ruido), "tri"] == 2).sum())),
            "ruido_adultos": str(int((vitimas.loc[list(ids_ruido), "idade"] > IDADE_MAX_CRIANCA).sum())),
            "criancas": str(int((vitimas["idade"] <= IDADE_MAX_CRIANCA).sum())),
            "acuracia": re.search(r"Acurácia:\s*([\d.]+)", saida_plot).group(1).replace(".", ","),
            "mse": re.search(r"MSE \(sobr\):\s*([\d.]+)", saida_plot).group(1).replace(".", ","),
            "tamanhos": ", ".join(f"{len(ids)}" for ids in clusters.values()),
            "com_criancas": str(com_criancas),
        },
        "enumeracao": {"adultos": str(n_adultos), "gerais": str(n_gerais),
                       "soc_adultos": str(len(SOCORRISTAS_ADULTOS)), "soc_gerais": str(len(SOCORRISTAS_GERAIS)),
                       "comb_adultos": f(len(SOCORRISTAS_ADULTOS) ** n_adultos, 0),
                       "comb_gerais": f(len(SOCORRISTAS_GERAIS) ** n_gerais, 0)},
        "n_vitimas": str(len(vitimas)),
        "lambda": g(lam), "custo_vmp": g(1 + lam),
        "varredura": {"lam_min": g(varredura[0]["lambda"]), "lam_max": g(varredura[-1]["lambda"]),
                      "red_lat": f(100 * queda_total / varredura[0]["latencia_total"], 0),
                      "var_dist": f(100 * abs(dist_fim - dist_ini) / dist_ini, 0),
                      "verbo_dist": "sobe" if dist_fim > dist_ini else "cai",
                      "passo_de": g(varredura[maior]["lambda"]), "passo_ate": g(varredura[maior + 1]["lambda"]),
                      "passo_fracao": f(100 * quedas[maior] / queda_total, 0)},
        "convergencia": {"parcela": c2["parcela"], "n": str(len(c2["ids"]))},
        "lambda_sementes": str(len(an["lambda"]["sementes_por_inicializacao"])),
        "pesos": {"VM": f(FAIXA_TRI[2], 0), "AM": f(FAIXA_TRI[1], 0), "VD": f(FAIXA_TRI[0], 0),
                  "PR": f(FAIXA_TRI[3], 2), "ajuste": f(AJUSTE_SOBR, 1), "socorro": f(CUSTO_SOCORRO, 0)},
        "parcelas": [{"seq": str(x["seq"]), "nome": x["parcela"], "cluster": str(x["cluster_t3"]), "tipo": x["tipo"],
                      "n": str(len(x["ids"])), "ruido": str(len(x["ids_ruido"])), "socorrista": str(x["socorrista"])}
                     for x in sequencias],
        "socorristas": por_socorrista,
        "makespan": {"t4": f(soc["t4"]["makespan"], 1), "t3_ag": f(soc["t3_atribuicao_com_ag"]["makespan"], 1),
                     "t3": f(soc["t3_completa"]["makespan"], 1),
                     "red_t3_ag": pct(soc["t3_atribuicao_com_ag"]["makespan"], soc["t4"]["makespan"]),
                     "red_t3": pct(soc["t3_completa"]["makespan"], soc["t4"]["makespan"]),
                     "lat_t4": f(soc["t4"]["latencia_total"], 0), "lat_t3": f(soc["t3_completa"]["latencia_total"], 0),
                     "tlim": f(soc["tlim"], 0),
                     "excedem": ", ".join(s["socorrista"] for s in por_socorrista if s["excede"]),
                     "n_excedem": str(sum(s["excede"] for s in por_socorrista))},
        "ag": {"N": str(p.tamanho_populacao), "pc": f(p.p_cruzamento, 1), "pm": f(p.p_mutacao, 3),
               "mutacao": {"insercao": "inserção", "troca": "troca", "embaralhamento": "embaralhamento"}[p.mutacao],
               "max_ger": f(p.max_geracoes, 0), "estag": str(p.estagnacao),
               "sementes": str(por_inicializacao), "execucoes": str(len(execs))},
        "calibracao": {
            "n_comb": str(len(linhas_cal)), "parcelas": ", ".join(PARCELAS_CALIBRACAO),
            "n_parcelas": str(len(PARCELAS_CALIBRACAO)), "n_top": str(len(top)),
            "top_mutacao": ("todas de " + top[0]["mutacao"].replace("insercao", "inserção")) if len(mutacoes_top) == 1 else "de mais de um tipo",
            "pms": "; ".join(f(x, 3) for x in P_MUTACAO), "Ns": "; ".join(str(x) for x in TAMANHO_POPULACAO),
            "sementes": str(len(cal["sementes"])),
            "linhas": [{"mutacao": l["mutacao"].replace("insercao", "inserção"), "pm": f(l["p_mutacao"], 3),
                        "N": str(l["tamanho_populacao"]), "custo": f(l["custo_medio"], 4),
                        "chamadas": f(l["chamadas_media"], 0),
                        "escolhida": (l["mutacao"], l["p_mutacao"], l["tamanho_populacao"]) ==
                                     (escolhida["mutacao"], escolhida["p_mutacao"], escolhida["tamanho_populacao"])}
                       for l in linhas_cal[:5]],
            "melhor_troca": f(melhor_troca["custo_medio"], 4), "melhor_emb": f(melhor_emb["custo_medio"], 4),
        },
        "tabela_1": {
            "linhas": [{k: (f(v, 1) if k == "distancia" else f(v, 4) if k.startswith("sobr") else str(v))
                        for k, v in l.items()} for l in t1["linhas"]],
            "total": f"{f(t1['total']['media'], 1)} ± {f(t1['total']['dp'], 1)}",
            "distancia": f"{f(t1['distancia']['media'], 1)} ± {f(t1['distancia']['dp'], 1)}",
            "soma_vitimas": str(t1["soma_vitimas"]), "soma_distancia": f(t1["soma_distancia"], 1),
        },
        "comparacao": {
            "ag": {"dist": f(tot["ag"]["distancia"], 0), "custo": f(comp["custo_medio"]["ag"], 3)},
            "vmp_2opt": {"custo": f(comp["custo_medio"]["vmp_2opt"], 3)},
            "red_dist_vmp": pct(tot["vmp"]["distancia"], tot["ag"]["distancia"]),
            "red_dist_start": pct(tot["start"]["distancia"], tot["ag"]["distancia"]),
            "red_lat_vmp": pct(tot["vmp"]["latencia"], tot["ag"]["latencia"]),
            "red_lat_start": pct(tot["start"]["latencia"], tot["ag"]["latencia"]),
            "red_dist_2opt": pct(tot["vmp_2opt"]["distancia"], tot["ag"]["distancia"], 1),
            "start_vs_vmp": f(tot["start"]["distancia"] / tot["vmp"]["distancia"], 1),
            "n_aleatorias": str(comp["n_aleatorias"]),
            "chegada": {m: {c: f(v, 1) for c, v in comp["chegada_media_por_tri"][m].items()}
                        for m in comp["chegada_media_por_tri"]},
            "vm_ag_vs_vmp": pct(comp["chegada_media_por_tri"]["vmp"]["VM"], comp["chegada_media_por_tri"]["ag"]["VM"]),
            "vm_ag_vs_start": pct(comp["chegada_media_por_tri"]["start"]["VM"], comp["chegada_media_por_tri"]["ag"]["VM"]),
        },
        "semeadura": {"vit_puro": str(vitorias["puro"]), "vit_semeado": str(vitorias["semeado"]), "empates": str(vitorias["empate"]),
                      "melhor_puro": f(sem["custo_medio_melhor"]["puro"], 3),
                      "melhor_semeado": f(sem["custo_medio_melhor"]["semeado"], 3),
                      "final": f(sem["custo_medio_final"], 3),
                      "c2_puro": f(sem["por_parcela"][c2["parcela"]]["puro"]["melhor"], 3),
                      "c2_semeado": f(sem["por_parcela"][c2["parcela"]]["semeado"]["melhor"], 3),
                      "dp_puro": f(np.mean([v["puro"]["dp"] for v in sem["por_parcela"].values()]), 3),
                      "dp_semeado": f(np.mean([v["semeado"]["dp"] for v in sem["por_parcela"].values()]), 3),
                      "ger_puro": str(len(an["convergencia"]["puro"]["melhor_por_geracao"]) - 1),
                      "ger_semeado": str(len(an["convergencia"]["semeado"]["melhor_por_geracao"]) - 1)},
        "robustez": {"dp_max": f(max(dp_custos), 3), "dp_medio": f(float(np.mean(dp_custos)), 3),
                     "chamadas": f(float(np.mean([r["chamadas_fitness"]["media"] for r in rob.values()])), 0),
                     "geracoes": f(float(np.mean([r["geracoes"]["media"] for r in rob.values()])), 0),
                     "dp_zero": str(sum(1 for d in dp_custos if d < 1e-9))},
        "n_seq": str(len(sequencias)),
    }


def gerar_pdf():
    ENTREGA.mkdir(exist_ok=True)
    pdf = typst.compile(str(TEMPLATE), root=str(RAIZ),
                        sys_inputs={"dados": json.dumps(dados_relatorio(), ensure_ascii=False)})
    RELATORIO.write_bytes(pdf)


def copiar_clusters():
    destino = ENTREGA / "clusters"
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    arquivos = sorted(SAIDA_CLUSTERS.glob("cluster_*.txt"), key=lambda a: int(a.stem.split("_")[1]))
    for arquivo in arquivos:
        shutil.copy2(arquivo, destino / arquivo.name)
    with zipfile.ZipFile(CLUSTERS_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for arquivo in arquivos:
            _gravar(zf, f"clusters/{arquivo.name}", arquivo.read_bytes())


def _gravar(zf, nome, conteudo):
    info = zipfile.ZipInfo(nome, DATA_FIXA)
    info.external_attr = 0o644 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(info, conteudo)


def montar_zip():
    arquivos = []
    for item in CODIGO:
        caminho = RAIZ / item
        if caminho.is_dir():
            arquivos += [a for a in caminho.rglob("*") if a.is_file() and "__pycache__" not in a.parts]
        else:
            arquivos.append(caminho)
    with zipfile.ZipFile(CODIGO_FONTE, "w", zipfile.ZIP_DEFLATED) as zf:
        for arquivo in sorted(arquivos):
            _gravar(zf, f"{PASTA_NO_ZIP}/{arquivo.relative_to(RAIZ).as_posix()}", arquivo.read_bytes())


def main():
    gerar_pdf()
    copiar_clusters()
    montar_zip()
    for caminho in (RELATORIO, ENTREGA / "clusters", CLUSTERS_ZIP, CODIGO_FONTE):
        print(caminho.relative_to(RAIZ))


if __name__ == "__main__":
    main()
