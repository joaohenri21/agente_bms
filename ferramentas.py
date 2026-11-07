from config import TENSAO_CORTE_V, TEMP_MAX_C, LIMITE_DESBALANCEAMENTO_V

COLUNAS_CELULAS = ["v_celula1", "v_celula2", "v_celula3"]
COLUNAS_TEMPERATURA = ["temp_ntc1_c", "temp_ntc2_c"]


def resumo_celulas(df):
    resumo = {"duracao_min": round(float(df["tempo_s"].iloc[-1]) / 60, 1)}
    for coluna in COLUNAS_CELULAS:
        resumo[coluna] = {
            "inicial_v": round(float(df[coluna].iloc[0]), 3),
            "final_v": round(float(df[coluna].iloc[-1]), 3),
            "minima_v": round(float(df[coluna].min()), 3),
            "media_v": round(float(df[coluna].mean()), 3),
        }
    for coluna in COLUNAS_TEMPERATURA:
        resumo[f"{coluna}_maxima"] = round(float(df[coluna].max()), 1)
    return resumo


def verificar_alertas(df):
    alertas = []

    # Desbalanceamento: diferença entre a célula mais alta e a mais baixa, em cada leitura
    diferenca = df[COLUNAS_CELULAS].max(axis=1) - df[COLUNAS_CELULAS].min(axis=1)
    acima = df[diferenca > LIMITE_DESBALANCEAMENTO_V]
    if not acima.empty:
        alertas.append({
            "tipo": "desbalanceamento",
            "primeira_vez_min": round(float(acima["tempo_s"].iloc[0]) / 60, 1),
            "maior_diferenca_v": round(float(diferenca.max()), 3),
        })

    # Subtensão: alguma célula chegou na tensão de corte?
    for coluna in COLUNAS_CELULAS:
        abaixo = df[df[coluna] <= TENSAO_CORTE_V]
        if not abaixo.empty:
            alertas.append({
                "tipo": "subtensao",
                "celula": coluna,
                "primeira_vez_min": round(float(abaixo["tempo_s"].iloc[0]) / 60, 1),
            })

    # Sobretemperatura
    for coluna in COLUNAS_TEMPERATURA:
        quente = df[df[coluna] >= TEMP_MAX_C]
        if not quente.empty:
            alertas.append({
                "tipo": "sobretemperatura",
                "sensor": coluna,
                "primeira_vez_min": round(float(quente["tempo_s"].iloc[0]) / 60, 1),
            })

    return {
        "limites_usados": {
            "desbalanceamento_v": LIMITE_DESBALANCEAMENTO_V,
            "tensao_corte_v": TENSAO_CORTE_V,
            "temperatura_max_c": TEMP_MAX_C,
        },
        "alertas": alertas,
    }


def estado_no_tempo(df, minuto):
    alvo_s = minuto * 60
    indice = (df["tempo_s"] - alvo_s).abs().idxmin()  # leitura mais próxima do minuto pedido
    linha = df.loc[indice]
    return {coluna: float(linha[coluna]) for coluna in df.columns}


if __name__ == "__main__":
    import json
    from dados import carregar_dados

    df = carregar_dados()

    print("=== resumo_celulas ===")
    print(json.dumps(resumo_celulas(df), indent=2, ensure_ascii=False))

    print("\n=== verificar_alertas ===")
    print(json.dumps(verificar_alertas(df), indent=2, ensure_ascii=False))

    print("\n=== estado_no_tempo(50) ===")
    print(json.dumps(estado_no_tempo(df, 50), indent=2, ensure_ascii=False))