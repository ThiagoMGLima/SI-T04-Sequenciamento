# Os clusters da T3 são divididos em parcelas, e cada parcela vira um `cluster_k.txt`

O enunciado manda cada socorrista "regravar os arquivos cluster_i.txt" na ordem de socorro, e o programa de plot do professor trata cada arquivo `cluster*` como um caminho. Seis dos sete clusters da T3 têm crianças, que os socorristas 3, 4 e 5 não podem socorrer, então um cluster não pode ser socorrido por um único socorrista de adultos. Dividimos cada cluster em parcela de adultos e parcela geral (crianças mais as vítimas-ruído anexadas), e cada parcela vira uma sequência, uma linha da Tabela 1 e um arquivo `cluster_k.txt`, com k = número da sequência. O `cluster_k.txt` da T4 não é o `cluster_k.txt` da T3: `sequencias.json` e o relatório dizem de qual cluster e parcela cada sequência veio.

## Considered Options

- Manter o número da T3 nas parcelas de adultos e numerar as gerais depois: daria a impressão de que `cluster_2.txt` ainda é o cluster 2 da T3, que perdeu as crianças.
- Um arquivo por socorrista: conflita com a Tabela 1 do enunciado, que separa as colunas Seq. e Agente (um agente pode ter várias sequências).
