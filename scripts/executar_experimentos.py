"""Experimento reproduzível do tópico 2. Execute --fase piloto antes de --fase completo."""
import argparse
import csv
import hashlib
import json
import platform
import os
import random
import statistics
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".mplconfig"))
import matplotlib
matplotlib.use("Agg")
import numpy as np

from cache_core import CacheMemory, REGIOES_QUENTES, gerar_padrao_realista, mapa_temporal_blocos

ROOT = Path(__file__).resolve().parents[1]
from configuracao import CONFIG, cenarios


def salvar_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def executar(phase):
    repetitions = 3 if phase == "piloto" else 30
    out = ROOT / "resultados" / phase
    out.mkdir(parents=True, exist_ok=True)
    (out / "traces").mkdir(exist_ok=True)
    # As figuras ficam em graficos/ e mapas_calor/, fora dos CSVs.
    test = subprocess.run([sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "testes", "-v"],
                          cwd=ROOT, capture_output=True, encoding="utf-8")
    (out / "testes.txt").write_text(test.stdout + test.stderr, encoding="utf-8")
    if test.returncode:
        raise SystemExit("Testes falharam. Consulte testes.txt.")
    if phase == "completo":
        pilot = ROOT / "resultados" / "piloto"
        if not (pilot / "validacao.json").exists() or not all(json.loads((pilot / "validacao.json").read_text(encoding="utf-8")).values()):
            raise SystemExit("É necessário executar e aprovar o piloto primeiro.")
        hashes = json.loads((pilot / "metadados.json").read_text(encoding="utf-8"))["fontes_sha256"]
        if any(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != value for name, value in hashes.items()):
            raise SystemExit("O código mudou após o piloto. Execute o piloto novamente.")
    rows, summaries, representatives = [], [], {}
    started = time.perf_counter()
    for name, probs, label in cenarios():
        rates = []
        for rep in range(repetitions):
            seed = 20261111 + rep
            pattern = gerar_padrao_realista(CONFIG["acessos"], CONFIG["memory_size"],
                                           REGIOES_QUENTES, probs, random.Random(seed))
            cache = CacheMemory(CONFIG["cache_size"], CONFIG["bloco_tamanho"],
                                CONFIG["associatividade"], CONFIG["algoritmo"])
            hits = [int(cache.request_access(address)) for address in pattern]
            rates.append(cache.hit_rate)
            digest = hashlib.sha256(
                np.array(pattern, dtype="<u4").tobytes()).hexdigest()
            rows.append(dict(cenario=name, repeticao=rep+1, semente=seed,
                             prob_temporal=probs[0], prob_espacial=probs[1], prob_quente=probs[2],
                             prob_aleatoria=max(0., 1-sum(probs)), hits=cache.hits, misses=cache.misses,
                             taxa_acerto=cache.hit_rate, blocos_distintos=len(set(a//CONFIG["bloco_tamanho"] for a in pattern)),
                             sha256_trace=digest))
            if rep == 0:
                representatives[name] = (pattern, cache.hit_rate, label)
                salvar_csv(out / "traces" / f"{name}.csv", [
                    dict(acesso=i+1, endereco=a, bloco=a//CONFIG["bloco_tamanho"], hit=h)
                    for i, (a, h) in enumerate(zip(pattern, hits))])
        summaries.append(dict(cenario=name, descricao=label, prob_temporal=probs[0],
                              prob_espacial=probs[1], prob_quente=probs[2],
                              repeticoes=repetitions, media=statistics.mean(rates),
                              desvio_padrao=statistics.stdev(rates), minimo=min(rates), maximo=max(rates)))
        print(f"{name:22s} média={statistics.mean(rates):.4%} DP={statistics.stdev(rates):.4%}", flush=True)
    salvar_csv(out / "execucoes.csv", rows)
    salvar_csv(out / "resumo.csv", summaries)
    checks = verificar_resultados(rows, summaries)
    (out / "validacao.json").write_text(json.dumps(checks, indent=2, ensure_ascii=False), encoding="utf-8")
    metadata = dict(fase=phase, data_local=datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(),
                    simulador_original_sha256=hashlib.sha256((ROOT.parent / "cache_simulator_GUI.py").read_bytes()).hexdigest(),
                    configuracao=CONFIG, regioes_quentes=REGIOES_QUENTES,
                    sementes=list(range(20261111, 20261111+repetitions)),
                    python=sys.version, plataforma=platform.platform(), numpy=np.__version__,
                    matplotlib=matplotlib.__version__, numero_cenarios=len(summaries),
                    numero_execucoes=len(rows), acessos_totais=len(rows)*CONFIG["acessos"],
                    segundos_simulacao=time.perf_counter()-started,
                    hash_formato="SHA-256 dos endereços uint32 little endian, na ordem de acesso",
                    fontes_sha256={name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                                   for name in ("scripts/cache_core.py", "scripts/configuracao.py",
                                                "scripts/executar_experimentos.py", "scripts/visualizacoes.py")})
    (out / "metadados.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit("Critérios de validação falharam; consulte validacao.json. Não executar coleta definitiva.")
    from visualizacoes import gerar_graficos, gerar_mapas
    gerar_graficos(out, summaries, representatives)
    gerar_mapas(out, summaries, representatives)
    print(f"VALIDADO: {len(rows)} execuções, {len(rows)*CONFIG['acessos']:,} acessos. Saída: {out}")


def verificar_resultados(rows, summaries):
    means = {r["cenario"]: r["media"] for r in summaries}
    # Faixas largas de plausibilidade; não se impõe ordem entre tipos de localidade.
    # O limite espacial permite deslocamentos e aquecimento da caminhada aleatória.
    return {
        "contadores_consistentes": all(r["hits"]+r["misses"] == CONFIG["acessos"] for r in rows),
        "taxas_validas": all(0 <= r["taxa_acerto"] <= 1 for r in rows),
        "temporal_100_um_miss": all(r["misses"] == 1 for r in rows if r["cenario"] == "temporal_100"),
        "quente_100_nove_misses": all(r["misses"] == 9 for r in rows if r["cenario"] == "quente_100"),
        "aleatorio_proximo_capacidade_relativa": .002 < means["aleatorio"] < .02,
        "espacial_100_alta_reutilizacao": means["espacial_100"] > .90,
        "curvas_puras_crescentes_em_media": all(
            all(a < b for a, b in zip(values, values[1:]))
            for values in [[means["aleatorio"]] + [means[f"{name}_{p:03d}"] for p in (20,40,60,80,100)]
                           for name in ("temporal", "espacial", "quente")]),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fase", choices=("piloto", "completo"), default="piloto")
    executar(parser.parse_args().fase)
