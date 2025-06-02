import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from a_estrella import a_estrella
from path_finder import PathFinder

class GraphVisualizer(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 8), dpi=100)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.nodes = []
        self.edges = []
        self.coords_imagen = [
            [-15.825354, -70.011445], [-15.823873, -70.012067],
            [-15.82398, -70.013258], [-15.822161, -70.015832],
            [-15.82057, -70.01677], [-15.821731, -70.018739],
            [-15.82144, -70.019364], [-15.823072, -70.019974],
            [-15.823251, -70.019886], [-15.824381, -70.019013],
            [-15.825473, -70.017894], [-15.826369, -70.017414],
            [-15.828208, -70.016875]
        ]
        self.path_finder = None
        
    def load_data(self, json_path):
        with open(json_path, 'r') as file:
            data = json.load(file)
        self.nodes = data['nodes']
        self.edges = data['edges']
        self.path_finder = PathFinder(self.nodes, self.edges)
        self.draw_base_graph()

        
    def draw_base_graph(self):
        self.ax.clear()
        
        # Dibujar polígono
        self.ax.plot(
            [p[1] for p in self.coords_imagen] + [self.coords_imagen[0][1]],
            [p[0] for p in self.coords_imagen] + [self.coords_imagen[0][0]], 
            'r-', linewidth=2, alpha=0.7
        )
        
        # Dibujar nodos y aristas
        for node in self.nodes:
            lon, lat = node['longitude'], node['latitude']
            if node['is_school']:
                self.ax.plot(lon, lat, 'go', markersize=8, markeredgecolor='black', alpha=0.7)
                #self.ax.text(lon, lat, node['school_name'], fontsize=8, color='black', ha='center', va='bottom')
            else:
                self.ax.plot(lon, lat, 'bo', markersize=4, alpha=0.3)

        # 3. Graficar aristas normales (grises)
        for edge in self.edges:
            source = self.nodes[edge['source']]
            target = self.nodes[edge['target']]
            self.ax.plot(
                [source['longitude'], target['longitude']],
                [source['latitude'], target['latitude']],
                'gray', linewidth=1, alpha=0.3
            )
        
        self.ax.axis('off')
        self.draw()
    
    def highlight_path(self, path_ids):
        self.draw_base_graph()
        
        if not path_ids:
            return
        
        # Calcular los límites del área que contiene la ruta
        min_lon = float('inf')
        max_lon = -float('inf')
        min_lat = float('inf')
        max_lat = -float('inf')
        
        # Primero encontrar todos los nodos en el camino
        path_nodes = [self.nodes[node_id] for node_id in path_ids]
        
        # Calcular los límites
        for node in path_nodes:
            lon, lat = node['longitude'], node['latitude']
            if lon < min_lon: min_lon = lon
            if lon > max_lon: max_lon = lon
            if lat < min_lat: min_lat = lat
            if lat > max_lat: max_lat = lat
        
        # Añadir un margen alrededor de la ruta
        margin = 0.002  # Puedes ajustar este valor según necesites
        min_lon -= margin
        max_lon += margin
        min_lat -= margin
        max_lat += margin
        
        # Resaltar nodos y aristas del camino
        for i in range(len(path_ids)-1):
            start = path_ids[i]
            end = path_ids[i+1]
            
            # Resaltar nodos del camino
            for node_id in [start, end]:
                node = self.nodes[node_id]
                self.ax.plot(node['longitude'], node['latitude'], 
                    'yo', markersize=12, markeredgecolor='red', alpha=1)  # Amarillo con borde rojo
            
            # Resaltar arista del camino
            start_node = self.nodes[start]
            end_node = self.nodes[end]
            self.ax.plot(
                [start_node['longitude'], end_node['longitude']],
                [start_node['latitude'], end_node['latitude']],
                'r-', linewidth=2, alpha=0.8  # Rojo intenso
            )
        
        # Configuración final con zoom automático
        self.ax.set_xlim(min_lon, max_lon)
        self.ax.set_ylim(min_lat, max_lat)
        self.ax.axis('off')
        plt.tight_layout()
        
        self.draw()

    def find_and_highlight_path(self, start, end):
        """Encuentra y resalta la ruta más corta entre dos nodos"""
        if self.path_finder is None:
            print("Error: PathFinder no está inicializado")
            return None
            
        path = self.path_finder.a_estrella(start, end)
        if path:
            self.highlight_path(path)
            print(f"Ruta encontrada: {path}")
            return path
        else:
            print(f"No se encontró ruta entre {start} y {end}")
        return None