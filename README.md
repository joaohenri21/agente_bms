# Agente BMS

Agente de IA que analisa dados de um conjunto de baterias de lítio (3S1P) usando um LLM com ferramentas em Python. Você faz perguntas em português, como "alguma célula está desbalanceada?", e o agente escolhe qual análise rodar, calcula com Python e explica o resultado.

## Status

🚧 Em desenvolvimento

- [x] Simulador de descarga do conjunto 3S1P
- [x] Integração com LLM
- [x] Ferramentas de análise (resumo, alertas, gráficos)
- [x] Interface de chat (Streamlit)
- [ ] Publicação online

## Contexto

Este projeto continua a minha iniciação científica (PIBIC/IFTM), na qual construí um protótipo de monitoramento de baterias com ESP32, ADS1115, INA219 e sensores NTC. O simulador usa os parâmetros reais desse protótipo (células Samsung ICR18650-26J de 2600 mAh) e gera dados no mesmo formato do firmware, para que depois os dados simulados possam ser trocados pelos dados reais.

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python simulador.py
```

## Autor

João Henrique Rezende · [LinkedIn](https://www.linkedin.com/in/joaohenriquerezende)
