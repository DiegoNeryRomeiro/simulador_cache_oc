"""Parâmetros fixos e cenários da atividade 2."""
CONFIG = dict(memory_size=1048576, cache_size=8192, bloco_tamanho=16,
              associatividade=16, algoritmo="LRU", acessos=10000,
              janela_heatmap=50, max_linhas_heatmap=64)


def cenarios():
    out = [("aleatorio", (0., 0., 0.), "Referência aleatória")]
    for i, name in enumerate(("temporal", "espacial", "quente")):
        for p in (.2, .4, .6, .8, 1.):
            probs = [0., 0., 0.]
            probs[i] = p
            out.append((f"{name}_{round(p*100):03d}", tuple(probs), f"{name.capitalize()} {p:.0%}"))
    out.extend([
        ("misto_te", (.4, .4, 0.), "Temporal 40% + espacial 40%"),
        ("misto_tq", (.4, 0., .4), "Temporal 40% + quente 40%"),
        ("misto_eq", (0., .4, .4), "Espacial 40% + quente 40%"),
        ("misto_equilibrado", (.8/3, .8/3, .8/3), "Misto equilibrado (80%)"),
        ("misto_padrao", (.2, .2, .4), "Configuração original (20/20/40%)"),
    ])
    return out


