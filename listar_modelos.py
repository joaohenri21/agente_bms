import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

for modelo in cliente.models.list().data:
    print(modelo.id)