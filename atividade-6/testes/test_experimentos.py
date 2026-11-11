import ast
import csv
import math
import random
import sys
import tempfile
import unittest
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from cache_core import (  # noqa: E402
    CacheConfig,
    CacheMemory,
    generate_random_pattern,
    generate_realistic_pattern,
    simulate,
    write_access_csv,
)
from gerar_mapas_calor import heatmap  # noqa: E402


class PatternTests(unittest.TestCase):
    def test_random_addresses_are_valid(self):
        addresses = generate_random_pattern(500, 2**20, 42)
        self.assertEqual(len(addresses), 500)
        self.assertTrue(all(0 <= address < 2**20 for address in addresses))

    def test_realistic_pattern_is_reproducible(self):
        args = (500, 2**20, 42)
        self.assertEqual(generate_realistic_pattern(*args), generate_realistic_pattern(*args))

    def test_patterns_are_not_accidentally_identical(self):
        random_pattern = generate_random_pattern(500, 2**20, 42)
        realistic_pattern = generate_realistic_pattern(500, 2**20, 42)
        self.assertNotEqual(random_pattern, realistic_pattern)


class CacheTests(unittest.TestCase):
    def test_metrics_and_rates(self):
        config = CacheConfig(2**20, 4096, 32, 4, "LRU")
        result = simulate(config, [0, 1, 32, 0, 64, 0])
        self.assertEqual(result.hits + result.misses, 6)
        self.assertTrue(math.isclose(result.hit_rate_percent + result.miss_rate_percent, 100.0))
        self.assertEqual(len(result.cumulative_hit_rate), 6)

    def test_same_hardware_configuration(self):
        random_config = CacheConfig(2**20, 4096, 32, 4, "LRU")
        realistic_config = CacheConfig(2**20, 4096, 32, 4, "LRU")
        self.assertEqual(random_config, realistic_config)
        self.assertEqual(random_config.lines, 128)
        self.assertEqual(random_config.sets, 32)

    def test_all_original_policies_keep_consistent_counts(self):
        addresses = generate_random_pattern(200, 2**20, 42)
        for policy in ("FIFO", "LRU", "LFU", "Random"):
            with self.subTest(policy=policy):
                result = simulate(CacheConfig(2**20, 4096, 32, 4, policy), addresses, seed=42)
                self.assertEqual(result.hits + result.misses, len(addresses))

    def test_original_lru_core_matches_headless_core(self):
        source_path = ROOT.parent / "cache_simulator_GUI.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        wanted = {
            "CacheLine", "EvictionPolicy", "FIFO", "LRU", "LFU", "RandomPolicy",
            "CacheSet", "CacheMemory",
        }
        nodes = [
            node for node in tree.body
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in wanted
        ]
        namespace = {
            "ABC": ABC, "abstractmethod": abstractmethod, "List": List,
            "Tuple": Tuple, "random": random, "math": math,
        }
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source_path), "exec"), namespace)
        original = namespace["CacheMemory"](4096, 32, 4, "LRU")
        headless = CacheMemory(CacheConfig(2**20, 4096, 32, 4, "LRU"))
        addresses = generate_realistic_pattern(1000, 2**20, 42)
        for address in addresses:
            original.request_access(address)
            headless.request_access(address)
        self.assertEqual((original.hits, original.misses), (headless.hits, headless.misses))


class HeatmapAndCsvTests(unittest.TestCase):
    def test_heatmap_uses_recorded_window_and_region(self):
        rows = [
            {"regiao": "0", "janela": "0"},
            {"regiao": "0", "janela": "0"},
            {"regiao": "1", "janela": "1"},
        ]
        matrix = heatmap(rows, windows=2, regions=2)
        self.assertEqual(matrix.tolist(), [[2, 0], [0, 1]])

    def test_sequence_csv_integrity(self):
        addresses = generate_random_pattern(10, 2**20, 42)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "acessos.csv"
            write_access_csv(path, addresses, 32, 4096, 100)
            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 10)
            self.assertEqual([int(row["endereco"]) for row in rows], addresses)
            self.assertTrue(all(0 <= int(row["endereco"]) < 2**20 for row in rows))

    def test_final_artifacts_are_consistent(self):
        result_dir = ROOT / "resultados"
        with (result_dir / "comparacao_resultados.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual({row["cenario"] for row in rows}, {"A", "B"})
        for row in rows:
            self.assertEqual(int(row["hits"]) + int(row["misses"]), int(row["acessos"]))
            self.assertTrue(math.isclose(float(row["hit_rate_percent"]) + float(row["miss_rate_percent"]), 100.0, abs_tol=1e-6))
        for filename in ("acessos_aleatorios.csv", "acessos_realistas.csv"):
            with (result_dir / filename).open(encoding="utf-8", newline="") as handle:
                self.assertEqual(sum(1 for _ in csv.DictReader(handle)), 10_000)


if __name__ == "__main__":
    unittest.main()
