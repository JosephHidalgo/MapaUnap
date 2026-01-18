import axios from 'axios';
import type { NavigationResponse, SchoolsResponse, GraphInfo } from '../types/api';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const navigationAPI = {
  /**
   * Procesa una consulta de navegación en lenguaje natural
   */
  navigate: async (query: string): Promise<NavigationResponse> => {
    const response = await apiClient.post<NavigationResponse>('/api/navigate', { query });
    return response.data;
  },

  /**
   * Obtiene todas las escuelas disponibles
   */
  getSchools: async (): Promise<SchoolsResponse> => {
    const response = await apiClient.get<SchoolsResponse>('/api/schools');
    return response.data;
  },

  /**
   * Obtiene información general del grafo
   */
  getGraphInfo: async (): Promise<GraphInfo> => {
    const response = await apiClient.get<GraphInfo>('/api/graph/info');
    return response.data;
  },

  /**
   * Obtiene todos los nodos del grafo
   */
  getNodes: async () => {
    const response = await apiClient.get('/api/graph/nodes');
    return response.data;
  },

  /**
   * Obtiene todas las aristas del grafo
   */
  getEdges: async () => {
    const response = await apiClient.get('/api/graph/edges');
    return response.data;
  },

  /**
   * Calcula la ruta entre dos nodos específicos
   */
  getPath: async (originId: string, destinationId: string) => {
    const response = await apiClient.get(`/api/path/${originId}/${destinationId}`);
    return response.data;
  },

  /**
   * Verifica el estado de la API
   */
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};
