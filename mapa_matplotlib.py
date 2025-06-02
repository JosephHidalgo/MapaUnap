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
        
        # Configuración de estilo general
        plt.style.use('seaborn')  # Fondo con degradado suave
        self.fig.patch.set_facecolor('#eefeec')  # Color de fondo de la figura
        self.ax.set_facecolor('#e8f4f8')  # Color de fondo del área del gráfico (azul claro)
        
        # Dibujar polígono con relleno
        polygon_lons = [p[1] for p in self.coords_imagen] + [self.coords_imagen[0][1]]
        polygon_lats = [p[0] for p in self.coords_imagen] + [self.coords_imagen[0][0]]
        self.ax.fill(polygon_lons, polygon_lats, '#d4f1f9', alpha=0.5, edgecolor='#2a6f8b', linewidth=2)
        
        # Dibujar aristas normales (estilo mejorado)
        for edge in self.edges:
            source = self.nodes[edge['source']]
            target = self.nodes[edge['target']]
            self.ax.plot(
                [source['longitude'], target['longitude']],
                [source['latitude'], target['latitude']],
                color='#7f7f7f', linewidth=1.5, alpha=0.4, zorder=1
            )
        
        # Dibujar nodos (estilo mejorado)
        for node in self.nodes:
            lon, lat = node['longitude'], node['latitude']
            if node['is_school']:
                # Escuelas con icono más llamativo
                self.ax.plot(lon, lat, 'P', color='#2ecc71', markersize=12, 
                            markeredgecolor='#27ae60', alpha=0.9, zorder=3)
                """ self.ax.text(lon, lat, node['school_name'], fontsize=9, 
                            color='#2c3e50', ha='center', va='bottom', weight='bold') """
            else:
                # Nodos normales más discretos
                self.ax.plot(lon, lat, 'o', color='#3498db', markersize=6, 
                            alpha=0.6, zorder=2)
        
        self.ax.axis('off')
        self.draw()

    def highlight_path(self, path_ids):
        self.draw_base_graph()
        
        if not path_ids:
            return
        
        # Calcular los límites del área que contiene la ruta
        path_nodes = [self.nodes[node_id] for node_id in path_ids]
        lons = [node['longitude'] for node in path_nodes]
        lats = [node['latitude'] for node in path_nodes]
        
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)
        
        # Margen dinámico basado en el tamaño del área
        lon_range = max_lon - min_lon
        lat_range = max_lat - min_lat
        margin = max(lon_range, lat_range) * 0.3  # 30% de margen
        
        min_lon -= margin
        max_lon += margin
        min_lat -= margin
        max_lat += margin
        
        # Resaltar la ruta con mejor estilo
        for i in range(len(path_ids)-1):
            start = path_ids[i]
            end = path_ids[i+1]
            
            # Nodos del camino
            for node_id in [start, end]:
                node = self.nodes[node_id]
                if node['is_school']:
                    # Escuelas en la ruta con estilo especial
                    self.ax.plot(node['longitude'], node['latitude'], 
                                'P', color='#e74c3c', markersize=14, 
                                markeredgecolor='#c0392b', alpha=1, zorder=5)
                else:
                    # Nodos intermedios de la ruta
                    self.ax.plot(node['longitude'], node['latitude'], 
                                'o', color='#f39c12', markersize=10, 
                                markeredgecolor='#d35400', alpha=1, zorder=4)
            
            # Aristas del camino
            start_node = self.nodes[start]
            end_node = self.nodes[end]
            self.ax.plot(
                [start_node['longitude'], end_node['longitude']],
                [start_node['latitude'], end_node['latitude']],
                color='#e74c3c', linewidth=3, alpha=0.9, zorder=3,
                solid_capstyle='round', solid_joinstyle='round'
            )
        
        # Flecha indicando dirección (opcional)
        if len(path_ids) > 1:
            last_node = self.nodes[path_ids[-1]]
            self.ax.plot(last_node['longitude'], last_node['latitude'], 
                        '>', color='#c0392b', markersize=12, alpha=1, zorder=5)
        
        # Configuración final con zoom automático
        self.ax.set_xlim(min_lon, max_lon)
        self.ax.set_ylim(min_lat, max_lat)
        self.ax.set_title('Ruta Óptima Entre Nodos', pad=20, 
                        fontdict={'fontsize': 14, 'fontweight': 'bold'})
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