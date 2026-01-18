from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import navigation
from .config import API_TITLE, API_VERSION, API_DESCRIPTION

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(navigation.router)


@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "Bienvenido a la API de Navegación UNAP",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "navigate": "POST /api/navigate - Procesar consulta de navegación",
            "graph_info": "GET /api/graph/info - Información del grafo",
            "schools": "GET /api/schools - Lista de escuelas",
            "calculate_path": "GET /api/path/{origin_id}/{destination_id} - Calcular ruta entre nodos"
        }
    }


@app.get("/health")
async def health_check():
    """Verificar el estado de la API"""
    return {"status": "healthy", "service": "UNAP Navigation API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
