# Cada parcela roda o AG com população pura e com população semeada, e a mutação sai de calibração

O AG canônico do material (roleta, PMX, mutação por troca, pMUT = 0,05 por gene) ficou pior que o vizinho mais próximo nas parcelas grandes; a mutação por inserção (também do material, slide 35) foi a escolha que mais pesou, então o tipo de mutação, o pMUT e o tamanho da população saem de uma calibração. A semeadura com o vizinho mais próximo e a ordem START parecia a melhor saída num protótipo com 3 parcelas, mas com as 14 parcelas ela causa convergência prematura: o indivíduo do vizinho mais próximo toma a população e as execuções terminam quase no mesmo ponto. Sem semeadura, porém, a maior parcela (c2-adultos, 78 vítimas) não chega ao vizinho mais próximo. Por isso cada socorrista roda, em cada parcela, 10 execuções com população pura e 10 com população semeada e fica com a melhor das 20.

Com a calibração final (inserção, pMUT 0,005, N 100), a melhor execução pura venceu em 8 parcelas, a semeada em 1 (c2-adultos: 1,942 contra 2,057 da pura) e houve 5 empates; a média do melhor custo nas 14 parcelas é 1,830 só com a pura, 1,867 só com a semeada e 1,822 com as duas, contra 1,877 da subida de encosta 2-opt e 2 do vizinho mais próximo (resultados/analises.json, chave "semeadura").

## Considered Options

- Só semeada (decisão inicial): perde para a subida de encosta 2-opt.
- Só pura: na maior parcela fica acima (pior) que o vizinho mais próximo.
- Semente só do vizinho mais próximo ou só da ordem START: num teste exploratório (com a calibração anterior, só semeada), ambas ficaram piores que as duas populações juntas.
