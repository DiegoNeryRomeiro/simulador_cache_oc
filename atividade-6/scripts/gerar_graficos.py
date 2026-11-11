#!/usr/bin/env python3
"""Gera os gráficos comparativos da Atividade 6."""

import argparse
import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-atividade-6")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def read_comparison(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 2:
        raise ValueError("o CSV comparativo deve conter os dois cenários")
    return rows


def read_access(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Gráfico gravado em: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resultados", type=Path, default=ROOT / "resultados")
    parser.add_argument("--saida-dir", type=Path, default=ROOT / "graficos")
    args = parser.parse_args()
    rows = read_comparison(args.resultados / "comparacao_resultados.csv")
    labels = [row["padrao"].replace("_", " ").title() for row in rows]
    colors = ["#6b7280", "#b45309"]
    rates = [float(row["hit_rate_percent"]) for row in rows]
    hits = [int(row["hits"]) for row in rows]
    misses = [int(row["misses"]) for row in rows]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, rates, color=colors)
    ax.set_title("Taxa de acerto por padrão de acesso")
    ax.set_ylabel("Taxa de acerto (%)")
    ax.set_ylim(0, max(rates) * 1.25)
    for bar, value in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.5, f"{value:.2f}%", ha="center")
    save(fig, args.saida_dir / "comparacao_hit_rate.png")

    positions = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(positions - width / 2, hits, width, label="Hits", color="#15803d")
    ax.bar(positions + width / 2, misses, width, label="Misses", color="#b91c1c")
    ax.set_xticks(positions, labels)
    ax.set_ylabel("Quantidade de acessos")
    ax.set_title("Hits e misses por padrão")
    ax.legend()
    save(fig, args.saida_dir / "comparacao_hits_misses.png")

    random_rows = read_access(args.resultados / "acessos_aleatorios.csv")
    realistic_rows = read_access(args.resultados / "acessos_realistas.csv")
    regions = max(int(row["regiao"]) for row in random_rows + realistic_rows) + 1
    random_counts = np.bincount([int(row["regiao"]) for row in random_rows], minlength=regions)
    realistic_counts = np.bincount([int(row["regiao"]) for row in realistic_rows], minlength=regions)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(random_counts, label="Aleatório", color="#6b7280", linewidth=1)
    ax.plot(realistic_counts, label="Realista sintético", color="#b45309", linewidth=1)
    ax.set_xlabel("Índice da região de 4 KiB")
    ax.set_ylabel("Quantidade de acessos")
    ax.set_title("Distribuição espacial dos acessos")
    ax.legend()
    ax.grid(alpha=0.25)
    save(fig, args.saida_dir / "distribuicao_acessos.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    for access_rows, label, color in (
        (random_rows, "Aleatório", "#6b7280"),
        (realistic_rows, "Realista sintético", "#b45309"),
    ):
        cumulative_path = args.resultados / f"taxa_acumulada_{'aleatorio' if label == 'Aleatório' else 'realista'}.csv"
        with cumulative_path.open(encoding="utf-8", newline="") as handle:
            values = [float(row["hit_rate_percent"]) for row in csv.DictReader(handle)]
        ax.plot(range(1, len(values) + 1), values, label=label, color=color, linewidth=1)
    ax.set_xlabel("Número do acesso")
    ax.set_ylabel("Taxa de acerto acumulada (%)")
    ax.set_title("Evolução da taxa de acerto")
    ax.set_ylim(0, 100)
    ax.grid(alpha=0.25)
    ax.legend()
    save(fig, args.saida_dir / "evolucao_hit_rate.png")


if __name__ == "__main__":
    main()
