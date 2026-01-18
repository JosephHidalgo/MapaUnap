# Campus Navigation API Backend

API RESTful para navegación en el campus universitario usando el algoritmo A* y OpenAI GPT-4o mini.

## 🚀 Características

- **Algoritmo A***: Encuentra la ruta más corta entre ubicaciones
- **OpenAI GPT-4o mini**: Procesa consultas en lenguaje natural
- **FastAPI**: Framework moderno y rápido para crear APIs
- **Arquitectura modular**: Código organizado y mantenible

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación principal de FastAPI
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Modelos Pydantic
│   ├── routers/
│   │   ├── __init__.py
│   │   └── navigation.py       # Endpoints de navegación
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pathfinding.py      # Algoritmo A*
│   │   └── openai_service.py   # Integración con OpenAI
│   └── utils/
│       └── __init__.py
├── .env.example                # Ejemplo de variables de entorno
└── README.md
```

## 🛠️ Instalación

### 1. Activar el entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```bash
pip install fastapi uvicorn openai python-dotenv
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la carpeta `backend/`:

```bash
OPENAI_API_KEY=tu_api_key_de_openai
```

## 🏃 Ejecutar el Servidor

### Modo desarrollo (con hot reload)

```powershell
.\venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Modo producción

```powershell
.\venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

## 📚 Documentación de la API

Una vez iniciado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints Principales

### 1. Navegación por Lenguaje Natural

**POST** `/api/navigate`

Procesa una consulta en lenguaje natural y calcula las rutas.

```json
{
  "query": "Estoy en Medicina Humana y quiero ir a Ingeniería Civil"
}
```

**Respuesta:**

```json
{
  "success": true,
  "message": "Ruta calculada exitosamente. Distancia total: 234.56 metros",
  "schools_detected": ["Medicina Humana", "Ingeniería Civil"],
  "paths": [
    {
      "origin": "Medicina Humana",
      "destination": "Ingeniería Civil",
      "path": [...],
      "total_distance": 234.56,
      "node_count": 15
    }
  ],
  "total_route_distance": 234.56
}
```

### 2. Información del Grafo

**GET** `/api/graph/info`

Obtiene estadísticas generales del grafo.

### 3. Lista de Escuelas

**GET** `/api/schools`

Retorna todas las escuelas profesionales disponibles.

### 4. Calcular Ruta entre Nodos

**GET** `/api/path/{origin_id}/{destination_id}`

Calcula la ruta más corta entre dos nodos específicos.

## 🧪 Pruebas

### Con curl

```bash
curl -X POST "http://localhost:8000/api/navigate" \
  -H "Content-Type: application/json" \
  -d '{"query": "Estoy en Medicina Humana y quiero ir a Biología"}'
```

### Con Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/navigate",
    json={"query": "Estoy en Medicina Humana y quiero ir a Biología"}
)

print(response.json())
```

## 🔧 Tecnologías Utilizadas

- **FastAPI**: Framework web para Python
- **Uvicorn**: Servidor ASGI
- **OpenAI API**: GPT-4o mini para procesamiento de lenguaje natural
- **Pydantic**: Validación de datos
- **Python-dotenv**: Gestión de variables de entorno

## 📝 Notas Importantes

- Asegúrate de tener el archivo `graph_information.json` en la raíz del proyecto
- La API key de OpenAI debe configurarse en el archivo `.env`
- El algoritmo A* utiliza distancia euclidiana como heurística

## 🤝 Contribuciones

Este es un proyecto académico de la UNAP, VII Semestre - Inteligencia Artificial.

## 📄 Licencia

Proyecto educativo - UNAP 2026
