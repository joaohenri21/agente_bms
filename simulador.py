import numpy as np
import pandas as pd
from config import (
    CAPACIDADE_AH, TENSAO_CORTE_V, RESISTENCIA_INTERNA_OHM, INTERVALO_S,
    CELULAS, TEMP_AMBIENTE_C,
    CAPACIDADE_TERMICA_J_POR_C, RESISTENCIA_TERMICA_C_POR_W,
)

# Curva OCV x SoC aproximada, típica de célula de lítio.
# Depois, na IC, você troca esses pontos pelos medidos nos ensaios reais.
SOC_PONTOS = [0.00, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 0.90, 1.00]
OCV_PONTOS = [3.00, 3.30, 3.45, 3.55, 3.65, 3.80, 3.95, 4.05, 4.20]


def tensao_circuito_aberto(soc):
    # np.interp liga os pontos da curva com retas e acha o valor para qualquer SoC
    return np.interp(soc, SOC_PONTOS, OCV_PONTOS)


def tensao_terminal(soc, corrente_a, resistencia_ohm):
    return tensao_circuito_aberto(soc) - corrente_a * resistencia_ohm


def atualizar_soc(soc, corrente_a, capacidade_ah, dt_s):
    carga_retirada_ah = corrente_a * dt_s / 3600   # A·s → Ah
    return soc - carga_retirada_ah / capacidade_ah  # Ah / Ah → adimensional

def atualizar_temperatura(temp_c, corrente_a, resistencia_ohm, dt_s):
    calor_gerado_w = corrente_a ** 2 * resistencia_ohm                       # I² × R
    calor_perdido_w = (temp_c - TEMP_AMBIENTE_C) / RESISTENCIA_TERMICA_C_POR_W
    return temp_c + (calor_gerado_w - calor_perdido_w) * dt_s / CAPACIDADE_TERMICA_J_POR_C


def simular_descarga(corrente_a=1.3, semente=42):
    # "semente" faz o ruído aleatório sair sempre igual,
    # assim você consegue repetir o experimento e comparar resultados
    rng = np.random.default_rng(semente)

    n = len(CELULAS)
    socs = [1.0] * n                 # todas começam cheias
    temps = [TEMP_AMBIENTE_C] * n    # e na temperatura ambiente
    linhas = []
    t = 0

    while True:
        tensoes = [
            tensao_terminal(socs[i], corrente_a, CELULAS[i]["resistencia_ohm"])
            for i in range(n)
        ]

        # Para quando a célula MAIS FRACA chega no limite
        if min(tensoes) <= TENSAO_CORTE_V or min(socs) <= 0:
            break

        # Leitura dos sensores com um pouco de ruído, como no ADS1115 e nos NTCs
        v_lidas = [v + rng.normal(0, 0.003) for v in tensoes]

        linhas.append({
            "tempo_s": t,
            "v_celula1": round(v_lidas[0], 3),
            "v_celula2": round(v_lidas[1], 3),
            "v_celula3": round(v_lidas[2], 3),
            "v_total": round(sum(v_lidas), 3),
            "corrente_ma": round(corrente_a * 1000 + rng.normal(0, 5), 1),
            "temp_ntc1_c": round(temps[0] + rng.normal(0, 0.1), 1),   # NTC1 na célula 1
            "temp_ntc2_c": round(temps[1] + rng.normal(0, 0.1), 1),   # NTC2 na célula 2
        })

        for i in range(n):
            socs[i] = atualizar_soc(socs[i], corrente_a, CELULAS[i]["capacidade_ah"], INTERVALO_S)
            temps[i] = atualizar_temperatura(temps[i], corrente_a, CELULAS[i]["resistencia_ohm"], INTERVALO_S)

        t += INTERVALO_S

    return pd.DataFrame(linhas)


# Teste rápido: só roda quando você executa este arquivo diretamente
if __name__ == "__main__":
    df = simular_descarga()
    df.to_csv("dados_simulados.csv", index=False)

    print(df.head())
    print("...")
    print(df.tail())
    print(f"\n{len(df)} leituras salvas | descarga parou em {df['tempo_s'].iloc[-1] / 60:.0f} min")