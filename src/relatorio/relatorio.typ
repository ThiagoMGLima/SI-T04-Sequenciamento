// Relatório da Tarefa 4 (sequenciamento do socorro). Gerado por src/gerar_relatorio.py, que passa
// todos os números já formatados em sys.inputs.dados (JSON). O texto fica aqui; os números vêm de
// resultados/*.json e das entradas da T3 (dados/t3/).
#let d = json(bytes(sys.inputs.dados))

// ------------------------------------------------------------------ estilo (fichas de defesa T1/T2)
#let azul = rgb("#2a78d6")
#let azul-escuro = rgb("#1c5cab")
#let azul-claro = rgb("#eef4fc")
#let laranja-escuro = rgb("#b4471c")
#let laranja-claro = rgb("#fdf1eb")
#let verde-escuro = rgb("#1f7a4d")
#let verde-claro = rgb("#ecf7f1")
#let tinta = rgb("#0b0b0b")
#let tinta2 = rgb("#52514e")
#let linha = rgb("#d9d8d4")
#let fundo = rgb("#f4f4f2")
#let sans = "Noto Sans"

#set document(title: "Tarefa 4: Sequenciamento de socorro", author: "Thiago Moreira Gomes de Lima", date: none)
#set page(
  paper: "a4",
  margin: (x: 2.1cm, top: 2.2cm, bottom: 2.1cm),
  header: context {
    if counter(page).get().first() > 1 {
      set text(font: sans, size: 7.5pt, fill: tinta2)
      [Tarefa 4 · Sequenciamento de socorro #h(1fr) Thiago Moreira Gomes de Lima · RA 2413108]
      v(-0.5em)
      line(length: 100%, stroke: 0.4pt + linha)
    }
  },
  footer: context {
    set text(font: sans, size: 7.5pt, fill: tinta2)
    h(1fr)
    counter(page).display("1 / 1", both: true)
    h(1fr)
  },
)
#set text(font: "Libertinus Serif", size: 11pt, lang: "pt", region: "br", fill: tinta)
#set par(justify: true, leading: 0.58em, spacing: 0.9em)
#set list(indent: 0.6em, spacing: 0.6em)
#set enum(indent: 0.6em, spacing: 0.6em)
#set heading(numbering: "1.1")
#show heading: set text(font: sans, fill: tinta)
#show heading.where(level: 1): it => block(above: 1.4em, below: 0.8em, {
  text(size: 9pt, fill: azul, weight: "bold", counter(heading).display(it.numbering))
  h(0.5em)
  text(size: 14pt, weight: "bold", it.body)
})
#show heading.where(level: 2): it => block(above: 1.2em, below: 0.6em, text(size: 11pt, weight: "bold", it))
#show raw: set text(font: "DejaVu Sans Mono", size: 8.5pt)
#show raw.where(block: false): box.with(fill: fundo, inset: (x: 2pt), outset: (y: 2.5pt), radius: 2pt)
#show table: set text(font: sans, size: 8pt)
#show table: set par(justify: false, leading: 0.45em)
#show figure.caption: set text(font: sans, size: 8pt, fill: tinta2)
#show figure.caption: set par(justify: false)
#show figure.where(kind: table): set figure.caption(position: top)
#set figure(gap: 0.5em)
#show figure: set block(above: 1.1em, below: 1.1em)
#show link: set text(fill: azul-escuro)

#let caixa(rotulo, cor, cor-fundo, corpo) = block(
  width: 100%, fill: cor-fundo, inset: (left: 11pt, right: 10pt, y: 7pt),
  stroke: (left: 2.5pt + cor), radius: (right: 3pt), breakable: false, above: 1em, below: 1em,
)[
  #text(font: sans, size: 7.5pt, weight: "bold", fill: cor, tracking: 0.05em, upper(rotulo))
  #v(-0.4em)
  #corpo
]
#let destaque(corpo) = caixa("Em resumo", azul-escuro, azul-claro, corpo)
#let limitacao(corpo) = caixa("Limitação", laranja-escuro, laranja-claro, corpo)
#let conferido(corpo) = caixa("Conferido", verde-escuro, verde-claro, corpo)

#let tile(rotulo, valor, nota) = block(fill: fundo, radius: 4pt, inset: (x: 9pt, y: 8pt), width: 100%)[
  #set par(justify: false)
  #text(font: sans, size: 7.5pt, fill: tinta2, rotulo)
  #v(-0.3em)
  #text(font: sans, size: 17pt, weight: "semibold", valor)
  #v(-0.55em)
  #text(font: sans, size: 7pt, fill: tinta2, nota)
]

// Tabela com filetes horizontais
#let tab(colunas, cabecalho, alinhar: auto, inset-y: 3.5pt, ..celulas) = table(
  columns: colunas,
  align: if alinhar == auto { (x, y) => if x == 0 { left + horizon } else { center + horizon } } else { alinhar },
  inset: (x: 4pt, y: inset-y),
  stroke: (x, y) => (top: if y == 0 { 0.8pt + tinta } else if y == 1 { 0.5pt + tinta } else { 0.3pt + linha }),
  table.header(..cabecalho.map(c => text(weight: "bold", c))),
  ..celulas,
  table.hline(stroke: 0.8pt + tinta),
)
#let fig(caminho) = "/resultados/" + caminho
#let sem-sinal(x) = x.replace("−", "")

// ------------------------------------------------------------------ título
#block(below: 1.2em)[
  #text(font: sans, size: 8.5pt, fill: azul, weight: "bold", tracking: 0.04em)[SISTEMAS INTELIGENTES · UTFPR/CURITIBA · PROF. TACLA]
  #v(-0.3em)
  #text(font: sans, size: 21pt, weight: "bold")[Tarefa 4: Sequenciamento de socorro]
  #v(-0.5em)
  #text(font: sans, size: 10pt, fill: tinta2)[Thiago Moreira Gomes de Lima · RA 2413108 · cenário 75x75_410v, base (#d.base), 5 socorristas]
]

#grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 7pt,
  tile[Distância total][#d.comparacao.ag.dist][células, #d.n_seq sequências (#d.comparacao.red_dist_start% × ordem START)],
  tile[Makespan][#d.makespan.t4][#d.makespan.red_t3_ag% × atribuição da T3, mesmas sequências],
  tile[Custo médio do AG][#d.comparacao.ag.custo][vizinho mais próximo = #d.custo_vmp\; 2-opt = #d.comparacao.vmp_2opt.custo],
  tile[Vítimas sequenciadas][#d.tabela_1.soma_vitimas][#d.t3.ruido_vermelhas das #d.t3.vermelhas vermelhas vinham do ruído],
)

Cada socorrista recebe parcelas dos clusters da Tarefa 3 e ordena as vítimas de cada parcela com um algoritmo genético (AG) que minimiza, ao mesmo tempo, a distância percorrida e a espera das vítimas mais urgentes. A atribuição e o sequenciamento rodam dentro de 5 agentes socorristas no VictSim3, como recomenda o enunciado; cada agente grava os seus `cluster_k.txt`, um por sequência.

= Estratégia de socorro

== Agrupamento

O agrupamento é o da Tarefa 3, sem alterações. A `tri` e a `sobr` das #d.n_vitimas vítimas do `map.csv` vieram ocultas (−1) e foram preditas pelos melhores modelos das tarefas anteriores: a rede neural da T1 para a `tri` (acurácia #d.t3.acuracia contra o gabarito, medida pelo programa de plot do professor) e a da T2 para a `sobr` (MSE #d.t3.mse). Resultado: #d.t3.tri.VD verdes, #d.t3.tri.AM amarelas, #d.t3.tri.VM vermelhas e #d.t3.tri.PR pretas; #d.t3.criancas vítimas têm até #d.idade_crianca anos.

- *Critério*: posição e probabilidade de sobrevivência, (#d.t3.features), padronizadas (z-score). A intuição: grupos espacialmente compactos (menos deslocamento) e de urgência homogênea (a ordem entre grupos vira priorização real). A `sobr` foi preferida à `tri` por ser contínua e graduar a gravidade dentro de uma mesma cor.
- *Algoritmo*: DBSCAN, porque o espaço mistura regiões não convexas (um arco e faixas curvas) com vítimas esparsas, e o DBSCAN aceita formas arbitrárias e separa o ruído. Parametrização escolhida na T3: eps = #d.t3.eps, min_samples = #d.t3.min_samples (silhueta sem ruído #d.t3.silhueta, cobertura #d.t3.cobertura, Score final #d.t3.score).
- *Número de grupos variável*: definido pela densidade. Saíram #d.t3.clusters clusters (#d.t3.tamanhos vítimas) e #d.t3.ruido vítimas-ruído, isoladas entre as regiões densas. O ruído concentra #d.t3.ruido_vermelhas das #d.t3.vermelhas vítimas vermelhas, então ele não pode ficar sem socorro: cada vítima-ruído é anexada ao cluster da vítima agrupada mais próxima (empate: menor id), como prometido na T3.

== Atribuição e coordenação

*Parcelas.* Os socorristas 3, 4 e 5 só socorrem vítimas com mais de #d.idade_crianca anos, e #d.t3.com_criancas dos #d.t3.clusters clusters têm crianças. Por isso cada cluster é dividido em duas *parcelas*: a de *adultos* (vítimas do cluster com mais de #d.idade_crianca anos), para um socorrista de adultos, e a *geral* (crianças do cluster mais o ruído anexado), para um socorrista geral (1 ou 2). São #d.n_seq parcelas; cada uma vira uma *sequência*, uma linha da Tabela 1 e um arquivo `cluster_k.txt`, com k = número da sequência. O `cluster_k.txt` da T4 não é o da T3 (Quadro 1 dá a correspondência).

*Socorro em paralelo.* Os 5 socorristas trabalham ao mesmo tempo, em conjuntos disjuntos de vítimas; cada um atende as suas parcelas em fila, voltando à base ao fim de cada uma. Como o socorro só termina quando termina o último socorrista (o *makespan*), a atribuição procura equilibrar o custo das viagens, e não só o número de vítimas, como fazia a regra LPT da T3.

*Como a atribuição é feita.* O socorrista 1 (mestre) estima o custo de viagem de cada parcela pela sequência do vizinho mais próximo (distância + #d.pesos.socorro por vítima socorrida) e escolhe a divisão ótima por *enumeração exaustiva*: as #d.enumeracao.adultos parcelas de adultos entre #d.enumeracao.soc_adultos socorristas (#d.enumeracao.soc_adultos#super[#d.enumeracao.adultos] = #d.enumeracao.comb_adultos divisões) e as #d.enumeracao.gerais gerais entre #d.enumeracao.soc_gerais (#d.enumeracao.soc_gerais#super[#d.enumeracao.gerais] = #d.enumeracao.comb_gerais). Critério: menor makespan; no empate, menor latência ponderada total (seção 1.3). Na fila de cada socorrista, as parcelas seguem a *regra de Smith* (1956): maior razão urgência total ÷ custo de viagem primeiro, que é a ordem ótima para minimizar a soma dos tempos de conclusão ponderados. Depois, cada socorrista recebe a sua fila (`do_rescue`), roda o AG em cada parcela e grava os seus arquivos.

#figure(
  tab((auto, auto, auto, 1fr, auto, auto, auto), ("Socorrista", "Tipo", "Seq.", "Parcelas (na ordem da fila)", "Vítimas", "Custo T4", "Custo T3"),
    ..d.socorristas.map(s => (s.socorrista, s.tipo, s.seqs, s.parcelas, s.vitimas,
      if s.excede { text(weight: "bold", s.custo) } else { s.custo }, s.custo_t3)).flatten()),
  caption: [Quadro 1: atribuição. `cK-adultos`/`cK-geral`: parcela do cluster K da T3. Custo de viagem = distância das sequências do AG + #d.pesos.socorro por vítima. "Custo T3": mesmo cálculo com a atribuição LPT da T3. Em negrito, acima do TLIM = #d.makespan.tlim dos configs do professor.],
  kind: table, supplement: none,
)

== Sequenciamento

A ordem de socorro de uma parcela deve atender primeiro quem mais ganha com a rapidez, mas sem fazer o socorrista atravessar o mapa à toa. A ordem START estrita da T3 (vermelhas, depois amarelas, verdes e pretas) ignora a geografia e percorre #d.comparacao.start_vs_vmp vezes a distância do vizinho mais próximo; pior, como anda tanto, até as vermelhas chegam mais tarde do que com o AG (seção 5.1). O critério da T4 junta as duas coisas:

- *Peso de urgência* de cada vítima: faixa da classe START mais um ajuste pela chance de não sobreviver, $w = "faixa"("tri") + #d.pesos.ajuste dot (1 - "sobr")$, com faixas vermelho #d.pesos.VM, amarelo #d.pesos.AM, verde #d.pesos.VD e preto #d.pesos.PR. As faixas não se sobrepõem: uma vermelha sempre pesa mais que uma amarela, e entre duas vermelhas pesa mais a de menor `sobr`. A preta (expectante) tem peso pequeno, mas maior que 0, para não virar apenas "caminho".
- *Tempo de chegada* $t_v$: distância percorrida desde a base até a vítima $v$ mais #d.pesos.socorro (custo de primeiros socorros dos configs do professor) por vítima já atendida.
- *Latência ponderada* $L = sum_v w_v t_v$: quanto as vítimas esperam, pesado pela urgência.
- *Custo da sequência*, minimizado pelo AG: $C = D \/ D_"VMP" + lambda dot L \/ L_"VMP"$, em que $D$ é a distância (base → vítimas → base) e os denominadores são os da sequência do vizinho mais próximo (VMP) da mesma parcela, que tornam os dois termos adimensionais e comparáveis entre parcelas (o VMP vale sempre $1 + lambda$). Usamos $lambda = #d.lambda$; a seção 5.3 mostra o efeito de outros valores.

= Algoritmo de sequenciamento

== Algoritmo e parametrização

Algoritmo genético, na forma do AG canônico do material da disciplina (seleção, reprodução por crossover e mutação, sobrevivência dos melhores entre pais e filhos), com os operadores para problemas de permutação. A parametrização final saiu de uma calibração (abaixo).

#figure(
  tab((auto, 1fr), ("Parâmetro", "Valor"), alinhar: left + horizon,
    [Tamanho da população (N) e da descendência (R)], [N = R = #d.ag.N],
    [Seleção], [roleta, fitness = 1/custo],
    [Crossover], [PMX, pCROSS = #d.ag.pc],
    [Mutação], [#d.ag.mutacao (por posição), pMUT = #d.ag.pm por gene],
    [Sobrevivência], [os N melhores entre pais e filhos],
    [Parada], [#d.ag.max_ger gerações ou #d.ag.estag gerações sem melhorar o melhor indivíduo],
    [Execuções por parcela], [#d.ag.sementes com população pura + #d.ag.sementes com população semeada; fica a melhor das #d.ag.execucoes],
  ),
  caption: [Quadro 2: parametrização do AG.], kind: table, supplement: none,
)

*Calibração.* O tipo de mutação (troca, inserção, embaralhamento) × pMUT (#d.calibracao.pms) × N (#d.calibracao.Ns), #d.calibracao.n_comb combinações, foram testados em #d.calibracao.n_parcelas parcelas de tamanhos diferentes (#d.calibracao.parcelas), com as duas populações iniciais e #d.calibracao.sementes sementes cada. Critério: menor custo médio; empate pelo menor número de chamadas da função de fitness (a medida de esforço do material). As #d.calibracao.n_top melhores combinações são #d.calibracao.top_mutacao\; a melhor com troca ficou em #d.calibracao.melhor_troca e a melhor com embaralhamento em #d.calibracao.melhor_emb. A troca de dois genes distantes desmancha trechos bons da sequência, enquanto a inserção só desloca uma vítima.

#figure(
  tab((auto, auto, auto, auto, auto), ("Mutação", "pMUT", "N", "Custo médio", "Chamadas de fitness"),
    ..d.calibracao.linhas.map(l => {
      let c(x) = if l.escolhida { text(weight: "bold", x) } else { x }
      (c(l.mutacao), c(l.pm), c(l.N), c(l.custo), c(l.chamadas))
    }).flatten()),
  caption: [Quadro 3: as #d.calibracao.n_top melhores combinações da calibração (em negrito, a escolhida).], kind: table, supplement: none,
)

== Modelagem

- *Indivíduo*: uma permutação das vítimas da parcela, em *codificação posicional* (o gene na posição $i$ é a $i$-ésima vítima socorrida). A base não entra no indivíduo: toda sequência sai dela e volta a ela.
- *Fitness*: $1\/C$, com o custo $C$ da seção 1.3; a roleta sorteia os pais com probabilidade proporcional ao fitness.
- *Crossover PMX*: sorteiam-se dois pontos; cada filho recebe o segmento do outro pai, herda o resto do próprio pai e troca as repetições pelo mapeamento entre os segmentos. O teste automatizado do operador reproduz o exemplo do material (pais 123456 e 235614 → filhos 325614 e 213456).
- *Mutação por inserção*: cada gene, com probabilidade pMUT, é retirado da sua posição e inserido numa posição sorteada (ABCDEF → ACDEBF, exemplo do material).
- *População inicial*: na *pura*, só permutações aleatórias; na *semeada*, um indivíduo do vizinho mais próximo, um da ordem START e os demais aleatórios. Cada parcela roda as duas (seção 5.2 explica por quê).
- *Indivíduos infactíveis*: não surgem. Das estratégias do material (rejeitar, reparar, penalizar ou modificar os operadores), usamos a de *operadores que preservam a factibilidade*: PMX e inserção sempre produzem permutações válidas (cada vítima uma única vez). A outra restrição, a de idade, é garantida antes do AG, pela construção das parcelas; o agente socorrista de adultos ainda recusa (erro) qualquer parcela com criança.

= Distância estimada do trajeto

Para cada sequência, a distância é a soma das distâncias euclidianas entre pontos consecutivos, $d = sqrt(Delta x^2 + Delta y^2)$, desconsiderando os obstáculos: da base (#d.base) à primeira vítima, entre vítimas consecutivas na ordem de socorro e da última vítima de volta à base, em células. A Tabela 1 traz a distância de cada sequência; somadas, são #d.tabela_1.soma_distancia células.

= Resultados

#figure(
  tab((auto, auto, auto, auto, auto, auto, auto, auto, auto, auto),
    ("Seq.", "Agente", "VD", "AM", "VM", "PR", "Total vítimas", "Distância trajeto", [$mu$ sobr], [$sigma$ sobr]),
    alinhar: center + horizon, inset-y: 2.4pt,
    ..d.tabela_1.linhas.map(l => (l.seq, l.agente, l.VD, l.AM, l.VM, l.PR, l.total, l.distancia, l.sobr_media, l.sobr_dp)).flatten(),
    [], [], [], [], [], [], [#text(weight: "bold", [$mu plus.minus sigma$]) \ #d.tabela_1.total], [#text(weight: "bold", [$mu plus.minus sigma$]) \ #d.tabela_1.distancia], [], [],
  ),
  caption: [Tabela 1: resultados de socorro. VD/AM/VM/PR: vítimas verdes, amarelas, vermelhas e pretas (tri predita); distância euclidiana da base à base; $mu$ e $sigma$: média e desvio padrão (populacional) da sobr; última linha: média ± desvio padrão entre as #d.n_seq sequências.],
  kind: table, supplement: none,
)

As sequências da Tabela 1 são as dos arquivos entregues (`cluster_1.txt` a #raw("cluster_" + d.n_seq + ".txt")): #d.tabela_1.soma_vitimas vítimas, cada uma em exatamente uma sequência. A Figura 1 mostra cada sequência no grid.

#figure(image(fig("fig_sequencias.png"), width: 100%),
  caption: [as #d.n_seq sequências no grid (uma miniatura por sequência; base em losango; paredes em cinza; cor e forma = tri predita; d = distância da Tabela 1).])

= Análises dos sequenciamentos

== O AG contra outras ordens

#figure(image(fig("fig_comparacao.png"), width: 100%),
  caption: [distância e latência ponderada, somadas nas #d.n_seq parcelas, por método. "Aleatória": média de #d.comparacao.n_aleatorias permutações.])

O AG reduz a distância total em #sem-sinal(d.comparacao.red_dist_vmp)% em relação ao vizinho mais próximo e em #sem-sinal(d.comparacao.red_dist_start)% em relação à ordem START da T3, e a latência ponderada em #sem-sinal(d.comparacao.red_lat_vmp)% e #sem-sinal(d.comparacao.red_lat_start)%. A ordem START, que prioriza só pela cor, fica quase tão ruim quanto uma ordem aleatória na distância. Como referência de busca local, a subida de encosta 2-opt a partir do vizinho mais próximo (inverte trechos da sequência enquanto o custo cai) chega a custo médio #d.comparacao.vmp_2opt.custo\; o AG chega a #d.comparacao.ag.custo e anda #sem-sinal(d.comparacao.red_dist_2opt)% menos.

#figure(
  tab((1fr, auto, auto, auto, auto), ("Método", "Vermelhas", "Amarelas", "Verdes", "Pretas"),
    ..(("ag", "AG (T4)"), ("vmp_2opt", "VMP + 2-opt"), ("vmp", "Vizinho mais próximo"), ("start", "Ordem START (T3)"), ("aleatoria", "Ordem aleatória")).map(((m, nome)) => {
      let c = d.comparacao.chegada.at(m)
      (nome, c.VM, c.AM, c.VD, c.PR)
    }).flatten()),
  caption: [Quadro 4: tempo médio de chegada às vítimas de cada cor (distância desde a saída da base mais o socorro das anteriores, dentro da parcela).], kind: table, supplement: none,
)

#destaque[Priorizar só pela cor custa caro: na ordem START as vítimas ficam juntas na fila, mas espalhadas no mapa, e as vermelhas chegam em média #d.comparacao.chegada.start.VM, contra #d.comparacao.chegada.ag.VM no AG (#d.comparacao.vm_ag_vs_start%). O AG de fato prioriza: as vermelhas chegam #sem-sinal(d.comparacao.vm_ag_vs_vmp)% antes que no vizinho mais próximo, enquanto verdes e pretas, menos urgentes, chegam um pouco depois.]

== População inicial e convergência

#grid(columns: (1fr, 1fr), gutter: 10pt,
  figure(image(fig("fig_convergencia.png"), width: 100%),
    caption: [melhor e média do custo por geração na maior parcela (#d.convergencia.parcela, #d.convergencia.n vítimas): melhor execução pura e melhor semeada.]),
  figure(image(fig("fig_lambda.png"), width: 100%),
    caption: [varredura de $lambda$ (#d.lambda_sementes sementes por população), distância × latência ponderada totais.]),
)

A semeadura com o vizinho mais próximo faz o AG convergir cedo: o indivíduo semeado é muito melhor que os aleatórios, toma a população pela roleta e pela sobrevivência dos melhores, e a busca para perto dele (na Figura 3, #d.semeadura.ger_semeado gerações, contra #d.semeadura.ger_puro da pura). Sem semente, a população é mais diversa e acha sequências melhores na maioria das parcelas: a melhor execução pura venceu em #d.semeadura.vit_puro parcelas, a semeada em #d.semeadura.vit_semeado e houve #d.semeadura.empates empates (parcelas pequenas). Na maior parcela, porém, a pura não chega ao vizinho mais próximo dentro de #d.ag.max_ger gerações (#d.semeadura.c2_puro contra #d.semeadura.c2_semeado da semeada). Por isso cada parcela roda as duas e fica a melhor: o custo médio da melhor execução é #d.semeadura.melhor_puro só com a pura, #d.semeadura.melhor_semeado só com a semeada e #d.semeadura.final com as duas.

*Robustez.* Entre as #d.ag.execucoes execuções de cada parcela, o desvio padrão do custo é em média #d.robustez.dp_medio (máximo #d.robustez.dp_max); em #d.robustez.dp_zero parcelas pequenas todas as execuções chegam à mesma sequência. O desvio médio é #d.semeadura.dp_puro nas execuções puras e #d.semeadura.dp_semeado nas semeadas. Cada execução faz em média #d.robustez.geracoes gerações e #d.robustez.chamadas chamadas da função de fitness.

== Peso da urgência ($lambda$)

Com $lambda = 0$ (o $lambda$ multiplica a latência, então zero a elimina do custo) o AG minimiza só a distância (o caixeiro-viajante); aumentar $lambda$ troca distância por menos espera das vítimas urgentes (Figura 4). De $lambda = #d.varredura.lam_min$ a $lambda = #d.varredura.lam_max$, a latência ponderada total cai #d.varredura.red_lat% e a distância #d.varredura.verbo_dist #d.varredura.var_dist%. O maior ganho vem do passo de $lambda = #d.varredura.passo_de$ a $lambda = #d.varredura.passo_ate$, que responde por #d.varredura.passo_fracao% da queda total da latência: uma pequena preferência pela urgência já reordena as vítimas sem alongar muito a sequência. Os pontos não são exatamente monotônicos porque cada um é o melhor de poucas execuções de um algoritmo estocástico.

== Socorristas, makespan e TLIM

#grid(columns: (1.05fr, 1fr), gutter: 12pt,
  figure(image(fig("fig_socorristas.png"), width: 100%),
    caption: [custo de viagem por socorrista, atribuição da T4 × LPT da T3, ambas com as sequências do AG.]),
  [
    #v(0.3em)
    Com as mesmas sequências do AG, a atribuição por enumeração reduz o makespan de #d.makespan.t3_ag para #d.makespan.t4 (#d.makespan.red_t3_ag%). A estratégia completa da T3 (LPT e ordem START) teria makespan #d.makespan.t3, então a T4 reduz o tempo de socorro em #sem-sinal(d.makespan.red_t3)% e a latência ponderada total de #d.makespan.lat_t3 para #d.makespan.lat_t4.

    Os configs de socorrista do professor dão TLIM = #d.makespan.tlim. O enunciado não pede o socorro nem limita o tempo, então o TLIM não entrou como restrição; mesmo assim, #d.makespan.n_excedem socorristas (#d.makespan.excedem) não terminariam dentro dele.
  ],
)

#limitacao[O makespan é dominado pelos socorristas gerais (1 e 2), que levam as #d.t3.criancas crianças *e* todas as #d.t3.ruido vítimas-ruído, das quais #d.t3.ruido_adultos são adultas e espalhadas pelo mapa. Mandar o ruído adulto para os socorristas 3, 4 e 5 equilibraria a carga; fica como trabalho futuro. Outras limitações: a distância euclidiana ignora paredes e terrenos difíceis (o custo real só é conhecido no planejamento do caminho, por exemplo com A\*), a atribuição usa custos estimados pelo vizinho mais próximo, e a `sobr` é tratada como fixa durante o socorro.]

== Sequências no programa do professor

#figure(image(fig("sequencias_victsim.png"), width: 55%),
  caption: [saída de `plot_clusters_and_sequencing.py` (VictSim3) com `PLOTAR_SEQUENCIAMENTO = True` e os #d.n_seq arquivos entregues. Cada cor é uma sequência, ligada na ordem de socorro (o programa não desenha a base, em ciano); X marca vítima com tri predita diferente do gabarito.])

#conferido[Os #d.n_seq arquivos `cluster_k.txt` têm um id por linha e cobrem as #d.tabela_1.soma_vitimas vítimas uma única vez; nenhuma criança está com os socorristas 3, 4 e 5. Esses fatos, os operadores (com os exemplos do material) e as fórmulas de custo são verificados por testes automatizados (`uv run pytest`). O VictSim3 foi usado sem nenhuma modificação: o `Env` do professor não lê o `env_config.txt` do cenário 75x75_410v (`BASE 30, 40`, com espaço), e os agentes usam uma subclasse que só substitui essa leitura.]

#v(0.6em)
#text(font: sans, size: 8pt, weight: "bold")[Referências]
#set text(size: 8.5pt)
#set par(spacing: 0.5em)

Tacla, C. A. Algoritmos genéticos; Penalização e reparação; Busca local. Material da disciplina Sistemas Inteligentes, UTFPR.

Tacla, C. A. VictSim3. https://github.com/tacla/VictSim3 (commit 803a01e).

Smith, W. E. Various optimizers for single-stage production. _Naval Research Logistics Quarterly_, 3(1–2), p. 59–66, 1956.

Goldberg, D. E.; Lingle, R. Alleles, loci, and the traveling salesman problem. _Proc. 1st Int. Conf. on Genetic Algorithms_, p. 154–159, 1985 (crossover PMX).
