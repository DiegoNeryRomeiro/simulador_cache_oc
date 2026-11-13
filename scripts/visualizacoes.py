"""Renderização headless dos resultados salvos da atividade 2."""
import csv
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
from cache_core import mapa_temporal_blocos
from configuracao import CONFIG


def pasta_figuras(resultados, nome):
    pasta = ROOT / nome if resultados.name == "completo" else resultados / nome
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def carregar_resultados():
    pasta = ROOT / "resultados" / "completo"
    with (pasta / "resumo.csv").open(encoding="utf-8", newline="") as arquivo:
        resumo = list(csv.DictReader(arquivo))
    for linha in resumo:
        for campo in ("media", "desvio_padrao"):
            linha[campo] = float(linha[campo])
    representantes = {}
    for linha in resumo:
        with (pasta / "traces" / (linha["cenario"] + ".csv")).open(encoding="utf-8", newline="") as arquivo:
            trace = list(csv.DictReader(arquivo))
        padrao = [int(t["endereco"]) for t in trace]
        taxa = sum(int(t["hit"]) for t in trace) / len(trace)
        representantes[linha["cenario"]] = (padrao, taxa, linha["descricao"])
    return pasta, resumo, representantes


def decorar(ax):
    ax.grid(alpha=.2)
    ax.set_ylim(0, 102)
    ax.set_ylabel("Taxa de acerto (%)")


def gerar_graficos(out, summaries, representatives):
    out = pasta_figuras(out, "graficos")
    by_name = {r["cenario"]: r for r in summaries}
    plt.rcParams.update({"font.size": 10, "figure.dpi": 140})
    fig, ax = plt.subplots(figsize=(9, 5), layout="constrained")
    for name in ("temporal", "espacial", "quente"):
        data = [by_name["aleatorio"]] + [by_name[f"{name}_{p:03d}"] for p in (20,40,60,80,100)]
        ax.errorbar([0,20,40,60,80,100], [r["media"]*100 for r in data],
                    yerr=[r["desvio_padrao"]*100 for r in data], marker="o", capsize=3, label=name.capitalize())
    decorar(ax)
    ax.set_xlabel("Probabilidade do mecanismo de localidade (%)")
    ax.set_title("Efeito isolado da localidade | média ± desvio padrão amostral")
    ax.legend()
    fig.savefig(out / "curvas_localidade.png")
    plt.close(fig)
    names = ["temporal_080", "espacial_080", "quente_080", "misto_te", "misto_tq", "misto_eq", "misto_equilibrado", "misto_padrao"]
    fig, ax = plt.subplots(figsize=(11, 6), layout="constrained")
    ax.bar(range(len(names)), [by_name[n]["media"]*100 for n in names],
           yerr=[by_name[n]["desvio_padrao"]*100 for n in names], capsize=3, color="#286eaa")
    ax.set_xticks(range(len(names)), [n.replace("misto_", "Misto\n").replace("_080", "\n80%") for n in names], rotation=15)
    decorar(ax)
    ax.set_title("Mesma parcela aleatória (20%): cenários puros e mistos")
    fig.savefig(out / "comparacao_mistos.png")
    plt.close(fig)

    selected = ["aleatorio", "temporal_080", "espacial_080", "quente_080", "misto_padrao", "espacial_100"]
    # Preserva a posição física; os mapas acima usam linhas selecionadas sem escala espacial.
    fig, axes = plt.subplots(3, 2, figsize=(13, 11), layout="constrained")
    for name, ax in zip(selected, axes.flat):
        pattern, rate, label = representatives[name]
        ax.scatter(range(1, len(pattern)+1), np.array(pattern)/1024, s=.6, alpha=.4, rasterized=True)
        ax.set(title=label, xlabel="Número do acesso", ylabel="Endereço (KiB)", ylim=(0,1024))
    fig.suptitle("Distribuição dos endereços reais ao longo de todos os 10.000 acessos")
    fig.savefig(out / "enderecos_tempo.png")
    plt.close(fig)



def gerar_mapas(out, summaries, representatives):
    out = pasta_figuras(out, "mapas_calor")
    plt.rcParams.update({"font.size": 10, "figure.dpi": 140})
    selected = ["aleatorio", "temporal_080", "espacial_080", "quente_080", "misto_padrao", "espacial_100"]
    fig, axes = plt.subplots(3, 2, figsize=(13, 13), layout="constrained")
    for name, ax in zip(selected, axes.flat):
        desenhar_mapa(ax, *representatives[name])
    fig.suptitle("Mesma repetição usada no cálculo | blocos reais mais ativos + Outros\n"
                 "Cores em escala logarítmica comum (1 a 50 acessos por janela de 50)")
    fig.colorbar(matplotlib.cm.ScalarMappable(norm=LogNorm(1,50), cmap="magma"),
                 ax=list(axes.flat), label="Acessos por janela", shrink=.5)
    fig.savefig(out / "painel_mapas.png")
    plt.close(fig)
    for name, (pattern, rate, label) in representatives.items():
        fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
        cax = desenhar_mapa(ax, pattern, rate, label)
        fig.colorbar(cax, ax=ax, label="Acessos por janela (escala log)")
        fig.savefig(out / f"{name}.png")
        plt.close(fig)


def desenhar_mapa(ax, pattern, rate, label):
    matrix, labels = mapa_temporal_blocos(pattern, CONFIG["bloco_tamanho"], CONFIG["janela_heatmap"], CONFIG["max_linhas_heatmap"])
    # Outros não recebe a mesma cor de um único bloco: são totais não comparáveis.
    shown = matrix[:-1] if labels[-1] == "Outros" else matrix
    shown_labels = labels[:len(shown)]
    cax = ax.imshow(np.ma.masked_equal(shown, 0), origin="lower", aspect="auto",
                    cmap="magma", norm=LogNorm(1,50), interpolation="nearest")
    ax.set_facecolor("#efefef")
    ticks = list(range(0, len(shown), max(1, len(shown)//6)))
    ax.set_yticks(ticks, [shown_labels[i] for i in ticks])
    omitted = int(matrix[-1].sum()) if labels[-1] == "Outros" else 0
    ax.set(title=f"{label} | HR {rate:.2%}\nOutros: {omitted} acessos ({omitted/len(pattern):.1%}), fora das cores",
           xlabel="Janela temporal (50 acessos)", ylabel="ID do bloco (linhas sem escala de distância)")
    return cax


