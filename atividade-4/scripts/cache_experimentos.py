"""Nucleo headless para os experimentos da Atividade 4.

A organizacao e as politicas reproduzem o nucleo de ``cache_simulator_GUI.py``.
O gerador recebe uma instancia de ``random.Random`` para tornar a carga
reprodutivel sem depender do estado aleatorio global da interface.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


POLITICAS = ("FIFO", "LRU", "LFU", "Random")
PROBABILIDADES_PADRAO = (0.20, 0.20, 0.40)
REGIOES_QUENTES_PADRAO = (
    64,
    1024,
    8192,
    32768,
    131072,
    262144,
    524288,
    786432,
    983040,
)


def is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


@dataclass(frozen=True)
class CacheConfig:
    ram_bytes: int
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
        integer_fields = {
            "ram_bytes": self.ram_bytes,
            "cache_bytes": self.cache_bytes,
            "block_bytes": self.block_bytes,
            "associativity": self.associativity,
        }
        for name, value in integer_fields.items():
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} deve ser um inteiro positivo")
        if self.policy not in POLITICAS:
            raise ValueError(f"politica desconhecida: {self.policy}")
        if not is_power_of_two(self.ram_bytes):
            raise ValueError("a RAM deve ter tamanho potencia de dois")
        if not is_power_of_two(self.cache_bytes):
            raise ValueError("a cache deve ter tamanho potencia de dois")
        if not is_power_of_two(self.block_bytes):
            raise ValueError("o bloco deve ter tamanho potencia de dois")
        if not is_power_of_two(self.associativity):
            raise ValueError("a associatividade deve ser potencia de dois")
        if self.cache_bytes >= self.ram_bytes:
            raise ValueError("a cache deve ser menor que a RAM")
        if self.block_bytes > self.cache_bytes:
            raise ValueError("o bloco nao pode ser maior que a cache")
        if self.cache_bytes % self.block_bytes:
            raise ValueError("a capacidade deve ser multipla do tamanho do bloco")
        if self.lines % self.associativity:
            raise ValueError("o numero de linhas deve ser multiplo da associatividade")
        if self.sets < 1 or not is_power_of_two(self.sets):
            raise ValueError("o numero de conjuntos deve ser uma potencia de dois positiva")


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

    def _victim(self) -> CacheLine:
        if self.policy == "FIFO":
            return min(self.lines, key=lambda line: line.insertion_time)
        if self.policy == "LRU":
            return min(self.lines, key=lambda line: line.last_access_time)
        if self.policy == "LFU":
            return min(
                self.lines,
                key=lambda line: (line.access_frequency, line.last_access_time),
            )
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
        self._insert(self._victim(), tag, current_time)
        return False


class CacheMemory:
    def __init__(self, config: CacheConfig, seed: int = 0):
        config.validate()
        self.config = config
        self.offset_bits = int(math.log2(config.block_bytes))
        self.index_bits = int(math.log2(config.sets))
        rng = random.Random(seed)
        self.sets = [
            CacheSet(config.associativity, config.policy, rng)
            for _ in range(config.sets)
        ]
        self.global_clock = 0
        self.hits = 0
        self.misses = 0

    def calculate_address_fields(self, address: int) -> tuple[int, int, int]:
        if not isinstance(address, int) or isinstance(address, bool):
            raise ValueError("o endereco deve ser inteiro")
        if not 0 <= address < self.config.ram_bytes:
            raise ValueError(f"endereco fora da RAM: {address}")
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

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


def generate_realistic_pattern(
    accesses: int,
    memory_size: int,
    hot_regions: Sequence[int],
    probabilities: tuple[float, float, float],
    seed: int,
) -> list[int]:
    """Reproduz ``gerar_padrao_realista`` com estado aleatorio local."""
    if accesses <= 0:
        raise ValueError("a quantidade de acessos deve ser positiva")
    if memory_size <= 0:
        raise ValueError("o tamanho da memoria deve ser positivo")
    if len(probabilities) != 3 or any(p < 0 or p > 1 for p in probabilities):
        raise ValueError("as tres probabilidades devem pertencer ao intervalo [0, 1]")
    if sum(probabilities) > 1.0 + 1e-12:
        raise ValueError("a soma das probabilidades nao pode exceder 1")
    valid_hot_regions = [region for region in hot_regions if 0 <= region < memory_size]
    if probabilities[2] > 0 and not valid_hot_regions:
        raise ValueError("e necessaria ao menos uma regiao quente valida")

    rng = random.Random(seed)
    temporal, spatial, hot = probabilities
    pattern: list[int] = []
    previous = rng.randint(0, memory_size - 1)
    for _ in range(accesses):
        draw = rng.random()
        if draw < temporal:
            address = previous
        elif draw < temporal + spatial:
            displacement = rng.randint(-16, 16)
            address = max(0, min(memory_size - 1, previous + displacement))
        elif draw < temporal + spatial + hot:
            base = rng.choice(valid_hot_regions)
            address = min(memory_size - 1, base + rng.randint(0, 3))
        else:
            address = rng.randint(0, memory_size - 1)
        pattern.append(address)
        previous = address
    return pattern


@dataclass(frozen=True)
class ExperimentResult:
    experimento: str
    ram_bytes: int
    cache_bytes: int
    numero_linhas: int
    bloco_bytes: int
    associatividade: int
    numero_conjuntos: int
    politica: str
    acessos: int
    hits: int
    misses: int
    hit_rate_percent: float
    miss_rate_percent: float
    semente: int


CSV_FIELDS = tuple(ExperimentResult.__dataclass_fields__)


def run_scenario(
    experiment_id: str,
    config: CacheConfig,
    pattern: Sequence[int],
    seed: int,
) -> ExperimentResult:
    cache = CacheMemory(config, seed=seed)
    for address in pattern:
        cache.request_access(address)
    accesses = len(pattern)
    hit_rate = 100.0 * cache.hits / accesses
    result = ExperimentResult(
        experimento=experiment_id,
        ram_bytes=config.ram_bytes,
        cache_bytes=config.cache_bytes,
        numero_linhas=config.lines,
        bloco_bytes=config.block_bytes,
        associatividade=config.associativity,
        numero_conjuntos=config.sets,
        politica=config.policy,
        acessos=accesses,
        hits=cache.hits,
        misses=cache.misses,
        hit_rate_percent=hit_rate,
        miss_rate_percent=100.0 - hit_rate,
        semente=seed,
    )
    validate_result(result)
    return result


def validate_result(result: ExperimentResult) -> None:
    if result.hits + result.misses != result.acessos:
        raise ValueError("hits + misses difere do total de acessos")
    if result.numero_linhas != result.cache_bytes // result.bloco_bytes:
        raise ValueError("numero de linhas inconsistente")
    if result.numero_conjuntos != result.numero_linhas // result.associatividade:
        raise ValueError("numero de conjuntos inconsistente")
    if not math.isclose(
        result.hit_rate_percent + result.miss_rate_percent,
        100.0,
        abs_tol=1e-9,
    ):
        raise ValueError("taxas de hit e miss nao somam 100%")


def write_results(path: Path, results: Iterable[ExperimentResult]) -> None:
    rows = list(results)
    if not rows:
        raise ValueError("nenhum resultado para gravar")
    for row in rows:
        validate_result(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            values = asdict(row)
            values["hit_rate_percent"] = f"{row.hit_rate_percent:.6f}"
            values["miss_rate_percent"] = f"{row.miss_rate_percent:.6f}"
            writer.writerow(values)


def execute_experiment(
    scenarios: Sequence[tuple[str, CacheConfig]],
    accesses: int,
    seed: int,
    output: Path,
) -> list[ExperimentResult]:
    if not scenarios:
        raise ValueError("a lista de cenarios esta vazia")
    ram_sizes = {config.ram_bytes for _, config in scenarios}
    if len(ram_sizes) != 1:
        raise ValueError("todos os cenarios devem utilizar a mesma RAM")
    for _, config in scenarios:
        config.validate()
    ram_bytes = next(iter(ram_sizes))
    pattern = generate_realistic_pattern(
        accesses,
        ram_bytes,
        REGIOES_QUENTES_PADRAO,
        PROBABILIDADES_PADRAO,
        seed,
    )
    results = [
        run_scenario(identifier, config, pattern, seed)
        for identifier, config in scenarios
    ]
    write_results(output, results)
    return results


def print_results(results: Sequence[ExperimentResult], output: Path) -> None:
    for row in results:
        print(
            f"{row.experimento}: hits={row.hits}, misses={row.misses}, "
            f"hit_rate={row.hit_rate_percent:.4f}%"
        )
    print(f"CSV gravado em: {output}")
