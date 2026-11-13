import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import math
import random
import unittest
import ast
from abc import ABC, abstractmethod
from typing import List, Tuple

from cache_core import (CacheMemory, REGIOES_QUENTES, gerar_padrao_realista,
                        mapa_temporal_blocos, validar_probabilidades)
from configuracao import cenarios


class CacheTests(unittest.TestCase):
    @staticmethod
    def original():
        original_path = Path(__file__).resolve().parents[2] / "cache_simulator_GUI.py"
        tree = ast.parse(original_path.read_text(encoding="utf-8"))
        names = {"CacheLine", "EvictionPolicy", "FIFO", "LRU", "LFU", "RandomPolicy",
                 "CacheSet", "CacheMemory", "gerar_padrao_realista"}
        nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names]
        namespace = dict(ABC=ABC, abstractmethod=abstractmethod, List=List, Tuple=Tuple,
                         random=random, math=math)
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(original_path), "exec"), namespace)
        return namespace

    def test_lru_matches_original_for_all_scenarios(self):
        original_class = self.original()["CacheMemory"]
        for name, probs, _ in cenarios():
            with self.subTest(cenario=name):
                pattern = gerar_padrao_realista(500, 2**20, REGIOES_QUENTES, probs, random.Random(42))
                original = original_class(8192, 16, 16, "LRU")
                headless = CacheMemory(8192, 16, 16, "LRU")
                self.assertEqual([original.request_access(a) for a in pattern],
                                 [headless.request_access(a) for a in pattern])

    def test_generator_matches_original_for_all_scenarios(self):
        generator = self.original()["gerar_padrao_realista"]
        state = random.getstate()
        try:
            for name, probs, _ in cenarios():
                with self.subTest(cenario=name):
                    random.seed(42)
                    expected = generator(500, 2**20, REGIOES_QUENTES, probs)
                    actual = gerar_padrao_realista(500, 2**20, REGIOES_QUENTES, probs, random.Random(42))
                    self.assertEqual(actual, expected)
        finally:
            random.setstate(state)

    def test_cold_hit_and_fields(self):
        cache = CacheMemory(128, 16, 2, "LRU")
        self.assertEqual(cache.calculate_address_fields(0xAB), (2, 2, 11))
        self.assertFalse(cache.request_access(160))
        self.assertTrue(cache.request_access(175))
        self.assertEqual((cache.hits, cache.misses, cache.hit_rate), (1, 1, .5))

    def test_fifo_lru_victims(self):
        for policy, expected in [("FIFO", False), ("LRU", True)]:
            cache = CacheMemory(32, 16, 2, policy)
            for a in (0, 16, 0, 32):
                cache.request_access(a)
            self.assertEqual(cache.request_access(0), expected)

    def test_lfu_victim(self):
        cache = CacheMemory(32, 16, 2, "LFU")
        for a in (0, 0, 16, 32):
            cache.request_access(a)
        self.assertTrue(cache.request_access(0))
        self.assertFalse(cache.request_access(16))

    def test_random_accounting(self):
        cache = CacheMemory(32, 16, 2, "Random")
        for a in range(100):
            cache.request_access(a * 16)
        self.assertEqual(cache.hits + cache.misses, 100)
        self.assertTrue(all(line.valid_bit for line in cache.sets[0].lines))

    def test_invalid_architecture(self):
        for args in [(0, 16, 1), (-8, 2, 1), (128, 3, 1), (16, 16, 2)]:
            with self.assertRaises(ValueError):
                CacheMemory(*args, "LRU")

    def test_invalid_probabilities(self):
        for probs in [(-.1, 0, 0), (.5, .5, .1), (math.nan, 0, 0), (math.inf, 0, 0), (0, 0)]:
            with self.assertRaises(ValueError):
                validar_probabilidades(probs)

    def test_reproducibility_and_bounds(self):
        args = (1000, 2**20, REGIOES_QUENTES, (.2, .2, .4))
        a = gerar_padrao_realista(*args, rng=random.Random(42))
        b = gerar_padrao_realista(*args, rng=random.Random(42))
        self.assertEqual(a, b)
        self.assertTrue(all(0 <= x < 2**20 for x in a))

    def test_temporal_exactly_one_miss(self):
        pattern = gerar_padrao_realista(10000, 2**20, REGIOES_QUENTES, (1, 0, 0), random.Random(42))
        cache = CacheMemory(8192, 16, 16, "LRU")
        for a in pattern:
            cache.request_access(a)
        self.assertEqual(len(set(pattern)), 1)
        self.assertEqual((cache.hits, cache.misses), (9999, 1))

    def test_spatial_steps(self):
        pattern = gerar_padrao_realista(1000, 2**20, [], (0, 1, 0), random.Random(42))
        self.assertTrue(all(abs(a-b) <= 16 for a, b in zip(pattern, pattern[1:])))

    def test_hot_support_and_cold_misses(self):
        pattern = gerar_padrao_realista(10000, 2**20, REGIOES_QUENTES, (0, 0, 1), random.Random(42))
        support = {base + offset for base in REGIOES_QUENTES for offset in range(4)}
        self.assertTrue(set(pattern) <= support)
        self.assertEqual(len(set(a // 16 for a in pattern)), 9)
        cache = CacheMemory(8192, 16, 16, "LRU")
        for a in pattern:
            cache.request_access(a)
        self.assertEqual(cache.misses, 9)

    def test_heatmap_no_aliasing_partial_window(self):
        pattern = [0, 1024, 0, 1024, 32]
        matrix, labels = mapa_temporal_blocos(pattern, 16, janela=2)
        self.assertEqual(labels, ["0", "2", "64"])
        self.assertEqual(matrix.tolist(), [[1, 1, 0], [0, 0, 1], [1, 1, 0]])
        self.assertEqual(int(matrix.sum()), len(pattern))

    def test_heatmap_other_preserves_total(self):
        matrix, labels = mapa_temporal_blocos(list(range(100)), 1, janela=7, max_linhas=4)
        self.assertEqual(labels[-1], "Outros")
        self.assertEqual(int(matrix.sum()), 100)

    def test_invalid_hot_regions(self):
        for regions in ([], [2**20]):
            with self.assertRaises(ValueError):
                gerar_padrao_realista(10, 2**20, regions, (0, 0, 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
