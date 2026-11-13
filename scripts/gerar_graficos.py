"""Regenera figuras a partir dos CSVs definitivos, sem repetir simulações."""
from visualizacoes import carregar_resultados, gerar_graficos

if __name__ == "__main__":
    gerar_graficos(*carregar_resultados())
