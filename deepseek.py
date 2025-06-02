from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv() 
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_API_BASE_URL")

def assistant(mensaje):
    client = OpenAI(api_key=api_key, base_url=base_url) 

    chat = client.chat.completions.create(
        model= "deepseek/deepseek-r1:free",
        messages =[
            {
                "role": "system",
                "content": "Vas a identificar escuelas profesionales y me lo darás en el orden que el usuario lo indique. Por ejemplo, si el usuario dice 'Estoy en medicina humana, y quiero ir a ingeniería civil, para luego ir a arquitectura' lo que debes entregarme debe ser 'Medicina Humana, Ingeniería Civil, Arquitectura'. No debes darme ningún otro tipo de información, solo el nombre de las escuelas profesionales en el orden que el usuario lo indique.",	
            },
            {
                "role": "user",
                "content": mensaje
            }
        ] 
    )

    print("Respuesta de deepseek ", chat.choices[0].message.content)  # Imprime la respuesta del modelo
    return chat.choices[0].message.content


