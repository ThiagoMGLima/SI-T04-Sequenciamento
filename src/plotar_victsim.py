"""Sequências no grid com o programa do professor (VictSim3), sem modificá-lo, com
PLOTAR_SEQUENCIAMENTO = True: cada cluster_<seq>.txt é desenhado com uma cor e as vítimas são
ligadas na ordem de socorro (o programa não desenha a base; ela aparece em ciano).

O programa abre uma janela pygame em laço infinito. Aqui o vídeo é o driver "dummy" (sem janela) e
pygame.display.flip é trocado por uma função que salva o quadro e encerra o laço com um evento QUIT
(mesma técnica da T3). A saída de texto do programa (matriz de confusão da tri, MSE da sobr) vai
para resultados/plot_victsim_saida.txt.

Uso: uv run python src/plotar_victsim.py   (depois de sma/main_t4.py)
"""

import contextlib
import importlib.util
import io
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402  (precisa do SDL_VIDEODRIVER definido antes)

from comum import DADOS_T3, RESULTADOS, SAIDA_CLUSTERS, VICTSIM  # noqa: E402

PROGRAMA = VICTSIM / "data_vis_and_stats" / "plot_clusters_and_sequencing.py"
SAIDA_PNG = RESULTADOS / "sequencias_victsim.png"
SAIDA_TXT = RESULTADOS / "plot_victsim_saida.txt"


def carregar_programa():
    spec = importlib.util.spec_from_file_location("plot_clusters_and_sequencing", PROGRAMA)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    modulo.path_config = str(VICTSIM / "datasets" / "env" / "75x75_410v")
    modulo.path_vict = str(VICTSIM / "datasets" / "vict" / "410v")
    modulo.path_maps = str(DADOS_T3)
    modulo.map_file = "map_preenchido.csv"
    modulo.path_clusters = str(SAIDA_CLUSTERS)
    modulo.PLOTAR_SEQUENCIAMENTO = True
    return modulo


def main():
    if not any(SAIDA_CLUSTERS.glob("cluster_*.txt")):
        raise SystemExit("clusters/ vazio: rode antes sma/main_t4.py")
    programa = carregar_programa()
    flip_original = pygame.display.flip

    def salvar_e_sair():
        flip_original()
        pygame.image.save(pygame.display.get_surface(), str(SAIDA_PNG))
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    pygame.display.flip = salvar_e_sair
    RESULTADOS.mkdir(exist_ok=True)
    saida = io.StringIO()
    try:
        with contextlib.redirect_stdout(saida):
            programa.run()
    finally:
        pygame.display.flip = flip_original
    SAIDA_TXT.write_text(saida.getvalue(), encoding="utf-8")
    print(saida.getvalue())
    print(f"Imagem salva em {SAIDA_PNG}")


if __name__ == "__main__":
    main()
