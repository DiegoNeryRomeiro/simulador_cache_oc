# Atividades 1 e 5 — Comparação de Políticas de Substituição e Implementação da MRU

## 1. Objetivo

Esta parte do projeto teve como objetivo comparar o desempenho das políticas de substituição FIFO, LRU, LFU e Random, já disponíveis no simulador de memória cache fornecido pelo professor, e implementar uma nova política denominada MRU (*Most Recently Used*).

A proposta foi observar como a escolha do algoritmo de substituição influencia a taxa de acerto da memória cache, utilizando simulações com parâmetros controlados e analisando os resultados obtidos.

## 2. Políticas de substituição analisadas

Foram avaliadas cinco políticas:

- **FIFO (First-In, First-Out):** substitui o bloco que está há mais tempo na cache, considerando sua ordem de entrada.
- **LRU (Least Recently Used):** substitui o bloco que não é acessado há mais tempo.
- **LFU (Least Frequently Used):** substitui o bloco com menor frequência de acesso.
- **Random:** seleciona aleatoriamente o bloco que será substituído.
- **MRU (Most Recently Used):** substitui o bloco acessado mais recentemente.

As quatro primeiras políticas já estavam implementadas no simulador original. A MRU foi adicionada durante o desenvolvimento desta atividade.

## 3. Implementação da política MRU

A implementação da MRU foi realizada no arquivo `cache_simulator_GUI.py`, aproveitando a estrutura de políticas de substituição existente no projeto.

Foi criada uma nova classe chamada `MRU`, herdando da classe abstrata `EvictionPolicy` e implementando o método `find_victim()`.

O método utiliza o atributo `last_access_time` para identificar a linha utilizada mais recentemente e selecioná-la para substituição.

O código implementado foi:

```python
class MRU(EvictionPolicy):
    def find_victim(self, lines: List[CacheLine]) -> CacheLine:
        return max(lines, key=lambda line: line.last_access_time)
```

Além da implementação da classe, foram realizadas duas modificações no simulador:

1. Inclusão da política MRU no dicionário `policy_map`, responsável por associar os nomes dos algoritmos às suas respectivas implementações.
2. Inclusão da opção `MRU` na lista de algoritmos disponíveis na interface gráfica.

Com essas alterações, tornou-se possível selecionar e executar a MRU diretamente pela interface do simulador.

### 3.1. Teste de funcionamento

Para verificar a escolha da linha vítima, foi criado o arquivo `test_mru.py`.

O teste utilizou três linhas de cache com os seguintes valores de último acesso:

| Linha | Último acesso |
|---|---:|
| Linha 1 | 5 |
| Linha 2 | 15 |
| Linha 3 | 10 |

Como a MRU deve selecionar a linha utilizada mais recentemente, o resultado esperado era a escolha da Linha 2.

O teste foi executado com sucesso, apresentando a mensagem:

`TESTE APROVADO: MRU substitui a linha mais recentemente utilizada.`

Também foi realizada uma simulação utilizando a MRU na interface gráfica, que concluiu a execução e gerou os resultados e gráficos esperados.

Essas verificações confirmaram o funcionamento básico da nova política. O teste unitário verifica especificamente a escolha da vítima, não substituindo testes mais amplos de integração.

## 4. Metodologia das simulações

As simulações foram realizadas utilizando o simulador de memória cache da versão 2026.

Para comparar as políticas, foram mantidos os mesmos parâmetros de configuração, variando apenas o algoritmo de substituição.

| Parâmetro | Valor |
|---|---|
| Memória principal | 1.048.576 bytes (1 MiB) |
| Tamanho da cache | 8.192 bytes (8 KiB) |
| Associatividade | 4 |
| Número de acessos da CPU | 10.000 |
| Simulações Monte Carlo | 100 |
| Probabilidade de localidade temporal | 0,20 |
| Probabilidade de localidade espacial | 0,20 |
| Probabilidade de regiões quentes | 0,40 |
| Políticas avaliadas | FIFO, LRU, LFU, Random e MRU |

Inicialmente, foram realizadas simulações considerando os tamanhos de bloco de 2, 4, 8, 16, 32, 64, 128, 256 e 512 bytes.

Esses resultados permitiram observar como o desempenho de cada algoritmo variava de acordo com o tamanho dos blocos.

Posteriormente, foi realizada uma comparação gráfica utilizando exclusivamente os resultados correspondentes ao tamanho de bloco de **32 bytes**, extraídos dos arquivos CSV das simulações anteriores.

Esse procedimento permitiu comparar as cinco políticas para um mesmo tamanho de bloco, preservando as demais configurações.

Como a geração de acessos possui componentes aleatórios, as diferentes execuções não utilizaram necessariamente sequências idênticas de endereços. As 100 repetições de Monte Carlo foram utilizadas para obter estimativas médias e reduzir a influência da aleatoriedade.

## 5. Resultados obtidos

### 5.1. Comparação das políticas com blocos de 32 bytes

Os valores de taxa média de acerto obtidos foram:

| Política | Taxa média de acerto |
|---|---:|
| FIFO | 62,64% |
| LRU | 63,13% |
| LFU | 63,47% |
| Random | 62,72% |
| MRU | 50,76% |

O gráfico comparativo foi gerado a partir dos arquivos CSV utilizando um script Python com as bibliotecas Pandas e Matplotlib.

**Figura 1 — Comparação das taxas médias de acerto das cinco políticas para blocos de 32 bytes.**

![Comparação das políticas de substituição](../resultados/pessoa1_politicas/grafico/comparacao_politicas_32_bytes.png)

A LFU apresentou a maior taxa média de acerto, atingindo aproximadamente 63,47%.

As políticas LRU, Random e FIFO apresentaram resultados próximos, enquanto a MRU obteve uma taxa de acerto consideravelmente inferior.

### 5.2. Análise considerando diferentes tamanhos de bloco

Além da comparação com blocos de 32 bytes, foram avaliados nove tamanhos de bloco, de 2 a 512 bytes.

O gráfico produzido pelo simulador mostrou que as políticas FIFO, LRU, LFU e Random apresentaram comportamentos semelhantes.

De maneira geral, a taxa de acerto aumentou até os blocos de 32 bytes e diminuiu para tamanhos maiores.

A MRU apresentou desempenho inferior às demais políticas durante os experimentos.

Os maiores valores registrados nas curvas foram:

| Política | Maior taxa de acerto observada |
|---|---:|
| FIFO | 62,64% |
| LRU | 63,13% |
| LFU | 63,47% |
| Random | 62,72% |
| MRU | 52,16% |

É importante diferenciar esses valores dos apresentados na seção anterior. O valor máximo da MRU, por exemplo, foi de 52,16% considerando todos os tamanhos de bloco, enquanto seu resultado para blocos de 32 bytes foi de 50,76%.

Os dados completos das simulações foram armazenados nos arquivos CSV:

- `FIFO.csv`
- `LRU.csv`
- `LFU.csv`
- `RANDOM.csv`
- `MRU.csv`

Esses arquivos estão disponíveis no diretório `resultados/pessoa1_politicas/csv/`.

O gráfico com as curvas dos diferentes tamanhos de bloco também foi armazenado no diretório de gráficos da atividade.

## 6. Análise dos resultados

Os experimentos demonstraram que a escolha da política de substituição influencia o desempenho da memória cache.

Entre os algoritmos avaliados, a LFU apresentou a maior taxa média de acerto para blocos de 32 bytes, alcançando 63,47%.

Esse resultado sugere que, para os padrões de acesso utilizados, manter na cache os blocos acessados com maior frequência foi uma estratégia vantajosa.

A LRU também apresentou um resultado próximo, com 63,13%. Como essa política considera o tempo desde o último acesso, ela tende a aproveitar situações em que informações utilizadas recentemente são acessadas novamente.

As políticas Random e FIFO apresentaram respectivamente 62,72% e 62,64%, mantendo resultados próximos aos da LRU e LFU.

Já a MRU apresentou uma taxa média de acerto de 50,76%, sendo o menor resultado da comparação.

Esse comportamento é coerente com sua estratégia de substituição. Ao remover o bloco acessado mais recentemente, a MRU pode eliminar informações que ainda possuem grande probabilidade de reutilização, principalmente em situações com localidade temporal.

Outro comportamento observado foi a influência do tamanho do bloco. Nos experimentos realizados, os melhores resultados das políticas originais ocorreram com blocos de 32 bytes.

Isso demonstra que aumentar continuamente o tamanho dos blocos não garante uma melhoria contínua na taxa de acerto.

Entretanto, os resultados não significam que a LFU seja sempre superior ou que a MRU seja inadequada em qualquer situação. O desempenho de uma política depende das características dos acessos à memória e da configuração da cache.

Além disso, como as sequências de acessos foram geradas aleatoriamente, as diferenças observadas devem ser interpretadas dentro das condições experimentais utilizadas.

## 7. Conclusão

As atividades realizadas permitiram comparar as políticas de substituição FIFO, LRU, LFU e Random e implementar uma nova política, denominada MRU.

A MRU foi integrada ao simulador, disponibilizada na interface gráfica e submetida a um teste unitário que confirmou sua capacidade de selecionar a linha acessada mais recentemente.

As simulações foram executadas utilizando parâmetros equivalentes, e os resultados foram armazenados em arquivos CSV para análise e geração de gráficos.

Na comparação com blocos de 32 bytes, a LFU apresentou a maior taxa média de acerto, com 63,47%, enquanto a MRU obteve o menor resultado, com 50,76%.

Os experimentos também demonstraram que as taxas de acerto variam conforme o tamanho dos blocos e que diferentes políticas podem apresentar comportamentos distintos diante dos mesmos tipos de padrões de acesso.

Dessa forma, as atividades contribuíram para compreender a influência das políticas de substituição no desempenho da memória cache, além de permitir a ampliação prática do simulador fornecido como base para o projeto.

## 8. Arquivos produzidos

Os arquivos relacionados a esta contribuição são:

| Arquivo | Finalidade |
|---|---|
| `cache_simulator_GUI.py` | Simulador com a política MRU implementada |
| `test_mru.py` | Teste unitário da política MRU |
| `gerar_grafico_politicas.py` | Script de geração do gráfico comparativo |
| `resultados/pessoa1_politicas/csv/` | Dados das cinco políticas |
| `resultados/pessoa1_politicas/grafico/` | Gráficos das simulações |
| `docs/pessoa1_politicas_mru.md` | Documentação das atividades 1 e 5 |

Esta documentação corresponde à contribuição da Pessoa 1 e será incorporada ao relatório técnico coletivo do projeto.