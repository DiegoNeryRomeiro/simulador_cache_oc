#!/usr/bin/env python3
"""Gera e exporta os dois padrões de acesso da Atividade 6."""

import argparse
import csv
from pathlib import Path

from cache_core import (
    HOT_REGIONS,
    REALISTIC_PROBABILITIES,
    generate_random_pattern,
    generate_realistic_pattern,
    write_access_csv,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acessos", type=int, default=10_000)
    parser.add_argument("--memoria", type=int, default=2**20)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--janela", type=int, default=100)
    parser.add_argument("--regiao", type=int, default=4096)
    parser.add_argument("--saida-dir", type=Path, default=ROOT / "resultados")
    args = parser.parse_args()

    random_addresses = generate_random_pattern(args.acessos, args.memoria, args.semente)
    realistic_addresses = generate_realistic_pattern(
        args.acessos, args.memoria, args.semente, REALISTIC_PROBABILITIES, HOT_REGIONS
    )
    for path, addresses in (
        (args.saida_dir / "acessos_aleatorios.csv", random_addresses),
        (args.saida_dir / "acessos_realistas.csv", realistic_addresses),
    ):
        write_access_csv(path, addresses, 32, args.regiao, args.janela)
        print(f"{path}: {len(addresses)} acessos")


if __name__ == "__main__":
    main()
