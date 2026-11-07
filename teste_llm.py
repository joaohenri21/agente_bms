import os
from dotenv import load_dotenv
from groq import Groq
from config import MODELO

load_dotenv()  # lê o arquivo .env e carrega a chave
cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

mensagens = [
    {"role": "system", "content": "Você é um especialista em baterias de íon-lítio. Responda em português, de forma curta e simples."},
    {"role": "user", "content": "Qual era a tensão da célula 2 no final do meu ensaio de descarga?"},
]

resposta = cliente.chat.completions.create(model=MODELO, messages=mensagens)

print(resposta.choices[0].message.content)
print("\nTokens usados:", resposta.usage.total_tokens)