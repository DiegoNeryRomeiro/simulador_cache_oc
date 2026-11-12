"""
Atividade 3 - Avaliacao de desempenho de cache via Simulacao de Monte Carlo.

Como rodar (na mesma pasta do cache_simulator_GUI.py):
    python analise_monte_carlo.py                 # 100 simulacoes por cenario (o que a atividade pede)
    python analise_monte_carlo.py --sims 20       # teste rapido

O que ele faz:
  1) Usa simulacao_monte_carlo() (com retornar_taxas=True) para obter a taxa de
     acerto de CADA uma das N simulacoes de cada cenario.
  2) Calcula media, variancia, desvio, CV, quantis, IQR, outliers (criterio de Tukey)
     e o desempenho nos piores/melhores casos.
  3) Salva CSVs e graficos na pasta resultados_monte_carlo/.

Experimentos:
  A) Politica de substituicao x associatividade   (cache fixa)
  B) Tamanho da cache x associatividade           (politica LRU)
"""
import argparse
import os
import random
import time

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

# Importa o simulador 
   
import cache_aprimorado as sim

plt.switch_backend("Agg")  # so salva PNG, nao abre janela (o modulo acima forca TkAgg)


# Parametros fixos do carregamento 

MEMORY_SIZE = 2 ** 20                       # 1 MB de RAM
PROBS = (0.20, 0.20, 0.40)                  # temporal, espacial, hot regions (o resto = aleatorio puro)
REGIOES_QUENTES = [64, 1024, 8192, 32768, 131072, 262144, 524288, 786432, 983040]
SEED = 42                                   # reprodutibilidade

POLITICAS = ["FIFO", "LRU", "LFU", "Random"]
ASSOCS_A = [1, 2, 4, 8, 16]                 # Experimento A
CACHES_B = [2048, 4096, 8192, 16384, 32768]  # Experimento B
ASSOCS_B = [1, 4, 16]
POLITICA_B = "LRU"

PASTA = "resultados_monte_carlo"


# Estatistica
def resumo_estatistico(taxas):
    x = np.asarray(taxas, dtype=float)
    n = len(x)
    media = x.mean()
    var = x.var(ddof=1)                     # variancia amostral
    std = x.std(ddof=1)
    q1, med, q3 = np.percentile(x, [25, 50, 75])
    iqr = q3 - q1
    lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    out_inf = x[x < lim_inf]
    out_sup = x[x > lim_sup]
    k = max(1, int(round(0.05 * n)))        # 5% piores / melhores
    ordenado = np.sort(x)
    skew = ((x - media) ** 3).mean() / (x.std(ddof=0) ** 3) if std > 0 else 0.0
    return {
        "n": n,
        "media": media,
        "ic95_meia_largura": 1.96 * std / np.sqrt(n),
        "variancia": var,
        "desvio": std,
        "cv_pct": 100 * std / media if media > 0 else 0.0,
        "min": x.min(),
        "p5": np.percentile(x, 5),
        "mediana": med,
        "p95": np.percentile(x, 95),
        "max": x.max(),
        "amplitude": x.max() - x.min(),
        "iqr": iqr,
        "assimetria": skew,
        "n_outliers_inf": len(out_inf),
        "n_outliers_sup": len(out_sup),
        "media_outliers": np.concatenate([out_inf, out_sup]).mean() if (len(out_inf) + len(out_sup)) else np.nan,
        "media_piores5pct": ordenado[:k].mean(),
        "media_melhores5pct": ordenado[-k:].mean(),
        "queda_pior_caso_pp": 100 * (media - x.min()),   # em pontos percentuais
    }


# Execucao dos cenarios

def rodar_cenario(rotulo, sims, acessos, cache_size, assoc, bloco, politica):
    random.seed(SEED)  # mesma semente => mesmos padroes de acesso em todos os cenarios 
    taxas = sim.simulacao_monte_carlo(
        sims, acessos, MEMORY_SIZE, cache_size, assoc, REGIOES_QUENTES, PROBS,
        bloco, politica, retornar_taxas=True, verbose=False,
    )
    r = resumo_estatistico(taxas)
    r.update({"cenario": rotulo, "cache_bytes": cache_size, "associatividade": assoc,
              "bloco": bloco, "politica": politica})
    print(f"{rotulo:<28} media={r['media']:.4f}  std={r['desvio']:.5f}  "
          f"min={r['min']:.4f}  max={r['max']:.4f}  outliers={r['n_outliers_inf'] + r['n_outliers_sup']}")
    return taxas, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", type=int, default=100, help="simulacoes por cenario (atividade pede 100)")
    ap.add_argument("--acessos", type=int, default=10000, help="acessos de CPU por simulacao")
    ap.add_argument("--bloco", type=int, default=64, help="tamanho do bloco em bytes")
    ap.add_argument("--cache-a", type=int, default=8192, help="tamanho da cache no experimento A")
    args = ap.parse_args()

    os.makedirs(PASTA, exist_ok=True)
    t0 = time.time()
    dados = {}      # rotulo -> lista de taxas
    linhas = []     # resumos

    print(f"\n=== Experimento A: politica x associatividade (cache {args.cache_a} B, bloco {args.bloco} B) ===")
    for pol in POLITICAS:
        for a in ASSOCS_A:
            rot = f"A|{pol}|{a}-way"
            taxas, r = rodar_cenario(rot, args.sims, args.acessos, args.cache_a, a, args.bloco, pol)
            r["experimento"] = "A"
            dados[rot] = taxas
            linhas.append(r)

    print(f"\n=== Experimento B: tamanho da cache x associatividade (politica {POLITICA_B}, bloco {args.bloco} B) ===")
    for c in CACHES_B:
        for a in ASSOCS_B:
            rot = f"B|{c}B|{a}-way"
            taxas, r = rodar_cenario(rot, args.sims, args.acessos, c, a, args.bloco, POLITICA_B)
            r["experimento"] = "B"
            dados[rot] = taxas
            linhas.append(r)

    salvar_csvs(linhas, dados)
    gerar_graficos(linhas, dados, args)
    print(f"\nPronto em {time.time() - t0:.1f}s. Arquivos em '{PASTA}/'.")



# Saidas

def salvar_csvs(linhas, dados):
    cols = ["experimento", "cenario", "politica", "cache_bytes", "associatividade", "bloco", "n", "media",
            "ic95_meia_largura", "variancia", "desvio", "cv_pct", "min", "p5", "mediana", "p95", "max",
            "amplitude", "iqr", "assimetria", "n_outliers_inf", "n_outliers_sup", "media_outliers",
            "media_piores5pct", "media_melhores5pct", "queda_pior_caso_pp"]
    with open(os.path.join(PASTA, "resumo_por_cenario.csv"), "w", encoding="utf-8") as f:
        f.write(",".join(cols) + "\n")
        for r in linhas:
            f.write(",".join(str(r[c]) if isinstance(r[c], str) else f"{r[c]:.8g}" for c in cols) + "\n")

    with open(os.path.join(PASTA, "taxas_brutas.csv"), "w", encoding="utf-8") as f:
        f.write("cenario,simulacao,taxa_acerto\n")
        for rot, taxas in dados.items():
            for i, t in enumerate(taxas, 1):
                f.write(f"{rot},{i},{t:.8f}\n")


def _boxplot(ax, rotulos, series, titulo, cores=None):
    bp = ax.boxplot(series, patch_artist=True, showmeans=True, flierprops=dict(marker="o", markersize=4))
    ax.set_xticks(range(1, len(rotulos) + 1))
    ax.set_xticklabels(rotulos)
    for i, box in enumerate(bp["boxes"]):
        box.set_facecolor(cores[i] if cores else "#9ecae1")
        box.set_alpha(0.8)
    ax.set_title(titulo)
    ax.set_ylabel("Taxa de acerto")
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)


def gerar_graficos(linhas, dados, args):
    cores_pol = {"FIFO": "#4c78a8", "LRU": "#54a24b", "LFU": "#f58518", "Random": "#b279a2"}

    # 1) Boxplots do experimento A: um painel por politica
    fig, axs = plt.subplots(1, 4, figsize=(18, 4.5), sharey=True)
    for ax, pol in zip(axs, POLITICAS):
        _boxplot(ax, [f"{a}-way" for a in ASSOCS_A], [dados[f"A|{pol}|{a}-way"] for a in ASSOCS_A],
                 pol, [cores_pol[pol]] * len(ASSOCS_A))
    fig.suptitle(f"Distribuicao da taxa de acerto - {args.sims} simulacoes/cenario (cache {args.cache_a} B)")
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, "A1_boxplot_politica_assoc.png"), dpi=140)
    plt.close(fig)

    # 2) Media +- desvio vs associatividade, uma linha por politica
    fig, ax = plt.subplots(figsize=(8, 5))
    for pol in POLITICAS:
        rs = [r for r in linhas if r["experimento"] == "A" and r["politica"] == pol]
        ax.errorbar(range(len(ASSOCS_A)), [r["media"] for r in rs], yerr=[r["desvio"] for r in rs],
                    marker="o", capsize=4, label=pol, color=cores_pol[pol])
    ax.set_xticks(range(len(ASSOCS_A)))
    ax.set_xticklabels([f"{a}-way" for a in ASSOCS_A])
    ax.set_xlabel("Associatividade")
    ax.set_ylabel("Taxa de acerto (media +- 1 desvio)")
    ax.set_title("Experimento A: media e dispersao por politica")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, "A2_media_desvio.png"), dpi=140)
    plt.close(fig)

    # 3) Histogramas (4 cenarios representativos) com media e outliers marcados
    escolhidos = [f"A|LRU|1-way", f"A|LRU|16-way", f"A|Random|16-way", f"A|FIFO|16-way"]
    fig, axs = plt.subplots(2, 2, figsize=(11, 7))
    for ax, rot in zip(axs.ravel(), escolhidos):
        x = np.array(dados[rot])
        ax.hist(x, bins=15, color="#9ecae1", edgecolor="white")
        ax.axvline(x.mean(), color="red", lw=2, label=f"media {x.mean():.4f}")
        r = next(r for r in linhas if r["cenario"] == rot)
        ax.set_title(f"{rot[2:]} | std={r['desvio']:.5f} | outliers={r['n_outliers_inf'] + r['n_outliers_sup']}")
        ax.set_xlabel("Taxa de acerto")
        ax.set_ylabel("Frequencia")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, "A3_histogramas.png"), dpi=140)
    plt.close(fig)

    # 4) Experimento B: tamanho da cache x associatividade (media +- desvio)
    fig, ax = plt.subplots(figsize=(8, 5))
    for a in ASSOCS_B:
        rs = [r for r in linhas if r["experimento"] == "B" and r["associatividade"] == a]
        ax.errorbar(range(len(CACHES_B)), [r["media"] for r in rs], yerr=[r["desvio"] for r in rs],
                    marker="o", capsize=4, label=f"{a}-way")
    ax.set_xticks(range(len(CACHES_B)))
    ax.set_xticklabels([f"{c // 1024} KB" for c in CACHES_B])
    ax.set_xlabel("Tamanho da cache")
    ax.set_ylabel("Taxa de acerto (media +- 1 desvio)")
    ax.set_title(f"Experimento B: tamanho da cache x associatividade ({POLITICA_B})")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, "B1_cache_x_assoc.png"), dpi=140)
    plt.close(fig)

    # 5) Boxplot do experimento B (16-way) para ver a robustez ao crescer a cache
    fig, ax = plt.subplots(figsize=(8, 4.5))
    _boxplot(ax, [f"{c // 1024} KB" for c in CACHES_B], [dados[f"B|{c}B|4-way"] for c in CACHES_B],
             f"Experimento B: distribuicao por tamanho de cache (4-way, {POLITICA_B})")
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, "B2_boxplot_cache_4way.png"), dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
