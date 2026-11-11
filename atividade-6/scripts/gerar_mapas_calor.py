#!/usr/bin/env python3
"""Gera mapas de calor comparáveis a partir das sequências gravadas."""

import argparse
import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-atividade-6")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize

ROOT = Path(__file__).resolve().parents[1]


def read_accesses(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"CSV sem acessos: {path}")
    return rows


def heatmap(rows: list[dict[str, str]], windows: int, regions: int) -> np.ndarray:
    matrix = np.zeros((regions, windows), dtype=int)
    for row in rows:
        region = int(row["regiao"])
        window = int(row["janela"])
        if 0 <= region < regions and 0 <= window < windows:
            matrix[region, window] += 1
    return matrix


def save_map(matrix: np.ndarray, output: Path, title: str, norm: Normalize, region_bytes: int, window_size: int) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    image = ax.imshow(matrix, origin="lower", aspect="auto", cmap="magma", norm=norm)
    ax.set_title(title)
    ax.set_xlabel(f"Janela temporal ({window_size} acessos)")
    ax.set_ylabel(f"Região da memória ({region_bytes} bytes por região)")
    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Quantidade de acessos")
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Mapa gravado em: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resultados", type=Path, default=ROOT / "resultados")
    parser.add_argument("--saida-dir", type=Path, default=ROOT / "mapas_calor")
    parser.add_argument("--memoria", type=int, default=2**20)
    args = parser.parse_args()
    random_rows = read_accesses(args.resultados / "acessos_aleatorios.csv")
    realistic_rows = read_accesses(args.resultados / "acessos_realistas.csv")
    region_bytes = int(random_rows[0]["regiao_bytes"])
    max_window = max(int(row["janela"]) for row in random_rows + realistic_rows) + 1
    regions = (args.memoria + region_bytes - 1) // region_bytes
    random_matrix = heatmap(random_rows, max_window, regions)
    realistic_matrix = heatmap(realistic_rows, max_window, regions)
    vmax = max(int(random_matrix.max()), int(realistic_matrix.max()))
    norm = Normalize(vmin=0, vmax=max(1, vmax))
    # A janela foi registrada no CSV comparativo para manter a documentação
    # independente dos valores padrão usados pela linha de comando.
    comparison_path = args.resultados / "comparacao_resultados.csv"
    with comparison_path.open(encoding="utf-8", newline="") as handle:
        comparison_row = next(csv.DictReader(handle))
    window_size = int(comparison_row["janela_acessos"])
    save_map(random_matrix, args.saida_dir / "heatmap_aleatorio.png", "Mapa de calor — acessos aleatórios", norm, region_bytes, window_size)
    save_map(realistic_matrix, args.saida_dir / "heatmap_realista.png", "Mapa de calor — acessos realistas sintéticos", norm, region_bytes, window_size)


if __name__ == "__main__":
    main()
