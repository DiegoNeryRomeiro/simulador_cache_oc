"""Regenera figuras a partir dos CSVs definitivos, sem repetir simulações."""
from visualizacoes import carregar_resultados, gerar_mapas

if __name__ == "__main__":
    gerar_mapas(*carregar_resultados())
