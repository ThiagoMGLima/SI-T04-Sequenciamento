"""Caminhos e constantes compartilhados pela Tarefa 4."""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS_T3 = RAIZ / "dados" / "t3"
RESULTADOS = RAIZ / "resultados"
SAIDA_CLUSTERS = RAIZ / "clusters"
VICTSIM = RAIZ / "vendor" / "victsim3"
CFG_SOCORRISTAS = RAIZ / "sma" / "cfg"

# Base do ambiente 75x75_410v (env_config.txt): as coordenadas do map.csv são relativas a ela.
BASE = (30, 40)
N_VITIMAS = 410
IDADE_MAX_CRIANCA = 12          # socorristas 3, 4 e 5 só socorrem vítimas com idade > 12
SOCORRISTAS_GERAIS = (1, 2)     # todas as idades
SOCORRISTAS_ADULTOS = (3, 4, 5)
CUSTO_SOCORRO = 1.0             # COST_FIRST_AID dos configs de socorrista do professor
LAMBDA = 1.0                    # peso da latência ponderada no custo da sequência (observacoes.md, item 10)
SEMENTE = 42


def salvar_json(caminho, dados):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ler_json(caminho):
    return json.loads(caminho.read_text(encoding="utf-8"))
