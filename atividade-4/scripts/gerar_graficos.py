#!/usr/bin/env python3
"""Gera os tres graficos academicos a partir dos CSVs medidos."""

import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-atividade-4")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]


def read_csv(filename: str) -> list[dict[str, str]]:
    path = ROOT / "resultados" / filename
    with path.open(encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    if not rows:
        raise ValueError(f"CSV sem dados: {path}")
    return rows


def plot(rows, x_field, output, title, x_label):
    x_values = [int(row[x_field]) for row in rows]
    rates = [float(row["hit_rate_percent"]) for row in rows]
    labels = [row["experimento"] for row in rows]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_values, rates, marker="o", linewidth=2, color="#2457a7", label="LRU")
    for x_value, rate, label in zip(x_values, rates, labels):
        ax.annotate(
            f"{label}: {rate:.2f}%",
            (x_value, rate),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            fontsize=9,
        )
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Taxa de acerto (%)")
    ax.set_xticks(x_values)
    spread = max(rates) - min(rates)
    padding = max(0.8, spread * 0.18)
    ax.set_ylim(min(rates) - padding, max(rates) + padding)
    ax.margins(x=0.06)
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Grafico gravado em: {output}")


def main() -> None:
    plot(
        read_csv("linhas.csv"),
        "numero_linhas",
        ROOT / "graficos/linhas_vs_hit_rate.png",
        "Influência do número de linhas na taxa de acerto",
        "Número de linhas da cache",
    )
    plot(
        read_csv("associatividade.csv"),
        "associatividade",
        ROOT / "graficos/associatividade_vs_hit_rate.png",
        "Influência da associatividade na taxa de acerto",
        "Associatividade (vias por conjunto)",
    )
    plot(
        read_csv("blocos.csv"),
        "bloco_bytes",
        ROOT / "graficos/blocos_vs_hit_rate.png",
        "Influência do tamanho do bloco na taxa de acerto",
        "Tamanho do bloco (bytes)",
    )


if __name__ == "__main__":
    main()
