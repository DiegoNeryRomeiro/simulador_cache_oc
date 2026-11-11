# Atividade 4 — Influência dos Parâmetros da Cache

Este diretório contém uma execução reprodutível dos experimentos sobre número
de linhas, associatividade e tamanho de bloco. O núcleo headless reproduz a
organização e as políticas FIFO, LRU, LFU e Random do simulador da branch
`Versão-2026`; os experimentos desta atividade usam LRU. A interface gráfica e
o arquivo original não foram alterados.

## Ambiente e dependências

- Python 3.10 ou posterior;
- Matplotlib 3.6 ou posterior, somente para gerar os gráficos;
- biblioteca padrão do Python para as simulações, CSVs e testes.

Opcionalmente, instale a dependência gráfica em um ambiente virtual:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r atividade-4/requirements.txt
```

O `requirements.txt` da raiz não descreve corretamente a GUI deste commit: ele
lista `dearpygui`, mas `cache_simulator_GUI.py` importa `customtkinter`. No
ambiente em que a atividade foi executada, nenhum dos dois pacotes estava
instalado; por isso a confirmação da GUI ficou limitada à inspeção estática.

## Configuração usada

Todos os cenários usam RAM de 1 MiB, política LRU, 10.000 acessos, semente
`2026` e probabilidades do simulador: 0,20 temporal, 0,20 espacial, 0,40 em
regiões quentes e 0,20 aleatória. A mesma lista de endereços é reutilizada por
todos os cenários. Como RAM, número de acessos, probabilidades e semente também
são comuns entre os experimentos, a carga é idêntica nos 13 cenários.

- Experimento A: bloco de 16 B, 2 vias e 16, 32, 64 ou 128 linhas.
- Experimento B: cache de 1 KiB, bloco de 16 B e 1, 2, 4 ou 8 vias.
- Experimento C: cache de 1 KiB, 2 vias e blocos de 8, 16, 32, 64 ou 128 B.

## Reprodução

Execute a partir da raiz do repositório:

```bash
python3 atividade-4/scripts/experimento_linhas.py
python3 atividade-4/scripts/experimento_associatividade.py
python3 atividade-4/scripts/experimento_blocos.py
python3 atividade-4/scripts/gerar_graficos.py
python3 -m unittest discover -s atividade-4/tests -v
```

Os scripts aceitam `--acessos`, `--semente` e `--saida`. Por exemplo, um teste
rápido que não substitui o CSV definitivo pode ser feito com:

```bash
python3 atividade-4/scripts/experimento_linhas.py \
  --acessos 200 --saida /tmp/atividade4-linhas-smoke.csv
```

## Arquivos

- `scripts/cache_experimentos.py`: núcleo, validações, gerador e escrita CSV;
- `scripts/experimento_*.py`: cenários A, B e C;
- `scripts/gerar_graficos.py`: geração dos PNGs a partir dos CSVs;
- `resultados/*.csv`: medições efetivamente obtidas;
- `graficos/*.png`: visualizações em 220 dpi;
- `tests/test_experimentos.py`: testes de parâmetros, cálculos,
  reprodutibilidade e integridade dos CSVs;
- `relatorio/atividade_4_parametros_cache.md`: relatório acadêmico completo.

Os PDFs fornecidos pelo professor foram consultados para a fundamentação e para
delimitar a Atividade 4: `Memória cache - teoria.pdf`, `Projeto - Simulador
cache.pdf` e `README_Simulador_Memoria_Cache.pdf`. Eles orientam a análise de
localidade, mapeamento, linhas, conjuntos e associatividade; os resultados
numéricos deste diretório foram produzidos pelos scripts e não foram retirados
dos PDFs.
