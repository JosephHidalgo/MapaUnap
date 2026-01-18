import heapq
import json
from math import sqrt
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from ..config import GRAPH_DATA_PATH


class AStarPathfinder:
    """Servicio para encontrar rutas usando el algoritmo A*"""
    
    def __init__(self, graph_data_path: str = None):
        """
        Inicializa el pathfinder con datos del grafo
        
        Args:
            graph_data_path: Ruta al archivo graph_information.json
        """
        if graph_data_path is None:
            graph_data_path = GRAPH_DATA_PATH
        
        self.nodes = {}
        self.edges = {}
        self.load_graph_data(graph_data_path)
    
    def load_graph_data(self, file_path: str):
        """Carga los datos del grafo desde el archivo JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Cargar nodos
        for node in data['nodes']:
            node_id = str(node['id'])
            self.nodes[node_id] = {
                'id': node_id,
                'latitude': node['latitude'],
                'longitude': node['longitude'],
                'is_school': node['is_school'],
                'school_name': node.get('school_name')
            }
        
        # Cargar aristas
        self.edges = {node_id: [] for node_id in self.nodes}
        for edge in data['edges']:
            source = str(edge['source'])
            target = str(edge['target'])
            weight = edge['weight']
            
            # Grafo bidireccional
            self.edges[source].append((target, weight))
            self.edges[target].append((source, weight))
    
    def heuristic(self, node1_id: str, node2_id: str) -> float:
        """
        Calcula la distancia euclidiana entre dos nodos (heurística para A*)
        
        Args:
            node1_id: ID del primer nodo
            node2_id: ID del segundo nodo
            
        Returns:
            Distancia euclidiana entre los nodos
        """
        node1 = self.nodes[node1_id]
        node2 = self.nodes[node2_id]
        
        lat_diff = node1['latitude'] - node2['latitude']
        lon_diff = node1['longitude'] - node2['longitude']
        
        # Convertir a metros aproximadamente
        distance = sqrt((lat_diff * 111320) ** 2 + (lon_diff * 111320) ** 2)
        return distance
    
    def find_path(self, start_id: str, goal_id: str) -> Tuple[List[str], float]:
        """
        Encuentra el camino más corto usando A*
        
        Args:
            start_id: ID del nodo inicial
            goal_id: ID del nodo objetivo
            
        Returns:
            Tupla (camino, distancia_total)
        """
        if start_id not in self.nodes or goal_id not in self.nodes:
            return [], 0.0
        
        # Priority queue: (f_score, node_id)
        open_set = [(0, start_id)]
        came_from = {}
        
        # g_score: costo desde el inicio hasta el nodo
        g_score = {node_id: float('inf') for node_id in self.nodes}
        g_score[start_id] = 0
        
        # f_score: estimación del costo total
        f_score = {node_id: float('inf') for node_id in self.nodes}
        f_score[start_id] = self.heuristic(start_id, goal_id)
        
        visited = set()
        
        while open_set:
            current_f, current = heapq.heappop(open_set)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == goal_id:
                return self._reconstruct_path(came_from, current), g_score[current]
            
            # Explorar vecinos
            for neighbor, weight in self.edges[current]:
                if neighbor in visited:
                    continue
                
                tentative_g_score = g_score[current] + weight
                
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal_id)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # No se encontró camino
        return [], 0.0
    
    def _reconstruct_path(self, came_from: Dict[str, str], current: str) -> List[str]:
        """Reconstruye el camino desde el diccionario came_from"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
    
    def find_school_by_name(self, school_name: str) -> Optional[str]:
        """
        Encuentra el ID de un nodo que contiene una escuela por su nombre
        
        Args:
            school_name: Nombre de la escuela a buscar
            
        Returns:
            ID del nodo o None si no se encuentra
        """
        school_name_lower = school_name.lower().strip()
        
        for node_id, node_data in self.nodes.items():
            if node_data['is_school'] and node_data['school_name']:
                if school_name_lower in node_data['school_name'].lower():
                    return node_id
        
        return None
    
    def get_all_schools(self) -> List[Dict]:
        """Obtiene todas las escuelas del grafo"""
        schools = []
        for node_id, node_data in self.nodes.items():
            if node_data['is_school'] and node_data['school_name']:
                schools.append({
                    'id': node_id,
                    'name': node_data['school_name'],
                    'latitude': node_data['latitude'],
                    'longitude': node_data['longitude']
                })
        return schools
    
    def get_all_nodes(self) -> List[Dict]:
        """Obtiene todos los nodos del grafo"""
        nodes = []
        for node_id, node_data in self.nodes.items():
            nodes.append({
                'id': node_id,
                'latitude': node_data['latitude'],
                'longitude': node_data['longitude'],
                'is_school': node_data['is_school'],
                'school_name': node_data['school_name']
            })
        return nodes
    
    def get_all_edges(self) -> List[Dict]:
        """Obtiene todas las aristas del grafo"""
        edges = []
        seen = set()
        for source, neighbors in self.edges.items():
            for target, weight in neighbors:
                # Evitar duplicados (grafo bidireccional)
                edge_key = tuple(sorted([source, target]))
                if edge_key not in seen:
                    seen.add(edge_key)
                    source_node = self.nodes[source]
                    target_node = self.nodes[target]
                    edges.append({
                        'source': source,
                        'target': target,
                        'weight': weight,
                        'source_coords': [source_node['longitude'], source_node['latitude']],
                        'target_coords': [target_node['longitude'], target_node['latitude']]
                    })
        return edges
    
    def get_node_info(self, node_id: str) -> Optional[Dict]:
        """Obtiene información de un nodo específico"""
        return self.nodes.get(node_id)
    
    def get_graph_stats(self) -> Dict:
        """Obtiene estadísticas del grafo"""
        total_edges = sum(len(neighbors) for neighbors in self.edges.values()) // 2
        schools = self.get_all_schools()
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': total_edges,
            'schools_count': len(schools),
            'schools': schools
        }
