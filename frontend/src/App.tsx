import { useState, useEffect } from 'react';
import MapComponent from './components/MapComponent';
import SearchBox from './components/SearchBox';
import RouteInfo from './components/RouteInfo';
import { navigationAPI } from './services/api';
import type { NavigationResponse, PathStep, Node, Edge } from './types/api';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [navigationData, setNavigationData] = useState<NavigationResponse | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [paths, setPaths] = useState<PathStep[][]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadNodes();
    loadEdges();
  }, []);

  const loadNodes = async () => {
    try {
      const data = await navigationAPI.getNodes();
      if (data.nodes) {
        setNodes(data.nodes);
      }
    } catch (err) {
      console.error('Error al cargar nodos:', err);
    }
  };

  const loadEdges = async () => {
    try {
      const data = await navigationAPI.getEdges();
      if (data.edges) {
        setEdges(data.edges);
      }
    } catch (err) {
      console.error('Error al cargar aristas:', err);
    }
  };

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setError(null);
    setNavigationData(null);
    setPaths([]);

    try {
      const data = await navigationAPI.navigate(query);
      setNavigationData(data);

      if (data.success && data.paths.length > 0) {
        const allPaths = data.paths.map(pathData => pathData.path);
        setPaths(allPaths);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al procesar la búsqueda';
      setError(errorMessage);
      setNavigationData({
        success: false,
        message: errorMessage,
        schools_detected: [],
        paths: [],
        total_route_distance: 0
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseRouteInfo = () => {
    setNavigationData(null);
    setPaths([]);
  };

  return (
    <div className="app">
      {/* Panel lateral */}
      <div className="sidebar">
        {/* Header con logo */}
        <div className="sidebar-header">
          <img src="/logo.png" alt="Logo" className="header-logo" />
          <div className="header-text">
            <h1 className="header-title">MapUnap</h1>
            <p className="header-subtitle">Sistema de Navegación</p>
          </div>
        </div>
        
        <div className="sidebar-content">
          <SearchBox 
            onSearch={handleSearch} 
            isLoading={isLoading}
            hasResults={!!navigationData}
          />
          
          {error && (
            <div className="error-message">
              <p>⚠️ {error}</p>
            </div>
          )}

          {navigationData && (
            <RouteInfo 
              navigationData={navigationData} 
              onClose={handleCloseRouteInfo}
            />
          )}
        </div>
      </div>

      {/* Mapa */}
      <div className="map-container">
        <MapComponent 
          paths={paths}
          nodes={nodes}
          edges={edges}
        />
      </div>
    </div>
  );
}

export default App;
