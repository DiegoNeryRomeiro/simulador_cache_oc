"""Audita CSVs e traces representativos sem depender da interface gráfica."""
import csv
import hashlib
import json
import statistics
from pathlib import Path
import numpy as np
from cache_core import CacheMemory, mapa_temporal_blocos

ROOT = Path(__file__).resolve().parents[1]


def ler(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def auditar():
    folder = ROOT / "resultados" / "completo"
    metadata = json.loads((folder / "metadados.json").read_text(encoding="utf-8"))
    config = metadata["configuracao"]
    rows = ler(folder / "execucoes.csv")
    summary = ler(folder / "resumo.csv")
    assert len(rows) == 630 and len(summary) == 21
    checks = []
    for s in summary:
        scenario_rows = [r for r in rows if r["cenario"] == s["cenario"]]
        assert len(scenario_rows) == 30
        assert len({r["semente"] for r in scenario_rows}) == 30
        assert abs(statistics.mean(float(r["taxa_acerto"]) for r in scenario_rows)-float(s["media"])) < 1e-12
        assert abs(statistics.stdev(float(r["taxa_acerto"]) for r in scenario_rows)-float(s["desvio_padrao"])) < 1e-12
        trace = ler(folder / "traces" / (s["cenario"] + ".csv"))
        addresses = [int(t["endereco"]) for t in trace]
        assert len(trace) == config["acessos"]
        assert [int(t["acesso"]) for t in trace] == list(range(1, len(trace)+1))
        assert all(0 <= a < config["memory_size"] for a in addresses)
        assert all(int(t["bloco"]) == a//config["bloco_tamanho"] for t, a in zip(trace, addresses))
        digest = hashlib.sha256(np.array(addresses, dtype="<u4").tobytes()).hexdigest()
        assert digest == scenario_rows[0]["sha256_trace"]
        cache = CacheMemory(config["cache_size"], config["bloco_tamanho"], config["associatividade"], config["algoritmo"])
        assert [int(cache.request_access(a)) for a in addresses] == [int(t["hit"]) for t in trace]
        assert cache.hits == int(scenario_rows[0]["hits"])
        matrix, _ = mapa_temporal_blocos(addresses, config["bloco_tamanho"], config["janela_heatmap"], config["max_linhas_heatmap"])
        assert int(matrix.sum()) == len(trace)
        checks.append(dict(cenario=s["cenario"], trace_sha256=digest, acessos=len(trace), status="PASS"))
    pilot = ler(ROOT / "resultados" / "piloto" / "execucoes.csv")
    lookup = {(r["cenario"], r["repeticao"]): r for r in rows}
    assert all(lookup[(r["cenario"], r["repeticao"])] == r for r in pilot)
    assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == value
               for name, value in metadata["fontes_sha256"].items())
    result = dict(status="PASS", execucoes=630, cenarios=21,
                  traces_reexecutados=len(checks), acessos_reexecutados=sum(c["acessos"] for c in checks),
                  piloto_reproduzido=True, medias_e_desvios_recalculados=True,
                  hashes_dos_fontes_conferidos=True, traces=checks)
    (folder / "auditoria.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("PASS: 630 execuções conferidas; 21 traces (210.000 acessos) reexecutados; piloto reproduzido.")


if __name__ == "__main__":
    auditar()
