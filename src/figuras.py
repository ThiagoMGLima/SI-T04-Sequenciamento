"""Figuras do relatório, a partir de resultados/sequenciamento.json e resultados/analises.json.

- fig_sequencias.png: uma miniatura do grid por sequência (pequenos múltiplos), com a base, o
  trajeto (base -> vítimas -> base) e as vítimas por tri. As cores START são do domínio e não separam
  vermelho de verde para daltônicos, por isso a forma do marcador também codifica a tri.
- fig_comparacao.png: distância total e latência ponderada total por método.
- fig_lambda.png: varredura de λ (distância total × latência ponderada total).
- fig_convergencia.png: melhor e média do custo por geração, população pura × semeada.
- fig_socorristas.png: custo de viagem por socorrista, T4 × atribuição da T3, com o TLIM.

Uso: uv run python src/figuras.py   (depois de src/analises.py)
"""

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from comum import BASE, DADOS_T3, RESULTADOS, ler_json  # noqa: E402
from parcelas import carregar_vitimas  # noqa: E402

# Paleta de referência (skill dataviz): slots categóricos 1 e 2; textos e grade neutros.
SERIE_1, SERIE_2 = "#257de0", "#f47230"
TEXTO, TEXTO_2, GRADE = "#191919", "#666666", "#e6e6e6"
PAREDE, DIFICIL = "#cfcfcf", "#f1f1f1"
# Triagem START (cores do domínio) com forma como segunda codificação.
TRI = {2: ("vermelho", "#d93a3a", "^"), 1: ("amarelo", "#e3ad00", "s"),
       0: ("verde", "#1f9e3a", "o"), 3: ("preto", "#2b2b2b", "X")}
NOMES_METODO = {"aleatoria": "Ordem aleatória (média de {n})", "start": "Ordem START (T3)",
                "vmp": "Vizinho mais próximo", "vmp_2opt": "VMP + 2-opt (subida de encosta)",
                "ag": "AG (T4)"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": TEXTO_2, "axes.labelcolor": TEXTO,
    "xtick.color": TEXTO_2, "ytick.color": TEXTO_2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "legend.frameon": False, "figure.dpi": 200,
})


def salvar(fig, nome):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=200, bbox_inches="tight", metadata={"Software": None})
    plt.close(fig)
    (RESULTADOS / nome).write_bytes(buffer.getvalue())


def fig_sequencias(vitimas, sequencias):
    mapa = pd.read_csv(DADOS_T3 / "map_preenchido.csv")
    mapa["x"], mapa["y"] = mapa["x_rel"] + BASE[0], mapa["y_rel"] + BASE[1]
    paredes = mapa[mapa["obst"] >= 100]
    dificeis = mapa[(mapa["obst"] > 1) & (mapa["obst"] < 100)]

    fig, eixos = plt.subplots(3, 5, figsize=(7.1, 4.6))
    for ax in eixos.flat:
        ax.set_xlim(-0.5, 74.5)
        ax.set_ylim(74.5, -0.5)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for lado in ax.spines.values():
            lado.set_visible(True)
            lado.set_color(GRADE)
    for ax, s in zip(eixos.flat, sequencias):
        ax.scatter(dificeis["x"], dificeis["y"], s=0.6, marker="s", color=DIFICIL, linewidths=0)
        ax.scatter(paredes["x"], paredes["y"], s=0.9, marker="s", color=PAREDE, linewidths=0)
        v = vitimas.loc[s["ids"]]
        xs = [BASE[0], *v["x"], BASE[0]]
        ys = [BASE[1], *v["y"], BASE[1]]
        ax.plot(xs, ys, color=SERIE_1, linewidth=0.8, alpha=0.9, zorder=2)
        for t, (_, cor, marcador) in TRI.items():
            g = v[v["tri"] == t]
            ax.scatter(g["x"], g["y"], s=7, marker=marcador, color=cor, edgecolors="white",
                       linewidths=0.3, zorder=3)
        ax.scatter([BASE[0]], [BASE[1]], s=22, marker="D", color=TEXTO, edgecolors="white", linewidths=0.6, zorder=4)
        ax.set_title(f"Seq. {s['seq']} · SOC {s['socorrista']}\n{s['parcela']} · d = {s['distancia']:.0f}",
                     fontsize=6.5, color=TEXTO, pad=2, linespacing=1.1)
    legenda = eixos.flat[-1]
    legenda.axis("off")
    for t, (nome, cor, marcador) in TRI.items():
        legenda.scatter([], [], s=16, marker=marcador, color=cor, label=nome)
    legenda.scatter([], [], s=22, marker="D", color=TEXTO, label=f"base ({BASE[0]}, {BASE[1]})")
    legenda.plot([], [], color=SERIE_1, linewidth=1, label="sequência")
    legenda.scatter([], [], s=10, marker="s", color=PAREDE, label="parede")
    legenda.legend(loc="center", fontsize=6.5, title="tri predita", title_fontsize=6.5)
    fig.subplots_adjust(wspace=0.05, hspace=0.32)
    salvar(fig, "fig_sequencias.png")


def fig_comparacao(comparacao):
    ordem = ["aleatoria", "start", "vmp", "vmp_2opt", "ag"]
    fig, eixos = plt.subplots(1, 2, figsize=(7.1, 1.9), sharey=True)
    for ax, (chave, titulo) in zip(eixos, [("distancia", "Distância total (células)"),
                                          ("latencia", "Latência ponderada total")]):
        valores = [comparacao["totais"][m][chave] for m in ordem]
        y = np.arange(len(ordem))
        ax.barh(y, valores, height=0.62, color=SERIE_1)
        for yi, v in zip(y, valores):
            ax.text(v, yi, f" {v:,.0f}".replace(",", "."), va="center", fontsize=7, color=TEXTO)
        ax.set_yticks(y, [NOMES_METODO[m].format(n=comparacao["n_aleatorias"]) for m in ordem])
        ax.set_title(titulo, fontsize=8, color=TEXTO, loc="left")
        ax.grid(axis="y", visible=False)
        ax.set_xlim(0, max(valores) * 1.2)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
    for rotulo in eixos[0].get_yticklabels():
        if rotulo.get_text() == NOMES_METODO["ag"]:
            rotulo.set_fontweight("bold")
    fig.tight_layout(w_pad=1.5)
    salvar(fig, "fig_comparacao.png")


def fig_lambda(varredura):
    linhas = varredura["linhas"]
    x = [l["distancia_total"] for l in linhas]
    y = [l["latencia_total"] for l in linhas]
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    ax.plot(x, y, color=SERIE_1, linewidth=2, marker="o", markersize=5, markeredgecolor="white")
    for l, xi, yi in zip(linhas, x, y):
        ax.annotate(f"λ = {l['lambda']:g}", (xi, yi), textcoords="offset points", xytext=(5, 3),
                    fontsize=7, color=TEXTO)
    ax.set_xlabel("distância total (células)")
    ax.set_ylabel("latência ponderada total")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
    ax.set_xlim(min(x) - 20, max(x) + 45)
    salvar(fig, "fig_lambda.png")


def fig_convergencia(convergencia, lam):
    fig, ax = plt.subplots(figsize=(3.6, 2.3))
    for ini, cor, rotulo in (("puro", SERIE_1, "pura"), ("semeado", SERIE_2, "semeada")):
        h = convergencia[ini]
        geracoes = np.arange(len(h["melhor_por_geracao"]))
        ax.plot(geracoes, h["media_por_geracao"], color=cor, linewidth=1, linestyle="--", alpha=0.8,
                label=f"média, população {rotulo}")
        ax.plot(geracoes, h["melhor_por_geracao"], color=cor, linewidth=2, label=f"melhor, população {rotulo}")
        ax.annotate(f"{h['melhor_por_geracao'][-1]:.3f}".replace(".", ","),
                    (geracoes[-1], h["melhor_por_geracao"][-1]), textcoords="offset points",
                    xytext=(0, 5) if ini == "puro" else (0, -10), ha="right", fontsize=7, color=TEXTO)
    # O custo é normalizado pela sequência do vizinho mais próximo, que vale sempre 1 + λ.
    referencia = 1 + lam
    ax.axhline(referencia, color=TEXTO_2, linewidth=0.8, linestyle=":")
    ax.text(len(convergencia["puro"]["melhor_por_geracao"]) * 0.5, referencia, f"vizinho mais próximo = {referencia:g}",
            fontsize=6.5, color=TEXTO_2, va="bottom", ha="center")
    ax.set_xlabel("geração")
    ax.set_ylabel(f"custo ({convergencia['parcela']})")
    ax.set_ylim(1.85, 3.2)
    ax.legend(fontsize=6.5, loc="upper right")
    salvar(fig, "fig_convergencia.png")


def fig_socorristas(socorristas):
    t4, t3 = socorristas["t4"]["por_socorrista"], socorristas["t3_atribuicao_com_ag"]["por_socorrista"]
    numeros = sorted(int(s) for s in t4)
    x = np.arange(len(numeros))
    largura = 0.38
    fig, ax = plt.subplots(figsize=(3.6, 2.3))
    for deslocamento, plano, cor, rotulo in ((-largura / 2 - 0.01, t3, SERIE_2, "atribuição da T3 (LPT)"),
                                             (largura / 2 + 0.01, t4, SERIE_1, "atribuição da T4")):
        valores = [plano[str(n)]["custo_viagem"] for n in numeros]
        ax.bar(x + deslocamento, valores, width=largura, color=cor, label=rotulo)
        for xi, v in zip(x + deslocamento, valores):
            ax.text(xi, v + 8, f"{v:.0f}", ha="center", fontsize=6, color=TEXTO)
    tlim = socorristas["tlim"]
    ax.axhline(tlim, color=TEXTO, linewidth=0.9, linestyle="--", label=f"TLIM = {tlim:.0f}")
    ax.set_xticks(x, [f"SOC {n}" for n in numeros])
    ax.set_ylabel("custo de viagem (distância + socorro)")
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, max(max(v["custo_viagem"] for v in t3.values()), max(v["custo_viagem"] for v in t4.values())) * 1.25)
    ax.legend(fontsize=6.5, loc="upper left", ncols=3, handlelength=1.5, columnspacing=1)
    salvar(fig, "fig_socorristas.png")


def main():
    vitimas = carregar_vitimas(DADOS_T3 / "map_preenchido.csv")
    seq = ler_json(RESULTADOS / "sequenciamento.json")
    sequencias = seq["sequencias"]
    analises = ler_json(RESULTADOS / "analises.json")
    fig_sequencias(vitimas, sequencias)
    fig_comparacao(analises["comparacao"])
    fig_lambda(analises["lambda"])
    fig_convergencia(analises["convergencia"], seq["lambda"])
    fig_socorristas(analises["socorristas"])
    print("figuras em", RESULTADOS)


if __name__ == "__main__":
    main()
