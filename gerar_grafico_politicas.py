
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

pasta = Path("resultados/pessoa1_politicas")
csv_dir = pasta / "csv"
grafico_dir = pasta / "grafico"
grafico_dir.mkdir(parents=True, exist_ok=True)

politicas = ["FIFO", "LRU", "LFU", "RANDOM", "MRU"]
taxas = []

for politica in politicas:
    arquivo = csv_dir / f"{politica}.csv"
    dados = pd.read_csv(arquivo)

    linha = dados.loc[dados["Tamanho_Bloco"] == 32]

    if linha.empty:
        raise ValueError(f"Bloco de 32 bytes não encontrado em {arquivo}")

    taxa = float(linha["Taxa_Acerto"].iloc[0]) * 100
    taxas.append(taxa)

plt.figure(figsize=(9, 5))
barras = plt.bar(politicas, taxas)

plt.title("Comparação das Políticas de Substituição")
plt.xlabel("Algoritmo")
plt.ylabel("Taxa média de acerto (%)")
plt.ylim(0, 75)
plt.grid(axis="y", alpha=0.2)

for barra, taxa in zip(barras, taxas):
    plt.text(
        barra.get_x() + barra.get_width() / 2,
        taxa + 0.7,
        f"{taxa:.2f}%",
        ha="center"
    )

plt.tight_layout()
saida = grafico_dir / "comparacao_politicas_32_bytes.png"
plt.savefig(saida, dpi=200)
plt.show()

print(f"Gráfico salvo em: {saida}")

for politica, taxa in zip(politicas, taxas):
    print(f"{politica}: {taxa:.2f}%")
