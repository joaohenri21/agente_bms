import json
import os

from dotenv import load_dotenv
from groq import Groq

from config import MODELO
from dados import carregar_dados
from ferramentas import resumo_celulas, verificar_alertas, estado_no_tempo, avaliar_celulas

load_dotenv()
chave = os.getenv("GROQ_API_KEY")
if not chave:
    import streamlit as st
    chave = st.secrets["GROQ_API_KEY"]
cliente = Groq(api_key=chave)
df = carregar_dados()

INSTRUCOES = (
    "Você é um assistente que analisa os dados de um ensaio de descarga de um "
    "conjunto de baterias de íon-lítio 3S1P (três células em série). "
    "Sempre use as ferramentas para obter números e nunca invente valores. "
    "Se as ferramentas não tiverem a informação, diga que não sabe. "
    "Responda em português, de forma curta e simples, citando os números com unidade. "
    "Quando a pergunta for sobre o estado ou o desgaste de uma célula, "
    "consulte o resumo e os alertas, e considere tensão, temperatura e desbalanceamento. "
    "Use vírgula como separador decimal (exemplo: 2,91 V). "
    "Use o termo tensão, e não voltagem. "
)

FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "resumo_celulas",
            "description": (
                "Resumo do ensaio inteiro: duração, tensão inicial, final, mínima e média "
                "de cada célula, e temperatura máxima de cada sensor NTC."
                "Para avaliar desgaste ou saúde das células, use a ferramenta 'avaliar_celulas' que junta resumo e alertas."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verificar_alertas",
            "description": (
                "Verifica problemas no ensaio: desbalanceamento entre células, "
                "subtensão e sobretemperatura. Informa os limites usados e quando "
                "cada alerta apareceu pela primeira vez."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "estado_no_tempo",
            "description": (
                "Mostra todas as medições (tensões, corrente e temperaturas) "
                "em um momento específico do ensaio."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "minuto": {
                        "type": "number",
                        "description": "Momento do ensaio, em minutos desde o início.",
                    }
                },
                "required": ["minuto"],
            },
        },
    },
        {
        "type": "function",
        "function": {
            "name": "avaliar_celulas",
            "description": (
                "Avalia o estado de cada célula juntando tensão final e média, "
                "temperatura máxima e alertas. Use para perguntas sobre saúde, "
                "desgaste ou qual célula está pior."
                "Uma célula gasta tem menos capacidade e mais resistência interna: por isso "
                "descarrega antes (tensão mais baixa e desbalanceamento) e esquenta mais. "
                "Desbalanceamento e temperatura são sintomas do desgaste, não a causa."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def executar_ferramenta(nome, argumentos):
    if nome == "resumo_celulas":
        return resumo_celulas(df)
    if nome == "verificar_alertas":
        return verificar_alertas(df)
    if nome == "estado_no_tempo":
        return estado_no_tempo(df, argumentos["minuto"])
    if nome == "avaliar_celulas":
        return avaliar_celulas(df)
    return {"erro": f"Ferramenta desconhecida: {nome}"}


def perguntar(pergunta, historico=None, max_rodadas=5):
    mensagens = [{"role": "system", "content": INSTRUCOES}]
    mensagens += historico or []
    mensagens.append({"role": "user", "content": pergunta})
    usadas = []

    for _ in range(max_rodadas):
        resposta = cliente.chat.completions.create(
            model=MODELO,
            messages=mensagens,
            tools=FERRAMENTAS,
            tool_choice="auto",
        )
        mensagem = resposta.choices[0].message

        # Sem pedido de ferramenta: o LLM já tem tudo e respondeu
        if not mensagem.tool_calls:
            return {"resposta": mensagem.content, "ferramentas": usadas}

        # Guarda no histórico o pedido que o LLM fez
        mensagens.append({
            "role": "assistant",
            "content": mensagem.content or "",
            "tool_calls": [
                {
                    "id": chamada.id,
                    "type": "function",
                    "function": {
                        "name": chamada.function.name,
                        "arguments": chamada.function.arguments,
                    },
                }
                for chamada in mensagem.tool_calls
            ],
        })

        # Roda cada ferramenta pedida e devolve o resultado ao LLM
        for chamada in mensagem.tool_calls:
            try:
                argumentos = json.loads(chamada.function.arguments or "{}")
            except json.JSONDecodeError:
                argumentos = {}
            print(f"  [ferramenta] {chamada.function.name}({argumentos})")
            resultado = executar_ferramenta(chamada.function.name, argumentos)
            usadas.append({
                "nome": chamada.function.name,
                "argumentos": argumentos,
                "resultado": resultado,
            })
            mensagens.append({
                "role": "tool",
                "tool_call_id": chamada.id,
                "content": json.dumps(resultado, ensure_ascii=False),
            })

    return {
        "resposta": "Não consegui chegar a uma resposta. Tente perguntar de outro jeito.",
        "ferramentas": usadas,
    }

if __name__ == "__main__":
    print("Agente BMS. Digite sua pergunta (ou 'sair do programa').")
    while True:
        pergunta = input("\nFaça sua pergunta: ").strip()
        if pergunta.lower() == "sair do programa":
            break
        if pergunta:
            print("\nAgente:", perguntar(pergunta) ["resposta"])