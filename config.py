# Parâmetros do protótipo: célula Samsung ICR18650-26J, conjunto 3S1P
# Confira os valores marcados no datasheet (referência [2] do seu relatório)

CAPACIDADE_AH = 2.6             # 2600 mAh = 2,6 Ah
TENSAO_MAX_V = 4.2              # tensão de carga completa
TENSAO_CORTE_V = 2.75           # tensão mínima de descarga (conferir)
RESISTENCIA_INTERNA_OHM = 0.05  # valor aproximado, típico de 18650

TEMP_AMBIENTE_C = 25.0
TEMP_MAX_C = 60.0               # limite de alerta (conferir)

INTERVALO_S = 1                 # 1 leitura por segundo, como na sua interface web

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