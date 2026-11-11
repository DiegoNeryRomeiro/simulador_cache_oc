import csv
import math
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from cache_experimentos import (  # noqa: E402
    CSV_FIELDS,
    CacheConfig,
    CacheMemory,
    execute_experiment,
    generate_realistic_pattern,
)


class ConfigurationTests(unittest.TestCase):
    def test_lines_and_sets(self):
        config = CacheConfig(2**20, 1024, 16, 4, "LRU")
        config.validate()
        self.assertEqual(config.lines, 64)
        self.assertEqual(config.sets, 16)

    def test_invalid_associativity_is_rejected(self):
        with self.assertRaises(ValueError):
            CacheConfig(2**20, 1024, 16, 3, "LRU").validate()

    def test_invalid_set_count_is_rejected(self):
        with self.assertRaises(ValueError):
            CacheConfig(2**20, 1024, 256, 8, "LRU").validate()


class SimulationTests(unittest.TestCase):
    def test_known_hit_miss_sequence(self):
        cache = CacheMemory(CacheConfig(256, 16, 4, 1, "LRU"))
        for address in (0, 1, 4, 0, 64, 0):
            cache.request_access(address)
        self.assertEqual((cache.hits, cache.misses), (2, 4))
        self.assertTrue(math.isclose(cache.hit_rate, 2 / 6))

    def test_fixed_seed_is_reproducible(self):
        args = (1000, 2**20, (64, 1024), (0.2, 0.2, 0.4), 2026)
        self.assertEqual(generate_realistic_pattern(*args), generate_realistic_pattern(*args))

    def test_different_seed_changes_pattern(self):
        first = generate_realistic_pattern(100, 2**20, (64,), (0.2, 0.2, 0.4), 1)
        second = generate_realistic_pattern(100, 2**20, (64,), (0.2, 0.2, 0.4), 2)
        self.assertNotEqual(first, second)


class CsvTests(unittest.TestCase):
    def test_csv_integrity_and_rates(self):
        scenarios = [("T1", CacheConfig(2**20, 256, 16, 2, "LRU"))]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.csv"
            results = execute_experiment(scenarios, 200, 2026, path)
            self.assertEqual(results[0].hits + results[0].misses, 200)
            self.assertTrue(
                math.isclose(
                    results[0].hit_rate_percent + results[0].miss_rate_percent,
                    100.0,
                )
            )
            with path.open(encoding="utf-8", newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                rows = list(reader)
            self.assertEqual(tuple(reader.fieldnames or ()), CSV_FIELDS)
            self.assertEqual(len(rows), 1)
            self.assertEqual(int(rows[0]["acessos"]), 200)

    def test_generated_csv_artifacts(self):
        result_dir = Path(__file__).resolve().parents[1] / "resultados"
        expected_rows = {"linhas.csv": 4, "associatividade.csv": 4, "blocos.csv": 5}
        for filename, row_count in expected_rows.items():
            with self.subTest(filename=filename):
                with (result_dir / filename).open(encoding="utf-8", newline="") as csv_file:
                    reader = csv.DictReader(csv_file)
                    rows = list(reader)
                self.assertEqual(tuple(reader.fieldnames or ()), CSV_FIELDS)
                self.assertEqual(len(rows), row_count)
                for row in rows:
                    self.assertEqual(int(row["hits"]) + int(row["misses"]), int(row["acessos"]))
                    self.assertEqual(
                        int(row["numero_linhas"]),
                        int(row["cache_bytes"]) // int(row["bloco_bytes"]),
                    )
                    self.assertEqual(
                        int(row["numero_conjuntos"]),
                        int(row["numero_linhas"]) // int(row["associatividade"]),
                    )
                    self.assertTrue(
                        math.isclose(
                            float(row["hit_rate_percent"])
                            + float(row["miss_rate_percent"]),
                            100.0,
                            abs_tol=1e-6,
                        )
                    )


if __name__ == "__main__":
    unittest.main()
