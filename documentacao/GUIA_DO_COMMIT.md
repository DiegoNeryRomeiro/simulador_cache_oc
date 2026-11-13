# Commit no mesmo padrão da atividade 6

## O que copiar

Copie **somente a pasta `atividade-2/` inteira** desta entrega para a raiz do clone do grupo. Ela deve ficar ao lado de `atividade-6/`. Os quatro arquivos da raiz desta cópia (`cache_simulator_GUI.py`, `README.md`, `requirements.txt`, `LICENSE`) são a base original, idêntica à do exemplo, e **não precisam entrar no seu commit**.

Não copie a pasta antiga `simulador_cache_oc-projeto-2026/`, que contém o protótipo com alterações na GUI. Não misture as duas estruturas. A atividade 6 fornecida não foi editada.

## Arquivos incluídos

- `atividade-2/scripts/`: núcleo, configuração, execução, renderização e auditoria.
- `atividade-2/testes/`: 15 testes automatizados.
- `atividade-2/resultados/completo/`: dados completos, 21 traces, metadados, testes e auditoria.
- `atividade-2/resultados/piloto/`: tabelas e evidências do piloto.
- `atividade-2/graficos/`: três gráficos PNG.
- `atividade-2/mapas_calor/`: painel e 21 mapas PNG.
- `atividade-2/relatorio/atividade_2_impacto_localidade.md`.
- `atividade-2/documentacao/`, `README.md`, requisitos e `.gitignore`.

O `.gitignore` local exclui cache, bytecode, ambientes virtuais e gráficos/traces redundantes do piloto. Não envie o ambiente `.venv`, o cache `.mplconfig`, a pasta de trabalho `tmp` nem o parecer da atividade 6. O parecer é material de revisão, não parte da sua atividade.

## Comandos no clone do grupo

Depois de copiar a pasta e executar os testes do README:

```powershell
git switch -c atividade-2-localidade
git status --short
git add atividade-2
git diff --cached --stat
git diff --cached
git commit -m "Adiciona atividade 2 sobre impacto da localidade na cache"
git push -u origin atividade-2-localidade
```

Se a branch já existir, use `git switch nome-da-branch`. Execute os comandos na raiz do clone real, não nesta cópia sem `.git`. O diff deve mostrar adições apenas em `atividade-2/`, sem modificar `atividade-6/` nem o simulador original. Se houver outros arquivos já staged, revise-os antes de confirmar o commit.

## Antes da entrega acadêmica

Acrescente os nomes dos integrantes e a identificação solicitada pelo professor ao relatório. Confirme no GitHub que as imagens e links relativos do Markdown abrem. Os 15 testes dependem de o `cache_simulator_GUI.py` original estar na raiz, pois extraem suas classes e gerador por AST sem importar a GUI.

Não foi criado commit, branch ou push automaticamente. A integração foi organizada para você realizar o envio após revisar o conteúdo.
