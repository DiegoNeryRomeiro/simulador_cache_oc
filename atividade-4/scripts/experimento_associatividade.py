#!/usr/bin/env python3
"""Experimento B: influencia do grau de associatividade."""

import argparse
from pathlib import Path

from cache_experimentos import CacheConfig, execute_experiment, print_results


ROOT = Path(__file__).resolve().parents[1]


def scenarios() -> list[tuple[str, CacheConfig]]:
    return [
        (f"B{index}", CacheConfig(2**20, 1024, 16, ways, "LRU"))
        for index, ways in enumerate((1, 2, 4, 8), start=1)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acessos", type=int, default=10_000)
    parser.add_argument("--semente", type=int, default=2026)
    parser.add_argument(
        "--saida", type=Path, default=ROOT / "resultados/associatividade.csv"
    )
    args = parser.parse_args()
    results = execute_experiment(scenarios(), args.acessos, args.semente, args.saida)
    print_results(results, args.saida)


if __name__ == "__main__":
    main()
