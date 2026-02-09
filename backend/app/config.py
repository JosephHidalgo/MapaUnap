"""
Configuración central de la aplicación
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde la raíz del proyecto
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

# Configuración de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

# Configuración de rutas
GRAPH_DATA_PATH = BASE_DIR / "graph_information.json"

# Configuración de la API
API_TITLE = "UNAP Navigation API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "API para navegación en el campus universitario usando A* y OpenAI GPT-4o mini"

if not OPENAI_API_KEY or OPENAI_API_KEY == "tu_api_key_de_openai_aqui":
    print("⚠️  ADVERTENCIA: OPENAI_API_KEY no está configurada correctamente en el archivo .env")
    print(f"   Ruta esperada del .env: {env_path}")
