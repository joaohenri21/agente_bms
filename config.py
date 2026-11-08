# Parâmetros do protótipo: célula Samsung ICR18650-26J, conjunto 3S1P

CAPACIDADE_AH = 2.6             # 2600 mAh
TENSAO_MAX_V = 4.2              # tensão de carga completa
TENSAO_CORTE_V = 2.75           # tensão mínima de descarga (conferir)
RESISTENCIA_INTERNA_OHM = 0.05  # valor aproximado

TEMP_AMBIENTE_C = 25.0
TEMP_MAX_C = 60.0               # limite de alerta

INTERVALO_S = 1                 # 1 leitura por segundo, como na interface web

# Cada célula do conjunto 3S1P: capacidade (Ah) e resistência interna (ohm)
# A célula 2 simula uma célula mais gasta: menos capacidade e mais resistência
CELULAS = [
    {"capacidade_ah": 2.6, "resistencia_ohm": 0.05},
    {"capacidade_ah": 2.3, "resistencia_ohm": 0.07},
    {"capacidade_ah": 2.6, "resistencia_ohm": 0.05},
]

# Modelo térmico aproximado de uma 18650 no ar
CAPACIDADE_TERMICA_J_POR_C = 45.0    # J/°C (célula de ~45 g)
RESISTENCIA_TERMICA_C_POR_W = 20.0   # °C/W

MODELO = "openai/gpt-oss-120b"

# Diferença máxima aceitável entre a célula mais carregada e a menos carregada
LIMITE_DESBALANCEAMENTO_V = 0.10