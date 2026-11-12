# Avaliação do Desempenho de Cache via Simulação de Monte Carlo

**Atividade 3 — Arquitetura de Computadores**

---

## 1. Introdução e objetivo

Os acessos à memória de um programa real não seguem um padrão exato: há reutilização de dados recentes, vizinhança de endereços e regiões muito acessadas, mas também acessos imprevisíveis. Por isso, medir o desempenho de uma cache com **uma única execução** pode induzir a erro, já que o resultado depende do padrão aleatório sorteado naquela rodada.

O objetivo desta atividade é **analisar estatisticamente a variação do desempenho de uma cache frente a padrões aleatórios**, usando a **Simulação de Monte Carlo**: repetir o experimento muitas vezes (aqui, **100 simulações por cenário**) e estudar a distribuição da taxa de acerto (*hit rate*). Em particular, comparamos:

- a **distribuição** e a **média** da taxa de acerto;
- a **variância** (desvio padrão) entre simulações;
- o **desempenho em outliers** (piores e melhores casos);
- o efeito de diferentes **configurações de cache** (tamanho, associatividade, política de substituição e tamanho do bloco).

## 2. Metodologia

### 2.1 Simulador e modelo de carga

Usamos o simulador de memória cache em Python (`cache_simulator_GUI.py`), que implementa uma cache associativa por conjuntos com as políticas de substituição **FIFO, LRU, LFU e Random**. Cada simulação gera uma sequência de **10.000 acessos** a uma RAM de **1 MB** (1.048.576 B) pela função `gerar_padrao_realista()`, em que cada acesso é sorteado assim:

| Tipo de acesso | Probabilidade | Descrição |
|---|---:|---|
| Localidade temporal | 20% | repete o endereço anterior |
| Localidade espacial | 20% | endereço anterior ± até 16 bytes |
| Regiões quentes (*hot regions*) | 40% | um entre 9 endereços-base fixos (+0 a +3 bytes) |
| Aleatório puro | 20% | endereço uniforme em toda a RAM |

### 2.2 Simulação de Monte Carlo

A função `simulacao_monte_carlo()` executa **N = 100 simulações independentes** de cada cenário: a cada simulação um novo padrão de 10.000 acessos é sorteado, a cache é reiniciada e a taxa de acerto final é registrada. O conjunto das 100 taxas forma a **distribuição empírica** do cenário. Como o simulador não fixa semente, cada execução usa números aleatórios novos.

Como cada simulação é uma média de 10.000 acessos, o **erro-padrão da média** de um cenário é de apenas σ/√100 ≈ 0,0005 (IC 95% ≈ ±0,001). Assim, diferenças de média maiores que ~0,002 entre cenários já podem ser consideradas estatisticamente relevantes.

### 2.3 Métricas

Para cada cenário (100 simulações) foram registradas:

- **Média** da taxa de acerto;
- **Desvio padrão** e **variância** (`np.std` e `np.var`, com ddof = 0);
- **Mínimo** e **máximo**, a partir dos quais calculamos a **amplitude** e a **queda do pior caso** (média − mínimo, em pontos percentuais, pp);
- **Coeficiente de variação** (CV = desvio / média);
- **Número de outliers** pelo critério de Tukey (valores fora de [Q1 − 1,5·IQR ; Q3 + 1,5·IQR]).

### 2.4 Extensão (extra) implementada no simulador

Além do que a atividade pedia, **acrescentamos recursos ao simulador para mostrar a distribuição** das simulações dentro da própria interface:

1. **Nova aba "Boxplot (Distribuição)"**: a cada execução, um boxplot com as 100 taxas de acerto é adicionado ao gráfico (acumulando entre execuções para comparar configurações). Cada caixa mostra mediana, média (losango verde) e outliers (pontos vermelhos), e o gráfico pode ser exportado em PNG. Cada caixa é rotulada com a configuração, por exemplo `LRU | 16-way | 8KB | B128`.
2. **Console com estatísticas completas**: além da média, passou a exibir desvio padrão, variância, mínimo, máximo e número de outliers (Tukey), identificando política, associatividade, cache e bloco em cada linha.
3. **`simulacao_monte_carlo(..., retornar_taxas=True)`**: o parâmetro opcional devolve a lista com as 100 taxas (antes só a média era retornada), mantendo o comportamento original quando omitido.
4. **Validação de entradas** (configuração que resulta em menos de 1 conjunto) e **arquivos CSV nomeados pela configuração** (por exemplo, `Simulacao_LRU_16way_8192B_<data-hora>.csv`).

![Interface do simulador com a aba de boxplot e o console com média, desvio, variância, mínimo, máximo e outliers](figuras/fig1_gui_extra.png)
*Figura 1 — Interface do simulador com as extensões (aba "Boxplot (Distribuição)" e console com as estatísticas por bloco).*

### 2.5 Plano de experimentos

Em todas as fases: RAM 1 MB, 10.000 acessos por simulação, **100 simulações por cenário**, probabilidades 0,20 / 0,20 / 0,40. Em cada execução da interface variamos também o tamanho do bloco (2 a 128 B; na Fase 0, de 2 a 512 B), o que gera um cenário por bloco. As comparações principais usam o **bloco de 128 B como referência**.

| Fase | Pergunta | Configuração | Cenários |
|---|---|---|---:|
| 0 | Qual o efeito do tamanho do bloco? | 4 políticas, 16 vias, cache 8 KB, blocos 2–512 B | 36 |
| 1 | Qual o efeito da associatividade e da política? | 4 políticas × 2, 4, 8, 16 vias, cache 8 KB, blocos 2–128 B | 112 |
| 2 | Qual o efeito do tamanho da cache? | LRU, 16 e 2 vias, cache 2–32 KB, blocos 2–128 B | 70 |
| 3 | A política importa mais em cache pequena ou grande? | 4 políticas, 16 vias, cache 2 e 32 KB, blocos 2–128 B | 56 |
| | **Total** | | **274** |

No total, foram **27.400 simulações de Monte Carlo** (274.000.000 acessos de CPU simulados).

---

## 3. Resultados

### 3.1 Fase 0 — efeito do tamanho do bloco

Média da taxa de acerto (100 simulações por célula; cache 8 KB, 16 vias). Em negrito, o melhor bloco de cada política.

| Política | 2 B | 4 B | 8 B | 16 B | 32 B | 64 B | 128 B | 256 B | 512 B |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FIFO | 0,7138 | 0,7214 | 0,7330 | 0,7506 | **0,7631** | 0,7550 | 0,7317 | 0,6970 | 0,6321 |
| LRU | 0,7172 | 0,7320 | 0,7447 | 0,7629 | 0,7815 | **0,7844** | 0,7803 | 0,7591 | 0,6895 |
| LFU | 0,7169 | 0,7310 | 0,7455 | 0,7656 | 0,7839 | 0,7918 | **0,7943** | 0,7907 | 0,7691 |
| Random | 0,7143 | 0,7246 | 0,7349 | 0,7519 | **0,7643** | 0,7547 | 0,7330 | 0,6979 | 0,6341 |

![Taxa de acerto média em função do tamanho do bloco (escala log2), uma curva por política](figuras/fig2_fase0_curva.png)
*Figura 2 — Curva de desempenho: taxa de acerto média × tamanho do bloco (Fase 0).*

![Boxplots das 100 simulações para cada política e tamanho de bloco (Fase 0)](figuras/fig3_fase0_boxplot.png)
*Figura 3 — Distribuição das 100 simulações por cenário na Fase 0 (cada caixa = um cenário).*

A curva tem o formato clássico de "subida e queda". Blocos maiores trazem vizinhos junto com o dado pedido e aproveitam a **localidade espacial**, mas, com a cache de tamanho fixo, blocos grandes significam **menos linhas**. O melhor bloco depende da política: **32 B** para FIFO e Random, **64 B** para LRU e **128 B** para LFU. Com 512 B, a cache de 8 KB tem só 16 linhas (um único conjunto de 16 vias) e FIFO/Random caem para ≈ 0,632 e LRU para 0,690, enquanto o LFU mantém 0,769. Como as regiões quentes são fixas na nossa carga, é plausível que a contagem de frequência do LFU as preserve na cache enquanto as demais políticas as expulsam em meio ao tráfego espacial e aleatório (explicação coerente com os dados, mas não testada isoladamente).

Adotamos **128 B como bloco de referência** nas fases seguintes: nele as diferenças entre políticas ficam mais nítidas (LFU − FIFO = 6,3 pp, contra 3,7 pp em 64 B). Os resultados com 64 B estão no Apêndice A.

### 3.2 Fase 1 — associatividade × política (cache 8 KB, bloco 128 B)

| Política | Vias | Média | Desvio | Variância | Mínimo | Máximo | Outliers |
|---|---:|---:|---:|---:|---:|---:|---:|
| FIFO | 2 | 0,4964 | 0,0047 | 0,000022 | 0,4861 | 0,5082 | 3 |
| FIFO | 4 | 0,5831 | 0,0049 | 0,000024 | 0,5706 | 0,5951 | 0 |
| FIFO | 8 | 0,6733 | 0,0056 | 0,000031 | 0,6584 | 0,6884 | 0 |
| FIFO | 16 | 0,7330 | 0,0048 | 0,000023 | 0,7207 | 0,7435 | 0 |
| LRU | 2 | 0,4984 | 0,0052 | 0,000027 | 0,4874 | 0,5107 | 0 |
| LRU | 4 | 0,5881 | 0,0045 | 0,000020 | 0,5740 | 0,5972 | 0 |
| LRU | 8 | 0,6967 | 0,0055 | 0,000030 | 0,6842 | 0,7101 | 0 |
| LRU | 16 | 0,7802 | 0,0052 | 0,000027 | 0,7658 | 0,7926 | 0 |
| LFU | 2 | 0,5026 | 0,0053 | 0,000028 | 0,4916 | 0,5183 | 1 |
| LFU | 4 | 0,5989 | 0,0050 | 0,000025 | 0,5873 | 0,6126 | 1 |
| LFU | 8 | 0,7347 | 0,0046 | 0,000021 | 0,7266 | 0,7531 | 1 |
| LFU | 16 | 0,7940 | 0,0043 | 0,000018 | 0,7839 | 0,8048 | 0 |
| Random | 2 | 0,4947 | 0,0057 | 0,000032 | 0,4823 | 0,5090 | 0 |
| Random | 4 | 0,5820 | 0,0055 | 0,000030 | 0,5680 | 0,5966 | 0 |
| Random | 8 | 0,6733 | 0,0062 | 0,000038 | 0,6570 | 0,6866 | 2 |
| Random | 16 | 0,7331 | 0,0060 | 0,000036 | 0,7161 | 0,7503 | 4 |

*Tabela de dispersão da Fase 1 (média, desvio padrão, variância, mínimo, máximo e outliers de cada cenário, com 100 simulações cada).*

![Boxplots da Fase 1 — FIFO](figuras/fig4a_fase1_fifo.png)
*Figura 4a — Fase 1, FIFO (28 cenários: 4 associatividades × 7 blocos).*

![Boxplots da Fase 1 — LRU](figuras/fig4b_fase1_lru.png)
*Figura 4b — Fase 1, LRU.*

![Boxplots da Fase 1 — LFU](figuras/fig4c_fase1_lfu.png)
*Figura 4c — Fase 1, LFU.*

![Boxplots da Fase 1 — Random](figuras/fig4d_fase1_random.png)
*Figura 4d — Fase 1, Random.*

**Efeito da associatividade.** Passar de 2 para 16 vias eleva a taxa de acerto média em **28,2 pp no LRU**, 29,1 pp no LFU, 23,7 pp no FIFO e 23,8 pp no Random, o maior efeito de toda a atividade. Parte disso se explica pela carga: as 9 regiões quentes são múltiplos de potências de 2 grandes e, com bloco de 128 B, **8 ou 9 dos 9 blocos quentes caem no mesmo conjunto** (verificamos o cálculo do índice, `(endereço >> offset) & máscara`, para cada configuração). Com 8 KB, os conjuntos têm 2, 4 ou 8 vias, menos que os 8–9 blocos quentes empilhados, e há conflito constante; com 16 vias (comportam os 9), o conflito praticamente desaparece. Isso é coerente com o grande salto entre 8 e 16 vias.

**Efeito da política.** Com poucas vias, as políticas são quase equivalentes; a diferença cresce com a associatividade (LFU − FIFO: 0,6 pp com 2 vias; ≈ 6 pp com 8 e 16 vias), pois só então existe escolha de qual bloco expulsar. A tabela abaixo compara as médias (diferença em pontos percentuais e estatística z para 100 simulações em cada lado; |z| ≥ 2 indica diferença significativa a ~95%, e *n.s.* = não significativa):

| Vias | LRU − FIFO | LFU − LRU | LFU − FIFO | Random − FIFO |
|---:|---:|---:|---:|---:|
| 2 | +0,20 pp (z = +2,9) | +0,42 pp (z = +5,7) | +0,62 pp (z = +8,8) | -0,17 pp (z = -2,3) |
| 4 | +0,50 pp (z = +7,5) | +1,08 pp (z = +16,1) | +1,58 pp (z = +22,6) | -0,11 pp (z = -1,5) (n.s.) |
| 8 | +2,34 pp (z = +29,8) | +3,80 pp (z = +53,0) | +6,14 pp (z = +84,7) | +0,00 pp (z = +0,0) (n.s.) |
| 16 | +4,72 pp (z = +66,7) | +1,38 pp (z = +20,5) | +6,10 pp (z = +94,7) | +0,01 pp (z = +0,1) (n.s.) |

- **LFU > LRU > FIFO** em 8 e 16 vias, com diferenças muito acima do ruído (|z| > 20). Em 16 vias, a pior simulação do LRU (0,7658) ainda supera a melhor do FIFO (0,7435): as distribuições **não se sobrepõem**. Em 8 vias, a pior do LFU (0,7266) supera a melhor do LRU (0,7101).
- **FIFO ≈ Random**: nas 51 comparações pareadas (Fases 0, 1 e 3) a diferença absoluta média entre as médias foi de apenas 0,0012 (máximo 0,0032). Ambas ignoram o histórico de uso dos blocos, o que é coerente com o resultado.
- Com 2 vias as diferenças são pequenas (0,2 a 0,6 pp) e **comparáveis à dispersão de uma simulação isolada**, o que é discutido na Seção 3.5.

### 3.3 Fase 2 — efeito do tamanho da cache (LRU, bloco 128 B)

**16 vias**

| Cache | Média | Desvio | Variância | Mínimo | Máximo | Outliers |
|---:|---:|---:|---:|---:|---:|---:|
| 2 KB | 0,6811 | 0,0063 | 0,000039 | 0,6654 | 0,6971 | 0 |
| 4 KB | 0,7551 | 0,0051 | 0,000026 | 0,7406 | 0,7654 | 0 |
| 8 KB | 0,7798 | 0,0046 | 0,000021 | 0,7675 | 0,7944 | 2 |
| 16 KB | 0,7919 | 0,0034 | 0,000012 | 0,7817 | 0,8001 | 1 |
| 32 KB | 0,7994 | 0,0044 | 0,000020 | 0,7908 | 0,8137 | 1 |

**2 vias**

| Cache | Média | Desvio | Variância | Mínimo | Máximo | Outliers |
|---:|---:|---:|---:|---:|---:|---:|
| 2 KB | 0,4443 | 0,0051 | 0,000026 | 0,4343 | 0,4559 | 0 |
| 4 KB | 0,4925 | 0,0050 | 0,000025 | 0,4813 | 0,5059 | 0 |
| 8 KB | 0,4984 | 0,0046 | 0,000022 | 0,4802 | 0,5066 | 1 |
| 16 KB | 0,5032 | 0,0049 | 0,000024 | 0,4932 | 0,5144 | 0 |
| 32 KB | 0,5559 | 0,0051 | 0,000026 | 0,5426 | 0,5682 | 0 |

![Boxplots da Fase 2 com 16 vias](figuras/fig5a_fase2_16way.png)
*Figura 5a — Fase 2, LRU com 16 vias (35 cenários: 5 caches × 7 blocos).*

![Boxplots da Fase 2 com 2 vias](figuras/fig5b_fase2_2way.png)
*Figura 5b — Fase 2, LRU com 2 vias.*

Com **16 vias**, aumentar a cache de 2 para 32 KB eleva a média de 0,6811 para 0,7994, mas com **retornos decrescentes**: os ganhos por dobra de tamanho são de 7,4, 2,5, 1,2 e 0,75 pp. A curva **satura perto de 0,80**, o que é esperado: 20% dos acessos são aleatórios numa RAM de 1 MB e quase sempre dão *miss* (mesmo uma cache de 32 KB cobre só ~3% da RAM), portanto nenhuma cache chega perto de 100% nessa carga.

Com **2 vias**, a cache maior ajuda pouco: de 4 a 16 KB a média quase não muda (0,4925 → 0,5032), com saltos de 4,8 pp (2→4 KB) e 5,3 pp (16→32 KB). Os blocos quentes continuam empilhados no mesmo conjunto (7 a 9 deles, para qualquer cache de 2 a 32 KB) e não cabem em apenas 2 vias, então **aumentar a cache não resolve o conflito: a associatividade importa mais que a capacidade**. O salto de 16 para 32 KB não é explicado pelos blocos quentes (que seguem empilhados); provavelmente vem do tráfego de localidade temporal e espacial, que passa a conflitar menos (hipótese não testada).

### 3.4 Fase 3 — a política importa mais em cache pequena ou grande? (16 vias, bloco 128 B)

| Cache | Política | Média | Desvio | Mínimo | Máximo | Outliers | Queda do pior caso (pp) |
|---:|---|---:|---:|---:|---:|---:|---:|
| 2 KB | FIFO | 0,6258 | 0,0050 | 0,6148 | 0,6397 | 1 | 1,10 |
| 2 KB | LRU | 0,6838 | 0,0059 | 0,6727 | 0,6979 | 0 | 1,11 |
| 2 KB | LFU | 0,7654 | 0,0084 | 0,7273 | 0,7816 | 3 | 3,81 |
| 2 KB | Random | 0,6276 | 0,0062 | 0,6159 | 0,6442 | 1 | 1,17 |
| 32 KB | FIFO | 0,7828 | 0,0043 | 0,7732 | 0,7914 | 0 | 0,96 |
| 32 KB | LRU | 0,7991 | 0,0045 | 0,7887 | 0,8096 | 0 | 1,04 |
| 32 KB | LFU | 0,8005 | 0,0040 | 0,7917 | 0,8106 | 0 | 0,88 |
| 32 KB | Random | 0,7844 | 0,0048 | 0,7725 | 0,7965 | 1 | 1,19 |

![Boxplots da Fase 3: 4 políticas com cache de 2 KB e 32 KB](figuras/fig6_fase3.png)
*Figura 6 — Fase 3: FIFO, LRU, LFU e Random com 16 vias, cache de 2 KB e de 32 KB (56 cenários).*

Em **cache pequena (2 KB)**, a escolha da política pesa muito: com bloco de 128 B, a diferença entre a melhor e a pior política é de **14,0 pp** (LFU 0,7654 contra FIFO 0,6258). Em **cache grande (32 KB)**, as políticas **convergem**: a diferença cai para 1,8 pp (0,8005 contra 0,7828). A mesma tendência aparece em todos os tamanhos de bloco: com 2 KB a diferença cresce de 2,6 pp (bloco de 2 B) para 14,0 pp (128 B), e com 32 KB fica entre 0,06 e 1,8 pp. Quando há espaço de sobra, o que se expulsa importa menos.

### 3.5 Variância e robustez

Para os **274 cenários** (cada um com 100 simulações de 10.000 acessos), a dispersão entre simulações é pequena e estável:

| Indicador | Mínimo | Média | Máximo |
|---|---:|---:|---:|
| Desvio padrão da taxa de acerto | 0,0034 | 0,0052 | 0,0084 |
| Variância | 0,000012 | 0,000028 | 0,000070 |
| Coeficiente de variação (%) | 0,43 | 0,81 | 1,54 |
| Amplitude mínimo–máximo (pp) | 1,74 | 2,67 | 5,67 |
| Queda do pior caso: média − mínimo (pp) | 0,79 | 1,34 | 4,20 |
| Outliers por cenário | 0 | 1,00 | 7 |

O desvio padrão típico é de **≈ 0,005 (0,5 pp)** e o CV fica **abaixo de 1,6%**: a taxa de acerto de um cenário varia muito pouco de uma simulação para outra. Essa dispersão é praticamente o **ruído de amostragem de 10.000 acessos**: para acessos independentes, σ = √(p(1−p)/N) vale entre 0,0040 e 0,0050 quando p vai de 0,44 a 0,80, de mesma ordem do que observamos (a pequena diferença vem de os acessos não serem independentes, por causa das localidades temporal e espacial). Ou seja, **a variação não vem de instabilidade dos algoritmos**, e sim do tamanho finito de cada simulação.

A dispersão é quase **independente da configuração**; o desvio padrão médio por grupo varia só de 0,0047 a 0,0060:

**Por política**

| Valor | Nº de cenários | Desvio padrão médio | Desvio padrão máximo | Outliers médios | Queda média do pior caso (pp) |
|---|---:|---:|---:|---:|---:|
| FIFO | 51 | 0,0053 | 0,0069 | 1,06 | 1,30 |
| LRU | 121 | 0,0051 | 0,0064 | 0,95 | 1,29 |
| LFU | 51 | 0,0052 | 0,0084 | 1,02 | 1,46 |
| Random | 51 | 0,0056 | 0,0068 | 1,04 | 1,40 |

**Por associatividade (vias)**

| Valor | Nº de cenários | Desvio padrão médio | Desvio padrão máximo | Outliers médios | Queda média do pior caso (pp) |
|---|---:|---:|---:|---:|---:|
| 2 | 63 | 0,0052 | 0,0068 | 0,86 | 1,29 |
| 4 | 28 | 0,0053 | 0,0062 | 0,79 | 1,35 |
| 8 | 28 | 0,0057 | 0,0069 | 1,00 | 1,53 |
| 16 | 155 | 0,0051 | 0,0084 | 1,10 | 1,33 |

**Por tamanho de cache (KB)**

| Valor | Nº de cenários | Desvio padrão médio | Desvio padrão máximo | Outliers médios | Queda média do pior caso (pp) |
|---|---:|---:|---:|---:|---:|
| 2 | 42 | 0,0055 | 0,0084 | 0,90 | 1,41 |
| 4 | 14 | 0,0051 | 0,0058 | 1,00 | 1,22 |
| 8 | 162 | 0,0053 | 0,0077 | 0,96 | 1,37 |
| 16 | 14 | 0,0047 | 0,0053 | 1,29 | 1,29 |
| 32 | 42 | 0,0049 | 0,0059 | 1,17 | 1,23 |

**Por tamanho de bloco (B)** *(256 e 512 B só existem na Fase 0, com 4 cenários cada)*

| Valor | Nº de cenários | Desvio padrão médio | Desvio padrão máximo | Outliers médios | Queda média do pior caso (pp) |
|---|---:|---:|---:|---:|---:|
| 2 | 38 | 0,0056 | 0,0068 | 1,34 | 1,41 |
| 4 | 38 | 0,0055 | 0,0069 | 0,82 | 1,40 |
| 8 | 38 | 0,0054 | 0,0067 | 0,97 | 1,37 |
| 16 | 38 | 0,0050 | 0,0066 | 1,05 | 1,26 |
| 32 | 38 | 0,0049 | 0,0066 | 0,84 | 1,21 |
| 64 | 38 | 0,0050 | 0,0067 | 1,29 | 1,37 |
| 128 | 38 | 0,0051 | 0,0084 | 0,71 | 1,30 |
| 256 | 4 | 0,0055 | 0,0059 | 1,25 | 1,43 |
| 512 | 4 | 0,0060 | 0,0077 | 0,50 | 2,07 |

Como a dispersão é similar entre configurações, **o que decide qual configuração é melhor é a média, não a variância**. Por outro lado, a variância não é irrelevante: com **2 vias**, a diferença LFU − FIFO é de 0,62 pp, enquanto cada simulação isolada tem desvio de ≈ 0,5 pp. Comparando **uma única simulação de cada política**, haveria cerca de **19% de chance de a ordem sair invertida** (aproximação normal, σ da diferença ≈ 0,007). É exatamente esse tipo de erro que as 100 simulações evitam.

### 3.6 Desempenho em outliers

Pelo critério de Tukey, houve **274 outliers** em 274 cenários, ou seja, **1,00 por cenário (1,0% das simulações)**; **112 cenários (41%) não tiveram nenhum**. A distribuição do número de outliers por cenário foi: 0 → 112 · 1 → 93 · 2 → 40 · 3 → 20 · 4 → 6 · 5 → 2 · 7 → 1. Em uma distribuição normal esperaríamos ≈ 0,7% de pontos marcados pelo critério; os 1,0% observados indicam caudas **ligeiramente mais pesadas, mas compatíveis com distribuições aproximadamente normais**, como sugerem as caixas simétricas dos boxplots (e como o teste de Shapiro–Wilk do script complementar confirma, Seção 6.4).

Os outliers são **de baixa magnitude**: na média, o pior caso fica **1,34 pp abaixo da média** (≈ 2,6 desvios), e o melhor caso, 1,33 pp acima. As maiores quedas observadas foram:

| Cenário | Média | Mínimo | Queda (pp) | Queda em desvios | Outliers |
|---|---:|---:|---:|---:|---:|
| Fase 0: LFU, 16 vias, 8 KB, bloco 512 B | 0,7691 | 0,7271 | 4,20 | 5,5 σ | 1 |
| Fase 3: LFU, 16 vias, 2 KB, bloco 128 B | 0,7654 | 0,7273 | 3,81 | 4,5 σ | 3 |
| Fase 1: LFU, 4 vias, 8 KB, bloco 64 B | 0,6333 | 0,5956 | 3,77 | 6,1 σ | 3 |
| Fase 1: LFU, 8 vias, 8 KB, bloco 64 B | 0,7682 | 0,7355 | 3,27 | 4,9 σ | 2 |
| Fase 1: FIFO, 8 vias, 8 KB, bloco 4 B | 0,7059 | 0,6829 | 2,30 | 3,3 σ | 1 |

Observações:

- **Quatro das cinco maiores quedas são do LFU**, que também tem o maior desvio padrão de todos os cenários (0,0084, em LFU 16 vias, 2 KB, bloco 128 B: variância 0,000070). A queda média do pior caso por política foi de 1,30 pp (FIFO), 1,29 pp (LRU), **1,46 pp (LFU)** e 1,40 pp (Random). Ou seja, o LFU tem a **melhor média**, mas uma **cauda inferior mais pesada** em algumas configurações (cache pequena, ou bloco grande). Uma hipótese é que sua decisão dependa mais do histórico inicial sorteado; não a testamos aqui.
- Mesmo no pior caso observado (queda de 4,2 pp), o LFU 16 vias com bloco de 512 B (0,7271) ainda supera a **média** de FIFO e Random nas mesmas condições (≈ 0,632).
- O número de outliers não segue um padrão claro com política, associatividade, cache ou bloco (a média por grupo fica entre 0,5 e 1,3 por cenário), então parecem eventos aleatórios e não um defeito de configuração.

### 3.7 Reprodutibilidade

Como o simulador não fixa semente, as configurações repetidas em fases diferentes funcionam como **réplicas independentes**: 49 configurações foram rodadas 2 ou 3 vezes. A diferença média entre as médias das réplicas foi de apenas **0,0006**, e a maior, **0,0027** (LRU, 16 vias, 2 KB, bloco 128 B: 0,6811 contra 0,6838). Isso é da mesma ordem do erro-padrão esperado para a diferença de duas médias de 100 simulações (≈ 0,0007), ou seja, **os resultados são reprodutíveis**: 100 simulações bastam para estimar a média com precisão de cerca de ±0,001.

---

## 4. Discussão

- **Desempenho médio.** O fator mais influente foi a **associatividade** (≈ 24 a 29 pp de 2 para 16 vias, bloco 128 B), seguida da **política de substituição**, que só faz diferença com muitas vias (até ≈ 6 pp) e em cache pequena (até ≈ 14 pp), e do **tamanho da cache**, com retornos decrescentes e teto perto de 0,80 por causa dos acessos aleatórios. O **tamanho do bloco** tem um ponto ótimo (32 a 128 B, conforme a política).
- **Robustez.** A taxa de acerto é muito estável entre simulações (desvio ≈ 0,5 pp, CV < 1,6%), e a ordenação das configurações é a mesma entre réplicas. A dispersão praticamente não depende da configuração, de modo que a escolha entre elas se faz pela média.
- **Valor do Monte Carlo.** Para diferenças grandes (> 1 pp), uma única simulação já indicaria o vencedor. Para diferenças pequenas (cache com 2 vias, FIFO × Random × LRU), a variação de uma simulação isolada é comparável à diferença real, e só a distribuição de 100 simulações permite concluir com segurança.
- **Outliers.** Existem, mas são poucos e de baixa magnitude. A exceção é o LFU, que combina a melhor média com as maiores quedas de pior caso: **o melhor desempenho médio não é necessariamente o mais robusto**.
- **Boxplot como ferramenta.** A extensão que adicionamos ao simulador permitiu ver, em um único gráfico, a posição, a largura e os outliers das caixas de cada configuração, o que torna evidente que as caixas de políticas diferentes se separam quando há muitas vias e se sobrepõem quando há poucas.

## 5. Conclusão

A simulação de Monte Carlo com 100 simulações por cenário mostrou que o desempenho de cache nessa carga é **estável e previsível**: a taxa de acerto de cada configuração varia apenas ≈ 0,5 pp entre simulações, com poucos outliers de baixa magnitude. O desempenho médio é governado principalmente pela **associatividade** (por causa dos conflitos de mapeamento das regiões quentes), depois pela **política** (LFU > LRU > FIFO ≈ Random com 8 ou mais vias) e, com retornos decrescentes, pelo **tamanho da cache**. A análise estatística foi essencial para **separar diferenças reais de ruído** e para identificar o único ponto de atenção em robustez, as caudas inferiores do LFU.

## 6. Material complementar: script `analise_monte_carlo.py`

A interface mostra, para cada cenário, apenas o resumo (média, desvio, variância, mínimo, máximo e número de outliers) e o boxplot, e **não guarda as 100 taxas de acerto** de cada cenário. Para complementar a análise, também usamos um script em Python (`analise_monte_carlo.py`) que importa o simulador, chama diretamente `simulacao_monte_carlo(..., retornar_taxas=True)` e **guarda as 100 taxas brutas de cada cenário**, o que permite fazer histogramas, testes estatísticos e obter os valores reais dos outliers.

### 6.1 O que o script faz

- **Experimento A:** 4 políticas (FIFO, LRU, LFU, Random) × 1, 2, 4, 8 e 16 vias, com cache de 8 KB e bloco de 64 B (20 cenários).
- **Experimento B:** LRU × cache de 2, 4, 8, 16 e 32 KB × 1, 4 e 16 vias, com bloco de 64 B (15 cenários).
- Total de **35 cenários × 100 simulações = 3.500 simulações**, com os mesmos parâmetros de carga da interface (10.000 acessos, RAM de 1 MB, probabilidades 0,20 / 0,20 / 0,40).
- **Semente fixa (42)**, igual em todos os cenários: o resultado é reproduzível e as políticas enxergam **exatamente os mesmos padrões de acesso**, o que permite comparar políticas simulação a simulação (comparação pareada). O script inclui também a associatividade de 1 via, que não foi rodada na interface.
- Estatísticas por cenário: média, variância e desvio amostrais (ddof = 1), intervalo de confiança de 95% da média, CV, mínimo, percentis 5 e 95, mediana, máximo, IQR, assimetria, outliers de Tukey (com a média dos outliers), média dos 5% piores e melhores casos e queda do pior caso.

### 6.2 O que ele gera

Tudo é salvo na pasta `resultados_monte_carlo/`:

| Arquivo | Conteúdo |
|---|---|
| `resumo_por_cenario.csv` | 35 linhas × 26 colunas com as estatísticas de cada cenário |
| `taxas_brutas.csv` | 3.500 linhas (cenário, nº da simulação, taxa de acerto) |
| `A1_boxplot_politica_assoc.png` | boxplots por política e associatividade |
| `A2_media_desvio.png` | média ± desvio por associatividade, uma linha por política |
| `A3_histogramas.png` | histogramas de 4 cenários, com a média marcada |
| `B1_cache_x_assoc.png` | média ± desvio por tamanho de cache e associatividade |
| `B2_boxplot_cache_4way.png` | boxplots por tamanho de cache (LRU, 4 vias) |

### 6.3 Como executar

Com o script na mesma pasta do simulador (`cache_simulator_GUI.py`):

```bash
pip install numpy matplotlib customtkinter
python analise_monte_carlo.py            # 100 simulações por cenário (≈ 1 minuto)
python analise_monte_carlo.py --sims 20  # teste rápido
```

![Histogramas da taxa de acerto de quatro cenários (100 simulações cada), com a média marcada](figuras/fig7_script_histogramas.png)
*Figura 7 — Histogramas gerados pelo script (`A3_histogramas.png`): distribuição de 100 simulações em quatro cenários.*

![Boxplots por política e associatividade gerados pelo script](figuras/fig8_script_boxplot_politica_assoc.png)
*Figura 8 — Boxplots gerados pelo script (`A1_boxplot_politica_assoc.png`), cache de 8 KB e bloco de 64 B.*

### 6.4 O que o script acrescenta à análise

**Consistência com a interface.** A tabela compara a média da taxa de acerto da interface (Apêndice A, bloco de 64 B, cache de 8 KB) com a do script, no formato *interface / script*:

| Política | 2 vias | 4 vias | 8 vias | 16 vias |
|---|---:|---:|---:|---:|
| FIFO | 0,5311 / 0,5320 | 0,6200 / 0,6206 | 0,7118 / 0,7121 | 0,7540 / 0,7547 |
| LRU | 0,5343 / 0,5353 | 0,6267 / 0,6266 | 0,7396 / 0,7398 | 0,7850 / 0,7848 |
| LFU | 0,5379 / 0,5377 | 0,6333 / 0,6347 | 0,7682 / 0,7692 | 0,7915 / 0,7916 |
| Random | 0,5313 / 0,5318 | 0,6210 / 0,6198 | 0,7116 / 0,7123 | 0,7556 / 0,7551 |

A diferença absoluta média entre as duas execuções foi de apenas 0,0006 (máxima 0,0014), da ordem do erro-padrão esperado (≈ 0,0007 para a diferença de duas médias). As duas formas de rodar a simulação, portanto, **concordam**.

**Comparação pareada entre políticas.** Como os padrões de acesso são os mesmos para FIFO, LRU e LFU, podemos contar em quantas das 100 simulações uma política supera a outra:

| Vias | LRU > FIFO | LFU > LRU | LFU > FIFO |
|---:|---:|---:|---:|
| 2 | 100% | 79% | 99% |
| 4 | 100% | 98% | 100% |
| 8 | 100% | 99% | 100% |
| 16 | 100% | 100% | 100% |

O LRU superou o FIFO em **todas** as 100 simulações, com 2, 4, 8 e 16 vias, e o LFU superou o LRU em 79% (2 vias) a 100% (16 vias) das simulações. Com **1 via**, as três políticas deram **exatamente o mesmo resultado em todas as simulações**, como esperado, já que não há escolha de bloco a expulsar. Em 2 vias, a diferença média entre LFU e LRU é pequena (≈ 0,2 pp) e, ainda assim, o LFU ganha na maioria das simulações, mas não em todas: é o caso em que a ordem das políticas mais depende da simulação sorteada.

**Normalidade.** Como o script guarda as 100 taxas, aplicamos o teste de Shapiro–Wilk em cada cenário: **34 dos 35 cenários (97%)** não rejeitam a normalidade (p > 0,05), e a assimetria média é de 0,06 (entre -0,92 e 0,33). Isso sustenta, com um teste formal, a ideia de distribuições aproximadamente normais, que na Seção 3.6 estava apenas sugerida pela simetria dos boxplots. O desvio padrão dos cenários do script ficou entre 0,0043 e 0,0070 (mediana 0,0048), coerente com o da interface.

**Valores reais dos outliers.** O script registra **17 outliers em 3.500 simulações (0,49%)**, sendo 9 inferiores (em média 1,35 pp abaixo da mediana) e 8 superiores (em média 1,24 pp acima); o maior desvio foi de 2,70 pp. Isso confirma que os outliers são **poucos e de baixa magnitude** (a interface acusou ≈ 1%, o script ≈ 0,5%; ambos na faixa de 0,5% a 1%). A maior queda de pior caso do script ocorreu, novamente, no **LFU** (8 vias, bloco de 64 B: 2,66 pp abaixo da média), o mesmo cenário que aparece entre os piores casos da interface (3,27 pp), reforçando a observação da Seção 3.6 sobre a cauda inferior do LFU.

**Tamanho da cache × associatividade (Experimento B, LRU, bloco de 64 B).** Média da taxa de acerto:

| Cache | 1 via | 4 vias | 16 vias |
|---:|---:|---:|---:|
| 2 KB | 0,4722 | 0,5612 | 0,7506 |
| 4 KB | 0,4795 | 0,5722 | 0,7738 |
| 8 KB | 0,4844 | 0,6266 | 0,7848 |
| 16 KB | 0,5362 | 0,6322 | 0,7918 |
| 32 KB | 0,5402 | 0,6369 | 0,7961 |

Repete-se o padrão da Fase 2: o **ganho por aumentar a cache é bem menor que o ganho por aumentar a associatividade** (com 16 vias a taxa vai de 0,7506 a 0,7961; com 1 via, de 0,4722 a 0,5402), e com 16 vias a curva satura perto de 0,80.

---

## 7. Limitações

- A carga é **sintética** (probabilidades fixas e 9 regiões quentes fixas); resultados com *traces* reais podem diferir. Como a carga é estacionária, ela favorece o LFU; em cargas que mudam ao longo do tempo o resultado poderia se inverter (não testado).
- Cada cenário foi executado **uma vez por fase** (réplicas só nas configurações que se repetiram entre fases) e o simulador **não fixa semente**; por isso os números variam ligeiramente a cada execução (≈ ±0,001 na média).
- Do console da interface só obtemos a **contagem** de outliers (não seus valores); as análises de pior e melhor caso usam mínimo e máximo. Os valores reais e a normalidade foram verificados apenas nos 35 cenários do script complementar (Seção 6). Na interface, desvio padrão e variância usam ddof = 0.
- A comparação entre políticas usa aproximação normal (n = 100 por cenário) e execuções independentes, sem teste formal de normalidade. As explicações marcadas como hipótese não foram testadas isoladamente.
- Só foram exploradas RAM de 1 MB e 10.000 acessos por simulação; a dispersão depende desse número (cai com mais acessos e sobe com menos).

---

## Apêndice A — Fase 1 com bloco de 64 B (cache 8 KB)

| Política | Vias | Média | Desvio | Variância | Mínimo | Máximo | Outliers |
|---|---:|---:|---:|---:|---:|---:|---:|
| FIFO | 2 | 0,5311 | 0,0046 | 0,000021 | 0,5151 | 0,5408 | 1 |
| FIFO | 4 | 0,6200 | 0,0056 | 0,000031 | 0,6072 | 0,6390 | 1 |
| FIFO | 8 | 0,7118 | 0,0054 | 0,000029 | 0,7012 | 0,7324 | 1 |
| FIFO | 16 | 0,7540 | 0,0046 | 0,000021 | 0,7421 | 0,7655 | 0 |
| LRU | 2 | 0,5343 | 0,0047 | 0,000022 | 0,5199 | 0,5437 | 1 |
| LRU | 4 | 0,6267 | 0,0047 | 0,000022 | 0,6134 | 0,6361 | 2 |
| LRU | 8 | 0,7396 | 0,0053 | 0,000028 | 0,7241 | 0,7515 | 1 |
| LRU | 16 | 0,7850 | 0,0043 | 0,000018 | 0,7721 | 0,7943 | 3 |
| LFU | 2 | 0,5379 | 0,0047 | 0,000022 | 0,5283 | 0,5488 | 0 |
| LFU | 4 | 0,6333 | 0,0062 | 0,000038 | 0,5956 | 0,6470 | 3 |
| LFU | 8 | 0,7682 | 0,0067 | 0,000045 | 0,7355 | 0,7776 | 2 |
| LFU | 16 | 0,7915 | 0,0047 | 0,000022 | 0,7786 | 0,8030 | 3 |
| Random | 2 | 0,5313 | 0,0055 | 0,000030 | 0,5181 | 0,5464 | 1 |
| Random | 4 | 0,6210 | 0,0057 | 0,000032 | 0,6064 | 0,6330 | 2 |
| Random | 8 | 0,7116 | 0,0063 | 0,000039 | 0,6954 | 0,7307 | 1 |
| Random | 16 | 0,7556 | 0,0050 | 0,000025 | 0,7430 | 0,7693 | 0 |

## Apêndice B — Arquivos e como reproduzir

- **`tabela_dispersao_monte_carlo.xlsx`**: tabela de dispersão com os 274 cenários (média, desvio padrão, variância, CV, mínimo, máximo, amplitude, queda do pior caso e outliers) e resumos por política, associatividade, cache e bloco.
- **`figuras/`**: gráficos gerados pelo simulador (curvas e boxplots) e pelo script complementar (histogramas e boxplots).
- **`analise_monte_carlo.py`** e **`resultados_monte_carlo/`**: script complementar (Seção 6) e seus resultados (`resumo_por_cenario.csv`, `taxas_brutas.csv` e 5 gráficos).
- Para reproduzir: abrir `cache_simulator_GUI.py`, configurar RAM = 1048576, acessos = 10000, **Simulações MC = 100**, probabilidades 0,20 / 0,20 / 0,40, escolher política, associatividade e tamanho da cache, e clicar em *Executar Simulação*. O console mostra as estatísticas e a aba *Boxplot (Distribuição)* mostra as caixas.
