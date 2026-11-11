"""Núcleo headless da Atividade 6.

As classes de cache reproduzem o núcleo de ``cache_simulator_GUI.py`` da
branch Versão-2026. A geração de padrões usa ``random.Random`` local para
permitir reprodutibilidade sem alterar o estado global do simulador.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Iterable, Sequence


POLICIES = ("FIFO", "LRU", "LFU", "Random")
HOT_REGIONS = (64, 1024, 8192, 32768, 131072, 262144, 524288, 786432, 983040)
REALISTIC_PROBABILITIES = (0.20, 0.20, 0.40)


def is_power_of_two(value: int) -> bool:
    return value > 0 and (value & (value - 1)) == 0


@dataclass(frozen=True)
class CacheConfig:
    memory_bytes: int
    cache_bytes: int
    block_bytes: int
    associativity: int
    policy: str = "LRU"

    @property
    def lines(self) -> int:
        return self.cache_bytes // self.block_bytes

    @property
    def sets(self) -> int:
        return self.lines // self.associativity

    def validate(self) -> None:
        for name in ("memory_bytes", "cache_bytes", "block_bytes", "associativity"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} deve ser inteiro positivo")
        if self.policy not in POLICIES:
            raise ValueError(f"política inválida: {self.policy}")
        if not is_power_of_two(self.memory_bytes):
            raise ValueError("a memória deve ter tamanho potência de dois")
        if not is_power_of_two(self.cache_bytes):
            raise ValueError("a cache deve ter tamanho potência de dois")
        if not is_power_of_two(self.block_bytes):
            raise ValueError("o bloco deve ter tamanho potência de dois")
        if not is_power_of_two(self.associativity):
            raise ValueError("a associatividade deve ser potência de dois")
        if self.cache_bytes >= self.memory_bytes:
            raise ValueError("a cache deve ser menor que a memória")
        if self.block_bytes > self.cache_bytes:
            raise ValueError("o bloco não pode ser maior que a cache")
        if self.cache_bytes % self.block_bytes:
            raise ValueError("cache e bloco devem ser divisíveis")
        if self.lines % self.associativity or self.sets < 1:
            raise ValueError("linhas devem ser múltiplas da associatividade")
        if not is_power_of_two(self.sets):
            raise ValueError("o número de conjuntos deve ser potência de dois")


@dataclass
class CacheLine:
    valid_bit: bool = False
    dirty_bit: bool = False
    tag: int = -1
    insertion_time: int = 0
    last_access_time: int = 0
    access_frequency: int = 0

    def update_access_metadata(self, current_time: int) -> None:
        self.last_access_time = current_time
        self.access_frequency += 1


class CacheSet:
    def __init__(self, associativity: int, policy: str, rng: random.Random):
        self.lines = [CacheLine() for _ in range(associativity)]
        self.policy = policy
        self.rng = rng

    def _find_victim(self) -> CacheLine:
        if self.policy == "FIFO":
            return min(self.lines, key=lambda line: line.insertion_time)
        if self.policy == "LRU":
            return min(self.lines, key=lambda line: line.last_access_time)
        if self.policy == "LFU":
            return min(self.lines, key=lambda line: (line.access_frequency, line.last_access_time))
        return self.rng.choice(self.lines)

    @staticmethod
    def _insert(line: CacheLine, tag: int, current_time: int) -> None:
        line.valid_bit = True
        line.dirty_bit = False
        line.tag = tag
        line.insertion_time = current_time
        line.last_access_time = current_time
        line.access_frequency = 1

    def access(self, tag: int, current_time: int) -> bool:
        for line in self.lines:
            if line.valid_bit and line.tag == tag:
                line.update_access_metadata(current_time)
                return True
        for line in self.lines:
            if not line.valid_bit:
                self._insert(line, tag, current_time)
                return False
        self._insert(self._find_victim(), tag, current_time)
        return False


class CacheMemory:
    def __init__(self, config: CacheConfig, seed: int = 0):
        config.validate()
        self.config = config
        self.offset_bits = int(math.log2(config.block_bytes))
        self.index_bits = int(math.log2(config.sets))
        rng = random.Random(seed)
        self.sets = [CacheSet(config.associativity, config.policy, rng) for _ in range(config.sets)]
        self.global_clock = 0
        self.hits = 0
        self.misses = 0

    def calculate_address_fields(self, address: int) -> tuple[int, int, int]:
        if not isinstance(address, int) or isinstance(address, bool):
            raise ValueError("endereço deve ser inteiro")
        if not 0 <= address < self.config.memory_bytes:
            raise ValueError(f"endereço fora da memória: {address}")
        offset = address & ((1 << self.offset_bits) - 1)
        index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = address >> (self.offset_bits + self.index_bits)
        return tag, index, offset

    def request_access(self, address: int) -> bool:
        self.global_clock += 1
        tag, index, _ = self.calculate_address_fields(address)
        hit = self.sets[index].access(tag, self.global_clock)
        if hit:
            self.hits += 1
        else:
            self.misses += 1
        return hit


@dataclass(frozen=True)
class SimulationResult:
    hits: int
    misses: int
    cumulative_hit_rate: tuple[float, ...]

    @property
    def accesses(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate_percent(self) -> float:
        return 100.0 * self.hits / self.accesses if self.accesses else 0.0

    @property
    def miss_rate_percent(self) -> float:
        return 100.0 - self.hit_rate_percent


def _validate_pattern_parameters(accesses: int, memory_bytes: int) -> None:
    if accesses <= 0:
        raise ValueError("a quantidade de acessos deve ser positiva")
    if memory_bytes <= 0:
        raise ValueError("a memória deve ser positiva")


def generate_random_pattern(accesses: int, memory_bytes: int, seed: int) -> list[int]:
    """Gera endereços uniformes, sem regras de repetição ou vizinhança."""
    _validate_pattern_parameters(accesses, memory_bytes)
    rng = random.Random(seed)
    return [rng.randint(0, memory_bytes - 1) for _ in range(accesses)]


def generate_realistic_pattern(
    accesses: int,
    memory_bytes: int,
    seed: int,
    probabilities: tuple[float, float, float] = REALISTIC_PROBABILITIES,
    hot_regions: Sequence[int] = HOT_REGIONS,
) -> list[int]:
    """Reproduz a lógica de gerar_padrao_realista do simulador original."""
    _validate_pattern_parameters(accesses, memory_bytes)
    if len(probabilities) != 3 or any(p < 0 or p > 1 for p in probabilities):
        raise ValueError("probabilidades devem estar entre 0 e 1")
    if sum(probabilities) > 1.0 + 1e-12:
        raise ValueError("a soma das probabilidades não pode exceder 1")
    valid_hot_regions = [region for region in hot_regions if 0 <= region < memory_bytes]
    if probabilities[2] and not valid_hot_regions:
        raise ValueError("não há região quente válida")

    rng = random.Random(seed)
    temporal, spatial, hot = probabilities
    previous = rng.randint(0, memory_bytes - 1)
    pattern: list[int] = []
    for _ in range(accesses):
        draw = rng.random()
        if draw < temporal:
            address = previous
        elif draw < temporal + spatial:
            address = max(0, min(memory_bytes - 1, previous + rng.randint(-16, 16)))
        elif draw < temporal + spatial + hot:
            base = rng.choice(valid_hot_regions)
            address = min(memory_bytes - 1, base + rng.randint(0, 3))
        else:
            address = rng.randint(0, memory_bytes - 1)
        pattern.append(address)
        previous = address
    return pattern


def simulate(config: CacheConfig, addresses: Sequence[int], seed: int = 0) -> SimulationResult:
    cache = CacheMemory(config, seed=seed)
    cumulative: list[float] = []
    for address in addresses:
        cache.request_access(address)
        cumulative.append(100.0 * cache.hits / (cache.hits + cache.misses))
    result = SimulationResult(cache.hits, cache.misses, tuple(cumulative))
    if result.accesses != len(addresses):
        raise AssertionError("contagem de acessos inconsistente")
    return result


ACCESS_FIELDS = ("indice", "endereco", "bloco", "janela", "regiao", "regiao_bytes")


def access_rows(addresses: Sequence[int], block_bytes: int, region_bytes: int, window_size: int):
    if block_bytes <= 0 or region_bytes <= 0 or window_size <= 0:
        raise ValueError("granularidades devem ser positivas")
    for index, address in enumerate(addresses):
        yield {
            "indice": index,
            "endereco": address,
            "bloco": address // block_bytes,
            "janela": index // window_size,
            "regiao": address // region_bytes,
            "regiao_bytes": region_bytes,
        }


def write_access_csv(path: Path, addresses: Sequence[int], block_bytes: int, region_bytes: int, window_size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ACCESS_FIELDS)
        writer.writeheader()
        writer.writerows(access_rows(addresses, block_bytes, region_bytes, window_size))


def write_cumulative_csv(path: Path, cumulative_hit_rate: Sequence[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("indice", "hit_rate_percent"))
        writer.writeheader()
        writer.writerows(
            {"indice": index, "hit_rate_percent": f"{rate:.6f}"}
            for index, rate in enumerate(cumulative_hit_rate, start=1)
        )


COMPARISON_FIELDS = (
    "cenario", "padrao", "memoria_bytes", "cache_bytes", "bloco_bytes",
    "associatividade", "linhas", "conjuntos", "politica", "acessos",
    "semente", "hits", "misses", "hit_rate_percent", "miss_rate_percent",
    "prob_temporal", "prob_espacial", "prob_quente", "janela_acessos",
    "regiao_bytes",
)


def write_comparison_csv(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COMPARISON_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def result_row(
    scenario: str,
    pattern_name: str,
    config: CacheConfig,
    seed: int,
    result: SimulationResult,
    probabilities: tuple[float, float, float] | None,
    window_size: int,
    region_bytes: int,
) -> dict:
    probability_values = probabilities or (0.0, 0.0, 0.0)
    return {
        "cenario": scenario,
        "padrao": pattern_name,
        "memoria_bytes": config.memory_bytes,
        "cache_bytes": config.cache_bytes,
        "bloco_bytes": config.block_bytes,
        "associatividade": config.associativity,
        "linhas": config.lines,
        "conjuntos": config.sets,
        "politica": config.policy,
        "acessos": result.accesses,
        "semente": seed,
        "hits": result.hits,
        "misses": result.misses,
        "hit_rate_percent": f"{result.hit_rate_percent:.6f}",
        "miss_rate_percent": f"{result.miss_rate_percent:.6f}",
        "prob_temporal": probability_values[0],
        "prob_espacial": probability_values[1],
        "prob_quente": probability_values[2],
        "janela_acessos": window_size,
        "regiao_bytes": region_bytes,
    }


def validate_result_row(row: dict) -> None:
    accesses = int(row["acessos"])
    hits = int(row["hits"])
    misses = int(row["misses"])
    if hits + misses != accesses:
        raise ValueError("hits + misses não corresponde aos acessos")
    if int(row["linhas"]) != int(row["cache_bytes"]) // int(row["bloco_bytes"]):
        raise ValueError("linhas inconsistentes")
    if int(row["conjuntos"]) != int(row["linhas"]) // int(row["associatividade"]):
        raise ValueError("conjuntos inconsistentes")
    if not math.isclose(float(row["hit_rate_percent"]) + float(row["miss_rate_percent"]), 100.0, abs_tol=1e-6):
        raise ValueError("taxas não somam 100%")
