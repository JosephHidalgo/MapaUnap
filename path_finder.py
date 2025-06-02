import heapq
import math

class PathFinder:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Construye un grafo de adyacencia"""
        graph = {i: [] for i in range(len(self.nodes))}
        for edge in self.edges:
            source = edge['source']
            target = edge['target']
            weight = edge['weight']
            graph[source].append((target, weight))
            graph[target].append((source, weight))  # Grafo no dirigido
        return graph
    
    def _heuristic(self, node1, node2):
        """Distancia euclidiana entre dos nodos"""
        lon1, lat1 = self.nodes[node1]['longitude'], self.nodes[node1]['latitude']
        lon2, lat2 = self.nodes[node2]['longitude'], self.nodes[node2]['latitude']
        return math.sqrt((lon2-lon1)**2 + (lat2-lat1)**2)
    
    def a_estrella(self, start, end):
        """Implementación del algoritmo A*"""
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {node: float('inf') for node in range(len(self.nodes))}
        g_score[start] = 0
        f_score = {node: float('inf') for node in range(len(self.nodes))}
        f_score[start] = self._heuristic(start, end)
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            for neighbor, weight in self.graph[current]:
                tentative_g_score = g_score[current] + weight
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self._heuristic(neighbor, end)
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return []  # No se encontró camino