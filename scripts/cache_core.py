import math
import random
from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np

class CacheLine:
    def __init__(self):
        self.valid_bit: bool = False
        self.dirty_bit: bool = False
        self.tag: int = -1
        self.insertion_time: int = 0
        self.last_access_time: int = 0
        self.access_frequency: int = 0

    def update_access_metadata(self, current_time: int) -> None:
        self.last_access_time = current_time
        self.access_frequency += 1


class EvictionPolicy(ABC):
    @abstractmethod
    def find_victim(self, lines: List[CacheLine]) -> CacheLine:
        pass


class FIFO(EvictionPolicy):
    def find_victim(self, lines: List[CacheLine]) -> CacheLine:
        return min(lines, key=lambda line: line.insertion_time)


class LRU(EvictionPolicy):
    def find_victim(self, lines: List[CacheLine]) -> CacheLine:
        return min(lines, key=lambda line: line.last_access_time)


class LFU(EvictionPolicy):
    def find_victim(self, lines: List[CacheLine]) -> CacheLine:
        return min(lines, key=lambda line: (line.access_frequency, line.last_access_time))


class RandomPolicy(EvictionPolicy):
    def find_victim(self, lines: List[CacheLine]) -> CacheLine:
        return random.choice(lines)


class CacheSet:
    def __init__(self, associativity: int, policy: EvictionPolicy):
        self.ways = associativity
        self.lines: List[CacheLine] = [CacheLine() for _ in range(associativity)]
        self.policy: EvictionPolicy = policy

    def access(self, tag: int, current_time: int) -> bool:
        for line in self.lines:
            if line.valid_bit and line.tag == tag:
                line.update_access_metadata(current_time)
                return True

        for line in self.lines:
            if not line.valid_bit:
                self._insert_block(line, tag, current_time)
                return False

        victim_line = self.policy.find_victim(self.lines)
        self._insert_block(victim_line, tag, current_time)
        return False

    def _insert_block(self, line: CacheLine, tag: int, current_time: int) -> None:
        line.valid_bit = True
        line.tag = tag
        line.insertion_time = current_time
        line.last_access_time = current_time
        line.access_frequency = 1
        line.dirty_bit = False


class CacheMemory:
    def __init__(self, cache_size_bytes: int, block_size_bytes: int, associativity: int, policy_name: str):
        for value in (cache_size_bytes, block_size_bytes, associativity):
            if not isinstance(value, int) or not is_power_of_two(value):
                raise ValueError("Cache, bloco e associatividade devem ser potências de dois positivas.")
        if cache_size_bytes < block_size_bytes * associativity:
            raise ValueError("A cache deve comportar pelo menos um conjunto completo.")
        if policy_name not in ("FIFO", "LRU", "LFU", "Random"):
            raise ValueError("Política desconhecida.")
        self.cache_size = cache_size_bytes
        self.block_size = block_size_bytes
        self.associativity = associativity
        
        self.num_blocks = self.cache_size // self.block_size
        self.num_sets = self.num_blocks // self.associativity
        
        self.offset_bits = int(math.log2(self.block_size))
        self.index_bits = int(math.log2(self.num_sets))
        
        policy_map = {"FIFO": FIFO(), "LRU": LRU(), "LFU": LFU(), "Random": RandomPolicy()}
        self.policy = policy_map.get(policy_name, FIFO())

        self.sets: List[CacheSet] = [CacheSet(self.associativity, self.policy) for _ in range(self.num_sets)]
        
        self.global_clock: int = 0
        self.hits: int = 0
        self.misses: int = 0

    def calculate_address_fields(self, address: int) -> Tuple[int, int, int]:
        offset_mask = (1 << self.offset_bits) - 1
        offset = address & offset_mask
        
        index_mask = (1 << self.index_bits) - 1
        index = (address >> self.offset_bits) & index_mask
        
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
        return self.hits / total if total > 0 else 0.0

# ==============================================================================
# 2. MOTOR DE SIMULAÇÃO E UTILITÁRIOS
# ==============================================================================

def is_power_of_two(x: int) -> bool:
    return x > 0 and ((x & (x - 1)) == 0)

REGIOES_QUENTES = [64, 1024, 8192, 32768, 131072, 262144, 524288, 786432, 983040]


def validar_probabilidades(probs):
    if len(probs) != 3 or any(not math.isfinite(p) or not 0 <= p <= 1 for p in probs):
        raise ValueError("As três probabilidades devem estar entre 0 e 1 e ser finitas.")
    if sum(probs) > 1 + 1e-12:
        raise ValueError("A soma das probabilidades não pode ultrapassar 1.")


def gerar_padrao_realista(acessos: int, memory_size: int, regioes_quentes: List[int], probs: Tuple[float, float, float], rng=None) -> List[int]:
    validar_probabilidades(probs)
    if acessos <= 0 or memory_size <= 0:
        raise ValueError("Número de acessos e memória devem ser positivos.")
    if probs[2] > 0 and (not regioes_quentes or any(not 0 <= b < memory_size for b in regioes_quentes)):
        raise ValueError("Regiões quentes devem existir e estar dentro da memória.")
    rng = rng if rng is not None else random
    prob_temporal, prob_espacial, prob_quente = probs
    padrao = []
    endereco_anterior = rng.randint(0, memory_size - 1)
    
    for _ in range(acessos):
        r = rng.random()
        if r < prob_temporal:
            endereco = endereco_anterior
        elif r < prob_temporal + prob_espacial:
            deslocamento = rng.randint(-16, 16)
            endereco = max(0, min(memory_size - 1, endereco_anterior + deslocamento))
        elif r < prob_temporal + prob_espacial + prob_quente:
            base = rng.choice(regioes_quentes)
            deslocamento = rng.randint(0, 3)
            endereco = min(memory_size - 1, base + deslocamento)
        else:
            endereco = rng.randint(0, memory_size - 1)

        padrao.append(endereco)
        endereco_anterior = endereco

    return padrao

def simulacao_monte_carlo(n_simulacoes: int, acessos: int, memory_size: int, cache_size: int,
                          associatividade: int, regioes_quentes: List[int], probs: Tuple[float, float, float],
                          bloco_tamanho: int, algoritmo: str, registrar_padrao=None) -> float:
    if n_simulacoes <= 0:
        raise ValueError("Número de simulações deve ser positivo.")
    taxas_acerto = []

    for _ in range(n_simulacoes):
        padrao = gerar_padrao_realista(acessos, memory_size, regioes_quentes, probs)
        cache = CacheMemory(cache_size, bloco_tamanho, associatividade, algoritmo)
        for endereco in padrao:
            cache.request_access(endereco)
        if registrar_padrao is not None and _ == 0:
            registrar_padrao(padrao, bloco_tamanho, cache.hit_rate)
        taxas_acerto.append(cache.hit_rate)

    print(f"--- Bloco: {bloco_tamanho} Bytes | Hit Rate Médio: {np.mean(taxas_acerto):.4f} | Std: {np.std(taxas_acerto):.4f} ---")
    return float(np.mean(taxas_acerto))


def mapa_temporal_blocos(padrao, bloco_tamanho, janela=50, max_linhas=64):
    """Contagens por bloco real; se necessário, mostra os mais ativos + Outros.

    Não usa módulo: blocos distantes não são confundidos. A última janela
    parcial é preservada. Retorna matriz e rótulos (ordem crescente dos blocos).
    """
    from collections import Counter
    if not padrao or bloco_tamanho <= 0 or janela <= 0 or max_linhas < 2:
        raise ValueError("Mapa requer acessos e dimensões positivas (mínimo 2 linhas).")
    blocos = [a // bloco_tamanho for a in padrao]
    contagens = Counter(blocos)
    selecionados = sorted(contagens) if len(contagens) <= max_linhas else sorted(
        sorted(contagens, key=lambda b: (-contagens[b], b))[:max_linhas - 1])
    outros = len(selecionados) < len(contagens)
    indices = {b: i for i, b in enumerate(selecionados)}
    matriz = np.zeros((len(selecionados) + int(outros), (len(padrao) + janela - 1) // janela), dtype=int)
    for i, bloco in enumerate(blocos):
        matriz[indices.get(bloco, len(selecionados)), i // janela] += 1
    return matriz, [str(b) for b in selecionados] + (["Outros"] if outros else [])

