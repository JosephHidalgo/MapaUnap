# 🗺️ Campus Navigation System

Sistema de navegación inteligente para campus universitarios usando algoritmo A* y procesamiento de lenguaje natural con OpenAI GPT-4o mini.

Un proyecto personal que combina algoritmos de grafos, inteligencia artificial y desarrollo web moderno para crear una experiencia de navegación intuitiva.

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.11+
- Entorno virtual activado

### Instalación y Ejecución

```powershell
# 1. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 2. Iniciar el servidor backend
cd backend
uvicorn app.main:app --reload

# 3. Abrir documentación
# Navega a: http://localhost:8000/docs
```

📖 **Guía completa:** [INICIO_RAPIDO.md](INICIO_RAPIDO.md)

## ✨ Características

### Backend (FastAPI)
- ✅ **API RESTful** con FastAPI
- ✅ **Algoritmo A*** para encontrar rutas óptimas
- ✅ **OpenAI GPT-4o mini** para procesar lenguaje natural
- ✅ **30 Escuelas Profesionales** en el grafo
- ✅ **205 Nodos** y **229 Aristas**
- ✅ **Documentación automática** con Swagger UI

### Frontend
🔜 **En desarrollo** - Próxima fase del proyecto

## 🏗️ Arquitectura

```
├── backend/                    # API Backend con FastAPI
│   ├── app/
│   │   ├── main.py            # Aplicación FastAPI
│   │   ├── config.py          # Configuración
│   │   ├── models/            # Modelos Pydantic
│   │   ├── routers/           # Endpoints
│   │   └── services/          # Lógica de negocio (A*, OpenAI)
│   ├── test_backend.py        # Tests
│   └── README.md              # Documentación del backend
├── graph_information.json      # Datos del grafo del campus
├── .env                        # Variables de entorno
└── venv/                       # Entorno virtual Python
```

## 🌐 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/navigate` | Navegación con lenguaje natural |
| GET | `/api/schools` | Lista de escuelas profesionales |
| GET | `/api/graph/info` | Información del grafo |
| GET | `/api/path/{origen}/{destino}` | Ruta entre nodos |
| GET | `/health` | Estado de la API |
| GET | `/docs` | Documentación interactiva |

## 📊 Ejemplo de Uso

### Navegación con Lenguaje Natural

**Request:**
```json
POST /api/navigate
{
  "query": "Estoy en Medicina Humana y quiero ir a Biología"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Ruta calculada exitosamente. Distancia total: 251.73 metros",
  "schools_detected": ["Medicina Humana", "Biología"],
  "paths": [
    {
      "origin": "Medicina Humana",
      "destination": "Biología",
      "total_distance": 251.73,
      "node_count": 10,
      "path": [...]
    }
  ],
  "total_route_distance": 251.73
}
```

## 🧪 Tests

```powershell
# Ejecutar todos los tests
python backend\test_backend.py

# Prueba rápida de la API
python backend\test_api_simple.py
```

**Estado actual:** ✅ 7/7 tests pasando

## 🔧 Tecnologías

### Backend
- **FastAPI** 0.128.0 - Framework web
- **Uvicorn** 0.40.0 - Servidor ASGI
- **OpenAI** 2.15.0 - GPT-4o mini
- **Pydantic** 2.12.5 - Validación de datos

### Algoritmo
- **A*** - Búsqueda de caminos más cortos
- **Heurística** - Distancia euclidiana
- **Complejidad** - O((V+E) log V)

## 📚 Documentación

- 📖 [INICIO_RAPIDO.md](INICIO_RAPIDO.md) - Guía de inicio rápido
- 📋 [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) - Resumen del proyecto
- 🔧 [RESUMEN_BACKEND.md](RESUMEN_BACKEND.md) - Documentación técnica
- ✅ [MIGRACION_COMPLETADA.md](MIGRACION_COMPLETADA.md) - Detalles de la migración
- 🔑 [backend/CONFIGURACION_OPENAI.md](backend/CONFIGURACION_OPENAI.md) - Configurar OpenAI

## ⚙️ Configuración

### Variables de Entorno

Crea/edita el archivo `.env` en la raíz del proyecto:

```env
# OpenAI (opcional - hay sistema de fallback)
OPENAI_API_KEY=tu_api_key_de_openai
```

**Nota:** El sistema funciona sin API key usando coincidencia de texto.

##  Estado del Proyecto

| Componente | Estado | Progreso |
|------------|--------|----------|
| Backend API | ✅ Completado | 100% |
| Algoritmo A* | ✅ Funcionando | 100% |
| OpenAI Integration | ✅ Implementado | 100% |
| Tests | ✅ 7/7 Pasando | 100% |
| Documentación | ✅ Completa | 100% |
| Frontend | 🔜 Pendiente | 0% |

## 🚦 Roadmap

### ✅ Fase 1: Backend (Completado)
- [x] Migración a FastAPI
- [x] Implementación de A*
- [x] Integración con OpenAI
- [x] Tests y documentación

### 🔜 Fase 2: Frontend (Próxima)
- [ ] Diseño de interfaz
- [ ] Integración con API
- [ ] Mapa interactivo
- [ ] Visualización de rutas

### 🔜 Fase 3: Mejoras Futuras
- [ ] Aplicación móvil
- [ ] Navegación en tiempo real
- [ ] Puntos de interés adicionales
- [ ] Optimizaciones de rendimiento

## 🆘 Soporte

### Problemas Comunes

1. **Servidor no inicia:** Verifica que el entorno virtual esté activado
2. **Puerto en uso:** Cambia el puerto con `--port 8001`
3. **Módulos no encontrados:** Ejecuta `pip install -r backend/requirements.txt`

### Logs y Debugging

El servidor muestra logs en tiempo real. Busca mensajes en rojo para errores.

## 📄 Licencia

Proyecto personal - 2025

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si encuentras algún bug o tienes sugerencias, no dudes en abrir un issue o pull request.

---

**🟢 Estado del Servidor:** Activo en http://localhost:8000  
**📚 Documentación:** http://localhost:8000/docs  
**✅ Estado:** Backend completamente funcional

**¡Sistema listo para usar!** 🎉
