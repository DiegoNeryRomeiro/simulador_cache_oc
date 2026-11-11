# Atividade 6 — Acesso realista versus aleatório

Esta atividade compara duas cargas sintéticas no simulador da branch
`Versão-2026`: endereços uniformemente aleatórios e a carga produzida por
`gerar_padrao_realista`, com localidade temporal, espacial e regiões quentes.
Os dois cenários usam exatamente a mesma configuração de hardware, política,
quantidade de acessos e semente.

## Configuração executada

- RAM: 1 MiB (`1048576` bytes);
- cache: 4 KiB (`4096` bytes);
- bloco: 32 bytes;
- associatividade: 4 vias;
- política: LRU;
- acessos: 10.000 por cenário;
- semente: 42;
- regiões para os mapas: 4 KiB por região;
- janelas temporais: 100 acessos.

O cenário aleatório usa `randint(0, memory_size - 1)` em todos os acessos. O
cenário realista preserva a lógica do simulador original: probabilidades 0,20
temporal, 0,20 espacial e 0,40 para regiões quentes; os 0,20 restantes são
aleatórios. A carga realista é sintética e não representa o rastro de um
programa específico.

## Execução

A partir da raiz do repositório:

```bash
python3 atividade-6/scripts/executar_experimentos.py
python3 atividade-6/scripts/gerar_graficos.py
python3 atividade-6/scripts/gerar_mapas_calor.py
python3 -m unittest discover -s atividade-6/testes -v
```

Para uma simulação piloto:

```bash
python3 atividade-6/scripts/executar_experimentos.py \
  --acessos 200 --saida-dir /tmp/atividade6-piloto
python3 atividade-6/scripts/gerar_graficos.py \
  --resultados /tmp/atividade6-piloto --saida-dir /tmp/atividade6-piloto/graficos
python3 atividade-6/scripts/gerar_mapas_calor.py \
  --resultados /tmp/atividade6-piloto --saida-dir /tmp/atividade6-piloto/mapas
```

## Organização

- `scripts/cache_core.py`: núcleo headless, geradores, cache, métricas e CSVs;
- `scripts/gerar_acessos.py`: exportação independente dos padrões;
- `scripts/executar_experimentos.py`: execução dos dois cenários e taxas
  acumuladas;
- `scripts/gerar_graficos.py`: quatro gráficos comparativos;
- `scripts/gerar_mapas_calor.py`: dois mapas com normalização comum;
- `resultados/acessos_*.csv`: sequências efetivamente utilizadas;
- `resultados/comparacao_resultados.csv`: configuração e métricas finais;
- `resultados/taxa_acumulada_*.csv`: taxa de acerto após cada acesso;
- `graficos/`: PNGs comparativos;
- `mapas_calor/`: PNGs espaciais-temporais;
- `testes/`: verificações automatizadas;
- `relatorio/atividade_6_acessos_realistas_aleatorios.md`: relatório acadêmico.

## Mapa de calor original

O método gráfico original depende de Tk, `FigureCanvasTkAgg` e de uma janela
GUI. Além disso, calcula o número de janelas por divisão inteira por 50; com
cargas menores que 50 acessos, isso pode produzir uma matriz com zero colunas.
Para a atividade, a solução menos invasiva foi gerar os mapas em um script
headless com Matplotlib `Agg`, usando `ceil` conceitualmente por meio do maior
índice de janela registrado. A mesma granularidade espacial e temporal e a
mesma normalização de cores são aplicadas aos dois cenários. O arquivo original
não foi alterado.
