# 🗺️ Campus Navigation System - Frontend

Frontend de un sistema de navegación inteligente para campus universitarios, desarrollado con React, Vite, TypeScript y MapLibre GL.

## 🚀 Tecnologías

- **React 18** - Librería de UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **MapLibre GL** - Mapas interactivos
- **MapTiler** - Proveedor de mapas vectoriales
- **Axios** - Cliente HTTP
- **Lucide React** - Iconos

## 📦 Instalación

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview
```

## 🌐 Servidor de Desarrollo

El frontend se ejecuta en: **http://localhost:5173**

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del directorio `frontend`:

```env
VITE_API_URL=http://localhost:8000
VITE_MAPTILER_STYLE=https://api.maptiler.com/maps/019bbed0-dea0-7369-abe9-d50e8bd45cbf/style.json?key=uk3AXONkcRHs9iNrVDv3
```

### Proxy de Desarrollo

El servidor de desarrollo está configurado para hacer proxy de las peticiones `/api/*` al backend en `http://localhost:8000`.

## 📂 Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/
│   │   ├── Map.tsx              # Componente del mapa
│   │   ├── SearchBox.tsx        # Caja de búsqueda
│   │   └── RouteInfo.tsx        # Información de rutas
│   ├── services/
│   │   └── api.ts               # API client
│   ├── types/
│   │   └── api.ts               # Tipos TypeScript
│   ├── utils/
│   │   └── mapHelpers.ts        # Utilidades para el mapa
│   ├── App.tsx                  # Componente principal
│   ├── App.css                  # Estilos principales
│   ├── index.css                # Estilos globales
│   └── main.tsx                 # Punto de entrada
├── .env                         # Variables de entorno
├── vite.config.ts               # Configuración de Vite
├── tsconfig.json                # Configuración de TypeScript
└── package.json                 # Dependencias
```

## 🎨 Características

### Mapa Interactivo
- Visualización interactiva del campus con MapLibre GL
- Estilo de mapa personalizado de MapTiler
- Controles de navegación y escala
- Zoom y rotación del mapa

### Búsqueda Inteligente
- Búsqueda en lenguaje natural
- Ejemplos predefinidos de consultas
- Validación de entrada
- Feedback visual durante la búsqueda

### Visualización de Rutas
- Marcadores para escuelas profesionales
- Líneas de ruta con colores diferenciados
- Marcadores de inicio (A) y fin (B)
- Ajuste automático de vista para mostrar toda la ruta

### Información de Rutas
- Detalles de distancia total
- Lista de escuelas en el recorrido
- Información de cada tramo
- Estadísticas del camino

## 🔧 Scripts Disponibles

```bash
# Desarrollo
npm run dev          # Iniciar servidor de desarrollo

# Build
npm run build        # Compilar para producción
npm run preview      # Vista previa del build

# Linting
npm run lint         # Ejecutar ESLint
```

## 🎯 Uso

1. **Iniciar el backend**:
   ```bash
   cd ../backend
   uvicorn app.main:app --reload
   ```

2. **Iniciar el frontend**:
   ```bash
   npm run dev
   ```

3. **Abrir en el navegador**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Docs API: http://localhost:8000/docs

## 🗺️ Integración con MapTiler

El proyecto usa un estilo de mapa personalizado de MapTiler. La API key está incluida en la URL del estilo:

```
https://api.maptiler.com/maps/019bbed0-dea0-7369-abe9-d50e8bd45cbf/style.json?key=uk3AXONkcRHs9iNrVDv3
```

## 📝 Flujo de la Aplicación

1. Usuario ingresa consulta en lenguaje natural
2. Frontend envía petición POST a `/api/navigate`
3. Backend procesa con OpenAI y calcula ruta con A*
4. Frontend recibe respuesta y dibuja ruta en el mapa
5. Se muestran detalles de la ruta en el panel lateral

## 🎨 Personalización

### Colores de las Rutas

Los colores se definen en `src/utils/mapHelpers.ts`:

```typescript
export const ROUTE_COLORS = [
  '#FF6B6B', // Rojo
  '#4ECDC4', // Turquesa
  '#45B7D1', // Azul
  // ...
];
```

### Estilos

Los estilos están organizados en:
- `src/index.css` - Variables CSS y estilos globales
- `src/App.css` - Estilos de componentes

## 🐛 Solución de Problemas

### El mapa no carga
- Verifica que la URL del estilo de MapTiler sea correcta
- Revisa la consola del navegador para errores

### No se comunica con el backend
- Asegúrate de que el backend esté corriendo en http://localhost:8000
- Verifica las variables de entorno en `.env`
- Revisa la configuración del proxy en `vite.config.ts`

### Errores de TypeScript
- Ejecuta `npm install` para asegurarte de que todas las dependencias estén instaladas
- Verifica que `@types` estén instalados

## 📱 Responsive

La aplicación es responsive y se adapta a diferentes tamaños de pantalla:
- **Desktop**: Sidebar lateral + mapa
- **Mobile**: Sidebar arriba + mapa abajo

## 🚀 Despliegue

### Build de Producción

```bash
npm run build
```

Los archivos optimizados se generan en `dist/`.

### Servir Build Localmente

```bash
npm run preview
```

## 📄 Licencia

Proyecto personal - 2025

---

**Estado**: ✅ Completamente funcional
**Versión**: 1.0.0
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
