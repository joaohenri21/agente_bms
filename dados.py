import pandas as pd


def carregar_dados(caminho="dados_simulados.csv"):
    return pd.read_csv(caminho)