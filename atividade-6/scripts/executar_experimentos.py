#!/usr/bin/env python3
"""Executa os cenários aleatório e realista com hardware idêntico."""

import argparse
import csv
from pathlib import Path

from cache_core import (
    CacheConfig,
    HOT_REGIONS,
    REALISTIC_PROBABILITIES,
    generate_random_pattern,
    generate_realistic_pattern,
    result_row,
    simulate,
    write_access_csv,
    write_cumulative_csv,
    write_comparison_csv,
)

ROOT = Path(__file__).resolve().parents[1]


def run(accesses: int, seed: int, output_dir: Path, window_size: int, region_bytes: int) -> list[dict]:
    config = CacheConfig(2**20, 4096, 32, 4, "LRU")
    config.validate()
    random_addresses = generate_random_pattern(accesses, config.memory_bytes, seed)
    realistic_addresses = generate_realistic_pattern(
        accesses, config.memory_bytes, seed, REALISTIC_PROBABILITIES, HOT_REGIONS
    )
    scenarios = (
        ("A", "aleatorio", random_addresses, None),
        ("B", "realista_sintetico", realistic_addresses, REALISTIC_PROBABILITIES),
    )
    rows = []
    for scenario, name, addresses, probabilities in scenarios:
        result = simulate(config, addresses)
        write_access_csv(
            output_dir / ("acessos_aleatorios.csv" if scenario == "A" else "acessos_realistas.csv"),
            addresses,
            config.block_bytes,
            region_bytes,
            window_size,
        )
        write_cumulative_csv(
            output_dir / ("taxa_acumulada_aleatorio.csv" if scenario == "A" else "taxa_acumulada_realista.csv"),
            result.cumulative_hit_rate,
        )
        rows.append(result_row(scenario, name, config, seed, result, probabilities, window_size, region_bytes))
    write_comparison_csv(output_dir / "comparacao_resultados.csv", rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acessos", type=int, default=10_000)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--janela", type=int, default=100)
    parser.add_argument("--regiao", type=int, default=4096)
    parser.add_argument("--saida-dir", type=Path, default=ROOT / "resultados")
    args = parser.parse_args()
    rows = run(args.acessos, args.semente, args.saida_dir, args.janela, args.regiao)
    for row in rows:
        print(
            f"{row['cenario']} ({row['padrao']}): hits={row['hits']}, "
            f"misses={row['misses']}, hit_rate={row['hit_rate_percent']}%"
        )
    print(f"CSV comparativo: {args.saida_dir / 'comparacao_resultados.csv'}")


if __name__ == "__main__":
    main()
