import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
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
        self.hover_annotation = None
        self.current_path = None
        self.start_node_id = None
        self.end_node_id = None
        
        # Conectar eventos del mouse
        self.mpl_connect('motion_notify_event', self.on_hover)
        
    def load_data(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.nodes = data['nodes']
        self.edges = data['edges']
        self.path_finder = PathFinder(self.nodes, self.edges)
        self.draw_base_graph()

    def fix_encoding(self, text):
        """Corrige problemas de codificación con tildes"""
        if not isinstance(text, str):
            return text
            
        # Diccionario de reemplazos para caracteres mal codificados
        replacements = {
            'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
            'Ã±': 'ñ', 'Ã¼': 'ü', 'Ã': 'Á', 'Ã‰': 'É', 'Ã': 'Í',
            '\xc3\x93': 'Ó', '\xc3\x9a': 'Ú', '\xc3\x91': 'Ñ', '\xc3\x81': 'Á',
            'Ã\xa1': 'á', 'Ã\xa9': 'é', 'Ã\xad': 'í', 'Ã\xb3': 'ó',
            'Ã\xba': 'ú', 'Ã\xb1': 'ñ', 'FÃ\xadsico': 'Físico',
            'MatemÃ¡ticas': 'Matemáticas', 'IngenierÃ\xada': 'Ingeniería',
            'GeolÃ³gicas': 'Geológicas', 'QuÃ\xadmicas': 'Químicas',
            'BiolÃ³gicas': 'Biológicas', 'EconÃ³micas': 'Económicas',
            'PolÃ\xadticas': 'Políticas', 'FilosofÃ\xada': 'Filosofía',
            'PsicologÃ\xada': 'Psicología', 'SociolÃ³gicas': 'Sociológicas',
            'HistÃ³ricas': 'Históricas', 'GeográÃ\xadficas': 'Geográficas'
        }
        
        result = text
        for wrong, correct in replacements.items():
            result = result.replace(wrong, correct)
        
        return result

    def on_hover(self, event):
        """Maneja el evento hover del mouse"""
        if event.inaxes != self.ax or not self.nodes:
            if self.hover_annotation:
                self.hover_annotation.set_visible(False)
                self.draw()
            return
        
        # Buscar el nodo más cercano al cursor
        closest_node = None
        min_distance = float('inf')
        
        for i, node in enumerate(self.nodes):
            if node['is_school']:
                # Convertir coordenadas del nodo a coordenadas de la pantalla
                x_screen, y_screen = self.ax.transData.transform([node['longitude'], node['latitude']])
                
                # Calcular distancia euclidiana
                distance = ((event.x - x_screen)**2 + (event.y - y_screen)**2)**0.5
                
                if distance < min_distance and distance < 20:  # Radio de 20 píxeles
                    min_distance = distance
                    closest_node = (i, node)
        
        if closest_node:
            node_id, node = closest_node
            # Solo mostrar si no es nodo de inicio o final (esos se muestran siempre)
            if node_id not in [self.start_node_id, self.end_node_id]:
                school_name = self.fix_encoding(node['school_name'])
                
                if self.hover_annotation:
                    self.hover_annotation.remove()
                
                self.hover_annotation = self.ax.annotate(
                    school_name,
                    xy=(node['longitude'], node['latitude']),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', 
                             alpha=0.9, edgecolor='orange'),
                    fontsize=9, color='black', weight='bold',
                    zorder=10
                )
                self.draw()
        else:
            if self.hover_annotation:
                self.hover_annotation.set_visible(False)
                self.draw()
        
    def draw_base_graph(self, show_all_schools=True):
        self.ax.clear()
        
        # Configuración de estilo general
        plt.style.use('seaborn')
        self.fig.patch.set_facecolor('#eefeec')  # Color de fondo de la figura
        self.ax.set_facecolor('#e8f4f8')  # Color de fondo del área del gráfico
        
        # Definición de los polígonos
        main_polygon = self.coords_imagen
        
        # Primer polígono adicional (color naranja pastel)
        polygon1 = [
            [-15.82278422249303, -70.01597278964509],
            [-15.82215154584551, -70.01572081512693],
            [-15.820513672804312, -70.01676558751927],
            [-15.820525498649982, -70.01680860755896],
            [-15.820655582906848, -70.0169253762381],
            [-15.821743557050839, -70.01867690642524],
            [-15.822595010992876, -70.01854784630619],
            [-15.822665965326193, -70.01836347470756],
            [-15.823026649468822, -70.01811764590936],
            [-15.82328090183842, -70.01812993734926],
            [-15.823458287023195, -70.01769973695241],
            [-15.823263163311392, -70.01755838539346],
            [-15.822760571065201, -70.01651975872107],
            [-15.822796048205921, -70.01596664392513]
        ]
        
        # Segundo polígono adicional (color morado pastel)
        polygon2 = [
            [-15.824101546543835, -70.0168498509705],
            [-15.823997335974369, -70.01754534937186],
            [-15.824840160268455, -70.01772777518205],
            [-15.824898664210512, -70.01765746523438],
            [-15.824966309373675, -70.01706458134963],
            [-15.824940713909683, -70.01702847624135]
        ]
        
        # Dibujar el polígono principal
        main_lons = [p[1] for p in main_polygon] + [main_polygon[0][1]]
        main_lats = [p[0] for p in main_polygon] + [main_polygon[0][0]]
        self.ax.fill(main_lons, main_lats, '#d4f1f9', alpha=0.5, 
                    edgecolor='#2a6f8b', linewidth=2, zorder=1)
        
        # Dibujar primer polígono adicional (naranja pastel)
        poly1_lons = [p[1] for p in polygon1] + [polygon1[0][1]]
        poly1_lats = [p[0] for p in polygon1] + [polygon1[0][0]]
        self.ax.fill(poly1_lons, poly1_lats, '#ffddb3', alpha=0.5, 
                    edgecolor='#e67e22', linewidth=1.5, zorder=1)
        
        # Dibujar segundo polígono adicional (morado pastel)
        poly2_lons = [p[1] for p in polygon2] + [polygon2[0][1]]
        poly2_lats = [p[0] for p in polygon2] + [polygon2[0][0]]
        self.ax.fill(poly2_lons, poly2_lats, '#e0c4f0', alpha=0.5, 
                    edgecolor='#9b59b6', linewidth=1.5, zorder=1)
        
        # Dibujar aristas normales
        for edge in self.edges:
            source = self.nodes[edge['source']]
            target = self.nodes[edge['target']]
            self.ax.plot(
                [source['longitude'], target['longitude']],
                [source['latitude'], target['latitude']],
                color='#7f7f7f', linewidth=1.5, alpha=0.4, zorder=2
            )
        
        # Dibujar nodos normales
        for node in self.nodes:
            if not node['is_school']:
                lon, lat = node['longitude'], node['latitude']
                self.ax.plot(lon, lat, 'o', color='#3498db', markersize=6, 
                            alpha=0.6, zorder=3)
        
        # Dibujar escuelas profesionales (condicional)
        if show_all_schools:
            for node in self.nodes:
                if node['is_school']:
                    lon, lat = node['longitude'], node['latitude']
                    self.ax.plot(lon, lat, 'P', color='#2ecc71', markersize=12, 
                                markeredgecolor='#27ae60', alpha=0.9, zorder=4)
        
        self.ax.axis('off')
        self.draw()

    def highlight_path(self, path_ids, start_id=None, end_id=None):
        self.draw_base_graph()
        self.current_path = path_ids
        self.start_node_id = start_id
        self.end_node_id = end_id
        
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
        
        # MOSTRAR NOMBRES SOLO DE NODOS INICIO Y FINAL
        if start_id is not None and self.nodes[start_id]['is_school']:
            node = self.nodes[start_id]
            school_name = self.fix_encoding(node['school_name'])
            self.ax.text(node['longitude'], node['latitude'], f"INICIO: {school_name}", 
                        fontsize=10, color='#2c3e50', ha='center', va='bottom', 
                        weight='bold', bbox=dict(boxstyle="round,pad=0.3", 
                        facecolor='lightgreen', alpha=0.9, edgecolor='#27ae60'))
        
        if end_id is not None and end_id != start_id and self.nodes[end_id]['is_school']:
            node = self.nodes[end_id]
            school_name = self.fix_encoding(node['school_name'])
            self.ax.text(node['longitude'], node['latitude'], f"FINAL: {school_name}", 
                        fontsize=10, color='#2c3e50', ha='center', va='top', 
                        weight='bold', bbox=dict(boxstyle="round,pad=0.3", 
                        facecolor='lightcoral', alpha=0.9, edgecolor='#c0392b'))
        
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
            self.highlight_path(path, start, end)
            print(f"Ruta encontrada: {path}")
            return path
        else:
            print(f"No se encontró ruta entre {start} y {end}")
        return None