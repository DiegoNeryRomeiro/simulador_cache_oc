# Registro de execução e reorganização

## Escopo e origem

O enunciado do tópico 2 solicita variar as probabilidades temporal, espacial e quente, observar a taxa de acerto e correlacionar padrões com mapas temporais. O manual recomenda manter as demais variáveis constantes e registrar sementes.

Na coleta original de **11/11/2026**, foi preparado um protótipo em `simulador_cache_oc-projeto-2026`, com testes do núcleo, ajustes da GUI e estudo de 21 cenários. Após o usuário fornecer a entrega da atividade 6, foi solicitada uma organização equivalente para o commit do grupo.

Em **13/11/2026**, foi criada esta entrega independente, dentro de `atividade-2/`, seguindo as pastas `scripts`, `testes`, `resultados`, `graficos`, `mapas_calor` e `relatorio`. Foi acrescentada `documentacao` para registrar as evidências e orientar o commit. A pasta do protótipo foi preservada; não é a pasta indicada para envio.

## Preservação da base

Os quatro arquivos da raiz desta cópia foram preservados byte a byte a partir da base fornecida com a atividade 6: `cache_simulator_GUI.py`, `README.md`, `requirements.txt` e `LICENSE`. Assim, apenas `atividade-2/` precisa entrar no commit. Não foi necessário alterar arquivos das outras atividades.

O núcleo experimental de `scripts/cache_core.py` mantém as regras de mapeamento e substituição do simulador. Acrescenta validações de probabilidades e configuração e aceita um gerador aleatório local. A geração dos mapas usa as sequências efetivamente medidas e não usa módulo para confundir blocos diferentes. As limitações da rotina gráfica original permanecem na GUI original, que não é chamada por esta entrega.

## Ambiente e dependências

- Windows 11, Python 3.12.14, NumPy 2.3.0 e Matplotlib 3.10.3.
- Backend `Agg`, sem display ou inicialização da GUI.
- Reutilizado o ambiente virtual já preparado no protótipo; ele não faz parte do commit.
- `requirements.txt` declara as dependências da atividade e os dados de fuso horário necessários no Windows.
- `requirements-lock.txt` registra todo o ambiente utilizado, incluindo pacotes da GUI do protótipo. A atividade não os importa.
- O cache do Matplotlib fica em `.mplconfig`, excluído pelo `.gitignore`.

No protótipo, a preparação inicial enfrentou bloqueios de rede e de temporários do sandbox; a instalação foi concluída após autorização. Também houve um ajuste de localização Tcl/Tk no teste da GUI do protótipo. A entrega atual não depende desse teste, da GUI ou de variáveis locais Tcl/Tk.

## Testes e equivalência com o original

A suíte original de 13 verificações foi mantida e ganhou duas verificações de equivalência, totalizando **15 testes aprovados**:

- Primeiro acesso frio, hit no mesmo bloco e campos tag/index/offset.
- Escolha de vítimas FIFO, LRU e LFU; contadores da política Random.
- Rejeição de arquiteturas, probabilidades e regiões quentes inválidas.
- Reprodutibilidade por semente, limites dos endereços e passos espaciais.
- Temporal 100% com um miss; quente 100% com nove misses.
- Mapas com IDs distintos, janela parcial e conservação do agregado `Outros`.
- Comparação de cada hit/miss LRU do núcleo independente com o original para 500 acessos em cada um dos 21 cenários.
- Comparação de cada endereço gerado com o gerador original para 500 acessos em cada um dos 21 cenários.

As classes e o gerador originais são extraídos por AST, sem importar a GUI. Evidência: `resultados/completo/testes.txt`.

## Piloto e coleta completa reproduzidos

O piloto foi repetido com **21 cenários × 3 repetições × 10.000 acessos = 630.000 acessos**. Passaram os sete critérios de plausibilidade codificados: contadores, limites de taxas, um miss temporal extremo, nove misses quentes extremos, faixa aleatória, alta reutilização espacial extrema e crescimento médio das curvas isoladas.

Após a aprovação, foram repetidos os **630 ensaios**, totalizando **6.300.000 acessos**. Cada ensaio começou com cache vazia. RAM, cache, bloco, associatividade e LRU ficaram fixos. Sementes: 20261111 a 20261140. As médias e os desvios reproduziram a coleta de 11/11.

Os metadados foram regenerados para refletir a data real da reprodução, novos caminhos e hashes dos arquivos na estrutura final. Data, duração e hashes dos scripts mudaram por causa da reorganização; os dados numéricos e as sequências foram preservados.

## Auditoria e organização

- Recalculadas médias e desvios dos 21 cenários a partir dos 630 registros.
- Reexecutados os 21 traces definitivos: **210.000 acessos**, conferindo cada hit/miss e SHA-256.
- Conferidos IDs de bloco, ordem, limites e conservação das contagens nos mapas.
- Confirmada equivalência das primeiras três repetições com o piloto.
- Conferidos hashes dos scripts da coleta.
- Comparados os CSVs e traces com a coleta do protótipo.
- Verificada a preservação byte a byte dos quatro arquivos da base.
- Verificados links Markdown e separação entre três gráficos e 22 imagens de mapas (painel + 21 cenários).
- Validados os comandos independentes de regeneração de gráficos e mapas a partir dos CSVs.

Evidências em `resultados/completo/auditoria.json`, `validacao.json`, `metadados.json`, `testes.txt` e `documentacao/verificacao_reorganizacao.json`.

## Entrega

O relatório foi atualizado para os caminhos finais e para distinguir a coleta original da reprodução. A entrega atual não exige mudanças de GUI e pode ser integrada adicionando somente `atividade-2/`. Nenhum commit, branch ou push foi feito. O usuário fará o envio, conforme `GUIA_DO_COMMIT.md`.
