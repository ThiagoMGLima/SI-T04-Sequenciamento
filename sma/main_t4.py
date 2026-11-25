"""Sistema multiagente da Tarefa 4: 5 socorristas no ambiente 75x75_410v do VictSim3.

Não há exploradores: o enunciado assume que o mapa da exploração já existe (map.csv, com tri e sobr
preditos na T3). O socorrista mestre (1) faz a atribuição; cada socorrista sequencia as suas parcelas
pelo AG e grava os seus cluster_<seq>.txt em clusters/. O laço do simulador (env.run) não é chamado,
porque o socorro em si não é executado nesta tarefa.

Saídas: clusters/cluster_1.txt ... cluster_n.txt e resultados/sequenciamento.json.
Uso: uv run python sma/main_t4.py   (depois de src/calibrar.py)
"""

import os
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
for pasta in ("src", "sma", "vendor/victsim3"):
    if str(RAIZ / pasta) not in sys.path:
        sys.path.insert(0, str(RAIZ / pasta))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from ag import ParametrosAG  # noqa: E402
from comum import CFG_SOCORRISTAS, DADOS_T3, LAMBDA, RESULTADOS, SAIDA_CLUSTERS, VICTSIM, ler_json, salvar_json  # noqa: E402
from socorrista import Socorrista  # noqa: E402
from vs.environment import Env  # noqa: E402

N_SOCORRISTAS = 5


class AmbienteT4(Env):
    """O Env do professor, sem modificação, exceto a leitura do env_config.txt: o do 75x75_410v
    escreve "BASE 30, 40" (com espaço), que o Env.__read_config original não lê (quebra o
    int("")). Aqui as palavras depois da chave são juntadas antes da conversão."""

    def _Env__read_config(self):
        with open(os.path.join(self.env_folder, "env_config.txt")) as arquivo:
            for linha in arquivo:
                palavras = linha.split()
                if not palavras:
                    continue
                chave, valor = palavras[0], "".join(palavras[1:])
                if chave == "BASE":
                    self.dic[chave] = [int(v) for v in valor.split(",")]
                elif chave == "DELAY":
                    self.dic[chave] = float(valor)
                else:
                    self.dic[chave] = int(valor)


def criar_socorristas():
    """Ambiente do cenário de referência e os 5 socorristas, que se conhecem entre si."""
    env = AmbienteT4(str(VICTSIM / "datasets" / "vict" / "410v"), str(VICTSIM / "datasets" / "env" / "75x75_410v"))
    socorristas = [Socorrista(env, str(CFG_SOCORRISTAS / f"soc_{i}.txt"), i) for i in range(1, N_SOCORRISTAS + 1)]
    for s in socorristas:
        s.set_rescuers(socorristas)
    return socorristas


def parametros_calibrados():
    calibracao = RESULTADOS / "calibracao.json"
    if not calibracao.exists():
        raise SystemExit("rode antes src/calibrar.py")
    return ParametrosAG(**ler_json(calibracao)["parametros_escolhidos"])


def main():
    parametros = parametros_calibrados()
    SAIDA_CLUSTERS.mkdir(exist_ok=True)
    for antigo in SAIDA_CLUSTERS.glob("cluster_*.txt"):
        antigo.unlink()
    socorristas = criar_socorristas()
    plano = socorristas[0].planejar_socorro(DADOS_T3 / "map_preenchido.csv", DADOS_T3, parametros, SAIDA_CLUSTERS)
    salvar_json(RESULTADOS / "sequenciamento.json", {"parametros": asdict(parametros), "lambda": LAMBDA, **plano})
    for numero, fila in plano["filas"].items():
        print(f"SOC_{numero}: {', '.join(fila)}")


if __name__ == "__main__":
    main()
