"""Conferência automática da entrega (observacoes.md, item 16).

1. Cada número usado pelo relatório (os valores que src/gerar_relatorio.py passa ao Typst) aparece no
   texto do PDF (extraído com pdftotext).
2. Os arquivos entrega/clusters/cluster_k.txt são iguais aos gravados pelos socorristas, têm um id
   por linha e cobrem as 410 vítimas uma única vez; nenhuma criança está com os socorristas 3 a 5;
   a distância de cada arquivo, recalculada do zero, bate com a Tabela 1.
3. O zip do código não contém o VictSim3 e o zip dos clusters tem os mesmos arquivos.

Uso: uv run python src/conferir_entrega.py   (depois de src/gerar_relatorio.py)
"""

import re
import subprocess
import zipfile

import numpy as np

from comum import BASE, DADOS_T3, IDADE_MAX_CRIANCA, N_VITIMAS, RESULTADOS, SAIDA_CLUSTERS, SOCORRISTAS_ADULTOS, ler_json
from gerar_relatorio import CLUSTERS_ZIP, CODIGO_FONTE, ENTREGA, RELATORIO, TEMPLATE, dados_relatorio
from parcelas import carregar_vitimas


def folhas(valor):
    if isinstance(valor, dict):
        for v in valor.values():
            yield from folhas(v)
    elif isinstance(valor, list):
        for v in valor:
            yield from folhas(v)
    elif isinstance(valor, str):
        yield valor


def ponto_e_virgula_engolido():
    """No Typst, um ";" logo depois de #expr encerra a expressão e some do texto: tem de ser \\;."""
    return [m.group(0) for m in re.finditer(r"#d\.[\w.]+;", TEMPLATE.read_text(encoding="utf-8"))]


def numeros_no_pdf():
    texto = subprocess.run(["pdftotext", str(RELATORIO), "-"], capture_output=True, text=True, check=True).stdout
    texto = re.sub(r"\s+", " ", texto)
    # Sem sinal: o texto diz "reduz em 13%" para a variação −13.
    return sorted({v for v in folhas(dados_relatorio()) if re.search(r"\d", v) and v.replace("−", "") not in texto})


def conferir_clusters():
    vitimas = carregar_vitimas(DADOS_T3 / "map_preenchido.csv")
    tabela = {l["seq"]: l for l in ler_json(RESULTADOS / "analises.json")["tabela_1"]["linhas"]}
    agentes = {s["seq"]: s["socorrista"] for s in ler_json(RESULTADOS / "sequenciamento.json")["sequencias"]}
    arquivos = sorted((ENTREGA / "clusters").glob("cluster_*.txt"), key=lambda a: int(a.stem.split("_")[1]))
    erros, todos = [], []
    for arquivo in arquivos:
        k = int(arquivo.stem.split("_")[1])
        if arquivo.read_bytes() != (SAIDA_CLUSTERS / arquivo.name).read_bytes():
            erros.append(f"{arquivo.name} difere do gravado pelo socorrista")
        linhas = arquivo.read_text(encoding="utf-8").splitlines()
        if not all(re.fullmatch(r"\d+", l) for l in linhas):
            erros.append(f"{arquivo.name}: linha que não é um id")
        ids = [int(l) for l in linhas]
        todos += ids
        if agentes[k] in SOCORRISTAS_ADULTOS and (vitimas.loc[ids, "idade"] <= IDADE_MAX_CRIANCA).any():
            erros.append(f"{arquivo.name}: criança com o socorrista {agentes[k]}")
        pontos = np.vstack([BASE, vitimas.loc[ids, ["x", "y"]].to_numpy(float), BASE])
        distancia = float(np.hypot(*np.diff(pontos, axis=0).T).sum())
        if abs(distancia - tabela[k]["distancia"]) > 1e-6:
            erros.append(f"{arquivo.name}: distância {distancia:.4f} ≠ Tabela 1 {tabela[k]['distancia']:.4f}")
    if len(todos) != N_VITIMAS or len(set(todos)) != N_VITIMAS or set(todos) != set(vitimas.index):
        erros.append(f"as sequências cobrem {len(set(todos))} vítimas distintas em {len(todos)} linhas")
    if sorted(tabela) != list(range(1, len(arquivos) + 1)):
        erros.append("número de arquivos diferente do número de linhas da Tabela 1")
    return erros, len(arquivos)


def conferir_zips():
    erros = []
    with zipfile.ZipFile(CODIGO_FONTE) as zf:
        nomes = zf.namelist()
        if zf.testzip() is not None:
            erros.append("codigo_fonte: CRC inválido")
    if any("vendor/" in n or "/vs/" in n for n in nomes):
        erros.append("o zip do código contém o VictSim3")
    with zipfile.ZipFile(CLUSTERS_ZIP) as zf:
        for nome in zf.namelist():
            if zf.read(nome) != (ENTREGA / nome).read_bytes():
                erros.append(f"clusters.zip: {nome} difere de entrega/{nome}")
    return erros, len(nomes)


def main():
    faltando = numeros_no_pdf()
    engolidos = ponto_e_virgula_engolido()
    print(f"';' engolidos pelo Typst: {engolidos or 'nenhum'}")
    erros_clusters, n_arquivos = conferir_clusters()
    erros_zip, n_zip = conferir_zips()
    print(f"Números do relatório ausentes do PDF: {faltando or 'nenhum'}")
    print(f"Arquivos de sequência conferidos: {n_arquivos}; erros: {erros_clusters or 'nenhum'}")
    print(f"Zip do código: {n_zip} arquivos; erros: {erros_zip or 'nenhum'}")
    if faltando or engolidos or erros_clusters or erros_zip:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
