# Sequenciamento do socorro

Atribuir as vítimas agrupadas na Tarefa 3 aos 5 socorristas e definir, por algoritmo genético, a ordem em que cada socorrista as socorre (Tarefa 4 de Sistemas Inteligentes, UTFPR, cenário 75x75_410v).

## Vítimas

**Vítima**:
Pessoa atingida pela catástrofe, identificada pelo `id` do `map.csv`, com posição, idade, `tri` e `sobr` (estes dois preditos na T3).
_Avoid_: paciente

**Criança**:
Vítima com até 12 anos. Só os socorristas gerais podem socorrê-la.
_Avoid_: menor

**Vítima-ruído**:
Vítima que o DBSCAN da T3 não colocou em nenhum cluster (está em `ruido.txt`).
_Avoid_: outlier, vítima isolada

**Peso de urgência**:
Número que mede o quanto a vítima ganha com um socorro rápido: a faixa da classe START (vermelho > amarelo > verde > preto) ajustada, dentro da faixa, pela chance de não sobreviver (1 − sobr).
_Avoid_: prioridade (ambíguo), gravidade

## Socorristas e atribuição

**Socorrista geral**:
Socorristas 1 e 2, que socorrem vítimas de qualquer idade.

**Socorrista de adultos**:
Socorristas 3, 4 e 5, que só socorrem vítimas com mais de 12 anos.
_Avoid_: socorrista restrito

**Socorrista mestre**:
O socorrista 1, que além de socorrer faz a atribuição e informa cada socorrista das suas parcelas.

**Cluster da T3**:
Um dos 7 agrupamentos produzidos pelo DBSCAN na Tarefa 3 (`cluster_1.txt` a `cluster_7.txt` da T3).
_Avoid_: agrupamento (sozinho, quando houver risco de confundir com parcela)

**Parcela**:
Parte de um cluster da T3 entregue a um único socorrista: a parcela de adultos (vítimas do cluster com mais de 12 anos) ou a parcela geral (crianças do cluster mais as vítimas-ruído anexadas a ele).
_Avoid_: pacote, subcluster

**Atribuição**:
A escolha de qual socorrista recebe cada parcela.

**Fila do socorrista**:
A ordem em que um socorrista atende as suas parcelas.

## Sequenciamento

**Sequência**:
A ordem de socorro das vítimas de uma parcela, percorrida numa viagem que sai da base e volta a ela. Cada sequência é uma linha da Tabela 1 e um arquivo `cluster_k.txt` da saída, com k = número da sequência.
_Avoid_: rota (sozinho), trajeto, tour

**Distância da sequência**:
Soma das distâncias euclidianas, sem obstáculos, da base à primeira vítima, entre vítimas consecutivas e da última vítima à base.

**Tempo de chegada**:
Estimativa de quando o socorrista chega a uma vítima: a distância percorrida desde a base mais o custo de primeiros socorros das vítimas já atendidas na sequência.

**Latência ponderada**:
Soma, sobre as vítimas da sequência, do peso de urgência vezes o tempo de chegada. Mede o quanto as vítimas urgentes esperam.
_Avoid_: tempo de espera, atraso

**Custo da sequência**:
O que o algoritmo genético minimiza: a distância e a latência ponderada da sequência, cada uma dividida pelo valor da sequência do vizinho mais próximo, somadas com o peso λ na latência.
_Avoid_: fitness (o fitness é o inverso do custo), aptidão (idem)

**Makespan**:
O maior custo total de viagem entre os socorristas: como o socorro é em paralelo, é quando termina o último socorrista.
_Avoid_: tempo total

## Algoritmo genético

**Indivíduo**:
Uma permutação das vítimas de uma parcela (codificação posicional: o gene na posição i é a i-ésima vítima socorrida).
_Avoid_: cromossomo (sinônimo aceito no material, mas use um só)

**Semeadura**:
Pôr na população inicial indivíduos vindos de heurísticas (vizinho mais próximo e ordem START) em vez de só permutações aleatórias.

**Ordem START**:
A ordem de socorro da T3: vermelho, amarelo, verde, preto; na mesma cor, crianças e idosos primeiro e depois menor sobr.
